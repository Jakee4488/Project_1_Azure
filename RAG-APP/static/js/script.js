// script.js - Enhanced Functionality for Dark/Light Mode and Responsive Sidebar

document.addEventListener('DOMContentLoaded', () => {
    // =======================
    // 1. Element References
    // =======================
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatWindow = document.getElementById('chat-window');
    const themeToggleBtn = document.getElementById('theme-toggle');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarToggleMobile = document.getElementById('sidebarToggleMobile'); // If applicable
    const sidebarOpenBtn = document.getElementById('sidebarOpen');
    const voiceBtn = document.getElementById('voice-btn');
    const fileBtn = document.getElementById('file-btn');
    const fileInput = document.getElementById('file-input');
    const overlay = document.querySelector('.overlay');
    const sidebar = document.querySelector('.sidebar');
    const body = document.body;
    const mainContent = document.querySelector('.flex-grow-1.d-flex.flex-column');

    // =======================
    // 2. State Variables
    // =======================
    let isBotResponding = false;
    let recognition;
    let uploadedFilename = ''; // State variable to store the filename

    // =======================
    // 3. Initialization Functions
    // =======================
    initializeSpeechRecognition();
    initializeEventListeners();
    loadChatHistory(); // Ensure this is called once
    handleResponsiveSidebar();
    loadTheme();

    // =======================
    // 4. Speech Recognition
    // =======================
    function initializeSpeechRecognition() {
        if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US';

            voiceBtn.addEventListener('click', () => {
                if (recognition) {
                    recognition.start();
                    toggleVoiceIcon(true);
                    console.log('Voice recognition started');
                }
            });

            recognition.addEventListener('result', (event) => {
                const transcript = event.results[0][0].transcript;
                userInput.value = transcript;
                console.log('Voice recognition result:', transcript);
                toggleVoiceIcon(false);
            });

            recognition.addEventListener('end', () => {
                toggleVoiceIcon(false);
                console.log('Voice recognition ended');
            });

            recognition.addEventListener('error', (event) => {
                toggleVoiceIcon(false);
                console.error('Voice recognition error:', event.error);
                alert(`Voice recognition error: ${event.error}`);
            });
        } else {
            voiceBtn.style.display = 'none';
            console.warn('Speech Recognition API not supported in this browser.');
        }
    }

    function toggleVoiceIcon(isListening) {
        voiceBtn.innerHTML = isListening
            ? `<i class="bi bi-mic-mute-fill"></i>`
            : `<i class="bi bi-mic-fill"></i>`;
    }

    // =======================
    // 5. Event Listeners
    // =======================
    function initializeEventListeners() {
        // Sidebar Toggle for Desktop
        sidebarToggle.addEventListener('click', () => toggleSidebar());

        // Sidebar Open Button for Mobile
        sidebarOpenBtn.addEventListener('click', () => openSidebar());

        // Sidebar Toggle for Mobile
        if (sidebarToggleMobile) {
            sidebarToggleMobile.addEventListener('click', () => toggleSidebarMobile());
        }

        // Overlay Click to Close Sidebar on Mobile
        overlay.addEventListener('click', () => closeSidebarMobile());

        // Theme Toggle Button
        themeToggleBtn.addEventListener('click', () => toggleTheme());

        // Window Resize Event for Responsive Sidebar
        window.addEventListener('resize', handleResponsiveSidebar);

        // Chat Form Submission
        chatForm.addEventListener('submit', handleFormSubmit); // Ensure it's attached only once

        // File Attachment
        fileBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleFileSelection);

        // Clear Chat and New Chat Buttons
        const clearChatBtn = document.getElementById('clearChatBtn');
        const newChatBtn = document.getElementById('newChatBtn');
        if (clearChatBtn) clearChatBtn.addEventListener('click', clearChat);
        if (newChatBtn) newChatBtn.addEventListener('click', newChat);
    }

    // =======================
    // 6. Chat Functionality
    // =======================
    async function handleFormSubmit(e) {
        e.preventDefault();
        const message = userInput.value.trim();
        if (message === '') return;

        appendMessage('user', message, null, true);
        userInput.value = '';
        userInput.focus();

        if (!isBotResponding) {
            isBotResponding = true;
            appendMessage('bot', 'loading', null, false);

            try {
                const response = await queryBotAPI(message);
                const loadingMessage = chatWindow.querySelector('.message.bot.loading');
                if (loadingMessage) loadingMessage.remove();
                appendMessage('bot', response.response, null, true);
            } catch (error) {
                console.error('Error:', error);
                const loadingMessage = chatWindow.querySelector('.message.bot.loading');
                if (loadingMessage) loadingMessage.remove();
                appendMessage('bot', 'Sorry, something went wrong.', null, true);
            } finally {
                isBotResponding = false;
            }
        }
    }

    // Function to query the bot API
    async function queryBotAPI(userMessage) {
        // Prepare the request payload
        const bodyData = { query: userMessage };
        if (uploadedFilename) {
            bodyData.filename = uploadedFilename; // Optional for file upload
        }

        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(bodyData) // Send the body data
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to query bot API');
        }

        const data = await response.json();
        return data;
    }

    // Handles file selection and upload
    // Handles file selection and upload
