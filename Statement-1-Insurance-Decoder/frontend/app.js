const form = document.getElementById("chat-form");
const input = document.getElementById("query-input");
const messages = document.getElementById("chat-messages");
const template = document.getElementById("result-template");

let selectedFilter = "all";

// 🎯 Handle filter clicks
document.querySelectorAll(".filter-item").forEach(item => {
    item.addEventListener("click", () => {
        document.querySelectorAll(".filter-item").forEach(i => i.classList.remove("active"));
        item.classList.add("active");
        selectedFilter = item.dataset.filter;
    });
});

// 🧠 Add user message
function addUserMessage(text) {
    const div = document.createElement("div");
    div.className = "message user";
    div.innerHTML = `
        <div class="avatar"><i class='bx bx-user'></i></div>
        <div class="bubble"><p>${text}</p></div>
    `;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

// 🧠 Add bot response
function addBotResponse(data) {
    const clone = template.content.cloneNode(true);

    const status = clone.querySelector(".result-status");
    const direct = clone.querySelector(".direct-text");
    const eli5 = clone.querySelector(".eli5-text");
    const citations = clone.querySelector(".citation-list");

    // ✅ Status
    if (data.covered === true) {
        status.innerText = "✅ Covered";
    } else if (data.covered === false) {
        status.innerText = "❌ Not Covered";
    } else {
        status.innerText = "⚠️ Not Mentioned";
    }

    // ✅ Content
    direct.innerText = data.direct_answer;
    eli5.innerText = data.eli5;

    // ✅ Citations
    citations.innerHTML = "";
    data.citations.forEach(c => {
        const li = document.createElement("li");
        li.innerText = c;
        citations.appendChild(li);
    });

    messages.appendChild(clone);
    messages.scrollTop = messages.scrollHeight;
}

// 🚀 Handle submit
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const query = input.value.trim();
    if (!query) return;

    addUserMessage(query);
    input.value = "";

    try {
        const res = await fetch("http://127.0.0.1:8000/api", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: query,
                filter: selectedFilter
            })
        });

        const data = await res.json();
        console.log(data);

        addBotResponse(data);

    } catch (err) {
        console.error(err);
    }
});