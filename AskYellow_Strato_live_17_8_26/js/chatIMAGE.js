import * as image from "/js/image.js";

document.addEventListener("DOMContentLoaded", () => {
    console.log("✅ DOMContentLoaded fired");

    // 👤 Gast
    if (isGuest()) {
        console.log("👤 Guest → show welcome");
        showGuestWelcome();
        return;
    }

    // 🔐 Ingelogd
    console.log("🔐 User → load history");
    loadChatHistory("today");
    });


    const messagesDiv = document.getElementById("chatMessages");
    const chatInput = document.getElementById("chatInput");
    const sendBtn = document.getElementById("sendChat");
    const closeBtn = document.getElementById("btn-close");
    const yello = document.getElementById("yelloAvatar");
    const thinkingEl = document.getElementById("thinking");
    const historyBtn = document.getElementById("history-toggle");
    const historySub = document.querySelector(".history-sub");

    const API_BASE = "https://askyellow-ai.onrender.com";
    
    const BASE_PATH = "";

    // =============================
    // SESSION MANAGER (single truth)
    // =============================
    const SESSION_KEY = "ay_session_id";

    function getSessionId() {
        let sid = localStorage.getItem(SESSION_KEY);
        if (!sid) {
            sid = crypto.randomUUID();
            localStorage.setItem(SESSION_KEY, sid);
        }
        return sid;
    }

    let CURRENT_SESSION = getSessionId();


    
    /* =============================
    TIMESTAMP BIJ BERICHTEN
    ============================== */

    function nowTime() {
        return new Date().toLocaleTimeString("nl-NL", {
            hour: "2-digit",
            minute: "2-digit"
        });
    }

    /* =============================
        HELPERS
    ============================== */
    function showGuestWelcome() {
        messagesDiv.innerHTML = "";

        addBubble(
            "👋 Welkom bij YellowMind!\n\n" +
            "Je chat nu als gast. Dit gesprek wordt niet opgeslagen.\n\n" +
            "✨ Tip: maak gratis een account aan om je gesprekken te bewaren en afbeeldingen te genereren.",
            "ai"
        );
    }


    function startChat() {
        if (isGuest()) {
            // 👤 Gast: GEEN history
            messagesDiv.innerHTML = "";

            addBubble(
                "👋 Welkom! Je chat nu als gast.\n\n" +
                "Je kunt vragen stellen, maar gesprekken worden niet opgeslagen. " +
                "Wil je alles bewaren? Maak dan gratis een account aan 😊",
                "ai"
            );

            return;
        }

        // 🔐 Ingelogd: wél history
        loadChatHistory("today");
    }

    function isGuest() {
        return localStorage.getItem("authSession")?.startsWith("guest_");
    }

    function renderSystemMessage(text) {
        const el = document.createElement("div");
        el.className = "system-message";
        el.textContent = text;
        chatContainer.appendChild(el);
    }
    function openSidebar() {
        sidebar.classList.add("open");

        historySub.classList.remove("open");
        historyBtn.classList.remove("active");
        }

    function closeSidebar() {
        appShell.classList.remove("sidebar-open");
    }
    
    function showImagesView() {
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
                grid.appendChild(el);
            });
        }

        chat.appendChild(block);
    }

    /* =============================
    geeft weer: in ben een afbeelding aan het maken
    ============================== */
    function showImageGenerating() {
    const el = document.createElement("div");
    el.className = "bubble ai image-generating";
    el.textContent = "🖼️ Ik ben een afbeelding voor je aan het maken…";
    messagesDiv.appendChild(el);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return el;
}
    
    /* =============================
    koppeling naar image.js
    ============================== */
    image.initImageEngine({
        isGuest,
        addBubble,
        setYello
        });

    /* =============================
        Knop voor afbeeldingen
    ============================== */
    document
        .querySelector('[data-action="images"]')
        .addEventListener('click', () => {
            closeSidebar();
            image.showImagesView();
        });
    /* =============================
        YELLO STATE
    ============================== */
    let isGeneratingImage = false;

    function setYello(state) {
        // 🛑 voorkom thinking tijdens image generatie
        if (isGeneratingImage && state === "thinking") return;

        let src;
        switch (state) {
            case "typing":
                src = "/img/yello_typen_trans.mp4";
                break;
            case "thinking":
                src = "/img/yello_denkend_trans.mp4";
                break;
            case "image":
                src = "/img/yello_image_trans.mp4";
                break;
            default:
                src = "/img/yello_lopend_trans.mp4";
        }

        if (!yello.src.includes(src)) {
            yello.src = src;
            yello.load();
            yello.play();
        }
    }


    /* =============================
    BUBBLES
    ============================== */
    function addBubble(content, who = "ai", isHtml = false) {

        // 🧱 WRAPPER (voor alignment + timestamp)
        const wrapper = document.createElement("div");
        wrapper.className = "message " + (who === "user" ? "user" : "ai");

        // 💬 BUBBLE
        const div = document.createElement("div");
        div.className = "bubble";

        // 🖼️ IMAGE DETECTIE (base64 image van AI)
        if (
            typeof content === "string" &&
            content.startsWith("[IMAGE]data:image")
        ) {
            const img = document.createElement("img");
            img.src = content.replace("[IMAGE]", "");
            img.className = "chat-image";

            // optioneel: klik om te vergroten
            img.onclick = () => window.open(img.src, "_blank");

            div.appendChild(img);

        } else if (isHtml) {
            div.innerHTML = content;
        } else {
            div.textContent = content;
        }

        // 🕒 TIMESTAMP
        const time = document.createElement("div");
        time.className = "timestamp";
        time.textContent = nowTime();

        // 🧩 OPBOUW
        wrapper.appendChild(div);
        wrapper.appendChild(time);

        messagesDiv.appendChild(wrapper);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    // =============================
    // HISTORY LOADING FEEDBACK
    // =============================
    var historyLoadingBubble = null;

    function showHistoryLoading() {
        historyLoadingBubble = document.createElement("div");
        historyLoadingBubble.className = "bubble ai";
        historyLoadingBubble.textContent =
            "🕘 Geschiedenis wordt opgehaald, moment geduld…";
        messagesDiv.appendChild(historyLoadingBubble);
    }

    function removeHistoryLoading() {
        if (historyLoadingBubble) {
            historyLoadingBubble.remove();
            historyLoadingBubble = null;
        }
    }

    async function loadChatHistory(day) {
    console.log("🔥 loadChatHistory CALLED with day =", day);

    if (isGuest()) {
        console.log("👤 Guest → history loading skipped");
        return;
    }

    const session_id = getSessionId();
    messagesDiv.innerHTML = "";
    image.resetImages();
    showHistoryLoading();

    try {
        const res = await fetch(
        `${API_BASE}/chat/history?session_id=${encodeURIComponent(session_id)}`
        );

        const data = await res.json();
        removeHistoryLoading();

        const messages =
        day === "yesterday" ? data.yesterday : data.today;

        if (messages && messages.length > 0) {
        messages.forEach(msg => {
            // 🖼️ image.js mag eerst proberen
            if (image.handleHistoryMessage(msg)) return;

            // 📝 normale tekst
            addBubble(
            msg.content || "",
            msg.role === "user" ? "user" : "ai"
            );
        });
        } else if (day === "today" && data.welcome) {
        addBubble(data.welcome, "ai");
        }

    } catch (err) {
        console.error("History load failed:", err);
        removeHistoryLoading();
    }
    }
async function sendChatMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // 1️⃣ eerst: confirmation afhandelen (1x!)
    const confirmResult = image.handleConfirmation(text);

    if (confirmResult?.handled) {
        chatInput.value = "";
        chatInput.focus();
        return;
    }

    // 2️⃣ image-intent ALLEEN bij echte user submit
    const imageIntent = image.handleImageFlow(text, { source: "user" });

    if (imageIntent?.handled) {
        chatInput.value = "";
        chatInput.focus();
        return;
    }

    // 3️⃣ normale chat-flow
    addBubble(text, "user");
    chatInput.value = "";
    setYello("thinking");

    let thinkingBubble = null;

    if (imageIntent?.wantsImage) {
        thinkingBubble = showImageGenerating();
    } else {
        thinkingBubble = document.createElement("div");
        thinkingBubble.className = "bubble ai";
        thinkingBubble.textContent = "Aan het denken…";
        messagesDiv.appendChild(thinkingBubble);
    }

    try {
        const finalPrompt = confirmResult?.overridePrompt || text;

        const res = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: finalPrompt,
                session_id: CURRENT_SESSION,
                language: "nl",
                wants_image: imageIntent?.wantsImage === true
            })
        });

        const data = await res.json();
        thinkingBubble?.remove();

        // 🔍 search handoff
        if (data.type === "search") {
            addBubble("🔍 Ik ga dit voor je opzoeken…");
            window.location.href =
                `${BASE_PATH}/search.html?q=${encodeURIComponent(data.query)}`;
            return;
        }

        // 🖼️ image response?
        if (image.handleApiResponse(data)) return;

        // 📝 normale AI-reply
        addBubble(data.reply || "⚠️ Geen antwoord", "ai");

    } catch (err) {
        thinkingBubble.textContent = "⚠️ Er ging iets mis.";
    }

    setYello("idle");
}

