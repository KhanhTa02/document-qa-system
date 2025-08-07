let isLoading = false;
let startTime = 0;

window.onload = function() {
    loadPdfInfo();
};

async function loadPdfInfo() {
    try {
        const response = await fetch('/api/pdf_info');
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('pdfInfo').innerHTML = `<strong>Error:</strong> ${data.error}`;
        } else {
            document.getElementById('pdfInfo').innerHTML = `<strong>Document:</strong> ${data.file_name}`;
            
            const iframe = document.getElementById('pdfIframe');
            if (iframe && data.file_name) {
                iframe.src = `/pdf/${data.file_name}`;
            }
        }
    } catch (error) {
        document.getElementById('pdfInfo').innerHTML = `<strong>Error:</strong> Failed to load document info`;
    }
}

async function askQuestion(questionText = null) {
    if (isLoading) return;

    const question = questionText || document.getElementById('questionInput').value.trim();
    if (!question) return;

    addUserMessage(question);
    isLoading = true;
    startTime = Date.now();
    showLoading();

    if (!questionText) {
        document.getElementById('questionInput').value = '';
    }

    try {
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });

        const data = await response.json();
        
        if (data.error) {
            addAIMessage(`Error: ${data.error}`, 'error');
        } else {
            const answerHtml = formatAnswer(data);
            addAIMessage(answerHtml, 'answer');
        }

    } catch (error) {
        addAIMessage(`Network error: ${error.message}`, 'error');
    } finally {
        isLoading = false;
        hideLoading();
    }
}

function formatAnswer(data) {
    const sources = data.sources || [];
    const responseTime = ((Date.now() - startTime) / 1000).toFixed(2);
    
    return `
        <div class="answer-text">${data.answer}</div>
        <button class="btn btn-secondary" onclick="toggleDetails(this)">Show Details</button>
        <div class="answer-meta">
            <strong>Time:</strong> ${responseTime}s<br>
            <strong>Sources:</strong> ${sources.join(', ') || 'No sources'}
        </div>
    `;
}

function toggleDetails(button) {
    const metaDiv = button.nextElementSibling;
    if (metaDiv.classList.contains('show')) {
        metaDiv.classList.remove('show');
        button.textContent = 'Show Details';
    } else {
        metaDiv.classList.add('show');
        button.textContent = 'Hide Details';
    }
}

function addUserMessage(question) {
    const chatMessages = document.getElementById('chatMessages');
    const welcomeMessage = document.getElementById('welcomeMessage');
    
    if (welcomeMessage && !welcomeMessage.classList.contains('hidden')) {
        welcomeMessage.classList.add('hidden');
    }
    
    const questionDiv = document.createElement('div');
    questionDiv.className = 'message question';
    questionDiv.innerHTML = `<div class="question-text">${question}</div>`;
    chatMessages.appendChild(questionDiv);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addAIMessage(answer, type) {
    const chatMessages = document.getElementById('chatMessages');
    
    const answerDiv = document.createElement('div');
    answerDiv.className = `message answer ${type === 'error' ? 'error' : ''}`;
    answerDiv.innerHTML = `<div class="answer-content">${answer}</div>`;
    chatMessages.appendChild(answerDiv);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showLoading() {
    const chatMessages = document.getElementById('chatMessages');
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loadingMessage';
    loadingDiv.className = 'message answer loading';
    loadingDiv.innerHTML = `<div class="spinner"></div>`;
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideLoading() {
    const loadingMessage = document.getElementById('loadingMessage');
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const questionInput = document.getElementById('questionInput');
    if (questionInput) {
        questionInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                askQuestion();
            }
        });
    }
}); 