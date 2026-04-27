from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def launch_generation(repo_root: Path) -> None:
    repo_root = Path(repo_root)
    command = ["cmd", "/k", sys.executable, "action_make_all.py"]
    creation_flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
    subprocess.Popen(
        command,
        cwd=str(repo_root),
        creationflags=creation_flags,
    )
