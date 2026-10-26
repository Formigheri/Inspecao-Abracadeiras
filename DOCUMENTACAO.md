# Documentação do projeto: Inspeção de abraçadeiras por visão computacional

**Integrantes do grupo**

- Felipe dos Santos Bueno
- Vinicius Menegol Cardoso
- Guilherme Pedroni Formigheri
- Kael Eduardo Faldi
- Eduardo da Cruz dos Santos

**Professor:** Vinícius Colombo Sonda

**Disciplina / turma:** _preencher_

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
a circunferência interna precisa estar dentro de uma tolerância. Uma peça amassada ou
mal conformada tem a circunferência diferente da peça boa. A conferência manual é lenta
e depende de quem mede.

### 1.2 Proposta

Um sistema web que usa a webcam do computador para medir a **circunferência interna**
da peça e compará-la com a de uma **peça padrão**, uma abraçadeira boa escolhida pelo
operador. O resultado é um **percentual da circunferência** em relação ao padrão, e a peça
é **aprovada** ou **reprovada** conforme uma tolerância em porcentagem. Como o perímetro de uma
cinta amassada não muda (a fita tem comprimento fixo), a peça também é comparada com o padrão
pela **forma**: a razão entre os eixos da elipse ajustada ao contorno.

Exemplo: se o padrão tem circunferência de 395,6 px e a peça testada tem 368,3 px, ela tem
93,1% da circunferência do padrão. Com tolerância de ±2%, é reprovada.

### 1.3 Por que comparar com um padrão

- A comparação é **relativa**: padrão e peça testada passam pela mesma câmera, então a
  escala (pixels por milímetro) se cancela e **não é preciso calibrar a câmera**.
- O limite de aprovação pode ser **definido com dados**: medindo uma peça boa e uma
  reprovada de verdade, vê-se qual porcentagem separa as duas.
- A circunferência é medida pelo **perímetro real do contorno**, não calculada a partir
  de um diâmetro. Por isso uma peça deformada (oval, achatada) é detectada, o que não
  aconteceria se o sistema assumisse que toda peça é um círculo perfeito.

### 1.4 Escopo desta versão (MVP)

| Faz | Não faz (ainda) |
|---|---|
| Mostra o vídeo da webcam no navegador | Identificar o tipo da abraçadeira |
| Guarda uma peça padrão e compara a circunferência | Corrigir a distorção da lente |
| Mede o perímetro do furo e devolve o % do padrão | Isolar a peça em qualquer fundo (ver limitações) |
| Aprova ou reprova por tolerância em % | Guardar histórico em banco de dados |
| Desenha o contorno real detectado sobre o vídeo | Trabalhar com várias peças ao mesmo tempo |
| Mede sob demanda ou automaticamente quando a peça para | Mostrar medidas em milímetros |
| Suaviza o contorno para o perímetro não oscilar | Ignorar texto ou manchas no fundo |
| Guarda histórico e exporta CSV | |

> Uma versão anterior tinha também média de vários quadros, subtração de um fundo vazio, guia da
> peça padrão, modo ao vivo e calibração em milímetros. Como nenhum desses recursos mostrou ganho
> com peças reais, foram retirados para manter o MVP simples (seção 11).

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

**Esta versão não usa nenhum modelo pré-treinado.** Um modelo de remoção de fundo (U²-Net) foi avaliado e descartado (seção 9.3). A detecção é feita com técnicas
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
├── medicao.py             visão computacional (medição)
├── teste_medicao.py       testes automáticos
├── validar_fotos.py       mede as fotos reais de fotos_teste/ e mostra o veredito
├── fotos_teste/           4 fotos reais usadas na validação (seção 9.4.1)
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

- Use um **fundo liso e escuro** (cartolina preta fosca, por exemplo). O metal brilhante fica
  claro contra o fundo escuro, e o furo da peça aparece como um buraco escuro bem definido.
  Fundo claro funciona, mas exige que a peça seja bem mais escura que o papel.
