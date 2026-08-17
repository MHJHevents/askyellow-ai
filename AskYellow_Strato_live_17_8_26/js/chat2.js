

document.addEventListener("DOMContentLoaded", () => {
  console.log("CHAT JS LIVE BUILD 2026-03-28 15:55");
const API_BASE = "https://askyellow-ai.onrender.com";
const BASE_PATH = "";
console.log("API_BASE =", API_BASE);
console.log("BASE_PATH =", BASE_PATH);
  const messagesDiv = document.getElementById("chatMessages");
  const chatInput = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendChat");
  const closeBtn = document.getElementById("btn-close");
  const yello = document.getElementById("yelloAvatar");
  const historyBtn = document.getElementById("history-toggle");
  const historySub = document.getElementById("historySub");
  const menuToggle = document.getElementById("menuToggle");
  const appShell = document.getElementById("app-shell");
  const sidebarClose = document.getElementById("sidebarClose");

  const chatImageInput = document.getElementById("chatImageInput");
  const uploadPreview = document.getElementById("uploadPreview");
  const uploadPreviewImg = document.getElementById("uploadPreviewImg");
  const uploadPreviewText = document.getElementById("uploadPreviewText");
  const removeUploadBtn = document.getElementById("removeUploadBtn");

  const imageStore = [];
  let selectedImageFile = null;
  let historyLoadingBubble = null;
  let lastUploadedImageFile = null;
  let imageModal = null;

  const SESSION_KEY = "ay_session_id";
  const chatShell = document.getElementById("chat-shell");
  let dragDepth = 0;

  // =========================
  // SIDEBAR CONTROL
  // =========================
function closeSidebar() {
  appShell.classList.remove("sidebar-open");
}

menuToggle?.addEventListener("click", () => {
  appShell.classList.toggle("sidebar-open");
});

sidebarClose?.addEventListener("click", closeSidebar);



document.querySelectorAll(
  '.sidebar-sub-btn, .sidebar-btn[data-action="images"], .sidebar-btn[data-action="logout"]'
).forEach((btn) => {
  btn.addEventListener("click", closeSidebar);
});

["dragenter", "dragover"].forEach((eventName) => {
  window.addEventListener(eventName, (e) => {
    e.preventDefault();
    e.stopPropagation();
  });
});

["dragleave", "drop"].forEach((eventName) => {
  window.addEventListener(eventName, (e) => {
    e.preventDefault();
    e.stopPropagation();
  });
});

chatShell?.addEventListener("dragenter", (e) => {
  e.preventDefault();
  e.stopPropagation();
  dragDepth++;
  setDropzoneActive(true);
});

chatShell?.addEventListener("dragover", (e) => {
  e.preventDefault();
  e.stopPropagation();
  setDropzoneActive(true);
});

chatShell?.addEventListener("dragleave", (e) => {
  e.preventDefault();
  e.stopPropagation();

  dragDepth--;
  if (dragDepth <= 0) {
    dragDepth = 0;
    setDropzoneActive(false);
  }
});

chatShell?.addEventListener("drop", (e) => {
  e.preventDefault();
  e.stopPropagation();

  dragDepth = 0;
  setDropzoneActive(false);

  const files = e.dataTransfer?.files;
  if (!files || !files.length) return;

  handleDroppedFile(files[0]);
});

  function getSessionId() {
    let sid = localStorage.getItem(SESSION_KEY);
    if (!sid) {
      sid = crypto.randomUUID();
      localStorage.setItem(SESSION_KEY, sid);
    }
    return sid;
  }

  let CURRENT_SESSION = getSessionId();

  function isGuest() {
    return localStorage.getItem("authSession")?.startsWith("guest_");
  }

  function nowTime() {
    return new Date().toLocaleTimeString("nl-NL", {
      hour: "2-digit",
      minute: "2-digit"
    });
  }

  // avatars en realtime interractie

  const AVATAR_MEDIA = {
  yello: {
    idle: "/img/yello_lopend_trans.mp4",
    typing: "/img/yello_typen_trans.mp4",
    thinking: "/img/yello_denkend_trans.mp4",
    image: "/img/yello_image_trans.mp4"
  }
};

  let currentAvatar = "yello";
  let currentState = null;


  function setYello(state) {
  if (!AVATAR_MEDIA[currentAvatar]) return;

  // voorkom onnodige reloads
  if (state === currentState) return;

  const src = AVATAR_MEDIA[currentAvatar][state] 
           || AVATAR_MEDIA[currentAvatar].idle;

  if (yello && !yello.src.includes(src)) {
    yello.src = src;
    yello.load();
    yello.play().catch(() => {});
  }

  currentState = state;
}

function setIdleWithDelay(delay = 1000) {
  setTimeout(() => {
    setYello("idle");
  }, delay);
}

function isUserImageMarker(content) {
  return typeof content === "string" && content.startsWith("[USER_IMAGE]");
}

function isAiImageMarker(content) {
  return typeof content === "string" && content.startsWith("[IMAGE]");
}

function isImageMarker(content) {
  return isAiImageMarker(content);
}

function extractImageSrc(content) {
  return content.replace("[IMAGE]", "").trim();
}

function isRenderableImageSrc(src) {
  if (!src) return false;

  return (
    src.startsWith("data:image/") ||
    src.startsWith("http://") ||
    src.startsWith("https://") ||
    src.startsWith("/uploads/") ||
    src.startsWith("/img/") ||
    src.startsWith("blob:")
  );
}
  function addBubble(content, who = "ai", isHtml = false) {
    const wrapper = document.createElement("div");
    wrapper.className = "message " + (who === "user" ? "user" : "ai");

    const div = document.createElement("div");
    div.className = "bubble";

  if (isImageMarker(content)) {
    const src = extractImageSrc(content);

    if (isRenderableImageSrc(src)) {
      const img = document.createElement("img");
      img.src = src;
      img.className = "chat-image";
      img.style.maxWidth = "280px";
      img.style.borderRadius = "14px";
      img.style.cursor = "pointer";
      img.onclick = () => window.open(img.src, "_blank");
      div.appendChild(img);

      imageStore.push({
        url: src,
        createdAt: new Date().toISOString()
      });
    } else {
      // Legacy fallback: oude [USER_IMAGE]-records bevatten alleen prompttekst
      div.textContent = src || "Geüploade afbeelding";
    }
  } else if (isHtml) {
    div.innerHTML = content;
  } else {
    div.textContent = content;
  }

    const time = document.createElement("div");
    time.className = "timestamp";
    time.textContent = nowTime();

    wrapper.appendChild(div);
    wrapper.appendChild(time);
    messagesDiv.appendChild(wrapper);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  function showGuestWelcome() {
    messagesDiv.innerHTML = "";
    addBubble(
      "👋 Welkom bij YellowMind!\n\n" +
      "Je chat nu als gast. Dit gesprek wordt niet opgeslagen.\n\n" +
      "✨ Tip: maak gratis een account aan om je gesprekken te bewaren en afbeeldingen te genereren.",
      "ai"
    );
  }

  function formatHistoryLabel(dateStr) {
  const d = new Date(dateStr);
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);

  const iso = d.toISOString().slice(0, 10);
  const todayIso = today.toISOString().slice(0, 10);
  const yesterdayIso = yesterday.toISOString().slice(0, 10);

  if (iso === todayIso) return "Vandaag";
  if (iso === yesterdayIso) return "Gisteren";

  return d.toLocaleDateString("nl-NL", {
    weekday: "long",
    day: "numeric",
    month: "long"
  });
}

  function renderHistoryButtons(days) {
    if (!historySub) return;

    historySub.innerHTML = "";

    if (!days || !days.length) {
      const empty = document.createElement("div");
      empty.className = "history-empty";
      empty.textContent = "Nog geen eerdere gesprekken";
      historySub.appendChild(empty);
      return;
    }

    days.forEach((day) => {
      const btn = document.createElement("button");
      btn.className = "sidebar-sub-btn";
      btn.dataset.action = "history";
      btn.dataset.day = day;
      btn.textContent = formatHistoryLabel(day);

      btn.addEventListener("click", () => {
        loadChatHistory(day);
        closeSidebar();
      });

      historySub.appendChild(btn);
    });
  }

  function openImageModal(url) {
  if (!imageModal) {
    imageModal = document.createElement("div");
    imageModal.className = "image-modal";
    document.body.appendChild(imageModal);
  }

  imageModal.innerHTML = `
    <div class="image-modal-inner">
      <img src="${url}" class="image-modal-img"/>
      <div class="image-modal-actions">
        <button id="downloadImageBtn">⬇️ Download</button>
        <button id="closeImageModal">✖</button>
      </div>
    </div>
  `;

  imageModal.style.display = "flex";

  document.getElementById("closeImageModal").onclick = () => {
    imageModal.style.display = "none";
  };

  document.getElementById("downloadImageBtn").onclick = async () => {
    const res = await fetch(`${API_BASE}/images/download`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        session_id: getSessionId(),
        image_url: url
      })
    });

    const data = await res.json();

    if (!data.allowed) {
      alert("⚠️ Download limiet bereikt (free account)");
      return;
    }

    const link = document.createElement("a");
    link.href = url;
    link.download = "yellowmind-image.jpg";
    link.click();
  };
}
async function loadChatHistory(day = "today") {
  if (isGuest()) return;

  const session_id = getSessionId();
  messagesDiv.innerHTML = "";
  showHistoryLoading();

  try {
    let url = `${API_BASE}/chat/history?session_id=${encodeURIComponent(session_id)}`;

    if (day) {
      url += `&day=${encodeURIComponent(day)}`;
    }

    const res = await fetch(url);
    const data = await res.json();
    removeHistoryLoading();

    let messages = [];

    if (day === "today") {
      messages = data.today || data.messages || [];
    } else if (day === "yesterday") {
      messages = data.yesterday || data.messages || [];
    } else {
      messages = data.messages || [];
    }

    if (messages.length > 0) {
      messages.forEach((msg) => {
        if (typeof msg.content === "string" && msg.content.startsWith("[USER_IMAGE]")) {
          return;
        }

        addBubble(
          msg.content || "",
          msg.role === "user" ? "user" : "ai"
        );
      });
    } else if (day === "today" && data.welcome) {
      addBubble(data.welcome, "ai");
    } else {
      addBubble("Nog geen gesprekken op deze datum.", "ai");
    }
  } catch (err) {
    console.error("History load failed:", err);
    removeHistoryLoading();
    addBubble("⚠️ Geschiedenis laden is mislukt.", "ai");
  }
}

