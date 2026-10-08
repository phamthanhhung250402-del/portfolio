/* MC Thúy Vy - portfolio. JS thuần, không framework.
 * Toàn bộ chữ lấy từ data/content.{vi,en}.json, liên hệ & video từ js/config.js,
 * kích thước ảnh từ data/images.json (do tools/build_images.py tạo). */
(function () {
  'use strict';

  var CFG = window.SITE_CONFIG || {};
  var doc = document;
  var root = doc.documentElement;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  var T = null;            // nội dung ngôn ngữ hiện tại
  var IMG = {};            // manifest ảnh: { key: { w, h, widths: [] } }
  var cache = {};
  var lang = root.lang === 'en' ? 'en' : 'vi';
  var statsCounted = false;
  var currentFilter = 'all';

  /* ---------- Helpers ---------- */
  function $(s, c) { return (c || doc).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); }
  function isSet(v) { return typeof v === 'string' && v.trim() !== '' && !/^\{\{.*\}\}$/.test(v.trim()); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function get(obj, path) {
    return path.split('.').reduce(function (o, k) { return o == null ? undefined : o[k]; }, obj);
  }
  function fmt(tpl, vars) { return String(tpl).replace(/\{(\w+)\}/g, function (_, k) { return vars[k] != null ? vars[k] : ''; }); }
  function icon(id, cls) { return '<svg class="icon' + (cls ? ' ' + cls : '') + '" aria-hidden="true"><use href="#i-' + id + '"/></svg>'; }
  function digits(s) { return String(s).replace(/[^\d+]/g, ''); }
  function loadJSON(url) {
    return fetch(url, { credentials: 'same-origin' }).then(function (r) {
      if (!r.ok) throw new Error(url + ' ' + r.status);
      return r.json();
    });
  }
  function loadLang(l) {
    if (!cache[l]) cache[l] = loadJSON('data/content.' + l + '.json');
    return cache[l];
  }
  function numberFmt(n) {
    try { return new Intl.NumberFormat(T.meta.locale).format(n); } catch (e) { return String(n); }
  }

  /* Ảnh responsive dựa trên manifest */
  function imgTag(key, o) {
    o = o || {};
    var base = 'assets/img/' + key;
    var m = IMG[key];
    var w = m ? m.w : 1200, h = m ? m.h : 1500;
    var srcset = '';
    if (m && m.widths && m.widths.length) {
      srcset = m.widths.map(function (x) { return base + '-' + x + '.webp ' + x + 'w'; })
        .concat(base + '.webp ' + m.w + 'w').join(', ');
    }
    return '<img src="' + base + '.webp"' +
      (srcset ? ' srcset="' + srcset + '" sizes="' + (o.sizes || '100vw') + '"' : '') +
      ' width="' + w + '" height="' + h + '" alt="' + esc(o.alt || '') + '"' +
      (o.eager ? '' : ' loading="lazy"') + ' decoding="async"' + (o.cls ? ' class="' + o.cls + '"' : '') + '>';
  }

  /* ---------- Contact links from config ---------- */
  function contactLinks() {
    var out = [];
    if (isSet(CFG.PHONE)) out.push({ key: 'phone', icon: 'phone', href: 'tel:' + digits(CFG.PHONE), value: CFG.PHONE.trim() });
    if (isSet(CFG.ZALO)) {
      var z = CFG.ZALO.trim();
      out.push({ key: 'zalo', icon: 'chat', href: /^https?:/.test(z) ? z : 'https://zalo.me/' + digits(z).replace(/^\+84/, '0'), value: /^https?:/.test(z) ? z.replace(/^https?:\/\/(www\.)?/, '') : z, external: true });
    }
    if (isSet(CFG.EMAIL)) out.push({ key: 'email', icon: 'mail', href: 'mailto:' + CFG.EMAIL.trim(), value: CFG.EMAIL.trim() });
    ['FACEBOOK', 'TIKTOK', 'INSTAGRAM'].forEach(function (k) {
      if (isSet(CFG[k])) {
        out.push({
          key: k.toLowerCase(), icon: k.toLowerCase(), href: CFG[k].trim(), external: true, social: true,
          value: CFG[k].trim().replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '')
        });
      }
    });
    return out;
  }

  /* ---------- Video helpers ---------- */
  function parseVideo(url) {
    if (!isSet(url)) return null;
    var u;
    try { u = new URL(url.trim()); } catch (e) { return null; }
    var host = u.hostname.replace(/^(www|m)\./, '');
    var id, m;
    if (host === 'youtu.be' || /(^|\.)youtube(-nocookie)?\.com$/.test(host)) {
      id = host === 'youtu.be' ? u.pathname.slice(1).split('/')[0] : u.searchParams.get('v');
      if (!id && (m = u.pathname.match(/\/(shorts|embed|live)\/([\w-]{6,})/))) id = m[2];
      if (!id) return { type: 'link', url: url };
      return {
        type: 'youtube', url: url, vertical: /\/shorts\//.test(u.pathname),
        embed: 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0&playsinline=1',
        thumb: 'https://i.ytimg.com/vi/' + id + '/hqdefault.jpg'
      };
    }
    if (/(^|\.)tiktok\.com$/.test(host)) {
      m = u.pathname.match(/\/video\/(\d+)/);
      if (!m) return { type: 'link', url: url, vertical: true };
      return { type: 'tiktok', url: url, vertical: true, embed: 'https://www.tiktok.com/player/v1/' + m[1] + '?autoplay=1&rel=0' };
    }
    if (/(^|\.)facebook\.com$/.test(host) || host === 'fb.watch') {
      return {
        type: 'facebook', url: url, vertical: /\/reel\//.test(u.pathname),
        embed: 'https://www.facebook.com/plugins/video.php?href=' + encodeURIComponent(url) + '&show_text=false&autoplay=1'
      };
    }
    if (/\.(mp4|webm|mov)(\?|$)/i.test(u.pathname)) return { type: 'file', url: url };
    return { type: 'link', url: url };
  }

  var videoRegistry = {};
  function playerHTML(key, v, opts) {
    videoRegistry[key] = v;
    var poster = opts.poster || (v.thumb ? '<img src="' + v.thumb + '" alt="" loading="lazy" decoding="async">' : '');
    var cls = 'player' + (v.vertical ? ' player--vertical' : '');
    var inner = poster + '<span class="play-btn">' + icon('play') + '</span>' +
      (opts.label ? '<span class="player__label">' + esc(opts.label) + '</span>' : '');
    if (v.type === 'link') {
      return '<div class="' + cls + '"><a class="player__poster" href="' + esc(v.url) + '" target="_blank" rel="noopener" aria-label="' +
        esc(opts.aria + ' ' + T.a11y.newTab) + '">' + inner + '</a></div>';
    }
    return '<div class="' + cls + '"><button type="button" class="player__poster" data-play="' + key + '" aria-label="' + esc(opts.aria) + '">' + inner + '</button></div>';
  }
  function playVideo(key) {
    var v = videoRegistry[key];
    var btn = $('[data-play="' + key + '"]');
    if (!v || !btn) return;
    var box = btn.parentNode;
    if (v.type === 'file') {
      box.innerHTML = '<video src="' + esc(v.url) + '" controls autoplay playsinline></video>';
    } else {
      box.innerHTML = '<iframe src="' + esc(v.embed) + '" title="' + esc(T.showreel.iframeTitle) +
        '" allow="autoplay; encrypted-media; picture-in-picture; fullscreen; clipboard-write" allowfullscreen loading="eager"></iframe>';
    }
    var media = box.firstElementChild;
    if (media) { media.setAttribute('tabindex', '0'); media.focus({ preventScroll: true }); }
  }

  /* ---------- Rendering ---------- */
  function applyText() {
    $$('[data-i18n]').forEach(function (el) {
      var v = get(T, el.getAttribute('data-i18n'));
      if (typeof v === 'string') el.textContent = v;
    });
    $$('[data-i18n-attr]').forEach(function (el) {
      el.getAttribute('data-i18n-attr').split(';').forEach(function (pair) {
        var p = pair.split(':');
        var v = get(T, p[1]);
        if (typeof v === 'string') el.setAttribute(p[0], v);
      });
    });
    root.lang = T.meta.lang;
    doc.title = T.meta.title;
    var md = $('meta[name="description"]');
    if (md) md.setAttribute('content', T.meta.description);
    $$('.lang__btn').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-lang') === lang)); });
    var y = $('[data-year]');
    if (y) y.textContent = new Date().getFullYear();
  }

  function render(name, html) {
    var el = $('[data-render="' + name + '"]');
    if (el) el.innerHTML = html;
    return el;
  }
  function stagger(el, step) {
    if (!el) return;
    el.setAttribute('data-reveal-stagger', '');
    Array.prototype.forEach.call(el.children, function (c, i) { c.style.transitionDelay = Math.min(i * (step || 70), 700) + 'ms'; });
    observeReveal(el);
  }

  function renderStats() {
    var el = render('stats', T.stats.items.map(function (s) {
      var shown = statsCounted || reduceMotion.matches ? numberFmt(s.value) : '0';
      return '<li class="stat shimmer"><span class="stat__num" data-value="' + s.value + '" data-suffix="' + esc(s.suffix) + '">' +
        shown + esc(s.suffix) + '</span><span class="stat__label">' + esc(s.label) + '</span></li>';
    }).join(''));
    stagger(el, 110);
    render('specs', T.stats.specs.map(function (s) {
      return '<li>' + icon('star') + '<strong>' + esc(s.label) + '</strong><span>' + esc(s.value) + '</span></li>';
    }).join(''));
    if (el && !statsCounted) countObserver.observe(el);
  }

  function countUp() {
    statsCounted = true;
    $$('.stat__num').forEach(function (n) {
      var target = +n.getAttribute('data-value'), suffix = n.getAttribute('data-suffix') || '';
      if (reduceMotion.matches) { n.textContent = numberFmt(target) + suffix; return; }
      var start = null, dur = 1800;
      function step(t) {
        if (start === null) start = t;
        var p = Math.min(1, (t - start) / dur);
        var e = 1 - Math.pow(1 - p, 4);
        n.textContent = numberFmt(Math.round(target * e)) + suffix;
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    });
  }

  function renderHighlights() {
    stagger(render('highlights', T.highlights.items.map(function (h) {
      return '<li>' + icon('star') + '<span>' + esc(h) + '</span></li>';
    }).join('')), 60);
  }

  function renderShowreel() {
    var v = parseVideo(CFG.SHOWREEL_URL);
    var poster = IMG['showreel-poster'] ? imgTag('showreel-poster', { alt: '', sizes: '(min-width: 1100px) 1040px, 100vw' }) : '';
    var html;
    if (v) {
      html = playerHTML('reel', v, { poster: poster, label: 'Showreel', aria: T.showreel.play });
    } else {
      html = '<div class="player player--pending"><div class="player__poster">' + poster +
        '<div class="pending"><p class="pending__title">' + esc(T.showreel.pendingTitle) + '</p>' +
        '<p class="pending__note">' + esc(T.showreel.pendingNote) + '</p>' +
        '<a class="btn btn--ghost" href="#contact">' + esc(T.showreel.pendingCta) + '</a></div></div></div>';
    }
    render('showreel', html);

    var list = (Array.isArray(CFG.VIDEO_URLS) ? CFG.VIDEO_URLS : []).map(parseVideo).filter(Boolean);
    var box = $('[data-render="videos"]');
    if (!box) return;
    box.hidden = !list.length;
    if (!list.length) { box.innerHTML = ''; return; }
    box.innerHTML = '<h3 class="videos__title">' + esc(T.showreel.moreTitle) + '</h3><div class="videos__grid">' +
      list.map(function (vid, i) {
        return playerHTML('v' + i, vid, { label: T.showreel.videoLabel + ' ' + (i + 1), aria: T.showreel.playVideo + ' ' + (i + 1) });
      }).join('') + '</div>';
  }

  function fieldTitle(id) {
    var f = T.fields.items.filter(function (x) { return x.id === id; })[0];
    return f ? f.title : '';
  }

  function renderFields() {
    stagger(render('fields', T.fields.items.map(function (f, i) {
      return '<li><button type="button" class="card" data-field="' + esc(f.id) + '" aria-haspopup="dialog">' +
        '<span class="card__media">' + imgTag('fields/' + f.id, { alt: '', sizes: '(min-width: 1024px) 380px, (min-width: 768px) 45vw, 80vw' }) +
        '<span class="card__index" aria-hidden="true">0' + (i + 1) + '</span></span>' +
        '<span class="card__body"><span class="card__title">' + esc(f.title) + '</span>' +
        '<span class="card__summary">' + esc(f.summary) + '</span>' +
        '<span class="card__events">' + f.events.slice(0, 3).map(function (e) { return '<span class="card__event">' + esc(e) + '</span>'; }).join('') + '</span>' +
        '<span class="card__more">' + esc(T.fields.open) + icon('arrow-r') + '</span></span></button></li>';
    }).join('')), 90);
    // list inside a button must be phrasing content: use spans styled as list
    $$('.card__events').forEach(function (ev) { ev.setAttribute('role', 'list'); });
    $$('.card__event').forEach(function (ev) { ev.setAttribute('role', 'listitem'); });
  }

  function renderGallery() {
    var filters = [{ id: 'all', title: T.gallery.all }].concat(T.fields.items);
    render('filters', filters.map(function (f) {
      return '<button type="button" class="chip" data-filter="' + esc(f.id) + '" aria-pressed="' + (f.id === currentFilter) + '">' + esc(f.title) + '</button>';
    }).join(''));
    render('gallery', T.gallery.items.map(function (g, i) {
      return '<li data-field="' + esc(g.field) + '"' + (currentFilter !== 'all' && g.field !== currentFilter ? ' class="is-hidden"' : '') + '>' +
        '<button type="button" class="shot" data-shot="' + i + '" aria-haspopup="dialog">' +
        '<span class="shot__media">' + imgTag(g.img, { alt: g.caption + ' - MC Thúy Vy', sizes: '(min-width: 1024px) 400px, (min-width: 480px) 48vw, 92vw' }) + '</span>' +
        '<span class="shot__caption"><span class="shot__title">' + esc(g.caption) + '</span>' +
        '<span class="shot__field">' + esc(fieldTitle(g.field)) + '</span></span></button></li>';
    }).join(''));
  }

  function setFilter(id) {
    currentFilter = id;
    $$('.chip').forEach(function (c) { c.setAttribute('aria-pressed', String(c.getAttribute('data-filter') === id)); });
    $$('[data-render="gallery"] > li').forEach(function (li) {
      li.classList.toggle('is-hidden', id !== 'all' && li.getAttribute('data-field') !== id);
    });
  }

  function renderClients() {
    stagger(render('clients', T.clients.list.map(function (c) { return '<li>' + esc(c) + '</li>'; }).join('')), 25);
  }

  function renderTestimonials() {
    var n = T.testimonials.items.length;
    render('testimonials', T.testimonials.items.map(function (q, i) {
      return '<div class="quote" role="group" aria-roledescription="slide" aria-label="' + esc(fmt(T.testimonials.slide, { i: i + 1, n: n })) + '">' +
        '<svg class="quote__mark" aria-hidden="true"><use href="#i-star"/></svg>' +
        '<blockquote class="quote__text">' + esc(q.quote) + '</blockquote>' +
        '<p class="quote__who"><span class="quote__name">' + esc(q.name) + '</span>' +
        (q.role ? '<span class="quote__role">' + esc(q.role) + '</span>' : '') + '</p></div>';
    }).join(''));
    render('dots', T.testimonials.items.map(function (_, i) {
      return '<button type="button" class="dot" data-dot="' + i + '" aria-label="' + esc(fmt(T.testimonials.goTo, { i: i + 1 })) + '"' + (i === 0 ? ' aria-current="true"' : '') + '></button>';
    }).join(''));
    carousel.sync();
  }

  function renderContact() {
    var links = contactLinks();
    var L = T.contact.labels;
    var html = links.map(function (l) {
      return '<li><a href="' + esc(l.href) + '"' + (l.external ? ' target="_blank" rel="noopener"' : '') + '>' +
        '<span class="contact__icon">' + icon(l.icon) + '</span><span><span class="contact__label">' + esc(L[l.key]) +
        (l.external ? '<span class="visually-hidden"> ' + esc(T.a11y.newTab) + '</span>' : '') + '</span>' +
        '<span class="contact__value">' + esc(l.value) + '</span></span></a></li>';
    }).join('');
    if (!links.length) html = '<li><p class="contact__pending"><span class="contact__icon">' + icon('star') + '</span><span>' + esc(T.contact.pending) + '</span></p></li>';
    render('contact', html);

    render('socials', links.filter(function (l) { return l.social; }).map(function (l) {
      return '<li><a href="' + esc(l.href) + '" target="_blank" rel="noopener" aria-label="' + esc(L[l.key] + ' ' + T.a11y.newTab) + '">' + icon(l.icon) + '</a></li>';
    }).join(''));

    // Thanh liên hệ nhanh trên mobile
    links.forEach(function (l) {
      var a = $('.mobile-bar [data-link="' + l.key + '"]');
      if (a) {
        a.href = l.href;
        if (l.external) { a.target = '_blank'; a.rel = 'noopener'; }
      }
    });

    var sel = $('[data-render="event-types"]');
    if (sel) {
      var cur = sel.value;
      sel.innerHTML = '<option value="">' + esc(T.contact.form.typePlaceholder) + '</option>' +
        T.fields.items.map(function (f) { return '<option>' + esc(f.title) + '</option>'; }).join('') +
        '<option>' + esc(T.contact.form.typeOther) + '</option>';
      sel.value = cur;
      if (sel.selectedIndex < 0) sel.selectedIndex = 0;
    }
  }

  function updateSchema() {
    var s = $('script[type="application/ld+json"]');
    if (!s) return;
    try {
      var data = JSON.parse(s.textContent);
      var same = contactLinks().filter(function (l) { return l.social; }).map(function (l) { return l.href; });
      if (same.length) data.sameAs = same;
      if (isSet(CFG.EMAIL)) data.email = 'mailto:' + CFG.EMAIL.trim();
      if (isSet(CFG.PHONE)) data.telephone = CFG.PHONE.trim();
      s.textContent = JSON.stringify(data);
    } catch (e) { /* bỏ qua */ }
  }

  function renderAll() {
    applyText();
    renderStats();
    renderHighlights();
    renderShowreel();
    renderFields();
    renderGallery();
    renderClients();
    renderTestimonials();
    renderContact();
  }

  function setLang(l) {
    if (l === lang && T) return;
    loadLang(l).then(function (data) {
      lang = l; T = data;
      try { localStorage.setItem('lang', l); } catch (e) { /* private mode */ }
      try {
        var url = new URL(location.href);
        if (l === 'en') url.searchParams.set('lang', 'en'); else url.searchParams.delete('lang');
        history.replaceState(null, '', url.pathname + url.search + url.hash);
      } catch (e) { /* bỏ qua */ }
      renderAll();
    });
  }

  /* ---------- Reveal & count-up observers ---------- */
  var revealObserver = 'IntersectionObserver' in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('is-in'); revealObserver.unobserve(e.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 }) : null;
  function observeReveal(el) {
    if (!el || el.classList.contains('is-in')) return;
    if (revealObserver && !reduceMotion.matches) revealObserver.observe(el); else el.classList.add('is-in');
  }
  var countObserver = 'IntersectionObserver' in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { countObserver.disconnect(); countUp(); }
    });
  }, { threshold: 0.35 }) : { observe: function () { countUp(); }, disconnect: function () {} };

  /* ---------- Header, menu, active link ---------- */
  function initHeader() {
    var header = $('.site-header');
    var onScroll = function () { header.classList.toggle('is-scrolled', window.scrollY > 24); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    var toggle = $('.menu-toggle'), nav = $('#site-nav');
    var outside = [$('main'), $('.site-footer'), $('.mobile-bar')];
    function setMenu(open) {
      nav.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? T.a11y.closeMenu : T.a11y.openMenu);
      toggle.querySelector('use').setAttribute('href', open ? '#i-close' : '#i-menu');
      doc.body.classList.toggle('menu-open', open);
      outside.forEach(function (el) { if (el) el.inert = open; });
      if (open) { var first = $('a', nav); if (first) first.focus(); }
    }
    toggle.addEventListener('click', function () { setMenu(!nav.classList.contains('is-open')); });
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) { setMenu(false); toggle.focus(); }
    });
    window.matchMedia('(min-width: 1024px)').addEventListener('change', function (m) { if (m.matches) setMenu(false); });

    if ('IntersectionObserver' in window) {
      var links = $$('.nav__list a');
      var map = {};
      links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
      var spy = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          var a = map[e.target.id];
          if (!a) return;
          if (e.isIntersecting) {
            links.forEach(function (x) { x.removeAttribute('aria-current'); });
            a.setAttribute('aria-current', 'true');
          }
        });
      }, { rootMargin: '-45% 0px -50% 0px' });
      Object.keys(map).forEach(function (id) { var s = doc.getElementById(id); if (s) spy.observe(s); });
    }
  }

  /* ---------- Testimonial carousel ---------- */
  var carousel = (function () {
    var track, timer = null, paused = false, inView = false, index = 0, lockUntil = 0;
    function slides() { return track ? track.children : []; }
    function go(i, smooth) {
      var n = slides().length;
      if (!n) return;
      index = (i + n) % n;
      lockUntil = Date.now() + 900; // bỏ qua sự kiện scroll do chính lệnh cuộn này sinh ra
      track.scrollTo({ left: index * track.clientWidth, behavior: smooth === false || reduceMotion.matches ? 'auto' : 'smooth' });
      mark();
    }
    function mark() {
      $$('.dot').forEach(function (d, i) { if (i === index) d.setAttribute('aria-current', 'true'); else d.removeAttribute('aria-current'); });
    }
    function tick() { if (!paused && inView && !doc.hidden) go(index + 1); }
    function start() { if (!reduceMotion.matches && !timer) timer = setInterval(tick, 7000); }
    function init() {
      track = $('.carousel__track');
      if (!track) return;
      var raf;
      track.addEventListener('scroll', function () {
        cancelAnimationFrame(raf);
        if (Date.now() < lockUntil) return;
        raf = requestAnimationFrame(function () {
          var i = Math.round(track.scrollLeft / Math.max(1, track.clientWidth));
          if (i !== index) { index = i; mark(); }
        });
      }, { passive: true });
      $('[data-carousel="prev"]').addEventListener('click', function () { go(index - 1); });
      $('[data-carousel="next"]').addEventListener('click', function () { go(index + 1); });
      $('.carousel__dots').addEventListener('click', function (e) {
        var d = e.target.closest('[data-dot]');
        if (d) go(+d.getAttribute('data-dot'));
      });
      var box = $('.carousel');
      box.addEventListener('mouseenter', function () { paused = true; });
      box.addEventListener('mouseleave', function () { paused = false; });
      box.addEventListener('focusin', function () { paused = true; });
      box.addEventListener('focusout', function () { paused = false; });
      box.addEventListener('pointerdown', function () { paused = true; });
      box.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowLeft') { e.preventDefault(); go(index - 1); }
        if (e.key === 'ArrowRight') { e.preventDefault(); go(index + 1); }
      });
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (en) { inView = en[0].isIntersecting; }, { threshold: 0.4 }).observe(box);
      }
      window.addEventListener('resize', function () { go(index, false); });
      start();
    }
    return { init: init, sync: function () { if (track) go(Math.min(index, slides().length - 1), false); } };
  })();

  /* ---------- Lightbox ---------- */
  var lightbox = (function () {
    var dlg, img, text, count, list = [], idx = 0, opener = null;
    function show(i, anim) {
      idx = (i + list.length) % list.length;
      var g = list[idx], m = IMG[g.img];
      var base = 'assets/img/' + g.img;
      img.removeAttribute('srcset');
      if (m && m.widths) img.srcset = m.widths.map(function (x) { return base + '-' + x + '.webp ' + x + 'w'; }).concat(base + '.webp ' + m.w + 'w').join(', ');
      img.sizes = '100vw';
      img.src = base + '.webp';
      if (m) { img.width = m.w; img.height = m.h; }
      img.alt = g.caption + ' - MC Thúy Vy';
      text.textContent = g.caption;
      count.textContent = fmt(T.gallery.counter, { i: idx + 1, n: list.length });
      if (anim) { img.classList.remove('is-swapping'); void img.offsetWidth; img.classList.add('is-swapping'); }
      [1, -1].forEach(function (d) { var n = list[(idx + d + list.length) % list.length]; if (n) { var p = new Image(); p.src = 'assets/img/' + n.img + '.webp'; } });
      var single = list.length < 2;
      $$('[data-lb]', dlg).forEach(function (b) { b.hidden = single; });
    }
    function open(items, i) {
      if (!items.length) return;
      list = items; opener = doc.activeElement;
      show(i, false);
      if (!dlg.open) dlg.showModal();
    }
    function init() {
      dlg = $('#lightbox'); img = $('.lightbox__img', dlg); text = $('.lightbox__text', dlg); count = $('.lightbox__count', dlg);
      $('[data-lb="prev"]', dlg).addEventListener('click', function () { show(idx - 1, true); });
      $('[data-lb="next"]', dlg).addEventListener('click', function () { show(idx + 1, true); });
      $('[data-close]', dlg).addEventListener('click', function () { dlg.close(); });
      dlg.addEventListener('click', function (e) { if (e.target === dlg || e.target.classList.contains('lightbox__figure')) dlg.close(); });
      dlg.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowLeft') show(idx - 1, true);
        if (e.key === 'ArrowRight') show(idx + 1, true);
      });
      dlg.addEventListener('close', function () { if (opener && opener.focus) opener.focus({ preventScroll: true }); });
      // Vuốt trên mobile
      var x0 = null, y0 = null;
      dlg.addEventListener('pointerdown', function (e) { x0 = e.clientX; y0 = e.clientY; });
      dlg.addEventListener('pointerup', function (e) {
        if (x0 === null) return;
        var dx = e.clientX - x0, dy = e.clientY - y0;
        x0 = null;
        if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.3 && list.length > 1) show(idx + (dx < 0 ? 1 : -1), true);
      });
      dlg.addEventListener('pointercancel', function () { x0 = null; });
    }
    return { init: init, open: open };
  })();

  /* ---------- Field dialog ---------- */
  var fieldDialog = (function () {
    var dlg, opener = null, items = [];
    function open(id) {
      var f = T.fields.items.filter(function (x) { return x.id === id; })[0];
      if (!f) return;
      opener = doc.activeElement;
      items = T.gallery.items.filter(function (g) { return g.field === id; });
      var photos = items.length ? items : [{ img: 'fields/' + id, caption: f.title }];
      render('field-dialog',
        '<p class="eyebrow">' + esc(T.fields.eyebrow) + '</p>' +
        '<h2 class="modal__title" id="field-dialog-title">' + esc(f.title) + '</h2>' +
        '<p class="modal__summary">' + esc(f.summary) + '</p>' +
        '<div class="modal__grid"><div class="modal__events"><h3>' + esc(T.fields.dialogEvents) + '</h3><ul>' +
        f.events.map(function (e) { return '<li>' + icon('star') + '<span>' + esc(e) + '</span></li>'; }).join('') +
        '</ul></div><div class="modal__photos">' +
        photos.map(function (g, i) {
          return '<button type="button" data-modal-shot="' + i + '" aria-label="' + esc(T.gallery.open + ': ' + g.caption) + '">' +
            imgTag(g.img, { alt: g.caption + ' - MC Thúy Vy', sizes: '(min-width: 768px) 420px, 92vw' }) + '</button>';
        }).join('') + '</div></div>' +
        '<div class="modal__actions">' +
        (items.length ? '<button type="button" class="btn btn--ghost" data-to-gallery="' + esc(id) + '">' + esc(T.fields.viewInGallery) + '</button>' : '') +
        '<a class="btn btn--primary" href="#contact" data-close-link>' + icon('calendar') + '<span>' + esc(T.nav.book) + '</span></a></div>');
      items = photos;
      dlg.showModal();
      $('.modal__inner', dlg).scrollTop = 0;
      $('.modal__close', dlg).focus();
    }
    function init() {
      dlg = $('#field-dialog');
      dlg.addEventListener('click', function (e) {
        if (e.target === dlg) { dlg.close(); return; }
        if (e.target.closest('[data-close]')) { dlg.close(); return; }
        var shot = e.target.closest('[data-modal-shot]');
        if (shot) { lightbox.open(items, +shot.getAttribute('data-modal-shot')); return; }
        var tg = e.target.closest('[data-to-gallery]');
        if (tg) {
          opener = null; dlg.close(); setFilter(tg.getAttribute('data-to-gallery'));
          $('#events').scrollIntoView({ behavior: reduceMotion.matches ? 'auto' : 'smooth' });
          return;
        }
        if (e.target.closest('[data-close-link]')) { opener = null; dlg.close(); }
      });
      dlg.addEventListener('close', function () { if (opener && opener.focus) opener.focus({ preventScroll: true }); });
    }
    return { init: init, open: open };
  })();

  /* ---------- Booking form ---------- */
  function initForm() {
    var form = $('#booking-form');
    if (!form) return;
    var status = $('.booking__status', form);
    var submit = $('button[type="submit"]', form);
    var mailBtn = $('.booking__mailto', form);

    function values() {
      var fd = new FormData(form);
      return {
        fd: fd,
        lines: [
          [T.contact.form.name, fd.get('name')],
          [T.contact.form.company, fd.get('company')],
          [T.contact.form.reach, fd.get('contact')],
          [T.contact.form.date, fd.get('event_date')],
          [T.contact.form.type, fd.get('event_type')],
          [T.contact.form.location, fd.get('location')],
          [T.contact.form.message, fd.get('message')]
        ].filter(function (p) { return p[1]; }).map(function (p) { return p[0] + ': ' + p[1]; })
      };
    }
    function mailto(lines) {
      return 'mailto:' + (isSet(CFG.EMAIL) ? CFG.EMAIL.trim() : '') + '?subject=' + encodeURIComponent(T.contact.form.subject) +
        '&body=' + encodeURIComponent(lines.join('\n'));
    }
    function setStatus(msg, kind) {
      status.textContent = msg;
      status.className = 'booking__status' + (kind ? ' is-' + kind : '');
    }
    form.addEventListener('input', function (e) {
      if (e.target.getAttribute('aria-invalid') === 'true' && e.target.value.trim()) e.target.removeAttribute('aria-invalid');
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (form._gotcha && form._gotcha.value) return;
      var invalid = $$('[required]', form).filter(function (f) { return !f.value.trim(); });
      $$('[required]', form).forEach(function (f) {
        if (invalid.indexOf(f) > -1) f.setAttribute('aria-invalid', 'true'); else f.removeAttribute('aria-invalid');
      });
      if (invalid.length) { setStatus(T.contact.form.invalid, 'error'); invalid[0].focus(); return; }

      var v = values();
      if (!isSet(CFG.FORM_ENDPOINT)) {
        if (isSet(CFG.EMAIL)) {
          setStatus(T.contact.form.mailtoNote, '');
          window.location.href = mailto(v.lines);
        } else {
          setStatus(T.contact.pending, 'error');
        }
        return;
      }
      submit.disabled = true;
      submit.textContent = T.contact.form.sending;
      setStatus('', '');
      v.fd.append('_subject', T.contact.form.subject);
      v.fd.append('language', lang);
      fetch(CFG.FORM_ENDPOINT.trim(), { method: 'POST', body: v.fd, headers: { Accept: 'application/json' } })
        .then(function (r) { if (!r.ok) throw new Error(r.status); })
        .then(function () { form.reset(); setStatus(T.contact.form.success, 'ok'); mailBtn.hidden = true; })
        .catch(function () {
          setStatus(T.contact.form.error, 'error');
          if (isSet(CFG.EMAIL)) { mailBtn.href = mailto(v.lines); mailBtn.hidden = false; }
        })
        .then(function () { submit.disabled = false; submit.textContent = T.contact.form.submit; });
    });
  }

  /* ---------- Delegated clicks ---------- */
  function initClicks() {
    doc.addEventListener('click', function (e) {
      var t = e.target;
      var lb = t.closest('.lang__btn');
      if (lb) { setLang(lb.getAttribute('data-lang')); return; }

      var play = t.closest('[data-play]');
      if (play) { playVideo(play.getAttribute('data-play')); return; }

      var reel = t.closest('[data-action="play-showreel"]');
      if (reel) {
        e.preventDefault();
        $('#showreel').scrollIntoView({ behavior: reduceMotion.matches ? 'auto' : 'smooth' });
        if (videoRegistry.reel && videoRegistry.reel.type !== 'link') playVideo('reel');
        return;
      }

      var card = t.closest('[data-field]');
      if (card && card.classList.contains('card')) { fieldDialog.open(card.getAttribute('data-field')); return; }

      var chip = t.closest('[data-filter]');
      if (chip) { setFilter(chip.getAttribute('data-filter')); return; }

      var shot = t.closest('[data-shot]');
      if (shot) {
        var visible = T.gallery.items.filter(function (g) { return currentFilter === 'all' || g.field === currentFilter; });
        var g = T.gallery.items[+shot.getAttribute('data-shot')];
        lightbox.open(visible, Math.max(0, visible.indexOf(g)));
      }
    });
  }

  /* ---------- Curtain intro ---------- */
  function initCurtain() {
    var c = $('.curtain-intro');
    if (!c) return;
    var done = function () { c.classList.add('is-done'); };
    if (reduceMotion.matches) { done(); return; }
    c.addEventListener('animationend', done, { once: true });
    setTimeout(done, 2600);
  }

  /* ---------- Boot ---------- */
  function boot() {
    initCurtain();
    initHeader();
    initClicks();
    lightbox.init();
    fieldDialog.init();
    carousel.init();
    initForm();
    $$('[data-reveal]').forEach(observeReveal);
    var bar = $('.mobile-bar');
    if (bar) requestAnimationFrame(function () { bar.classList.add('is-visible'); });

    var manifest = loadJSON('data/images.json').catch(function () { return {}; });
    Promise.all([loadLang(lang), manifest]).then(function (r) {
      T = r[0]; IMG = r[1] || {};
      renderAll();
      updateSchema();
      if (location.hash && location.hash.length > 1) {
        var target = doc.getElementById(location.hash.slice(1));
        if (target) target.scrollIntoView();
      }
    }).catch(function (err) {
      console.error(err);
      if (lang !== 'vi') { lang = 'vi'; loadLang('vi').then(function (d) { T = d; renderAll(); }); }
    });
  }

  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', boot); else boot();
})();