- Uma alternativa muito robusta é o **contraluz**: apoiar a peça sobre uma superfície branca iluminada por baixo (uma folha sobre uma tela de celular ou tablet com fundo branco, ou uma caixa de luz). A cinta metálica vira uma silhueta escura e o furo fica claro, com contraste forte e bordas nítidas. É a técnica usada em inspeção industrial de contornos. Nesse caso, deixe marcada a opção "Fundo claro".
- Outra opção é a **luz coaxial**: uma luz bem perto da câmera (um ring light, ou a lanterna do celular colada na webcam) faz a sombra cair atrás da peça, onde a câmera não enxerga.
- Use **luz difusa**, sem reflexo forte no metal. Uma caixa de papelão forrada com papel branco ou vegetal, com um furo para a câmera, ajuda a espalhar a luz.
- Deixe a **câmera parada, apontada de cima para baixo e centralizada sobre a peça**. Câmera
  inclinada mostra a parede interna da cinta e distorce o contorno.
- Posicione cada peça sempre **no mesmo lugar** e na **mesma regulagem** (as de rosca sem-fim
  são ajustáveis, então a circunferência muda conforme o aperto do parafuso).

### 5.2 Passo a passo na tela

1. **Definir a peça padrão.** Coloque uma peça boa sob a câmera e clique em
   *Definir como peça padrão*. O contorno detectado aparece em azul e a tela mostra a
   circunferência do padrão em pixels. Esse valor fica guardado no navegador.
2. **Definir o critério.** Informe a **tolerância ±%** da circunferência (padrão: 2%) e a **tolerância da forma** (padrão: 5%), que é o quanto a peça pode ficar mais achatada que o padrão.
3. **Medir.** Troque pela peça a testar e use um dos modos (seção 5.3).
4. **Ler o resultado.** A tela mostra o **percentual da circunferência** em relação ao padrão e o
   veredito **APROVADA** (verde) ou **REPROVADA** (vermelho). O contorno desenhado sobre o vídeo
   mostra o formato real detectado. Também aparecem a circunferência em pixels e a forma em % do padrão.
5. **Registrar.** Informe em *A peça realmente é* se a peça é **boa**, **defeituosa** ou "não sei" (é uma
   anotação de quem mede, o sistema não descobre isso) e clique em *Registrar no histórico*. A medida entra
   na tabela com a coluna "Situação real" e uma conferência contra o veredito do sistema. O resumo acima da
   tabela mostra quantas o sistema acertou e conta separadamente as **boas reprovadas** e as
   **defeituosas aprovadas** (a mais grave num controle de qualidade). O registro é manual: medir não
   registra sozinho. *Baixar CSV* exporta a tabela.

Para usar outro modelo de abraçadeira, defina uma nova peça padrão: cada modelo tem o seu.

### 5.3 Modos de medição

| Modo | Como funciona | Quando usar |
|---|---|---|
| **Manual** | O botão *Medir agora* captura um quadro e mede | Conferências pontuais |
| **Automático (peça parada)** | O sistema observa o vídeo; quando a cena fica parada pelo tempo definido em *Esperar (s)*, mede uma vez. Só mede de novo depois que algo se mexer, ou seja, quando a peça for trocada | Inspeção em sequência, sem apertar botão |

No modo automático, a tela mostra o estado ("Movimento detectado...", "Peça parada há 1,2 s...",
"Medida feita. Troque a peça para medir de novo."). A detecção compara o vídeo com o quadro
anterior e considera a cena em movimento quando mais de 0,5% dos pixels mudam bastante. Isso ignora o
ruído da webcam e pequenas variações de luz, mas os valores podem precisar de ajuste conforme a
câmera (constantes no topo do `script.js`).

### 5.4 Como o sistema decide e como escolher as tolerâncias

Uma peça é **aprovada** quando as duas condições valem:

1. **Perímetro:** `abs(percentual - 100) <= tolerância`. Padrão de 2%.
2. **Forma:** `forma >= 100 - tolerância da forma`. Padrão de 5%.

Onde isso está no código:

