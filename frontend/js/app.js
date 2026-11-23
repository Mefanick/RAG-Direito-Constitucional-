const atalhos = [
  ["Anonimato (Art. 5º, IV)", "A Constituição garante a liberdade de manifestação do pensamento e proíbe o anonimato?"],
  ["ADI das Mesas", "A Mesa da Câmara dos Deputados e a Mesa do Senado podem propor ADI?"],
  ["Usucapião rural", "Quais são os requisitos da usucapião especial rural (pro labore)?"],
  ["Monopólio de mineração", "O Estado pode intervir na economia para criar um monopólio de mineração?"],
  ["Furto qualificado", "Qual é a pena prevista no Código Penal para o crime de furto qualificado?"],
]

const conversa = document.querySelector("#conversa")
const campo = document.querySelector("#campo")
const offline = new URLSearchParams(location.search).has("offline")

document.querySelector("#atalhos").innerHTML = atalhos.map(([titulo, pergunta]) =>
  `<button type="button" data-pergunta="${pergunta}">${titulo}</button>`
).join("")

document.querySelector("#atalhos").addEventListener("click", (evento) => {
  const botao = evento.target.closest("button")
  if (botao) enviar(botao.dataset.pergunta)
})

document.querySelector("#formulario").addEventListener("submit", (evento) => {
  evento.preventDefault()
  enviar(campo.value)
})

campo.addEventListener("keydown", (evento) => {
  if (evento.key === "Enter" && !evento.shiftKey && !evento.isComposing) {
    evento.preventDefault()
    enviar(campo.value)
  }
})

document.querySelector("#limpar").addEventListener("click", async () => {
  await fetch("/api/cache/limpar", { method: "POST" })
  historico.length = 0
  conversa.innerHTML = ""
})

document.querySelector("#reverificar").addEventListener("click", () => {
  saude()
  carregarModelos()
})

document.querySelector("#modelo").addEventListener("change", atualizarThink)

const catalogoModelos = []

function atualizarThink() {
  const id = document.querySelector("#modelo").value
  const item = catalogoModelos.find((modelo) => modelo.id === id)
  const caixa = document.querySelector("#usar-think")
  if (!item || !item.suporta_think) {
    caixa.checked = false
    caixa.disabled = true
  } else {
    caixa.disabled = false
  }
}

async function carregarModelos() {
  const selecao = document.querySelector("#modelo")
  try {
    const resposta = await fetch("/api/modelos")
    const dados = await resposta.json()
    catalogoModelos.length = 0
    catalogoModelos.push(...(dados.modelos || []))
    selecao.innerHTML = catalogoModelos.map((modelo) => {
      const extra = modelo.instalado ? "" : " (não instalado)"
      const marcado = modelo.id === dados.modelo_ativo_atual || (modelo.padrao && !dados.modelo_ativo_atual) ? " selected" : ""
      const bloqueado = modelo.instalado ? "" : " disabled"
      return `<option value="${modelo.id}"${marcado}${bloqueado}>${modelo.label}${extra}</option>`
    }).join("")
  } catch (erro) {
    selecao.innerHTML = `<option value="qwen3:8b">Máxima Precisão (Qwen3 8B)</option>`
  }
  atualizarThink()
}

const historico = []

function selo(auditoria) {
  if (!auditoria || auditoria.status === "SEM_CITACAO") return ""
  if (auditoria.status === "ALUCINACAO_ARTIGO") {
    const lista = (auditoria.artigos_inventados || []).join(", ")
    return `<span class="badge erro">Artigo fora das fontes${lista ? `: ${escapar(lista)}` : ""}</span>`
  }
  if (auditoria.status === "ALERTA_SUBDISPOSITIVO") {
    const lista = (auditoria.subdispositivos_nao_confirmados || []).join(", ")
    return `<span class="badge aviso">Verificar inciso/parágrafo${lista ? `: ${escapar(lista)}` : ""}</span>`
  }
  if (auditoria.status === "FIEL") return `<span class="badge ok">Citações fiéis (artigo + inciso)</span>`
  return ""
}

function badgeModo(modo) {
  if (modo === "MODO_LLM_PURO") return `<span class="badge neutro">LLM puro</span>`
  if (modo === "MODO_RAG_ALTA_CONFIANCA") return `<span class="badge ok">Base Constitucional</span>`
  if (modo === "MODO_RAG_ZONA_CINZENTA") return `<span class="badge aviso">Contexto Parcial</span>`
  if (modo === "MODO_ATALHO_SOCIAL") return `<span class="badge neutro">Atalho</span>`
  return `<span class="badge neutro">Conversa Livre</span>`
}

