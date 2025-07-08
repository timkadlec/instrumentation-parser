import re

def normalize_abbr(abbr):
    return abbr.lower().replace('.', '').replace(' ', '').replace('-', '')

def clean_line(input_line):
    cleaned = re.sub(r'[\u200b\u200c\u200d\u2060\ufeff]', '', input_line)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def split_instrumentation_line(input_line):
    input_line = clean_line(input_line)

    parts = []
    current = ''
    parentheses_level = 0

    for char in input_line:
        if char == ',' and parentheses_level == 0:
            parts.append(current.strip())
            current = ''
        else:
            if char == '(':
                parentheses_level += 1
            elif char == ')':
                parentheses_level -= 1
            current += char

    if current:
        parts.append(current.strip())

    return parts