| O quê | Onde |
|---|---|
| Regra de aprovação (back-end) | `aprovada()` em `medicao.py` |
| Regra de aprovação usada na tela | `veredito()` em `static/script.js` (mesma regra, repetida no front para o veredito aparecer na hora, sem nova medição) |
| Valores padrão das tolerâncias (2 e 5) | campos `tolerancia` e `toleranciaForma` em `templates/index.html` |
| Cálculo do percentual e da forma | `percentual_circunferencia()`, `razao_dos_eixos()` e `forma_relativa()` em `medicao.py` |

As tolerâncias **não são gravadas**: voltam ao padrão ao recarregar a página. Já a peça padrão (perímetro e
razão dos eixos) e o histórico ficam no `localStorage` do navegador. Se mudar a regra, é preciso mudar
`aprovada()` e `veredito()` juntas.

Para escolher as tolerâncias, meça a peça padrão, uma peça boa e uma reprovada de verdade. Se a reprovada deu,
por exemplo, 93% e uma boa variou entre 99% e 101%, uma tolerância de ±3% separa as duas. O mesmo vale para a
forma. Registre os valores no histórico e use o CSV para justificar a escolha no relatório.

### 5.5 Ajuste do limiar

O controle **Limiar** começa em "automático" (método de Otsu), que costuma funcionar. Se o
contorno desenhado não acompanhar o furo, mova o controle até acompanhar.


---

## 6. Visão geral da arquitetura

```
 ┌──────────────────────────── NAVEGADOR ────────────────────────────┐
 │  index.html + estilo.css + script.js                               │
 │   - liga a webcam (getUserMedia)                                   │
 │   - detecta quando a peça para e captura um quadro (canvas)       │
 │   - guarda o padrão, desenha o contorno e mostra o veredito        │
 └───────────────▲────────────────────────────────┬───────────────────┘
                 │ JSON (perímetro, %, contorno)  │ POST multipart
                 │                                │ (quadros + parâmetros)
 ┌───────────────┴────────────────────────────────▼───────────────────┐
 │                     SERVIDOR FLASK  (app.py)                       │
 │   GET  /              -> entrega a página                          │
 │   POST /api/medir     -> perímetro do furo e % em relação ao padrão│
 └───────────────────────────────┬────────────────────────────────────┘
                                 │ chama funções
 ┌───────────────────────────────▼────────────────────────────────────┐
 │               VISÃO COMPUTACIONAL  (medicao.py, OpenCV)            │
 │   binarizar -> achar o furo -> suavizar o contorno -> medir o     │
 │   perímetro                                                        │
 └────────────────────────────────────────────────────────────────────┘
```

Decisões de projeto:

- **A medição fica no servidor** (Python + OpenCV) e não no navegador, porque o requisito
  do trabalho é um back-end funcional e porque a lógica de visão fica isolada e testável.
- **O servidor não guarda estado.** A circunferência da peça padrão fica no
  navegador e é enviada junto a cada pedido. Isso simplifica o back-end (não precisa de sessão nem de banco).
- **A detecção de "peça parada" fica no navegador**, comparando quadros reduzidos do vídeo. Assim o servidor
  só recebe pedidos quando há de fato uma medição a fazer.
- **O servidor devolve números e pontos** (perímetro, percentual, contorno), não imagens. O
  navegador desenha o contorno sobre o vídeo. Cada resposta é pequena.
---
## 7. Funcionamento do back-end

### 7.1 `app.py`: servidor e rotas

| Função | Papel |
|---|---|
| `ler_imagem()` | Converte o JPEG enviado no campo `imagem` em imagem do OpenCV (`cv2.imdecode`) |
| `ler_opcoes()` | Lê `fundo_claro` e `limiar` do formulário |
| `ler_numero_opcional()` | Lê um número positivo que pode estar ausente (devolve `None`), como o perímetro e a razão dos eixos do padrão |
| `ErroDeRequisicao` | Exceção que o Flask transforma numa resposta `400` com a mensagem |
| `index()` | Rota `GET /`. Devolve `templates/index.html` |
| `medir()` | Rota `POST /api/medir` |

#### Contrato da API

