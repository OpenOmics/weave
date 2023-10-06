getr1 = lambda wc, input: open(input.R1_adapter).read().strip()
getr2 = lambda wc, input: open(input.R2_adapter).read().strip()


def get_adapter_opts(wc, input):
    r1_index = getr1(wc, input)
    r2_index = getr2(wc, input)
    flag = f"--adapter_sequence {r1_index}" 
    if r2_index not in ('', None):
        flag += f" --adapter_sequence_r2 {r2_index}"
    return flag