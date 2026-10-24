# Documentação do projeto: Inspeção de abraçadeiras por visão computacional

> Integrantes do grupo: _preencher_
> Disciplina / turma: _preencher_
> Professor(a): _preencher_

## Sumário

1. [Apresentação do projeto](#1-apresentação-do-projeto)
2. [Tecnologias e versões utilizadas](#2-tecnologias-e-versões-utilizadas)
3. [Estrutura de pastas](#3-estrutura-de-pastas)
4. [Instalação e configuração do ambiente](#4-instalação-e-configuração-do-ambiente)
5. [Como usar o sistema](#5-como-usar-o-sistema)
6. [Visão geral da arquitetura](#6-visão-geral-da-arquitetura)
7. [Funcionamento do back-end](#7-funcionamento-do-back-end)
8. [Funcionamento do front-end](#8-funcionamento-do-front-end)
9. [Testes e validação](#9-testes-e-validação)
10. [Limitações conhecidas](#10-limitações-conhecidas)
11. [Melhorias futuras](#11-melhorias-futuras)
12. [Publicação no GitHub](#12-publicação-no-github)
13. [Referências e licenças](#13-referências-e-licenças)

---

## 1. Apresentação do projeto

### 1.1 Problema

Na produção de abraçadeiras metálicas (de rosca sem-fim, tipo T e mini com parafuso),
o diâmetro interno precisa estar dentro de uma tolerância. A conferência manual com
paquímetro é lenta e depende de quem mede.

### 1.2 Proposta

Um sistema web que usa a webcam do computador para medir o diâmetro interno da
peça e indicar automaticamente se ela está **aprovada** ou **reprovada** conforme um
valor nominal e uma tolerância informados pelo usuário.

### 1.3 Escopo desta versão (MVP)

| Faz | Não faz (ainda) |
|---|---|
| Mostra o vídeo da webcam no navegador | Identificar o tipo da abraçadeira |
| Calibra a escala usando uma moeda | Corrigir a distorção da lente |
| Mede o diâmetro interno (furo) em mm | Medir largura da cinta ou outros detalhes |
| Compara com nominal e tolerância | Guardar histórico em banco de dados |
| Mede ao vivo ou sob demanda | Trabalhar com várias peças ao mesmo tempo |
| Guarda histórico e exporta CSV | |

---

## 2. Tecnologias e versões utilizadas

### 2.1 Back-end

| Tecnologia | Versão testada | Para que serve | Licença |
|---|---|---|---|
| Python | 3.13.17 | Linguagem do back-end (recomendado 3.9 ou superior) | PSF |
| Flask | 3.1.3 | Servidor web e rotas da API | BSD-3-Clause |
| Werkzeug | 3.1.9 | Base do Flask (instalado junto) | BSD-3-Clause |
| Jinja2 | 3.1.6 | Motor de templates do Flask (instalado junto) | BSD-3-Clause |
| OpenCV (`opencv-python-headless`) | 5.0.0.93 | Processamento de imagem e detecção de contornos | Apache-2.0 |
| NumPy | 2.5.3 | Arrays numéricos (OpenCV usa por baixo) | BSD-3-Clause |

A versão "headless" do OpenCV é a mesma biblioteca sem as janelas gráficas dela.
Como a interface é o navegador, não precisamos delas.

### 2.2 Front-end

| Tecnologia | Detalhe |
|---|---|
| HTML5 | Estrutura da página (`templates/index.html`) |
| CSS3 | Visual, sem nenhum framework (`static/estilo.css`) |
| JavaScript (ES2017+) | Lógica da tela, sem bibliotecas (`static/script.js`) |
| API `MediaDevices.getUserMedia` | Acesso à webcam pelo navegador |
| API Canvas | Captura de quadros e desenho do círculo sobre o vídeo |
| API Fetch e `FormData` | Envio das imagens para o servidor |
| `localStorage` | Guarda a escala e o histórico no navegador |

Navegadores: Google Chrome ou Microsoft Edge atuais (o desenvolvimento foi feito
pensando em Chromium).

### 2.3 Modelos pré-treinados

**Esta versão não usa nenhum modelo pré-treinado.** A detecção é feita com técnicas
clássicas de visão computacional do OpenCV (binarização por Otsu, detecção de
contornos e análise de hierarquia). Se o grupo incluir um modelo no futuro
(por exemplo, para classificar o tipo de abraçadeira), ele deve ser open source e
listado na seção de [referências](#13-referências-e-licenças).

### 2.4 Ferramentas de apoio

| Ferramenta | Uso |
|---|---|
| Git e GitHub | Controle de versão e entrega do código |
| `unittest` (biblioteca padrão do Python) | Testes automáticos |
| venv (biblioteca padrão do Python) | Ambiente virtual isolado |

---

## 3. Estrutura de pastas

```
inspecao_abracadeiras/
├── app.py                 servidor Flask e rotas da API
├── medicao.py             visão computacional (calibração e medição)
├── teste_medicao.py       testes automáticos
├── requirements.txt       dependências Python
├── README.md              resumo e instruções rápidas
├── DOCUMENTACAO.md        este documento
├── .gitignore             arquivos que o Git deve ignorar
├── templates/
│   └── index.html         página única da aplicação
└── static/
    ├── script.js          lógica do front-end
    └── estilo.css         estilos
```

> O Flask procura o HTML dentro de `templates/` e os arquivos CSS/JS dentro de
> `static/`. Se essas pastas forem renomeadas ou os arquivos ficarem soltos na raiz,
> a página não carrega.

---

## 4. Instalação e configuração do ambiente

O passo a passo abaixo é para **Windows 10/11**. No fim há as diferenças para Linux e macOS.

### 4.1 Instalar o Python

1. Acesse https://www.python.org/downloads/ e baixe o Python 3 mais recente.
2. Execute o instalador e **marque a opção "Add python.exe to PATH"** antes de clicar em *Install Now*.
3. Abra o **PowerShell** e confira:

```
python --version
pip --version
```

Se aparecer a versão nos dois comandos, está certo. Se disser que o comando não foi
reconhecido, tente `py --version` (e use `py` no lugar de `python` nos próximos passos)
ou reinstale marcando a opção do PATH.

### 4.2 Obter o código

Com Git instalado:

```
git clone <endereço-do-repositório>
cd inspecao_abracadeiras
```

Sem Git: baixe o repositório como ZIP pelo botão **Code > Download ZIP** do GitHub,
extraia e entre na pasta pelo PowerShell com `cd`.

### 4.3 Criar o ambiente virtual

O ambiente virtual mantém as bibliotecas do projeto isoladas do resto do computador.

```
python -m venv venv
```

Ative o ambiente:

```
.\venv\Scripts\Activate.ps1
```

Se o PowerShell reclamar de "execução de scripts desabilitada", rode uma vez:

```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

e tente ativar de novo. Alternativa no Prompt de Comando (cmd): `venv\Scripts\activate.bat`.

Quando funcionar, o terminal mostra `(venv)` no começo da linha.

### 4.4 Instalar as dependências

```
pip install -r requirements.txt
```

Isso instala Flask, OpenCV (headless) e NumPy, que são as três dependências diretas.

### 4.5 Rodar o servidor

```
python app.py
```

A saída deve conter algo como `Running on http://127.0.0.1:5000`.
Deixe esse terminal aberto enquanto usa o sistema. Para parar, use `Ctrl + C`.

### 4.6 Abrir no navegador

Acesse **http://127.0.0.1:5000** no Chrome ou Edge e clique em **Permitir** quando o
navegador pedir acesso à câmera.

> A câmera só funciona em `localhost`/`127.0.0.1` ou em páginas `https`.
> Se abrir o app por outro endereço (como o IP da rede), o navegador bloqueia a webcam.

### 4.7 Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `python` não é reconhecido | PATH não configurado | Reinstalar marcando "Add to PATH", ou usar `py` |
| Erro ao ativar o `venv` no PowerShell | Política de execução | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `ModuleNotFoundError: No module named 'flask'` | Ambiente virtual não ativado | Ativar o `venv` e rodar o `pip install` de novo |
| Página abre mas sem vídeo | Permissão da câmera negada ou câmera em uso por outro app | Liberar a câmera no ícone de cadeado da barra de endereço e fechar outros programas que a usem |
| Página abre sem estilo | Pasta `static/` fora do lugar | Conferir a [estrutura de pastas](#3-estrutura-de-pastas) |
| `Address already in use` | Porta 5000 ocupada | Fechar o outro servidor, ou trocar para `app.run(port=5001)` no `app.py` |

### 4.8 Linux e macOS

Os passos são os mesmos, mudando só estes comandos:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

---

## 5. Como usar o sistema

### 5.1 Preparar o ambiente físico

A qualidade da medição depende mais do cenário do que do código:

- Use uma **folha lisa** (branca ou preta fosca) como fundo. A mesa de madeira com veios atrapalha a detecção.
- Use **luz difusa**, sem reflexo forte no metal.
- Deixe a **câmera parada**, apontada de cima para baixo, sempre à mesma distância.
- Se o fundo for claro e a peça escura, deixe marcada a opção "Fundo claro". Se for o contrário, desmarque.

### 5.2 Passo a passo na tela

1. **Calibrar.** Coloque só uma moeda sobre a folha, informe o diâmetro real dela
   (uma moeda de R$ 1 tem cerca de 27 mm) e clique em *Calibrar com a moeda*.
   Aparece "Escala: X px/mm" e um círculo verde sobre a moeda.
2. **Definir a especificação.** Digite o diâmetro **nominal** e a **tolerância** (±) da peça.
3. **Medir.** Retire a moeda, coloque a abraçadeira no mesmo lugar e clique em
   *Medir agora*, ou ligue *Medir ao vivo* para medir continuamente.
4. **Ler o resultado.** O diâmetro aparece em mm com o veredito **APROVADA** (verde)
   ou **REPROVADA** (vermelho). O círculo desenhado sobre o vídeo mostra o furo detectado.
5. **Registrar.** *Registrar no histórico* adiciona a medida à tabela; *Baixar CSV* exporta
   os dados para o Excel.

### 5.3 Ajuste do limiar

O controle **Limiar** começa em "automático" (método de Otsu), que costuma funcionar.
Se o contorno sair errado (por exemplo, reflexo atrapalhando), mova o controle até o
círculo desenhado acompanhar o furo.

### 5.4 Por que calibrar

A câmera enxerga a peça em pixels, mas o resultado precisa ser em milímetros. A
calibração descobre quantos pixels cabem em 1 mm usando a moeda, que tem tamanho
conhecido. Exemplo: moeda de 27 mm aparece com 135 px, então a escala é 135 / 27 = 5 px/mm;
um furo que aparece com 125 px mede 125 / 5 = 25 mm.

Essa escala muda se a câmera for movida, aproximada ou se o zoom mudar. Por isso é
preciso calibrar de novo sempre que mexer na câmera. O sistema guarda a última escala
no navegador, então ela continua válida após recarregar a página.

---

## 6. Visão geral da arquitetura

```
 ┌──────────────────────────── NAVEGADOR ────────────────────────────┐
 │  index.html + estilo.css + script.js                               │
 │   - liga a webcam (getUserMedia)                                   │
 │   - captura um quadro do vídeo (canvas) e converte em JPEG         │
 │   - desenha o círculo detectado e mostra aprovada/reprovada        │
 └───────────────▲────────────────────────────────┬───────────────────┘
                 │ JSON (diâmetro, círculo)       │ POST multipart
                 │                                │ (imagem + parâmetros)
 ┌───────────────┴────────────────────────────────▼───────────────────┐
 │                     SERVIDOR FLASK  (app.py)                       │
 │   GET  /              -> entrega a página                          │
 │   POST /api/calibrar  -> escala em px/mm                           │
 │   POST /api/medir     -> diâmetro do furo em mm                    │
 └───────────────────────────────┬────────────────────────────────────┘
                                 │ chama funções
 ┌───────────────────────────────▼────────────────────────────────────┐
 │               VISÃO COMPUTACIONAL  (medicao.py, OpenCV)            │
 │   binarizar -> achar contornos -> filtrar -> converter px em mm    │
 └────────────────────────────────────────────────────────────────────┘
```

Decisões de projeto:

- **A medição fica no servidor** (Python + OpenCV) e não no navegador, porque o requisito
  do trabalho é um back-end funcional e porque a lógica de visão fica isolada e testável.
- **O servidor não guarda estado.** A escala de calibração fica no navegador e é enviada
  junto a cada pedido de medição. Isso simplifica o back-end (não precisa de sessão nem de banco).
- **O servidor devolve só números** (diâmetro e centro/raio do círculo), não imagens. O
  navegador desenha o círculo sobre o vídeo. Assim cada resposta é pequena, o que permite
  a medição ao vivo.

---

## 7. Funcionamento do back-end

### 7.1 `app.py`: servidor e rotas

| Função | Papel |
|---|---|
| `ler_imagem()` | Lê o arquivo JPEG enviado no formulário e converte em imagem do OpenCV (`cv2.imdecode`) |
| `ler_opcoes()` | Lê `fundo_claro` e `limiar` do formulário |
| `index()` | Rota `GET /`. Devolve `templates/index.html` |
| `calibrar()` | Rota `POST /api/calibrar` |
| `medir()` | Rota `POST /api/medir` |

#### Contrato da API

**`POST /api/calibrar`** (formato `multipart/form-data`)

| Campo | Tipo | Descrição |
|---|---|---|
| `imagem` | arquivo JPEG | Quadro da webcam com a moeda |
| `diametro_moeda` | número (mm) | Diâmetro real da moeda |
| `fundo_claro` | `"true"` ou `"false"` | Fundo claro com objeto escuro, ou o inverso |
| `limiar` | inteiro 0 a 255 | 0 = automático (Otsu) |

Resposta `200`:
```json
{ "px_por_mm": 4.976, "circulo": { "x": 640.1, "y": 360.0, "raio": 67.2 } }
```

**`POST /api/medir`** (formato `multipart/form-data`)

| Campo | Tipo | Descrição |
|---|---|---|
| `imagem` | arquivo JPEG | Quadro da webcam com a abraçadeira |
| `px_por_mm` | número | Escala obtida na calibração |
| `fundo_claro` | `"true"` ou `"false"` | Igual à calibração |
| `limiar` | inteiro 0 a 255 | Igual à calibração |

Resposta `200`:
```json
{ "diametro_mm": 25.31, "circulo": { "x": 640.0, "y": 360.1, "raio": 63.2 } }
```

**Códigos de erro** (em ambas as rotas, corpo `{ "erro": "mensagem" }`):

| Código | Quando acontece |
|---|---|
| `400` | Imagem ausente, parâmetros inválidos ou valores não positivos |
| `422` | Requisição correta, mas não foi possível achar a moeda (calibrar) ou o furo (medir) |

### 7.2 `medicao.py`: o processamento da imagem

Tudo parte de uma imagem BGR (formato do OpenCV) e segue este caminho:

```
imagem colorida
   │  1. escala de cinza
   │  2. desfoque gaussiano 5x5 (tira ruído)
   │  3. binarização (Otsu ou limiar manual)
   │  4. fechamento morfológico (tapa buracos pequenos)
   ▼
máscara preto e branco
   │  5. findContours
   │  6. filtros: área mínima e circularidade
   │  7. diâmetro equivalente (px)
   ▼
conversão para mm: px / (px por mm)
```

| Função | O que faz |
|---|---|
| `binarizar` | Executa as etapas 1 a 4. Se `fundo_claro` for verdadeiro, usa threshold invertido, pois a peça é mais escura que o fundo |
| `circularidade` | Calcula `4 · π · área / perímetro²`. Vale 1 para um círculo perfeito e cai para formas alongadas |
| `diametro_equivalente` | Diâmetro do círculo de mesma área do contorno: `d = √(4 · área / π)` |
| `circulo_do_contorno` | Devolve centro (centroide) e raio para o front desenhar |
| `calibrar` | Acha o maior contorno externo redondo (circularidade ≥ 0,8 e área ≥ 500 px) e calcula `px_por_mm = diâmetro_px / diâmetro_real_mm` |
| `medir_furo` | Acha contornos que estão **dentro** de outros (furos), filtra por área mínima e circularidade, escolhe o maior e converte para mm |
| `aprovada` | `abs(medido - nominal) <= tolerância` |

**Por que o diâmetro "equivalente"?** Usar a área do contorno em vez de medir uma
linha de lado a lado deixa a medida menos sensível a pequenas falhas na borda e a
elipses causadas por leve inclinação da câmera.

**Como o furo é distinguido do resto?** O `findContours` em modo `RETR_CCOMP` devolve
uma hierarquia. Um contorno com "pai" (`h[3] != -1`) está dentro de outro, e é isso
que caracteriza o furo de uma peça em forma de anel.

---

## 8. Funcionamento do front-end

### 8.1 `templates/index.html`

Página única com três regiões:

1. **Vídeo** (`<video id="video">`) com um `<canvas id="camada">` por cima, usado para desenhar o círculo detectado.
2. **Painel** com três blocos: calibração, especificação (nominal, tolerância, fundo, limiar) e medição.
3. **Histórico** em tabela, com botões de exportar e limpar.

Os caminhos do CSS e do JS usam `url_for('static', ...)`, que o Flask resolve.

### 8.2 `static/estilo.css`

CSS simples: layout em duas colunas (`display: grid`) que vira uma coluna em telas
estreitas (`@media`), cartões brancos para cada bloco e as cores verde/vermelho do
resultado, controladas pelas classes `aprovada` e `reprovada`.

### 8.3 `static/script.js`

| Função | Papel |
|---|---|
| `iniciarCamera` | Pede permissão e liga a webcam (`getUserMedia`) |
| `pegarQuadro` | Copia o quadro atual do vídeo para um canvas invisível e gera um JPEG |
| `enviar` | Monta o `FormData` (imagem, fundo, limiar e extras) e faz o `fetch` POST |
| `calibrar` | Chama `/api/calibrar`, guarda a escala e desenha o círculo verde |
| `medir` | Chama `/api/medir`, atualiza o resultado e desenha o círculo (verde ou vermelho) |
| `repetirMedicao` | Modo ao vivo: mede, espera 400 ms e repete. Usa `setTimeout` para nunca haver duas requisições simultâneas |
| `veredito` / `mostrarResultado` | Comparam a medida com nominal e tolerância e pintam a caixa de resultado |
| `registrar`, `desenharHistorico` | Guardam a medida e redesenham a tabela |
| `baixarCsv` | Gera o CSV (separador `;`, vírgula decimal, BOM para acentos) e dispara o download |
| `guardar` / `recuperar` | Leitura e escrita em `localStorage` |

**Fluxo de uma medição**

```
clique em "Medir agora"
  -> pegarQuadro()              captura o vídeo em JPEG
  -> enviar("/api/medir")       POST com imagem + px_por_mm
  -> servidor devolve JSON      { diametro_mm, circulo }
  -> mostrarResultado()         valor e APROVADA/REPROVADA
  -> desenharCirculo()          círculo sobre o vídeo
```

Ao alterar nominal ou tolerância, o veredito da última medida é recalculado na hora,
sem nova medição.

---

## 9. Testes e validação

### 9.1 Testes automáticos

O arquivo `teste_medicao.py` usa imagens desenhadas por código (moeda e anel com
tamanho conhecido) e verifica:

| Teste | Verifica |
|---|---|
| `test_calibracao` | Escala encontrada próxima de 5 px/mm |
| `test_medida_do_furo` | Furo de 25 mm medido com diferença de até 0,6 mm |
| `test_imagem_sem_furo` | Sem furo, não devolve medida |
| `test_tolerancia` | Regra de aprovação |
| `test_fluxo_completo` | Calibrar e depois medir pela API |
| `test_sem_imagem` | Rota responde `400` sem imagem |
| `test_moeda_nao_encontrada` | Rota responde `422` com fundo vazio |

Para rodar: `python teste_medicao.py`

### 9.2 Teste de ponta a ponta

Durante o desenvolvimento, o sistema completo foi executado num Chromium com webcam
simulada (vídeo gerado por código com uma moeda de 27 mm e depois um anel com furo
de 25 mm). Resultado:

| Item | Esperado | Obtido |
|---|---|---|
| Escala | 5,000 px/mm | 4,976 px/mm |
| Diâmetro do furo | 25,00 mm | 25,31 mm |
| Veredito (25 ± 1 mm) | Aprovada | Aprovada |
| Veredito (28 ± 1 mm) | Reprovada | Reprovada |

O erro de cerca de 0,3 mm nesse cenário ideal vem da resolução em pixels e da
suavização das bordas.

### 9.3 Validação com peças reais (a preencher pelo grupo)

Imagens desenhadas não têm reflexo, sombra nem lente real. Recomenda-se medir as
abraçadeiras de verdade e comparar com um paquímetro:

| Peça | Paquímetro (mm) | Sistema (mm) | Diferença (mm) |
|---|---|---|---|
| | | | |
| | | | |
| | | | |

---

## 10. Limitações conhecidas

- **Só mede o diâmetro interno** e não reconhece o tipo de abraçadeira.
- **Sem correção da distorção da lente.** As bordas da imagem podem sair levemente deformadas.
- **Diferença de altura:** a moeda é fina e a abraçadeira é mais alta, então fica mais perto da câmera e parece maior. Isso soma ao erro. Mitigação: calibrar com um objeto da mesma altura da peça.
- **Precisão esperada:** cerca de ±0,5 mm com uma webcam comum bem posicionada.
- **Sensível à iluminação e ao fundo.** Reflexos fortes no metal podem gerar contornos falsos.
- **Uma peça por vez** no campo de visão.
- **Servidor de desenvolvimento.** `app.run(debug=True)` é para uso local. Para produção seria preciso um servidor como Gunicorn ou Waitress, e `debug` desligado.
- **Histórico só no navegador** (`localStorage`): se limpar os dados do navegador, ele se perde.

---

## 11. Melhorias futuras

- Classificar o tipo da abraçadeira por forma ou com um modelo de detecção open source (por exemplo, YOLO), referenciando o modelo e a licença.
- Calibração por padrão xadrez (`cv2.calibrateCamera`) para corrigir a distorção da lente.
- Guardar o histórico em banco de dados (SQLite).
- Medir também a largura da cinta e a espessura.
- Perfis de especificação salvos por tipo de peça.

---

## 12. Publicação no GitHub

### 12.1 Criar o repositório

1. Entre em https://github.com e faça login.
2. Clique em **New repository**, dê o nome `inspecao-abracadeiras`, deixe sem README (já temos um) e clique em **Create repository**.

### 12.2 Enviar o código

No PowerShell, dentro da pasta do projeto:

```
git init
git add .
git commit -m "Primeira versão do sistema de inspeção de abraçadeiras"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/inspecao-abracadeiras.git
git push -u origin main
```

Troque `SEU-USUARIO` pelo usuário do GitHub. Na primeira vez o Git pode pedir login
pelo navegador.

O arquivo `.gitignore` já impede que a pasta `venv/` e os arquivos `__pycache__` subam.

### 12.3 Se o repositório for do grupo

Cada integrante deve ser adicionado em **Settings > Collaborators**, e os commits
devem ser feitos por todos, para o histórico mostrar a contribuição de cada um.

---

## 13. Referências e licenças

- Flask: https://flask.palletsprojects.com (BSD-3-Clause)
- OpenCV: https://opencv.org e https://docs.opencv.org (Apache-2.0)
- NumPy: https://numpy.org (BSD-3-Clause)
- Documentação MDN sobre `getUserMedia`: https://developer.mozilla.org/docs/Web/API/MediaDevices/getUserMedia
- Documentação MDN sobre Canvas: https://developer.mozilla.org/docs/Web/API/Canvas_API
- Documentação do OpenCV sobre contornos e limiarização (Otsu):
  https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html
- N. Otsu, "A Threshold Selection Method from Gray-Level Histograms",
  IEEE Transactions on Systems, Man, and Cybernetics, 1979 (método usado na binarização automática).

Nenhum modelo pré-treinado foi utilizado nesta versão.