async function loadHistoryDays() {
  if (isGuest()) return;

  const session_id = getSessionId();

  try {
    const res = await fetch(
      `${API_BASE}/chat/history?session_id=${encodeURIComponent(session_id)}&day=list`
    );
    const data = await res.json();

    renderHistoryButtons(data.available_days || []);
  } catch (err) {
    console.error("History days load failed:", err);
    if (historySub) {
      historySub.innerHTML = `<div class="history-empty">⚠️ Datums laden mislukt</div>`;
    }
  }
}

function formatHistoryLabel(dateStr) {
  const d = new Date(dateStr);
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);

  const iso = d.toISOString().slice(0, 10);
  const todayIso = today.toISOString().slice(0, 10);
  const yesterdayIso = yesterday.toISOString().slice(0, 10);

  if (iso === todayIso) return "Vandaag";
  if (iso === yesterdayIso) return "Gisteren";

  return d.toLocaleDateString("nl-NL", {
    weekday: "long",
    day: "numeric",
    month: "long"
  });
}

function renderHistoryButtons(days) {
  if (!historySub) return;

  historySub.innerHTML = "";

  if (!days.length) {
    historySub.innerHTML = `<div class="history-empty">Nog geen eerdere gesprekken</div>`;
    return;
  }

  days.forEach((day) => {
    const btn = document.createElement("button");
    btn.className = "sidebar-sub-btn";
    btn.dataset.action = "history";
    btn.dataset.day = day;
    btn.textContent = formatHistoryLabel(day);

    btn.addEventListener("click", () => {
      loadChatHistory(day);
      closeSidebar();
    });

    historySub.appendChild(btn);
  });
}

