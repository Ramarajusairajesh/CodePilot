from flask import Flask, request, jsonify
import subprocess
import os
import json
from context_manager import save_context, load_context
import sys
import re

app = Flask(__name__)

WORKSPACE = '/home/agent/workspace'
DANGEROUS_SHELL = [
    r'rm\s+-rf\s+/', r'shutdown', r'reboot', r':\(\)\s*\{', r'\bkill\b', r'\binit\b', r'\bpoweroff\b', r'\bhalt\b', r'\bmkfs', r'\bdd\b', r'\bchown\b', r'\bchmod\b', r'\buseradd\b', r'\buserdel\b', r'\bgroupadd\b', r'\bgroupdel\b', r'\bpasswd\b', r'\bmount\b', r'\bumount\b', r'\bifconfig\b', r'\broute\b', r'\biptables\b', r'\bnetstat\b', r'\bservice\b', r'\bsudo\b', r'\bnohup\b', r'\bpkill\b', r'\bkillall\b', r'\bcrontab\b', r'\bvi\b', r'\bnano\b', r'\beditor\b', r'\bapt\b', r'\byum\b', r'\bdnf\b', r'\bpacman\b', r'\bzypper\b', r'\bdnf\b', r'\bwget\b', r'\bcurl\b.*http.*', r'\bscp\b', r'\bftp\b', r'\btelnet\b', r'\bssh\b', r'\bpython\b', r'\bperl\b', r'\bphp\b', r'\bnode\b', r'\bjava\b', r'\bmake\b', r'\bgcc\b', r'\bg\+\+\b', r'\bclang\b', r'\bld\b', r'\bstrip\b', r'\bobjcopy\b', r'\bobjdump\b', r'\bstrace\b', r'\bltrace\b', r'\bgdb\b', r'\bvalgrind\b', r'\bperf\b', r'\btop\b', r'\bhtop\b', r'\bfree\b', r'\bvmstat\b', r'\biostat\b', r'\bpidof\b', r'\bps\b', r'\bwhoami\b', r'\bwho\b', r'\bw\b', r'\busers\b', r'\bgroups\b', r'\bhostname\b', r'\buname\b', r'\bdmesg\b', r'\bjournalctl\b', r'\blogread\b', r'\bcat\b\s+/etc', r'\bcat\b\s+/proc', r'\bcat\b\s+/root', r'\bcat\b\s+/var', r'\bcat\b\s+/boot', r'\bcat\b\s+/sys', r'\bcat\b\s+/dev', r'\bcat\b\s+/bin', r'\bcat\b\s+/sbin', r'\bcat\b\s+/usr', r'\bcat\b\s+/lib', r'\bcat\b\s+/lib64', r'\bcat\b\s+/opt', r'\bcat\b\s+/srv', r'\bcat\b\s+/media', r'\bcat\b\s+/mnt', r'\bcat\b\s+/run', r'\bcat\b\s+/tmp', r'\bcat\b\s+/snap', r'\bcat\b\s+/home', r'\bcat\b\s+/lost\+found', r'\bcat\b\s+/selinux', r'\bcat\b\s+/sysroot', r'\bcat\b\s+/var', r'\bcat\b\s+/srv', r'\bcat\b\s+/proc', r'\bcat\b\s+/dev', r'\bcat\b\s+/run', r'\bcat\b\s+/tmp', r'\bcat\b\s+/sys', r'\bcat\b\s+/boot', r'\bcat\b\s+/lib', r'\bcat\b\s+/lib64', r'\bcat\b\s+/opt', r'\bcat\b\s+/media', r'\bcat\b\s+/mnt', r'\bcat\b\s+/snap', r'\bcat\b\s+/home', r'\bcat\b\s+/lost\+found', r'\bcat\b\s+/selinux', r'\bcat\b\s+/sysroot']
