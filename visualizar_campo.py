import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
from futbol_impedimento import Jogador, Bola, verificar_impedimento

def desenhar_campo(ax):
    # Fundo verde escuro do gramado
    ax.fill_between([0, 105], [0, 0], [68, 68], color='#1b5e20', zorder=0)
    
    # Linhas de demarcação do campo (brancas)
    ax.plot([0, 105, 105, 0, 0], [0, 0, 68, 68, 0], color='white', linewidth=2.5, zorder=1)
    
    # Linha do meio de campo
    ax.plot([52.5, 52.5], [0, 68], color='white', linewidth=2.5, zorder=1)
    
    # Círculo central
    circulo_centro = patches.Circle((52.5, 34), 9.15, edgecolor='white', facecolor='none', linewidth=2.5, zorder=1)
    ax.add_patch(circulo_centro)
    ponto_centro = patches.Circle((52.5, 34), 0.5, color='white', zorder=1)
    ax.add_patch(ponto_centro)
    
    # Grande Área da Esquerda
    ax.plot([0, 16.5, 16.5, 0], [13.85, 13.85, 54.15, 54.15], color='white', linewidth=2.5, zorder=1)
    # Pequena Área da Esquerda
    ax.plot([0, 5.5, 5.5, 0], [24.85, 24.85, 43.15, 43.15], color='white', linewidth=2.5, zorder=1)
    
    # Grande Área da Direita
    ax.plot([105, 105-16.5, 105-16.5, 105], [13.85, 13.85, 54.15, 54.15], color='white', linewidth=2.5, zorder=1)
    # Pequena Área da Direita
    ax.plot([105, 105-5.5, 105-5.5, 105], [24.85, 24.85, 43.15, 43.15], color='white', linewidth=2.5, zorder=1)
    
    # Marca do pênalti
    penalti_esq = patches.Circle((11, 34), 0.3, color='white', zorder=1)
    penalti_dir = patches.Circle((105-11, 34), 0.3, color='white', zorder=1)
    ax.add_patch(penalti_esq)
    ax.add_patch(penalti_dir)
    
    # Arcos da grande área
    arco_esq = patches.Arc((11, 34), 18.3, 18.3, theta1=-53, theta2=53, color='white', linewidth=2.5, zorder=1)
    arco_dir = patches.Arc((105-11, 34), 18.3, 18.3, theta1=127, theta2=233, color='white', linewidth=2.5, zorder=1)
    ax.add_patch(arco_esq)
    ax.add_patch(arco_dir)


