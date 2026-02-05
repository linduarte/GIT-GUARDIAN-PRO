🛡️ Git Guardian Pro
Local-First Repository Monitoring with YubiKey Authentication

Lead Engineer: Charles Duarte

Status: Production Ready

🚀 Overview
Git Guardian Pro is a high-performance desktop application designed to provide hardware-authenticated visibility into local Git repositories. Built with Python and NiceGUI, and compiled via Nuitka, it ensures that "Work" and "Personal" contexts remain strictly separated based on the physical YubiKey connected to the machine.

📂 Project Structure

Git Guardian Pro is a standalone desktop application built with Python, NiceGUI, and Nuitka. It provides a secure, hardware-authenticated dashboard to monitor the status of local Git repositories based on which YubiKey is physically connected to the machine.

```plaintext
git-guardian-pro/
├── main.py               # UI Logic & NiceGUI Page Definition
├── guardian_service.py   # Hardware & Config Logic (YubiKey/JSON)
├── generate_repos.py     # Option B: Automated Sync to main.dist
├── .gitignore            # Excludes main.dist/ and main.build/
└── main.dist/            # The Standalone Distribution Folder
    ├── main.exe          # The Guardian Executable
    └── repos.json        # Live configuration (Generated here)
```

```

🛠️ Maintenance & Deployment Checklists
(A) To Recreate the Standalone Executable
Clean Workspace: Close the app and run Remove-Item -Recurse -Force main.dist, main.build.

Verify Source: Run uv run main.py to check logic.

Compile: 

```powershell
uv run python -m nuitka `
    --standalone `
    --plugin-enable=tk-inter `
    --include-package-data=nicegui `
    --remove-output `
    --windows-disable-console `
    main.py
```

#### **(B) To Update Repository List (repos.json)**

1. **Configure:** Update `structure` in `generate_repos.py` if your D: drive paths have changed.

2. **Sync:** Run `uv run generate_repos.py`. This automatically injects the JSON into `main.dist/`.

3. **Refresh:** If the app is running, wait 5 seconds for the automatic refresh.

---

### 🚨 Troubleshooting (The "Ghost" Guide)

- **Port Conflict (10048):** Run `Stop-Process -Name "main"`.

- **Internal Server Error:** Ensure the `--include-package-data=nicegui` flag was used during build.

- **Invisible Repos:** Check if the YubiKey serial in `repos.json` matches the plugged-in hardware.

---

### 🔧 Technology Stack

- **Runtime:** Python 3.12+ (managed by `uv`)

- **UI Framework:** NiceGUI (FastAPI + Tailwind CSS)

- **Compiler:** Nuitka (Standalone Mode)

- **Hardware:** YubiKey 5 Series (via `ykman`)

---

### 🛡️ Core Principle

> "The goal of this tool is absolute control. By mapping physical hardware to local file paths, we ensure that work data stays in the work context and personal data stays in the personal context, all while maintaining a clean, automated dashboard."