 const API_BASE = "https://askyellow-ai.onrender.com";
  const BASE_PATH = "";

function setError(message) {
    document.getElementById("errorBox").textContent = message || "";
}

function setSuccess(message) {
    document.getElementById("successBox").textContent = message || "";
}

function formatDate(value) {
    if (!value) return "-";
    try {
        return new Date(value).toLocaleString("nl-NL");
    } catch {
        return value;
    }
}

async function loadAccount() {
    const session_id = localStorage.getItem("authSession");

    if (!session_id || session_id.startsWith("guest_")) {
        window.location.href = "/login.html";
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/auth/me?session_id=${encodeURIComponent(session_id)}`);
        const data = await res.json();

        if (!res.ok) {
            localStorage.removeItem("authSession");
            window.location.href = "/login.html";
            return;
        }

        const user = data.user;

        document.getElementById("firstName").value = user.first_name || "";
        document.getElementById("lastName").value = user.last_name || "";
        document.getElementById("email").value = user.email || "";

        document.getElementById("metaBox").innerHTML = `
            <strong>Accountstatus:</strong>
            <span class="${user.email_verified ? "status-ok" : "status-warn"}">
                ${user.email_verified ? "Email geverifieerd" : "Email nog niet geverifieerd"}
            </span><br>
            <strong>Abonnement:</strong> ${user.subscription_status || "free"}<br>
            <strong>Rol:</strong> ${user.account_role || "user"}<br>
            <strong>Aangemaakt:</strong> ${formatDate(user.created_at)}<br>
            <strong>Laatste login:</strong> ${formatDate(user.last_login)}
        `;
    } catch (err) {
        console.error(err);
        setError("Kon accountgegevens niet laden.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadAccount();

    document.getElementById("accountForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        setError("");
        setSuccess("");

        const session_id = localStorage.getItem("authSession");
        const first_name = document.getElementById("firstName").value.trim();
        const last_name = document.getElementById("lastName").value.trim();

        if (!first_name || !last_name) {
            setError("Voornaam en achternaam zijn verplicht.");
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/auth/account/update`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    session_id,
                    first_name,
                    last_name
                })
            });

            const data = await res.json();

            if (!res.ok) {
                setError(data.detail || "Opslaan mislukt.");
                return;
            }

            localStorage.setItem("authUserName", first_name);
            setSuccess("Gegevens opgeslagen.");
            loadAccount();
        } catch (err) {
            console.error(err);
            setError("Kon account niet opslaan.");
        }
    });

    document.getElementById("logoutBtn").addEventListener("click", async () => {
        const session_id = localStorage.getItem("authSession");

        try {
            await fetch(`${API_BASE}/auth/logout`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id })
            });
        } catch (err) {
            console.error("Logout failed:", err);
        }

        localStorage.removeItem("authSession");
        localStorage.removeItem("authUserName");
        window.location.href = "/login.html";
    });
});