function showHistoryLoading(text = "🕘 Geschiedenis wordt opgehaald, moment geduld…") {
  historyLoadingBubble = document.createElement("div");
  historyLoadingBubble.className = "bubble ai";
  historyLoadingBubble.textContent = text;
  messagesDiv.appendChild(historyLoadingBubble);
}

  function removeHistoryLoading() {
    if (historyLoadingBubble) {
      historyLoadingBubble.remove();
      historyLoadingBubble = null;
    }
  }

  function isRememberedImageQuestion(text) {
  const q = (text || "").toLowerCase().trim();

    if (!lastUploadedImageFile) return false;
    if (!q) return false;

    // Eerst text-to-image uitsluiten
    if (isTextToImagePrompt(q)) return false;

    // Analyse / verwijzing naar bestaande afbeelding
    const analysisSignals = [
      "genereer een afbeelding",
    "genereer afbeelding",
    "afbeelding genereren",
    "afbeeldingen genereren",
    "kun je een afbeelding maken",
    "kun je afbeeldingen maken",
    "maak een afbeelding",
    "maak afbeelding",
    "maak een plaatje",
    "maak een foto",
    "laat een afbeelding zien",
    "laat eens zien",
    "teken",
    "illustratie",
    "genereer een",
    "afbeelding van",
    "plaatje van",
    "foto van",
    "logo maken",
    "banner maken",
    "avatar maken"
    ];

    if (analysisSignals.some(t => q.includes(t))) {
      return true;
    }

    // Editvragen op bestaande afbeelding
    if (isUploadEditPrompt(q)) {
      return true;
    }

    return false;
  }



