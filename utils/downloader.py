# utils/downloader.py
"""
Thin wrapper around wget2 for mirroring static sites.
Keeps the command in one place so the GUI stays clean.
"""

import shutil
import subprocess
from pathlib import Path

# OPTIONAL: point to a CA bundle if wget2 warns about certificates.
CA_BUNDLE = r"C:/Program Files/Git/mingw64/ssl/certs/ca-bundle.crt"  # adjust or set to None

def wget_available(bin_name: str = "wget2") -> bool:
    return shutil.which(bin_name) is not None


def mirror_site(url: str, output_dir: Path, bin_name: str = "wget2") -> subprocess.CompletedProcess:
    """
    Mirror `url` into `output_dir` using wget2.
    Returns subprocess.CompletedProcess (stdout/stderr captured).
    """
    if not wget_available(bin_name):
        raise FileNotFoundError(f"'{bin_name}' not found in PATH. Install wget2 or tweak bin_name.")

    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        bin_name,
        "--verbose",
        "--mirror",
        "--convert-links",
        "--adjust-extension",
        "--page-requisites",
        "--no-parent",
        "-e", "robots=off",
        "--wait=1",
        f"--directory-prefix={output_dir.as_posix()}",
        url,
    ]

    if CA_BUNDLE:
        cmd.insert(1, f"--ca-certificate={CA_BUNDLE}")

    return subprocess.run(cmd, capture_output=True, text=True, check=False)
