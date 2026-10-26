# Mede as fotos reais da pasta fotos_teste/ com o mesmo código do sistema e mostra
# o veredito de cada peça em relação a um padrão. Serve para repetir a validação
# da seção 9.4.1 da documentação.
# Para rodar:  python validar_fotos.py

import cv2

import medicao

# fotos 3 e 4 têm duas peças lado a lado; cada metade é medida separadamente
PECAS = {
    "foto3 esquerda (achatada)": ("foto3.jpg", "esquerda"),
    "foto3 direita (redonda)": ("foto3.jpg", "direita"),
    "foto4 esquerda": ("foto4.jpg", "esquerda"),
    "foto4 direita": ("foto4.jpg", "direita"),
}
# dentro de cada foto o padrão é a peça mais redonda; fotos diferentes têm
# enquadramentos diferentes e não podem ser comparadas entre si
PADRAO = {"foto3.jpg": "foto3 direita (redonda)", "foto4.jpg": "foto4 esquerda"}
TOLERANCIA = 2.0         # % do perímetro
TOLERANCIA_FORMA = 5.0   # % de achatamento


def recortar(foto, lado):
    largura = foto.shape[1]
    return foto[:, :largura // 2] if lado == "esquerda" else foto[:, largura // 2:]


medidas = {}
for nome, (arquivo, lado) in PECAS.items():
    foto = cv2.imread("fotos_teste/" + arquivo)
    medidas[nome] = medicao.medir_peca(recortar(foto, lado), fundo_claro=False)

print("%-28s %10s %10s  %s" % ("peça", "perímetro", "forma", "resultado"))
for nome, (arquivo, _) in PECAS.items():
    padrao = medidas[PADRAO[arquivo]]
    m = medidas[nome]
    pct = medicao.percentual_circunferencia(m["perimetro_px"], padrao["perimetro_px"])
    forma = medicao.forma_relativa(m["razao_eixos"], padrao["razao_eixos"])
    ok = medicao.aprovada(pct, TOLERANCIA, forma, TOLERANCIA_FORMA)
    print("%-28s %9.1f%% %9.1f%%  %s" % (nome, pct, forma, "APROVADA" if ok else "REPROVADA"))
