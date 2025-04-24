import os

def get_aid_list(base_path):
    try:
        directorios = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        return directorios
    except FileNotFoundError:
        print(f"El directorio {base_path} no existe.")
        return []