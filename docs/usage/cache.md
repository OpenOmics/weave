
## Objective

The weave pipeline utilizes a number of large file resources including containers, reference genomes, reference databases, and indexes. This
command allows for the user to download all these files serially in one-shot. This execution method will updated to include a parallel cluster
option for faster execution.

## Execution

### Example command

```bash title="cache commmand"
# starting from install
./weave cache ./output_directory/
```

### Output

> Warning: cache download only implemented in serial local mode currently<br />
> Getting docker resource bcl2fastq...<br />
> ...singularity output...<br />
> Getting docker resource weave...<br />
> ...singularity output...<br />
> Getting web resource kraken...<br />
> ...progress bar...<br />
> Getting web resource kaiju...<br />
> ...progress bar...<br />
> Cache downloads complete!<br />

## Contents

The current contents of what all is downloaded via the cache command are:

1. All pipeline containerized images in read-only Singularity Image Format (SIF)
2. Kraken2 kmer databases
3. Kaiju kmer databases
4. FastQ_Screen genome indexes

