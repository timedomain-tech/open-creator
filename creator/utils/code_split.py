def split_code_blocks(code: str):
    lines = code.strip().split('\n')
    i = len(lines) - 1
    
    codes = []
    
    while i >= 0:
        line = lines[i]
        
        # If line not start with space
        if not line.startswith(("    ", "\t")):
            codes.append(line)
            i -= 1
        # Else
        else:
            break
    
    # Add remaining lines as a single block
    if i >= 0:
        codes.append("\n".join(lines[:i+1]))
    
    return codes[::-1]
