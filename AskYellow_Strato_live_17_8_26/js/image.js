console.log("🧩 image.js LOADED");

// =============================
// IMAGE ENGINE — YellowMind
// =============================

// 🔐 extern (wordt door chat.js gezet)
let isGuestFn = null;
let addBubbleFn = null;
let setYelloFn = null;

// 🧠 interne state
let pendingConfirmation = null;
let imageStore = [];
let isGeneratingImage = false;
let pendingExplanationPrompt = null;
let suppressImageIntentOnce = false;

// =============================
// INIT (wordt 1x aangeroepen)
// =============================
export function initImageEngine({ isGuest, addBubble, setYello }) {
  isGuestFn = isGuest;
  addBubbleFn = addBubble;
  setYelloFn = setYello;
}

// =============================
// INTENT DETECTIE (NU 1:1 GEDRAG)
// =============================
function isImageRequest(text) {
  return /(afbeelding|image|plaatje|foto|teken|tekenen|maak|maken|genereer|genereren|visualiseer|illustratie|draw|create)/i.test(
    text
  );
}

function detectImageIntent(text) {
  const t = text.toLowerCase();

  const hard = [
    "genereer een afbeelding",
    "maak een afbeelding",
    "genereer een plaatje",
    "maak een illustratie",
    "teken een",
  ];

  const soft = [
    "afbeelding",
    "plaatje",
    "illustratie",
    "visualiseren",
  ];

  if (hard.some(p => t.includes(p))) return "hard";
  if (soft.some(p => t.includes(p))) return "soft";

  return "none";
}

// =============================
// IMAGE FLOW confermatie
// =============================

export function handleConfirmation(text) {
  if (!pendingConfirmation) return false;

  const t = text.toLowerCase();

  if (t.includes("ja") || t.includes("doe maar") || t.includes("genereer")) {
    const prompt = pendingConfirmation;
    pendingConfirmation = null;

    return {
      handled: false,
      wantsImage: true,
      overridePrompt: prompt
    };
  }

if (t.includes("nee") || t.includes("uitleg")) {
  addBubbleFn("Prima! Dan leg ik het eerst uit 😊", "ai");

  const prompt = pendingExplanationPrompt;

  // reset confirmation state
  pendingConfirmation = null;
  pendingExplanationPrompt = null;

  // 🔑 BELANGRIJK: volgende message mag GEEN image-intent triggeren
  suppressImageIntentOnce = true;

  return {
    handled: false,
    wantsImage: false,
    overridePrompt: prompt
  };
}

}

// =============================
// IMAGE FLOW (entry point)
// =============================
export function handleImageFlow(text, meta = {}) {
    console.log("image flow", text, meta);

    // 🛑 image-intent alleen bij user input
    if (meta.source !== "user") {
        return { handled: false, wantsImage: false };
    }

    const intent = detectImageIntent(text);

    if (intent === "none") {
        return { handled: false, wantsImage: false };
    }

    // 🚫 gast → blokkeren
    if (isGuestFn && isGuestFn()) {
        addBubbleFn(
            "🖼️ Afbeeldingen maken kan alleen met een account 😊",
            "ai"
        );
        return { handled: true, wantsImage: false };
    }

    if (intent === "soft") {
        pendingConfirmation = text;
        pendingExplanationPrompt = text;

        addBubbleFn(
            "Ik kan hier een afbeelding van maken, maar ik ben dit nog aan het leren 😊\n\n" +
            "Wil je dat ik **nu een afbeelding genereer**, of zal ik het eerst uitleggen?",
            "ai"
        );

        return { handled: true, wantsImage: false };
    }

    if (intent === "hard") {
        return { handled: false, wantsImage: true };
    }

    return { handled: false, wantsImage: false };
}



// =============================
// API RESPONSE HANDLER
// =============================
export function handleApiResponse(data) {
  if (
    (data.tool === "image_generate" && data.url) ||
    (data.type === "image" && data.url)
  ) {
    addBubbleFn(
      `<img src="${data.url}" class="chat-image" />`,
      "ai",
      true
    );

    imageStore.push({
      url: data.url,
      created_at: Date.now()
    });

    setYelloFn?.("idle");
    return true;
  }

  return false;
}

// =============================
// HISTORY HANDLER
// =============================
export function handleHistoryMessage(msg) {
  const text = msg.content || "";

  if (
    msg.role === "assistant" &&
    typeof text === "string" &&
    text.startsWith("[IMAGE]")
  ) {
    const dataUrl = text.replace("[IMAGE]", "").trim();

    imageStore.push({
      url: dataUrl,
      created_at: msg.created_at
    });

    addBubbleFn(
      `<img src="${dataUrl}" class="chat-image" />`,
      "ai",
      true
    );

    return true;
  }

  return false;
}

// =============================
// IMAGE VIEW (sidebar)
// =============================
export function showImagesView() {
  const chat = document.getElementById("chatMessages");
  chat.innerHTML = "";

  const block = document.createElement("div");
  block.className = "images-view";

  block.innerHTML = `
    <div class="images-header">🖼️ Afbeeldingen</div>
    <div class="images-grid"></div>
  `;

  const grid = block.querySelector(".images-grid");

  if (imageStore.length === 0) {
    grid.innerHTML = `<div class="images-empty">Nog geen afbeeldingen</div>`;
  } else {
    imageStore.forEach(img => {
      const el = document.createElement("img");
      el.src = img.url;
      el.className = "image-thumb";
      el.onclick = () => window.open(img.url, "_blank");
      grid.appendChild(el);
    });
  }

  chat.appendChild(block);
}

// =============================
// RESET (bij history reload)
// =============================
export function resetImages() {
  imageStore.length = 0;
}
