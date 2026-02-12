import os
import sys
import subprocess
import json
# from git import Repo

class GuardianService:
    def __init__(self):
        # Determina o diretório base para localizar o repos.json em modo script ou EXE [cite: 21, 22]
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.config_path = os.path.join(self.base_dir, 'repos.json')

    def get_connected_serials(self) -> list[str]:
        """Captura os seriais das YubiKeys conectadas via ykman[cite: 23, 24]."""
        try:
            res = subprocess.run(["ykman", "list", "--serials"], 
                                 capture_output=True, text=True, timeout=1)
            return [s.strip() for s in res.stdout.strip().split('\n') if s.strip()]
        except Exception:
            return []

    def load_config(self):
        """Carrega a configuração dos repositórios ou retorna um dicionário vazio em caso de erro[cite: 25]."""
        try:
            if not os.path.exists(self.config_path):
                return {}
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    # Adicione este método ao final da classe GuardianService no seu arquivo
    def remove_repo_entry(self, category: str, path_to_remove: str) -> bool:
        """Remove um repositório específico do arquivo JSON e salva."""
        data = self.load_config()
        if category in data:
            # Filtra para manter apenas os que NÃO coincidem com o path deletado
            data[category] = [r for r in data[category] if r['path'] != path_to_remove]
            try:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                print(f"🗑️ Removido do JSON: {path_to_remove}")
                return True
            except Exception as e:
                print(f"❌ Erro ao salvar JSON: {e}")
                return False
        return False