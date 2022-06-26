def apply_ot(text, operations):
    '''
    Applies operational transformation to a text using a given list of operations
    Operations available:
    ["insert", char, position:int]
    ["delete", char, position:int]
    ["update", char, new_char, position: int]
    ["retain", char, position]

    Parameters
    ----------
    text: str
        original text
    operations: 2d list, each row is a list of operations by a client

    Returns
    -------
    new_text: str
        The string with the applied operations
    '''
    for idx in range(len(operations)):
        for op in operations[idx]:
            text = apply_operation(text, op)
            operations[idx+1:] = update_operations(operations[idx+1:], op)
    return text
    
def update_operations(operations, applied_op):
    '''
    Update a list of operations according to an operation applied

    Parameters
    ----------
    operations: 2d list, each row is a list of operations by a client
    applied_op: a list as described in the apply_ot function

    Returns
    -------
    new_operations: 
    '''
    assert applied_op[0] in ["insert", "delete", "update", "retain"]
    new_operations = []
    for row in operations:
        new_row = []
        for op in row:
            if op[0]=="retain":
                new_row.append(op)
            else:
                op_pos_idx = 2 if op[0] in ["insert", "delete"] else 3
                if applied_op[0]=="insert":
                    _, pos = applied_op[1:3]
                    if pos < op[op_pos_idx]:
                        op[op_pos_idx] += 1
                elif applied_op[0]=="delete":
                    _, pos = applied_op[1:3]
                    if pos < op[op_pos_idx]:
                        op[op_pos_idx] -= 1
                elif applied_op[0]=="update":
                    pass
                new_row.append(op)
        new_operations.append(new_row)
    return new_operations

def apply_operation(text, operation):
    '''
    Applies an atomic operation to a given text
    '''
    assert operation[0] in ["insert", "delete", "update", "retain"]
    if operation[0]=="insert":
        char, pos = operation[1:3]
        text = text[:pos] + char + text[pos:]
    elif operation[0]=="delete":
        char, pos = operation[1:3]
        text = text[:pos] + text[pos+1:]
    elif operation[0]=="update":
        new_char, char, pos = operation[1:4]
        assert text[pos]==char
        text = text[:pos] + new_char + text[pos+1:]
    elif operation[0]=="retain": # TODO
        text = text  
    
    return text

if __name__=="__main__":
    orig_text = "abc"
    ops = [[["delete","b",1]],[["insert","x",2]]]
    # Expected output axc
    print(apply_ot(orig_text, ops))