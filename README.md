<div align="center">
   
  <h1>weave 🔬</h1>
  
  **_An awesome metagenomic and metatranscriptomics pipeline_**

  [![tests](https://github.com/OpenOmics/weave/workflows/tests/badge.svg)](https://github.com/OpenOmics/weave/actions/workflows/main.yaml) [![docs](https://github.com/OpenOmics/weave/workflows/docs/badge.svg)](https://github.com/OpenOmics/weave/actions/workflows/docs.yml) [![GitHub issues](https://img.shields.io/github/issues/OpenOmics/weave?color=brightgreen)](https://github.com/OpenOmics/weave/issues)  [![GitHub license](https://img.shields.io/github/license/OpenOmics/weave)](https://github.com/OpenOmics/weave/blob/main/LICENSE) 
  
  <i>
    This is the home of the pipeline, weave. Its long-term goals: to provide accurate quantification, taxonomic classification, and functional profiling of assembled (bacteria and archaea) metagenomes!
  </i>
</div>

## Overview
Welcome to weave's documentation! This guide is the main source of documentation for users that are getting started with the [weave](https://github.com/OpenOmics/weave/). 

The **`./weave`** pipeline is composed of two sub commands to setup and run the pipeline across different systems. Each of the available sub commands perform different functions: 

> [weave **run**](https://openomics.github.io/weave/usage/run/)   
> Run the weave pipeline with your input files.


> [weave **cache**](https://openomics.github.io/weave/usage/cache/)  
> Downloads the reference files for the pipeline to a selected directory.

**weave** is a two-pronged pipeline; the first prong detects and uses the appropriate illumnia software to demultiplex the ensemble collection of reads into their individual samples and converts the sequencing information into the FASTQ file format. From there out the second prong is a distrubted parallele step that uses a variety of commonly accepting nextgen sequencing tools to report, visualize, and calculate the quality of the reads after sequencing. **weave** makes uses of the ubiquitous containerization software <a href="https://sylabs.io">singularity</a><sup>2</sup> for modularity, and the robust pipelining DSL [Snakemake](https://snakemake.github.io/)<sup>3</sup>

**weave** common use is to gauge the qualtiy of reads for potential downstream analysis. Since bioinformatic analysis requires robust and accurate data to draw scientific conclusions, this helps save time and resources when it comes to analyzing the volumous amount of sequencing data that is collected routinely.

Several of the applications that **weave** uses to visualize and report quality metrics are:
- [Kraken](https://github.com/DerrickWood/kraken2)<sup>71</sup>, kmer analysis
- [Kaiju](https://bioinformatics-centre.github.io/kaiju/)<sup>4</sup>, kmer analysis
- [FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/), fastq statistics
- [fastp](https://github.com/OpenGene/fastp)<sup>6</sup>, fastq adapter removal (trimming)
- [FastQ Screen](https://www.bioinformatics.babraham.ac.uk/projects/fastq_screen/)<sup>5</sup>, taxonomic quantification
- [MultiQC](https://multiqc.info/)<sup>1</sup>, ensemble QC results


## Dependencies
**System Requirements:** `singularity>=3.5`  
**Python Requirements:** `snakemake>=5.14.0`, `pyyaml`, `progressbar`, `requests`, `terminaltables`, `tabulate`

Please refer to the complete [installation documents](https://openomics.github.io/weave/install/) for detailed information.

## Installation
```bash
# clone repo
git clone https://github.com/OpenOmics/weave.git
cd weave
# create virtual environment
python -m venv ~/.my_venv
# activate environment
source ~/.my_venv/bin/activate
pip install -r requirements.txt 
```

Please refer to the complete [installation documents](https://openomics.github.io/weave/install/) for detailed information.

## Contribute 
This site is a living document, created for and by members like you. weave is maintained by the members of OpenOmics and is improved by continous feedback! We encourage you to contribute new content and make improvements to existing content via pull request to our [GitHub repository](https://github.com/OpenOmics/weave).


## References
<sup>**1.**  <a href="https://doi.org/10.1093/bioinformatics/btw354">Philip Ewels, Måns Magnusson, Sverker Lundin, Max Käller, MultiQC: summarize analysis results for multiple tools and samples in a single report, Bioinformatics, Volume 32, Issue 19, October 2016, Pages 3047–3048.</a></sup>  
<sup>**2.**  [Kurtzer GM, Sochat V, Bauer MW (2017). Singularity: Scientific containers for mobility of compute. PLoS ONE 12(5): e0177459.](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0177459)</sup>  
<sup>**3.**  [Koster, J. and S. Rahmann (2018). "Snakemake-a scalable bioinformatics workflow engine." Bioinformatics 34(20): 3600.](https://academic.oup.com/bioinformatics/article/28/19/2520/290322)</sup>  
<sup>**4.**  [Menzel P., Ng K.L., Krogh A. (2016) Fast and sensitive taxonomic classification for metagenomics with Kaiju. Nat. Commun. 7:11257](http://www.nature.com/ncomms/2016/160413/ncomms11257/full/ncomms11257.html)</sup>  
<sup>**5.**  [Wingett SW and Andrews S. FastQ Screen: A tool for multi-genome mapping and quality control [version 2; referees: 4 approved]. F1000Research 2018, 7:1338](https://doi.org/10.12688/f1000research.15931.2)</sup>  
<sup>**6.**  [Shifu Chen, Yanqing Zhou, Yaru Chen, Jia Gu; fastp: an ultra-fast all-in-one FASTQ preprocessor, Bioinformatics, Volume 34, Issue 17, 1 September 2018, Pages i884–i890.](https://doi.org/10.1093/bioinformatics/bty560)</sup>  
<sup>**7.**  [Wood, D.E., Lu, J. & Langmead, B. Improved metagenomic analysis with Kraken 2. Genome Biol 20, 257 (2019).](https://doi.org/10.1186/s13059-019-1891-0)</sup>  