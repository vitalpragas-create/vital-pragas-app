document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.signature-pad').forEach((canvas) => {
    const ctx = canvas.getContext('2d');
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    let drawing = false;

    const hiddenInput = canvas.parentElement.querySelector('.signature-data');
    const clearButton = canvas.parentElement.querySelector('.clear-signature');

    function position(e) {
      const rect = canvas.getBoundingClientRect();
      const point = e.touches ? e.touches[0] : e;
      return { x: point.clientX - rect.left, y: point.clientY - rect.top };
    }
    function start(e) {
      drawing = true;
      const p = position(e);
      ctx.beginPath();
      ctx.moveTo(p.x, p.y);
      e.preventDefault();
    }
    function move(e) {
      if (!drawing) return;
      const p = position(e);
      ctx.lineTo(p.x, p.y);
      ctx.stroke();
      if (hiddenInput) hiddenInput.value = canvas.toDataURL('image/png');
      e.preventDefault();
    }
    function end() {
      drawing = false;
      if (hiddenInput) hiddenInput.value = canvas.toDataURL('image/png');
    }

    canvas.addEventListener('mousedown', start);
    canvas.addEventListener('mousemove', move);
    canvas.addEventListener('mouseup', end);
    canvas.addEventListener('mouseleave', end);
    canvas.addEventListener('touchstart', start, { passive: false });
    canvas.addEventListener('touchmove', move, { passive: false });
    canvas.addEventListener('touchend', end);

    if (clearButton) {
      clearButton.addEventListener('click', () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (hiddenInput) hiddenInput.value = '';
      });
    }
  });
});
