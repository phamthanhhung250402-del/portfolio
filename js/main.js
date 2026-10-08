(function () {
  "use strict";

  var CONFIG = window.SITE_CONFIG || {};
  var CATEGORIES = {
    launch: "Launch & Sự kiện",
    ads: "Quảng cáo sản phẩm",
    service: "Dịch vụ & Talking-head",
    creative: "Sáng tạo & Giải trí"
  };
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  /* ---------- Định dạng ---------- */
  function formatViews(n) {
    if (n >= 999500) return trimZero((n / 1e6).toFixed(1)) + "M";
    if (n >= 1000) return Math.round(n / 1000) + "K";
    return String(n);
  }
  function trimZero(s) { return s.replace(/\.0$/, "").replace(".", ","); }
  function formatDuration(sec) {
    var m = Math.floor(sec / 60), s = sec % 60;
    return m + ":" + (s < 10 ? "0" : "") + s;
  }
  function formatDate(iso) {
    var p = String(iso || "").split("-");
    return p.length === 3 ? p[2] + "/" + p[1] + "/" + p[0] : "";
  }
  function isUnset(v) { return !v || /\{\{/.test(v); }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function hash(str) {
    var h = 0;
    for (var i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) >>> 0;
    return h;
  }

  /* ---------- Áp cấu hình liên hệ & giá ---------- */
  function applyConfig() {
    var zalo = String(CONFIG.zalo || "").replace(/[^\d+]/g, "");
    var links = {
      zalo: isUnset(CONFIG.zalo) ? null : "https://zalo.me/" + zalo,
      email: isUnset(CONFIG.email) ? null : "mailto:" + CONFIG.email + "?subject=" + encodeURIComponent("Brief video - "),
      linkedin: CONFIG.linkedin || null
    };
    $$("[data-contact]").forEach(function (a) {
      var url = links[a.getAttribute("data-contact")];
      if (url) {
        a.href = url;
      } else {
        // Chưa điền thông tin: nút cuộn tới mục Liên hệ thay vì mở link hỏng
        a.href = "#lien-he";
        a.removeAttribute("target");
      }
      if (a.getAttribute("data-contact") === "email") a.removeAttribute("target");
    });
    $$("[data-contact-text]").forEach(function (el) {
      var v = CONFIG[el.getAttribute("data-contact-text")];
      if (v) el.textContent = v;
    });
    var services = CONFIG.services || {};
    $$("[data-price]").forEach(function (el) {
      var s = services[el.getAttribute("data-price")];
      if (s && s.price) el.textContent = s.price;
    });
    $$("[data-delivery]").forEach(function (el) {
      var s = services[el.getAttribute("data-delivery")];
      if (s && s.delivery) el.textContent = s.delivery;
    });
    var year = $("#year");
    if (year) year.textContent = new Date().getFullYear();
  }

  /* ---------- Header & menu ---------- */
  function initHeader() {
    var header = $(".site-header");
    var toggle = $(".menu-toggle");
    var nav = $("#site-nav");
    var fab = $(".fab-zalo");

    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    function setMenu(open) {
      toggle.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("is-open", open);
      $(".sr-only", toggle).textContent = open ? "Đóng menu" : "Mở menu";
    }
    toggle.addEventListener("click", function () {
      setMenu(toggle.getAttribute("aria-expanded") !== "true");
    });
    $$("a", nav).forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setMenu(false);
        toggle.focus();
      }
    });
    document.addEventListener("click", function (e) {
      if (nav.classList.contains("is-open") && !nav.contains(e.target) && !toggle.contains(e.target)) setMenu(false);
    });

    if (!("IntersectionObserver" in window)) return;

    // Đánh dấu mục menu đang xem
    var navLinks = $$("a", nav);
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        navLinks.forEach(function (a) {
          var active = a.getAttribute("href") === "#" + en.target.id;
          a.classList.toggle("is-active", active);
          if (active) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current");
        });
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    navLinks.forEach(function (a) {
      var sec = $(a.getAttribute("href"));
      if (sec) spy.observe(sec);
    });

    // Ẩn nút Zalo nổi khi đang ở mục Liên hệ (tránh trùng nút)
    var contact = $("#lien-he");
    if (fab && contact) {
      new IntersectionObserver(function (entries) {
        fab.classList.toggle("is-hidden", entries[0].isIntersecting);
      }, { threshold: 0.25 }).observe(contact);
    }
  }

  /* ---------- Đếm số ---------- */
  function initCountUp() {
    var els = $$(".countup");
    if (reduceMotion || !("IntersectionObserver" in window)) return;
    var fmt = function (el, v) {
      var d = +el.getAttribute("data-decimals") || 0;
      return (el.getAttribute("data-prefix") || "") +
        v.toFixed(d).replace(".", ",") +
        (el.getAttribute("data-suffix") || "");
    };
    var run = function (el) {
      var to = parseFloat(el.getAttribute("data-to"));
      var dur = 1600, start = null;
      var step = function (t) {
        if (start === null) start = t;
        var p = Math.min((t - start) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 4);
        el.textContent = fmt(el, to * eased);
        if (p < 1) requestAnimationFrame(step);
        else el.textContent = fmt(el, to);
      };
      requestAnimationFrame(step);
    };
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          io.unobserve(en.target);
          run(en.target);
        }
      });
    }, { threshold: 0.6 });
    els.forEach(function (el) {
      el.setAttribute("aria-label", el.textContent);
      io.observe(el);
    });
  }

  /* ---------- Hiệu ứng xuất hiện ---------- */
  var revealObserver = null;
  function reveal(els) {
    if (reduceMotion || !("IntersectionObserver" in window)) return;
    if (!revealObserver) {
      revealObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) {
            en.target.classList.add("is-visible");
            revealObserver.unobserve(en.target);
          }
        });
      }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    }
    els.forEach(function (el, i) {
      el.classList.add("reveal");
      el.style.transitionDelay = (i % 4) * 70 + "ms";
      revealObserver.observe(el);
    });
  }

  /* ---------- Card clip ---------- */
  var ICON_PLAY = '<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M8 5.6v12.8a.8.8 0 0 0 1.2.7l10-6.4a.8.8 0 0 0 0-1.4l-10-6.4A.8.8 0 0 0 8 5.6z" fill="currentColor"/></svg>';
  var ICON_EYE = '<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M12 5C6.5 5 2.7 9.3 1.6 11.4a1.3 1.3 0 0 0 0 1.2C2.7 14.7 6.5 19 12 19s9.3-4.3 10.4-6.4a1.3 1.3 0 0 0 0-1.2C21.3 9.3 17.5 5 12 5zm0 11a4 4 0 1 1 0-8 4 4 0 0 1 0 8z" fill="currentColor"/></svg>';

  function mediaHtml(clip, opts) {
    opts = opts || {};
    var h = hash(clip.id);
    var style = "--gx:" + (15 + (h % 70)) + "%;--gy:" + (8 + ((h >> 3) % 40)) + "%;" +
      "--angle:" + (140 + ((h >> 5) % 60)) + "deg;--ga:" + (0.2 + ((h >> 7) % 20) / 100).toFixed(2);
    var inner;
    if (clip.thumb) {
      inner = '<img src="' + escapeHtml(clip.thumb) + '" alt="Ảnh bìa clip: ' + escapeHtml(clip.title) + '" width="540" height="960"' +
        (opts.eager ? ' fetchpriority="high"' : ' loading="lazy"') + ' decoding="async">';
    } else {
      inner = '<span class="clip-cover" style="' + style + '" aria-hidden="true"></span>' +
        '<span class="cover-cat" aria-hidden="true">' + escapeHtml(CATEGORIES[clip.category] || "") + '</span>';
    }
    return '<span class="clip-media">' + inner +
      '<span class="clip-scrim" aria-hidden="true"></span>' +
      (opts.noPlay ? "" : '<span class="cover-play" aria-hidden="true">' + ICON_PLAY + '</span>') +
      (opts.badges === false ? "" :
        '<span class="badge badge-views" aria-hidden="true">' + ICON_EYE + formatViews(clip.views) + '</span>' +
        '<span class="badge badge-duration" aria-hidden="true">' + formatDuration(clip.duration) + '</span>' +
        '<span class="clip-title">' + escapeHtml(clip.title) + '</span>') +
      '</span>';
  }

  function cardLabel(clip) {
    return "Xem clip: " + clip.title + ". " + formatViews(clip.views) + " lượt xem, thời lượng " + formatDuration(clip.duration);
  }

  /* ---------- Lưới clip + bộ lọc ---------- */
  function initClips(clips) {
    var grid = $("#clip-grid");
    var countEl = $("#clip-count");
    var sorted = clips.slice().sort(function (a, b) { return b.views - a.views; });

    grid.innerHTML = sorted.map(function (c) {
      return '<li data-category="' + escapeHtml(c.category) + '">' +
        '<button type="button" class="clip-card" data-id="' + escapeHtml(c.id) + '" aria-label="' + escapeHtml(cardLabel(c)) + '">' +
        mediaHtml(c) + '</button></li>';
    }).join("");
    grid.classList.remove("is-loading");

    $$(".clip-card", grid).forEach(function (btn) {
      btn.addEventListener("click", function () { openLightbox(btn.getAttribute("data-id"), btn); });
    });

    var chips = $$(".chip");
    chips.forEach(function (chip) {
      var f = chip.getAttribute("data-filter");
      var n = f === "all" ? clips.length : clips.filter(function (c) { return c.category === f; }).length;
      chip.insertAdjacentHTML("beforeend", '<span class="count" aria-hidden="true">' + n + "</span>");
      chip.addEventListener("click", function () {
        chips.forEach(function (c) { c.setAttribute("aria-pressed", String(c === chip)); });
        var shown = 0;
        $$("li", grid).forEach(function (li) {
          var match = f === "all" || li.getAttribute("data-category") === f;
          li.hidden = !match;
          if (match) shown++;
        });
        countEl.textContent = "Đang hiển thị " + shown + " clip " + (f === "all" ? "" : "thuộc nhóm " + CATEGORIES[f]);
        // Giữ thanh lọc trong tầm nhìn khi danh sách ngắn lại
        var bar = $("#filter-bar");
        var top = $("#clip").getBoundingClientRect().top;
        if (top < -bar.offsetHeight) {
          var target = window.scrollY + grid.getBoundingClientRect().top - bar.offsetHeight - $(".site-header").offsetHeight - 16;
          window.scrollTo({ top: target, behavior: reduceMotion ? "auto" : "smooth" });
        }
        if (window.innerWidth < 768) chip.scrollIntoView({ inline: "center", block: "nearest", behavior: reduceMotion ? "auto" : "smooth" });
      });
    });

    reveal($$("li", grid));
  }

  /* ---------- Showreel / slideshow ---------- */
  function initShowreel(clips) {
    var screen = $("#showreel-screen");
    if (!screen) return;

    if (CONFIG.showreel) {
      var v = document.createElement("video");
      v.muted = true;
      v.loop = true;
      v.playsInline = true;
      v.setAttribute("muted", "");
      v.setAttribute("playsinline", "");
      v.setAttribute("aria-label", "Showreel video của Phạm Thành Hưng");
      v.preload = "metadata";
      if (reduceMotion) {
        v.controls = true;
      } else {
        v.autoplay = true;
        v.setAttribute("autoplay", "");
      }
      v.addEventListener("error", function () { buildSlideshow(screen, clips); }, true);
      var src = document.createElement("source");
      src.src = CONFIG.showreel;
      src.type = "video/mp4";
      src.addEventListener("error", function () { buildSlideshow(screen, clips); });
      v.appendChild(src);
      screen.innerHTML = "";
      screen.appendChild(v);
      return;
    }
    buildSlideshow(screen, clips);
  }

  function buildSlideshow(screen, clips) {
    if (screen.getAttribute("data-mode") === "slides") return;
    screen.setAttribute("data-mode", "slides");
    var featured = clips.filter(function (c) { return c.featured; }).slice(0, 4);
    if (!featured.length) featured = clips.slice(0, 4);
    if (!featured.length) return;

    screen.innerHTML =
      '<span class="showreel-label">Clip nổi bật</span>' +
      '<div class="slides">' + featured.map(function (c, i) {
        return '<button type="button" class="slide' + (i === 0 ? " is-active" : "") + '" data-id="' + escapeHtml(c.id) + '" aria-label="' + escapeHtml(formatViews(c.views) + " lượt xem " + c.title + ". Bấm để xem clip") + '">' +
          mediaHtml(c, { badges: false, eager: i === 0 }) +
          '<span class="slide-info" aria-hidden="true">' +
          '<span class="slide-views">' + formatViews(c.views) + '<small>lượt xem</small></span>' +
          '<span class="slide-title" style="display:block">' + escapeHtml(c.title) + '</span>' +
          '</span></button>';
      }).join("") + '</div>' +
      '<div class="slide-dots" aria-hidden="true">' + featured.map(function (_, i) {
        return '<span' + (i === 0 ? ' class="is-active"' : "") + "></span>";
      }).join("") + "</div>";

    var slides = $$(".slide", screen);
    var dots = $$(".slide-dots span", screen);
    slides.forEach(function (s) {
      s.addEventListener("click", function () { openLightbox(s.getAttribute("data-id"), s); });
    });
    if (reduceMotion || slides.length < 2) return;

    var idx = 0, timer = null, visible = true, hovering = false;
    function go(n) {
      slides[idx].classList.remove("is-active");
      dots[idx].classList.remove("is-active");
      idx = (n + slides.length) % slides.length;
      slides[idx].classList.add("is-active");
      dots[idx].classList.add("is-active");
    }
    function tick() {
      stop();
      if (visible && !hovering && !document.hidden) timer = setTimeout(function () { go(idx + 1); tick(); }, 3200);
    }
    function stop() { clearTimeout(timer); }
    screen.addEventListener("mouseenter", function () { hovering = true; stop(); });
    screen.addEventListener("mouseleave", function () { hovering = false; tick(); });
    screen.addEventListener("focusin", function () { hovering = true; stop(); });
    screen.addEventListener("focusout", function () { hovering = false; tick(); });
    document.addEventListener("visibilitychange", tick);
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) { visible = en[0].isIntersecting; tick(); }).observe(screen);
    }
    tick();
  }

  /* ---------- Lightbox ---------- */
  var clipById = {};
  var dialog, frame, panel, lastFocus;

  function openLightbox(id, trigger) {
    var clip = clipById[id];
    if (!clip || !dialog) return;
    lastFocus = trigger || document.activeElement;

    $("#lb-title").textContent = clip.title;
    $("#lb-meta").innerHTML = "<strong>" + formatViews(clip.views) + "</strong> lượt xem · " +
      formatDuration(clip.duration) + " · " + formatDate(clip.date);
    $("#lb-tiktok").href = clip.tiktok;
    var fb = $("#lb-facebook");
    if (clip.facebook) { fb.href = clip.facebook; fb.hidden = false; } else { fb.hidden = true; }

    // Chỉ tạo iframe khi người xem bấm mở
    frame.innerHTML = '<span class="lb-loading">Đang tải video…</span>';
    var iframe = document.createElement("iframe");
    iframe.src = "https://www.tiktok.com/player/v1/" + encodeURIComponent(clip.id) +
      "?autoplay=1&music_info=1&description=0&rel=0&native_context_menu=0&closed_caption=1";
    iframe.title = "Video TikTok: " + clip.title;
    iframe.allow = "autoplay; fullscreen; encrypted-media; picture-in-picture";
    iframe.setAttribute("allowfullscreen", "");
    iframe.referrerPolicy = "strict-origin-when-cross-origin";
    frame.appendChild(iframe);

    panel.style.transform = "";
    if (typeof dialog.showModal === "function") dialog.showModal();
    else dialog.setAttribute("open", "");
    document.body.classList.add("lb-open");
    $("#lb-close").focus();
  }

  function closeLightbox() {
    if (!dialog) return;
    if (dialog.open && typeof dialog.close === "function") dialog.close();
    else onClosed();
  }

  function onClosed() {
    dialog.removeAttribute("open");
    frame.innerHTML = ""; // dừng phát video
    panel.style.transform = "";
    document.body.classList.remove("lb-open");
    if (lastFocus && document.contains(lastFocus)) lastFocus.focus({ preventScroll: true });
  }

  function initLightbox() {
    dialog = $("#lightbox");
    frame = $("#lb-frame");
    panel = $("#lb-panel");
    if (!dialog) return;

    $("#lb-close").addEventListener("click", closeLightbox);
    dialog.addEventListener("close", onClosed);
    // Bấm ra nền tối để đóng
    dialog.addEventListener("click", function (e) { if (e.target === dialog) closeLightbox(); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && dialog.hasAttribute("open")) closeLightbox();
    });

    // Vuốt xuống để đóng (mobile)
    var startY = 0, dy = 0, startT = 0, dragging = false;
    panel.addEventListener("touchstart", function (e) {
      if (window.innerWidth >= 768 || e.touches.length !== 1) return;
      dragging = true;
      startY = e.touches[0].clientY;
      startT = Date.now();
      dy = 0;
      panel.classList.add("is-dragging");
    }, { passive: true });
    panel.addEventListener("touchmove", function (e) {
      if (!dragging) return;
      dy = Math.max(0, e.touches[0].clientY - startY);
      panel.style.transform = "translateY(" + dy + "px)";
    }, { passive: true });
    var end = function () {
      if (!dragging) return;
      dragging = false;
      panel.classList.remove("is-dragging");
      var fast = dy > 40 && dy / Math.max(1, Date.now() - startT) > 0.6;
      if (dy > 110 || fast) {
        panel.style.transform = "translateY(100%)";
        setTimeout(closeLightbox, reduceMotion ? 0 : 220);
      } else {
        panel.style.transform = "";
      }
    };
    panel.addEventListener("touchend", end);
    panel.addEventListener("touchcancel", end);
  }

  /* ---------- Khởi động ---------- */
  function init() {
    applyConfig();
    initHeader();
    initCountUp();
    initLightbox();
    reveal($$(".section-head, .service, .process li, .tl-item, .contact-list li"));

    var grid = $("#clip-grid");
    grid.classList.add("is-loading");
    grid.innerHTML = new Array(9).join('<li aria-hidden="true"><span class="clip-media"></span></li>');

    fetch("data/clips.json")
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (all) {
        var clips = all.filter(function (c) { return !c.placeholder; });
        clips.forEach(function (c) { clipById[c.id] = c; });
        initClips(clips);
        initShowreel(clips);
      })
      .catch(function (err) {
        console.warn("Không tải được data/clips.json:", err);
        grid.classList.remove("is-loading");
        grid.innerHTML = '<li style="grid-column:1/-1"><p class="section-desc">Không tải được danh sách clip. Xem trực tiếp tại <a href="https://www.tiktok.com/@topzone.official" target="_blank" rel="noopener">TikTok TopZone Official</a>.</p></li>';
        initShowreel([]);
      });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
