// =============================
// DOM Elements
// =============================
const chatBox = document.getElementById('chatBox');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');

// API Configuration
const API_URL = 'http://localhost:5000/api';

// Default responses
const defaultResponses = {
    greeting: "Hello! How can I assist you with your university admission questions today?",
    fallback: "I'm not sure I understand. Could you please rephrase your question? You can ask about admission requirements, deadlines, programs, or tuition fees.",
    farewell: "You're welcome! If you have more questions, feel free to ask. Good luck with your application!"
};

// =============================
// Add message to chat UI
// =============================
function addMessage(sender, message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `${sender}-message`;

    const avatar = document.createElement('img');
    avatar.className = `${sender}-avatar`;
    avatar.src = sender === 'bot'
        ? 'https://img.icons8.com/color/48/000000/robot.png'
        : 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiw0QTQsNCAwIDAsMCA4LDhBNCw0IDAgMCwwIDEyLDEyQTQsNCAwIDAsMCAxNiw4QTQsNCAwIDAsMCAxMiw0TTEyLDE0QzguNywxNCAyLDE1LjMzIDIsMThWMjBIMjJWOEMyMCw1LjMzIDE1LjMsNCAxMiw0WiIgLz48L3N2Zz4=';

    const content = document.createElement('div');
    content.className = 'message-content';

    if (Array.isArray(message)) {
        message.forEach(text => {
            const p = document.createElement('p');
            p.textContent = text;
            content.appendChild(p);
        });
    } else if (typeof message === 'object') {
        const ul = document.createElement('ul');
        ul.className = 'suggestions';

        for (const key of Object.keys(message)) {
            const li = document.createElement('li');
            li.textContent = key;
            li.onclick = () => sendMessage(key);
            ul.appendChild(li);
        }
        content.appendChild(ul);
    } else {
        content.innerHTML = message.replace(/\n/g, '<br>');
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// =============================
// RULE-BASED ADMISSION BOT
// =============================
function processAdmissionQuery(input, responses) {

    // Deadlines
    if (input.match(/deadline|last date|apply by|closing/i)) {
        if (input.match(/fall/i)) {
            return responses.deadlines.fall;
        } else if (input.match(/spring/i)) {
            return responses.deadlines.spring;
        } else if (input.match(/financial aid|fafsa|scholarship/i)) {
            return responses.deadlines.financialAid;
        } else {
            return {
                "Fall Admission": "Click for deadline",
                "Spring Admission": "Click for deadline",
                "Financial Aid": "Click for deadline"
            };
        }
    }

    // Programs
    if (input.match(/program|course|major|degree|study|offer/i)) {
        if (input.match(/undergrad|bachelor|bsc|ba|bs/i)) {
            return responses.programs.undergraduate;
        } else if (input.match(/grad|master|msc|ma|mba|phd|doctorate/i)) {
            return responses.programs.graduate;
        } else {
            return {
                "Undergraduate Programs": "Click to see options",
                "Graduate Programs": "Click to see options"
            };
        }
    }

    // Tuition & fees
    if (input.match(/tuition|fee|cost|price|financial aid|scholarship/i)) {
        if (input.match(/undergrad|bachelor|bsc|ba|bs/i)) {
            return responses.tuition.undergraduate;
        } else if (input.match(/grad|master|msc|ma|mba|phd|doctorate/i)) {
            return responses.tuition.graduate;
        } else if (input.match(/financial aid|scholarship|grant|funding/i)) {
            return responses.tuition.financialAid;
        } else {
            return {
                "Undergraduate Tuition": "Click for details",
                "Graduate Tuition": "Click for details",
                "Financial Aid": "Click for details"
            };
        }
    }

    // Contact info
    if (input.match(/contact|email|phone|address|location/i)) {
        return "You can contact our admissions office at:\n\nEmail: admissions@university.edu\nPhone: (123) 456-7890\nAddress: 123 University Ave, City, State 12345\n\nOffice hours: Mon–Fri, 9 AM – 5 PM.";
    }

    // Fallback
    return responses.fallback;
}

// =============================
// BACKEND API CALL
// =============================
async function getBotResponse(message) {
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        if (!response.ok) throw new Error("Backend error");

        const data = await response.json();
        return data.response;

    } catch (error) {
        console.error(error);
        return "I'm having trouble connecting to the server. Please try again later.";
    }
}

// =============================
// SEND MESSAGE
// =============================
async function sendMessage(message) {

    if (!message) {
        message = userInput.value.trim();
        if (!message) return;
        userInput.value = '';
    }

    // User message
    addMessage('user', message);

    // Typing indicator
    const typing = document.createElement('div');
    typing.className = 'bot-message';
    typing.innerHTML = `
        <img src="https://img.icons8.com/color/48/000000/robot.png" class="bot-avatar">
        <div class="message-content"><div class="typing"><span></span><span></span><span></span></div></div>`;
    chatBox.appendChild(typing);
    chatBox.scrollTop = chatBox.scrollHeight;

    // Get backend response
    let botReply;
    try {
        botReply = await getBotResponse(message);
    } catch {
        botReply = "Something went wrong. Try again.";
    }

    chatBox.removeChild(typing);

    addMessage('bot', botReply);
}

// =============================
// Events
// =============================
sendButton.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', e => {
    if (e.key === 'Enter') sendMessage();
});

// =============================
// Initial Greeting + Program Load
// =============================
setTimeout(() => {
    addMessage('bot', defaultResponses.greeting);

    fetch(`${API_URL}/programs`)
        .then(res => res.json())
        .then(programs => {
            if (programs && programs.length > 0) {
                const list = programs.map(p => p.name).join(', ');
                addMessage('bot', `We currently offer the following programs: ${list}.`);
            }
        })
        .catch(err => console.error("Program fetch error:", err));

}, 500);