function selosVisiveis(pacote) {
  const modo = pacote.modo_rag || pacote.modo_resposta
  const auditoria = pacote.auditoria
    ? selo(pacote.auditoria) || `<span class="badge neutro">Sem citação nova</span>`
    : `<span class="badge neutro">Sem auditoria</span>`
  const prefill = pacote.prefill_s == null ? "" : `<span class="badge neutro">Prefill ${segundos(pacote.prefill_s)}</span>`
  const decode = pacote.eval_s == null ? "" : `<span class="badge neutro">Decode ${segundos(pacote.eval_s)}</span>`
  const tok = pacote.tok_s == null ? "" : `<span class="badge neutro">${Number(pacote.tok_s).toFixed(1)} tok/s</span>`
  return `<p class="selos"><span class="badge neutro">${escapar(pacote.modelo || "modelo")}</span>${badgeModo(modo)}${auditoria}${prefill}${decode}${tok}</p>`
}

function fontes(artigos) {
  if (!artigos || !artigos.length) return "<p>Nenhum artigo acima do corte.</p>"
  const vistos = new Set()
  const unicos = []
  for (const artigo of artigos) {
    const chave = String(artigo.artigo_id || "").replace(/\s+/g, " ").toLowerCase()
    if (vistos.has(chave)) continue
    vistos.add(chave)
    unicos.push(artigo)
  }
  return unicos.map((artigo, indice) => {
    const irmao = artigo.origem === "irmao_adjacente" ? `<span class="badge aviso">Irmão Adjacente</span>` : ""
    const pai = artigo.origem === "parent_document" ? `<span class="badge ok">Parent-Document (${artigo.filhos || 0} filhos)</span>` : ""
    const nota = Number(artigo.score_reranker || 0)
    const largura = Math.max(0, Math.min(100, nota * 100))
    return `<article class="fonte" id="fonte-${indice}">
      <header><strong>${escapar(artigo.artigo_id)}</strong> ${pai}${irmao}</header>
      <div class="barra"><i style="width:${largura}%"></i></div>
      <small>${nota.toFixed(3)}</small>
      <pre>${artigo.texto}</pre>
    </article>`
  }).join("")
}

function telemetria(pacote) {
  const tempos = pacote.tempos_s || {}
  const linhas = [
    ["Roteador", segundos(tempos.roteador)],
    ["Retriever", segundos(tempos.retriever)],
    ["Prefill", pacote.prefill_s == null ? "n/d" : segundos(pacote.prefill_s)],
    ["Tokens entrada", pacote.tokens_prompt == null ? "n/d" : pacote.tokens_prompt],
    ["TTFT", pacote.ttft_s == null ? "n/d" : segundos(pacote.ttft_s)],
    ["Gerador", segundos(tempos.gerador)],
    ["Total", segundos(tempos.total)],
    ["Raciocínio profundo", pacote.usar_think ? "ligado" : "desligado"],
    ["Pensamento", pacote.think_s == null && pacote.tempo_thinking_s == null ? "n/d" : segundos(pacote.think_s ?? pacote.tempo_thinking_s)],
    ["Decode", pacote.eval_s == null ? "n/d" : segundos(pacote.eval_s)],
    ["tok/s", pacote.tok_s == null ? "n/d" : Number(pacote.tok_s).toFixed(1)],
  ]
  return `<ul class="log-box">${linhas.map(([nome, valor]) => `<li><span class="log-passo">${nome}</span><span>${valor}</span></li>`).join("")}</ul>`
}

