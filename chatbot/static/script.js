function sendMessage() {
    let userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return;

    let chatBox = document.getElementById("chat-box");

    // Display user message
    let userMessage = document.createElement("div");
    userMessage.classList.add("message", "user");
    userMessage.innerText = userInput;
    chatBox.appendChild(userMessage);

    // Clear input field
    document.getElementById("user-input").value = "";

    // Send request to backend
    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ prompt: userInput })
    })
    .then(response => response.json())
    .then(data => {
        let botMessage = document.createElement("div");
        botMessage.classList.add("message", "bot");
        botMessage.innerText = data.response; // Use the backend response
        chatBox.appendChild(botMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        console.error("Error:", error);
    });
}
