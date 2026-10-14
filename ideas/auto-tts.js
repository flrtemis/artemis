// ==UserScript==
// @name         AI Studio TTS v4
// @namespace    http://tampermonkey.net/
// @version      1.4
// @description  Reads AI Studio responses in real-time. Speaks on sentence ends OR when a length threshold is hit to prevent lag.
// @author       AI Assistant
// @match        https://aistudio.google.com/*
// @grant        none
// ==/UserScript==

(function () {
    'use strict';

    // --- TTS Configuration ---
    let ttsEnabled = true;
    let speechRate = 1.0;
    let selectedVoice = null;
    let spokenTextIndex = 0;
    let debounceTimer = null;

    // The "Safety Valve": If a sentence is longer than this, speak it anyway
    const MAX_CHUNK_LENGTH = 150;

    function populateVoices() {
        const voices = window.speechSynthesis.getVoices();
        if (voices.length === 0) return;

        const isBritishFemale = (v) => {
            const name = v.name.toLowerCase();
            const lang = v.lang.toLowerCase();
            const isGB = lang.includes('en-gb') || lang.includes('en_gb');
            const femaleIdentifiers = ['female', 'google uk english', 'hazel', 'sonia', 'samantha', 'alice'];
            const hasFemaleName = femaleIdentifiers.some(id => name.includes(id));
            return isGB && hasFemaleName;
        };

        selectedVoice = voices.find(isBritishFemale)
                     || voices.find(v => v.lang.includes('en-GB'))
                     || voices.find(v => v.lang.startsWith('en') && v.name.toLowerCase().includes('female'))
                     || voices.find(v => v.lang.startsWith('en'))
                     || voices[0];
    }

    window.speechSynthesis.onvoiceschanged = populateVoices;
    populateVoices();

    function speakChunk(text) {
        if (!ttsEnabled || !text || text.trim().length === 0) return;

        // Clean up markdown and artifacts
        let cleanedText = text.replace(/```[\s\S]*?```/g, ' [Code block] ');
        cleanedText = cleanedText.replace(/[*_~#`]/g, '');
        cleanedText = cleanedText.trim();

        if (!cleanedText) return;

        const utterance = new SpeechSynthesisUtterance(cleanedText);
        if (selectedVoice) utterance.voice = selectedVoice;
        utterance.rate = speechRate;
        window.speechSynthesis.speak(utterance);
    }

    function createUI() {
        const container = document.createElement('div');
        container.style = `position: fixed; bottom: 140px; right: 110px; z-index: 99999; background: #1e1e1e; color: #fff; padding: 8px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.4); font-family: sans-serif; display: flex; align-items: center; gap: 10px; cursor: move; user-select: none;`;

        const toggleBtn = document.createElement('button');
        toggleBtn.innerText = '🔊';
        toggleBtn.style = `background: #2563eb; color: white; border: none; padding: 6px 10px; border-radius: 4px; cursor: pointer; font-weight: bold;`;
        toggleBtn.onclick = (e) => {
            e.stopPropagation();
            ttsEnabled = !ttsEnabled;
            toggleBtn.innerText = ttsEnabled ? '🔊' : '🔇';
            toggleBtn.style.background = ttsEnabled ? '#2563eb' : '#6b7280';
            if (!ttsEnabled) window.speechSynthesis.cancel();
        };

        const stopBtn = document.createElement('button');
        stopBtn.innerText = '⏹';
        stopBtn.style = `background: #dc2626; color: white; border: none; padding: 6px 8px; border-radius: 4px; cursor: pointer;`;
        stopBtn.onclick = (e) => {
            e.stopPropagation();
            window.speechSynthesis.cancel();
        };

        container.appendChild(toggleBtn);
        container.appendChild(stopBtn);
        document.body.appendChild(container);

        let isDragging = false;
        let offsetX = 0, offsetY = 0;
        container.addEventListener('mousedown', (e) => {
            isDragging = true;
            const rect = container.getBoundingClientRect();
            offsetX = e.clientX - rect.left;
            offsetY = e.clientY - rect.top;
            container.style.bottom = 'auto'; container.style.right = 'auto';
            container.style.left = rect.left + 'px'; container.style.top = rect.top + 'px';
        });
        window.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            container.style.left = (e.clientX - offsetX) + 'px';
            container.style.top = (e.clientY - offsetY) + 'px';
        });
        window.addEventListener('mouseup', () => { isDragging = false; });
    }

    function processResponse() {
        const modelTurns = document.querySelectorAll('ms-chat-turn:not([is-user]), .model-turn, [data-turn-role="model"], .message-content');
        if (modelTurns.length === 0) return;

        const latestTurn = modelTurns[modelTurns.length - 1];
        const fullText = latestTurn.textContent || "";

        if (fullText.length < spokenTextIndex) {
            spokenTextIndex = 0;
        }

        const newText = fullText.slice(spokenTextIndex);
        if (!newText) return;

        // 1. Try to find a natural sentence break (. ! ? or newline)
        const sentenceEndMatch = newText.match(/.*?[.!?\n]+/);

        if (sentenceEndMatch) {
            const sentenceToSpeak = sentenceEndMatch[0];
            spokenTextIndex += sentenceToSpeak.length;
            speakChunk(sentenceToSpeak);
        }
        // 2. HYBRID FALLBACK: If the text is getting too long without a punctuation mark,
        // speak the chunk anyway so the user isn't waiting in silence.
        else if (newText.length > MAX_CHUNK_LENGTH) {
            const chunkToSpeak = newText.slice(0, MAX_CHUNK_LENGTH);
            spokenTextIndex += MAX_CHUNK_LENGTH;
            speakChunk(chunkToSpeak);
        }
    }

    const observer = new MutationObserver(() => {
        if (!ttsEnabled) return;
        clearTimeout(debounceTimer);
        // 100ms is the sweet spot for "real-time" feel without lagging the browser
        debounceTimer = setTimeout(processResponse, 100);
    });

    window.addEventListener('load', () => {
        createUI();
        observer.observe(document.body, { childList: true, subtree: true, characterData: true });
    });
})();
