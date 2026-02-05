import os
import json
import subprocess

def get_yubikey_serial():
    """Helper to get the connected YubiKey serial for verification (optional)."""
    try:
        result = subprocess.run(['ykman', 'list'], capture_output=True, text=True, shell=True)
        return result.stdout.strip()
    except Exception:
        return "Not Found"

def generate():
    # 1. Configuration: Define your Roots and Serials
    # Note: Use raw strings (r"") for Windows paths to avoid escape character issues
    structure = {
        "pessoal": {
            "root": r"D:\reposground\personal", 
            "serial": "27757828"
        },
        "work": {
            "root": r"D:\reposground\work", 
            "serial": "23959486" # Update with your work key serial
        }
    }

    repos_config = {}

    print("--- 🔍 Scanning Repositories ---")

    for category, info in structure.items():
        root_path = info["root"]
        serial = info["serial"]
        
        if not os.path.exists(root_path):
            print(f"⚠️ Warning: Root path not found for {category}: {root_path}")
            continue

        repos_config[category] = []
        
        # Scan immediate subdirectories for .git folders
        for folder in os.listdir(root_path):
            full_path = os.path.join(root_path, folder)
            git_path = os.path.join(full_path, ".git")

            if os.path.isdir(git_path):
                # Clean up path for JSON (use forward slashes for cross-platform safety)
                clean_path = full_path.replace("\\", "/")
                
                repo_entry = {
                    "name": folder,
                    "path": clean_path,
                    "serial": serial
                }
                repos_config[category].append(repo_entry)
                print(f"✅ Found [{category}]: {folder}")

    # 2. Option B Logic: Direct Injection into main.dist
    dist_folder = 'main.dist'
    
    # Ensure the distribution folder exists (prevents errors during first build)
    if not os.path.exists(dist_folder):
        os.makedirs(dist_folder)
        print(f"📁 Created directory: {dist_folder}")

    target_file = os.path.join(dist_folder, 'repos.json')

    # 3. Save the JSON
    try:
        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump(repos_config, f, indent=4, ensure_ascii=False)
        print("\n========================================")
        print(f"🚀 BINGO! Configuration injected to: {target_file}")
        print(f"📊 Total repositories mapped: {sum(len(v) for v in repos_config.values())}")
        print("========================================")
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")

if __name__ == "__main__":
    generate()