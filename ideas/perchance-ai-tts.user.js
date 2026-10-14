// ==UserScript==
// @name         Perchance AI Reply Auto-Reader
// @namespace    perchance-ai-tts
// @version      1.0.0
// @description  Automatically reads Perchance AI helper replies aloud using your device speech.
// @match        *://perchance.org/*
// @match        *://*.perchance.org/*
// @run-at       document-idle
// @grant        none
// @noframes
// ==/UserScript==

(function () {
  'use strict';

  var SET_KEY = 'perchance-ai-tts-settings-v1';
  var settings = loadSettings();
  var spokenHashes = [];
  var debounceTimer = null;
  var lastCandidateText = '';

  function loadSettings() {
    var d = { auto: true, rate: 1.0, skipCode: true, maxChars: 2000 };
    try {
      var raw = localStorage.getItem(SET_KEY);
      if (raw) Object.assign(d, JSON.parse(raw));
    } catch (e) {}
    return d;
  }

  function saveSettings() {
    try { localStorage.setItem(SET_KEY, JSON.stringify(settings)); } catch (e) {}
  }

  function hashStr(s) {
    var h = 0;
    for (var i = 0; i < s.length; i++) {
      h = ((h << 5) - h + s.charCodeAt(i)) | 0;
    }
    return h + ':' + s.length;
  }

  function alreadySpoken(h) {
    return spokenHashes.indexOf(h) !== -1;
  }

  function markSpoken(h) {
    spokenHashes.push(h);
    if (spokenHashes.length > 40) spokenHashes.shift();
  }

  // Heuristic: find likely assistant message elements.
  // Perchance may change its editor markup, so we try several patterns
  // and fall back to "largest recent bubble that is not user input".
  function findAssistantMessages() {
    var out = [];
    var seen = new Set();

    function push(el) {
      if (!el || seen.has(el)) return;
      seen.add(el);
      out.push(el);
    }

    // 1. Explicit role markers (most reliable when present).
    var explicit = document.querySelectorAll(
      '[data-role="assistant"], [data-message-author-role="assistant"], ' +
      '[data-author="assistant"], [data-sender="assistant"], ' +
      '.ai-message, .assistant-message, .assistant, .ai-response, ' +
      '.chat-message-assistant, .msg-assistant'
    );
    for (var i = 0; i < explicit.length; i++) push(explicit[i]);

    // 2. Generic chat bubbles: look inside likely chat containers.
    var containers = document.querySelectorAll(
      '[id*="chat"], [class*="chat"], [id*="conversation"], [class*="conversation"], ' +
      '[id*="messages"], [class*="messages"], main, [role="log"]'
    );
    var userPat = /user|human|you-sent|own|prompt/i;
    for (var c = 0; c < containers.length; c++) {
      var kids = containers[c].children;
      for (var k = 0; k < kids.length; k++) {
        var el = kids[k];
        if (!(el instanceof HTMLElement)) continue;
        var cls = (el.className || '').toString() + ' ' + (el.id || '');
        if (userPat.test(cls)) continue;
        if (/input|textarea|composer|prompt-box/i.test(cls)) continue;
        var t = (el.innerText || '').trim();
        if (t.length < 30) continue;
        // Skip our own floating panel.
        if (el.id === 'ai-tts-panel') continue;
        if (el.querySelector && el.querySelector('#ai-tts-panel')) continue;
        push(el);
      }
    }
    return out;
  }

  function cleanForSpeech(text) {
    var t = text || '';
    // Remove markdown images, keep link text.
    t = t.replace(/!\[([^\]]*)\]\([^)]+\)/g, '$1');
    t = t.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
    if (settings.skipCode) {
      t = t.replace(/```[\s\S]*?```/g, ' [code block skipped] ');
      t = t.replace(/`[^`]+`/g, ' [code] ');
    }
    // Collapse whitespace.
    t = t.replace(/[ \t]+\n/g, '\n').replace(/\n{3,}/g, '\n\n').trim();
    if (t.length > settings.maxChars) {
      t = t.slice(0, settings.maxChars) + ' … [message shortened]';
    }
    return t;
  }

  function speak(text) {
    try {
      if (!('speechSynthesis' in window)) {
        toast('No speech on this browser');
        return;
      }
      var clean = cleanForSpeech(text);
      if (!clean) return;
      speechSynthesis.cancel();
      var u = new SpeechSynthesisUtterance(clean);
      u.rate = settings.rate;
      speechSynthesis.speak(u);
      markSpoken(hashStr(text));
    } catch (e) {
      toast('Speech failed');
    }
  }

  function stop() {
    try { speechSynthesis.cancel(); } catch (e) {}
  }

  function lastAssistantText() {
    var msgs = findAssistantMessages();
    for (var i = msgs.length - 1; i >= 0; i--) {
      var t = (msgs[i].innerText || '').trim();
      if (t.length >= 30) return t;
    }
    return '';
  }

  function checkForNew() {
    if (!settings.auto) return;
    var t = lastAssistantText();
    if (!t || t === lastCandidateText) return;
    lastCandidateText = t;
    if (alreadySpoken(hashStr(t))) return;
    speak(t);
    try { statusEl.textContent = 'Reading reply…'; } catch (e) {}
    setTimeout(function () {
      try { statusEl.textContent = settings.auto ? 'Auto-read on' : 'Auto-read off'; } catch (e) {}
    }, 3000);
  }

  function scheduleCheck() {
    if (debounceTimer) clearTimeout(debounceTimer);
    // Wait for streaming to settle before speaking.
    debounceTimer = setTimeout(checkForNew, 2500);
  }

  // ---- Floating panel (big, mobile friendly) ----
  var panel, statusEl, autoBtn;
  function toast(msg) {
    try {
      statusEl.textContent = msg;
      setTimeout(function () {
        statusEl.textContent = settings.auto ? 'Auto-read on' : 'Auto-read off';
      }, 2500);
    } catch (e) {}
  }

  function buildPanel() {
    panel = document.createElement('div');
    panel.id = 'ai-tts-panel';
    panel.setAttribute('role', 'region');
    panel.setAttribute('aria-label', 'AI reply reader');
    panel.style.cssText = [
      'position:fixed', 'right:12px', 'bottom:12px', 'z-index:999999',
      'background:#111', 'color:#fff', 'border-radius:14px', 'padding:10px',
      'font-size:16px', 'box-shadow:0 4px 16px rgba(0,0,0,.4)',
      'max-width:240px', 'font-family:sans-serif'
    ].join(';');

    var title = document.createElement('div');
    title.textContent = 'AI reply reader';
    title.style.cssText = 'font-weight:bold;margin-bottom:6px;';
    panel.appendChild(title);

    statusEl = document.createElement('div');
    statusEl.textContent = settings.auto ? 'Auto-read on' : 'Auto-read off';
    statusEl.style.cssText = 'opacity:.8;margin-bottom:8px;font-size:14px;';
    panel.appendChild(statusEl);

    function btn(label, fn) {
      var b = document.createElement('button');
      b.textContent = label;
      b.style.cssText = [
        'display:block', 'width:100%', 'margin:4px 0', 'padding:12px',
        'font-size:17px', 'border-radius:10px', 'border:none',
        'background:#2e7d32', 'color:#fff'
      ].join(';');
      b.addEventListener('click', fn);
      panel.appendChild(b);
      return b;
    }

    autoBtn = btn(settings.auto ? 'Turn auto-read OFF' : 'Turn auto-read ON', function () {
      settings.auto = !settings.auto;
      saveSettings();
      autoBtn.textContent = settings.auto ? 'Turn auto-read OFF' : 'Turn auto-read ON';
      toast(settings.auto ? 'Auto-read on' : 'Auto-read off');
      if (settings.auto) checkForNew();
      else stop();
    });

    btn('Read last reply now', function () {
      var t = lastAssistantText();
      if (t) speak(t);
      else toast('No AI reply found yet');
    });

    var stopBtn = btn('Stop speech', stop);
    stopBtn.style.background = '#b71c1c';

    var slower = btn('Slower', function () {
      settings.rate = Math.max(0.5, +(settings.rate - 0.1).toFixed(2));
      saveSettings();
      toast('Speed ' + settings.rate.toFixed(1));
    });
    slower.style.background = '#455a64';

    var faster = btn('Faster', function () {
      settings.rate = Math.min(2.0, +(settings.rate + 0.1).toFixed(2));
      saveSettings();
      toast('Speed ' + settings.rate.toFixed(1));
    });
    faster.style.background = '#455a64';

    document.documentElement.appendChild(panel);
  }

  function start() {
    buildPanel();
    var obs = new MutationObserver(scheduleCheck);
    try {
      obs.observe(document.body, { childList: true, subtree: true, characterData: true });
    } catch (e) {
      try { obs.observe(document.documentElement, { childList: true, subtree: true }); } catch (e2) {}
    }
    // First check shortly after load.
    setTimeout(checkForNew, 3000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
