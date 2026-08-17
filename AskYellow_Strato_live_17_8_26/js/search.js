const API_BASE = "https://askyellow-ai.onrender.com";
console.log("API Base selected:", API_BASE);
console.log("Affiliate API_BASE =", API_BASE);

// ============================
// SEARCH STATE (frontend)
// ============================

let searchActive = false;
let searchSteps = [];
const MAX_SEARCH_STEPS = 5;
let leadQuerySent = false;


// ============================
// ELEMENTEN
// ============================

const searchInput = document.getElementById("searchInput");
const answerBox   = document.getElementById("answerBox");
const answerText  = document.getElementById("answerText");
const webBlock    = document.getElementById("webResults");
const webList     = document.getElementById("webList");
const shopSection = document.getElementById("shopResults");
const resultList  = document.getElementById("resultList");
const kbSection   = document.getElementById("kbResults");
const kbBox       = document.getElementById("kbBox");
const affiliateSection = document.getElementById("affiliate-section");
const affiliateList = document.getElementById("affiliate-section");
// const newSearchButton = document.getElementById("searchCloseBtn");


// ============================
// HELPER
// ============================


document.addEventListener("DOMContentLoaded", () => {

  const btn = document.getElementById("showAffiliateOptions");
  if (!btn) return;

  btn.addEventListener("click", async () => {
    const sessionId = getSessionId();
    const combinedQuery = getCombinedSearchQuery();

    if (!combinedQuery) return;

    const data = await fetchAffiliateOptions(sessionId, {
      query: combinedQuery
    });

    renderAffiliateOptions(data.models);
  });

});
document.addEventListener("click", (e) => {
  if (e.target.matches("#searchCloseBtn")) { // pas id aan
    resetFlow();
    clearSearchUI?.();
  }
});

// =============================
// 🔘 ACTION BUTTONS
// =============================
  btnNewSearch.addEventListener("click", () => {
    // 🔥 nieuwe flow
    resetFlow();

    // UI reset
    actions.style.display = "none";
    clearSearchUI?.(); // als je deze functie al hebt
    const input = document.querySelector("#searchInput"); // pas id aan
    if (input) {
      input.value = "";
      input.focus();
      input.placeholder = "Nieuwe zoekopdracht…";
    }
  });

function showSearchActions() {
  const actions = document.getElementById("searchActions");
  if (!actions) return;
  actions.style.display = "flex";
}

function hideSearchActions() {
  const actions = document.getElementById("searchActions");
  if (!actions) return;
  actions.style.display = "none";
}

// Zorg dat dit bestaat (je riep clearSearchUI?.() aan)
function clearSearchUI() {
  answerText.innerHTML = "";
  answerBox.style.display = "none";

  webBlock.style.display = "none";
  webList.innerHTML = "";

  shopSection.style.display = "none";
  resultList.innerHTML = "";

  kbSection.style.display = "none";
  kbBox.innerHTML = "";

  hideSearchActions();
}
document.addEventListener("click", (e) => {
  if (e.target && e.target.id === "btnRefine") {
    hideSearchActions();
    const input = document.querySelector("#searchInput"); // pas aan
    if (input) {
      input.focus();
      input.placeholder = "Oké, waar wil je op verfijnen?";
    }
  }

  if (e.target && e.target.id === "btnNewSearch") {
    resetFlow();             // jouw flow reset
    hideSearchActions();
    if (typeof clearSearchUI === "function") clearSearchUI();
    const input = document.querySelector("#searchInput"); // pas aan
    if (input) {
      input.value = "";
      input.focus();
      input.placeholder = "Nieuwe zoekopdracht…";
    }
  }
});


function getOrCreateFlowId() {
  let flowId = sessionStorage.getItem("search_flow_id");

  if (!flowId) {
    flowId = crypto.randomUUID();
    sessionStorage.setItem("search_flow_id", flowId);
    console.log("🆕 Nieuwe flow gestart:", flowId);
  }

  return flowId;
}

function resetFlow() {
  const newFlowId = crypto.randomUUID();
  sessionStorage.setItem("search_flow_id", newFlowId);
  console.log("🔄 Flow gereset:", newFlowId);
  return newFlowId;
}

function getQueryParam(name) {
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}

function getSessionId() {
  let sid = localStorage.getItem("ym_session_id");
  if (!sid) {
    sid = "web-" + Math.random().toString(16).slice(2);
    localStorage.setItem("ym_session_id", sid);
  }
  return sid;
}

function getCombinedSearchQuery() {
  return searchSteps.join(" ");
}

function resetSearchState() {
  searchActive = false;
  searchSteps = [];
  leadQuerySent = false; // 👈 belangrijk
}

