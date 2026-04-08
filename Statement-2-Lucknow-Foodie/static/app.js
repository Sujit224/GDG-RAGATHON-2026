/* =============================================
   GOURMET GUIDE — JavaScript Application
   RAG-Powered Restaurant Recommendation Bot
   ============================================= */

// ── DOM References ──
const chatMessages   = document.getElementById('chatMessages');
const userInput      = document.getElementById('userInput');
const sendBtn        = document.getElementById('sendBtn');
const cardsTrack     = document.getElementById('cardsTrack');
const heroSubtitle   = document.getElementById('heroSubtitle');
const prevBtn        = document.getElementById('prevBtn');
const nextBtn        = document.getElementById('nextBtn');
const cardsWrapper   = document.getElementById('cardsWrapper');

// ── Configure Marked.js ──
marked.setOptions({ breaks: true, gfm: true });

// ── Utility: Scroll chat to bottom ──
function scrollChat() {
    chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: 'smooth' });
}

// ── Utility: Set input value and send ──
function setQuery(text) {
    userInput.value = text;
    handleSend();
}
window.setQuery = setQuery; // expose to inline onclick

// ── Append User Message ──
function appendUserMessage(text) {
    const el = document.createElement('div');
    el.className = 'chat-message user-msg slide-up';
    el.innerHTML = `
        <div class="message-bubble user-bubble">
            <p>${escapeHtml(text)}</p>
        </div>
    `;
    chatMessages.appendChild(el);
    scrollChat();
}

// ── Show Typing Indicator ──
function showTyping() {
    const tpl = document.getElementById('typingTemplate');
    const clone = tpl.content.cloneNode(true);
    const el = document.createElement('div');
    el.appendChild(clone);
    const msg = el.firstElementChild;
    msg.id = 'typingIndicator';
    chatMessages.appendChild(msg);
    scrollChat();
    return msg;
}

// ── Append Bot Message with Sources ──
function appendBotMessage(text, sources) {
    const el = document.createElement('div');
    el.className = 'chat-message bot-msg slide-up';

    const formattedText = marked.parse(text);
    let sourceCardsHTML = '';

    if (sources && sources.length > 0) {
        const cards = sources.map(src => buildSourceMiniCard(src)).join('');
        sourceCardsHTML = `<div class="source-mini-cards">${cards}</div>`;
    }

    el.innerHTML = `
        <div class="bot-avatar"><i class="ph-fill ph-robot"></i></div>
        <div class="message-bubble bot-bubble">
            <div class="bot-response-text">${formattedText}</div>
            ${sourceCardsHTML}
        </div>
    `;
    chatMessages.appendChild(el);
    scrollChat();

    // Also update the right slider
    if (sources && sources.length > 0) {
        updateSlider(sources, text);
    }
}

// ── Build Source Mini-Card HTML ──
function buildSourceMiniCard(src) {
    const isVeg = src.cuisine && (src.cuisine.includes('Veg') || src.cuisine.join('').toLowerCase().includes('veg'));
    const isNonVeg = src.cuisine && src.cuisine.includes('Non-veg');
    const budgetLabel = src.budget || '₹';
    const firstDish = Array.isArray(src.signature_dishes) ? src.signature_dishes[0] : (src.signature_dishes || '').split(',')[0];
    const vegTag = isNonVeg && !isVeg
        ? `<span class="smtag smtag-nonveg">Non-Veg</span>`
        : `<span class="smtag smtag-veg">Veg</span>`;
    const budgetTag = `<span class="smtag smtag-budget">${budgetLabel}</span>`;

    return `
    <div class="source-mini-card" onclick="highlightCard('${escapeHtml(src.name)}')">
        <div class="smcard-header">
            <span class="smcard-name">${escapeHtml(src.name)}</span>
            <span class="smcard-rating">⭐ ${src.rating || ''}</span>
        </div>
        <div class="smcard-dish">${escapeHtml(firstDish)} • ${escapeHtml(src.location || '')}</div>
        <div class="smcard-meta">${vegTag}${budgetTag}</div>
    </div>`;
}

// ── HTML Escape ──
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

