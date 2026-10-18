/* sintr — site behaviour.
   Everything here is an enhancement: the page reads completely without it. */
(function () {
  'use strict';

  var root = document.documentElement;
  var motion = root.classList.contains('motion');
  var live = document.querySelector('.toast');

  /* ── Copy to clipboard ─────────────────────────────────────────────── */

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var area = document.createElement('textarea');
      area.value = text;
      area.setAttribute('readonly', '');
      area.style.position = 'fixed';
      area.style.opacity = '0';
      document.body.appendChild(area);
      area.select();
      try {
        document.execCommand('copy') ? resolve() : reject(new Error('copy failed'));
      } catch (err) {
        reject(err);
      } finally {
        document.body.removeChild(area);
      }
    });
  }

  function announce(message) {
    if (!live) return;
    live.textContent = '';
    window.setTimeout(function () { live.textContent = message; }, 30);
  }

  document.querySelectorAll('[data-copy]').forEach(function (trigger) {
    var label = trigger.querySelector('[data-label]');
    var idle = label ? label.textContent : '';
    var timer;

    trigger.addEventListener('click', function (event) {
      var source = document.querySelector(trigger.getAttribute('data-copy'));
      if (!source) return;
      event.preventDefault();
      // innerText drops the decorative "$ " and "/" prompt spans' styling but keeps their text,
      // so strip shell prompts to leave only what should be pasted.
      // Text inside a closed <details> isn't rendered, so innerText comes back empty there.
      var raw = source.innerText;
      if (!raw || !raw.trim()) raw = source.textContent.replace(/\s+/g, ' ');
      var text = raw.replace(/^\$ /gm, '').trim();

      copyText(text).then(function () {
        var done = trigger.getAttribute('data-copied') || 'Copied';
        trigger.classList.add('is-done');
        if (label) label.textContent = done;
        announce(done);
        window.clearTimeout(timer);
        timer = window.setTimeout(function () {
          trigger.classList.remove('is-done');
          if (label) label.textContent = idle;
        }, 2600);
      }, function () {
        // Clipboard refused: fall back to showing the text so it can be copied by hand.
        if (trigger.tagName === 'A') window.location.hash = trigger.getAttribute('href');
        announce(document.body.getAttribute('data-copy-failed') || 'Copy failed. Select the text to copy it.');
      });
    });
  });

  /* ── Languages: remember an explicit choice; close the menu like a menu ── */

  document.querySelectorAll('a[data-lang]').forEach(function (link) {
    link.addEventListener('click', function () {
      try { localStorage.setItem('sintr-lang', link.getAttribute('data-lang')); } catch (e) {}
    });
  });
  var langs = document.querySelector('details.langs');
  if (langs) {
    document.addEventListener('click', function (event) {
      if (langs.open && !langs.contains(event.target)) langs.open = false;
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && langs.open) {
        langs.open = false;
        langs.querySelector('summary').focus();
      }
    });
  }

  /* ── Deep link to an install tab (#install-generic, #install-hermes…) ── */

  function openInstallTab() {
    var match = /^#install-(claude|hermes|generic)$/.exec(window.location.hash);
    var radio = match && document.getElementById('ag-' + match[1]);
    if (!radio) return;
    radio.checked = true;
    var section = document.getElementById('install');
    if (section) section.scrollIntoView();
  }
  openInstallTab();
  window.addEventListener('hashchange', openInstallTab);

  /* ── Contents: mark the section being read (works with or without motion) ── */

  var tocLinks = Array.prototype.slice.call(document.querySelectorAll('.toc a[href^="#"]'));
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var byId = {};
    tocLinks.forEach(function (link) { byId[link.getAttribute('href').slice(1)] = link; });
    var tocObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        tocLinks.forEach(function (link) { link.removeAttribute('aria-current'); });
        var current = byId[entry.target.id];
        if (current) current.setAttribute('aria-current', 'true');
      });
    }, { rootMargin: '-30% 0px -65% 0px' });
    Object.keys(byId).forEach(function (id) {
      var section = document.getElementById(id);
      if (section) tocObserver.observe(section);
    });
  }

  if (!motion) return;

  /* ── Time of day: the light follows the section you are reading ───── */

  var timed = Array.prototype.slice.call(document.querySelectorAll('[data-time]'))
    .filter(function (el) { return el !== root; });

  var timeObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) root.setAttribute('data-time', entry.target.getAttribute('data-time'));
    });
  }, { rootMargin: '-48% 0px -48% 0px' });
  timed.forEach(function (el) { timeObserver.observe(el); });

  /* ── Reveals ───────────────────────────────────────────────────────── */

  // Siblings revealed together get a small stagger, so groups settle rather than pop.
  var groups = new Map();
  document.querySelectorAll('[data-reveal]').forEach(function (el) {
    var parent = el.parentElement;
    var index = groups.get(parent) || 0;
    groups.set(parent, index + 1);
    el.style.setProperty('--d', Math.min(index, 6) * 0.09 + 's');
  });

  var revealObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-in');
      revealObserver.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

  document.querySelectorAll('[data-reveal], [data-write]').forEach(function (el) {
    revealObserver.observe(el);
  });

  // The entry writes itself one field at a time.
  document.querySelectorAll('[data-write] .ln').forEach(function (line, i) {
    line.style.setProperty('--i', i);
  });

  /* ── Parallax: artifacts drift a little slower than the words ──────── */

  var layers = Array.prototype.slice.call(document.querySelectorAll('[data-depth]'));
  var ticking = false;

  function drift() {
    var mid = window.innerHeight / 2;
    layers.forEach(function (el) {
      var rect = el.getBoundingClientRect();
      if (rect.bottom < -200 || rect.top > window.innerHeight + 200) return;
      var depth = parseFloat(el.getAttribute('data-depth')) || 0;
      var offset = (rect.top + rect.height / 2 - mid) * depth;
      el.style.transform = 'translate3d(0,' + offset.toFixed(1) + 'px,0)';
    });
    ticking = false;
  }

  function requestDrift() {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(drift);
    }
  }

  if (window.matchMedia('(min-width: 901px)').matches) {
    window.addEventListener('scroll', requestDrift, { passive: true });
    window.addEventListener('resize', requestDrift);
    drift();
  }
})();
