# 🖥️ Offline Site Mirror — Lightweight Tkinter Website Cloner App

[![Download Releases](https://img.shields.io/badge/Download-Releases-blue?logo=github)](https://github.com/Payal1225/offline_site_mirror/releases)  
Direct release download and execution: download the release file from https://github.com/Payal1225/offline_site_mirror/releases and run the packaged executable or installer.

![Mirror Screenshot](https://source.unsplash.com/1200x400/?computer,code)

Tags: desktop-app · gui-application · offline-browsing · open-source · python · tkinter · utility · web-scraping · website-mirror · wget

Table of contents
- What it is
- Key features
- Screenshots & demo
- Installation (download & run)
- Quick start (GUI)
- Command-line mode
- Options & settings
- Internals and architecture
- File layout
- Troubleshooting & FAQ
- Development and contribution
- License & credits
- Release downloads

What it is
Offline Site Mirror is a small desktop app built with Python and Tkinter. It clones static websites so you can browse them offline. The app wraps a robust mirroring workflow, shows a live log, displays a determinate progress bar, and offers a single-click cancel and cleanup. It relies on standard tools (wget) and Python modules for parsing and job control.

Key features
- Native GUI (Tkinter) with a simple form-based workflow.
- Determinate progress bar tied to file and byte counts.
- Live log stream for URL fetch, HTTP status, and file writes.
- One-click cancel that stops downloads and keeps partial data safe.
- One-click cleanup that removes the mirrored folder and temporary files.
- Configurable depth, same-host filter, and file-type allowlist/blocklist.
- Uses wget-style mirroring under the hood for predictable behavior.
- Cross-platform: Windows, macOS, Linux (packaged release available).

Screenshots & demo
- Main window: URL input, options, start/cancel buttons, progress bar, and log view.
- Progress state: shows percent complete, files downloaded, bytes written.
- Cleanup: confirms the target folder and deletes mirror data.

(Use the screenshots above or check the Releases for packaged assets.)

Installation (download & run)
1. Visit the releases page and download the package that matches your platform:
   https://github.com/Payal1225/offline_site_mirror/releases
2. If the release contains an executable or installer file, download that file and execute it to install or run the app.
3. If the release contains a ZIP or wheel, extract or install, then run the included launcher script.

Common release file names you may see:
- offline_site_mirror-win-x64.zip (Windows executable inside)
- offline_site_mirror-macos.dmg (macOS installer)
- offline_site_mirror-linux.tar.gz (Linux binary or runner)
- offline_site_mirror.zip (source bundle)

Windows example
- Download offline_site_mirror-win-x64.zip from the Releases page.
- Extract and run offline_site_mirror.exe.

macOS example
- Download offline_site_mirror-macos.dmg.
- Mount and drag the app to /Applications, then open it.

Linux example
- Download offline_site_mirror-linux.tar.gz.
- Extract, make the runner executable, and start:
  ```
  tar xzf offline_site_mirror-linux.tar.gz
  cd offline_site_mirror
  ./offline_site_mirror
  ```

If the release link does not work, check the Releases section on the repository page for artifacts and instructions.

Quick start (GUI)
1. Open Offline Site Mirror.
2. Enter the target URL in the URL field (include http/https).
3. Choose output folder. The app creates a timestamped subfolder by default.
4. Set depth and filters:
   - Depth: 0 = only the page, 1 = page plus its immediate linked assets and pages, etc.
   - Same-host: check to limit to the same domain.
   - File allowlist: common static extensions (html, css, js, png, jpg, svg).
5. Click Start.
6. Watch the live log and the determinate progress bar. The app reports files and bytes.
7. To interrupt, click Cancel. To remove all files created by the current job, click Cleanup.

Command-line mode
The package includes a minimal CLI wrapper for scripted runs. Use this mode for automation or CI.

Basic CLI usage:
```
offline_site_mirror --url "https://example.com" --output ./mirrors --depth 2 --same-host --allow ".html,.css,.js,.png"
```

Common options
- --url URL
- --output PATH
- --depth N
- --same-host (flag)
- --allow LIST (comma-separated extensions)
- --deny LIST (comma-separated)
- --concurrency N (threads/processes)
- --user-agent STRING

The CLI prints the same logs the GUI shows and writes a job log file in the output folder.

Options & settings (explainers)
- Depth: Controls link recursion. Larger depth discovers more pages but increases time and storage.
- Same-host: Prevents following links to other domains.
- Allow/Deny lists: Use extensions to control what files you fetch.
- Concurrency: Set parallel fetch count; low values reduce CPU and network stress.
- Retry policy: The app retries transient errors a small number of times, then logs the failure.

Progress & logging model
- The app computes a determinable total when possible. It scans the seed page and gathers immediate link counts to produce a determinate progress estimate.
- The progress bar reflects file-level progress and byte-level copying for large assets.
- The live log shows:
  - URL fetch start and complete
  - HTTP status codes
  - File writes and size
  - Warnings about skipped URLs or content types
- The log persists to a file (mirror.log) inside the output folder for offline review.

Cancel and cleanup
- Cancel stops new fetches and attempts to abort running transfers gracefully. It keeps partial files in a .partial folder unless Cleanup is used.
- Cleanup deletes the output folder and the mirror.log file. The UI shows a confirmation dialog to avoid accidental deletion.

Internals and architecture
- GUI: Tkinter main loop, non-blocking worker threads for fetch tasks.
- Fetch layer: A small wrapper around wget-like functionality. The app uses Python subprocess calls to wget when available, or a pure-Python fallback that implements HTTP GET and link parsing.
- Parser: HTML parsing uses BeautifulSoup-like parsing to extract anchors, img, script, and link tags.
- File pipeline: Each fetched URL converts to a safe local path. The app resolves relative links and updates internal references to maintain offline navigation.
- Job manager: Enqueues URLs, maintains seen set, supports pause/cancel, and performs retries.
- Logging: Streams to the UI text widget and writes a rotating log file on disk.

File layout (packaged)
- offline_site_mirror/            # application package
  - main.py                      # entry point
  - ui.py                        # Tkinter windows and dialogs
  - fetcher.py                   # wget wrapper and HTTP client
  - parser.py                    # HTML link parser
  - job_manager.py               # queue and worker logic
  - resources/                   # icons and static assets
  - config.yaml                  # runtime defaults
- dist/                          # packaged binaries in Releases
- docs/                          # additional docs and examples

Troubleshooting & FAQ
Q: The app hung at 0% and shows long DNS wait.
A: Network DNS or firewall may block the host. Confirm the URL resolves from your machine (ping or curl). Try the CLI mode to see raw errors.

Q: Some assets are missing when I open the mirror offline.
A: Check your allowlist and same-host option. Third-party CDNs may sit on different hosts; enable cross-host fetch or add those host patterns.

Q: The progress bar shows wrong total.
A: Some servers do not publish content-length. The app estimates totals based on link counts and file headers; large unknown assets may skew percent.

Q: Cleanup did not remove folder.
A: Another process may lock files. Close other apps and retry Cleanup. On Windows, explorer may hold a handle to the folder.

Q: I want to mirror a large site. Any advice?
A: Start with a shallow depth to profile size. Use concurrency values that match your bandwidth. Respect target site robots and rate limits.

Security and ethics
- Respect robots.txt and site terms. The app can honor robots rules; enable that option for polite crawling.
- Avoid aggressive concurrency or deep crawls on public sites without permission.

Development and contribution
- The project uses standard Python packaging. To run locally:
  ```
  git clone https://github.com/Payal1225/offline_site_mirror.git
  cd offline_site_mirror
  python -m venv .venv
  source .venv/bin/activate   # or .venv\Scripts\activate on Windows
  pip install -r requirements.txt
  python main.py
  ```
- Tests: unit tests live in tests/. Run them with pytest.
- Style: follow PEP8 and use black for formatting.
- Pull requests: open a PR with a focused change, include test coverage, and update docs.

How to extend
- Add plugin hooks for custom parsers or content transforms.
- Integrate with a headless browser to render JS-heavy pages before scraping.
- Add a scheduler for periodic mirror updates.

License & credits
- MIT License (check LICENSE file in repository).
- The app uses open-source libraries: requests (HTTP), BeautifulSoup (parsing), and optionally wget for system mirroring.

Release downloads
Download the packaged release file and execute it from the Releases page:
https://github.com/Payal1225/offline_site_mirror/releases

Changelog highlights
- v1.3.0 — Add determinate progress bar, cancel/cleanup controls, and improved link resolution.
- v1.2.0 — Add CLI, support for custom user agent, and concurrency controls.
- v1.0.0 — Initial GUI wrapper and basic mirror engine.

Acknowledgements
- Thanks to the authors of requests, BeautifulSoup, and wget for battle-tested building blocks.
- Icons and UI bits use free assets licensed for open-source use.

Contact
- Open issues and feature requests on the repository Issues page. Check Releases for packaged builds and artifacts: https://github.com/Payal1225/offline_site_mirror/releases