/* SEA Audit · site script: motion, navigation, interactions, booking form, consent. */
(function () {
  'use strict';

  /* ---------------------------------------------------------------
     Settings
     WEB3FORMS_KEY: free key from https://web3forms.com (sign up with
     hello@seaaudit.com). Until it is set, the booking form opens the
     visitor's email app with their details filled in.
  --------------------------------------------------------------- */
  var WEB3FORMS_KEY = '';
  var CONTACT_EMAIL = 'hello@seaaudit.com';

  var SEA = window.SEA = window.SEA || {};
  var html = document.documentElement;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = html.classList.contains('no-motion');
  var fine = window.matchMedia('(pointer: fine)').matches;
  var safe = function (fn) { try { fn(); } catch (e) { if (window.console) console.warn('[sea]', e); } };
  var clamp = function (v, a, b) { return Math.max(a, Math.min(b, v)); };

  /* ---------- smooth scroll ---------- */
  var lenis = null;
  safe(function () {
    if (reduce || !window.Lenis) return;
    lenis = SEA.lenis = new window.Lenis({ lerp: 0.11, smoothWheel: true });
    var raf = function (t) { lenis.raf(t); requestAnimationFrame(raf); };
    requestAnimationFrame(raf);
    if (html.classList.contains('is-intro')) { lenis.stop(); setTimeout(function () { lenis.start(); }, 1300); }
  });
  var scrollToEl = function (el) {
    if (lenis) lenis.scrollTo(el, { offset: -90, duration: 1.3 });
    else el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
  };

  /* ---------- scroll loop: nav, progress, manifesto, rail, reading ---------- */
  var nav = $('.nav'), prog = $('.prog');
  var lastY = 0;
  var scrollers = [];
  var onScroll = function () {
    var y = window.scrollY, vh = window.innerHeight;
    if (nav) {
      nav.classList.toggle('solid', y > 30);
      nav.classList.toggle('hide', y > 500 && y > lastY + 4 && !html.classList.contains('menu-open'));
      if (y < lastY - 4) nav.classList.remove('hide');
    }
    lastY = y;
    if (prog) {
      var max = Math.max(1, document.documentElement.scrollHeight - vh);
      prog.style.transform = 'scaleX(' + (y / max).toFixed(4) + ')';
    }
    scrollers.forEach(function (f) { f(y, vh); });
  };
  var ticking = false;
  window.addEventListener('scroll', function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () { ticking = false; onScroll(); });
  }, { passive: true });
  window.addEventListener('resize', function () { onScroll(); }, { passive: true });

  /* ---------- menu ---------- */
  safe(function () {
    var btn = $('.menu-btn'), menu = $('#menu');
    if (!btn || !menu) return;
    var set = function (open) {
      if (open) {
        menu.hidden = false;
        requestAnimationFrame(function () { requestAnimationFrame(function () { menu.classList.add('open'); }); });
        html.classList.add('menu-open');
        if (lenis) lenis.stop();
      } else {
        menu.classList.remove('open');
        html.classList.remove('menu-open');
        if (lenis) lenis.start();
        setTimeout(function () { if (!menu.classList.contains('open')) menu.hidden = true; }, 400);
      }
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    };
    btn.addEventListener('click', function () { set(menu.hidden); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !menu.hidden) { set(false); btn.focus(); } });
    $$('a', menu).forEach(function (a) { a.addEventListener('click', function () { set(false); }); });
  });

  /* ---------- in-page anchors ---------- */
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a) return;
    var id = a.getAttribute('href');
    if (id.length < 2) return;
    var t = document.getElementById(id.slice(1));
    if (!t) return;
    e.preventDefault();
    scrollToEl(t);
    if (history.replaceState) history.replaceState(null, '', id);
  });

  /* ---------- reveals ---------- */
  safe(function () {
    var els = $$('.rv, .rv-s');
    $$('.rv-s').forEach(function (g) { Array.prototype.forEach.call(g.children, function (c, i) { c.style.setProperty('--i', i); }); });
    if (reduce || !('IntersectionObserver' in window)) { els.forEach(function (e) { e.classList.add('in'); }); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.06 });
    els.forEach(function (e) { io.observe(e); });
  });

  /* ---------- counters ---------- */
  safe(function () {
    var els = $$('[data-count]');
    if (!els.length || reduce || !('IntersectionObserver' in window)) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        io.unobserve(en.target);
        var el = en.target, to = parseFloat(el.getAttribute('data-count')), t0 = performance.now(), D = 1400;
        var tick = function (now) {
          var p = clamp((now - t0) / D, 0, 1), e = 1 - Math.pow(1 - p, 4);
          el.textContent = Math.round(to * e);
          if (p < 1) requestAnimationFrame(tick);
        };
        el.textContent = '0';
        requestAnimationFrame(tick);
      });
    }, { threshold: 0.6 });
    els.forEach(function (e) { io.observe(e); });
  });

  /* ---------- manifesto: words light up with scroll ---------- */
  safe(function () {
    $$('[data-words]').forEach(function (p) {
      var frag = document.createDocumentFragment();
      Array.prototype.slice.call(p.childNodes).forEach(function (node) {
        var hl = node.nodeType === 1;
        node.textContent.split(/(\s+)/).forEach(function (part) {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
          var s = document.createElement('span');
          s.className = hl ? 'w hl' : 'w';
          s.textContent = part;
          frag.appendChild(s);
        });
      });
      p.textContent = '';
      p.appendChild(frag);
      if (reduce) return;
      var sec = p.closest('.manifesto');
      var words = $$('.w', p);
      scrollers.push(function (y, vh) {
        var r = sec.getBoundingClientRect(), prog;
        if (r.top > vh * 1.4 || r.bottom < -vh * 0.4) { if (words[0].style.opacity !== '') words.forEach(function (w) { w.style.opacity = ''; }); return; }
        if (window.innerWidth >= 900) prog = clamp(-r.top / Math.max(1, r.height - vh), 0, 1);
        else { var pr = p.getBoundingClientRect(); prog = clamp((vh * 0.85 - pr.top) / (pr.height + vh * 0.4), 0, 1); }
        var lit = prog * (words.length + 4);
        words.forEach(function (w, i) { w.style.opacity = (0.14 + 0.86 * clamp(lit - i, 0, 1)).toFixed(3); });
      });
    });
  });

  /* ---------- horizontal rail ---------- */
  safe(function () {
    var sec = $('.rail');
    if (!sec) return;
    var track = $('.rail-track', sec), vp = $('.rail-viewport', sec), bar = $('.rail-progress i', sec);
    var desk = function () { return window.innerWidth >= 900 && !reduce; };
    var dist = 0;
    var measure = function () {
      if (desk()) {
        dist = Math.max(0, track.scrollWidth - window.innerWidth);
        sec.style.setProperty('--rail-h', (dist + window.innerHeight * 1.15) + 'px');
      } else {
        sec.style.removeProperty('--rail-h');
        track.style.transform = '';
      }
    };
    measure();
    window.addEventListener('resize', measure, { passive: true });
    window.addEventListener('load', measure);
    scrollers.push(function (y, vh) {
      if (!desk()) return;
      var r = sec.getBoundingClientRect();
      var p = clamp(-r.top / Math.max(1, r.height - vh), 0, 1);
      track.style.transform = 'translate3d(' + (-p * dist).toFixed(1) + 'px,0,0)';
      if (bar) bar.style.transform = 'scaleX(' + p.toFixed(4) + ')';
    });
    if (vp) vp.addEventListener('scroll', function () {
      if (desk() || !bar) return;
      var m = Math.max(1, vp.scrollWidth - vp.clientWidth);
      bar.style.transform = 'scaleX(' + (vp.scrollLeft / m).toFixed(4) + ')';
    }, { passive: true });
  });

  /* ---------- guide reading progress + contents highlight ---------- */
  safe(function () {
    var prose = $('.prose');
    var rp = $('.read-prog i');
    if (!prose || !rp) return;
    var links = $$('.toc a');
    var heads = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); }).filter(Boolean);
    scrollers.push(function (y, vh) {
      var r = prose.getBoundingClientRect();
      rp.style.transform = 'scaleX(' + clamp((vh * 0.3 - r.top) / Math.max(1, r.height - vh * 0.5), 0, 1).toFixed(4) + ')';
      var cur = 0;
      heads.forEach(function (h, i) { if (h.getBoundingClientRect().top < vh * 0.35) cur = i; });
      links.forEach(function (a, i) { a.classList.toggle('on', i === cur); });
    });
  });

  /* ---------- pointer effects: card glow, tilt, magnetic, parallax ---------- */
  safe(function () {
    if (!fine || reduce) return;
    $$('.card, .rc, .uc, .svc, [data-tilt]').forEach(function (el) {
      var tilt = el.hasAttribute('data-tilt');
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width, py = (e.clientY - r.top) / r.height;
        el.style.setProperty('--gx', (px * 100).toFixed(1) + '%');
        el.style.setProperty('--gy', (py * 100).toFixed(1) + '%');
        if (tilt) {
          el.classList.add('tilting');
          el.style.setProperty('--ry', ((px - 0.5) * 8).toFixed(2) + 'deg');
          el.style.setProperty('--rx', ((0.5 - py) * 6).toFixed(2) + 'deg');
        }
      });
      if (tilt) el.addEventListener('pointerleave', function () {
        el.classList.remove('tilting');
        el.style.setProperty('--rx', '0deg');
        el.style.setProperty('--ry', '0deg');
      });
    });
    $$('[data-magnetic]').forEach(function (b) {
      b.addEventListener('pointermove', function (e) {
        var r = b.getBoundingClientRect();
        b.style.translate = ((e.clientX - r.left - r.width / 2) * 0.18).toFixed(1) + 'px ' + ((e.clientY - r.top - r.height / 2) * 0.28).toFixed(1) + 'px';
      });
      b.addEventListener('pointerleave', function () { b.style.translate = ''; });
    });
    var layers = $$('[data-depth]');
    if (layers.length) {
      var mx = 0, my = 0, tx = 0, ty = 0;
      window.addEventListener('pointermove', function (e) { mx = e.clientX / window.innerWidth - 0.5; my = e.clientY / window.innerHeight - 0.5; }, { passive: true });
      var loop = function () {
        tx += (mx - tx) * 0.06; ty += (my - ty) * 0.06;
        layers.forEach(function (n) {
          var d = +n.getAttribute('data-depth');
          n.style.transform = 'translate3d(' + (tx * d * 36).toFixed(2) + 'px,' + (ty * d * 26).toFixed(2) + 'px,0)';
        });
        requestAnimationFrame(loop);
      };
      requestAnimationFrame(loop);
    }
  });

  /* ---------- audience tabs ---------- */
  $$('[data-tab]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var scope = btn.closest('section'), key = btn.getAttribute('data-tab');
      $$('[data-tab]', scope).forEach(function (b) { var on = b === btn; b.classList.toggle('on', on); b.setAttribute('aria-pressed', on ? 'true' : 'false'); });
      $$('[data-pane]', scope).forEach(function (p) { p.classList.toggle('on', p.getAttribute('data-pane') === key); });
    });
  });

  /* ---------- how-it-works steps ---------- */
  safe(function () {
    var btns = $$('[data-step]');
    if (!btns.length) return;
    var panes = $$('[data-step-pane]'), bar = $('[data-step-bar]'), labels = $$('[data-next-label]');
    var titles = btns.map(function (b) { return $('[data-step-title]', b).textContent; });
    var cur = 0;
    var set = function (i) {
      cur = i;
      btns.forEach(function (b, j) { b.classList.toggle('on', j === i); b.setAttribute('aria-pressed', j === i ? 'true' : 'false'); });
      panes.forEach(function (p, j) { p.classList.toggle('on', j === i); });
      if (bar) bar.style.width = Math.round(((i + 1) / btns.length) * 100) + '%';
      var last = i === btns.length - 1;
      labels.forEach(function (l) { l.textContent = last ? 'Back to the start' : 'Next: ' + titles[i + 1]; });
    };
    btns.forEach(function (b, i) { b.addEventListener('click', function () { set(i); }); });
    var next = $('[data-step-next]');
    if (next) next.addEventListener('click', function () { set(cur === btns.length - 1 ? 0 : cur + 1); });
  });

  /* ---------- use-case filter ---------- */
  safe(function () {
    var filters = $$('[data-filter]');
    if (!filters.length) return;
    var items = $$('[data-aud]'), count = $('[data-count-label]');
    filters.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var f = btn.getAttribute('data-filter'), shown = 0;
        filters.forEach(function (b) { var on = b === btn; b.classList.toggle('on', on); b.setAttribute('aria-pressed', on ? 'true' : 'false'); });
        items.forEach(function (it) {
          var a = it.getAttribute('data-aud'), show = f === 'all' || a === 'both' || a === f;
          it.hidden = !show;
          if (show) { shown++; it.classList.add('in'); }
        });
        if (count) count.textContent = 'Showing ' + shown + ' of ' + items.length + ' use cases';
        onScroll();
      });
    });
  });

  /* ---------- self-check ---------- */
  safe(function () {
    var checks = $$('[data-ck]');
    if (!checks.length) return;
    var done = $('[data-ck-done]'), bar = $('[data-ck-bar]'), msg = $('[data-ck-msg]');
    var update = function () {
      var n = checks.filter(function (c) { return c.checked; }).length, t = checks.length;
      checks.forEach(function (c) { c.closest('.ck').classList.toggle('on', c.checked); });
      done.textContent = n;
      bar.style.width = Math.round((n / t) * 100) + '%';
      msg.textContent = n === t ? 'This file looks audit-ready. Keep it that way with regular checks.'
        : n >= 9 ? 'Nearly there. Fix the remaining items before your next audit.'
        : n >= 5 ? 'Some solid foundations, with gaps an auditor would flag.'
        : 'Tick each item that is true for the file in front of you.';
    };
    checks.forEach(function (c) { c.addEventListener('change', update); });
    var reset = $('[data-ck-reset]');
    if (reset) reset.addEventListener('click', function () { checks.forEach(function (c) { c.checked = false; }); update(); });
  });

  /* ---------- booking forms ---------- */
  $$('[data-booking-form]').forEach(function (form) {
    var card = form.closest('.form'), body = $('[data-form-body]', card), doneBox = $('[data-form-done]', card);
    var errBox = $('[data-errbox]', form), submitBtn = $('button[type="submit"]', form);
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var fd = new FormData(form);
      var v = function (k) { return String(fd.get(k) || '').trim(); };
      var errors = { name: !v('name'), org: !v('org'), email: !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v('email')), role: !v('role'), consent: !fd.get('consent') };
      var bad = false;
      Object.keys(errors).forEach(function (k) {
        var el = $('[data-err="' + k + '"]', form);
        if (el) el.hidden = !errors[k];
        if (errors[k]) bad = true;
      });
      if (errBox) errBox.hidden = !bad;
      if (bad) {
        var first = Object.keys(errors).filter(function (k) { return errors[k]; })[0];
        if (form.elements[first] && form.elements[first].focus) form.elements[first].focus();
        return;
      }
      if (fd.get('botcheck')) return;
      var data = {
        name: v('name'), organisation: v('org'), email: v('email'), phone: v('phone'), role: v('role'),
        residents: v('size'), interested_in: fd.getAll('interest').join(', '), best_time: v('when'),
        local_authority: v('area'), message: v('message'), page: location.pathname
      };
      var firstName = data.name.split(/\s+/)[0];
      var finish = function (text) {
        $$('[data-sent-name]', card).forEach(function (s) { s.textContent = firstName; });
        if (text) { var p = $('.body', doneBox); if (p) p.textContent = text; }
        body.hidden = true; doneBox.hidden = false;
        doneBox.setAttribute('tabindex', '-1'); doneBox.focus();
        if (window.gtag) window.gtag('event', 'generate_lead', { form_location: location.pathname, role: data.role });
      };
      if (!WEB3FORMS_KEY) {
        var lines = Object.keys(data).filter(function (k) { return data[k]; }).map(function (k) { return k.replace(/_/g, ' ') + ': ' + data[k]; });
        location.href = 'mailto:' + CONTACT_EMAIL + '?subject=' + encodeURIComponent('Discovery call request: ' + data.organisation) + '&body=' + encodeURIComponent(lines.join('\n'));
        finish('Your email app should have opened with your details filled in. Press send and we will reply to confirm a time.');
        return;
      }
      submitBtn.disabled = true;
      submitBtn.setAttribute('aria-busy', 'true');
      var payload = Object.assign({ access_key: WEB3FORMS_KEY, subject: 'Discovery call request: ' + data.organisation, from_name: 'seaaudit.com' }, data);
      fetch('https://api.web3forms.com/submit', {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(payload)
      }).then(function (r) { return r.json(); }).then(function (res) {
        if (!res.success) throw new Error(res.message || 'Send failed');
        finish();
      }).catch(function () {
        if (errBox) {
          errBox.hidden = false;
          var box = $('.errbox', errBox);
          if (box) box.innerHTML = 'Sorry, that didn’t send. Please email <a href="mailto:' + CONTACT_EMAIL + '">' + CONTACT_EMAIL + '</a> instead.';
        }
      }).then(function () { submitBtn.disabled = false; submitBtn.removeAttribute('aria-busy'); });
    });
    var again = $('[data-again]', card);
    if (again) again.addEventListener('click', function () {
      form.reset();
      $$('[data-err]', form).forEach(function (el) { el.hidden = true; });
      if (errBox) errBox.hidden = true;
      doneBox.hidden = true; body.hidden = false;
    });
  });

  /* ---------- analytics consent (GA4, Consent Mode v2) ---------- */
  safe(function () {
    var KEY = 'sea-consent';
    var stored = null;
    try { stored = localStorage.getItem(KEY); } catch (e) {}
    var banner = null;
    var close = function () { if (banner) { banner.remove(); banner = null; } };
    var choose = function (ok) {
      try { localStorage.setItem(KEY, ok ? 'granted' : 'denied'); } catch (e) {}
      if (ok && window.SEA_loadGA) window.SEA_loadGA();
      if (!ok && window.gtag) window.gtag('consent', 'update', { analytics_storage: 'denied' });
      close();
    };
    var show = function () {
      close();
      banner = document.createElement('div');
      banner.className = 'cookie';
      banner.setAttribute('role', 'region');
      banner.setAttribute('aria-label', 'Cookie choice');
      banner.innerHTML = '<p><b>Can we use analytics cookies?</b> They help us see which pages are useful. No advertising cookies, and nothing is shared for marketing.</p>' +
        '<div class="row"><button type="button" class="btn btn-acc btn-sm" data-c="1">Accept analytics</button><button type="button" class="btn btn-line btn-sm" data-c="0">Decline</button></div>';
      document.body.appendChild(banner);
      $$('[data-c]', banner).forEach(function (b) { b.addEventListener('click', function () { choose(b.getAttribute('data-c') === '1'); }); });
    };
    if (!stored) setTimeout(show, 1600);
    $$('[data-cookie-settings]').forEach(function (b) { b.addEventListener('click', show); });
  });

  /* ---------- background field (loads when idle) ---------- */
  safe(function () {
    if (reduce) return;
    var src = html.getAttribute('data-field');
    if (!src) return;
    var go = function () {
      var s = document.createElement('script');
      s.src = src; s.async = true;
      document.body.appendChild(s);
    };
    var idle = window.requestIdleCallback || function (f) { return setTimeout(f, 300); };
    if (document.readyState === 'complete') idle(go);
    else window.addEventListener('load', function () { idle(go); });
  });

  onScroll();
  SEA.ready = true;
})();
