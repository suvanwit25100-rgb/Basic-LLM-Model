/* ================================================================
   Space & Physics Tutor — Frontend Logic
   ================================================================ */

// --- DOM refs -------------------------------------------------------
const chatMessages  = document.getElementById('chatMessages');
const messageInput  = document.getElementById('messageInput');
const sendBtn       = document.getElementById('sendBtn');
const welcomeCard   = document.getElementById('welcomeCard');
const canvas        = document.getElementById('starfield');
const ctx           = canvas.getContext('2d');

// --- State ----------------------------------------------------------
let isWaiting = false;

// ====================================================================
//  STARFIELD ANIMATION
// ====================================================================
const stars = [];
const shootingStars = [];
const STAR_COUNT = 260;
const SHOOTING_INTERVAL = 4000; // ms between shooting stars

function resizeCanvas() {
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
}

function createStar() {
    return {
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 1.6 + 0.3,
        alpha: Math.random(),
        dAlpha: (Math.random() * 0.008 + 0.003) * (Math.random() < 0.5 ? 1 : -1),
        hue: Math.random() < 0.3 ? 220 : Math.random() < 0.5 ? 260 : 200,
    };
}

function initStars() {
    stars.length = 0;
    for (let i = 0; i < STAR_COUNT; i++) stars.push(createStar());
}

function spawnShootingStar() {
    shootingStars.push({
        x: Math.random() * canvas.width * 0.8,
        y: Math.random() * canvas.height * 0.4,
        len: Math.random() * 80 + 40,
        speed: Math.random() * 8 + 6,
        alpha: 1,
        angle: Math.PI / 4 + (Math.random() - 0.5) * 0.3,
    });
}

function drawStars() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Background gradient
    const bg = ctx.createRadialGradient(
        canvas.width / 2, canvas.height / 2, 0,
        canvas.width / 2, canvas.height / 2, canvas.width * 0.8
    );
    bg.addColorStop(0, '#0d1229');
    bg.addColorStop(0.5, '#080c1a');
    bg.addColorStop(1, '#050810');
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Nebula smudge
    const neb = ctx.createRadialGradient(
        canvas.width * 0.75, canvas.height * 0.25, 0,
        canvas.width * 0.75, canvas.height * 0.25, canvas.width * 0.35
    );
    neb.addColorStop(0, 'rgba(99, 102, 241, 0.04)');
    neb.addColorStop(0.5, 'rgba(139, 92, 246, 0.02)');
    neb.addColorStop(1, 'transparent');
    ctx.fillStyle = neb;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Stars
    for (const s of stars) {
        s.alpha += s.dAlpha;
        if (s.alpha <= 0.15 || s.alpha >= 1) s.dAlpha *= -1;
        s.alpha = Math.max(0.15, Math.min(1, s.alpha));

        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${s.hue}, 80%, 85%, ${s.alpha})`;
        ctx.fill();

        // Glow for brighter stars
        if (s.r > 1.2) {
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r * 3, 0, Math.PI * 2);
            ctx.fillStyle = `hsla(${s.hue}, 80%, 80%, ${s.alpha * 0.08})`;
            ctx.fill();
        }
    }

    // Shooting stars
    for (let i = shootingStars.length - 1; i >= 0; i--) {
        const ss = shootingStars[i];
        const dx = Math.cos(ss.angle) * ss.speed;
        const dy = Math.sin(ss.angle) * ss.speed;
        ss.x += dx;
        ss.y += dy;
        ss.alpha -= 0.012;

        const tailX = ss.x - Math.cos(ss.angle) * ss.len;
        const tailY = ss.y - Math.sin(ss.angle) * ss.len;

        const grad = ctx.createLinearGradient(tailX, tailY, ss.x, ss.y);
        grad.addColorStop(0, `rgba(255, 255, 255, 0)`);
        grad.addColorStop(1, `rgba(200, 210, 255, ${ss.alpha})`);

        ctx.beginPath();
        ctx.moveTo(tailX, tailY);
        ctx.lineTo(ss.x, ss.y);
        ctx.strokeStyle = grad;
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Head glow
        ctx.beginPath();
        ctx.arc(ss.x, ss.y, 2, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(220, 230, 255, ${ss.alpha})`;
        ctx.fill();

        if (ss.alpha <= 0 || ss.x > canvas.width + 50 || ss.y > canvas.height + 50) {
            shootingStars.splice(i, 1);
        }
    }

    requestAnimationFrame(drawStars);
}

// Init starfield
resizeCanvas();
initStars();
drawStars();
window.addEventListener('resize', () => { resizeCanvas(); initStars(); });
setInterval(spawnShootingStar, SHOOTING_INTERVAL);

// ====================================================================
//  CHAT LOGIC
// ====================================================================

/** Append a message bubble to the chat area. */
function appendMessage(role, text) {
    // Hide welcome card on first real message
    if (welcomeCard) welcomeCard.style.display = 'none';

    const wrapper = document.createElement('div');
    wrapper.classList.add('message', role);

    const avatar = document.createElement('div');
    avatar.classList.add('message-avatar');
    avatar.textContent = role === 'user' ? '👤' : '🪐';

    const bubble = document.createElement('div');
    bubble.classList.add('message-content');
    bubble.textContent = text;

    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    chatMessages.appendChild(wrapper);

    scrollToBottom();
}

/** Show the loading / thinking indicator. */
function showLoading() {
    const el = document.createElement('div');
    el.classList.add('loading-indicator');
    el.id = 'loadingIndicator';
    el.innerHTML = `
        <div class="loading-dots">
            <span></span><span></span><span></span>
        </div>
        <span class="loading-text">Tutor is thinking…</span>
    `;
    chatMessages.appendChild(el);
    scrollToBottom();
}

/** Remove the loading indicator. */
function hideLoading() {
    const el = document.getElementById('loadingIndicator');
    if (el) el.remove();
}

/** Scroll the chat to the bottom. */
function scrollToBottom() {
    requestAnimationFrame(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
}

/** Auto-resize the textarea as the user types. */
function autoResize() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
}

/** Send the user's message to the backend. */
async function sendMessage(text) {
    const message = (text || messageInput.value).trim();
    if (!message || isWaiting) return;

    isWaiting = true;
    sendBtn.disabled = true;
    messageInput.value = '';
    autoResize();

    appendMessage('user', message);
    showLoading();

    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
        });

        hideLoading();

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.error || `Server error ${res.status}`);
        }

        const data = await res.json();
        appendMessage('tutor', data.response);
    } catch (err) {
        hideLoading();
        appendMessage('error', `⚠ ${err.message || 'Something went wrong. Is the server running?'}`);
    } finally {
        isWaiting = false;
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

// --- Event listeners ------------------------------------------------
sendBtn.addEventListener('click', () => sendMessage());

messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

messageInput.addEventListener('input', autoResize);

// Suggestion chips
document.querySelectorAll('.chip').forEach((chip) => {
    chip.addEventListener('click', () => {
        const q = chip.getAttribute('data-q');
        if (q) sendMessage(q);
    });
});

// Focus input on load
messageInput.focus();
