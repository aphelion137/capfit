// Simple interactive preview for margin/gutter
(function () {
  const PAGE_W_PX = 2480; // A4 @300DPI width
  const PREVIEW_W = 420;  // CSS width used in style.css
  const SCALE = PREVIEW_W / PAGE_W_PX;

  const marginInput = document.getElementById('margin');
  const gutterInput = document.getElementById('gutter');
  const dpiInput = document.getElementById('dpi');
  const marginRange = document.getElementById('margin-range');
  const gutterRange = document.getElementById('gutter-range');

  const pageInner = document.getElementById('page-inner');
  const gutterEl = document.getElementById('gutter-el');
  const colLeft = document.getElementById('col-left');
  const colRight = document.getElementById('col-right');

  function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

  function syncRangeToNumber(rangeEl, numEl) {
    rangeEl.value = numEl.value;
  }
  function syncNumberToRange(numEl, rangeEl) {
    numEl.value = rangeEl.value;
  }

  function updatePreview() {
    const dpi = parseInt(dpiInput.value || '300', 10);
    // Scale relative to current DPI (keep page ratio)
    const pageScale = SCALE * (dpi / 300);
    const marginPx = clamp(parseInt(marginInput.value || '0', 10), 0, 1000);
    const gutterPx = clamp(parseInt(gutterInput.value || '0', 10), 0, 1000);

    const cssMargin = Math.round(marginPx * pageScale);
    const cssGutter = Math.max(2, Math.round(gutterPx * pageScale));

    // Apply margin by shrinking page-inner inset
    pageInner.style.inset = `${cssMargin}px`;
    gutterEl.style.width = `${cssGutter}px`;

    // Grid columns: left, gutter, right with equal content widths
    // Remaining width is handled via CSS grid automatically.
  }

  // Bind events
  [marginInput, gutterInput, dpiInput].forEach((el) => el.addEventListener('input', updatePreview));
  marginRange.addEventListener('input', () => { syncNumberToRange(marginInput, marginRange); updatePreview(); });
  gutterRange.addEventListener('input', () => { syncNumberToRange(gutterInput, gutterRange); updatePreview(); });
  marginInput.addEventListener('input', () => syncRangeToNumber(marginRange, marginInput));
  gutterInput.addEventListener('input', () => syncRangeToNumber(gutterRange, gutterInput));

  // Initial paint
  syncRangeToNumber(marginRange, marginInput);
  syncRangeToNumber(gutterRange, gutterInput);
  updatePreview();
})();