//    async function sendChatMessage() {
//     const isUserSubmit = true;
//     const text = chatInput.value.trim();
//     const confirmResult = image.handleConfirmation(text);

//     if (confirmResult?.handled) {
//         chatInput.value = "";      // 🔑 reset input
//         chatInput.focus();         // 🔑 focus terug
//         return;
//     }


//     if (image.handleConfirmation?.(text)) return;

//     if (!text) return;

//     // 🧠 image-engine krijgt eerste kans
//     const imageIntent = image.handleImageFlow(text);

//     if (imageIntent?.handled) return;

//         addBubble(text, "user");
//         chatInput.value = "";
//         setYello("thinking");

//         let thinkingBubble = null;

//     if (imageIntent.wantsImage) {
//         thinkingBubble = showImageGenerating();
//         } else {
//             thinkingBubble = document.createElement("div");
//             thinkingBubble.className = "bubble ai";
//             thinkingBubble.textContent = "Aan het denken…";
//             messagesDiv.appendChild(thinkingBubble);
//         }

//         const finalPrompt = confirmResult?.overridePrompt || text;

//         try {
//             const res = await fetch(`${API_BASE}/chat`, {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({
//                 message: text,
//                 session_id: CURRENT_SESSION,
//                 language: "nl",
//                 wants_image: confirmResult?.wantsImage === true
//                 })

