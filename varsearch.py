from vitaldb import VitalFile
import os
import json
import sys
import gc

DIRECTORY = "./records/"
MODES = ["tabular", "wave"]
FILENAME = "./records/vital_tracks.txt"

def load_configs():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cfg_path = os.path.join(base_dir, 'model.json')
    with open(cfg_path) as f:
        configs = json.load(f)
    for cfg in configs:
        cfg['model'] = None  # Lazy loading posterior
    return configs

def search_vital_files(variables):

    found = []
    for root, _, files in os.walk(DIRECTORY):

        for file in files:
            if file.endswith('.vital'):
                vital_path = os.path.normpath(os.path.join(root, file))
                try:
                    tracks = VitalFile(vital_path, maxlen=12).get_track_names()
                    save_to_file(vital_path, tracks)
                    if all(var in tracks for var in variables):
                        print(f"Archivo válido encontrado: {vital_path}")
                        found.append(vital_path)
                    #else:
                        #print(f"Archivo {vital_path} no contiene todas las variables requeridas.")
                except Exception as e:
                    print(f"[ERROR] No se pudo leer {vital_path}: {e}")
                finally:
                    gc.collect()

def save_to_file(vital_path, tracks):
    # Check if the file was already saved
    already_saved = False
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            for line in f:
                if line.startswith(f"{vital_path},"):
                    already_saved = True
                    break
    if not already_saved:
        with open(FILENAME, "a") as f:
            f.write(f"{vital_path},{','.join(tracks)}\n")

def search_text_file(variables):
    found = []
    with open(FILENAME, "r") as f:
        for line in f:
            parts = line.strip().split(',')
            vital_path = parts[0]
            tracks = parts[1:]
            if all(var in tracks for var in variables):
                print(f"Archivo válido encontrado en texto: {vital_path}")
                found.append(vital_path)
    return found

def search(variables):
    
    if os.path.exists(FILENAME):
        return search_text_file(variables)
    else:
        print(f"Archivo {FILENAME} no encontrado. Parseando archivos .vital...")
        return search_vital_files(variables)
    
if __name__ == "__main__":
    configs = load_configs()

    if len(sys.argv) != 2 or sys.argv[1] not in MODES:
        print("Uso: python varsearch.py [tabular|wave]")
        sys.exit(1)
    
    if(sys.argv[1] == "tabular"):
        variables = [var for cfg in configs if cfg.get('input_type') == 'tabular' for var in cfg.get('input_vars', [])]
        print("Buscando archivos .vital con las variables tabulares:", variables)
    else:
        variables = [cfg.get('signal_track') for cfg in configs if cfg.get('input_type') == 'wave']
        print("Buscando archivos .vital con las variables de onda:", variables)
    
    search(variables)
