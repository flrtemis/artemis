'use strict';
// Static evidence playback ONLY. No model, private localhost, analytics or account API.
const buttons = Array.from(document.querySelectorAll('[data-step]'));
let captured;
const setText = (id, text) => { document.getElementById(id).textContent = text; };
function renderStep(index) {
  if (!captured?.steps?.[index]) return;
  const step = captured.steps[index];
  buttons.forEach((button, i) => button.setAttribute('aria-pressed', String(i === index)));
  setText('trace-phase', step.phase);
  setText('trace-title', step.title);
  setText('trace-explanation', step.explanation);
  setText('trace-output', typeof step.output === 'string' ? step.output : JSON.stringify(step.output, null, 2));
  setText('trace-meta', step.meta + ' · Captured sandbox evidence, not a live model response.');
}
buttons.forEach(button => button.addEventListener('click', () => renderStep(Number(button.dataset.step))));
fetch('assets/hot-tool-trace.json', {credentials: 'omit'})
  .then(response => { if (!response.ok) throw new Error('Trace unavailable'); return response.json(); })
  .then(data => { captured = data; renderStep(0); })
  .catch(() => setText('trace-meta', 'Captured trace could not load. The screenshot, setup and linked test evidence remain available; no output is simulated.'));
document.querySelectorAll('[data-copy]').forEach(button => {
  button.addEventListener('click', async () => {
    const text = document.getElementById(button.dataset.copy).textContent.trim();
    try {
      await navigator.clipboard.writeText(text);
      setText('copy-status', 'Quickstart commands copied. Initial Internet access and WSL2/Linux are required.');
      button.textContent = 'Copied';
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(document.getElementById(button.dataset.copy));
      selection.removeAllRanges(); selection.addRange(range);
      setText('copy-status', 'Automatic copying is unavailable. Commands selected; use your normal copy shortcut.');
      button.textContent = 'Selected';
    }
  });
});
