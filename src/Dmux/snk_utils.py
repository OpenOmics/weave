def get_adapter_opts(wc, input):
<<<<<<< HEAD
    adapter_file = open(input.adapters).readlines()
    sid = wc.sid
    sid = '_'.join(sid.split('_')[:-1])

    r1_adapter, r2_adapter = None, None
    for _line in adapter_file:
        if _line.startswith(sid + '_R1'):
            r1_adapter = _line.split('\t')[1].strip()
        if _line.startswith(sid + '_R2'):
            r2_adapter = _line.split('\t')[1].strip()

    if r1_adapter is None:
        return ''

    adapter_flags = f"--adapter_sequence {r1_adapter}"
    if r2_adapter:
        adapter_flags += f" --adapter_sequence_r2 {r2_adapter}"
    return adapter_flags
=======
    r1_index = getr1(wc, input)
    r2_index = getr2(wc, input)
    flag = f"--adapter_sequence {r1_index}" 
    if r2_index not in ('', None):
        flag += f" --adapter_sequence_r2 {r2_index}"
    return flag


def get_fastp_sample_list(r1, r1_index, r2, r2_index):
    r1, r2 = open(r1).read().strip(), open(r2).read().strip()
    if r2 not in ('', None):
        return [r1, r2]
    else:
        return [input.R1]
>>>>>>> 88d43eb (ngsqc fastqc, trimming, fastqc again after trim)
