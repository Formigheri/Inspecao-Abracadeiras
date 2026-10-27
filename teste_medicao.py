# Testes automáticos. Em vez de depender de webcam e de peças reais, as imagens
# são desenhadas com o OpenCV (anéis redondos e deformados) em tamanho conhecido,
# e os testes conferem se o código mede o valor esperado.
# Para rodar:  python teste_medicao.py

import io
import math
import unittest

import cv2
import numpy as np

import medicao
from app import app

CENTRO = (640, 360)
ESCURO = (90, 90, 90)
CLARO = (235, 235, 235)


def fundo():
    return np.full((720, 1280, 3), 235, np.uint8)


def anel(furo_px, externo_px=200):
    """Anel redondo: disco escuro com um furo circular no meio."""
    img = fundo()
    cv2.circle(img, CENTRO, externo_px // 2, ESCURO, -1, cv2.LINE_AA)
    cv2.circle(img, CENTRO, furo_px // 2, CLARO, -1, cv2.LINE_AA)
    return img


def anel_oval(eixo_a, eixo_b, externo_px=200):
    """Anel com furo oval, parecido com uma abraçadeira amassada."""
    img = fundo()
    cv2.circle(img, CENTRO, externo_px // 2, ESCURO, -1, cv2.LINE_AA)
    cv2.ellipse(img, CENTRO, (eixo_a, eixo_b), 0, 0, 360, CLARO, -1, cv2.LINE_AA)
    return img


def anel_irregular(amplitude, semente, pontos=720):
    """Anel cujo furo tem a borda irregular, como acontece com sombra e brilho do metal."""
    sorteio = np.random.default_rng(semente)
    angulos = np.linspace(0, 2 * np.pi, pontos, endpoint=False)
    desvio = sorteio.normal(0, amplitude, pontos)
    # irregularidade com correlação de poucos pixels, não ruído independente a cada ponto
    desvio = np.convolve(np.pad(desvio, 2, mode="wrap"), np.ones(5) / 5, mode="valid")
    raio = 62.5 + desvio * 2.2
    contorno = np.stack([CENTRO[0] + raio * np.cos(angulos),
                         CENTRO[1] + raio * np.sin(angulos)], axis=1)
    img = fundo()
    cv2.circle(img, CENTRO, 100, ESCURO, -1, cv2.LINE_AA)
    cv2.fillPoly(img, [np.round(contorno).astype(np.int32)], CLARO, cv2.LINE_AA)
    return img


def moeda(diametro_px):
    img = fundo()
    cv2.circle(img, CENTRO, diametro_px // 2, ESCURO, -1, cv2.LINE_AA)
    return img


def com_ruido(img, intensidade, semente):
    """Soma ruído aleatório, como o de uma webcam em pouca luz."""
    ruido = np.random.default_rng(semente).normal(0, intensidade, img.shape)
    return np.clip(img.astype(np.float32) + ruido, 0, 255).astype(np.uint8)


def como_arquivo(img):
    # JPEG em bytes, igual ao que o navegador envia
    _, jpg = cv2.imencode(".jpg", img)
    return jpg.tobytes()


class TesteMedicao(unittest.TestCase):
    """Funções do medicao.py chamadas diretamente."""

    def test_perimetro_do_furo_redondo(self):
        medida = medicao.medir_peca(anel(125))
        esperado = math.pi * 125
        # aceita 2% de diferença por causa da discretização em pixels
        self.assertAlmostEqual(medida["perimetro_px"], esperado, delta=esperado * 0.02)

    def test_mesma_peca_da_100_por_cento(self):
        padrao = medicao.medir_peca(anel(125))["perimetro_px"]
        testada = medicao.medir_peca(anel(125))["perimetro_px"]
        self.assertAlmostEqual(medicao.percentual_circunferencia(testada, padrao), 100, delta=0.5)

    def test_peca_menor_tem_percentual_menor(self):
        padrao = medicao.medir_peca(anel(125))["perimetro_px"]
        menor = medicao.medir_peca(anel(115))["perimetro_px"]
        # 115 / 125 = 92%
        self.assertAlmostEqual(medicao.percentual_circunferencia(menor, padrao), 92, delta=1.5)

    def test_peca_oval_tem_circunferencia_menor_e_circularidade_baixa(self):
        padrao = medicao.medir_peca(anel(125))
        oval = medicao.medir_peca(anel_oval(62, 53))
        pct = medicao.percentual_circunferencia(oval["perimetro_px"], padrao["perimetro_px"])
        # perímetro da elipse de semieixos 62 e 53 é cerca de 93% do círculo de diâmetro 125
        self.assertAlmostEqual(pct, 93, delta=1.5)
        self.assertLess(oval["circularidade"], padrao["circularidade"])

    def test_imagem_sem_furo(self):
        self.assertIsNone(medicao.medir_peca(moeda(125)))

    def test_regra_de_aprovacao(self):
        self.assertTrue(medicao.aprovada(101.5, 2))
        self.assertTrue(medicao.aprovada(98.0, 2))
        self.assertFalse(medicao.aprovada(93.0, 2))

    def test_regra_de_aprovacao_com_forma(self):
        self.assertTrue(medicao.aprovada(100, 2, forma=97, tolerancia_forma=5))
        self.assertFalse(medicao.aprovada(100, 2, forma=92, tolerancia_forma=5))
        self.assertFalse(medicao.aprovada(90, 2, forma=100, tolerancia_forma=5))

    def test_razao_dos_eixos_pega_peca_achatada(self):
        redonda = medicao.medir_peca(anel(125))["razao_eixos"]
        achatada = medicao.medir_peca(anel_oval(62, 50))["razao_eixos"]
        self.assertAlmostEqual(redonda, 1.0, delta=0.02)
        self.assertLess(achatada, 0.85)

    def test_achatamento_com_mesmo_perimetro_e_reprovado_pela_forma(self):
        # elipse com perímetro quase igual ao do círculo de diâmetro 125 (eixos 70 e 54)
        padrao = medicao.medir_peca(anel(125))
        achatada = medicao.medir_peca(anel_oval(70, 54))
        pct = medicao.percentual_circunferencia(achatada["perimetro_px"], padrao["perimetro_px"])
        forma = medicao.forma_relativa(achatada["razao_eixos"], padrao["razao_eixos"])
        self.assertAlmostEqual(pct, 100, delta=2.5)
        self.assertFalse(medicao.aprovada(pct, 2.5, forma, 5))


    def test_medida_resiste_a_ruido_da_webcam(self):
        # com ruído forte na imagem o perímetro não pode mudar
        limpo = medicao.medir_peca(anel(125))["perimetro_px"]
        for semente in range(5):
            ruidosa = medicao.medir_peca(com_ruido(anel(125), 18, semente))
            self.assertIsNotNone(ruidosa)
            pct = medicao.percentual_circunferencia(ruidosa["perimetro_px"], limpo)
            self.assertAlmostEqual(pct, 100, delta=2.0)

    def test_suavizacao_reduz_o_efeito_da_borda_irregular(self):
        esperado = math.pi * 125
        for semente in range(3):
            furo = medicao.achar_furo(anel_irregular(2.5, semente))
            # método sem suavização: aproxima por polígono de 2 px e mede
            sem_suavizar = cv2.arcLength(cv2.approxPolyDP(furo, 2.0, True), True)
            suavizado = medicao.perimetro(furo)
            self.assertLess(suavizado, sem_suavizar * 0.95)
            self.assertAlmostEqual(suavizado, esperado, delta=esperado * 0.06)


class TesteApi(unittest.TestCase):
    """Rotas do Flask, usando o cliente de teste (sem subir o servidor)."""

    def setUp(self):
        self.cliente = app.test_client()

    def enviar(self, rota, img, **campos):
        dados = {"imagem": (io.BytesIO(como_arquivo(img)), "q.jpg"), **campos}
        return self.cliente.post(rota, data=dados, content_type="multipart/form-data")

    def test_definir_padrao_e_medir_peca_igual(self):
        r = self.enviar("/api/medir", anel(125))
        self.assertEqual(r.status_code, 200)
        padrao = r.get_json()
        # sem padrão informado, a resposta não traz percentual
        self.assertNotIn("percentual", padrao)

        r = self.enviar("/api/medir", anel(125), perimetro_padrao_px=str(padrao["perimetro_px"]))
        self.assertAlmostEqual(r.get_json()["percentual"], 100, delta=0.5)

    def test_resposta_traz_a_forma_quando_ha_padrao(self):
        padrao = self.enviar("/api/medir", anel(125)).get_json()
        r = self.enviar("/api/medir", anel(125), perimetro_padrao_px=str(padrao["perimetro_px"]),
                        razao_padrao=str(padrao["razao_eixos"]))
        self.assertAlmostEqual(r.get_json()["forma"], 100, delta=1)

    def test_peca_deformada_fica_abaixo_do_padrao(self):
        padrao = self.enviar("/api/medir", anel(125)).get_json()["perimetro_px"]
        r = self.enviar("/api/medir", anel_oval(62, 53), perimetro_padrao_px=str(padrao))
        self.assertLess(r.get_json()["percentual"], 95)


    def test_sem_imagem(self):
        r = self.cliente.post("/api/medir", data={})
        self.assertEqual(r.status_code, 400)

    def test_parametro_invalido(self):
        r = self.enviar("/api/medir", anel(125), perimetro_padrao_px="abc")
        self.assertEqual(r.status_code, 400)

    def test_furo_nao_encontrado(self):
        r = self.enviar("/api/medir", fundo())
        self.assertEqual(r.status_code, 422)


if __name__ == "__main__":
    unittest.main()