**`POST /api/medir`** (formato `multipart/form-data`)

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `imagem` | arquivo JPEG | sim | Quadro da webcam |
| `fundo_claro` | `"true"` ou `"false"` | não (padrão `true`) | Fundo claro com peça escura, ou o inverso |
| `limiar` | inteiro 0 a 255 | não (padrão 0) | 0 = automático (Otsu) |
| `perimetro_padrao_px` | número | não | Circunferência da peça padrão, em pixels |
| `razao_padrao` | número | não | Razão dos eixos (forma) da peça padrão |

Resposta `200`:
```json
{
  "perimetro_px": 368.3,
  "area_px": 9120.0,
  "circularidade": 0.992,
  "razao_eixos": 0.949,
  "contorno": [[640, 307], [641, 307], ...],
  "percentual": 93.1,
  "forma": 100.0
}
```
Os campos `percentual` e `forma` aparecem só quando `perimetro_padrao_px` e `razao_padrao` são enviados. Para **definir a peça
padrão**, o front chama esta rota sem esses campos e guarda o `perimetro_px` e a `razao_eixos` devolvidos.

**Códigos de erro** (corpo `{ "erro": "mensagem" }`):

| Código | Quando acontece |
|---|---|
| `400` | Imagem ausente ou inválida, parâmetros inválidos |
| `422` | Requisição correta, mas não foi possível achar o furo |

### 7.2 `medicao.py`: o processamento da imagem

Tudo parte de uma imagem BGR (formato do OpenCV) e segue este caminho:

```
quadro da webcam
   │  1. escala de cinza
   │  2. desfoque gaussiano 5x5 (tira ruído)
   │  3. binarização: Otsu ou limiar manual
   │  4. fechamento morfológico (tapa buracos pequenos)
   ▼
máscara preto e branco
   │  5. findContours com hierarquia
   │  6. furo = contorno dentro de outro, com área mínima
   │  7. suavização do contorno e perímetro
   ▼
circunferência em pixels  ->  % em relação ao padrão
```

| Função | O que faz |
|---|---|
| `binarizar` | Executa as etapas 1 a 4. Usa threshold, invertido se `fundo_claro` (peça mais escura que o fundo) |
| `suavizar` | Média gaussiana ao longo da curva do contorno (janela de cerca de 4 px, curva fechada) |
| `perimetro` | Comprimento do contorno suavizado, em pixels (a circunferência) |
| `circularidade` | `4 · π · área / perímetro²`. Vale 1 para um círculo perfeito e cai para formas deformadas |
| `razao_dos_eixos` | Menor eixo dividido pelo maior da elipse ajustada ao contorno (`cv2.fitEllipse`). Vale 1 para uma peça redonda e cai quando ela é achatada |
| `forma_relativa` | `100 · razão_da_peça / razão_do_padrão` |
| `pontos_do_contorno` | Lista enxuta de pontos do contorno suavizado (até cerca de 300) para o front desenhar o formato real |
| `achar_furo` | Procura contornos que estão **dentro** de outros, filtra por área e escolhe o maior |
| `medir_peca` | Mede o furo e devolve perímetro, área, circularidade, razão dos eixos e contorno |
| `percentual_circunferencia` | `100 · perímetro_da_peça / perímetro_do_padrão` |
| `aprovada` | Aprova se `abs(percentual - 100) <= tolerância` **e** `forma >= 100 - tolerância_da_forma` |

**Por que suavizar o contorno.** Um contorno em pixels é irregular, e o perímetro é muito sensível a
essas irregularidades: cada reentrância pequena aumenta o comprimento. Em borda irregular, somar os
segmentos do contorno cru superestimou o perímetro em até 28% nos testes (a aproximação por polígono de 2 px
ainda errava por até 17%), enquanto o contorno suavizado errou cerca de 4% (seção 9.2). A suavização é a mesma para o padrão e para a
peça testada, então o pequeno viés que sobra se cancela no percentual.

**Por que o perímetro e não o diâmetro?** O diâmetro (ou o equivalente pela área) assume que o furo
é um círculo. Numa peça amassada isso esconde parte do defeito. O perímetro acompanha a forma real
do contorno e capta a deformação.

