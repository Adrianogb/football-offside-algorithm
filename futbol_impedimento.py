import math
from typing import List, Tuple, Dict, Any, Optional


class Jogador:
    def __init__(self, id_jogador: str, nome: str, time: str, x: float, y: float):
        """
        Representa um jogador em campo.
        Dimensões do campo padrão FIFA: 105m de comprimento (x) por 68m de largura (y).

        :param id_jogador: Identificador único do jogador (ex: "A9", "B1")
        :param nome: Nome do jogador
        :param time: Nome do time ("Atacante" ou "Defensor")
        :param x: Posição no eixo x (0 a 105). 0 é a linha de fundo esquerda, 105 é a direita.
        :param y: Posição no eixo y (0 a 68). 0 é a lateral inferior, 68 é a lateral superior.
        """
        self.id = id_jogador
        self.nome = nome
        self.time = time
        self.x = max(0.0, min(105.0, float(x)))
        self.y = max(0.0, min(68.0, float(y)))

    @property
    def posicao(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def __repr__(self):
        return f"Jogador({self.id}, {self.nome}, Time: {self.time}, Pos: ({self.x:.1f}, {self.y:.1f}))"


class Bola:
    def __init__(self, x: float, y: float):
        """
        Representa a bola no campo.

        :param x: Posição no eixo x (0 a 105)
        :param y: Posição no eixo y (0 a 68)
        """
        self.x = max(0.0, min(105.0, float(x)))
        self.y = max(0.0, min(68.0, float(y)))

    @property
    def posicao(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def __repr__(self):
        return f"Bola(Pos: ({self.x:.1f}, {self.y:.1f}))"


def verificar_impedimento(
    jogador_alvo: Jogador,
    bola: Bola,
    jogadores_time_defensor: List[Jogador],
    tipo_passe: str = "comum",
    participou_ativamente: bool = True,
    direcao_ataque: int = 1,
) -> Dict[str, Any]:
    """
    Verifica se um jogador atacante está em posição de impedimento e se cometeu
    a infração de impedimento no momento do passe, segundo a Lei 11 da FIFA.

    :param jogador_alvo: O jogador atacante que recebe o passe ou se envolve na jogada.
    :param bola: A bola no momento em que o passe é realizado.
    :param jogadores_time_defensor: Lista de jogadores do time adversário (defesa).
    :param tipo_passe: Tipo de passe ("comum", "lateral", "meta", "escanteio").
    :param participou_ativamente: Se o jogador participou ativamente (tocou na bola, interferiu no adversário, etc.).
    :param direcao_ataque: 1 se o time atacante ataca da esquerda para a direita (em direção a X=105).
                           -1 se ataca da direita para a esquerda (em direção a X=0).

    :return: Dicionário detalhado com o resultado da verificação.
    """
    # 1. Regra de Exceções de Reinício de Jogo (Lei 11.3)
    # Não há infração se o jogador receber a bola diretamente de tiro de meta, arremesso lateral ou escanteio.
    tipo_passe = tipo_passe.lower()
    if tipo_passe in ["lateral", "meta", "escanteio"]:
        return {
            "impedido": False,
            "em_posicao_impedimento": False,
            "motivo": f"Não há impedimento direto em passes de {tipo_passe}.",
            "detalhes": {
                "na_metade_ofensiva": False,
                "a_frente_da_bola": False,
                "a_frente_do_penultimo_defensor": False,
                "participou_ativamente": participou_ativamente,
                "tipo_passe": tipo_passe,
            },
        }

    # 2. Verificar se o jogador está na metade ofensiva do campo (Lei 11.1)
    # O jogador só pode estar impedido na metade adversária do campo (excluindo a linha de meio de campo).
    meio_campo = 52.5
    na_metade_ofensiva = False
    if direcao_ataque == 1:
        na_metade_ofensiva = jogador_alvo.x > meio_campo
    else:
        na_metade_ofensiva = jogador_alvo.x < meio_campo

    if not na_metade_ofensiva:
        return {
            "impedido": False,
            "em_posicao_impedimento": False,
            "motivo": "O jogador está em sua própria metade do campo no momento do passe.",
            "detalhes": {
                "na_metade_ofensiva": False,
                "a_frente_da_bola": None,
                "a_frente_do_penultimo_defensor": None,
                "participou_ativamente": participou_ativamente,
                "tipo_passe": tipo_passe,
            },
        }

    # 3. Verificar se o jogador está à frente da bola (mais próximo do gol adversário)
    # Se estiver atrás ou na mesma linha da bola, não há impedimento.
    a_frente_da_bola = False
    if direcao_ataque == 1:
        # Gol adversário está em X = 105
        a_frente_da_bola = jogador_alvo.x > bola.x
    else:
        # Gol adversário está em X = 0
        a_frente_da_bola = jogador_alvo.x < bola.x

    if not a_frente_da_bola:
        return {
            "impedido": False,
            "em_posicao_impedimento": False,
            "motivo": "O jogador está atrás ou na mesma linha da bola no momento do passe.",
            "detalhes": {
                "na_metade_ofensiva": True,
                "a_frente_da_bola": False,
                "a_frente_do_penultimo_defensor": None,
                "participou_ativamente": participou_ativamente,
                "tipo_passe": tipo_passe,
            },
        }

    # 4. Verificar se o jogador está à frente do penúltimo defensor
    # Primeiro, ordenar todos os defensores por sua proximidade da linha de meta do gol adversário.
    # Gol adversário em X = 105 (ataque 1): quanto maior X, mais próximo do gol. Ordenamos decrescente.
    # Gol adversário em X = 0 (ataque -1): quanto menor X, mais próximo do gol. Ordenamos crescente.
    if direcao_ataque == 1:
        defensores_ordenados = sorted(
            jogadores_time_defensor, key=lambda j: j.x, reverse=True
        )
        linha_gol_adversaria = 105.0
    else:
        defensores_ordenados = sorted(jogadores_time_defensor, key=lambda j: j.x)
        linha_gol_adversaria = 0.0

    # Determinar a linha do penúltimo defensor
    if len(defensores_ordenados) >= 2:
        penultimo_defensor = defensores_ordenados[1]
        x_limite_defesa = penultimo_defensor.x
    elif len(defensores_ordenados) == 1:
        # Apenas 1 defensor (normalmente o goleiro).
        # Nesse caso, a linha de impedimento vira o último defensor ou a linha de meta.
        # Matematicamente, a posição do penúltimo defensor virtualmente passa a ser o limite do gol.
        x_limite_defesa = defensores_ordenados[0].x
    else:
        # Nenhum defensor em campo (caso raro/teórico).
        x_limite_defesa = linha_gol_adversaria

    # Verificar se o atacante está à frente do penúltimo defensor
    a_frente_do_penultimo_defensor = False
    if direcao_ataque == 1:
        # Atacante tem X maior que a linha de defesa
        a_frente_do_penultimo_defensor = jogador_alvo.x > x_limite_defesa
    else:
        # Atacante tem X menor que a linha de defesa
        a_frente_do_penultimo_defensor = jogador_alvo.x < x_limite_defesa

    # Define se o jogador está formalmente em posição de impedimento
    em_posicao_impedimento = (
        na_metade_ofensiva and a_frente_da_bola and a_frente_do_penultimo_defensor
    )

    if not em_posicao_impedimento:
        return {
            "impedido": False,
            "em_posicao_impedimento": False,
            "motivo": "O jogador está atrás ou na mesma linha do penúltimo defensor.",
            "detalhes": {
                "na_metade_ofensiva": True,
                "a_frente_da_bola": True,
                "a_frente_do_penultimo_defensor": False,
                "linha_impedimento_x": x_limite_defesa,
                "participou_ativamente": participou_ativamente,
                "tipo_passe": tipo_passe,
            },
        }

    # 5. Se o jogador está em posição de impedimento, verificar se ele participa ativamente da jogada (Lei 11.2)
    # Estar em posição de impedimento por si só não é infração, a menos que o jogador participe do lance de forma ativa.
    if not participou_ativamente:
        return {
            "impedido": False,
            "em_posicao_impedimento": True,
            "motivo": "O jogador estava em posição de impedimento, mas NÃO participou ativamente da jogada.",
            "detalhes": {
                "na_metade_ofensiva": True,
                "a_frente_da_bola": True,
                "a_frente_do_penultimo_defensor": True,
                "linha_impedimento_x": x_limite_defesa,
                "participou_ativamente": False,
                "tipo_passe": tipo_passe,
            },
        }

    # Se atendeu a todos os critérios e participou, está impedido!
    return {
        "impedido": True,
        "em_posicao_impedimento": True,
        "motivo": "INFRAÇÃO DE IMPEDIMENTO! O jogador estava em posição de impedimento e participou ativamente da jogada.",
        "detalhes": {
            "na_metade_ofensiva": True,
            "a_frente_da_bola": True,
            "a_frente_do_penultimo_defensor": True,
            "linha_impedimento_x": x_limite_defesa,
            "participou_ativamente": True,
            "tipo_passe": tipo_passe,
        },
    }


def executar_exemplos_demonstrativos():
    """
    Executa cenários comuns para testar e demonstrar o funcionamento do algoritmo.
    """
    print("=" * 60)
    print(" SIMULADOR DE IMPEDIMENTO - REGRAS OFICIAIS DA FIFA (LEI 11)")
    print("=" * 60)

    # Defensores (Time B)
    goleiro = Jogador("B1", "Goleiro B", "Defensor", 102.0, 34.0)
    zagueiro = Jogador("B3", "Zagueiro B", "Defensor", 85.0, 20.0)
    lateral = Jogador("B4", "Lateral B", "Defensor", 88.0, 50.0)
    defensores = [goleiro, zagueiro, lateral]

    # Atacantes (Time A) - atacando da esquerda para a direita (direcao_ataque = 1)
    passador = Jogador("A10", "Meia A (Passador)", "Atacante", 45.0, 34.0)

    print("\n--- CONFIGURAÇÃO DA DEFESA ---")
    for d in defensores:
        print(f"  * {d}")
    print(
        f"Linha de impedimento (penúltimo defensor): {sorted(defensores, key=lambda j: j.x, reverse=True)[1].x:.1f}m"
    )

    # Cenário 1: Atacante recebe o passe estando na mesma linha do penúltimo defensor
    bola_c1 = Bola(x=45.0, y=34.0)  # na posição do passador
    atacante_c1 = Jogador("A9", "Centroavante A", "Atacante", 87.0, 30.0)
    res_c1 = verificar_impedimento(
        atacante_c1, bola_c1, defensores, tipo_passe="comum", participou_ativamente=True
    )
    print(
        f"\nCenário 1: {atacante_c1.nome} em X={atacante_c1.x}m (atrás do penúltimo defensor em X=88.0m)"
    )
    print(f"  => Impedido? {res_c1['impedido']} | Motivo: {res_c1['motivo']}")

    # Cenário 2: Atacante está à frente do penúltimo defensor e recebe o passe (Impedimento clássico)
    bola_c2 = Bola(x=45.0, y=34.0)
    atacante_c2 = Jogador("A9", "Centroavante A", "Atacante", 92.0, 30.0)
    res_c2 = verificar_impedimento(
        atacante_c2, bola_c2, defensores, tipo_passe="comum", participou_ativamente=True
    )
    print(
        f"\nCenário 2: {atacante_c2.nome} em X={atacante_c2.x}m (à frente do penúltimo defensor em X=88.0m)"
    )
    print(f"  => Impedido? {res_c2['impedido']} | Motivo: {res_c2['motivo']}")

    # Cenário 3: Atacante está à frente do penúltimo defensor, mas o passe é lateral/atrás da linha da bola
    bola_c3 = Bola(x=95.0, y=34.0)  # a bola já avançou
    atacante_c3 = Jogador(
        "A9", "Centroavante A", "Atacante", 92.0, 30.0
    )  # atacante está atrás da bola (X=92 < X=95)
    res_c3 = verificar_impedimento(
        atacante_c3, bola_c3, defensores, tipo_passe="comum", participou_ativamente=True
    )
    print(
        f"\nCenário 3: {atacante_c3.nome} em X={atacante_c3.x}m (à frente da defesa, mas atrás da linha da bola em X={bola_c3.x}m)"
    )
    print(f"  => Impedido? {res_c3['impedido']} | Motivo: {res_c3['motivo']}")

    # Cenário 4: Atacante está na sua metade do campo
    bola_c4 = Bola(x=30.0, y=20.0)
    atacante_c4 = Jogador("A11", "Ponta A", "Atacante", 48.0, 10.0)  # X < 52.5
    res_c4 = verificar_impedimento(
        atacante_c4, bola_c4, defensores, tipo_passe="comum", participou_ativamente=True
    )
    print(
        f"\nCenário 4: {atacante_c4.nome} em X={atacante_c4.x}m (recebendo na sua metade de campo)"
    )
    print(f"  => Impedido? {res_c4['impedido']} | Motivo: {res_c4['motivo']}")

    # Cenário 5: Exceção de arremesso lateral
    bola_c5 = Bola(x=80.0, y=68.0)
    atacante_c5 = Jogador("A9", "Centroavante A", "Atacante", 95.0, 34.0)
    res_c5 = verificar_impedimento(
        atacante_c5,
        bola_c5,
        defensores,
        tipo_passe="lateral",
        participou_ativamente=True,
    )
    print(
        f"\nCenário 5: {atacante_c5.nome} em X={atacante_c5.x}m (recebendo arremesso lateral)"
    )
    print(f"  => Impedido? {res_c5['impedido']} | Motivo: {res_c5['motivo']}")

    # Cenário 6: Em posição de impedimento, mas não participa da jogada (Lei da Vantagem/Sem infração)
    bola_c6 = Bola(x=45.0, y=34.0)
    atacante_c6 = Jogador(
        "A7", "Extremo A", "Atacante", 90.0, 60.0
    )  # Do outro lado do campo, não participa
    res_c6 = verificar_impedimento(
        atacante_c6,
        bola_c6,
        defensores,
        tipo_passe="comum",
        participou_ativamente=False,
    )
    print(
        f"\nCenário 6: {atacante_c6.nome} em X={atacante_c6.x}m (em posição de impedimento, mas passivo)"
    )
    print(f"  => Impedido? {res_c6['impedido']} | Motivo: {res_c6['motivo']}")
    print("=" * 60)


if __name__ == "__main__":
    executar_exemplos_demonstrativos()
