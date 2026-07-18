(function () {
  'use strict';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduced || !('IntersectionObserver' in window)) return;

  /* ---- scroll reveal with per-group stagger ---- */
  var targets = document.querySelectorAll(
    '.section .card, .section .rich-card, .section .offer-card, .section .link-card, ' +
    '.section .step, .section .chip, .faq-item, .section h2, .section .lead, .section .eyebrow, .prose p'
  );
  var groups = new Map();
  targets.forEach(function (el) {
    el.classList.add('reveal');
    var parent = el.parentElement;
    var idx = groups.get(parent) || 0;
    groups.set(parent, idx + 1);
    el.style.setProperty('--d', Math.min(idx * 0.06, 0.5) + 's');
  });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  targets.forEach(function (el) { io.observe(el); });

  /* ---- count-up stats ---- */
  function animateStat(el) {
    var num = parseFloat(el.dataset.num || '0');
    var dec = parseInt(el.dataset.dec || '0', 10);
    var suffix = el.dataset.suffix || '';
    var locale = el.dataset.locale || 'en-US';
    var dur = 1600, start = null;
    function frame(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      var val = num * eased;
      el.textContent = val.toLocaleString(locale, {
        minimumFractionDigits: dec, maximumFractionDigits: dec
      }) + (p === 1 ? suffix : '');
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  var statIO = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { animateStat(e.target); statIO.unobserve(e.target); }
    });
  }, { threshold: 0.6 });
  document.querySelectorAll('.stat-n[data-num]').forEach(function (el) { statIO.observe(el); });
})();
