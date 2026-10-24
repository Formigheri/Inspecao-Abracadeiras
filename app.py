# Servidor web (Flask). Entrega a página e expõe duas rotas de API:
#   POST /api/calibrar -> acha a moeda e devolve a escala (pixels por mm)
#   POST /api/medir    -> acha o furo da peça e devolve o diâmetro em mm
# A visão computacional fica em medicao.py.

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request

import medicao

app = Flask(__name__)


def ler_imagem():
    """Converte o JPEG enviado pelo navegador numa imagem do OpenCV."""
    arquivo = request.files.get("imagem")
    if arquivo is None:
        return None
    bytes_imagem = np.frombuffer(arquivo.read(), np.uint8)
    return cv2.imdecode(bytes_imagem, cv2.IMREAD_COLOR)


def ler_opcoes():
    """Lê as opções de segmentação (fundo e limiar) enviadas pela tela."""
    # o JavaScript envia o checkbox como o texto "true" ou "false"
    fundo_claro = request.form.get("fundo_claro", "true") == "true"
    limiar = int(request.form.get("limiar", 0))
    return fundo_claro, limiar


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/calibrar", methods=["POST"])
def calibrar():
    imagem = ler_imagem()
    if imagem is None:
        return jsonify(erro="Nenhuma imagem recebida."), 400

    try:
        diametro_moeda = float(request.form["diametro_moeda"])
        fundo_claro, limiar = ler_opcoes()
    except (KeyError, ValueError):
        return jsonify(erro="Parâmetros inválidos."), 400

    if diametro_moeda <= 0:
        return jsonify(erro="O diâmetro da moeda precisa ser maior que zero."), 400

    resultado = medicao.calibrar(imagem, diametro_moeda, fundo_claro, limiar)
    if resultado is None:
        # 422: a requisição está correta, mas a imagem não serve para calibrar
        return jsonify(erro="Não encontrei a moeda. Confira o fundo, a luz e o limiar."), 422

    px_por_mm, circulo = resultado
    return jsonify(px_por_mm=px_por_mm, circulo=circulo)


@app.route("/api/medir", methods=["POST"])
def medir():
    imagem = ler_imagem()
    if imagem is None:
        return jsonify(erro="Nenhuma imagem recebida."), 400

    try:
        px_por_mm = float(request.form["px_por_mm"])
        fundo_claro, limiar = ler_opcoes()
    except (KeyError, ValueError):
        return jsonify(erro="Parâmetros inválidos."), 400

    if px_por_mm <= 0:
        return jsonify(erro="Escala inválida, calibre de novo."), 400

    resultado = medicao.medir_furo(imagem, px_por_mm, fundo_claro, limiar)
    if resultado is None:
        return jsonify(erro="Não encontrei o furo da abraçadeira."), 422

    diametro_mm, circulo = resultado
    return jsonify(diametro_mm=diametro_mm, circulo=circulo)


if __name__ == "__main__":
    # debug=True é só para desenvolvimento local
    app.run(debug=True)
