import os
import json
# import subprocess

def generate():
    # Definição das raízes de busca e seriais vinculados [cite: 2]
    structure = {
        "pessoal": {"root": r"D:\reposground\personal", "serial": "27757828"},
        "work": {"root": r"D:\reposground\work", "serial": "23959486"}
    }

    repos_config = {}
    
    # Injeção direta no main.dist e na raiz para suporte ao executável [cite: 6, 7]
    dist_folder = 'main.dist'
    if not os.path.exists(dist_folder):
        os.makedirs(dist_folder)

    for category, info in structure.items():
        root_path = info["root"]
        if not os.path.exists(root_path):
            continue

        repos_config[category] = []
        
        # Varredura imediata de subdiretórios em busca de pastas .git [cite: 4]
        for folder in os.listdir(root_path):
            full_path = os.path.join(root_path, folder)
            if os.path.isdir(os.path.join(full_path, ".git")):
                repos_config[category].append({
                    "name": folder,
                    "path": full_path.replace("\\", "/"), # Normalização para JSON [cite: 5]
                    "serial": info["serial"]
                })

    # Salva o arquivo em ambos os locais para garantir consistência
    for path in ['repos.json', os.path.join(dist_folder, 'repos.json')]:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(repos_config, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    generate()