// Lógica do front-end: liga a webcam, captura um quadro, envia ao servidor Flask
// e mostra o resultado. Também cuida do modo automático, do histórico e do CSV.

const $ = (id) => document.getElementById(id);

// detecção de movimento: um pixel "mudou" se a diferença passar de MUDANCA_DE_PIXEL (0 a 255),
// e a cena está em movimento se mais que LIMITE_MOVIMENTO dos pixels mudaram
const MUDANCA_DE_PIXEL = 25;
const LIMITE_MOVIMENTO = 0.005;
const PASSO_AUTOMATICO = 200;           // ms entre uma checagem e outra

const video = $("video");
const camada = $("camada");
const ctx = camada.getContext("2d");
// canvas fora da página, usado só para capturar os quadros do vídeo
const quadro = document.createElement("canvas");
// versão reduzida do vídeo, usada só para detectar movimento
const amostra = document.createElement("canvas");
amostra.width = 160;
amostra.height = 90;
const ctxAmostra = amostra.getContext("2d", { willReadFrequently: true });

let perimetroPadrao = null;  // circunferência da peça padrão, em pixels
let razaoPadrao = null;      // razão dos eixos (forma) da peça padrão
let ultima = null;           // última medida devolvida pelo servidor
let historico = [];

let ciclo = 0;               // identifica o laço ativo; mudar de modo invalida os antigos


// ---------- armazenamento local ----------

// o padrão e o histórico ficam no navegador para sobreviver a um recarregamento
function guardar(chave, valor) {
  try {
    localStorage.setItem(chave, JSON.stringify(valor));
  } catch (e) {
    // sem localStorage ou sem espaço, o sistema segue sem salvar
  }
}

function recuperar(chave) {
  try {
    return JSON.parse(localStorage.getItem(chave));
  } catch (e) {
    return null;
  }
}

function avisar(texto) {
  $("aviso").textContent = texto || "";
}

function esperar(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}


// ---------- câmera ----------

async function iniciarCamera() {
  try {
    // só funciona em localhost ou https
    const fluxo = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false,
    });
    video.srcObject = fluxo;
  } catch (erro) {
    avisar("Não consegui acessar a câmera. Veja se o navegador deu permissão.");
  }
}

// o canvas do contorno precisa ter o mesmo tamanho do vídeo
video.addEventListener("loadedmetadata", () => {
  camada.width = video.videoWidth;
  camada.height = video.videoHeight;
});

function pegarQuadro() {
  quadro.width = video.videoWidth;
  quadro.height = video.videoHeight;
  quadro.getContext("2d").drawImage(video, 0, 0);
  return new Promise((resolve) => quadro.toBlob(resolve, "image/jpeg", 0.92));
}

function cameraAtiva() {
  if (video.videoWidth) return true;
  avisar("A câmera ainda não está ativa.");
  return false;
}


// ---------- comunicação com o servidor ----------

// Envia o quadro atual do vídeo mais as opções da tela e devolve a resposta em JSON.
// "extras" traz os campos adicionais da requisição.
async function enviar(url, extras) {
  const dados = new FormData();
  dados.append("imagem", await pegarQuadro(), "quadro.jpg");
  dados.append("fundo_claro", $("fundoClaro").checked);
  dados.append("limiar", $("limiar").value);
  for (const [chave, valor] of Object.entries(extras)) {
    dados.append(chave, valor);
  }
  const resposta = await fetch(url, { method: "POST", body: dados });
  return resposta.json();
}


// ---------- desenho sobre o vídeo ----------

function limparDesenho() {
  ctx.clearRect(0, 0, camada.width, camada.height);
}

