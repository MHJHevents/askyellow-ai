/* ============================================================
   YellowMind v2 — CORE ENGINE
   API → Safety → Personality → Answer
============================================================ */

const YM_API = "https://askyellow-staging.onrender.com/ask";

/* --------------------------
   SESSION ID (persistent)
--------------------------- */
function ymGetSessionId() {
  let sid = localStorage.getItem("ym_session");
  if (!sid) {
    sid = "anon-" + Math.random().toString(16).slice(2);
    localStorage.setItem("ym_session", sid);
  }
  return sid;
}

/* --------------------------
   1. CLEAN INPUT
--------------------------- */
function ymClean(text) {
  return text.trim().replace(/\s+/g, " ");
}

/* --------------------------
   2. BASIC SPAM CHECK
--------------------------- */
function ymSpam(text) {
  const t = text.toLowerCase();

  if (t.length < 2) return true;
  if (/^(.)\1{5,}$/.test(t)) return true;
  if (t.includes("<script")) return true;
  if (t.includes("drop table")) return true;

  return false;
}

/* --------------------------
   3. SEND TO BACKEND
--------------------------- */
async function ymAsk(question, lang = "nl") {
  question = ymClean(question);

  if (!question || ymSpam(question)) {
    return {
      ok: false,
      answer:
        lang === "en"
          ? "This question doesn’t look valid. Try rephrasing it 🙂"
          : "Deze vraag lijkt niet geldig. Probeer het anders te formuleren. 🙂",
    };
  }

  // ⭐ NEW — persistent session id
  const session_id = ymGetSessionId();

  try {
    const res = await fetch(YM_API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        language: lang,
        session_id: session_id,
      }),
    });

    const data = await res.json();

    return {
      ok: true,
      answer: data.answer || "⚠️ Geen antwoord ontvangen.",
    };
  } catch (err) {
    return {
      ok: false,
      answer:
        lang === "en"
          ? "⚠️ I can’t retrieve an answer right now. Try again soon."
          : "⚠️ Ik kan op dit moment geen live antwoord ophalen. Probeer het zo nog een keer.",
    };
  }
}
