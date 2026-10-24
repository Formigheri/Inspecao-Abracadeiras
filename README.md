# Inspeção de abraçadeiras

Aplicação web que mede o diâmetro interno de abraçadeiras pela webcam e indica se a
peça está aprovada ou reprovada conforme uma tolerância. Back-end em Python (Flask +
OpenCV) e interface em HTML, CSS e JavaScript.

A documentação completa (tecnologias e versões, instalação passo a passo,
funcionamento do back-end e do front-end) está em [DOCUMENTACAO.md](DOCUMENTACAO.md).

## Início rápido

```
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Abra http://127.0.0.1:5000 e permita o uso da câmera.

No Linux/macOS, ative o ambiente com `source venv/bin/activate`.

## Uso resumido

1. Coloque uma moeda sobre uma folha lisa e clique em **Calibrar**.
2. Informe o diâmetro nominal e a tolerância da peça.
3. Coloque a abraçadeira no lugar da moeda e clique em **Medir agora**.

## Testes

```
python teste_medicao.py
```

## Arquivos

- `app.py`: servidor Flask e rotas da API
- `medicao.py`: processamento da imagem com OpenCV
- `templates/index.html`, `static/`: interface
- `teste_medicao.py`: testes automáticos
