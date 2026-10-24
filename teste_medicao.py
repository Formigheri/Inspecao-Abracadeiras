# Testes automáticos. Em vez de depender de webcam e de peças reais, as imagens
# são desenhadas com o OpenCV (moeda e anel) em tamanho conhecido, e os testes
# conferem se o código mede o valor esperado.
# Para rodar:  python teste_medicao.py

import io
import unittest

import cv2
import numpy as np

import medicao
from app import app

# escala real das imagens desenhadas: 5 pixels = 1 mm
PX_POR_MM = 5.0


def fundo():
    return np.full((720, 1280, 3), 235, np.uint8)


def imagem_moeda(diametro_mm):
    img = fundo()
    cv2.circle(img, (640, 360), int(diametro_mm * PX_POR_MM / 2), (90, 90, 90), -1, cv2.LINE_AA)
    return img


def imagem_anel(furo_mm, externo_mm):
    # disco escuro com um furo no meio, como a abraçadeira vista de cima
    img = fundo()
    cv2.circle(img, (640, 360), int(externo_mm * PX_POR_MM / 2), (90, 90, 90), -1, cv2.LINE_AA)
    cv2.circle(img, (640, 360), int(furo_mm * PX_POR_MM / 2), (235, 235, 235), -1, cv2.LINE_AA)
    return img


def como_arquivo(img):
    # JPEG em bytes, igual ao que o navegador envia
    _, jpg = cv2.imencode(".jpg", img)
    return jpg.tobytes()


class TesteMedicao(unittest.TestCase):
    """Funções do medicao.py chamadas diretamente."""

    def test_calibracao(self):
        resultado = medicao.calibrar(imagem_moeda(27), 27)
        self.assertIsNotNone(resultado)
        # tolerância pequena por causa da discretização em pixels
        self.assertAlmostEqual(resultado[0], PX_POR_MM, delta=0.1)

    def test_medida_do_furo(self):
        escala, _ = medicao.calibrar(imagem_moeda(27), 27)
        medido, _ = medicao.medir_furo(imagem_anel(25, 32), escala)
        self.assertAlmostEqual(medido, 25, delta=0.6)

    def test_imagem_sem_furo(self):
        self.assertIsNone(medicao.medir_furo(imagem_moeda(27), PX_POR_MM))

    def test_tolerancia(self):
        self.assertTrue(medicao.aprovada(25.4, 25, 0.5))
        self.assertFalse(medicao.aprovada(26.0, 25, 0.5))


class TesteApi(unittest.TestCase):
    """Rotas do Flask, usando o cliente de teste (sem subir o servidor)."""

    def setUp(self):
        self.cliente = app.test_client()

    def enviar(self, rota, img, **campos):
        dados = {"imagem": (io.BytesIO(como_arquivo(img)), "q.jpg"), **campos}
        return self.cliente.post(rota, data=dados, content_type="multipart/form-data")

    def test_fluxo_completo(self):
        r = self.enviar("/api/calibrar", imagem_moeda(27), diametro_moeda="27")
        escala = r.get_json()["px_por_mm"]
        r = self.enviar("/api/medir", imagem_anel(25, 32), px_por_mm=str(escala))
        self.assertEqual(r.status_code, 200)
        self.assertAlmostEqual(r.get_json()["diametro_mm"], 25, delta=0.6)

    def test_sem_imagem(self):
        r = self.cliente.post("/api/medir", data={"px_por_mm": "5"})
        self.assertEqual(r.status_code, 400)

    def test_moeda_nao_encontrada(self):
        r = self.enviar("/api/calibrar", fundo(), diametro_moeda="27")
        self.assertEqual(r.status_code, 422)


if __name__ == "__main__":
    unittest.main()