// ── Highlight a specific card on the slider ──
function highlightCard(name) {
    const cards = cardsTrack.querySelectorAll('.restaurant-card[data-name]');
    cards.forEach(card => {
        if (card.dataset.name === name) {
            card.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
            card.style.boxShadow = '0 0 0 2px #f5c842, 0 40px 80px rgba(0,0,0,0.6)';
            setTimeout(() => { card.style.boxShadow = ''; }, 2000);
        }
    });
}

// ── Image Map for Dishes ──
const DISH_IMAGE_MAP = {
    'galauti kebab':    '/static/images/galauti_kebab.png',
    'basket chaat':     '/static/images/basket_chaat.png',
    'mutton biryani':   '/static/images/mutton_biryani.png',
    'kulhad chai':      '/static/images/kulhad_chai.png',
    'woodfired pizza':  '/static/images/woodfired_pizza.png',
    'kulfi falooda':    '/static/images/kulfi_falooda.png',
    'truffle pasta':    '/static/images/truffle_pasta.png',
    'glazed salmon':    '/static/images/glazed_salmon.png',
};

const RESTAURANT_IMAGE_MAP = {
    'Tunday Kababi':            '/static/images/galauti_kebab.png',
    'Royal Cafe':               '/static/images/basket_chaat.png',
    'Idris Ki Biryani':         '/static/images/mutton_biryani.png',
    'Lalla Biryani':            '/static/images/mutton_biryani.png',
    'Sky Glass Brewing Co.':    '/static/images/woodfired_pizza.png',
    'Sharma Ji Ki Chai':        '/static/images/kulhad_chai.png',
    'Prakash Ki Kulfi':         '/static/images/kulfi_falooda.png',
    'The Cherry Tree Cafe':     '/static/images/truffle_pasta.png',
};

function getCardImage(src) {
    // Try restaurant name first
    if (RESTAURANT_IMAGE_MAP[src.name]) return RESTAURANT_IMAGE_MAP[src.name];
    // Then try signature dishes
    const dishes = Array.isArray(src.signature_dishes) ? src.signature_dishes : (src.signature_dishes || '').split(',');
    for (const dish of dishes) {
        const key = dish.trim().toLowerCase();
        if (DISH_IMAGE_MAP[key]) return DISH_IMAGE_MAP[key];
    }
    // Fallback: use loremflickr with the dish name
    const term = dishes[0] ? encodeURIComponent(dishes[0].trim().replace(/\s+/g, ',')) : 'indian,food';
    return `https://loremflickr.com/600/800/food,indian,${term}?t=${Math.random()}`;
}

// ── Build Full Slider Card HTML ──
function buildSliderCard(src, idx) {
    const imgUrl = getCardImage(src);
    const cuisines = Array.isArray(src.cuisine) ? src.cuisine : [src.cuisine || ''];
    const isVeg = cuisines.includes('Veg') && !cuisines.includes('Non-veg');
    const isNonVeg = cuisines.includes('Non-veg');
    const vibes = Array.isArray(src.vibe) ? src.vibe : [src.vibe || ''];
    const dishes = Array.isArray(src.signature_dishes) ? src.signature_dishes : (src.signature_dishes || '').split(',');

    // Build tags
    let tagHTML = '';
    if (isVeg && !isNonVeg) tagHTML += `<span class="tag tag-veg">Pure Veg</span>`;
    if (isNonVeg) tagHTML += `<span class="tag tag-nonveg">Non-Veg</span>`;
    if (vibes.includes('Iconic') || vibes.includes('Historic')) tagHTML += `<span class="tag tag-iconic">Iconic</span>`;
    if (vibes.includes('Party')) tagHTML += `<span class="tag tag-party">Party</span>`;
    if (vibes.includes('Premium') || vibes.includes('Fine Dining')) tagHTML += `<span class="tag tag-premium">Premium</span>`;
    if (vibes.includes('Student friendly') || vibes.includes('Student favorite')) tagHTML += `<span class="tag tag-student">Campus Fav</span>`;

    const displayDish = dishes[0] ? dishes[0].trim() : '';

    return `
    <div class="restaurant-card slide-up" data-name="${escapeHtml(src.name)}" style="animation-delay:${idx * 0.08}s"
         onclick="showCardDetail(${idx})">
        <div class="card-img" style="background-image:url('${imgUrl}')"></div>
        <div class="card-shine"></div>
        <div class="card-body">
            <div class="card-tags">${tagHTML || '<span class="tag tag-classic">Local Gem</span>'}</div>
            <h3 class="card-restaurant">${escapeHtml(src.name)}</h3>
            <p class="card-dish">${escapeHtml(displayDish)}</p>
            <div class="card-meta">
                <span class="card-location">
                    <i class="ph ph-map-pin"></i> ${escapeHtml(src.location || '')}
                </span>
                <span class="card-rating">⭐ ${src.rating || ''}</span>
                <span class="card-budget">${src.budget || '₹'}</span>
            </div>
        </div>
    </div>`;
}

