import subprocess, os
from pathlib import Path
import yaml

class OSController:
    def __init__(self, policy_path: str = "policy.yaml"):
        self.policy = yaml.safe_load(Path(policy_path).read_text())
        self.allowed_dirs = [Path(os.path.expandvars(p)).resolve()
                             for p in self.policy["system"]["allowed_dirs"]]
        self.allowed_editors = set(self.policy["system"]["allowed_editors"])

    def _allowed_path(self, path: str) -> bool:
        p = Path(path).resolve()
        for d in self.allowed_dirs:
            try:
                p.relative_to(d)
                return True
            except ValueError:
                continue
        return False

    def run_shell(self, cmd: str, cwd: str = None, timeout: int = 60):
        if self.policy["system"].get("confirm_shell", True):
            print(f"[confirm] Run: {cmd} (cwd={cwd or os.getcwd()}) ? (y/N) ", end="")
            if input().strip().lower() != "y":
                return {"ok": False, "error": "shell denied"}
        r = subprocess.run(cmd, shell=True, cwd=cwd,
                           capture_output=True, text=True, timeout=timeout)
        return {
            "ok": r.returncode == 0,
            "code": r.returncode,
            "stdout": r.stdout[-20000:],
            "stderr": r.stderr[-20000:]
        }

    def open_in_editor(self, path: str, editor: str = "code"):
        if editor not in self.allowed_editors:
            return {"ok": False, "error": f"editor {editor} not allowed"}
        if not self._allowed_path(path):
            return {"ok": False, "error": "path outside allowed_dirs"}
        r = subprocess.run([editor, path], capture_output=True, text=True)
        return {"ok": r.returncode == 0, "stdout": r.stdout, "stderr": r.stderr}

    def write_file(self, path: str, content: str):
        if not self._allowed_path(path):
            return {"ok": False, "error": "path outside allowed_dirs"}
        if self.policy["system"].get("confirm_write", True):
            print(f"[confirm] Write file {path}? (y/N) ", end="")
            if input().strip().lower() != "y":
                return {"ok": False, "error": "write denied"}
        p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"ok": True, "path": str(p.resolve())}
