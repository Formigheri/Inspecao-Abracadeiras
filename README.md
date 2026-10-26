# Inspeção de abraçadeiras

Aplicação web que mede a circunferência interna de abraçadeiras pela webcam e compara com
uma peça padrão: o resultado é o percentual da circunferência em relação ao padrão, e a peça
é aprovada ou reprovada conforme uma tolerância. Back-end em Python (Flask + OpenCV) e
interface em HTML, CSS e JavaScript.

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

1. Coloque uma peça boa sob a câmera e clique em **Definir como peça padrão**.
2. Informe a tolerância (± % da circunferência).
3. Coloque a peça a testar e meça: **Medir agora**, ou o modo **Automático**, que mede
   sozinho quando a peça fica parada por alguns segundos.

Use fundo liso escuro e fosco (ou contraluz), luz difusa e câmera parada, de cima, centralizada sobre a peça.
Com fundo escuro, desmarque a opção "Fundo claro".

## Testes

```
python teste_medicao.py
```

## Arquivos

- `app.py`: servidor Flask e rotas da API
- `medicao.py`: processamento da imagem com OpenCV
- `templates/index.html`, `static/`: interface
- `teste_medicao.py`: testes automáticos
