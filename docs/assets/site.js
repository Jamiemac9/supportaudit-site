/* Support Audit: site interactions */
(function () {
  'use strict';

  /* ---------------------------------------------------------------
     Booking form delivery.
     1. Go to https://web3forms.com, enter hello@supportaudit.co.uk
        and copy the access key they email you.
     2. Paste it between the quotes below and push the change.
     Until a key is set, the form opens the visitor's email app
     with their details filled in instead.
  --------------------------------------------------------------- */
  var WEB3FORMS_KEY = '';
  var CONTACT_EMAIL = 'hello@supportaudit.co.uk';

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  /* Mobile menu */
  var toggle = $('[data-menu-toggle]');
  var drawer = $('[data-drawer]');
  if (toggle && drawer) {
    toggle.addEventListener('click', function () {
      var open = drawer.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && drawer.classList.contains('open')) {
        drawer.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });
  }

  /* Audience tabs (home) */
  $$('[data-tab]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var scope = btn.closest('section');
      var key = btn.getAttribute('data-tab');
      $$('[data-tab]', scope).forEach(function (b) {
        var on = b === btn;
        b.classList.toggle('on', on);
        b.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
      $$('[data-pane]', scope).forEach(function (p) {
        p.classList.toggle('on', p.getAttribute('data-pane') === key);
      });
    });
  });

  /* How it works steps (home) */
  var stepBtns = $$('[data-step]');
  if (stepBtns.length) {
    var panes = $$('[data-step-pane]');
    var bar = $('[data-step-bar]');
    var labels = $$('[data-next-label]');
    var titles = stepBtns.map(function (b) { return $('[data-step-title]', b).textContent; });
    var current = 0;
    var setStep = function (i) {
      current = i;
      stepBtns.forEach(function (b, j) {
        b.classList.toggle('on', j === i);
        b.setAttribute('aria-pressed', j === i ? 'true' : 'false');
      });
      panes.forEach(function (p, j) { p.classList.toggle('on', j === i); });
      if (bar) bar.style.width = Math.round(((i + 1) / stepBtns.length) * 100) + '%';
      var last = i === stepBtns.length - 1;
      labels.forEach(function (l) { l.textContent = last ? 'Back to the start' : 'Next: ' + titles[i + 1]; });
    };
    stepBtns.forEach(function (b, i) { b.addEventListener('click', function () { setStep(i); }); });
    var next = $('[data-step-next]');
    if (next) next.addEventListener('click', function () {
      setStep(current === stepBtns.length - 1 ? 0 : current + 1);
    });
  }

  /* Use case filter */
  var filters = $$('[data-filter]');
  if (filters.length) {
    var items = $$('[data-aud]');
    var count = $('[data-count]');
    filters.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var f = btn.getAttribute('data-filter');
        filters.forEach(function (b) {
          var on = b === btn;
          b.classList.toggle('on', on);
          b.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
        var shown = 0;
        items.forEach(function (it) {
          var a = it.getAttribute('data-aud');
          var show = f === 'all' || a === 'both' || a === f;
          it.hidden = !show;
          if (show) shown++;
        });
        if (count) count.textContent = 'Showing ' + shown + ' of ' + items.length + ' use cases';
      });
    });
  }

  /* Self-check (support file guide) */
  var checks = $$('[data-ck]');
  if (checks.length) {
    var done = $('[data-ck-done]');
    var ckBar = $('[data-ck-bar]');
    var msg = $('[data-ck-msg]');
    var update = function () {
      var n = checks.filter(function (c) { return c.checked; }).length;
      var t = checks.length;
      checks.forEach(function (c) { c.closest('.ck').classList.toggle('on', c.checked); });
      done.textContent = n;
      ckBar.style.width = Math.round((n / t) * 100) + '%';
      msg.textContent = n === t ? 'This file looks audit-ready. Keep it that way with regular checks.'
        : n >= 9 ? 'Nearly there. Fix the remaining items before your next audit.'
        : n >= 5 ? 'Some solid foundations, with gaps an auditor would flag.'
        : 'Tick each item that is true for the file in front of you.';
    };
    checks.forEach(function (c) { c.addEventListener('change', update); });
    var reset = $('[data-ck-reset]');
    if (reset) reset.addEventListener('click', function () {
      checks.forEach(function (c) { c.checked = false; });
      update();
    });
  }

  /* Booking forms */
  $$('[data-booking-form]').forEach(function (form) {
    var card = form.closest('.form');
    var body = $('[data-form-body]', card);
    var doneBox = $('[data-form-done]', card);
    var errBox = $('[data-errbox]', form);
    var submitBtn = $('button[type="submit"]', form);

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var fd = new FormData(form);
      var v = function (k) { return String(fd.get(k) || '').trim(); };
      var errors = {
        name: !v('name'),
        org: !v('org'),
        email: !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v('email')),
        role: !v('role'),
        consent: !fd.get('consent')
      };
      var bad = false;
      Object.keys(errors).forEach(function (k) {
        var el = $('[data-err="' + k + '"]', form);
        if (el) el.hidden = !errors[k];
        if (errors[k]) bad = true;
      });
      if (errBox) errBox.hidden = !bad;
      if (bad) {
        var first = Object.keys(errors).filter(function (k) { return errors[k]; })[0];
        var field = form.elements[first];
        if (field && field.focus) field.focus();
        return;
      }
      if (fd.get('botcheck')) return;

      var data = {
        name: v('name'), organisation: v('org'), email: v('email'), phone: v('phone'),
        role: v('role'), residents: v('size'),
        interested_in: fd.getAll('interest').join(', '),
        best_time: v('when'), local_authority: v('area'), message: v('message'),
        page: location.pathname
      };
      var first = data.name.split(/\s+/)[0];

      var finish = function (text) {
        $$('[data-sent-name]', card).forEach(function (s) { s.textContent = first; });
        if (text) { var p = $('.body', doneBox); if (p) p.textContent = text; }
        body.hidden = true;
        doneBox.hidden = false;
        doneBox.setAttribute('tabindex', '-1');
        doneBox.focus();
      };

      if (!WEB3FORMS_KEY) {
        var lines = Object.keys(data).filter(function (k) { return data[k]; })
          .map(function (k) { return k.replace(/_/g, ' ') + ': ' + data[k]; });
        location.href = 'mailto:' + CONTACT_EMAIL +
          '?subject=' + encodeURIComponent('Discovery call request: ' + data.organisation) +
          '&body=' + encodeURIComponent(lines.join('\n'));
        finish('Your email app should have opened with your details filled in. Press send and we will reply to confirm a time.');
        return;
      }

      submitBtn.disabled = true;
      submitBtn.setAttribute('aria-busy', 'true');
      var payload = Object.assign({
        access_key: WEB3FORMS_KEY,
        subject: 'Discovery call request: ' + data.organisation,
        from_name: 'supportaudit.co.uk'
      }, data);
      fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(payload)
      }).then(function (r) { return r.json(); }).then(function (res) {
        if (!res.success) throw new Error(res.message || 'Send failed');
        finish();
      }).catch(function () {
        if (errBox) {
          errBox.hidden = false;
          var box = $('.errbox', errBox);
          if (box) box.innerHTML = 'Sorry, that didn’t send. Please email <a href="mailto:' + CONTACT_EMAIL + '">' + CONTACT_EMAIL + '</a> instead.';
        }
      }).then(function () {
        submitBtn.disabled = false;
        submitBtn.removeAttribute('aria-busy');
      });
    });

    var again = $('[data-again]', card);
    if (again) again.addEventListener('click', function () {
      form.reset();
      $$('[data-err]', form).forEach(function (el) { el.hidden = true; });
      if (errBox) errBox.hidden = true;
      doneBox.hidden = true;
      body.hidden = false;
    });
  });
})();