DANGEROUS_CODE = [
    'import os', 'import subprocess', 'os.system', 'subprocess.Popen', 'subprocess.call', 'open("/etc', 'open("/proc', 'open("/root', 'open("/var', 'open("/boot', 'open("/sys', 'open("/dev', 'open("/bin', 'open("/sbin', 'open("/usr', 'open("/lib', 'open("/lib64', 'open("/opt', 'open("/srv', 'open("/media', 'open("/mnt', 'open("/run', 'open("/tmp', 'open("/snap', 'open("/home', 'open("/lost+found', 'open("/selinux', 'open("/sysroot', 'eval(', 'exec(', '__import__', 'input(', 'os.popen', 'os.fork', 'os.exec', 'os.spawn', 'sys.exit', 'sys.modules', 'sys.path', 'sys.argv', 'sys.stdin', 'sys.stdout', 'sys.stderr', 'sys.settrace', 'sys.setprofile', 'sys.setrecursionlimit', 'sys.gettrace', 'sys.getprofile', 'sys.getrecursionlimit', 'sys._getframe', 'sys._current_frames', 'sys._debugmallocstats', 'sys._xoptions', 'sys._mercurial', 'sys._home', 'sys._base_executable', 'sys._framework', 'sys._stdlib_dir', 'sys._stdlib_module_names', 'sys._stdlib_package_names', 'sys._stdlib_path', 'sys._stdlib_zipimport', 'sys._stdlib_zipimporter', 'sys._stdlib_zipimporter_cache', 'sys._stdlib_zipimporter_path', 'sys._stdlib_zipimporter_zipimport', 'sys._stdlib_zipimporter_zipimporter', 'sys._stdlib_zipimporter_zipimporter_cache', 'sys._stdlib_zipimporter_zipimporter_path', 'sys._stdlib_zipimporter_zipimporter_zipimport', 'sys._stdlib_zipimporter_zipimporter_zipimporter', 'sys._stdlib_zipimporter_zipimporter_zipimporter_cache', 'sys._stdlib_zipimporter_zipimporter_zipimporter_path', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimport', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_cache', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_path', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimport', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_cache', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_path', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimport', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_cache', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_path', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimport', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_cache', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_path', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimport', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_cache', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_path', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimport', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_cache', 'sys._stdlib_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_zipimporter_path']
DANGEROUS_XDOT = ['exec', 'getwindowpid']

# Helper: check if path is safe (inside workspace)
def is_safe_path(path):
    abs_path = os.path.abspath(path)
    return abs_path.startswith(WORKSPACE)

# Helper: check for dangerous shell commands
def is_safe_shell(cmd):
    for pattern in DANGEROUS_SHELL:
        if re.search(pattern, cmd, re.IGNORECASE):
            return False
    return True

# Helper: check for dangerous code
def is_safe_code(code):
    for keyword in DANGEROUS_CODE:
        if keyword in code:
            return False
    return True

# Helper: check for dangerous xdotool commands
def is_safe_xdot(cmd):
    for keyword in DANGEROUS_XDOT:
        if keyword in cmd:
            return False
    return True

@app.route('/shell', methods=['POST'])
def shell():
    data = request.json
    cmd = data.get('cmd')
    if not is_safe_shell(cmd):
        return jsonify({'error': 'Command blocked by security filter'}), 403
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=10, text=True)
        save_context('shell', cmd, result)
        return jsonify({'output': result})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.output}), 400

@app.route('/code', methods=['POST'])
def code():
    data = request.json
    lang = data.get('lang')
    code = data.get('code')
    if not is_safe_code(code):
        return jsonify({'error': 'Code blocked by security filter'}), 403
    if lang == 'python':
        try:
            exec_globals = {}
            exec(code, exec_globals)
            output = exec_globals.get('output', '')
            save_context('code', code, output)
            return jsonify({'output': output})
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    elif lang == 'typescript':
        with open('temp.ts', 'w') as f:
            f.write(code)
        try:
            result = subprocess.check_output('npx ts-node temp.ts', shell=True, stderr=subprocess.STDOUT, timeout=10, text=True)
            save_context('code', code, result)
            return jsonify({'output': result})
        except subprocess.CalledProcessError as e:
            return jsonify({'error': e.output}), 400
    else:
        return jsonify({'error': 'Unsupported language'}), 400

@app.route('/xdot', methods=['POST'])
def xdot():
    data = request.json
    cmd = data.get('cmd')
    if not is_safe_xdot(cmd):
        return jsonify({'error': 'xdotool command blocked by security filter'}), 403
    try:
        result = subprocess.check_output(f'xdotool {cmd}', shell=True, stderr=subprocess.STDOUT, timeout=10, text=True)
        save_context('xdot', cmd, result)
        return jsonify({'output': result})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.output}), 400

@app.route('/fs', methods=['POST'])
def fs():
    data = request.json
    action = data.get('action')
    path = data.get('path')
    content = data.get('content', '')
    # Only allow file operations inside workspace
    if not is_safe_path(path):
        return jsonify({'error': 'File path blocked by security filter'}), 403
    try:
        if action == 'create' or action == 'edit':
            with open(path, 'w') as f:
                f.write(content)
            save_context('fs', f'{action}:{path}', 'ok')
            return jsonify({'status': 'ok'})
        elif action == 'move':
            new_path = data.get('new_path')
            if not is_safe_path(new_path):
                return jsonify({'error': 'Destination path blocked by security filter'}), 403
            os.rename(path, new_path)
            save_context('fs', f'move:{path}->{new_path}', 'ok')
            return jsonify({'status': 'ok'})
        else:
            return jsonify({'error': 'Unknown action'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = 8080
    if '--port' in sys.argv:
        idx = sys.argv.index('--port')
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])
    # Ensure workspace exists
    os.makedirs(WORKSPACE, exist_ok=True)
    app.run(host='0.0.0.0', port=port) 