// ── Update Right Slider with RAG Results ──
function updateSlider(sources, queryContext) {
    // Update hero subtitle
    if (queryContext) {
        const short = queryContext.length > 60 ? queryContext.slice(0, 57) + '...' : queryContext;
        heroSubtitle.textContent = `Recommendations for: "${short}"`;
    }

    // Add skeleton loaders first
    let html = sources.map((_, i) => `
        <div class="skeleton-card slide-up" style="animation-delay:${i*0.08}s">
            <div class="skeleton-img" style="height:65%"></div>
            <div class="skeleton-body">
                <div class="skeleton-line medium"></div>
                <div class="skeleton-line short"></div>
                <div class="skeleton-line short"></div>
            </div>
        </div>
    `).join('');
    html += `<div class="restaurant-card cta-card slide-up">
        <div class="cta-inner">
            <div class="cta-icon"><i class="ph ph-chat-circle-dots"></i></div>
            <p>Ask me more to refine results</p>
            <button onclick="document.getElementById('userInput').focus()">Refine →</button>
        </div>
    </div>`;

    cardsTrack.innerHTML = html;

    // Replace skeletons with real cards after brief delay
    setTimeout(() => {
        const realCards = sources.map((src, i) => buildSliderCard(src, i)).join('');
        const ctaCard = `<div class="restaurant-card cta-card slide-up" style="animation-delay:${sources.length*0.08}s">
            <div class="cta-inner">
                <div class="cta-icon"><i class="ph ph-chat-circle-dots"></i></div>
                <p>Ask me more to discover hidden gems</p>
                <button onclick="document.getElementById('userInput').focus()">Ask Again →</button>
            </div>
        </div>`;
        cardsTrack.innerHTML = realCards + ctaCard;
        cardsTrack.scrollTo({ left: 0, behavior: 'smooth' });
    }, 600);
}

// ── Main Send Handler ──
async function handleSend() {
    const query = userInput.value.trim();
    if (!query) return;

    userInput.value = '';
    sendBtn.classList.add('loading');

    appendUserMessage(query);
    const typingEl = showTyping();

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });

        typingEl.remove();

        if (res.ok) {
            const data = await res.json();
            appendBotMessage(data.answer, data.sources);
        } else {
            appendBotMessage("⚠️ I'm having trouble connecting right now. Please try again in a moment.", []);
        }
    } catch (err) {
        typingEl.remove();
        appendBotMessage("⚠️ Network error — please ensure the server is running and try again.", []);
        console.error('Chat error:', err);
    } finally {
        sendBtn.classList.remove('loading');
        userInput.focus();
    }
}

// ── Slider Navigation ──
prevBtn.addEventListener('click', () => {
    cardsTrack.scrollBy({ left: -340, behavior: 'smooth' });
});
nextBtn.addEventListener('click', () => {
    cardsTrack.scrollBy({ left: 340, behavior: 'smooth' });
});

// ── Send Button + Enter Key ──
sendBtn.addEventListener('click', handleSend);
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
});

// ── Card Detail Popup (Optional Enhancement) ──
window.showCardDetail = function(idx) {
    // No-op for now; cards are already informative.
};
window.highlightCard = highlightCard;

// ── Focus input on page load ──
window.addEventListener('load', () => {
    userInput.focus();
});
