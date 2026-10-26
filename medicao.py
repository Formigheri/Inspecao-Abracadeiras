# Visão computacional do projeto: recebe quadros da webcam e usa OpenCV para
# achar o furo da abraçadeira e medir a circunferência (perímetro) dele.
# Não depende do Flask, então dá para testar estas funções isoladamente.

import math

import cv2
import numpy as np


def binarizar(imagem, fundo_claro=True, limiar=0):
    """Gera uma máscara preto e branco em que o objeto fica branco e o fundo preto."""
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    # o desfoque leve tira o ruído da webcam e suaviza as bordas
    cinza = cv2.GaussianBlur(cinza, (5, 5), 0)

    # peça escura sobre fundo claro precisa do threshold invertido
    tipo = cv2.THRESH_BINARY_INV if fundo_claro else cv2.THRESH_BINARY
    if limiar <= 0:
        # limiar 0 = o método de Otsu escolhe o valor sozinho
        _, mascara = cv2.threshold(cinza, 0, 255, tipo + cv2.THRESH_OTSU)
    else:
        _, mascara = cv2.threshold(cinza, limiar, 255, tipo)

    # fecha falhas na borda do metal (furos da rosca, reflexos); com um fechamento
    # fraco o contorno fica cheio de reentrâncias e o perímetro sai inflado
    kernel = np.ones((7, 7), np.uint8)
    return cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel, iterations=3)


def suavizar(contorno, sigma=10.0):
    """Suaviza o contorno com uma média gaussiana ao longo da própria curva.

    Tira o serrilhado do contorno em pixels. Sem isso, qualquer irregularidade
    pequena aumenta o perímetro e o percentual fica instável.
    """
    pontos = contorno.reshape(-1, 2).astype(np.float32)
    if len(pontos) < 20:
        return pontos
    raio = int(3 * sigma)
    x = np.arange(-raio, raio + 1)
    janela = np.exp(-x ** 2 / (2 * sigma ** 2))
    janela /= janela.sum()
    # o contorno é uma curva fechada, então o preenchimento das pontas é circular
    estendido = np.pad(pontos, ((raio, raio), (0, 0)), mode="wrap")
    return np.stack(
        [np.convolve(estendido[:, i], janela, mode="valid") for i in range(2)], axis=1
    )


def perimetro(contorno):
    """Comprimento do contorno suavizado, em pixels (a circunferência da peça na imagem)."""
    suave = suavizar(contorno)
    passos = np.roll(suave, -1, axis=0) - suave
    return float(np.sqrt((passos ** 2).sum(axis=1)).sum())


def circularidade(contorno):
    """Vale 1 para um círculo perfeito e diminui em formas deformadas."""
    area = cv2.contourArea(contorno)
    comprimento = perimetro(contorno)
    if comprimento == 0:
        return 0
    return 4 * math.pi * area / comprimento ** 2


def pontos_do_contorno(contorno, maximo=300):
    """Lista enxuta de pontos [x, y] do contorno, para o front desenhar o formato real."""
    pontos = suavizar(contorno)
    passo = max(1, len(pontos) // maximo)
    return pontos[::passo].round().astype(int).tolist()


def achar_furo(imagem, fundo_claro=True, limiar=0, area_minima=800):
    """Localiza o furo da abraçadeira. Devolve o contorno ou None."""
    mascara = binarizar(imagem, fundo_claro, limiar)
    # RETR_CCOMP guarda a hierarquia entre contornos, o que permite saber
    # quais estão dentro de outros (caso do furo)
    contornos, hierarquia = cv2.findContours(mascara, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    if hierarquia is None:
        return None

    furos = []
    for c, h in zip(contornos, hierarquia[0]):
        # h[3] é o índice do contorno "pai"; -1 significa contorno externo, não furo
        if h[3] == -1:
            continue
        # a circularidade mínima é baixa de propósito: uma peça amassada precisa
        # ser detectada para poder ser reprovada
        if cv2.contourArea(c) < area_minima or circularidade(c) < 0.3:
            continue
        furos.append(c)

    if not furos:
        return None
    return max(furos, key=cv2.contourArea)


def medir_peca(imagem, fundo_claro=True, limiar=0):
    """Mede a circunferência do furo da peça, em pixels.

    Devolve um dicionário com perímetro, área, circularidade e os pontos
    do contorno, ou None se não achar o furo.
    """
    furo = achar_furo(imagem, fundo_claro, limiar)
    if furo is None:
        return None
    return {
        "perimetro_px": perimetro(furo),
        "area_px": cv2.contourArea(furo),
        "circularidade": circularidade(furo),
        "contorno": pontos_do_contorno(furo),
    }


def percentual_circunferencia(perimetro_px, perimetro_padrao_px):
    """Circunferência da peça em relação à peça padrão (100 = igual ao padrão)."""
    return 100 * perimetro_px / perimetro_padrao_px


def aprovada(percentual, tolerancia_pct):
    """A peça passa se o percentual ficar dentro de 100% ± a tolerância."""
    return abs(percentual - 100) <= tolerancia_pct
