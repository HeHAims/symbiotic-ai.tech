(function () {
  const key = 'symbiotic-theme';
  const body = document.body;
  const saved = localStorage.getItem(key);
  if (saved === 'light') body.classList.add('light');

  const btn = document.querySelector('[data-theme-toggle]');
  if (btn) {
    const refresh = () => {
      const light = body.classList.contains('light');
      btn.textContent = light ? 'Dark Mode' : 'Light Mode';
      btn.setAttribute('aria-pressed', light ? 'true' : 'false');
    };
    refresh();
    btn.addEventListener('click', function () {
      body.classList.toggle('light');
      localStorage.setItem(key, body.classList.contains('light') ? 'light' : 'dark');
      refresh();
    });
  }
})();
