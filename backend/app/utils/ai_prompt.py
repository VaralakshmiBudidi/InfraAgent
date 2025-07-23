def parse_prompt(prompt: str) -> str:
    import re
    match = re.search(r'https://github.com/\S+', prompt)
    return match.group(0) if match else ""
