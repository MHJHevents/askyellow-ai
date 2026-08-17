const BASE_PATH = "";
const API_BASE = "https://askyellow-ai.onrender.com";
const SESSION_KEY = "ay_session_id";

function getSessionId() {
    let sid = localStorage.getItem(SESSION_KEY);
    if (!sid) {
        sid = crypto.randomUUID();
        localStorage.setItem(SESSION_KEY, sid);
    }
    return sid;
}

function showMessage(message) {
    alert(message);
}

function showError(message) {
    alert(message);
}

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);

    if (params.get("registered")) {
        showMessage("Account aangemaakt. Controleer je e-mail en bevestig eerst je account.");
    }

    if (params.get("verified")) {
        showMessage("Je e-mailadres is bevestigd. Je kunt nu inloggen.");
    }

    if (params.get("reset")) {
        showMessage("Wachtwoord succesvol gewijzigd. Je kunt nu inloggen.");
    }

    document.querySelectorAll(".toggle-password").forEach(toggle => {
        toggle.addEventListener("click", () => {
            const input = document.getElementById(toggle.dataset.target);
            const isPassword = input.type === "password";
            input.type = isPassword ? "text" : "password";
            toggle.textContent = isPassword ? "🙈" : "👁️";
        });
    });

    const guestBtn = document.getElementById("btn-guest");
    if (guestBtn) {
        guestBtn.onclick = () => {
            const guestSession = "guest_" + crypto.randomUUID();
            localStorage.setItem("authSession", guestSession);
            window.location.href = `${BASE_PATH}/chat.html`;
        };
    }

    const form = document.getElementById("loginForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const email = document.getElementById("email").value.trim().toLowerCase();
        const password = document.getElementById("password").value;

        if (!email || !password) {
            showError("Vul alle velden in.");
            return;
        }

        try {
            const newSessionId = crypto.randomUUID();
            localStorage.setItem("ay_session_id", newSessionId);

            const res = await fetch(`${API_BASE}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email,
                    password,
                    session_id: newSessionId
                })
            });

            const data = await res.json();

            if (!res.ok) {
                if (res.status === 403) {
                    const resend = confirm(
                        "Je e-mailadres is nog niet geverifieerd. Nieuwe verificatiemail versturen?"
                    );

                    if (resend) {
                        await fetch(`${API_BASE}/auth/resend-verification`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ email })
                        });
                        showMessage("Als het account bestaat, is een nieuwe verificatiemail verstuurd.");
                    }
                    return;
                }

                showError(data.detail || "Inloggen mislukt.");
                return;
            }

            localStorage.setItem("authSession", newSessionId);
            localStorage.setItem("authUserName", data.first_name || "");
            window.location.href = `${BASE_PATH}/chat.html`;
        } catch (err) {
            console.error("Login failed:", err);
            showError("Kon niet inloggen. Probeer het later nog eens.");
        }
    });
});
