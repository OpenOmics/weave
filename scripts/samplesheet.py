from csv import DictReader
from io import StringIO
from pathlib import Path
from datetime import datetime
from operator import itemgetter
from dateutil import parser as dateparser


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class IllumniaSampleSheet():
    """Class to parse illumnia sample sheet information according to the
    sample sheet format specified by [Illumina](https://support-docs.illumina.com/SHARE/SampleSheetv2/Content/SHARE/SampleSheetv2/SampleSheetStructure.htm)

    Properties:
        pairedend(bool): True for paired end seqencing data, False for single end sequencing data
        project(str): Title of the project for this sequencing run
        run(str): Run Identifer this single sequencing run

    """
    def __init__(self, samplesheet, end=None):
        self.path = Path(samplesheet).absolute()
        self.sheet = self.parse_sheet(samplesheet)
        self.force_endedness = end
        self.validate_sheet()
    
    def parse_sheet(self, sheet):
        sheet_sections = dict()
        with open(sheet) as opensheet:
            this_section = None
            for _line in opensheet:
                line = _line.strip()
                first = _line.split(',')[0]
                if first.startswith('[') and first.endswith(']'):
                    this_section = first[1:-1]
                    sheet_sections[this_section] = []
                else:
                    sheet_sections[this_section].append(line)

        if 'Header' in sheet_sections:
            self.process_simple_section(sheet_sections['Header'])
            
        if 'Settings' in sheet_sections:
            self.process_simple_section(sheet_sections['Settings'])

        if 'Reads' in sheet_sections:
            self.process_v1_reads_section(sheet_sections['Reads'])

        if 'BCLConvert_Settings' in sheet_sections:
            norm_names = {'AdapterRead1': 'Read01', 'AdapterRead2': 'Read02'}
            self.process_simple_section(sheet_sections['BCLConvert_Settings'], rename=norm_names)

        if 'Data' not in sheet_sections and 'BCLConvert_Data' in sheet_sections:
            sheet_sections['Data'] = sheet_sections['BCLConvert_Data']

        assert 'Data' in sheet_sections, 'No sample data within this sample sheet'
        filtered_data = list(filter(lambda x: len(set(x)) > 1, sheet_sections['Data']))
        self.process_csv_section(filtered_data)


    def process_v1_reads_section(self, section):
        section = [x for x in section if set(x) != {','}]
        r1, r2 = None, None
        for i, line in enumerate(section):
            this_line_name = line.split(',')[0]
            this_line_val = line.split(',')[1]
            if this_line_name.lower() in ('read01', 'read02') and this_line_val.isnumeric():
                if this_line_name.endswith('1') and int(this_line_val) > 0:
                    r1 = int(this_line_val)
                elif this_line_name.endswith('2') and int(this_line_val) > 0:
                    r2 = int(this_line_val)
            elif this_line_name.isnumeric() and int(this_line_name) > 0:
                if i == 0:
                    r1 = int(this_line_name)
                elif i == 1:
                    r2 = int(this_line_name)
        else:
            self.process_simple_section([line])
        if r1 and r1 > 0:
            setattr(self, 'Read01', r1)
        if r2 and r2 > 0:
            setattr(self, 'Read02', r2)
        return


    def process_simple_section(self, section, rename=None):
        """Simple section processing for Illumnia sample sheet. 

        Objective:
            Disgard rows of all commas, collect rows with single values into self attributes which 
            are 

        """
        for _line in section:
            index = _line.split(',')[0]
            if ' ' in index:
                index = index.replace(' ', '_')
            if "\n" in _line:
                _line = _line.replace("\n", ' ')
            rest = ','.join(_line.split(',')[1:])
            if set(list(rest)) == ',':
                continue
            else:
                second = _line.split(',')[1]
                if index == 'Date':
                    setattr(self, index, dateparser.parse(second))
                else:
                    if rename and index in rename:
                        index = rename[index]
                    setattr(self, index, second)
        return

    def process_csv_section(self, section):
        section_io = StringIO("\n".join(section))
        csv_data = []
        for row in DictReader(section_io, delimiter=','):
            csv_data.append(AttrDict({k: v for k, v in row.items() if k != '' and v != ''}))
        
        # reformat for consistency between v1 and v2 sample sheets
        for row in csv_data:
            if 'index' in row:
                row['Index'] = row['index']
                del row['index']
            if 'index2' in row:
                row['Index2'] = row['index2']
                del row['index2']
        setattr(self, 'data', csv_data)


    def validate_sheet(self):
        # this is the space we can do any type of sample sheet validation for running 
        # in our snakemake pipelines
        # check values in self.sheet and continue or raise appropriate error
        for row in self.data:
            if not getattr(row, 'Sample_Project', None):
                raise AttributeError("Sample sheet does not have 'Sample_Project' specified for each sample.")
    
    @property
    def samples(self):
        return getattr(self, 'data', None)
        
    @property
    def project(self):
        sheet_projects = list(set(map(itemgetter('Sample_Project'), self.data)))
        assert len(sheet_projects) == 1, 'Sample sheet containers multiple project, please limit to single project per sheet.'
        return sheet_projects[0]

    @property
    def instrument(self):
       return getattr(self, 'Instrument', None)

    @property
    def platform(self):
        return getattr(self, 'InstrumentPlatform', None)
    
    @staticmethod
    def intorlen(s):
        "Cast to int if possible, otherwise get length"
        try:
            v = int(s)
        except ValueError:
            v = len(s)
        return v

    @property
    def adapters(self):
        r1 = getattr(self, 'Read01', None)
        r2 = getattr(self, 'Read02', None)
        return list(map(self.intorlen, filter(None, [r1, r2])))

    @property
    def is_paired_end(self):
        if len(self.adapters) == 1:
            return False
        elif len(self.adapters) == 2:
            return True
        else:
            raise ValueError('Unknown endedness from sample sheet')

    @property
    def is_single_end(self):
        if len(self.adapters) == 1:
            return True
        elif len(self.adapters) == 2:
            return False
        else:
            raise ValueError('Unknown endedness from sample sheet')