//             });

//             const data = await res.json();
//             thinkingBubble?.remove();

//             // 🔍 search
//             if (data.type === "search") {
//             addBubble("🔍 Ik ga dit voor je opzoeken…");
//             window.location.href =
//                 `${BASE_PATH}/search.html?q=${encodeURIComponent(data.query)}`;
//             return;
//             }

//             // 🖼️ image response?
//             if (image.handleApiResponse(data)) return;

//             // 📝 normale chat
//             addBubble(data.reply || "⚠️ Geen antwoord", "ai");

//         } catch (e) {
//             thinking.textContent = "⚠️ Er ging iets mis.";
//         }

//         setYello("idle");
//         }

               
    /* =============================
        EVENTS onderstaande 
    ============================= */
    const appShell = document.getElementById("app-shell");
    const menuToggle = document.getElementById("menuToggle");

    menuToggle?.addEventListener("click", () => {
        appShell.classList.toggle("sidebar-open");
    });

    closeBtn?.addEventListener("click", () => {
        console.log("❌ Chat sluiten");

        // optie A: terug naar homepage
        window.location.href = `${BASE_PATH}/index.html`;

    });

    function showPanel(panelId) {
        document
            .querySelectorAll(".sidebar-panel")
            .forEach(p => p.classList.remove("active"));

        const panel = document.getElementById(panelId);
        if (panel) panel.classList.add("active");
    }

    historyBtn.addEventListener("click", (e) => {
        e.stopPropagation(); // ⬅️ DIT IS DE GOUDEN REGEL
        historySub.classList.toggle("open");
    });

    document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-action]");
    if (!btn) return;

    const action = btn.dataset.action;

    // 🔹 history: alleen dagen, niet toggle
    if (action === "history" && btn.dataset.day) {
        e.preventDefault();
        loadChatHistory(btn.dataset.day);
        closeSidebar();
        return;
    }

    // 🔹 images: elders afgehandeld
    if (action === "images") {
        e.preventDefault();
        return;
    }

    // 🔹 account
    if (action === "account") {
        e.preventDefault();
        showPanel("panel-account");
        closeSidebar();
        return;
    }

    // 🔹 logout (DIT WAS DE MISSENDE)
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

        return;
    }

    // fallback: sidebar sluiten
    closeSidebar();
    });
    
    // =============================
    // SEND EVENTS (VERSTUUR)
    // =============================
    sendBtn.addEventListener("click", () => {
        sendChatMessage();
    });

    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            sendChatMessage();
        }
});
    