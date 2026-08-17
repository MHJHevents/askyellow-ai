const API_BASE = "https://askyellow-ai.onrender.com";

function showError(message) {
    const box = document.getElementById("errorBox");
    if (box) box.textContent = message;
}

function clearError() {
    const box = document.getElementById("errorBox");
    if (box) box.textContent = "";
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".toggle-password").forEach(toggle => {
        toggle.addEventListener("click", () => {
            const input = document.getElementById(toggle.dataset.target);
            const isPassword = input.type === "password";
            input.type = isPassword ? "text" : "password";
            toggle.textContent = isPassword ? "🙈" : "👁️";
        });
    });

    const form = document.getElementById("registerForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        clearError();

        const first_name = document.getElementById("firstName").value.trim();
        const last_name = document.getElementById("lastName").value.trim();
        const email = document.getElementById("email").value.trim().toLowerCase();
        const password = document.getElementById("password").value;
        const password2 = document.getElementById("password2").value;

        if (!first_name || !last_name || !email || !password || !password2) {
            showError("Vul alle velden in.");
            return;
        }

        if (password.length < 6) {
            showError("Wachtwoord moet minimaal 6 tekens hebben.");
            return;
        }

        if (password !== password2) {
            showError("Wachtwoorden komen niet overeen.");
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    first_name,
                    last_name,
                    email,
                    password
                })
            });

            const data = await res.json();

            if (!res.ok) {
                showError(data.detail || "Registreren mislukt.");
                return;
            }

            window.location.href = `/login.html?registered=1`;
        } catch (err) {
            console.error("Register failed:", err);
            showError("Kon geen account aanmaken. Probeer het later opnieuw.");
        }
    });
});



