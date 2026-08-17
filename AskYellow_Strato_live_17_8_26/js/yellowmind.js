/* ===========================================================
   YellowMind API Handler
   Stuurt berichten naar de FastAPI Render backend
=========================================================== */

async function askYellowmind(userMessage) {
    try {
        const response = await fetch("https://askyellow-ai.onrender.com/ask", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ question: userMessage })
        });

        const data = await response.json();
        return data.reply || data.answer || "⚠️ Geen geldig antwoord beschikbaar.";
    }
    catch (err) {
        console.error(err);
        return "⚠️ Er ging iets mis met de verbinding.";
    }
}
