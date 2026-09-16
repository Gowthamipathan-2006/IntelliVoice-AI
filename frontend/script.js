/* =========================================================
   INTELLIVOICE AI
   =========================================================
   Features:

   - Text chat
   - Voice input
   - Natural female browser TTS preference
   - Doraemon speaking animation
   - Doraemon mouth movement
   - User messages RIGHT
   - AI messages LEFT
   - Copy button
   - Share button
   - PDF upload
   - Image upload
   - File analysis
   - MongoDB history
   - Local history fallback
   - Duplicate protection
   - Mobile sidebar
   ========================================================= */


document.addEventListener("DOMContentLoaded", () => {


    /* =====================================================
       API
       ===================================================== */

    const BASE_URL =
        "http://127.0.0.1:8000";


    const CHAT_URL =
        `${BASE_URL}/chat`;


    const HISTORY_URL =
        `${BASE_URL}/history?limit=50`;


    const PDF_URL =
        `${BASE_URL}/uploadPDF`;


    const IMAGE_URL =
        `${BASE_URL}/uploadImage`;


    const LOCAL_HISTORY_KEY =
        "intellivoice_history_v2";


    /* =====================================================
       ELEMENTS
       ===================================================== */

    const messageInput =
        document.getElementById("messageInput");


    const sendButton =
        document.getElementById("sendButton");


    const chatMessages =
        document.getElementById("chatMessages");


    const mainVoiceButton =
        document.getElementById("mainVoiceButton");


    const stopVoiceButton =
        document.getElementById("stopVoiceButton");


    const historyList =
        document.getElementById("historyList");


    const headerClear =
        document.getElementById("headerClear");


    const clearButton =
        document.getElementById("clearButton");


    const mobileMenu =
        document.getElementById("mobileMenu");


    const sidebar =
        document.getElementById("sidebar");


    const overlay =
        document.getElementById("overlay");


    const doraemon =
        document.getElementById("doraemon");


    const assistantStatus =
        document.getElementById("assistantStatus");


    const assistantSubstatus =
        document.getElementById("assistantSubstatus");


    const typingIndicator =
        document.getElementById("typingIndicator");


    const pdfButton =
        document.getElementById("pdfButton");


    const imageButton =
        document.getElementById("imageButton");


    const pdfInput =
        document.getElementById("pdfInput");


    const imageInput =
        document.getElementById("imageInput");


    const filePanel =
        document.getElementById("filePanel");


    const selectedFileName =
        document.getElementById("selectedFileName");


    const removeFileButton =
        document.getElementById("removeFileButton");


    const fileQuestion =
        document.getElementById("fileQuestion");


    const analyzeFileButton =
        document.getElementById("analyzeFileButton");


    const newConversation =
        document.getElementById("newConversation");


    const anywhereDoor =
        document.getElementById("anywhereDoor");


    /* =====================================================
       STATE
       ===================================================== */

    let recognition = null;

    let isListening = false;

    let isProcessing = false;

    let selectedFile = null;

    let selectedFileType = null;

    let selectedVoice = null;

    let currentSpeechToken = 0;


    /* =====================================================
       SMALL HELPERS
       ===================================================== */

    function safeText(value) {

        if (
            value === null ||
            value === undefined
        ) {
            return "";
        }

        return String(value);
    }


    function scrollChatToBottom() {

        if (!chatMessages) {
            return;
        }

        requestAnimationFrame(() => {

            chatMessages.scrollTop =
                chatMessages.scrollHeight;

        });

    }


    /* =====================================================
       DORAEMON STATE
       ===================================================== */

    function setDoraemonReady() {

        if (!doraemon) {
            return;
        }

        doraemon.classList.remove(
            "speaking",
            "thinking"
        );

        doraemon.classList.add(
            "ready"
        );

    }


    function setDoraemonThinking() {

        if (!doraemon) {
            return;
        }

        doraemon.classList.remove(
            "speaking",
            "ready"
        );

        doraemon.classList.add(
            "thinking"
        );

    }


    function setDoraemonSpeaking() {

        if (!doraemon) {
            return;
        }

        doraemon.classList.remove(
            "ready",
            "thinking"
        );

        doraemon.classList.add(
            "speaking"
        );

    }


    /* =====================================================
       STATUS
       ===================================================== */

    function setStatus(
        main,
        sub = ""
    ) {

        if (assistantStatus) {

            assistantStatus.textContent =
                main;

        }


        if (assistantSubstatus) {

            assistantSubstatus.textContent =
                sub;

        }

    }


    /* =====================================================
       TYPING INDICATOR
       ===================================================== */

    function showTyping() {

        if (!typingIndicator) {
            return;
        }

        typingIndicator.classList.add(
            "active"
        );


        if (
            chatMessages &&
            typingIndicator.parentElement !== chatMessages
        ) {

            chatMessages.appendChild(
                typingIndicator
            );

        }


        scrollChatToBottom();

    }


    function hideTyping() {

        if (!typingIndicator) {
            return;
        }

        typingIndicator.classList.remove(
            "active"
        );

    }


    /* =====================================================
       ADD MESSAGE
       ===================================================== */

    function addMessage(
        text,
        sender = "ai"
    ) {

        if (!chatMessages) {
            return null;
        }


        const cleanText =
            safeText(text);


        const row =
            document.createElement("div");


        row.className =
            `message-row ${
                sender === "user"
                    ? "user-row"
                    : "ai-row"
            }`;


        const content =
            document.createElement("div");


        content.className =
            "message-content";


        const bubble =
            document.createElement("div");


        bubble.className =
            "message-bubble";


        bubble.textContent =
            cleanText;


        content.appendChild(
            bubble
        );


        /* =================================================
           ACTION BUTTONS
           ================================================= */

        const actions =
            document.createElement("div");


        actions.className =
            "message-actions";


        if (sender === "ai") {


            /* COPY */

            const copyButton =
                document.createElement("button");


            copyButton.className =
                "message-action";


            copyButton.type =
                "button";


            copyButton.textContent =
                "📋 Copy";


            copyButton.addEventListener(
                "click",
                async () => {

                    try {

                        await copyText(
                            cleanText
                        );


                        copyButton.textContent =
                            "✓ Copied";


                        setTimeout(() => {

                            copyButton.textContent =
                                "📋 Copy";

                        }, 1200);


                    } catch (error) {

                        console.error(
                            "Copy error:",
                            error
                        );


                        copyButton.textContent =
                            "Copy failed";


                        setTimeout(() => {

                            copyButton.textContent =
                                "📋 Copy";

                        }, 1200);

                    }

                }
            );


            /* SHARE */

            const shareButton =
                document.createElement("button");


            shareButton.className =
                "message-action";


            shareButton.type =
                "button";


            shareButton.textContent =
                "↗ Share";


            shareButton.addEventListener(
                "click",
                async () => {

                    await shareText(
                        cleanText,
                        shareButton
                    );

                }
            );


            actions.appendChild(
                copyButton
            );


            actions.appendChild(
                shareButton
            );

        }


        content.appendChild(
            actions
        );


        row.appendChild(
            content
        );


        /* Keep typing indicator at bottom */

        if (
            typingIndicator &&
            typingIndicator.parentElement === chatMessages
        ) {

            chatMessages.insertBefore(
                row,
                typingIndicator
            );

        } else {

            chatMessages.appendChild(
                row
            );

        }


        scrollChatToBottom();


        return row;

    }


    /* =====================================================
       COPY TEXT
       ===================================================== */

    async function copyText(text) {

        const value =
            safeText(text);


        if (
            navigator.clipboard &&
            window.isSecureContext
        ) {

            await navigator.clipboard.writeText(
                value
            );

            return;

        }


        const temporary =
            document.createElement("textarea");


        temporary.value =
            value;


        temporary.style.position =
            "fixed";


        temporary.style.left =
            "-9999px";


        document.body.appendChild(
            temporary
        );


        temporary.select();


        const successful =
            document.execCommand(
                "copy"
            );


        temporary.remove();


        if (!successful) {

            throw new Error(
                "Copy failed"
            );

        }

    }


    /* =====================================================
       SHARE TEXT
       ===================================================== */

    async function shareText(
        text,
        button
    ) {

        const value =
            safeText(text);


        try {

            if (
                navigator.share
            ) {

                await navigator.share({

                    title:
                        "IntelliVoice AI",

                    text:
                        value

                });

                return;

            }


            await copyText(
                value
            );


            if (button) {

                button.textContent =
                    "✓ Copied";

                setTimeout(() => {

                    button.textContent =
                        "↗ Share";

                }, 1200);

            }

        } catch (error) {

            if (
                error &&
                error.name ===
                "AbortError"
            ) {

                return;

            }


            console.error(
                "Share error:",
                error
            );

        }

    }


    /* =====================================================
       LOCAL HISTORY
       ===================================================== */

    function getLocalHistory() {

        try {

            const data =
                localStorage.getItem(
                    LOCAL_HISTORY_KEY
                );


            if (!data) {
                return [];
            }


            const parsed =
                JSON.parse(data);


            return Array.isArray(parsed)
                ? parsed
                : [];


        } catch (error) {

            console.error(
                "Local history read error:",
                error
            );


            return [];

        }

    }


    function saveLocalHistory(
        userMessage,
        aiResponse,
        action = "direct"
    ) {

        try {

            const history =
                getLocalHistory();


            history.unshift({

                user_message:
                    safeText(userMessage),

                ai_response:
                    safeText(aiResponse),

                action:
                    safeText(action),

                timestamp:
                    new Date().toISOString()

            });


            const unique =
                [];


            const keys =
                new Set();


            for (
                const item
                of history
            ) {

                const key =
                    `${item.user_message}|${item.ai_response}`;


                if (
                    keys.has(key)
                ) {

                    continue;

                }


                keys.add(key);


                unique.push(
                    item
                );

            }


            localStorage.setItem(

                LOCAL_HISTORY_KEY,

                JSON.stringify(
                    unique.slice(0, 50)
                )

            );

        } catch (error) {

            console.error(
                "Local history save error:",
                error
            );

        }

    }


    /* =====================================================
       MERGE HISTORY
       ===================================================== */

    function mergeHistory(
        backendHistory,
        localHistory
    ) {

        const all = [

            ...(Array.isArray(
                backendHistory
            )
                ? backendHistory
                : []),

            ...(Array.isArray(
                localHistory
            )
                ? localHistory
                : [])

        ];


        const seen =
            new Set();


        const result =
            [];


        for (
            const item
            of all
        ) {

            const user =
                safeText(
                    item.user_message ||
                    item.message ||
                    ""
                );


            const ai =
                safeText(
                    item.ai_response ||
                    item.response ||
                    ""
                );


            if (
                !user &&
                !ai
            ) {

                continue;

            }


            const key =
                `${user}|${ai}`;


            if (
                seen.has(key)
            ) {

                continue;

            }


            seen.add(key);


            result.push({

                ...item,

                user_message:
                    user,

                ai_response:
                    ai

            });

        }


        result.sort(
            (a, b) => {

                return (
                    new Date(
                        b.timestamp || 0
                    ) -
                    new Date(
                        a.timestamp || 0
                    )
                );

            }
        );


        return result.slice(
            0,
            50
        );

    }


    /* =====================================================
       RENDER HISTORY
       ===================================================== */

    function renderHistory(
        history
    ) {

        if (!historyList) {
            return;
        }


        historyList.innerHTML =
            "";


        if (
            !Array.isArray(history) ||
            history.length === 0
        ) {

            historyList.innerHTML =
                `<div class="history-empty">
                    No conversations yet
                </div>`;

            return;

        }


        history.forEach(
            chat => {

                const item =
                    document.createElement(
                        "button"
                    );


                item.className =
                    "history-item";


                item.type =
                    "button";


                const icon =
                    document.createElement(
                        "span"
                    );


                icon.className =
                    "history-item-icon";


                icon.textContent =
                    "💬";


                const content =
                    document.createElement(
                        "span"
                    );


                content.className =
                    "history-item-content";


                const message =
                    document.createElement(
                        "span"
                    );


                message.className =
                    "history-item-message";


                message.textContent =
                    chat.user_message ||
                    "Previous conversation";


                const time =
                    document.createElement(
                        "span"
                    );


                time.className =
                    "history-item-time";


                time.textContent =
                    formatTime(
                        chat.timestamp
                    );


                content.appendChild(
                    message
                );


                content.appendChild(
                    time
                );


                item.appendChild(
                    icon
                );


                item.appendChild(
                    content
                );


                item.addEventListener(
                    "click",
                    () => {

                        openHistoryConversation(
                            chat
                        );

                        closeSidebar();

                    }
                );


                historyList.appendChild(
                    item
                );

            }
        );

    }


    /* =====================================================
       FORMAT TIME
       ===================================================== */

    function formatTime(
        timestamp
    ) {

        if (!timestamp) {
            return "";
        }


        const date =
            new Date(timestamp);


        if (
            Number.isNaN(
                date.getTime()
            )
        ) {

            return "";

        }


        return date.toLocaleString(
            [],
            {
                month: "short",
                day: "numeric",
                hour: "numeric",
                minute: "2-digit"
            }
        );

    }


    /* =====================================================
       LOAD HISTORY
       ===================================================== */

    async function loadHistory() {

        const localHistory =
            getLocalHistory();


        try {

            const response =
                await fetch(
                    HISTORY_URL
                );


            if (!response.ok) {

                throw new Error(
                    `History HTTP ${response.status}`
                );

            }


            const data =
                await response.json();


            const backendHistory =
                Array.isArray(
                    data.history
                )
                    ? data.history
                    : [];


            const merged =
                mergeHistory(
                    backendHistory,
                    localHistory
                );


            renderHistory(
                merged
            );


            return merged;


        } catch (error) {

            console.warn(
                "Backend history unavailable. Using local history.",
                error
            );


            renderHistory(
                localHistory
            );


            return localHistory;

        }

    }


    /* =====================================================
       OPEN HISTORY
       ===================================================== */

    function openHistoryConversation(
        chat
    ) {

        stopSpeaking();


        clearChatArea();


        const user =
            safeText(
                chat.user_message ||
                chat.message ||
                ""
            );


        const ai =
            safeText(
                chat.ai_response ||
                chat.response ||
                ""
            );


        if (user) {

            addMessage(
                user,
                "user"
            );

        }


        if (ai) {

            const row =
                addMessage(
                    ai,
                    "ai"
                );


            speakAI(
                ai,
                row
            );

        }

    }


    /* =====================================================
       CLEAR CHAT AREA
       ===================================================== */

    function clearChatArea() {

        if (!chatMessages) {
            return;
        }


        chatMessages
            .querySelectorAll(
                ".message-row"
            )
            .forEach(
                element =>
                    element.remove()
            );


        hideTyping();

    }


    /* =====================================================
       NATURAL FEMALE VOICE
       ===================================================== */

    function loadVoices() {

        if (
            !("speechSynthesis" in window)
        ) {

            return;

        }


        const voices =
            window.speechSynthesis.getVoices();


        if (!voices.length) {
            return;
        }


        /*
         * Voice selection priority:
         *
         * 1. Natural female Indian English
         * 2. Microsoft female voices
         * 3. Google female voices
         * 4. Other known female voices
         * 5. Any English voice
         */


        /* =================================================
           1. INDIAN ENGLISH FEMALE
           ================================================= */

        let voice =
            voices.find(
                voice => {

                    const name =
                        safeText(
                            voice.name
                        ).toLowerCase();

                    const lang =
                        safeText(
                            voice.lang
                        ).toLowerCase();

                    return (
                        lang === "en-in" &&
                        /female|heera|priya|neerja|ravi|swara/i.test(
                            name
                        )
                    );

                }
            );


        /* =================================================
           2. MICROSOFT NATURAL FEMALE
           ================================================= */

        if (!voice) {

            voice =
                voices.find(
                    voice => {

                        const name =
                            safeText(
                                voice.name
                            ).toLowerCase();

                        return (
                            /microsoft/i.test(name) &&
                            /jenny|aria|zira|sara|sonia|female/i.test(name)
                        );

                    }
                );

        }


        /* =================================================
           3. GOOGLE FEMALE
           ================================================= */

        if (!voice) {

            voice =
                voices.find(
                    voice => {

                        const name =
                            safeText(
                                voice.name
                            ).toLowerCase();

                        return (
                            /google/i.test(name) &&
                            /female|english/i.test(name)
                        );

                    }
                );

        }


        /* =================================================
           4. KNOWN FEMALE VOICES
           ================================================= */

        if (!voice) {

            voice =
                voices.find(
                    voice => {

                        const name =
                            safeText(
                                voice.name
                            ).toLowerCase();

                        return /jenny|zira|samantha|aria|heera|priya|female/i.test(
                            name
                        );

                    }
                );

        }


        /* =================================================
           5. INDIAN ENGLISH
           ================================================= */

        if (!voice) {

            voice =
                voices.find(
                    voice =>
                        safeText(
                            voice.lang
                        ).toLowerCase()
                        .startsWith("en-in")
                );

        }


        /* =================================================
           6. US ENGLISH
           ================================================= */

        if (!voice) {

            voice =
                voices.find(
                    voice =>
                        safeText(
                            voice.lang
                        ).toLowerCase()
                        .startsWith("en-us")
                );

        }


        /* =================================================
           7. ANY ENGLISH
           ================================================= */

        if (!voice) {

            voice =
                voices.find(
                    voice =>
                        safeText(
                            voice.lang
                        ).toLowerCase()
                        .startsWith("en")
                );

        }


        selectedVoice =
            voice || null;


        if (selectedVoice) {

            console.log(
                "IntelliVoice selected voice:",
                selectedVoice.name,
                "|",
                selectedVoice.lang
            );

        } else {

            console.warn(
                "No suitable English voice found."
            );

        }

    }


    /* =====================================================
       LOAD BROWSER VOICES
       ===================================================== */

    if (
        "speechSynthesis" in window
    ) {

        loadVoices();


        window.speechSynthesis.addEventListener(
            "voiceschanged",
            loadVoices
        );

    }


    /* =====================================================
       SPEAK AI
       ===================================================== */

    function speakAI(
        text,
        messageRow = null
    ) {

        return new Promise(
            resolve => {

                const speechText =
                    safeText(text).trim();


                if (!speechText) {

                    setDoraemonReady();

                    setStatus(
                        "Ready",
                        "Tap the microphone and speak"
                    );

                    resolve();

                    return;

                }


                if (
                    !("speechSynthesis" in window)
                ) {

                    setDoraemonReady();

                    setStatus(
                        "Ready",
                        "Voice playback unavailable"
                    );

                    resolve();

                    return;

                }


                /* Cancel previous speech */

                window.speechSynthesis.cancel();


                currentSpeechToken++;


                const token =
                    currentSpeechToken;


                /*
                 * Reload voices before every speech.
                 * Chrome sometimes loads voices late.
                 */

                loadVoices();


                setStatus(
                    "Speaking...",
                    "Doraemon is answering"
                );


                setDoraemonSpeaking();


                if (messageRow) {

                    messageRow.classList.add(
                        "assistant-speaking"
                    );

                }


                const utterance =
                    new SpeechSynthesisUtterance(
                        speechText
                    );


                /* =================================================
                   SELECTED FEMALE VOICE
                   ================================================= */

                if (selectedVoice) {

                    utterance.voice =
                        selectedVoice;


                    utterance.lang =
                        selectedVoice.lang;

                } else {

                    utterance.lang =
                        "en-IN";

                }


                /* =================================================
                   SWEET + NATURAL SETTINGS
                   ================================================= */

                /*
                 * Slightly slower than normal.
                 * Helps the voice sound conversational.
                 */

                utterance.rate =
                    0.90;


                /*
                 * Slightly warm / feminine pitch.
                 */

                utterance.pitch =
                    1.06;


                /*
                 * Avoid harsh maximum volume.
                 */

                utterance.volume =
                    0.95;


                let finished =
                    false;


                function finishSpeech() {

                    if (finished) {
                        return;
                    }


                    finished = true;


                    if (
                        token !==
                        currentSpeechToken
                    ) {

                        resolve();

                        return;

                    }


                    setDoraemonReady();


                    if (messageRow) {

                        messageRow.classList.remove(
                            "assistant-speaking"
                        );

                    }


                    setStatus(
                        "Ready",
                        "Tap the microphone and speak"
                    );


                    resolve();

                }


                utterance.onstart =
                    () => {

                        if (
                            token !==
                            currentSpeechToken
                        ) {

                            return;

                        }


                        setDoraemonSpeaking();


                        setStatus(
                            "Speaking...",
                            "Doraemon is answering"
                        );

                    };


                /*
                 * Chrome sometimes pauses long speech.
                 * Resume periodically.
                 */

                const resumeTimer =
                    setInterval(
                        () => {

                            if (
                                token !==
                                currentSpeechToken
                            ) {

                                clearInterval(
                                    resumeTimer
                                );

                                return;

                            }


                            if (
                                window.speechSynthesis.speaking
                            ) {

                                window.speechSynthesis.resume();

                            }

                        },
                        500
                    );


                utterance.onend =
                    () => {

                        clearInterval(
                            resumeTimer
                        );

                        finishSpeech();

                    };


                utterance.onerror =
                    () => {

                        clearInterval(
                            resumeTimer
                        );

                        finishSpeech();

                    };


                window.speechSynthesis.speak(
                    utterance
                );

            }
        );

    }


    /* =====================================================
       STOP SPEAKING
       ===================================================== */

    function stopSpeaking() {

        currentSpeechToken++;


        if (
            "speechSynthesis" in window
        ) {

            window.speechSynthesis.cancel();

        }


        document
            .querySelectorAll(
                ".assistant-speaking"
            )
            .forEach(
                row =>
                    row.classList.remove(
                        "assistant-speaking"
                    )
            );


        setDoraemonReady();


        setStatus(
            "Ready",
            "Tap the microphone and speak"
        );

    }


    /* =====================================================
       SEND CHAT
       ===================================================== */

    async function sendMessage(
        customMessage = null
    ) {

        if (isProcessing) {
            return;
        }


        const message =
            customMessage !== null

                ? safeText(
                    customMessage
                ).trim()

                : (
                    messageInput
                        ? safeText(
                            messageInput.value
                        ).trim()
                        : ""
                );


        if (!message) {
            return;
        }


        isProcessing =
            true;


        if (messageInput) {

            messageInput.value =
                "";

            messageInput.style.height =
                "auto";

        }


        stopSpeaking();


        /* USER MESSAGE RIGHT */

        addMessage(
            message,
            "user"
        );


        showTyping();


        setDoraemonThinking();


        setStatus(
            "Thinking...",
            "IntelliVoice is processing your question"
        );


        try {

            const response =
                await fetch(
                    CHAT_URL,
                    {

                        method:
                            "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                message:
                                    message
                            })

                    }
                );


            if (!response.ok) {

                let backendError =
                    "";


                try {

                    backendError =
                        await response.text();

                } catch (_) {

                    backendError =
                        "";

                }


                throw new Error(
                    `Backend returned ${response.status}: ${backendError}`
                );

            }


            const data =
                await response.json();


            const aiResponse =
                safeText(
                    data.response ||
                    data.message ||
                    "Sorry, I could not generate a response."
                ).trim();


            const action =
                safeText(
                    data.action ||
                    "direct"
                );


            hideTyping();


            /* AI MESSAGE LEFT */

            const aiRow =
                addMessage(
                    aiResponse,
                    "ai"
                );


            /* LOCAL BACKUP */

            saveLocalHistory(
                message,
                aiResponse,
                action
            );


            /*
             * Refresh sidebar history.
             * This does NOT redraw chat messages.
             */

            await loadHistory();


            /*
             * Speak AI response.
             * Doraemon mouth moves during speech.
             */

            await speakAI(
                aiResponse,
                aiRow
            );


        } catch (error) {

            console.error(
                "Chat error:",
                error
            );


            hideTyping();


            let errorText =
                "Sorry, something went wrong while processing your request.";


            if (
                error.message ===
                "Failed to fetch"
            ) {

                errorText =
                    "I cannot reach the FastAPI backend. Please make sure the backend is running on port 8000.";

            } else if (
                error.message &&
                error.message.includes(
                    "Backend returned 429"
                )
            ) {

                errorText =
                    "The AI service is temporarily busy or has reached its quota. Please try again shortly.";

            } else if (
                error.message &&
                error.message.includes(
                    "Backend returned 500"
                )
            ) {

                errorText =
                    "The backend encountered an error. Please check the FastAPI terminal for details.";

            }


            const errorRow =
                addMessage(
                    errorText,
                    "ai"
                );


            setDoraemonReady();


            setStatus(
                "Backend connection problem",
                "Check FastAPI on port 8000"
            );


            if (errorRow) {

                await speakAI(
                    errorText,
                    errorRow
                );

            }

        } finally {

            isProcessing =
                false;

        }

    }


    /* =====================================================
       SEND BUTTON
       ===================================================== */

    if (sendButton) {

        sendButton.addEventListener(
            "click",
            () => {

                sendMessage();

            }
        );

    }


    /* =====================================================
       TEXT INPUT
       ===================================================== */

    if (messageInput) {


        /* ENTER SEND */

        messageInput.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Enter" &&
                    !event.shiftKey
                ) {

                    event.preventDefault();

                    sendMessage();

                }

            }
        );


        /* AUTO HEIGHT */

        messageInput.addEventListener(
            "input",
            () => {

                messageInput.style.height =
                    "auto";


                messageInput.style.height =
                    Math.min(
                        messageInput.scrollHeight,
                        100
                    ) + "px";

            }
        );

    }


    /* =====================================================
       SPEECH RECOGNITION
       ===================================================== */

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;


    if (
        SpeechRecognition &&
        mainVoiceButton
    ) {


        recognition =
            new SpeechRecognition();


        recognition.lang =
            "en-IN";


        recognition.continuous =
            false;


        recognition.interimResults =
            false;


        recognition.maxAlternatives =
            1;


        /* START */

        recognition.onstart =
            () => {

                isListening =
                    true;


                mainVoiceButton.classList.add(
                    "listening"
                );


                setStatus(
                    "Listening...",
                    "Speak your question"
                );

            };


        /* RESULT */

        recognition.onresult =
            event => {

                const transcript =
                    safeText(
                        event
                            .results[0][0]
                            .transcript
                    ).trim();


                if (transcript) {

                    sendMessage(
                        transcript
                    );

                }

            };


        /* ERROR */

        recognition.onerror =
            event => {

                console.error(
                    "Speech recognition error:",
                    event.error
                );


                if (
                    event.error ===
                    "not-allowed"
                ) {

                    setStatus(
                        "Microphone blocked",
                        "Allow microphone access in Chrome"
                    );


                } else if (
                    event.error ===
                    "no-speech"
                ) {

                    setStatus(
                        "I didn't hear anything",
                        "Tap the microphone and try again"
                    );


                } else if (
                    event.error ===
                    "network"
                ) {

                    setStatus(
                        "Voice network error",
                        "Please check your internet connection"
                    );


                } else {

                    setStatus(
                        "Voice input error",
                        "Please try again"
                    );

                }

            };


        /* END */

        recognition.onend =
            () => {

                isListening =
                    false;


                mainVoiceButton.classList.remove(
                    "listening"
                );


                if (!isProcessing) {

                    setStatus(
                        "Ready",
                        "Tap the microphone and speak"
                    );

                }

            };


        /* MICROPHONE CLICK */

        mainVoiceButton.addEventListener(
            "click",
            () => {

                if (isProcessing) {
                    return;
                }


                if (isListening) {

                    try {

                        recognition.stop();

                    } catch (error) {

                        console.error(
                            error
                        );

                    }

                    return;

                }


                try {

                    window.speechSynthesis.cancel();


                    loadVoices();


                    recognition.start();


                } catch (error) {

                    console.error(
                        "Recognition start error:",
                        error
                    );

                }

            }
        );

    } else if (
        mainVoiceButton
    ) {

        mainVoiceButton.disabled =
            true;


        setStatus(
            "Voice input unavailable",
            "Use Chrome for microphone input"
        );

    }


    /* =====================================================
       FILE SELECTION
       ===================================================== */

    function handleSelectedFile(
        file,
        type
    ) {

        if (!file) {
            return;
        }


        selectedFile =
            file;


        selectedFileType =
            type;


        if (selectedFileName) {

            selectedFileName.textContent =
                type === "pdf"
                    ? `📄 ${file.name}`
                    : `📸 ${file.name}`;

        }


        if (filePanel) {

            filePanel.classList.add(
                "show"
            );

        }


        if (fileQuestion) {

            fileQuestion.value =
                "";

            fileQuestion.focus();

        }

    }


    /* =====================================================
       PDF BUTTON
       ===================================================== */

    if (
        pdfButton &&
        pdfInput
    ) {

        pdfButton.addEventListener(
            "click",
            () => {

                pdfInput.click();

            }
        );

    }


    /* =====================================================
       IMAGE BUTTON
       ===================================================== */

    if (
        imageButton &&
        imageInput
    ) {

        imageButton.addEventListener(
            "click",
            () => {

                imageInput.click();

            }
        );

    }


    /* =====================================================
       PDF CHANGE
       ===================================================== */

    if (pdfInput) {

        pdfInput.addEventListener(
            "change",
            () => {

                if (
                    pdfInput.files &&
                    pdfInput.files.length
                ) {

                    handleSelectedFile(
                        pdfInput.files[0],
                        "pdf"
                    );

                }

            }
        );

    }


    /* =====================================================
       IMAGE CHANGE
       ===================================================== */

    if (imageInput) {

        imageInput.addEventListener(
            "change",
            () => {

                if (
                    imageInput.files &&
                    imageInput.files.length
                ) {

                    handleSelectedFile(
                        imageInput.files[0],
                        "image"
                    );

                }

            }
        );

    }


    /* =====================================================
       CLEAR SELECTED FILE
       ===================================================== */

    function clearSelectedFile() {

        selectedFile =
            null;


        selectedFileType =
            null;


        if (pdfInput) {

            pdfInput.value =
                "";

        }


        if (imageInput) {

            imageInput.value =
                "";

        }


        if (selectedFileName) {

            selectedFileName.textContent =
                "No file selected";

        }


        if (fileQuestion) {

            fileQuestion.value =
                "";

        }


        if (filePanel) {

            filePanel.classList.remove(
                "show"
            );

        }

    }


    if (removeFileButton) {

        removeFileButton.addEventListener(
            "click",
            clearSelectedFile
        );

    }


    /* =====================================================
       FILE ANALYSIS
       ===================================================== */

    async function analyzeSelectedFile() {

        if (!selectedFile) {

            alert(
                "Please select a PDF or image first."
            );

            return;

        }


        if (isProcessing) {
            return;
        }


        isProcessing =
            true;


        const question =
            fileQuestion
                ? safeText(
                    fileQuestion.value
                ).trim()
                : "";


        const displayQuestion =
            question ||
            `Analyze this file: ${selectedFile.name}`;


        addMessage(
            displayQuestion,
            "user"
        );


        showTyping();


        setDoraemonThinking();


        setStatus(
            "Analyzing file...",
            "Please wait"
        );


        try {

            const formData =
                new FormData();


            formData.append(
                "file",
                selectedFile
            );


            if (question) {

                formData.append(
                    "question",
                    question
                );

            }


            const endpoint =
                selectedFileType === "pdf"
                    ? PDF_URL
                    : IMAGE_URL;


            const response =
                await fetch(
                    endpoint,
                    {
                        method:
                            "POST",

                        body:
                            formData
                    }
                );


            if (!response.ok) {

                const errorText =
                    await response.text();


                throw new Error(
                    `File upload failed: ${response.status} ${errorText}`
                );

            }


            const data =
                await response.json();


            hideTyping();


            const result =
                safeText(
                    data.response ||
                    data.message ||
                    "File was uploaded successfully."
                ).trim();


            const aiRow =
                addMessage(
                    result,
                    "ai"
                );


            saveLocalHistory(
                displayQuestion,
                result,
                "file"
            );


            await loadHistory();


            await speakAI(
                result,
                aiRow
            );


            clearSelectedFile();


        } catch (error) {

            console.error(
                "File analysis error:",
                error
            );


            hideTyping();


            const errorText =
                "Sorry, I could not analyze this file. Please check that the FastAPI backend is running and that the file type is supported.";


            const errorRow =
                addMessage(
                    errorText,
                    "ai"
                );


            setStatus(
                "File analysis failed",
                "Please try again"
            );


            if (errorRow) {

                await speakAI(
                    errorText,
                    errorRow
                );

            }


        } finally {

            isProcessing =
                false;

        }

    }


    if (analyzeFileButton) {

        analyzeFileButton.addEventListener(
            "click",
            analyzeSelectedFile
        );

    }


    /* =====================================================
       FILE QUESTION ENTER
       ===================================================== */

    if (fileQuestion) {

        fileQuestion.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Enter"
                ) {

                    event.preventDefault();

                    analyzeSelectedFile();

                }

            }
        );

    }


    /* =====================================================
       SUGGESTIONS
       ===================================================== */

    document
        .querySelectorAll(
            ".suggestion"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        const message =
                            button.dataset.message ||
                            button.textContent
                                .replace(
                                    /^[^\w]+/,
                                    ""
                                )
                                .trim();


                        if (message) {

                            sendMessage(
                                message
                            );

                        }

                    }
                );

            }
        );


    /* =====================================================
       QUICK TOOLS
       ===================================================== */

    document
        .querySelectorAll(
            ".quick-tool"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        const message =
                            button.dataset.message;


                        if (message) {

                            sendMessage(
                                message
                            );

                        }

                    }
                );

            }
        );


    /* =====================================================
       STOP BUTTON
       ===================================================== */

    if (stopVoiceButton) {

        stopVoiceButton.addEventListener(
            "click",
            stopSpeaking
        );

    }


    /* =====================================================
       NEW CONVERSATION
       ===================================================== */

    function startNewConversation() {

        stopSpeaking();


        clearChatArea();


        if (messageInput) {

            messageInput.value =
                "";

            messageInput.style.height =
                "auto";

        }


        clearSelectedFile();


        setStatus(
            "Ready",
            "Tap the microphone and speak"
        );


        setDoraemonReady();


        closeSidebar();

    }


    if (newConversation) {

        newConversation.addEventListener(
            "click",
            startNewConversation
        );

    }


    /* =====================================================
       ANYWHERE DOOR
       ===================================================== */

    if (anywhereDoor) {

        anywhereDoor.addEventListener(
            "click",
            () => {

                if (messageInput) {

                    messageInput.focus();

                }

            }

        );

    }


    /* =====================================================
       CLEAR HISTORY
       ===================================================== */

    async function clearHistory() {

        stopSpeaking();


        clearChatArea();


        localStorage.removeItem(
            LOCAL_HISTORY_KEY
        );


        try {

            await fetch(
                `${BASE_URL}/history`,
                {
                    method:
                        "DELETE"
                }
            );

        } catch (error) {

            console.warn(
                "Backend history clear failed:",
                error
            );

        }


        renderHistory([]);


        setStatus(
            "Ready",
            "New conversation started"
        );


        setDoraemonReady();

    }


    if (headerClear) {

        headerClear.addEventListener(
            "click",
            clearHistory
        );

    }


    if (clearButton) {

        clearButton.addEventListener(
            "click",
            clearHistory
        );

    }


    /* =====================================================
       MOBILE SIDEBAR
       ===================================================== */

    function openSidebar() {

        if (sidebar) {

            sidebar.classList.add(
                "open"
            );

        }


        if (overlay) {

            overlay.classList.add(
                "active"
            );

        }

    }


    function closeSidebar() {

        if (sidebar) {

            sidebar.classList.remove(
                "open"
            );

        }


        if (overlay) {

            overlay.classList.remove(
                "active"
            );

        }

    }


    if (mobileMenu) {

        mobileMenu.addEventListener(
            "click",
            openSidebar
        );

    }


    if (overlay) {

        overlay.addEventListener(
            "click",
            closeSidebar
        );

    }


    /* =====================================================
       INITIAL STATE
       ===================================================== */

    setDoraemonReady();


    setStatus(
        "Ready",
        "Tap the microphone and speak"
    );


    loadHistory();


    /* =====================================================
       CONSOLE
       ===================================================== */

    console.log(
        "========================================"
    );


    console.log(
        "INTELLIVOICE AI FRONTEND READY"
    );


    console.log(
        "Chat   :",
        CHAT_URL
    );


    console.log(
        "History:",
        HISTORY_URL
    );


    console.log(
        "PDF    :",
        PDF_URL
    );


    console.log(
        "Image  :",
        IMAGE_URL
    );


    console.log(
        "========================================"
    );

});