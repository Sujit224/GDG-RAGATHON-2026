const sessionId = Math.random().toString(36).substring(7);
const chatWindow = document.getElementById('chat-window');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const resultsPanel = document.getElementById('results-panel');
const scoreFill = document.getElementById('score-fill');
const scoreText = document.getElementById('score-text');
const experienceList = document.getElementById('experience-list');
const uploadBtn = document.getElementById('upload-btn');
const resumeInput = document.getElementById('resume-input');
const resetBtn = document.getElementById('reset-btn');
const loading = document.getElementById('loading');

const appendMessage = (role, text) => {
    const msg = document.createElement('div');
    msg.className = `message ${role}`;
    msg.innerHTML = text;
    chatWindow.appendChild(msg);
    chatWindow.scrollTop = chatWindow.scrollHeight;
};

const showLoading = (show) => {
    loading.classList.toggle('hidden', !show);
};

const updateUI = (data) => {
    resultsPanel.classList.remove('hidden');
    
    // Update Gauge
    const score = data.readiness_score;
    const rotation = score / 100 / 2;
    scoreFill.style.transform = `rotate(${rotation}turn)`;
    scoreText.innerText = `${Math.round(score)}/100`;

    // Update Experiences
    experienceList.innerHTML = '';
    data.top_experiences.forEach(exp => {
        const card = document.createElement('div');
        card.className = 'experience-card';
        card.innerHTML = `
            <div class="exp-header">
                <span class="company-badge">${exp.company}</span>
                <span class="similarity-badge">${exp.similarity_score}% Match</span>
            </div>
            <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.5rem;">${exp.role}</div>
            <div class="exp-text">${exp.experience_text}</div>
            <div style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--accent-color);"> Outcome: ${exp.outcome}</div>
        `;
        experienceList.appendChild(card);
    });
};

const sendMessage = async () => {
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage('user', text);
    userInput.value = '';

    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, message: text })
        });
        const data = await res.json();
        appendMessage('assistant', data.reply);

        if (data.complete) {
            analyzeSession();
        }
    } catch (err) {
        appendMessage('assistant', "Oops, something went wrong.");
    }
};

const analyzeSession = async () => {
    showLoading(true);
    try {
        const res = await fetch(`/analyze/${sessionId}`);
        const data = await res.json();
        updateUI(data);
    } catch (err) {
        console.error(err);
    } finally {
        showLoading(false);
    }
};

const uploadResume = async () => {
    const file = resumeInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    showLoading(true);
    try {
        const res = await fetch('/upload-resume', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        updateUI(data);
        appendMessage('assistant', "I've analyzed your resume and updated your profile!");
    } catch (err) {
        alert("Failed to parse resume.");
    } finally {
        showLoading(false);
    }
};

// Event Listeners
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
uploadBtn.addEventListener('click', () => resumeInput.click());
resumeInput.addEventListener('change', uploadResume);
resetBtn.addEventListener('click', () => window.location.reload());

// Initialize
(async () => {
    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, message: "INIT" })
        });
        const data = await res.json();
        chatWindow.innerHTML = ''; // Clear initial static message
        appendMessage('assistant', data.reply);
    } catch (err) { console.error(err); }
})();
