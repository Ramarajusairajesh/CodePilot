import json
import os

LOG_FILE = 'context.log'
MAX_ENTRIES = 1000

def save_context(kind, input, output):
    entry = {'kind': kind, 'input': input, 'output': output}
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
    lines.append(json.dumps(entry) + '\n')
    if len(lines) > MAX_ENTRIES:
        lines = lines[-MAX_ENTRIES:]
    with open(LOG_FILE, 'w') as f:
        f.writelines(lines)

def load_context():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, 'r') as f:
        return [json.loads(line) for line in f] 