def gerar_grafico_impedimento(salvar_caminho: str):
    fig, ax = plt.subplots(figsize=(12, 8))
    desenhar_campo(ax)
    
    # Cenário de Teste: Impedimento Ativo
    # Time Defensor (B) - em vermelho
    goleiro = Jogador("B1", "Goleiro B", "Defensor", 102.0, 34.0)
    zagueiro = Jogador("B3", "Zagueiro B", "Defensor", 85.0, 22.0)
    lateral = Jogador("B4", "Lateral B", "Defensor", 88.0, 48.0)
    defensores = [goleiro, zagueiro, lateral]
    
    # Time Atacante (A) - em azul
    passador = Jogador("A10", "Meia A (Passador)", "Atacante", 45.0, 34.0)
    recebedor = Jogador("A9", "Centroavante A (Recebedor)", "Atacante", 92.0, 30.0)
    outro_atacante = Jogador("A7", "Ponta A", "Atacante", 87.0, 58.0)
    atacantes = [passador, recebedor, outro_atacante]
    
    bola = Bola(x=45.0, y=34.0)  # bola saindo do pé do passador (A10)
    
    # Verificar impedimento para o recebedor
    resultado = verificar_impedimento(
        jogador_alvo=recebedor,
        bola=bola,
        jogadores_time_defensor=defensores,
        tipo_passe="comum",
        participou_ativamente=True,
        direcao_ataque=1
    )
    
    # Plotar defensores (Círculos vermelhos)
    for defen in defensores:
        ax.scatter(defen.x, defen.y, color='#d32f2f', edgecolor='white', s=250, linewidths=2, zorder=3, label="Defensores (Time B)" if defen == goleiro else "")
        ax.text(defen.x, defen.y - 3, defen.id, color='white', fontsize=10, fontweight='bold', ha='center', zorder=4,
                bbox=dict(boxstyle="round,pad=0.2", facecolor='#d32f2f', edgecolor='none'))
        
    # Plotar atacantes (Círculos azuis, exceto o receptor que será destacado se estiver impedido)
    ax.scatter(passador.x, passador.y, color='#1976d2', edgecolor='white', s=250, linewidths=2, zorder=3, label="Atacantes (Time A)")
    ax.text(passador.x, passador.y - 3, passador.id, color='white', fontsize=10, fontweight='bold', ha='center', zorder=4,
            bbox=dict(boxstyle="round,pad=0.2", facecolor='#1976d2', edgecolor='none'))
            
    ax.scatter(outro_atacante.x, outro_atacante.y, color='#1976d2', edgecolor='white', s=250, linewidths=2, zorder=3)
    ax.text(outro_atacante.x, outro_atacante.y - 3, outro_atacante.id, color='white', fontsize=10, fontweight='bold', ha='center', zorder=4,
            bbox=dict(boxstyle="round,pad=0.2", facecolor='#1976d2', edgecolor='none'))

    # Plotar receptor (Roxo se estiver impedido, senão verde claro)
    cor_receptor = '#9c27b0' if resultado['impedido'] else '#4caf50'
    ax.scatter(recebedor.x, recebedor.y, color=cor_receptor, edgecolor='white', s=350, linewidths=2.5, zorder=4, label="Receptor do Passe")
    ax.text(recebedor.x, recebedor.y - 3.5, f"{recebedor.id} (Alvo)", color='white', fontsize=10, fontweight='bold', ha='center', zorder=4,
            bbox=dict(boxstyle="round,pad=0.2", facecolor=cor_receptor, edgecolor='none'))

    # Plotar a Bola (Círculo amarelo)
    ax.scatter(bola.x, bola.y, color='#ffeb3b', edgecolor='black', s=120, linewidths=1.5, zorder=5, label="Bola")
    
    # Desenhar linha do Passe (seta)
    ax.annotate("", xy=(recebedor.x - 2, recebedor.y), xytext=(passador.x + 2, passador.y),
                arrowprops=dict(arrowstyle="->", color='#ffeb3b', lw=2.5, ls='--', connectionstyle="arc3,rad=-0.1"), zorder=2)

    # Linha do penúltimo defensor (linha de impedimento em vermelho tracejado)
    linha_impedimento_x = resultado['detalhes']['linha_impedimento_x']
    ax.axvline(x=linha_impedimento_x, color='#d32f2f', linestyle=':', linewidth=2, zorder=2, label=f"Linha de Impedimento ({linha_impedimento_x:.1f}m)")
    
    # Preencher a zona de impedimento de vermelho claro e transparente
    ax.fill_betweenx([0, 68], linha_impedimento_x, 105, color='#d32f2f', alpha=0.15, zorder=1)

    # Legendas e detalhes do gráfico
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 68)
    ax.set_title(f"Visualização do Algoritmo de Impedimento (Lei 11)\nResultado: {resultado['motivo']}", fontsize=14, fontweight='bold', color='white', pad=15)
    
    # Adicionar placa de informações estilizada no canto inferior esquerdo
    info_text = (
        f"Regras Analisadas:\n"
        f"1. Metade adversária (>52.5m): {'SIM' if resultado['detalhes']['na_metade_ofensiva'] else 'NÃO'}\n"
        f"2. À frente da bola (>bola_x): {'SIM' if resultado['detalhes']['a_frente_da_bola'] else 'NÃO'}\n"
        f"3. À frente da defesa (>defesa_x): {'SIM' if resultado['detalhes']['a_frente_do_penultimo_defensor'] else 'NÃO'}\n"
        f"4. Tipo de passe: {resultado['detalhes']['tipo_passe'].upper()}\n"
        f"5. Participação ativa: {'SIM' if resultado['detalhes']['participou_ativamente'] else 'NÃO'}\n\n"
        f"Veredito: IMPEDIDO" if resultado['impedido'] else "Veredito: LEGAL"
    )
    
    ax.text(5, 5, info_text, color='white', fontsize=10, fontfamily='monospace',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='#212121', edgecolor='white', alpha=0.9), zorder=6)

    # Ajuste de layout e cores de fundo do canvas
    fig.patch.set_facecolor('#212121')
    ax.set_facecolor('#1b5e20')
    
    # Remover bordas numéricas (eixos invisíveis) para parecer um campo de futebol limpo
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    
    # Legenda customizada
    plt.legend(loc='upper left', framealpha=0.9, facecolor='#212121', edgecolor='white', labelcolor='white')
    
    # Salvar a imagem
    plt.tight_layout()
    plt.savefig(salvar_caminho, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Gráfico salvo com sucesso em: {salvar_caminho}")


if __name__ == "__main__":
    # Salvar a imagem no diretório local
    output_path = os.path.join(os.path.dirname(__file__), "campo_impedimento.png")
    gerar_grafico_impedimento(output_path)
