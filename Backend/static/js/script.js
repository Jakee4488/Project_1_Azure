// script.js

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatWindow = document.getElementById('chat-window');
    const themeToggleBtn = document.getElementById('theme-toggle');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarToggleMobile = document.getElementById('sidebarToggleMobile');
    const sidebarOpenBtn = document.getElementById('sidebarOpen'); // Ensure this ID exists
    const voiceBtn = document.getElementById('voice-btn');
    const fileBtn = document.getElementById('file-btn');
    const fileInput = document.getElementById('file-input');
    const overlay = document.querySelector('.overlay');
    const sidebar = document.querySelector('.sidebar');
    const welcomeScreen = document.getElementById('welcome-screen');
    const body = document.body;

    let isBotResponding = false;
    let recognition;

    initializeSpeechRecognition();
    initializeEventListeners();
    loadChatHistory();
    handleResponsiveSidebar();
    loadTheme();

    // Initializes Speech Recognition if supported
    function initializeSpeechRecognition() {
        if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US';

            voiceBtn.addEventListener('click', () => {
                recognition.start();
                toggleVoiceIcon(true);
            });

            recognition.addEventListener('result', (event) => {
                userInput.value = event.results[0][0].transcript;
                toggleVoiceIcon(false);
            });

            recognition.addEventListener('end', () => toggleVoiceIcon(false));
            recognition.addEventListener('error', () => toggleVoiceIcon(false));
        } else {
            voiceBtn.style.display = 'none';
        }
    }

    function toggleVoiceIcon(isListening) {
        voiceBtn.innerHTML = isListening ? `<i class="bi bi-mic-mute-fill"></i>` : `<i class="bi bi-mic-fill"></i>`;
    }

    // Initialize Event Listeners
    function initializeEventListeners() {
        sidebarToggle.addEventListener('click', () => toggleSidebar());
        sidebarOpenBtn.addEventListener('click', () => openSidebar());
        sidebarToggleMobile.addEventListener('click', () => showSidebarMobile());
        overlay.addEventListener('click', () => closeSidebarMobile());
        themeToggleBtn.addEventListener('click', () => toggleTheme());
        window.addEventListener('resize', handleResponsiveSidebar);
        chatForm.addEventListener('submit', handleFormSubmit);
        fileBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleFileSelection);
        document.getElementById('clearChatBtn').addEventListener('click', clearChat);
        document.getElementById('newChatBtn').addEventListener('click', newChat);
    }

    function handleFormSubmit(e) {
        e.preventDefault();
        const message = userInput.value.trim();
        if (message === '') return;

        // Remove the welcome screen when the user sends their first message
        if (welcomeScreen) {
            welcomeScreen.style.display = 'none';
        }

        appendMessage('user', message);
        saveMessage('user', message);
        userInput.value = '';
        userInput.focus();

        if (!isBotResponding) {
            isBotResponding = true;
            simulateTyping(() => {
                const botResponse = getBotResponse(message);
                appendMessage('bot', botResponse);
                saveMessage('bot', botResponse);
                isBotResponding = false;
            });
        }
    }

    function handleFileSelection(e) {
        const file = e.target.files[0];
        if (file) {
            appendMessage('user', 'Sent a file:', file);
            fileInput.value = '';

            if (!isBotResponding) {
                appendMessage('bot', 'loading');
                isBotResponding = true;

                setTimeout(() => {
                    const loadingMessage = chatWindow.querySelector('.message.bot.loading');
                    if (loadingMessage) loadingMessage.remove();
                    const botResponse = getBotResponse('file');
                    appendMessage('bot', botResponse);
                    isBotResponding = false;
                }, 1000);
            }
        }
    }

    function toggleSidebar() {
        sidebar.classList.toggle('hidden');
        updateMainContentLayout();
        toggleOpenButton();
    }

    function openSidebar() {
        sidebar.classList.remove('hidden');
        updateMainContentLayout();
        toggleOpenButton();
    }

    function showSidebarMobile() {
        sidebar.classList.add('show');
        overlay.classList.add('show');
    }

    function closeSidebarMobile() {
        sidebar.classList.remove('show');
        overlay.classList.remove('show');
    }

    function handleResponsiveSidebar() {
        if (window.innerWidth <= 768) {
            sidebar.classList.add('hidden');
            updateMainContentLayout();
            toggleOpenButton();
        } else {
            sidebar.classList.remove('hidden');
            updateMainContentLayout();
            toggleOpenButton();
        }
    }

    function updateMainContentLayout() {
        const mainContent = document.querySelector('.flex-grow-1.d-flex.flex-column');
        const isSidebarHidden = sidebar.classList.contains('hidden');
        mainContent.style.marginLeft = isSidebarHidden ? '0' : '260px';
        mainContent.style.width = isSidebarHidden ? '100%' : 'calc(100% - 260px)';
    }

    // Append message to chat window
    function appendMessage(sender, text, file = null) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender, 'animate__animated', 'animate__fadeIn');

        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');

        if (file) {
            const filePreview = createFilePreview(file);
            messageContent.innerHTML = text;
            messageContent.appendChild(filePreview);
        } else {
            messageContent.innerText = text;
        }

        addTimestamp(messageContent);
        messageElement.appendChild(messageContent);
        if (sender === 'bot') addBotAvatar(messageElement);
        chatWindow.appendChild(messageElement);

        chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: 'smooth' });
        saveMessage(sender, text, file);
    }

    function addBotAvatar(messageElement) {
        const avatar = document.createElement('div');
        avatar.classList.add('avatar');
        avatar.innerText = 'B';
        messageElement.appendChild(avatar);
    }

    function addTimestamp(messageContent) {
        const timestamp = document.createElement('div');
        timestamp.classList.add('timestamp');
        const now = new Date();
        timestamp.innerText = `${now.getHours() % 12 || 12}:${now.getMinutes().toString().padStart(2, '0')} ${now.getHours() >= 12 ? 'PM' : 'AM'}`;
        messageContent.appendChild(timestamp);
    }

    function createFilePreview(file) {
        const previewContainer = document.createElement('div');
        previewContainer.classList.add('file-preview', 'mt-2');

        if (file.type.startsWith('image/')) {
            const img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            img.alt = file.name;
            img.onload = () => URL.revokeObjectURL(img.src);
            previewContainer.appendChild(img);
        } else {
            const fileIcon = document.createElement('i');
            fileIcon.classList.add('bi', 'bi-file-earmark', 'file-icon', 'me-2');
            fileIcon.style.fontSize = '2rem';
            previewContainer.appendChild(fileIcon);
        }

        const fileInfo = document.createElement('div');
        fileInfo.classList.add('file-info');
        fileInfo.innerHTML = `<span>${file.name}</span><span>${(file.size / 1024).toFixed(2)} KB</span>`;
        previewContainer.appendChild(fileInfo);

        return previewContainer;
    }

    function simulateTyping(callback) {
        const typingIndicator = document.createElement('div');
        typingIndicator.classList.add('typing-indicator');
        typingIndicator.innerHTML = `<span></span><span></span><span></span>`;
        chatWindow.appendChild(typingIndicator);

        setTimeout(() => {
            chatWindow.removeChild(typingIndicator);
            callback();
        }, 2000);
    }

    function getBotResponse(userMessage) {
        if (userMessage === 'file') return "I see you've sent a file. How can I assist you with it?";

        const responses = {
            'hello': "Hello! How can I assist you today?",
            'hi': "Hello! How can I assist you today?",
            'help': "Sure, I'm here to help! What do you need assistance with?",
            'thank': "You're welcome! Let me know if you need anything else.",
            'weather': "I can't check the weather, but you can try a weather app or website!",
            'time': `Current time is ${new Date().toLocaleTimeString()}.`
        };

        const lowerMessage = userMessage.toLowerCase();
        for (let key in responses) {
            if (lowerMessage.includes(key)) return responses[key];
        }

        const randomResponses = [
            "I'm here to help you!",
            "Can you please elaborate?",
            "That's interesting!",
            "Could you tell me more?",
            "Absolutely!",
            "Let's discuss that further.",
            "Why do you think that is?",
            "How does that make you feel?",
            "Can you provide more details?"
        ];
        return randomResponses[Math.floor(Math.random() * randomResponses.length)];
    }

    function saveMessage(sender, text, file = null) {
        const chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];
        chatHistory.push({ sender, text, timestamp: new Date().toISOString() });
        localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    }

    function loadChatHistory() {
        const chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];
        if (chatHistory.length === 0) {
            // Only show welcome message if there's no chat history
            appendMessage('bot', 'Welcome! How can I help you today?');
        } else {
            chatHistory.forEach(message => appendMessage(message.sender, message.text));
        }
    }

    function clearChat() {
        localStorage.removeItem('chatHistory');
        chatWindow.innerHTML = '';
        if (welcomeScreen) {
            welcomeScreen.style.display = 'flex';
        }
    }

    function newChat() {
        chatWindow.innerHTML = '';
        localStorage.removeItem('chatHistory');
        if (welcomeScreen) {
            welcomeScreen.style.display = 'flex';
        }
    }

    function toggleTheme() {
        const isDarkMode = document.body.classList.toggle('dark-mode');
        themeToggleBtn.innerHTML = isDarkMode ? '<i class="bi bi-sun-fill"></i>' : '<i class="bi bi-moon-fill"></i>';
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    }

    function loadTheme() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark' || (savedTheme === null && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.body.classList.add('dark-mode');
            themeToggleBtn.innerHTML = '<i class="bi bi-sun-fill"></i>';
        }
    }

    function toggleOpenButton() {
        if (sidebar.classList.contains('hidden')) {
            sidebarOpenBtn.classList.add('active');
        } else {
            sidebarOpenBtn.classList.remove('active');
        }
    }

    // Handle Suggested Prompts
    const promptButtons = document.querySelectorAll('.prompt-btn');
    promptButtons.forEach(button => {
        button.addEventListener('click', () => {
            const promptText = button.getAttribute('data-prompt');
            handlePromptAction(promptText);
        });
    });

    function handlePromptAction(promptText) {
        // Remove the welcome screen when the user clicks a suggested prompt
        if (welcomeScreen) {
            welcomeScreen.style.display = 'none';
        }
        
        // Handle predefined prompts
        appendMessage('user', promptText);
        if (promptText === 'Tell me a joke') {
            appendMessage('bot', 'Why don’t skeletons fight each other? They don’t have the guts.');
        } else if (promptText === 'Surprise me') {
            appendMessage('bot', 'Did you know? Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3000 years old and still perfectly edible.');
        } else if (promptText === 'Talk like Gen-Z') {
            appendMessage('bot', 'Yo fam, this place is lit! What’s poppin’ today?');
        }
        saveMessage('user', promptText);
        saveMessage('bot', getBotResponse(promptText));
    }
});
