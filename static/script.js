// Lógica do front-end: liga a webcam, captura quadros, envia ao servidor Flask
// e mostra o resultado. Também cuida do histórico e da exportação em CSV.

const $ = (id) => document.getElementById(id);

const video = $("video");
const camada = $("camada");
const ctx = camada.getContext("2d");
// canvas fora da página, usado só para capturar os quadros do vídeo
const quadro = document.createElement("canvas");

let pxPorMm = null;       // escala da calibração (pixels por milímetro)
let ultimaMedida = null;  // último diâmetro medido, em mm
let historico = [];
let aoVivo = false;


// ---------- armazenamento local ----------

// a escala e o histórico ficam no navegador para sobreviver a um recarregamento
function guardar(chave, valor) {
  try {
    localStorage.setItem(chave, JSON.stringify(valor));
  } catch (e) {
    // sem localStorage (aba anônima, por exemplo) o sistema segue sem salvar
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

// o canvas do círculo precisa ter o mesmo tamanho do vídeo
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


// ---------- comunicação com o servidor ----------

// envia o quadro atual mais as opções da tela; "extras" traz os campos de cada rota
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

function desenharCirculo(c, cor) {
  ctx.clearRect(0, 0, camada.width, camada.height);
  if (!c) return;
  ctx.strokeStyle = cor;
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.arc(c.x, c.y, c.raio, 0, Math.PI * 2);
  ctx.stroke();
}


// ---------- calibração ----------

function mostrarEscala() {
  const el = $("escala");
  if (pxPorMm) {
    el.textContent = "Escala: " + pxPorMm.toFixed(3) + " px/mm";
    el.classList.add("ok");
  } else {
    el.textContent = "Escala: não calibrada";
    el.classList.remove("ok");
  }
}

async function calibrar() {
  avisar("");
  if (!video.videoWidth) {
    avisar("A câmera ainda não está ativa.");
    return;
  }
  const r = await enviar("/api/calibrar", { diametro_moeda: $("diametroMoeda").value });
  // quando algo dá errado o servidor responde { erro: "..." }
  if (r.erro) {
    avisar(r.erro);
    desenharCirculo(null);
    return;
  }
  pxPorMm = r.px_por_mm;
  guardar("pxPorMm", pxPorMm);
  mostrarEscala();
  desenharCirculo(r.circulo, "#2e9e5b");
}


// ---------- medição ----------

function veredito(medido) {
  const nominal = parseFloat($("nominal").value);
  const tol = parseFloat($("tolerancia").value);
  return Math.abs(medido - nominal) <= tol;
}

// medido === null limpa a caixa de resultado
function mostrarResultado(medido) {
  const caixa = $("resultado");
  caixa.classList.remove("aprovada", "reprovada");

  if (medido === null) {
    $("valor").textContent = "--";
    $("veredito").textContent = "";
    $("btnRegistrar").disabled = true;
    return;
  }

  const ok = veredito(medido);
  $("valor").textContent = medido.toFixed(2) + " mm";
  $("veredito").textContent = ok ? "APROVADA" : "REPROVADA";
  caixa.classList.add(ok ? "aprovada" : "reprovada");
  $("btnRegistrar").disabled = false;
}

async function medir() {
  if (!pxPorMm) {
    avisar("Calibre antes de medir.");
    return false;
  }
  if (!video.videoWidth) {
    avisar("A câmera ainda não está ativa.");
    return false;
  }

  const r = await enviar("/api/medir", { px_por_mm: pxPorMm });
  if (r.erro) {
    avisar(r.erro);
    ultimaMedida = null;
    desenharCirculo(null);
    mostrarResultado(null);
    return false;
  }

  avisar("");
  ultimaMedida = r.diametro_mm;
  desenharCirculo(r.circulo, veredito(r.diametro_mm) ? "#2e9e5b" : "#d92d20");
  mostrarResultado(r.diametro_mm);
  return true;
}

// Modo ao vivo: mede, espera e repete. Usa setTimeout em vez de setInterval
// para nunca haver duas requisições ao mesmo tempo.
async function repetirMedicao() {
  if (!aoVivo) return;
  try {
    await medir();
  } catch (e) {
    avisar("Perdi a conexão com o servidor.");
  }
  setTimeout(repetirMedicao, 400);
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
      "<td>" + reg.medido.toFixed(2) + "</td>" +
      "<td>" + reg.nominal + "</td>" +
      "<td>" + reg.tolerancia + "</td>" +
      '<td class="' + classe + '">' + (reg.aprovada ? "Aprovada" : "Reprovada") + "</td>";
    corpo.appendChild(tr);
  }

  const total = historico.length;
  const boas = historico.filter((r) => r.aprovada).length;
  $("resumo").textContent = total ? boas + " de " + total + " aprovadas" : "";
}

function registrar() {
  if (ultimaMedida === null) return;
  historico.push({
    hora: new Date().toLocaleTimeString("pt-BR"),
    medido: ultimaMedida,
    nominal: parseFloat($("nominal").value),
    tolerancia: parseFloat($("tolerancia").value),
    aprovada: veredito(ultimaMedida),
  });
  guardar("historico", historico);
  desenharHistorico();
}

function baixarCsv() {
  if (!historico.length) return;
  // ponto e vírgula e vírgula decimal para o Excel em português abrir corretamente
  const linhas = ["hora;medido_mm;nominal_mm;tolerancia_mm;resultado"];
  for (const r of historico) {
    const num = (n) => String(n).replace(".", ",");
    linhas.push([r.hora, num(r.medido.toFixed(3)), num(r.nominal), num(r.tolerancia),
      r.aprovada ? "APROVADA" : "REPROVADA"].join(";"));
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

$("btnCalibrar").addEventListener("click", calibrar);
$("btnMedir").addEventListener("click", () => medir().catch(() => avisar("Erro ao falar com o servidor.")));
$("btnRegistrar").addEventListener("click", registrar);
$("btnCsv").addEventListener("click", baixarCsv);
$("btnLimpar").addEventListener("click", limparHistorico);
$("limiar").addEventListener("input", textoLimiar);

$("aoVivo").addEventListener("change", (e) => {
  aoVivo = e.target.checked;
  if (aoVivo) repetirMedicao();
});

// ao mudar nominal ou tolerância, reavalia a última medida sem medir de novo
["nominal", "tolerancia"].forEach((id) => {
  $(id).addEventListener("input", () => {
    if (ultimaMedida !== null) mostrarResultado(ultimaMedida);
  });
});

pxPorMm = recuperar("pxPorMm");
historico = recuperar("historico") || [];
mostrarEscala();
desenharHistorico();
textoLimiar();
iniciarCamera();
