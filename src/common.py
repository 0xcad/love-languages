def combine_bf(*args) -> list:
    def helper(ops_path, ops) -> list:
        ops_path = list(ops_path) if type(ops_path) == str else ops_path
        if ops:
            ops = [c for c in ops]
            while (ops and ops_path and
                   ((ops[0] == '>' and ops_path[-1] == '<') or
                   (ops[0] == '<' and ops_path[-1] == '>') or
                   (ops[0] == '+' and ops_path[-1] == '-') or
                   (ops[0] == '-' and ops_path[-1] == '+')# or
                   #(ops[0] == None and ops_path[-1] == None)
                   )):
                del ops[0]
                #if ops_path[-1] is not None:
                #    ops_path.pop()
                ops_path.pop()
            ops_path.extend(ops)
        return ops_path
    ops_path = args[0].copy()
    for i in range(1, len(args)):
        ops = list(args[i])
        ops_path = helper(ops_path, ops)

    return ops_path


def simplify_bf(bf_str) -> str:
    ops_path = []
    for c in bf_str:
        if c in '.,+-[]><':
            ops_path = combine_bf(ops_path, c)
    return ''.join(ops_path)