async function sendLeadQuery(payload) {
  try {
    await fetch(`${API_BASE}/lead/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  } catch (err) {
    console.warn("Lead query logging failed", err);
  }
}

function isRelevantShopResult(product, query) {
  const q = query.toLowerCase();

  return (
    product.title?.toLowerCase().includes(q) ||
    product.handle?.toLowerCase().includes(q) ||
    product.tags?.some(tag => tag.toLowerCase().includes(q))
  );
}

async function fetchAffiliateOptions(sessionId, constraints) {
  try {
    const res = await fetch(`${API_BASE}/affiliate/models`, {

      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        session_id: sessionId,
        constraints: constraints
      })
    });

    return await res.json();

  } catch (err) {
    console.error("Affiliate fetch error:", err);
    return { models: [] };
  }
}


// ============================
// AUTORUN VANUIT index.html
// ============================

const initialQuery = getQueryParam("q");
if (initialQuery) {
  searchInput.value = initialQuery;
  runSearch();
}

// ============================
// affiliate links TEST onder staat de goede
// ============================

function renderAffiliateOptions(models) {
  const box = document.getElementById("affiliateBox");
  const container = document.getElementById("affiliate-section");

  if (!box || !container) {
    console.warn("Affiliate elements not found");
    return;
  }

  box.style.display = "block";        // 🔥 dit ontbrak
  container.style.display = "block";

  container.innerHTML = "";

  if (!models || models.length === 0) {
    container.innerHTML = "<p>Geen opties gevonden.</p>";
    return;
  }

  models.forEach(model => {
    const card = document.createElement("a");
    card.href = model.affiliate_url;
    card.target = "_blank";
    card.textContent = `${model.brand} ${model.model}`;
    container.appendChild(card);
  });
}



// ============================
// RUN SEARCH
// ============================

async function runSearch() {
  const q = searchInput.value.trim();
  if (!leadQuerySent && !searchActive && searchSteps.length === 0 && q) {
    leadQuerySent = true;

    sendLeadQuery({
      session_id: getSessionId(),
      lead_query: q
    });
  }

  if (!q) return;
  let combinedQuery = ""; // 🔑 EXACT ÉÉN DECLARATIE

  console.log("▶ runSearch input:", q);
  console.log("▶ BEFORE update:", searchActive, JSON.stringify(searchSteps));

  const normalizedQ = q.toLowerCase().trim();
  const lastStep = searchSteps[searchSteps.length - 1]?.toLowerCase().trim();

  if (lastStep === normalizedQ) {
    searchInput.value = "";
        return;
  }

  // ---- SEARCH FLOW (frontend) ----
  if (!searchActive) {
    searchActive = true;
    searchSteps = [q];
  } else {
    searchSteps.push(q);
  }

if (searchSteps.length === 1) {
  const box = document.getElementById("affiliateBox");
  const btn = document.getElementById("showAffiliateOptions");

  if (box) box.style.display = "block";
  if (btn) btn.style.display = "inline-block";
}


  // 🔑 HIER TOEKENNEN (NIET opnieuw declareren!)
  combinedQuery = searchSteps.join(" ");

  console.log("▶ AFTER update:", searchActive, JSON.stringify(searchSteps));
  console.log("▶ combinedQuery:", combinedQuery);

// 🔥 V2 TEST CALL
const v2Response = await fetch(`${API_BASE}/search_v2/analyze`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    session_id: getOrCreateFlowId(),  // 🔥 flow-based session
    query: q
  })
});

const v2Data = await v2Response.json();
console.log("V2 RESPONSE:", v2Data);
console.log("V2 action:", v2Data.action);
console.log("V2 question:", v2Data.question);
console.log("V2 query:", v2Data.query);
console.log("V2 confidence:", v2Data.confidence);


if (v2Data.action === "ask") {
  answerText.innerHTML = v2Data.question;
  searchInput.value = "";
  return;
}

if (v2Data.action === "advice") {
    answerText.innerHTML = v2Data.answer;
    webBlock.style.display = "none";
    shopSection.style.display = "none";
    return;
}


if (v2Data.action === "search") {
  // ✅ UI basis
  answerBox.style.display = "block";
  answerText.innerHTML = "Ik heb iets gevonden voor je 👇";
  hideSearchActions();          // eerst verbergen, daarna tonen zodra results klaar zijn

  // ✅ query die we gaan gebruiken
  const searchQuery = v2Data.query;

  // (optioneel) laat zien wat we gaan zoeken
  answerText.innerHTML = `Ik heb iets gevonden voor: <b>${searchQuery}</b> 👇`;

  try {
    // ---------------------------
    // 1) WEB SEARCH (1x)
    // ---------------------------
    webBlock.style.display = "block";
    webList.innerHTML = `<li>Momentje… 🔎</li>`;

    const webRes = await fetch(`${API_BASE}/web`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: searchQuery })
    });

    const webData = await webRes.json();

    webList.innerHTML = "";
    if (webData?.results?.length) {
      webData.results.slice(0, 5).forEach(r => {
        const li = document.createElement("li");
        li.innerHTML = `<a href="${r.url}" target="_blank" rel="noopener">${r.title}</a>`;
        webList.appendChild(li);
      });
    } else {
      webList.innerHTML = `<li>Geen webresultaten gevonden.</li>`;
    }

    // ---------------------------
    // 2) SHOPIFY SEARCH (1x)
    // ---------------------------
    shopSection.style.display = "block";
    resultList.innerHTML = `<li>Shop laden… 🛒</li>`;

    const shopRes = await fetch(`${API_BASE}/tool/shopify_search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: searchQuery })
    });

    const shopData = await shopRes.json();
    resultList.innerHTML = "";

    if (shopData?.results?.length) {
      shopData.results.slice(0, 6).forEach(p => {
        const li = document.createElement("li");
        li.innerHTML = `<b>${p.title}</b> — ${p.price || ""}`;
        resultList.appendChild(li);
      });
    } else {
      resultList.innerHTML = `<li>Geen producten gevonden in de shop.</li>`;
    }

    // ---------------------------
    // 3) AFFILIATE (optioneel, 1x)
    // ---------------------------
    // Alleen doen als je dit al gebruikt; anders weglaten.
    // Belangrijk: dit is een losse flow, maakt niet uit voor search_v2 session_id.
    if (typeof runAffiliateSearch === "function") {
      await runAffiliateSearch(searchQuery); // jouw bestaande functie
    }

    // ✅ Nu pas buttons tonen (want er zijn resultaten / output)
    showSearchActions();

    // input leegmaken voor vervolg
    searchInput.value = "";
    searchInput.focus();

    return;
  } catch (err) {
    console.error("❌ Search flow error:", err);
    answerText.innerHTML = "Oeps, er ging iets mis bij het ophalen van resultaten.";
    showSearchActions(); // gebruiker kan alsnog “Nieuwe zoekopdracht”
    return;
  }
}


    console.log("FULL RESPONSE:", data);

      // ✅ wél relevant → tonen
      shopSection.style.display = "block";
      resultList.innerHTML = "";

      relevantResults.slice(0, 5).forEach(p => {
        resultList.innerHTML += `
          <div class="result-item" onclick="window.open('${p.url}', '_blank')">
            ${p.image ? `<img class="result-thumb" src="${p.image}" />` : ""}
            <div class="result-info">
              <div class="result-title">${p.title}</div>
              <div class="price-line">
                ${p.price ? `<span class="price">€${p.price}</span>` : ""}
                ${p.compare_at ? `<span class="compare">€${p.compare_at}</span>` : ""}
              </div>
            </div>
          </div>
        `;
      });
    };
    

  // NA alles → input leeghalen
  searchInput.value = "";

