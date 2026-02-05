import os
# import sys
import subprocess
from nicegui import ui
from guardian_service import GuardianService

# --- 1. INITIALIZATION ---
service = GuardianService()

# --- 2. GIT LOGIC ---
def get_git_status(repo_path):
    """Checks the local git status of a repository."""
    if not os.path.exists(repo_path):
        return "error"
    try:
        # Check for modified/untracked files
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            shell=True
        )
        if result.stdout.strip() == "":
            return "clean"    # Green
        else:
            return "modified" # Yellow
    except Exception:
        return "error"        # Red

# --- 3. UI COMPONENTS ---
def create_repo_card(repo, is_key_active):
    """Creates a repository card with a status indicator light."""
    repo_path = repo.get('path', '')
    
    # Determine Status and Color
    status = get_git_status(repo_path) if is_key_active else "inactive"
    
    status_map = {
        "clean": {"color": "#4ade80", "label": "Clean"},      # Green
        "modified": {"color": "#fbbf24", "label": "Pending"}, # Yellow
        "error": {"color": "#f87171", "label": "Error"},      # Red
        "inactive": {"color": "#475569", "label": "Locked"}   # Gray
    }
    
    current = status_map.get(status, status_map["error"]) or status_map["error"]
    card_opacity = "opacity-100" if is_key_active else "opacity-50"

    with ui.card().classes(f'w-full bg-slate-800 border-l-4 border-blue-500 mb-2 {card_opacity}'):
        with ui.row().classes('w-full justify-between items-center'):
            with ui.row().classes('items-center gap-3'):
                # The Status Light (The 'Bingo' element)
                ui.icon('circle', color=current['color']).classes('text-[12px]')
                
                with ui.column().classes('gap-0'):
                    ui.label(repo.get('name', 'UNKNOWN').upper()).classes('font-bold text-slate-100')
                    ui.label(repo_path).classes('text-[10px] text-slate-400 font-mono')
            
            with ui.row().classes('items-center gap-2'):
                ui.label(current['label']).classes('text-[8px] font-black text-slate-500')
                ui.button(icon='folder', on_click=lambda: os.startfile(repo_path)) \
                    .props('flat round size=sm').classes('text-blue-400')

# --- 4. THE MAIN PAGE ---
@ui.page('/')
def main_page():
    ui.dark_mode().enable()
    
    # Refresh hardware and data state
    serials = [str(s) for s in service.get_connected_serials()]
    config = service.load_config()

    # --- HEADER ---
    with ui.header().classes('bg-slate-900 justify-between items-center px-6 py-4'):
        ui.label('🛡️ GIT GUARDIAN PRO').classes('text-xl font-bold tracking-tight')
        
        with ui.row().classes('items-center bg-slate-800 px-4 py-1 rounded-full border border-slate-700'):
            is_any_key = len(serials) > 0
            label_text = "KEY ACTIVE" if is_any_key else "NO KEY"
            icon_color = "#4ade80" if is_any_key else "#f87171"
            
            ui.label(label_text).classes('text-[10px] font-black mr-2')
            ui.icon('vpn_key', color=icon_color).classes('text-xl')

    # --- CONTENT ---
    with ui.column().classes('w-full max-w-4xl mx-auto p-6 gap-2'):
        for category, repos in config.items():
            
            # 1. Create a list of repos that actually match the plugged-in keys
            active_repos_in_category = [
                r for r in repos 
                if str(r.get('serial', '')) in serials
            ]

            # 2. Only show the category label if there is at least one active repo
            if active_repos_in_category:
                ui.label(category.upper()).classes('text-xs font-black text-slate-500 mt-4 tracking-widest')
                
                for repo in active_repos_in_category:
                    # Now we only call this for authorized repos
                    create_repo_card(repo, is_key_active=True)

    # --- FOOTER ---
    with ui.footer().classes('bg-slate-900/50 text-slate-600 text-[10px] justify-center'):
        ui.label(f"Guardian V2.0 | Path: {service.config_path}")

# --- 5. RUN ---
ui.run(port=8085, native=False, reload=False, title="Git Guardian Pro")

# This will refresh the entire page every 5 seconds 
# so you don't have to press F5 when you swap YubiKeys
ui.timer(5.0, lambda: ui.navigate.to('/'))