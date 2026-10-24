# Visão computacional do projeto: recebe um quadro da webcam e usa OpenCV para
# achar a moeda de calibração e o furo da abraçadeira.
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

    # fecha buracos pequenos dentro do objeto, como reflexos no metal
    kernel = np.ones((3, 3), np.uint8)
    return cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel, iterations=2)


def circularidade(contorno):
    """Vale 1 para um círculo perfeito e diminui em formas alongadas."""
    area = cv2.contourArea(contorno)
    perimetro = cv2.arcLength(contorno, True)
    if perimetro == 0:
        return 0
    return 4 * math.pi * area / perimetro ** 2


def diametro_equivalente(contorno):
    """Diâmetro, em pixels, do círculo que tem a mesma área do contorno."""
    return math.sqrt(4 * cv2.contourArea(contorno) / math.pi)


def circulo_do_contorno(contorno):
    """Centro e raio do contorno, para o front desenhar sobre o vídeo."""
    m = cv2.moments(contorno)
    return {
        "x": m["m10"] / m["m00"],
        "y": m["m01"] / m["m00"],
        "raio": diametro_equivalente(contorno) / 2,
    }


def calibrar(imagem, diametro_moeda_mm, fundo_claro=True, limiar=0):
    """Descobre quantos pixels equivalem a 1 mm usando uma moeda como régua.

    Devolve (pixels_por_mm, circulo) ou None se não achar a moeda.
    """
    mascara = binarizar(imagem, fundo_claro, limiar)
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    moeda = None
    for c in contornos:
        area = cv2.contourArea(c)
        # descarta sujeira (área pequena) e formas que não são redondas
        if area < 500 or circularidade(c) < 0.8:
            continue
        if moeda is None or area > cv2.contourArea(moeda):
            moeda = c

    if moeda is None:
        return None

    px_por_mm = diametro_equivalente(moeda) / diametro_moeda_mm
    return px_por_mm, circulo_do_contorno(moeda)


def medir_furo(imagem, px_por_mm, fundo_claro=True, limiar=0, area_minima=800):
    """Mede o diâmetro interno da abraçadeira, em milímetros.

    Devolve (diametro_mm, circulo) ou None se não achar nenhum furo.
    """
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
        if cv2.contourArea(c) < area_minima or circularidade(c) < 0.5:
            continue
        furos.append(c)

    if not furos:
        return None

    furo = max(furos, key=cv2.contourArea)
    diametro_mm = diametro_equivalente(furo) / px_por_mm
    return diametro_mm, circulo_do_contorno(furo)


def aprovada(medido_mm, nominal_mm, tolerancia_mm):
    """A peça passa se a diferença para o valor nominal couber na tolerância."""
    return abs(medido_mm - nominal_mm) <= tolerancia_mm