// ENTER + KNOP WERKEN
searchInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    runSearch();
  }
});

document
  .getElementById("showAffiliateOptions")
  .addEventListener("click", async () => {
  const sessionId = getSessionId();
  const combinedQuery = getCombinedSearchQuery();

  if (!combinedQuery) return; // extra safety

  const data = await fetchAffiliateOptions(sessionId, {
    query: combinedQuery
  });

  renderAffiliateOptions(data.models);
});


// ============================
// FORMATTER
// ============================
function formatAI(txt) {
  if (!txt) return "";

  txt = txt.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  txt = txt.replace(/^### (.*)$/gim, "<h3>$1</h3>");
  txt = txt.replace(/^## (.*)$/gim, "<h3>$1</h3>");
  txt = txt.replace(/^# (.*)$/gim, "<h3>$1</h3>");

  txt = txt.replace(/^\d+\.\s+(.*)$/gim, "<li>$1</li>");
  if (txt.includes("<li>")) txt = "<ol>" + txt + "</ol>";

  txt = txt.replace(/^[-*]\s+(.*)$/gim, "<li>$1</li>");
  if (txt.includes("<li>") && !txt.includes("<ol>")) txt = "<ul>" + txt + "</ul>";

  txt = txt.replace(/\n/g, "<br>");

  return txt;
}

function openChatFromSearch() {
  const inIframe = (window.self !== window.top);

  // In iframe (search overlay op index.html) -> stuur bericht naar parent
  if (inIframe && window.parent && window.parent.postMessage) {
    console.log("Search: stuur openChat naar parent");
    window.parent.postMessage({ type: "openChat", from: "search" }, "*");
    return;
  }

  // Niet in iframe -> redirect naar index met autoChat
  console.log("Search: niet in iframe, redirect naar index.html?autoChat=1");
  const currentQuery =
    (typeof searchInput !== "undefined" && searchInput.value.trim()) ||
    getQueryParam("q") ||
    "";

  const baseIndex = path.startsWith("/dev/")
    ? "/dev/index.html"
    : "/index.html";

  const url =
    baseIndex +
    "?autoChat=1" +
    (currentQuery ? "&q=" + encodeURIComponent(currentQuery) : "");

  window.location.href = url;
}
window.runSearch = runSearch;