function clearSelectedImage() {
  selectedImageFile = null;

  if (chatImageInput) chatImageInput.value = "";
  if (uploadPreview) uploadPreview.style.display = "none";
  if (uploadPreviewImg) uploadPreviewImg.src = "";
  if (uploadPreviewText) uploadPreviewText.textContent = "Afbeelding geselecteerd";
}

    function showSelectedImagePreview(file) {
    console.log("🖼️ showSelectedImagePreview called:", file);

    if (!file) return;

    const objectUrl = URL.createObjectURL(file);
    console.log("🔗 preview objectUrl:", objectUrl);
    console.log("uploadPreview =", uploadPreview);
    console.log("uploadPreviewImg =", uploadPreviewImg);
    console.log("uploadPreviewText =", uploadPreviewText);

    if (uploadPreviewImg) {
        uploadPreviewImg.src = objectUrl;
    }

    if (uploadPreviewText) {
        uploadPreviewText.textContent = file.name;
    }

    if (uploadPreview) {
        uploadPreview.style.display = "flex";
        uploadPreview.style.alignItems = "center";
        uploadPreview.style.gap = "12px";
    }
    }

    function setDropzoneActive(active) {
    if (!chatShell) return;
    chatShell.classList.toggle("drag-active", active);
  }

    function handleDroppedFile(file) {
    console.log("📥 handleDroppedFile called:", file);

    if (!file) {
        console.log("⛔ geen file ontvangen");
        return;
    }

    const allowed = ["image/jpeg", "image/png", "image/webp"];
    if (!allowed.includes(file.type)) {
        console.log("⛔ ongeldig filetype:", file.type);
        alert("Alleen JPG, PNG en WEBP zijn toegestaan.");
        clearSelectedImage();
        return;
    }

    selectedImageFile = file;
    lastUploadedImageFile = file;

    console.log("✅ selectedImageFile gezet:", selectedImageFile);
    console.log("✅ lastUploadedImageFile gezet:", lastUploadedImageFile);

    showSelectedImagePreview(file);
    }


    function isUploadEditPrompt(text) {
    const q = (text || "").toLowerCase();
    const triggers = [
        "karikatuur",
        "cartoon",
        "anime",
        "ghibli",
        "bewerk",
        "bewerken",
        "edit",
        "verander",
        "veranderen",
        "transformeer",
        "transformeren",
        "stijl",
        "pas aan",
        "achtergrond",
        "verwijder",
        "weghalen",
        "haal",
        "eruit halen",
        "uitknippen",
        "losmaken",
        "apart zetten",
        "apart in een afbeelding",
        "vrijstaand",
        "maak hiervan",
        "maak hier",
        "van maken"
    ];
    
    return triggers.some(t => q.includes(t));
    }

