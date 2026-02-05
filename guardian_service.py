import os
import sys
import subprocess
import json
from git import Repo

class GuardianService:
    def __init__(self):
        # This is the most reliable way to find the EXE folder
        if getattr(sys, 'frozen', False):
            # If running as EXE
            self.base_dir = os.path.dirname(sys.executable)
        else:
            # If running as Script
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.config_path = os.path.join(self.base_dir, 'repos.json')
        
        # LOGGING: This will definitely show up in your PowerShell
        print(f"\n{'='*20}")
        print("SERVICE STARTING...")
        print(f"BASE DIR: {self.base_dir}")
        print(f"CONFIG PATH: {self.config_path}")
        print(f"CONFIG EXISTS: {os.path.exists(self.config_path)}")
        print(f"{'='*20}\n")

    def get_connected_serials(self) -> list[str]:
        """Harvested logic from your ykman subprocess call."""
        try:
            res = subprocess.run(["ykman", "list", "--serials"], 
                                 capture_output=True, text=True, timeout=1)
            return [s.strip() for s in res.stdout.strip().split('\n') if s.strip()]
        except Exception:
            return []

    def load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"FAILED TO LOAD JSON: {e}")
            return {} # Return empty dict instead of crashing

    def get_repo_details(self, path: str):
        """Harvested logic from your GitPython check."""
        try:
            repo = Repo(os.path.normpath(path))
            modified = len(repo.index.diff(None))
            untracked = len(repo.untracked_files)
            has_remote = len(repo.remotes) > 0
            
            return {
                "status": "Changes" if (modified > 0 or untracked > 0) else "Clean",
                "message": f"{modified} Mod | {untracked} New" if (modified > 0 or untracked > 0) else "✓ Synced",
                "has_remote": has_remote
            }
        except Exception:
            return {"status": "Error", "message": "Git Error", "has_remote": False}