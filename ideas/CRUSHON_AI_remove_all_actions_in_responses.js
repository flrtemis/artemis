// ==UserScript==
// @name         Crushon.ai – Keep ONLY spoken line (v2)
// @namespace    http://tampermonkey.net/
// @version      2025-05-30
// @description  Removes action lines, name prefixes (asterisked or plain), asterisk text, outer quotes, and bracket text in Crushon.ai replies.
// @author       Artemis
// @match        https://crushon.ai/*
// @grant        GM_addStyle
// @run-at       document-idle
// ==/UserScript==

(function() {
  'use strict';

  /* 1) Hide <em> tags immediately */
  GM_addStyle('em { display: none !important; }');

  /* Core regexes */
  const ACTION_LINE_REGEX = /(^|\n)\s*\*{1,2}[^*]+\*{1,2}.*?(?=\n|$)/g; // whole line starts with * or **
  const ASTERISK_SEGMENT_REGEX = /\*{1,2}[^*]+\*{1,2}/g; // leftover *text* or **text**
  const NAME_PREFIX_ASTERISKED = /(^|\n)\s*\*{2}[^*]+\*{2}\s*:\s*/g; // **Name**:
  const NAME_PREFIX_PLAIN = /(^|\n)\s*[A-Z][a-zA-Z0-9_]{1,20}\s*:\s*/g; // Name:
  const ANGLE_SEGMENT_REGEX = /<[^>]+>/g; // <text> (anything inside angle brackets)

  /* Clean a single string */
  function cleanText(str) {
    // 1) Remove any full action lines
    str = str.replace(ACTION_LINE_REGEX, '$1');

    // 2) Remove name prefixes (asterisked or plain)
    str = str.replace(NAME_PREFIX_ASTERISKED, '$1');
    str = str.replace(NAME_PREFIX_PLAIN, '$1');

    // 3) Strip leftover asterisk segments
    str = str.replace(ASTERISK_SEGMENT_REGEX, '');

    // 4) Remove any <...> segments
    str = str.replace(ANGLE_SEGMENT_REGEX, '');

    // 5) Remove outermost quotes if the entire line is quoted
    str = str.trim();
    if (str.startsWith('"') && str.endsWith('"')) {
      str = str.slice(1, -1);
    }
    return str;
  }

  /**
   * Helper that walks the DOM subtree and processes all text nodes.
   */
  function walkTheDOM(node, callback) {
    // If the node is a text node, run cleanText on its value
    if (node.nodeType === Node.TEXT_NODE) {
      node.textContent = cleanText(node.textContent);
    }
    // Otherwise, recurse into its children
    for (let child = node.firstChild; child; child = child.nextSibling) {
      walkTheDOM(child, callback);
    }
  }

  /**
   * Observe chat container (or entire body) for new nodes
   */
  function observePage() {
    // Adjust the selector to match the actual element(s) where messages are inserted
    const chatContainer = document.body;
    if (!chatContainer) return;

    // Clean up everything that's already on the page first
    walkTheDOM(chatContainer);

    // Now watch for future changes (e.g., new messages)
    const observer = new MutationObserver(mutations => {
      for (const mutation of mutations) {
        if (mutation.type === 'childList') {
          // For each newly added node, run walkTheDOM on it
          for (const addedNode of mutation.addedNodes) {
            // If it’s an element node or text node, process it
            if (addedNode.nodeType === Node.ELEMENT_NODE ||
                addedNode.nodeType === Node.TEXT_NODE) {
              walkTheDOM(addedNode);
            }
          }
        }
      }
    });

    // Set observer to watch childList changes within the container
    observer.observe(chatContainer, {
      childList: true,
      subtree: true
    });
  }

  // Initialize the observer after the page is done loading
  window.addEventListener('load', observePage);
})();