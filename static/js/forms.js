/* static/js/forms.js
   ناردنی فۆرمی پەیوەندی و CV بە fetch (CSP-safe، بێ inline script).
   لە capture phase دا کار دەکات، بۆیە ئەگەر main.js هەمان کار بکات دووبارە نانێردرێت. */
(function () {
  'use strict';

  var MSG = {
    ckb: { sending: 'دەنێردرێت...', ok: 'سوپاس! پەیامەکەت بە سەرکەوتوویی نێردرا.', err: 'هەڵەیەک ڕوویدا، تکایە دووبارە هەوڵبدەرەوە.', big: 'قەبارەی فایل لە 5MB زیاترە.', type: 'تەنها PDF یان Word قبوڵە.' },
    ar:  { sending: 'جارٍ الإرسال...', ok: 'شكراً! تم إرسال رسالتك بنجاح.', err: 'حدث خطأ، يرجى المحاولة مرة أخرى.', big: 'حجم الملف أكبر من 5MB.', type: 'يُقبل PDF أو Word فقط.' },
    en:  { sending: 'Sending...', ok: 'Thank you! Your message was sent successfully.', err: 'Something went wrong, please try again.', big: 'File is larger than 5MB.', type: 'Only PDF or Word files are accepted.' }
  };

  function lang() {
    var l = (document.documentElement.getAttribute('data-lang') || document.documentElement.lang || 'ckb').toLowerCase();
    if (l.indexOf('ar') === 0) return 'ar';
    if (l.indexOf('en') === 0) return 'en';
    return 'ckb';
  }

  function t(key) { return MSG[lang()][key]; }

  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form || (form.id !== 'contactForm' && form.id !== 'cvForm')) return;

    e.preventDefault();
    e.stopImmediatePropagation();

    var status = document.getElementById(form.getAttribute('data-status'));
    var btn = form.querySelector('button[type="submit"]');

    function say(text, ok) {
      if (!status) return;
      status.textContent = text;
      status.style.color = ok ? '#1a7f37' : '#b42318';
    }

    // پشکنینی فایل
    var file = form.querySelector('input[type="file"]');
    if (file && file.files && file.files[0]) {
      var f = file.files[0];
      if (f.size > 5 * 1024 * 1024) { say(t('big'), false); return; }
      if (!/\.(pdf|doc|docx)$/i.test(f.name)) { say(t('type'), false); return; }
    }

    var tokenInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
    var token = tokenInput ? tokenInput.value : '';

    if (btn) btn.disabled = true;
    say(t('sending'), true);

    fetch(form.getAttribute('data-action'), {
      method: 'POST',
      body: new FormData(form),
      credentials: 'same-origin',
      headers: { 'X-CSRFToken': token, 'X-Requested-With': 'XMLHttpRequest' }
    })
      .then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (d) { return { ok: r.ok, data: d }; });
      })
      .then(function (res) {
        if (res.ok && res.data.ok !== false) {
          say(t('ok'), true);
          form.reset();
        } else {
          say(t('err'), false);
        }
      })
      .catch(function () { say(t('err'), false); })
      .then(function () { if (btn) btn.disabled = false; });
  }, true);
})();