async function showImagesView() {
  messagesDiv.innerHTML = "";
  showHistoryLoading("🖼️ Afbeeldingen worden opgehaald, moment geduld…");

  try {
    const res = await fetch(
      `${API_BASE}/images/library?session_id=${getSessionId()}`
    );

    const data = await res.json();
    const images = data.images || [];

    removeHistoryLoading();

    const block = document.createElement("div");
    block.className = "images-view";

    const grid = document.createElement("div");
    grid.className = "images-grid";

    if (!images.length) {
      grid.innerHTML = "<div>Geen afbeeldingen</div>";
    } else {
      images.forEach(imgObj => {
        const img = document.createElement("img");
        img.src = imgObj.url;
        img.className = "image-thumb";
        img.onclick = () => openImageModal(imgObj.url);
        grid.appendChild(img);
      });
    }

    block.appendChild(grid);
    messagesDiv.appendChild(block);
  } catch (err) {
    console.error("Images load failed:", err);
    removeHistoryLoading();
    addBubble("⚠️ Afbeeldingen laden mislukt.", "ai");
  }
}


function openImageModal(url) {
  if (!imageModal) {
    imageModal = document.createElement("div");
    imageModal.className = "image-modal";
    document.body.appendChild(imageModal);
  }

  imageModal.innerHTML = `
    <div class="image-modal-inner">
      <img src="${url}" class="image-modal-img"/>
      <div class="image-modal-actions">
        <button id="downloadBtn">⬇️ Download</button>
        <button id="closeBtn">✖</button>
      </div>
    </div>
  `;

  imageModal.style.display = "flex";

  document.getElementById("closeBtn").onclick = () => {
    imageModal.style.display = "none";
  };

  document.getElementById("downloadBtn").onclick = async () => {
    const res = await fetch(`${API_BASE}/images/download`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        session_id: getSessionId(),
        image_url: url
      })
    });

    const data = await res.json();

    if (!data.allowed) {
      alert("⚠️ Free limiet bereikt");
      return;
    }

    const a = document.createElement("a");
    a.href = url;
    a.download = "yellowmind.jpg";
    a.click();
  };
}


  function isTextToImagePrompt(text) {
    const q = (text || "").toLowerCase();
    const triggers = [
      "genereer",
      "maak een afbeelding",
      "maak een plaatje",
      "teken",
      "illustratie",
      "genereer een"
    ];
    return triggers.some(t => q.includes(t));
  }

  async function sendPlainChat(text) {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        session_id: CURRENT_SESSION,
        language: "nl",
        wants_image: isTextToImagePrompt(text)
      })
    });

    return await res.json();
  }

  async function sendImageChat(text, file) {
    const formData = new FormData();
    formData.append("session_id", CURRENT_SESSION);
    formData.append("message", text || "");
    formData.append("file", file);

    const res = await fetch(`${API_BASE}/chat/image`, {
      method: "POST",
      body: formData
    });

    return await res.json();
  }

