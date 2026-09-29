/* Light/dark toggle for the .mode button in the nav.
   The inline script in each page's <head> sets data-mode before first paint;
   this file only wires up the button. Choice is remembered under localStorage "vc-mode". */
(function () {
  var root = document.documentElement;
  var btn = document.querySelector('.mode');
  if (!btn) return;
  var meta = document.querySelector('meta[name="theme-color"]');
  var bar = { light: '#f4f3ee', dark: '#0b0b0c' };
  function saved() { try { return localStorage.getItem('vc-mode'); } catch (e) { return null; } }
  function paint(m) {
    root.setAttribute('data-mode', m);
    var label = m === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
    btn.setAttribute('aria-label', label);
    btn.setAttribute('title', label);
    if (meta) meta.setAttribute('content', bar[m]);
  }
  paint(root.getAttribute('data-mode') === 'dark' ? 'dark' : 'light');
  btn.addEventListener('click', function () {
    var next = root.getAttribute('data-mode') === 'dark' ? 'light' : 'dark';
    paint(next);
    try { localStorage.setItem('vc-mode', next); } catch (e) {}
  });
  // until the visitor clicks, keep following their system setting
  if (window.matchMedia) {
    var mq = matchMedia('(prefers-color-scheme: dark)');
    var follow = function (e) { if (!saved()) paint(e.matches ? 'dark' : 'light'); };
    if (mq.addEventListener) mq.addEventListener('change', follow);
  }
})();
