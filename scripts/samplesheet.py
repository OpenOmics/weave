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
            self.process_simple_section(sheet_sections['Reads'])

        if 'BCLConvert_Settings' in sheet_sections:
            norm_names = {'AdapterRead1': 'Read01', 'AdapterRead2': 'Read02'}
            self.process_simple_section(sheet_sections['BCLConvert_Settings'], rename=norm_names)

        if 'Data' not in sheet_sections and 'BCLConvert_Data' in sheet_sections:
            sheet_sections['Data'] = sheet_sections['BCLConvert_Data']

        assert 'Data' in sheet_sections, 'No sample data within this sample sheet'
        filtered_data = list(filter(lambda x: len(set(x)) > 1, sheet_sections['Data']))
        self.process_csv_section(filtered_data)


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
        section_csv = DictReader(section_io, delimiter=',')
        setattr(self, 'data', list(map(AttrDict, section_csv)))

    
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
