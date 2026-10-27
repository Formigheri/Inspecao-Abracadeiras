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


def ler_numero_opcional(nome):
    """Campo numérico positivo que pode não vir. Devolve None se estiver ausente."""
    valor = request.form.get(nome, "")
    if valor == "":
        return None
    try:
        numero = float(valor)
    except ValueError:
        raise ErroDeRequisicao("Parâmetros inválidos.")
    if numero <= 0:
        raise ErroDeRequisicao("Parâmetros inválidos.")
    return numero


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/medir", methods=["POST"])
def medir():
    imagem = ler_imagem()
    fundo_claro, limiar = ler_opcoes()
    perimetro_padrao = ler_numero_opcional("perimetro_padrao_px")
    razao_padrao = ler_numero_opcional("razao_padrao")

    medida = medicao.medir_peca(imagem, fundo_claro, limiar)
    if medida is None:
        # 422: a requisição está correta, mas a imagem não serve para medir
        return jsonify(erro="Não encontrei o furo da abraçadeira."), 422

    # percentual e forma só existem quando o front envia os valores do padrão
    if perimetro_padrao is not None:
        medida["percentual"] = medicao.percentual_circunferencia(
            medida["perimetro_px"], perimetro_padrao)
    if razao_padrao is not None:
        medida["forma"] = medicao.forma_relativa(medida["razao_eixos"], razao_padrao)

    return jsonify(medida)


if __name__ == "__main__":
    # debug=True é só para desenvolvimento local
    app.run(debug=True)
