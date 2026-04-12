const chatHistory = document.getElementById('chatHistory');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const sliderTrack = document.getElementById('sliderTrack');

const API_URL = "http://127.0.0.1:8000/chat";

// Basic Markdown/HTML sanitization to just allow b, i, br
function createChatBubble(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${sender}`;
    
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    
    // Set innerHTML (assumes backend sends sanitized safe basic HTML)
    bubble.innerHTML = text;
    
    msgDiv.appendChild(bubble);
    chatHistory.appendChild(msgDiv);
    
    // Scroll to bottom
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function updateSlider(dishes) {
    if (!dishes || dishes.length === 0) return;
    
    sliderTrack.innerHTML = ''; // Clear current
    
    dishes.forEach(dish => {
        const card = document.createElement('div');
        card.className = 'card';
        
        card.innerHTML = `
            <img src="${dish.image_url}" alt="${dish.dish_name}" onerror="this.src='public/images/dish_1.png'">
            <div class="card-content">
              <h3>${dish.dish_name}</h3>
            </div>
            <div class="glow"></div>
        `;
        
        sliderTrack.appendChild(card);
    });
    
    // Auto scroll to start
    sliderTrack.scrollTo({left: 0, behavior: 'smooth'});
}

async function handleSend() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Echo user
    createChatBubble(text, 'user');
    chatInput.value = '';

    // Add loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-message bot loading';
    loadingDiv.innerHTML = `<div class="bubble">...</div>`;
    chatHistory.appendChild(loadingDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: text })
        });
        
        const data = await response.json();
        
        // Remove loading
        chatHistory.removeChild(loadingDiv);
        
        // Add bot message
        createChatBubble(data.reply, 'bot');
        
        // Update slider
        if (data.dishes) {
            updateSlider(data.dishes);
        }
        
    } catch (error) {
        console.error("Error:", error);
        chatHistory.removeChild(loadingDiv);
        createChatBubble("Sorry, I'm having trouble connecting to the food network right now.", 'bot');
    }
}

sendBtn.addEventListener('click', handleSend);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSend();
    }
});
