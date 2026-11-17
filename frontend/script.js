const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const messages = document.getElementById("chat-messages");

// Keep the same conversation ID across page refreshes
let conversationId = sessionStorage.getItem("chuck_conversation_id");

if (!conversationId) {
    conversationId = crypto.randomUUID();
    sessionStorage.setItem("chuck_conversation_id", conversationId);
}

function addMessage(role, content) {
    const message = document.createElement("div");
    message.className = `message ${role}`;

    const name = document.createElement("strong");
    name.textContent = role === "user" ? "YOU" : "CHUCK";

    const text = document.createElement("p");
    text.textContent = content;

    message.appendChild(name);
    message.appendChild(text);
    messages.appendChild(message);

    messages.scrollTop = messages.scrollHeight;
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const message = input.value.trim();
    if (!message) return;

    addMessage("user", message);
    input.value = "";

    const button = form.querySelector("button");
    button.disabled = true;
    button.textContent = "Thinking...";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                conversation_id: conversationId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        addMessage("assistant", data.response || "No response received.");

    } catch (error) {
        addMessage("assistant", `Connection error: ${error.message}`);
    } finally {
        button.disabled = false;
        button.textContent = "Send";
        input.focus();
    }
});