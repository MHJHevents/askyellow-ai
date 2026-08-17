/* ============================================================
   YellowMind v2 — PERSONALITY + LANGUAGE HANDLING
============================================================ */

/* -------------------------------
   1. Detect user language
-------------------------------- */
function ymDetectLang() {
  const saved = localStorage.getItem("ym_lang");
  if (saved) return saved;

  const nav = (navigator.language || "en").toLowerCase();
  const lang = nav.startsWith("nl") ? "nl" : "en";
  localStorage.setItem("ym_lang", lang);
  return lang;
}

/* -------------------------------
   2. Set language
-------------------------------- */
function ymSetLang(lang) {
  localStorage.setItem("ym_lang", lang);
  document.documentElement.setAttribute("lang", lang);
}

/* -------------------------------
   3. Response tuning (emotion/mode)
-------------------------------- */
function ymToneBoost(answer, question, lang) {
  const q = question.toLowerCase();

  // Empathie
  if (q.includes("bang") || q.includes("stress") || q.includes("verdriet")) {
    return (
      answer +
      (lang === "nl"
        ? " Ik ben er voor je. 💛"
        : " I'm here for you. 💛")
    );
  }

  // Tech help
  if (q.includes("api") || q.includes("code") || q.includes("dns")) {
    return (
      answer +
      (lang === "nl"
        ? " Als je wilt, leg ik het stap voor stap uit. 🔧"
        : " If you want, I can explain it step by step. 🔧")
    );
  }

  return answer;
}
