def add_tab_to_each_line(text: str, skip_first_line: bool = False) -> str:
    lines = text.splitlines()
    if skip_first_line:
        lines_with_tabs = [lines[0]] + ['\t' + line for line in lines[1:]]
    else:
        lines_with_tabs = ['\t' + line for line in lines]
    return '\n'.join(lines_with_tabs)