async function loadImages() {
  if (isGuest()) return;

  const session_id = getSessionId();
  messagesDiv.innerHTML = "";
  showHistoryLoading();

  try {
    const res = await fetch(
      `${API_BASE}/chat/history?session_id=${encodeURIComponent(session_id)}&day=images`
    );
    const data = await res.json();
    removeHistoryLoading();

    const images = data.images || [];
    let renderedCount = 0;

    if (!images.length) {
      addBubble("Nog geen afbeeldingen gevonden.", "ai");
      return;
    }

    images.forEach((img) => {
      const raw = (img.content || "").replace("[USER_IMAGE]", "").trim();

      const isUsableImage =
        raw.startsWith("http") ||
        raw.startsWith("/") ||
        raw.startsWith("data:image/");

      if (!isUsableImage) {
        return;
      }

      const url =
        raw.startsWith("http") || raw.startsWith("data:image/")
          ? raw
          : `${API_BASE}${raw}`;

      const wrapper = document.createElement("div");
      wrapper.className = "image-history-item";

      const image = document.createElement("img");
      image.src = url;
      image.className = "chat-image";
      image.alt = "Opgeslagen afbeelding";

      wrapper.appendChild(image);
      messagesDiv.appendChild(wrapper);
      renderedCount++;
    });

    if (renderedCount === 0) {
      addBubble("Er zijn afbeeldings-items gevonden, maar geen toonbare afbeeldingen.", "ai");
    }
  } catch (err) {
    console.error("Image load failed:", err);
    removeHistoryLoading();
    addBubble("⚠️ Afbeeldingen laden mislukt.", "ai");
  }
}

function formatHistoryLabel(dateStr) {
  const d = new Date(dateStr);
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);

  const iso = d.toISOString().slice(0, 10);
  const todayIso = today.toISOString().slice(0, 10);
  const yesterdayIso = yesterday.toISOString().slice(0, 10);

  if (iso === todayIso) return "Vandaag";
  if (iso === yesterdayIso) return "Gisteren";

  return d.toLocaleDateString("nl-NL", {
    weekday: "long",
    day: "numeric",
    month: "long"
  });
}

function renderHistoryButtons(days) {
  if (!historySub) return;

  historySub.innerHTML = "";

  if (!days.length) {
    historySub.innerHTML = `<div class="history-empty">Nog geen eerdere gesprekken</div>`;
    return;
  }

  days.forEach((day) => {
    const btn = document.createElement("button");
    btn.className = "sidebar-sub-btn";
    btn.dataset.action = "history";
    btn.dataset.day = day;
    btn.textContent = formatHistoryLabel(day);

    btn.addEventListener("click", () => {
      loadChatHistory(day);
      closeSidebar();
    });

    historySub.appendChild(btn);
  });
}  

