/* ============================================================
   ASKYELLOW QUICK ANSWERS ENGINE v2 (clean)
   Dit bestand levert alleen de quick-answer functie.
   Geen button handlers meer (die zitten in index-ai.html)
============================================================ */

let ASK_QUICK = {};

// JSON laden
fetch("answers.json")
  .then(res => res.json())
  .then(data => {
    ASK_QUICK = data;
    console.log("Quick answers geladen:", Object.keys(data).length);
  })
  .catch(err => console.error("answers.json kon niet geladen worden:", err));

/* ------------ Normaliseer tekst ------------- */
function norm(txt) {
  return txt
    .toLowerCase()
    .trim()
    .replace(/[?.,!]/g, "");
}

/* ------------ Quick Answer functie ------------- */
function checkQuickAnswer(vraag) {
  if (!ASK_QUICK) return null;

  const user = norm(vraag);

  // DIRECTE EXACTE MATCH
  if (ASK_QUICK[user]) return ASK_QUICK[user];

  // ANDERS: simpele "bevat" match
  for (const key in ASK_QUICK) {
    const keyNorm = norm(key);
    if (user.includes(keyNorm)) {
      return ASK_QUICK[key];
    }
  }

  return null;
}

