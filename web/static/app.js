// Minimal client: preview controls + file hint only
(function () {
  const PAGE_W_PX = 2480; // A4 @300DPI width
  const PREVIEW_W = 420;  // CSS width used in style.css
  const SCALE = PREVIEW_W / PAGE_W_PX;

  const marginInput = document.getElementById('margin');
  const gutterInput = document.getElementById('gutter');
  const dpiInput = document.getElementById('dpi');
  const marginRange = document.getElementById('margin-range');
  const gutterRange = document.getElementById('gutter-range');
  const fileInput = document.getElementById('file');
  const fileHint = document.getElementById('file-hint');
  const thumbList = document.getElementById('thumb-list');
  const orderWarn = document.getElementById('order-warning');
  const clearAllBtn = document.getElementById('clear-all');

  const pageInner = document.getElementById('page-inner');
  const gutterEl = document.getElementById('gutter-el');

  function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }
  function syncRangeToNumber(rangeEl, numEl) { if (rangeEl && numEl) rangeEl.value = numEl.value; }
  function syncNumberToRange(numEl, rangeEl) { if (rangeEl && numEl) numEl.value = rangeEl.value; }

  function updatePreview() {
    if (!dpiInput || !marginInput || !gutterInput || !pageInner || !gutterEl) return;
    const dpi = parseInt(dpiInput.value || '300', 10);
    const pageScale = SCALE * (dpi / 300);
    const marginPx = clamp(parseInt(marginInput.value || '0', 10), 0, 1000);
    const gutterPx = clamp(parseInt(gutterInput.value || '0', 10), 0, 1000);
    const cssMargin = Math.round(marginPx * pageScale);
    const cssGutter = Math.max(2, Math.round(gutterPx * pageScale));
    pageInner.style.inset = `${cssMargin}px`;
    gutterEl.style.width = `${cssGutter}px`;
  }

  [marginInput, gutterInput, dpiInput].forEach((el) => el && el.addEventListener('input', updatePreview));
  if (marginRange) marginRange.addEventListener('input', () => { syncNumberToRange(marginInput, marginRange); updatePreview(); });
  if (gutterRange) gutterRange.addEventListener('input', () => { syncNumberToRange(gutterInput, gutterRange); updatePreview(); });
  if (marginInput) marginInput.addEventListener('input', () => syncRangeToNumber(marginRange, marginInput));
  if (gutterInput) gutterInput.addEventListener('input', () => syncRangeToNumber(gutterRange, gutterInput));

  // Initial render
  syncRangeToNumber(marginRange, marginInput);
  syncRangeToNumber(gutterRange, gutterInput);
  updatePreview();

  // File hint only (no JS upload at all)
  // Reorder/remove support using DataTransfer when available
  let currentFiles = [];
  let dtSupported = true;

  function tryApplyToInput(files) {
    try {
      const dt = new DataTransfer();
      files.forEach((f) => dt.items.add(f));
      fileInput.files = dt.files;
      dtSupported = true;
    } catch (e) {
      dtSupported = false;
    }
    if (orderWarn) orderWarn.classList.toggle('hidden', dtSupported);
  }

  function renderThumbs() {
    if (!thumbList) return;
    thumbList.innerHTML = '';
    currentFiles.forEach((f, idx) => {
      const url = URL.createObjectURL(f);
      const item = document.createElement('div');
      item.className = 'thumb';
      item.innerHTML = `<span class="badge">${idx + 1}</span>`;
      const img = document.createElement('img');
      img.src = url;
      img.alt = `사진 ${idx + 1}`;
      img.onload = () => URL.revokeObjectURL(url);
      item.appendChild(img);
      const remove = document.createElement('button');
      remove.className = 'remove';
      remove.type = 'button';
      remove.textContent = '×';
      remove.addEventListener('click', () => {
        currentFiles.splice(idx, 1);
        if (dtSupported) tryApplyToInput(currentFiles);
        renderThumbs();
        updateHint();
      });
      item.appendChild(remove);
      const ctrls = document.createElement('div');
      ctrls.className = 'controls';
      const up = document.createElement('button');
      up.type = 'button'; up.textContent = '위로';
      up.addEventListener('click', () => {
        if (idx <= 0) return;
        const t = currentFiles[idx - 1];
        currentFiles[idx - 1] = currentFiles[idx];
        currentFiles[idx] = t;
        if (dtSupported) tryApplyToInput(currentFiles);
        renderThumbs();
      });
      const down = document.createElement('button');
      down.type = 'button'; down.textContent = '아래로';
      down.addEventListener('click', () => {
        if (idx >= currentFiles.length - 1) return;
        const t = currentFiles[idx + 1];
        currentFiles[idx + 1] = currentFiles[idx];
        currentFiles[idx] = t;
        if (dtSupported) tryApplyToInput(currentFiles);
        renderThumbs();
      });
      ctrls.appendChild(up); ctrls.appendChild(down);
      item.appendChild(ctrls);
      thumbList.appendChild(item);
    });
  }

  function updateHint() {
    const files = currentFiles;
    fileHint.textContent = files.length ? (files.length === 1 ? `선택됨: ${files[0].name}` : `${files.length}개 선택됨`) : '';
  }

  if (fileInput) {
    fileInput.addEventListener('change', () => {
      currentFiles = fileInput.files ? Array.from(fileInput.files) : [];
      tryApplyToInput(currentFiles); // detect support, also normalize order
      renderThumbs();
      updateHint();
    });
  }

  if (clearAllBtn) {
    clearAllBtn.addEventListener('click', () => {
      currentFiles = [];
      try { fileInput.value = ''; } catch {}
      renderThumbs();
      updateHint();
    });
  }
})();