**Como o furo é distinguido do resto?** O `findContours` em modo `RETR_CCOMP` devolve uma
hierarquia. Um contorno com "pai" (`h[3] != -1`) está dentro de outro, e é isso que caracteriza o
furo de uma peça em forma de anel. A circularidade mínima para aceitar um furo é baixa (0,3) de
propósito: uma peça amassada precisa ser detectada para poder ser reprovada.
---
## 8. Funcionamento do front-end

### 8.1 `templates/index.html`

Página única com estas regiões:

1. **Vídeo** (`<video id="video">`) com um `<canvas id="camada">` por cima, usado para desenhar o contorno detectado.
2. **Painel** com: peça padrão, critério (tolerância em %, fundo, limiar), e medição (modo, resultado, detalhes e registro).
3. **Histórico** em tabela, com botões de exportar e limpar.

Os caminhos do CSS e do JS usam `url_for('static', ...)`, que o Flask resolve.

### 8.2 `static/estilo.css`

CSS simples: layout em duas colunas (`display: grid`) que vira uma coluna em telas estreitas
(`@media`), cartões brancos para cada bloco e as cores verde/vermelho do resultado, controladas
pelas classes `aprovada` e `reprovada`.

### 8.3 `static/script.js`

| Função | Papel |
|---|---|
| `iniciarCamera` | Pede permissão e liga a webcam (`getUserMedia`) |
| `pegarQuadro` | Copia o quadro atual do vídeo para um canvas invisível e gera um JPEG |
| `enviar` | Captura um quadro, monta o `FormData` (quadro, opções e extras) e faz o `fetch` POST |
| `definirPadrao` | Chama `/api/medir`, guarda o `perimetro_px` do padrão e desenha o contorno em azul |
| `medir` | Chama `/api/medir` com o padrão, atualiza o resultado e desenha o contorno (verde ou vermelho) |
| `movimentoDaCena` | Compara uma versão reduzida (160x90) do vídeo com a da checagem anterior e devolve a fração de pixels que mudaram bastante |
| `passoAutomatico` | Modo automático: espera a cena ficar parada pelo tempo escolhido, mede uma vez e só mede de novo depois que algo se mexer |
| `trocarModo` | Troca entre manual e automático, invalidando o laço anterior |
| `limparDesenho`, `desenharContorno` | Limpam o canvas e desenham o contorno da medida sobre o vídeo |
| `veredito` / `mostrarResultado` | Comparam o percentual (100% ± tolerância) e a forma (não menor que 100% − tolerância da forma) e pintam a caixa de resultado |
| `registrar`, `desenharHistorico` | Guardam a medida (com a situação real informada) e redesenham a tabela e o placar |
| `conferir` | Compara o veredito do sistema com a situação real: `acertou`, `boa reprovada` ou `defeituosa aprovada` |
| `baixarCsv` | Gera o CSV (separador `;`, vírgula decimal, BOM para acentos; colunas de situação real e conferência) e dispara o download |
| `guardar` / `recuperar` | Leitura e escrita em `localStorage` |

**Fluxo do modo automático**

```
vídeo ao vivo
  -> movimentoDaCena()          a cada 200 ms compara com o quadro anterior
  -> cena parada >= "Esperar"   e o sistema está "armado"
  -> enviar("/api/medir")         servidor mede o quadro
  -> mostrarResultado()         "93,1 %" e APROVADA/REPROVADA
  -> desarma                    só mede de novo depois de detectar movimento
```

Ao alterar a tolerância, o veredito da última medida é recalculado na hora, sem nova medição.
---
## 9. Testes e validação

### 9.1 Testes automáticos

O arquivo `teste_medicao.py` usa imagens desenhadas por código (anéis redondos, menores, ovais e de
borda irregular, com tamanho conhecido) e tem 17 testes:

