from pathlib import Path

env_path = Path(".env")

if not env_path.exists():
    print("MISSING: no .env file in this folder.")
    raise SystemExit

lines = env_path.read_text(encoding="utf-8-sig").splitlines()

key_line_index = None
for i, line in enumerate(lines):
    if line.strip().startswith("ANTHROPIC_API_KEY"):
        key_line_index = i
        break

if key_line_index is None:
    print("PROBLEM: no line starting with ANTHROPIC_API_KEY found in .env at all.")
    raise SystemExit

line = lines[key_line_index]
print(f"Found the ANTHROPIC_API_KEY line at line {key_line_index + 1} of .env.")

if "=" not in line:
    print("PROBLEM: that line has no '=' sign on it.")
    raise SystemExit

value_on_same_line = line.split("=", 1)[1].strip()
print(f"Characters after '=' on that SAME line: {len(value_on_same_line)}")

if len(value_on_same_line) == 0:
    print("PROBLEM CONFIRMED: the line is 'ANTHROPIC_API_KEY=' with nothing after it.")
    print("This means the key got pushed onto its own separate line below.")
    if key_line_index + 1 < len(lines):
        next_line = lines[key_line_index + 1].strip()
        print(f"Next line has {len(next_line)} characters, starts with 'sk-ant-': {next_line.startswith('sk-ant-')}")
        if next_line.startswith("sk-ant-"):
            print("FIX: merge that next line back onto the ANTHROPIC_API_KEY= line, with no line break between them.")
elif value_on_same_line.startswith("sk-ant-"):
    print("This looks correctly formatted: key is on the same line, starts with sk-ant-.")
else:
    print("Value is present but doesn't start with 'sk-ant-' -- double check what's there.")