document.addEventListener('DOMContentLoaded', function () {
    const chatInput = document.getElementById('chatInput');
    const chatSend = document.getElementById('chatSend');
    const chatMessages = document.getElementById('chatMessages');

    if (!chatInput || !chatSend) return;

    function addMessage(text, isUser) {
        const div = document.createElement('div');
        div.className = 'message ' + (isUser ? 'user-message' : 'ai-message');
        div.innerHTML =
            '<div class="message-avatar"><i class="fas fa-' + (isUser ? 'user' : 'robot') + '"></i></div>' +
            '<div class="message-content">' + escapeHtml(text) + '</div>';
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async function sendMessage() {
        const question = chatInput.value.trim();
        if (!question) return;

        addMessage(question, true);
        chatInput.value = '';
        chatSend.disabled = true;

        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message ai-message';
        loadingDiv.id = 'loadingMsg';
        loadingDiv.innerHTML =
            '<div class="message-avatar"><i class="fas fa-robot"></i></div>' +
            '<div class="message-content"><i class="fas fa-spinner fa-spin"></i> Thinking...</div>';
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const body = { question: question };
            if (window.CHAT_CONFIG.materialId) body.material_id = window.CHAT_CONFIG.materialId;

            const res = await fetch(window.CHAT_CONFIG.askUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });

            const data = await res.json();
            loadingDiv.remove();

            if (data.error) {
                addMessage(data.error, false);
            } else {
                let answer = data.answer;
                if (data.sources && data.sources.length > 0) {
                    const srcText = data.sources
                        .map(function (s) { return s.title + ', Page ' + s.page; })
                        .join('; ');
                    answer += '\n\nSources: ' + srcText;
                }
                addMessage(answer, false);
            }
        } catch (e) {
            loadingDiv.remove();
            addMessage('Failed to get a response. Please try again.', false);
        }

        chatSend.disabled = false;
        chatInput.focus();
    }

    chatSend.addEventListener('click', sendMessage);
    chatInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') sendMessage();
    });
});