async function sendChatMessage() {
  const text = chatInput.value.trim();
  console.log("📨 sendChatMessage text =", text);
    console.log("📨 selectedImageFile =", selectedImageFile);
    console.log("📨 lastUploadedImageFile =", lastUploadedImageFile);

  const hasFreshUpload = !!selectedImageFile;
  const wantsNewGeneratedImage = isTextToImagePrompt(text);
  const wantsRememberedImage = isRememberedImageQuestion(text);

  const imageFileForRequest = hasFreshUpload
    ? selectedImageFile
    : (wantsRememberedImage ? lastUploadedImageFile : null);

  if (!text && !imageFileForRequest) return;

  addBubble(text || "🖼️ Afbeelding geüpload", "user");
  chatInput.value = "";
  setYello("thinking");

  // Alleen bubble tonen bij verse upload
  if (selectedImageFile) {
    const previewUrl = URL.createObjectURL(selectedImageFile);
    addBubble("[IMAGE]" + previewUrl, "user");
  }

  setYello(imageFileForRequest || wantsNewGeneratedImage ? "image" : "thinking");

  const thinkingBubble = document.createElement("div");
  thinkingBubble.className = "bubble ai";

  if (imageFileForRequest) {
    if (selectedImageFile) {
      thinkingBubble.textContent = isUploadEditPrompt(text)
        ? "🖼️ Ik ben je afbeelding aan het bewerken…"
        : "👀 Ik kijk even naar je afbeelding…";
    } else {
      thinkingBubble.textContent = isUploadEditPrompt(text)
        ? "🖼️ Ik gebruik je laatst geüploade afbeelding en ga hem bewerken…"
        : "👀 Ik gebruik je laatst geüploade afbeelding…";
    }
  } else if (wantsNewGeneratedImage) {
    thinkingBubble.textContent = "🖼️ Ik ben een afbeelding voor je aan het maken…";
  } else {
    thinkingBubble.textContent = "Aan het denken…";
  }

  messagesDiv.appendChild(thinkingBubble);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;

  try {
    let data;

    if (imageFileForRequest) {
      console.log("🚀 sendImageChat()");
      data = await sendImageChat(text, imageFileForRequest);
    } else {
      console.log("🚀 sendPlainChat()");
      data = await sendPlainChat(text);
    }

    thinkingBubble.remove();

    setYello("typing"); // simulatie van "praten"

    if (data.type === "image" && data.url) {
      if (data.reply) addBubble(data.reply, "ai");
      addBubble("[IMAGE]" + data.url, "ai");
    } else if (data.type === "vision") {
      addBubble(data.reply || "⚠️ Geen analyse teruggekregen.", "ai");
    } else if (data.type === "search") {
      addBubble("🔍 Ik ga dit voor je opzoeken…", "ai");
      window.location.href = `${BASE_PATH}/search.html?q=${encodeURIComponent(data.query)}`;
      return;
    } else {
      addBubble(data.reply || "⚠️ Geen antwoord", "ai");
    }
  } catch (err) {
    console.error(err);
    thinkingBubble.textContent = "⚠️ Er ging iets mis.";
  } finally {
  clearSelectedImage();

  setTimeout(() => {
    setYello("idle");
  }, 1200); // kleine delay voor natuurlijk gevoel

  chatInput.focus();
}
}

  chatImageInput?.addEventListener("change", (e) => {
    const file = e.target.files?.[0];
    handleDroppedFile(file);
  });

  removeUploadBtn?.addEventListener("click", () => {
    clearSelectedImage();
  });

  sendBtn?.addEventListener("click", sendChatMessage);

  chatInput?.addEventListener("input", () => {
    if (chatInput.value.trim().length > 0) {
      setYello("typing");
    } else {
      setYello("idle");
    }
  });


  chatInput?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendChatMessage();
    }
  });

  closeBtn?.addEventListener("click", () => {
    window.location.href = `${BASE_PATH}/index.html`;
  });

historyBtn?.addEventListener("click", async (e) => {
  e.stopPropagation();

  const willOpen = !historySub.classList.contains("open");

  if (willOpen) {
    await loadHistoryDays();
  }

  historySub.classList.toggle("open");
});

  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-action]");
    if (!btn) return;

    const action = btn.dataset.action;

    if (action === "images") {
      e.preventDefault();
      showImagesView();
      closeSidebar();
      return;
    }

    const accountBtn = document.querySelector('.sidebar-btn[data-action="account"]');
    const session = localStorage.getItem("authSession");

    if (accountBtn) {
      if (!session || session.startsWith("guest_")) {
        accountBtn.querySelector("span").textContent = "Inloggen";
      } else {
        const name = localStorage.getItem("authUserName");
        if (name) {
          accountBtn.querySelector("span").textContent = name;
        }
      }
    }

    if (action === "logout") {
      e.preventDefault();

      fetch(`${API_BASE}/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: getSessionId() })
      }).finally(() => {
        localStorage.clear();
        window.location.href = `${BASE_PATH}/index.html`;
      });
    }
  });

  if (isGuest()) {
    showGuestWelcome();
  } else {
    loadChatHistory("today");
    setYello("idle");
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const accountBtn = document.querySelector('.sidebar-btn[data-action="account"]');

  if (accountBtn) {
    accountBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();

      const session = localStorage.getItem("authSession");

      if (!session || session.startsWith("guest_")) {
        window.location.href = "/login.html";
        return;
      }

      window.location.href = "/account.html";
    });
  }
});