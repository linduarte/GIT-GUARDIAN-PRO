import os
import subprocess
from nicegui import ui
from guardian_service import GuardianService

# --- 1. INITIALIZATION ---
# Adicione a anotação de tipo : GuardianService para o VS Code reconhecer os métodos
service: GuardianService = GuardianService()

# --- 2. GESTÃO ATIVA (Wrapper Seguro) ---
async def handle_repo_removal(category: str, path: str):
    """
    Versão assíncrona para evitar o crash de conexão (WinError 10054).
    """
    if service and hasattr(service, 'remove_repo_entry'):
        # 1. Executa a remoção
        success = service.remove_repo_entry(category, path)
        
        if success:
            ui.notify(f"Registro removido: {os.path.basename(path)}", type='positive')
            # 2. Pequena pausa para garantir que o IO do arquivo liberou o sistema
            await ui.run_javascript('console.log("Refreshing UI...")') 
            render_content.refresh()
        else:
            ui.notify("Falha ao atualizar o arquivo JSON", type='negative')

def get_git_status(repo_path):
    """Verifica se o diretório existe e retorna o status do Git."""
    if not os.path.exists(repo_path):
        return "ghost" # Caso o repositório tenha sido deletado do disco
    try:
        result = subprocess.run(['git', 'status', '--porcelain'],
                                cwd=repo_path, capture_output=True, text=True, shell=True)
        return "clean" if not result.stdout.strip() else "modified"
    except Exception:
        return "error"

@ui.refreshable
def render_content():
    serials = service.get_connected_serials()
    config = service.load_config()

    with ui.column().classes('w-full max-w-4xl mx-auto p-6 gap-2'):
        for category, repos in config.items():
            # Filtra apenas os autorizados pela chave conectada
            active_repos = [r for r in repos if str(r.get('serial')) in serials]

            if active_repos:
                ui.label(category.upper()).classes('text-xs font-black text-slate-500 mt-4')
                for repo in active_repos:
                    path = repo.get('path', '')
                    status = get_git_status(path)
                    
                    # Definição visual baseada na integridade física e git
                    is_ghost = (status == "ghost")
                    card_color = 'border-red-600 bg-red-900/20' if is_ghost else 'border-blue-500 bg-slate-800'
                    
                    with ui.card().classes(f'w-full {card_color} mb-2'):
                        with ui.row().classes('w-full justify-between items-center'):
                            with ui.row().classes('items-center gap-3'):
                                # Status visual Bingo: Verde (OK), Amarelo (Pendente), Vermelho (Erro/Fantasma)
                                dot_color = "#f87171" if is_ghost else ("#4ade80" if status == "clean" else "#fbbf24")
                                ui.icon('circle', color=dot_color).classes('text-[12px]')
                                ui.label(repo.get('name', 'UNKNOWN').upper()).classes('font-bold text-slate-100')
                            
                            # Botão de Gestão Ativa: Aparece apenas se o repo sumiu do disco
                            # No loop de cards do main.py
                            if is_ghost:
                                ui.button(
                                    icon='delete_forever', 
                                    on_click=lambda c=category, p=path: handle_repo_removal(c, p)
                                ).props('flat round color=red').tooltip('Remover registro órfão do JSON')
                            else:
                                ui.button(icon='folder', on_click=lambda p=path: os.startfile(p)).props('flat round size=sm')

@ui.page('/')
def main_page():
    ui.dark_mode().enable()
    # Header dinâmico para status da chave
    with ui.header().classes('bg-slate-900 justify-between items-center px-6'):
        ui.label('🛡️ GIT GUARDIAN PRO').classes('text-xl font-bold')
        # No main.py, dentro da main_page()
        # Altere a linha do ícone no header para executar a função corretamente
        ui.icon('vpn_key', color="#4ade80").bind_visibility_from(
            service, 
            'get_connected_serials', 
            backward=lambda x: len(x()) > 0 if callable(x) else len(x) > 0
        )

    render_content()
    # Atualização automática a cada 5 segundos para refletir trocas de YubiKey
    ui.timer(5.0, render_content.refresh)

# Aumentamos o storage_secret e garantimos que o reload não cause loops
ui.run(
    port=8085, 
    title="Git Guardian Pro", 
    reload=False, 
    show=True,
    storage_secret='guardian_secret_key' # Ajuda a manter a sessão estável
)