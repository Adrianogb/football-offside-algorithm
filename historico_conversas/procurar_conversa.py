import os
import re
import datetime
import json
import sys

def buscar_conversas_japones():
    # Reconfigura a saida do console para UTF-8 para evitar problemas de charmap no Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    brain_dir = r"C:\Users\Adriano-pc\.gemini\antigravity-ide\brain"
    if not os.path.exists(brain_dir):
        print(f"Diretorio {brain_dir} nao existe.")
        return

    # Regex para caracteres japoneses: Hiragana, Katakana e Kanji
    jp_regex = re.compile(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]')
    
    resultados = []
    
    # Listar as pastas de conversas
    for folder in os.listdir(brain_dir):
        folder_path = os.path.join(brain_dir, folder)
        if not os.path.isdir(folder_path) or folder == "tempmediaStorage":
            continue
            
        transcript_path = os.path.join(folder_path, ".system_generated", "logs", "transcript.jsonl")
        if not os.path.exists(transcript_path):
            continue
            
        try:
            mtime = os.path.getmtime(transcript_path)
            dt_mod = datetime.datetime.fromtimestamp(mtime)
            
            com_jp = False
            trechos = []
            
            with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if jp_regex.search(line):
                        com_jp = True
                        try:
                            data = json.loads(line)
                            content = data.get("content", "")
                            if jp_regex.search(content):
                                content_clean = content.replace('\n', ' ')[:120]
                                trechos.append(content_clean)
                        except:
                            pass
            
            if com_jp:
                resultados.append({
                    "id": folder,
                    "data_mod": dt_mod,
                    "trechos": trechos[:3]
                })
        except Exception as e:
            pass

    resultados.sort(key=lambda x: x["data_mod"], reverse=True)
    
    print(f"=== RESULTADOS DA BUSCA (Total de conversas com Japones: {len(resultados)}) ===")
    for res in resultados:
        print(f"\nID da Conversa: {res['id']}")
        print(f"Data de Modificacao: {res['data_mod'].strftime('%Y-%m-%d %H:%M:%S')}")
        print("Trechos em Japones encontrados:")
        for t in res['trechos']:
            print(f"  - {t}")
        print("-" * 50)

if __name__ == "__main__":
    buscar_conversas_japones()