// desenha o formato real do furo, então uma peça amassada aparece amassada
function desenharContorno(pontos, cor) {
  limparDesenho();
  ctx.strokeStyle = cor;
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(pontos[0][0], pontos[0][1]);
  for (const [x, y] of pontos.slice(1)) {
    ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.stroke();
}


// ---------- peça padrão ----------

function mostrarPadrao() {
  const el = $("padrao");
  if (perimetroPadrao && razaoPadrao) {
    el.textContent = "Padrão: " + perimetroPadrao.toFixed(1) + " px de circunferência";
    el.classList.add("ok");
  } else {
    el.textContent = "Padrão: não definido";
    el.classList.remove("ok");
  }
}

async function definirPadrao() {
  avisar("");
  if (!cameraAtiva()) return;

  const r = await enviar("/api/medir", {});
  if (r.erro) {
    avisar(r.erro);
    limparDesenho();
    return;
  }
  perimetroPadrao = r.perimetro_px;
  razaoPadrao = r.razao_eixos;
  guardar("perimetroPadrao", perimetroPadrao);
  guardar("razaoPadrao", razaoPadrao);
  mostrarPadrao();
  desenharContorno(r.contorno, "#2563eb");

  // a medida anterior era comparada com o padrão antigo
  ultima = null;
  mostrarResultado();
}


// ---------- medição ----------

// passa se o percentual ficar dentro de 100% ± tolerância e a forma não ficar
// mais achatada que o padrão além da tolerância de forma
function veredito(medida) {
  const tol = parseFloat($("tolerancia").value);
  const tolForma = parseFloat($("toleranciaForma").value);
  return Math.abs(medida.percentual - 100) <= tol && medida.forma >= 100 - tolForma;
}

// sem medida (ultima === null) a caixa de resultado é limpa
function mostrarResultado() {
  const caixa = $("resultado");
  caixa.classList.remove("aprovada", "reprovada");

  if (!ultima) {
    $("valor").textContent = "--";
    $("veredito").textContent = "";
    $("detalhe").textContent = "";
    $("btnRegistrar").disabled = true;
    return;
  }

  const ok = veredito(ultima);
  $("valor").textContent = ultima.percentual.toFixed(1) + " %";
  $("veredito").textContent = ok ? "APROVADA" : "REPROVADA";
  caixa.classList.add(ok ? "aprovada" : "reprovada");

  $("detalhe").textContent = "Circunferência: " + ultima.perimetro_px.toFixed(1) +
    " px | Forma: " + ultima.forma.toFixed(1) + " % do padrão";
  $("btnRegistrar").disabled = false;
}

async function medir() {
  if (!perimetroPadrao || !razaoPadrao) {
    avisar("Defina a peça padrão antes de medir.");
    return false;
  }
  if (!cameraAtiva()) return false;

  const r = await enviar("/api/medir", { perimetro_padrao_px: perimetroPadrao, razao_padrao: razaoPadrao });
  if (r.erro) {
    avisar(r.erro);
    ultima = null;
    limparDesenho();
    mostrarResultado();
    return false;
  }

  avisar("");
  ultima = r;
  desenharContorno(r.contorno, veredito(r) ? "#2e9e5b" : "#d92d20");
  mostrarResultado();
  return true;
}

// ---------- modo automático (peça parada) ----------

let quadroAnterior = null;   // versão reduzida do quadro anterior, para detectar movimento
let paradoDesde = null;      // quando a cena parou de se mexer
let armado = true;           // pronto para medir assim que a cena ficar parada

// Devolve a fração de pixels que mudaram desde a checagem anterior (ou null na primeira).
// Contar pixels que mudaram bastante ignora o ruído da webcam e variações pequenas de luz.
function movimentoDaCena() {
  if (!video.videoWidth) return null;
  ctxAmostra.drawImage(video, 0, 0, amostra.width, amostra.height);
  const rgba = ctxAmostra.getImageData(0, 0, amostra.width, amostra.height).data;

  const cinza = new Uint8Array(amostra.width * amostra.height);
  for (let i = 0, j = 0; i < rgba.length; i += 4, j++) {
    cinza[j] = (rgba[i] + rgba[i + 1] + rgba[i + 2]) / 3;
  }

  let movimento = null;
  if (quadroAnterior) {
    let mudaram = 0;
    for (let j = 0; j < cinza.length; j++) {
      if (Math.abs(cinza[j] - quadroAnterior[j]) > MUDANCA_DE_PIXEL) mudaram++;
    }
    movimento = mudaram / cinza.length;
  }
  quadroAnterior = cinza;
  return movimento;
}

function statusAutomatico(texto) {
  $("statusAuto").textContent = texto;
}

// Espera a cena ficar parada pelo tempo escolhido, mede uma vez e só mede de novo
// depois que algo se mexer (a peça ser trocada).
async function passoAutomatico(id) {
  if (id !== ciclo) return;

  const movimento = movimentoDaCena();
  const espera = parseFloat($("espera").value) || 2;

  if (movimento === null) {
    statusAutomatico("Aguardando a câmera...");
  } else if (movimento > LIMITE_MOVIMENTO) {
    paradoDesde = null;
    armado = true;
    statusAutomatico("Movimento detectado, aguardando a peça parar...");
  } else {
    if (paradoDesde === null) paradoDesde = Date.now();
    const parado = (Date.now() - paradoDesde) / 1000;

    if (!armado) {
      // já mediu esta posição; só volta a medir depois que algo se mexer
    } else if (parado >= espera) {
      armado = false;
      statusAutomatico("Medindo...");
      try {
        const ok = await medir();
        statusAutomatico(ok
          ? "Medida feita. Troque a peça para medir de novo."
          : "Não consegui medir. Mova a peça para tentar de novo.");
      } catch (e) {
        statusAutomatico("Erro ao falar com o servidor.");
      }
    } else {
      statusAutomatico("Peça parada há " + parado.toFixed(1) + " s (mede com " + espera + " s)");
    }
  }

  setTimeout(() => passoAutomatico(id), PASSO_AUTOMATICO);
}

// ao mudar o modo, o laço antigo é invalidado e, se for o automático, um novo começa
function trocarModo(modo) {
  ciclo++;
  quadroAnterior = null;
  paradoDesde = null;
  armado = true;
  statusAutomatico("");

  if (modo === "automatico") {
    statusAutomatico("Aguardando a peça parar...");
    passoAutomatico(ciclo);
  }
}


// ---------- histórico ----------

function desenharHistorico() {
  const corpo = $("linhas");
  corpo.innerHTML = "";

  // mais recente primeiro
  for (const reg of [...historico].reverse()) {
    const tr = document.createElement("tr");
    const classe = reg.aprovada ? "aprovada" : "reprovada";
    tr.innerHTML =
      "<td>" + reg.hora + "</td>" +
      "<td>" + reg.perimetro.toFixed(1) + "</td>" +
      "<td>" + reg.percentual.toFixed(1) + " %</td>" +
      "<td>" + (reg.forma ? reg.forma.toFixed(1) + " %" : "-") + "</td>" +
      "<td>" + reg.tolerancia + "</td>" +
      '<td class="' + classe + '">' + (reg.aprovada ? "Aprovada" : "Reprovada") + "</td>";
    corpo.appendChild(tr);
  }

  const total = historico.length;
  const boas = historico.filter((r) => r.aprovada).length;
  $("resumo").textContent = total ? boas + " de " + total + " aprovadas" : "";
}

function registrar() {
  if (!ultima) return;
  historico.push({
    hora: new Date().toLocaleTimeString("pt-BR"),
    perimetro: ultima.perimetro_px,
    percentual: ultima.percentual,
    forma: ultima.forma,
    tolerancia: parseFloat($("tolerancia").value),
    aprovada: veredito(ultima),
  });
  guardar("historico", historico);
  desenharHistorico();
}

function baixarCsv() {
  if (!historico.length) return;
  // ponto e vírgula e vírgula decimal para o Excel em português abrir corretamente
  const num = (n, casas) => n.toFixed(casas).replace(".", ",");
  const linhas = ["hora;circunferencia_px;percentual_do_padrao;forma_pct;tolerancia_pct;resultado"];
  for (const r of historico) {
    linhas.push([r.hora, num(r.perimetro, 1), num(r.percentual, 2), (r.forma ? num(r.forma, 1) : ""),
      num(r.tolerancia, 1), r.aprovada ? "APROVADA" : "REPROVADA"].join(";"));
  }
  // o ﻿ no início (BOM) faz o Excel reconhecer os acentos
  const arquivo = new Blob(["﻿" + linhas.join("\n")], { type: "text/csv;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(arquivo);
  link.download = "historico.csv";
  link.click();
  URL.revokeObjectURL(link.href);
}

function limparHistorico() {
  historico = [];
  guardar("historico", historico);
  desenharHistorico();
}


// ---------- eventos e inicialização ----------

function textoLimiar() {
  const v = $("limiar").value;
  $("valorLimiar").textContent = v === "0" ? "automático" : v;
}

function falhaDeRede() {
  avisar("Erro ao falar com o servidor.");
}

$("btnPadrao").addEventListener("click", () => definirPadrao().catch(falhaDeRede));
$("btnMedir").addEventListener("click", () => medir().catch(falhaDeRede));
$("btnRegistrar").addEventListener("click", registrar);
$("btnCsv").addEventListener("click", baixarCsv);
$("btnLimpar").addEventListener("click", limparHistorico);
$("limiar").addEventListener("input", textoLimiar);
$("modo").addEventListener("change", (e) => trocarModo(e.target.value));

// ao mudar a tolerância, reavalia a última medida sem medir de novo
$("tolerancia").addEventListener("input", mostrarResultado);
$("toleranciaForma").addEventListener("input", mostrarResultado);

perimetroPadrao = recuperar("perimetroPadrao");
razaoPadrao = recuperar("razaoPadrao");
historico = recuperar("historico") || [];
mostrarPadrao();
mostrarResultado();
desenharHistorico();
textoLimiar();
iniciarCamera();
