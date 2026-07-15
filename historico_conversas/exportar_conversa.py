import os
import json
import sys

def exportar():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    conversa_id = "a5afec72-7331-4847-b241-408d00397ff0"
    
    # Tentamos primeiro o transcript_full.jsonl para ter certeza de pegar o texto sem truncamento
    log_path = rf"C:\Users\Adriano-pc\.gemini\antigravity-ide\brain\{conversa_id}\.system_generated\logs\transcript_full.jsonl"
    if not os.path.exists(log_path):
        log_path = rf"C:\Users\Adriano-pc\.gemini\antigravity-ide\brain\{conversa_id}\.system_generated\logs\transcript.jsonl"
        
    if not os.path.exists(log_path):
        print(f"Log nao encontrado em: {log_path}")
        return
        
    dialogo = []
    
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            try:
                data = json.loads(line)
                source = data.get("source", "")
                step_type = data.get("type", "")
                content = data.get("content", "")
                
                # USER_INPUT do USER_EXPLICIT representa o prompt enviado pelo usuario
                if step_type == "USER_INPUT" and source == "USER_EXPLICIT":
                    dialogo.append(("Usuário", content))
                # PLANNER_RESPONSE do MODEL representa a resposta de texto do assistente
                elif step_type == "PLANNER_RESPONSE" and source == "MODEL":
                    dialogo.append(("Assistente", content))
            except Exception as e:
                pass
                
    output_file = r"c:\Apps\var-code\conversa_japones_2026-07-13.md"
    
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("# 📝 Histórico de Conversa (Tradução Japonês)\n\n")
        out.write(f"- **Data de Execução:** 13 de Julho de 2026\n")
        out.write(f"- **ID da Sessão Original:** `{conversa_id}`\n\n")
        out.write("---\n\n")
        
        for autor, texto in dialogo:
            # Pula mensagens vazias ou de sistema caso apareçam
            if not texto.strip():
                continue
                
            out.write(f"## 👤 {autor}\n\n")
            out.write(f"{texto}\n\n")
            out.write("---\n\n")
            
    print(f"Sucesso! Conversa salva em: {output_file}")

if __name__ == "__main__":
    exportar()