function escapar(valor) {
  return String(valor || "").replace(/[&<>"]/g, (caractere) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[caractere]))
}

function descartados(lista) {
  const fora = (lista || []).filter((item) => item.status && item.status !== "APROVADO")
  if (!fora.length) return ""
  return `<ul class="log-box">${fora.map((item) => `<li><span class="log-passo">${escapar(item.status)}</span><span>${escapar(item.artigo_id)} · reranker ${Number(item.score_reranker || 0).toFixed(3)} · cosseno ${Number(item.score_cosseno || 0).toFixed(3)}</span></li>`).join("")}</ul>`
}

function subconsultas(lista) {
  if (!lista || !lista.length) return ""
  return `<p>Sub-consultas</p><ul class="log-box">${lista.map((item) => `<li><span>${escapar(item)}</span></li>`).join("")}</ul>`
}

function segundos(valor) {
  return `${Number(valor || 0).toFixed(2)} s`
}

function separar(texto) {
  const marca = "\nResposta:"
  const indice = texto.indexOf("Resposta:")
  if (indice < 0) return { base: "", corpo: texto }
  return {
    base: texto.slice(0, indice).replace("Base Constitucional:", "").trim(),
    corpo: texto.slice(indice + "Resposta:".length).trim(),
  }
}

function chips(base) {
  const achados = base.match(/Art\.\s*\d+[ºo°]?(?:-[A-Za-z])?(?:\s*,\s*(?:§\s*\d+[ºo°]?|[IVXLCDM]+))?/gi) || []
  const vistos = new Set()
  const unicos = []
  for (const item of achados) {
    const chave = item.replace(/\s+/g, " ").toLowerCase()
    if (vistos.has(chave)) continue
    vistos.add(chave)
    unicos.push(item)
  }
  return unicos.map((item) => `<button type="button" class="chip">${item}</button>`).join("")
}

function desenharFim(caixa, pacote) {
  const texto = pacote.resposta || ""
  const cache = pacote.cache ? `<span class="badge aviso">Cache</span>` : ""
  const aviso = pacote.erro
    ? `<div class="aviso-caixa"><strong>Ollama fora do ar.</strong><p>Suba o servidor com <code>${pacote.comando || "ollama serve"}</code>.</p><p>${pacote.erro}</p></div>`
    : ""
  const rota = pacote.roteamento || {}
  const traduzida = pacote.consulta_traduzida
    ? `<p>Consulta reestruturada: ${escapar(pacote.consulta_traduzida)}</p>`
    : ""
  caixa.querySelector(".corpo").innerHTML = `
    ${cache}
    ${selosVisiveis(pacote)}
    ${aviso}
    <div class="chips">${chips(texto)}</div>
    <p>${texto}</p>
    ${selo(pacote.auditoria)}
    <details>
      <summary>Fontes e auditoria</summary>
      <ul class="log-box">
        <li><span class="log-passo">Intenção</span><span>${rota.intencao || "n/d"}</span></li>
        <li><span class="log-passo">Prob.</span><span>${rota.prob_top1 == null ? "n/d" : Number(rota.prob_top1).toFixed(3)}</span></li>
        <li><span class="log-passo">Margem</span><span>${rota.margem == null ? "n/d" : Number(rota.margem).toFixed(3)}</span></li>
        <li><span class="log-passo">Modo</span><span>${pacote.modo_busca || "n/d"}</span></li>
        <li><span class="log-passo">Resposta</span><span>${pacote.modo_resposta || "n/d"}</span></li>
        <li><span class="log-passo">Consulta</span><span>${pacote.classe_consulta || "n/d"}</span></li>
      </ul>
      ${subconsultas(pacote.subconsultas)}
      ${traduzida}
      ${descartados(pacote.top_candidatos_brutos)}
      ${fontes(pacote.artigos)}
      ${pacote.raciocinio ? `<details><summary>Raciocínio interno do modelo</summary><pre>${escapar(pacote.raciocinio)}</pre></details>` : ""}
      ${telemetria(pacote)}
    </details>`
}

async function enviar(texto) {
  const pergunta = (texto || "").trim()
  if (!pergunta) return
  campo.value = ""
  const usuario = document.createElement("article")
  usuario.className = "bolha usuario"
  usuario.innerHTML = `<p class="pergunta">${pergunta}</p>`
  const caixa = document.createElement("article")
  caixa.className = "bolha"
  caixa.dataset.pergunta = pergunta
  const puro = document.querySelector("#modo-resposta").value === "puro"
  caixa.innerHTML = `<p class="etapa">${puro ? "Consultando o modelo..." : "Classificando intenção..."}</p><div class="corpo"></div>`
  conversa.append(usuario, caixa)
  const resposta = await fetch("/api/perguntar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      pergunta,
      historico: [],
      usar_cache: document.querySelector("#cache").checked,
      simular_offline: offline,
      usar_think: document.querySelector("#usar-think").checked,
      usar_rag: document.querySelector("#modo-resposta").value !== "puro",
      modelo: document.querySelector("#modelo").value || null,
    }),
  })
  const leitor = resposta.body.getReader()
  const decodificador = new TextDecoder()
  let resto = ""
  let visivel = ""
  while (true) {
    const pedaco = await leitor.read()
    if (pedaco.done) break
    resto += decodificador.decode(pedaco.value, { stream: true })
    const blocos = resto.split("\n\n")
    resto = blocos.pop()
    for (const bloco of blocos) tratar(bloco, caixa, (token) => { visivel += token })
  }
}

function tratar(bloco, caixa, acumular) {
  const nome = (/event: (.+)/.exec(bloco) || [])[1]
  const bruto = (/data: (.+)/.exec(bloco) || [])[1]
  if (!nome || !bruto) return
  const dados = JSON.parse(bruto)
  if (nome === "etapa") caixa.querySelector(".etapa").textContent = dados.rotulo
  if (nome === "token") {
    acumular(dados.texto)
    caixa.querySelector(".corpo").textContent = caixa.dataset.texto = (caixa.dataset.texto || "") + dados.texto
  }
  if (nome === "cache" || nome === "fim") {
    caixa.querySelector(".etapa").textContent = dados.cache ? "Cache" : "Concluído"
    desenharFim(caixa, dados)
  }
  if (nome === "erro") {
    caixa.querySelector(".etapa").textContent = "Aviso"
    caixa.querySelector(".corpo").innerHTML = `<div class="aviso-caixa"><strong>Ollama fora do ar.</strong><p>Suba o servidor com <code>${dados.comando || "ollama serve"}</code>.</p><p>${dados.mensagem}</p></div>${fontes(dados.artigos)}`
  }
}

async function saude() {
  const resposta = await fetch("/api/saude")
  const dados = await resposta.json()
  const ponto = document.querySelector("#ponto")
  ponto.className = `ponto ${dados.online ? "online" : "offline"}`
  document.querySelector("#estado").textContent = dados.online ? `Online · ${dados.modelo}` : "Offline"
  document.querySelector("#motor").textContent = dados.motor
}

saude()
carregarModelos()