| Grupo | Testes |
|---|---|
| Perímetro e percentual | Perímetro de um furo de 125 px a menos de 2% de π × 125; mesma peça dá 100%; furo de 115 px contra 125 px dá cerca de 92%; peça oval dá cerca de 93% e circularidade menor que a do padrão |
| Regra | Regra de 100% ± tolerância; regra da forma; peça achatada com perímetro igual ao do padrão é reprovada pela forma; imagem sem furo não devolve medida |
| Robustez | Medida estável com ruído forte na imagem; a suavização reduz o efeito da borda irregular |
| API | Definir padrão e medir peça igual; peça deformada abaixo do padrão; sem imagem (`400`); parâmetro inválido (`400`); furo não encontrado (`422`) |

Para rodar: `python teste_medicao.py`

### 9.2 Experimentos com imagens desenhadas

Resultados medidos durante o desenvolvimento (círculo de referência com perímetro teórico de 392,7 px):

| Situação | Sem a melhoria | Com a melhoria |
|---|---|---|
| Borda irregular do furo (amplitude de 2,5 px) | 115% a 117% do esperado (polígono de 2 px); 127% a 128% (contorno cru) | cerca de 104% (contorno suavizado) |
| Ruído forte na imagem (desvio de 18 níveis) | 100% | 100% (o desfoque e o Otsu já absorvem esse ruído) |

Em imagens desenhadas, o desfoque e o Otsu já absorvem o ruído da webcam. Um protótipo com média de
vários quadros e outro com subtração de fundo vazio (que corrigia um papel riscado, de 157% para 100%)
chegaram a ser feitos e foram retirados, porque não houve como confirmá-los com peças reais.

### 9.3 Teste de ponta a ponta

O sistema completo foi executado num Chromium com webcam simulada (vídeos gerados por código):

| Situação | Esperado | Obtido |
|---|---|---|
| Padrão sobre fundo liso | cerca de 394,8 px | 394,8 px |
| Mesma peça medida contra o padrão | 100% (aprovada) | 100,0% (aprovada) |
| Modo automático com a peça parada | 1 medição em cerca de 5 s | 1 medição |
| Modo automático com a peça indo e parando (13 s) | 2 ou mais medições | 3 medições |
| Voltar para o modo manual | 0 novas medições | 0 |
| Peça oval (semieixos 62 e 53 px) com tolerância de 2% | cerca de 93% (reprovada) | 93,1% (reprovada) |

Esta tabela foi obtida na versão anterior, com mais recursos; na versão enxuta foram repetidos
apenas o padrão, a medida da mesma peça e o modo automático com a peça parada.

Observação: nesses testes a **circularidade** da peça oval foi 0,992 contra 1,001 do padrão. Ou seja,
a circularidade quase não muda numa deformação leve, e é o **percentual da circunferência** que
separa as peças. Por isso o critério usa o percentual e a razão dos eixos, e a circularidade é só informativa.

### 9.4 Teste com foto real

Foi testada uma foto real de duas abraçadeiras de rosca sem-fim (uma boa e uma deformada) sobre
papel branco. A segmentação por limiar de brilho ou por bordas **não isolou o furo de
forma confiável** nessa foto, porque:

- metal prateado sobre papel branco tem pouco contraste;
- há sombra e o papel tem texto visível por transparência;
- a câmera estava inclinada, então aparecem a parede interna da cinta e o aro de cima.

Também foi testada a **normalização do fundo**: estimar o fundo (filtro de mediana em imagem
reduzida) e subtrair, para destacar só o que difere dele, sem depender de o fundo ser claro ou escuro.
O método encontrou os dois furos nas posições certas, mas o contorno ficou irregular e dentro da borda
real (pegou a sombra e o papel dentro do furo). Variando os parâmetros, a razão entre o perímetro das
duas peças oscilou entre **57% e 100%**, o que torna o resultado inutilizável para decidir aprovação.
O perímetro é muito sensível a contornos irregulares.

Depois da implementação da suavização do contorno, a foto foi testada de novo,
com cada abraçadeira recortada separadamente (o sistema mede uma peça por vez). Resultados:

