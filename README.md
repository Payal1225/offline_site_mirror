# Offline-Site-Mirror

A tiny Tkinter desktop app that lets you **mirror any static website for offline browsing** with one click.  
Under the hood it calls `wget2` and drops the mirror into the folder you choose—ready to open in any browser while you’re completely offline.

---

## Features

* **Point-and-click UI** – enter URL ➜ pick a directory ➜ *Extract*  
* **Link rewriting** – mirrored pages keep working offline (`wget2 --convert-links`)  
* **Resumable** – re-run on the same folder later to grab only new/changed files  
* **Modular code** – all download logic lives in `utils/downloader.py`, so you can swap `wget2` for another crawler without touching the GUI

---

## Prerequisites

| Tool | Windows install command |
|------|-------------------------|
| **Python 3.9+** | <https://python.org/downloads/> (tick “Add to PATH”) |
| **wget2** | `winget install -e --id GNU.Wget2`<br>*(or `choco install wget2` / Git-for-Windows includes classic wget)* |

> **CA bundle (optional):**  
> If wget2 prints *“No CAs were found”* warnings, point it at Git’s bundle:<br>
> `setx SSL_CERT_FILE "C:\Program Files\Git\mingw64\ssl\certs\ca-bundle.crt"`


## Setup

```powershell
# 1 — clone the repo
git clone https://github.com/your-username/offline_site_mirror.git
cd offline_site_mirror

# 2 — create a virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate        # or source venv/bin/activate on Linux/Mac

# 3 — install Python deps (just Tkinter; ships with CPython on Windows)
pip install -r requirements.txt

# 4 — run the app
python app.py

Usage
Website URL – paste the root URL you want to mirror

Save to folder – browse to (or type) the directory where the mirror should live

Click Extract

While the crawl runs you’ll see a verbose log in the console.
Files appear under:

php-template

<chosen folder>\www.example.com\index.html
You can open index.html immediately—wget2 writes each file as soon as it finishes.

Troubleshooting
Symptom	Fix
“wget2 not found”	Make sure it’s on PATH (winget install …), then open a new terminal.
CA bundle warning	Set SSL_CERT_FILE or add --ca-certificate inside utils/downloader.py.
Mirror appears under C%3A\Users\…	Use forward-slashes in paths or run the app from inside the target folder (no --directory-prefix).

Extending
Progress bar – spawn mirror_site() in a thread and poll stderr for [Files: stats

Authenticated mirrors – add --user --password flags in downloader.py

Pure-Python crawler – replace the wget2 command with your own requests + BeautifulSoup walk


License MIT © 2025 Tiān Jié Héng Feel free to fork, and fuck off! :)
