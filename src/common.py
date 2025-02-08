def combine_bf(*args) -> list:
    def helper(ops_path, ops) -> list:
        if ops:
            ops = [c for c in ops]
            while (ops and ops_path and
                   ((ops[0] == '>' and ops_path[-1] == '<') or
                   (ops[0] == '<' and ops_path[-1] == '>') or
                   (ops[0] == '+' and ops_path[-1] == '-') or
                   (ops[0] == '-' and ops_path[-1] == '+')
                   )):
                del ops[0]
                ops_path.pop()
            ops_path.extend(ops)
        return ops_path
    ops_path = args[0]
    for i in range(1, len(args)):
        ops = [c for c in args[i]]
        ops_path = helper(ops_path, ops)

    return ops_path