- Com o método padrão (limiar automático de Otsu), a peça da esquerda **não foi detectada**. Só com um limiar
  manual específico (160) as duas foram detectadas, e a razão entre elas foi 93,4%. Com limiares vizinhos
  (140 e 180) a medida falha ou se perde, então esse acerto é coincidência e não robustez.
- Com o fundo estimado, mas agora com o contorno suavizado, a razão entre as duas peças continuou entre
  **59% e 97%**. A suavização corrige irregularidades pequenas da borda, mas aqui o problema é a **posição**
  da borda: o contorno cai dentro ou fora da cinta conforme o limiar.

Mudar saturação ou matiz também não resolve: o metal prateado e o papel branco são ambos neutros
(sem cor), então esses canais não os separam. Ajustar contraste ou brilho só reescala as intensidades
e não cria diferença onde ela não existe.

Por fim, foi avaliado um **modelo pré-treinado de remoção de fundo**, o U²-Net (via biblioteca `rembg`,
nas versões `u2netp` e `u2net`, cerca de 1 s por quadro na CPU). O modelo recortou cada abraçadeira como um
**disco cheio**, sem o furo, e incluiu a sombra como parte da peça. Mesmo medindo o contorno externo, a
razão entre as duas peças variou de 94,6% a 99,2% conforme o limiar da máscara, o que é do tamanho da
tolerância. Esses modelos são treinados para recortes visuais (achar "o objeto" com borda suave e sem
buracos), e não para medir. Modelos generativos que "limpam" a imagem seriam piores, pois inventam pixels
e podem deixar redonda uma peça amassada, escondendo o defeito. O modelo foi **descartado** para a medição.

A conclusão é que o problema está nas **condições da imagem** e não no processamento. O sistema depende
do cenário físico (seção 5.1). A validação com peças reais nessas condições é o próximo passo.

### 9.4.1 Fotos com fundo preto

O grupo fotografou as peças sobre uma base preta fosca (4 fotos: duas peças sozinhas e dois pares lado a lado).
Com fundo escuro (opção "Fundo claro" desmarcada), o contorno do furo passou a acompanhar a cinta nas
quatro fotos, o que não acontecia com o papel branco. Os pares foram medidos recortando cada peça (o sistema
mede uma por vez), com a câmera em ângulo e a peça longe do centro.

Primeiro resultado, com o fechamento morfológico fraco (3x3, 2 iterações) e suavização de 4 px: duas peças
aparentemente iguais deram **117,5%** uma da outra, porque a rosca e o reflexo deixavam o contorno cheio de
reentrâncias que somavam perímetro. Com fechamento de 7x7 (3 iterações) e suavização de 10 px (valores
adotados no código), as mesmas duas peças deram **100,5%**.

Achado importante: a cinta é uma fita de comprimento fixo, então amassar a peça **não muda o perímetro**
se o aperto for o mesmo. Na foto 3, a peça da esquerda está visivelmente achatada, mas seu perímetro ficou em
99,8% da peça da direita. O que muda é a forma: a razão entre os eixos da elipse ajustada foi 0,88 na peça
achatada contra 0,95 na peça normal. Ou seja, o percentual de circunferência detecta diferença de **aperto
ou tamanho** (peça mais frouxa ou mais apertada), mas não detecta sozinho a deformação. O sistema passou então a
comparar também a **forma**. Na foto 3, com a peça da direita (a mais redonda, considerada aprovada pelo grupo)
como padrão, a da esquerda deu 99,8% de perímetro e 92,4% de forma, e foi **reprovada** com tolerância de forma de 5%.
Na foto 4, as duas peças deram 100,5% de perímetro e 100,0% de forma (aprovada).
As quatro fotos estão em `fotos_teste/` e o resultado acima se repete com `python validar_fotos.py`. Padrão e peça só podem ser
comparados dentro do mesmo enquadramento: entre as fotos 3 e 4 a câmera mudou e o perímetro difere em cerca de 3%.

### 9.5 Validação com peças reais (a preencher pelo grupo)

