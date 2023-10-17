def get_adapter_opts(wc, input):
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
