# Servidor web (Flask). Entrega a página e expõe uma rota de API:
#   POST /api/medir -> mede a circunferência do furo da peça (e o % em relação ao padrão)
# A visão computacional fica em medicao.py.

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request

import medicao

app = Flask(__name__)


class ErroDeRequisicao(Exception):
    """Pedido inválido: vira uma resposta 400 com a mensagem."""


@app.errorhandler(ErroDeRequisicao)
def tratar_erro_de_requisicao(erro):
    return jsonify(erro=str(erro)), 400


def ler_imagem():
    """Converte o JPEG enviado pelo navegador numa imagem do OpenCV."""
    arquivo = request.files.get("imagem")
    if arquivo is None:
        raise ErroDeRequisicao("Nenhuma imagem recebida.")
    bytes_imagem = np.frombuffer(arquivo.read(), np.uint8)
    imagem = cv2.imdecode(bytes_imagem, cv2.IMREAD_COLOR)
    if imagem is None:
        raise ErroDeRequisicao("Imagem inválida.")
    return imagem


def ler_opcoes():
    """Lê as opções de segmentação (fundo e limiar) enviadas pela tela."""
    try:
        # o JavaScript envia o checkbox como o texto "true" ou "false"
        fundo_claro = request.form.get("fundo_claro", "true") == "true"
        limiar = int(request.form.get("limiar", 0))
    except ValueError:
        raise ErroDeRequisicao("Parâmetros inválidos.")
    return fundo_claro, limiar


def ler_perimetro_padrao():
    """Perímetro da peça padrão, se veio. Devolve None se estiver ausente."""
    valor = request.form.get("perimetro_padrao_px", "")
    if valor == "":
        return None
    try:
        perimetro = float(valor)
    except ValueError:
        raise ErroDeRequisicao("Parâmetros inválidos.")
    if perimetro <= 0:
        raise ErroDeRequisicao("Parâmetros inválidos.")
    return perimetro


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/medir", methods=["POST"])
def medir():
    imagem = ler_imagem()
    fundo_claro, limiar = ler_opcoes()
    perimetro_padrao = ler_perimetro_padrao()

    medida = medicao.medir_peca(imagem, fundo_claro, limiar)
    if medida is None:
        # 422: a requisição está correta, mas a imagem não serve para medir
        return jsonify(erro="Não encontrei o furo da abraçadeira."), 422

    # o percentual só existe quando o front envia o perímetro do padrão
    if perimetro_padrao is not None:
        medida["percentual"] = medicao.percentual_circunferencia(
            medida["perimetro_px"], perimetro_padrao)

    return jsonify(medida)


if __name__ == "__main__":
    # debug=True é só para desenvolvimento local
    app.run(debug=True)