// Handles file selection and upload
function handleFileSelection(e) {
    const file = e.target.files[0];
    if (file) {
        const filename = file.name; // Get the filename from the file object
        appendMessage('user', `Sent a file: ${filename}`, file, true);
        fileInput.value = '';

        const formData = new FormData();
        formData.append('file', file);

        if (!isBotResponding) {
            isBotResponding = true;
            appendMessage('bot', 'loading', null, false);

            fetch('/api/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log('Response data:', data); // Log the entire response data
                const loadingMessage = chatWindow.querySelector('.message.bot.loading');
                if (loadingMessage) loadingMessage.remove();
                appendMessage('bot', data.message, null, true);
                if (data.filename) {
                    uploadedFilename = data.filename.replace('.pdf', ''); // Store the uploaded filename without .pdf
                    console.log('Uploaded filename:', uploadedFilename);
                } else {
                    console.error('Filename is missing in the response data');
                }
                isBotResponding = false;
            })
            .catch(error => {
                console.error('Error:', error);
                const loadingMessage = chatWindow.querySelector('.message.bot.loading');
                if (loadingMessage) loadingMessage.remove();
                appendMessage('bot', 'Failed to upload the file.', null, true);
                isBotResponding = false;
            });
        }
    }
}

    // Appends a message to the chat window
    // Added 'shouldSave' parameter to control saving to localStorage
    function appendMessage(sender, text, file = null, shouldSave = true) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);

        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');

        if (file) {
            const filePreview = createFilePreview(file);
            messageContent.innerHTML = text;
            messageContent.appendChild(filePreview);
        } else if (text === 'loading') {
            // Display typing indicator with enhanced animation
            messageElement.classList.add('loading');
            messageContent.innerHTML = `<div class="typing-indicator">
                                            <span></span><span></span><span></span>
                                        </div>`;
        } else {
            messageContent.innerText = text;
        }

        addTimestamp(messageContent);
        messageElement.appendChild(messageContent);
        if (sender === 'bot') addBotAvatar(messageElement);

        // Apply Animate.css classes based on sender
        if (sender === 'bot') {
            messageElement.classList.add('animate__bounceInRight');
        } else if (sender === 'user') {
            messageElement.classList.add('animate__fadeInLeft');
        }

        chatWindow.appendChild(messageElement);

        chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: 'smooth' });

        if (shouldSave) {
            saveMessage(sender, text, file);
        }
    }

    // Adds a bot avatar to the message element
    function addBotAvatar(messageElement) {
        const avatar = document.createElement('div');
        avatar.classList.add('avatar');
        avatar.innerText = 'B';
        messageElement.appendChild(avatar);
    }

    // Adds a timestamp to the message content
    function addTimestamp(messageContent) {
        const timestamp = document.createElement('div');
        timestamp.classList.add('timestamp');
        const now = new Date();
        timestamp.innerText = `${formatHours(now.getHours())}:${now.getMinutes().toString().padStart(2, '0')} ${now.getHours() >= 12 ? 'PM' : 'AM'}`;
        messageContent.appendChild(timestamp);
    }

    // Formats hours to 12-hour format
    function formatHours(hours) {
        return hours % 12 || 12;
    }

    // Creates a file preview element
    function createFilePreview(file) {
        const previewContainer = document.createElement('div');
        previewContainer.classList.add('file-preview', 'mt-2');

        if (file && file.type && file.type.startsWith('image/')) { // Added file.type check
            const img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            img.alt = file.name;
            img.onload = () => URL.revokeObjectURL(img.src);
            previewContainer.appendChild(img);
        } else if (file) {
            const fileIcon = document.createElement('i');
            fileIcon.classList.add('bi', 'bi-file-earmark', 'file-icon', 'me-2');
            fileIcon.style.fontSize = '2rem';
            previewContainer.appendChild(fileIcon);
        }

        if (file) {
            const fileInfo = document.createElement('div');
            fileInfo.classList.add('file-info');
            fileInfo.innerHTML = `<span>${file.name}</span><span>${(file.size / 1024).toFixed(2)} KB</span>`;
            previewContainer.appendChild(fileInfo);
        }

        return previewContainer;
    }

    // Saves a message to local storage
    function saveMessage(sender, text, file = null) {
        const chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];
        chatHistory.push({ sender, text, timestamp: new Date().toISOString(), file: file });
        localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    }

    // Loads chat history from local storage
    function loadChatHistory() {
        const chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];
        chatWindow.innerHTML = ''; // Clear chat window to prevent duplication
        chatHistory.forEach(message => {
            appendMessage(message.sender, message.text, message.file || null, false);
        });
    }

    // Clears the chat history
    function clearChat() {
        localStorage.removeItem('chatHistory');
        chatWindow.innerHTML = '';
    }

    // Starts a new chat
    function newChat() {
        clearChat();
        // If you want to initialize a new chat with a starting message, you can add it here.
    }

    // =======================
    // 7. Theme Functionality
    // =======================
    // Toggles the theme between light and dark modes
    function toggleTheme() {
        const isDarkMode = document.body.classList.toggle('dark-mode');
        themeToggleBtn.innerHTML = isDarkMode
            ? '<i class="bi bi-sun-fill me-2"></i> Light Mode'
            : '<i class="bi bi-moon-fill me-2"></i> Dark Mode';
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    }

    // Loads the saved theme from local storage
    function loadTheme() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark' || (savedTheme === null && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.body.classList.add('dark-mode');
            themeToggleBtn.innerHTML = '<i class="bi bi-sun-fill me-2"></i> Light Mode';
        } else {
            themeToggleBtn.innerHTML = '<i class="bi bi-moon-fill me-2"></i> Dark Mode';
        }
    }

    // =======================
    // 8. Sidebar Functionality
    // =======================
    function toggleSidebar() {
        sidebar.classList.toggle('hidden');
        body.classList.toggle('sidebar-hidden'); // For adjusting main content
        updateMainContentLayout();
        toggleOpenButton();
    }

    function openSidebar() {
        sidebar.classList.remove('hidden');
        body.classList.remove('sidebar-hidden');
        updateMainContentLayout();
        toggleOpenButton();
    }

    function toggleSidebarMobile() {
        sidebar.classList.toggle('show');
        overlay.classList.toggle('show');
    }

    function closeSidebarMobile() {
        sidebar.classList.remove('show');
        overlay.classList.remove('show');
    }

    function handleResponsiveSidebar() {
        if (window.innerWidth <= 768) {
            sidebar.classList.add('hidden');
            body.classList.add('sidebar-hidden');
            updateMainContentLayout();
            toggleOpenButton();
        } else {
            sidebar.classList.remove('hidden');
            body.classList.remove('sidebar-hidden');
            updateMainContentLayout();
            toggleOpenButton();
            // Ensure the sidebar is visible and overlay is hidden on desktop
            closeSidebarMobile();
        }
    }

    function updateMainContentLayout() {
        const isSidebarHidden = sidebar.classList.contains('hidden');
        if (isSidebarHidden) {
            mainContent.style.marginLeft = '0';
            mainContent.style.width = '100%';
        } else {
            mainContent.style.marginLeft = '250px';
            mainContent.style.width = 'calc(100% - 250px)';
        }
    }

    function toggleOpenButton() {
        if (sidebar.classList.contains('hidden')) {
            sidebarOpenBtn.classList.add('active');
        } else {
            sidebarOpenBtn.classList.remove('active');
        }
    }
});