| Peça | Situação (boa ou deformada) | % medido | Veredito esperado | Veredito do sistema |
|---|---|---|---|---|
| Padrão | boa | 100% | aprovada | |
| | | | | |
| | | | | |

Sugestão de roteiro: montar o cenário (fundo preto ou contraluz), definir o padrão, medir cada peça 5 vezes no
modo automático e registrar no histórico **informando a situação real** (boa ou defeituosa). Ao final, baixar
o CSV: ele já traz o veredito do sistema, a situação real e a conferência, e serve de base para esta tabela.
A variação entre as 5 medidas da mesma peça indica a repetibilidade do sistema, e o placar do histórico mostra
quantas boas foram reprovadas e quantas defeituosas foram aprovadas.
---
## 10. Limitações conhecidas

- **Depende do cenário físico.** A detecção usa contraste. Metal prateado sobre fundo claro, sombras e reflexos fortes atrapalham (ver seção 9.4). Recomenda-se fundo escuro fosco ou contraluz, e luz difusa.
- **Câmera inclinada ou fora do centro** mostra a parede interna da cinta e distorce o contorno. A câmera deve ficar de cima, centralizada.
- **Fundo com texto ou manchas** é confundido com a peça. Por isso o fundo deve ser liso.
- **Sem escala em milímetros.** O sistema só compara com o padrão e não mostra a medida real.
- **Abraçadeiras ajustáveis** (rosca sem-fim) mudam de circunferência conforme o aperto. A comparação só vale com padrão e peça na mesma regulagem.
- **Cada modelo precisa do seu padrão.** O percentual compara a peça com o padrão, não com um valor absoluto.
- **Sem correção da distorção da lente.** As bordas da imagem podem sair levemente deformadas.
- **Posição na imagem.** Padrão e peça testada devem ficar no mesmo lugar e à mesma distância da câmera, senão a escala muda e o percentual sai errado.
- **Modo automático:** a detecção de "peça parada" foi testada só com vídeos simulados. Em webcams reais os limites de movimento (constantes no `script.js`) podem precisar de ajuste.
- **Validação:** os resultados desta documentação vêm de imagens desenhadas por código e de uma foto real que não pôde ser medida. A medição com peças reais em cenário controlado ainda precisa ser feita (seção 9.5).
- **A forma é medida no plano da imagem.** Uma deformação que incline a peça em vez de achatá-la pode aparecer como achatamento, e a câmera inclinada também reduz a razão dos eixos. Os valores de 5% e 2% ainda não foram calibrados com um conjunto grande de peças.
- **Só mede o furo** e não reconhece o tipo de abraçadeira.
- **Uma peça por vez** no campo de visão.
- **Servidor de desenvolvimento.** `app.run(debug=True)` é para uso local. Para produção seria preciso um servidor como Gunicorn ou Waitress, e `debug` desligado.
- **Padrão e histórico só no navegador** (`localStorage`): se limpar os dados do navegador, eles se perdem.
---
## 11. Melhorias futuras

- Validação com um conjunto de fotos e peças reais em cenário controlado (fundo preto ou contraluz).
- Classificar o tipo da abraçadeira por forma ou com um modelo de detecção open source (por exemplo, YOLO), referenciando o modelo e a licença.
- Calibração por padrão xadrez (`cv2.calibrateCamera`) para corrigir a distorção da lente.
- Guardar peças padrão (uma por modelo) e o histórico em banco de dados (SQLite).
- Reprovar também por forma (por exemplo, comparando o contorno com o do padrão), além do perímetro.
- Reintroduzir, se as fotos reais mostrarem necessidade: subtração de um quadro do fundo vazio (para fundo com texto), média de vários quadros (para webcam ruidosa) e calibração em milímetros com uma moeda.
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

- X. Qin et al., "U2-Net: Going Deeper with Nested U-Structure for Salient Object Detection", Pattern Recognition, 2020 (modelo avaliado e descartado na seção 9.4; licença Apache-2.0).
- rembg: https://github.com/danielgatis/rembg (biblioteca usada para rodar o U²-Net no teste; licença MIT).

Nenhum modelo pré-treinado faz parte do sistema final.
