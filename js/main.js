(function () {
  "use strict";

  var CONFIG = window.SITE_CONFIG || {};
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
    if (!sec) return "";
    var m = Math.floor(sec / 60), s = sec % 60;
    return m + ":" + (s < 10 ? "0" : "") + s;
  }
  function formatDate(iso) {
    var p = String(iso || "").split("-");
    return p.length === 3 ? p[2] + "/" + p[1] + "/" + p[0] : "";
  }
  function isUnset(v) { return !v || /\{\{/.test(v); }
  function escapeHtml(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function hash(str) {
    var h = 0;
    for (var i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) >>> 0;
    return h;
  }
  function slug(s) {
    return String(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/đ/g, "d").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  }
  function getJSON(url) {
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error(url + " HTTP " + r.status);
      return r.json();
    });
  }
  function visible(list) { return (list || []).filter(function (x) { return !x.placeholder; }); }

  /* ---------- Áp cấu hình liên hệ & giá ---------- */
  function applyConfig() {
    var zaloDigits = String(CONFIG.zalo || "").replace(/\D/g, "").replace(/^84/, "0");
    var links = {
      messenger: CONFIG.messenger || CONFIG.facebook || null,
      facebook: CONFIG.facebook || null,
      zalo: isUnset(CONFIG.zalo) ? null : "https://zalo.me/" + zaloDigits,
      email: isUnset(CONFIG.email) ? null : "mailto:" + CONFIG.email + "?subject=" + encodeURIComponent("Brief - "),
      linkedin: CONFIG.linkedin || null
    };
    $$("[data-contact]").forEach(function (a) {
      var url = links[a.getAttribute("data-contact")];
      if (url) {
        a.href = url;
      } else {
        a.href = "#lien-he";
        a.removeAttribute("target");
      }
      if (a.getAttribute("data-contact") === "email") a.removeAttribute("target");
    });
    $$("[data-contact-text]").forEach(function (el) {
      var v = CONFIG[el.getAttribute("data-contact-text")];
      if (!isUnset(v)) el.textContent = v;
    });
    var emailItem = $('[data-contact-item="email"]');
    if (emailItem) emailItem.hidden = isUnset(CONFIG.email);

    if (CONFIG.socialPage) {
      $$("[data-social-page]").forEach(function (a) {
        a.href = CONFIG.socialPage.url;
        if (!a.classList.contains("btn")) a.textContent = CONFIG.socialPage.name;
      });
    }

    var services = CONFIG.services || {};
    $$("[data-price]").forEach(function (el) {
      var s = services[el.getAttribute("data-price")];
      if (s && !isUnset(s.price)) el.innerHTML = "Giá từ <strong>" + escapeHtml(s.price) + "</strong>";
    });
    $$("[data-delivery]").forEach(function (el) {
      var s = services[el.getAttribute("data-delivery")];
      if (s && s.delivery) el.textContent = s.delivery;
    });

    var ads = CONFIG.ads || {};
    $$("[data-ads-metric]").forEach(function (box) {
      var m = ads[box.getAttribute("data-ads-metric")];
      if (!m || isUnset(m.value)) return;
      $("[data-ads-value]", box).textContent = m.value;
      if (m.label) $("[data-ads-label]", box).textContent = m.label;
      if (m.note && $("[data-ads-note]", box)) $("[data-ads-note]", box).textContent = m.note;
      box.hidden = false;
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

    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
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

    var contact = $("#lien-he");
    if (fab && contact) {
      new IntersectionObserver(function (entries) {
        fab.classList.toggle("is-hidden", entries[0].isIntersecting);
      }, { threshold: 0.25 }).observe(contact);
    }
  }

  /* ---------- Đếm số ---------- */
  var countObserver = null;
  function countFormat(el, v) {
    var d = +el.getAttribute("data-decimals") || 0;
    return (el.getAttribute("data-prefix") || "") +
      trimZero(v.toFixed(d)).replace(/,0+$/, "") +
      (el.getAttribute("data-suffix") || "");
  }
  function runCount(el) {
    var to = parseFloat(el.getAttribute("data-to"));
    if (isNaN(to)) return;
    if (reduceMotion || !("IntersectionObserver" in window)) {
      el.textContent = countFormat(el, to);
      return;
    }
    var dur = 1600, start = null;
    var step = function (t) {
      if (start === null) start = t;
      var p = Math.min((t - start) / dur, 1);
      el.textContent = countFormat(el, to * (1 - Math.pow(1 - p, 4)));
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = countFormat(el, to);
    };
    requestAnimationFrame(step);
  }
  function observeCount(el) {
    if (reduceMotion || !("IntersectionObserver" in window)) { runCount(el); return; }
    if (!countObserver) {
      countObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) {
            countObserver.unobserve(en.target);
            runCount(en.target);
          }
        });
      }, { threshold: 0.6 });
    }
    el.setAttribute("aria-label", countFormat(el, parseFloat(el.getAttribute("data-to"))));
    countObserver.observe(el);
  }
  function initCountUp() {
    $$(".countup[data-to]").forEach(observeCount);
  }

  // Đặt số cho một ô đếm: tự chọn đơn vị M hoặc K
  function setCountValue(el, n, plus) {
    if (!el || !n) return;
    var big = n >= 999500;
    el.setAttribute("data-to", big ? (n / 1e6).toFixed(1) : String(Math.round(n / 1000)));
    el.setAttribute("data-decimals", big ? "1" : "0");
    el.setAttribute("data-suffix", (big ? "M" : "K") + (plus ? "+" : ""));
    el.textContent = countFormat(el, parseFloat(el.getAttribute("data-to")));
    observeCount(el);
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

  /* ---------- Card video ---------- */
  var ICON_PLAY = '<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M8 5.6v12.8a.8.8 0 0 0 1.2.7l10-6.4a.8.8 0 0 0 0-1.4l-10-6.4A.8.8 0 0 0 8 5.6z" fill="currentColor"/></svg>';
  var ICON_EYE = '<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M12 5C6.5 5 2.7 9.3 1.6 11.4a1.3 1.3 0 0 0 0 1.2C2.7 14.7 6.5 19 12 19s9.3-4.3 10.4-6.4a1.3 1.3 0 0 0 0-1.2C21.3 9.3 17.5 5 12 5zm0 11a4 4 0 1 1 0-8 4 4 0 0 1 0 8z" fill="currentColor"/></svg>';

  function mediaHtml(clip, opts) {
    opts = opts || {};
    var h = hash(clip.id);
    var style = "--gx:" + (15 + (h % 70)) + "%;--gy:" + (8 + ((h >> 3) % 40)) + "%;" +
      "--angle:" + (140 + ((h >> 5) % 60)) + "deg;--ga:" + (0.2 + ((h >> 7) % 20) / 100).toFixed(2);
    var inner;
    if (clip.thumb) {
      inner = '<img src="' + escapeHtml(clip.thumb) + '" alt="Ảnh bìa video: ' + escapeHtml(clip.title) + '" width="540" height="960"' +
        (opts.eager ? ' fetchpriority="high"' : ' loading="lazy"') + ' decoding="async">';
    } else {
      inner = '<span class="clip-cover" style="' + style + '" aria-hidden="true"></span>' +
        '<span class="cover-cat" aria-hidden="true">' + escapeHtml(clip.brand || "") + '</span>';
    }
    var badges = "";
    if (opts.badges !== false) {
      badges = '<span class="badge badge-views" aria-hidden="true">' + ICON_EYE + formatViews(clip.views) + '</span>' +
        (clip.duration ? '<span class="badge badge-duration" aria-hidden="true">' + formatDuration(clip.duration) + '</span>' : "") +
        '<span class="clip-title">' +
        (opts.metrics || "") +
        (opts.showBrand && clip.brand ? '<span class="clip-brand">' + escapeHtml(clip.brand) + '</span>' : "") +
        escapeHtml(clip.title) + '</span>';
    }
    return '<span class="clip-media">' + inner +
      '<span class="clip-scrim" aria-hidden="true"></span>' +
      '<span class="cover-play" aria-hidden="true">' + ICON_PLAY + '</span>' +
      badges + '</span>';
  }

  function cardLabel(clip) {
    return "Xem video: " + clip.title + ". " + formatViews(clip.views) + " lượt xem" +
      (clip.brand ? ", " + clip.brand : "");
  }

  function cardHtml(c, opts) {
    return '<button type="button" class="clip-card" data-id="' + escapeHtml(c.id) + '" aria-label="' + escapeHtml(cardLabel(c)) + '">' +
      mediaHtml(c, opts) + '</button>';
  }

  function bindCards(root) {
    $$(".clip-card", root).forEach(function (btn) {
      btn.addEventListener("click", function () { openLightbox(btn.getAttribute("data-id"), btn); });
    });
  }

  /* ---------- Lưới video + bộ lọc theo thương hiệu ---------- */
  function initClips(clips) {
    var grid = $("#clip-grid");
    var filters = $("#filters");
    var countEl = $("#clip-count");
    var sorted = clips.slice().sort(function (a, b) { return b.views - a.views; });

    if (!sorted.length) {
      grid.classList.remove("is-loading");
      grid.innerHTML = '<li class="grid-empty"><p class="section-desc">Video đang được cập nhật.</p></li>';
      return;
    }

    grid.innerHTML = sorted.map(function (c) {
      return '<li data-brand="' + escapeHtml(slug(c.brand || "khac")) + '">' + cardHtml(c, { showBrand: true }) + '</li>';
    }).join("");
    grid.classList.remove("is-loading");
    bindCards(grid);

    // Tạo tab lọc theo thương hiệu, xếp theo tổng lượt xem
    var brands = {};
    clips.forEach(function (c) {
      var b = c.brand || "Khác";
      brands[b] = brands[b] || { name: b, views: 0, n: 0 };
      brands[b].views += c.views;
      brands[b].n++;
    });
    var brandList = Object.keys(brands).map(function (k) { return brands[k]; })
      .sort(function (a, b) { return b.views - a.views; });
    if (brandList.length > 1) {
      filters.insertAdjacentHTML("beforeend", brandList.map(function (b) {
        return '<button type="button" class="chip" data-filter="' + escapeHtml(slug(b.name)) + '" aria-pressed="false">' + escapeHtml(b.name) + "</button>";
      }).join(""));
    } else {
      $("#filter-bar").hidden = true;
    }

    var chips = $$(".chip", filters);
    chips.forEach(function (chip) {
      var f = chip.getAttribute("data-filter");
      var n = f === "all" ? clips.length : $$('li[data-brand="' + f + '"]', grid).length;
      chip.insertAdjacentHTML("beforeend", '<span class="count" aria-hidden="true">' + n + "</span>");
      chip.addEventListener("click", function () {
        chips.forEach(function (c) { c.setAttribute("aria-pressed", String(c === chip)); });
        var shown = 0;
        $$("li", grid).forEach(function (li) {
          var match = f === "all" || li.getAttribute("data-brand") === f;
          li.hidden = !match;
          if (match) shown++;
        });
        countEl.textContent = "Đang hiển thị " + shown + " video";
        var bar = $("#filter-bar");
        if ($("#video").getBoundingClientRect().top < -bar.offsetHeight) {
          var target = window.scrollY + grid.getBoundingClientRect().top - bar.offsetHeight - $(".site-header").offsetHeight - 16;
          window.scrollTo({ top: target, behavior: reduceMotion ? "auto" : "smooth" });
        }
        if (window.innerWidth < 768) chip.scrollIntoView({ inline: "center", block: "nearest", behavior: reduceMotion ? "auto" : "smooth" });
      });
    });

    reveal($$("li", grid));
  }

  // Số liệu hero tự tính từ data/clips.json
  function initHeroStats(clips) {
    if (!clips.length) return;
    var total = clips.reduce(function (s, c) { return s + (c.views || 0); }, 0);
    var top = clips.reduce(function (m, c) { return Math.max(m, c.views || 0); }, 0);
    setCountValue($("#stat-total"), total, true);
    setCountValue($("#stat-top"), top, false);
    var count = $("#stat-count");
    if (count) count.textContent = clips.length;
  }

  /* ---------- Paid Ads ---------- */
  function initAds(list) {
    var grid = $("#ads-grid");
    list = list.slice().sort(function (a, b) { return b.views - a.views; });
    if (!list.length) return;
    $("#ads-clips-title").hidden = false;
    grid.innerHTML = list.map(function (c) {
      var m = "";
      if (!isUnset(c.cpv)) m += '<span class="metric">CPV ' + escapeHtml(c.cpv) + "</span>";
      if (!isUnset(c.cpm)) m += '<span class="metric">CPM ' + escapeHtml(c.cpm) + "</span>";
      return "<li>" + cardHtml(c, { metrics: m ? '<span class="metrics">' + m + "</span>" : "" }) + "</li>";
    }).join("");
    bindCards(grid);
    reveal($$("li", grid));
  }

  /* ---------- Bài đăng Facebook ---------- */
  function initPosts(posts) {
    var grid = $("#post-grid");
    if (!posts.length) {
      grid.innerHTML = '<li class="grid-empty"><p class="section-desc">Bài đăng đang được cập nhật.</p></li>';
      return;
    }
    grid.innerHTML = posts.map(function (p, i) {
      var title = escapeHtml(p.title || "Bài đăng Facebook");
      var body = p.image
        ? '<a class="post-image" href="' + escapeHtml(p.url) + '" target="_blank" rel="noopener"><img src="' + escapeHtml(p.image) + '" alt="' + title + '" width="600" height="750" loading="lazy" decoding="async"></a>'
        : '<div class="post-embed" data-href="' + escapeHtml(p.url) + '" data-height="' + (+p.height || 0) + '" data-title="' + title + '"><span class="post-loading">Đang tải bài đăng…</span></div>';
      return '<li class="post">' + body +
        '<div class="post-foot"><p class="post-title">' + title + '</p>' +
        '<a class="post-link" href="' + escapeHtml(p.url) + '" target="_blank" rel="noopener" aria-label="Xem bài trên Facebook: ' + title + '">Xem trên Facebook ↗</a></div></li>';
    }).join("");

    // Chỉ tạo iframe Facebook khi bài sắp cuộn tới (giữ trang nhẹ)
    var embeds = $$(".post-embed", grid);
    var load = function (box) {
      if (box.getAttribute("data-loaded")) return;
      box.setAttribute("data-loaded", "1");
      var w = Math.max(320, Math.min(750, Math.round(box.clientWidth || 400)));
      var h = +box.getAttribute("data-height") || Math.round(w * 1.55);
      var iframe = document.createElement("iframe");
      iframe.src = "https://www.facebook.com/plugins/post.php?href=" + encodeURIComponent(box.getAttribute("data-href")) +
        "&show_text=true&width=" + w;
      iframe.title = box.getAttribute("data-title");
      iframe.width = w;
      iframe.height = h;
      iframe.style.height = h + "px";
      iframe.setAttribute("scrolling", "no");
      iframe.setAttribute("frameborder", "0");
      iframe.allow = "encrypted-media; picture-in-picture";
      iframe.addEventListener("load", function () { box.classList.add("is-loaded"); });
      box.appendChild(iframe);
    };
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { io.unobserve(en.target); load(en.target); }
        });
      }, { rootMargin: "600px 0px" });
      embeds.forEach(function (b) { io.observe(b); });
    } else {
      embeds.forEach(load);
    }
    reveal($$(".post", grid));
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
    var byViews = clips.slice().sort(function (a, b) { return b.views - a.views; });
    var featured = byViews.filter(function (c) { return c.featured; }).slice(0, 4);
    if (!featured.length) featured = byViews.slice(0, 4);
    if (!featured.length) return;

    screen.innerHTML =
      '<span class="showreel-label">Video nổi bật</span>' +
      '<div class="slides">' + featured.map(function (c, i) {
        return '<button type="button" class="slide' + (i === 0 ? " is-active" : "") + '" data-id="' + escapeHtml(c.id) + '">' +
          mediaHtml(c, { badges: false, eager: i === 0 }) +
          '<span class="slide-info">' +
          '<span class="slide-views">' + formatViews(c.views) + ' <small>lượt xem</small></span>' +
          '<span class="slide-title" style="display:block">' + escapeHtml(c.title) + '</span>' +
          (c.brand ? '<span class="slide-brand">' + escapeHtml(c.brand) + '</span>' : "") +
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

    var idx = 0, timer = null, inView = true, hovering = false;
    function go(n) {
      slides[idx].classList.remove("is-active");
      dots[idx].classList.remove("is-active");
      idx = (n + slides.length) % slides.length;
      slides[idx].classList.add("is-active");
      dots[idx].classList.add("is-active");
    }
    function stop() { clearTimeout(timer); }
    function tick() {
      stop();
      if (inView && !hovering && !document.hidden) timer = setTimeout(function () { go(idx + 1); tick(); }, 3200);
    }
    screen.addEventListener("mouseenter", function () { hovering = true; stop(); });
    screen.addEventListener("mouseleave", function () { hovering = false; tick(); });
    screen.addEventListener("focusin", function () { hovering = true; stop(); });
    screen.addEventListener("focusout", function () { hovering = false; tick(); });
    document.addEventListener("visibilitychange", tick);
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) { inView = en[0].isIntersecting; tick(); }).observe(screen);
    }
    tick();
  }

  /* ---------- Lightbox ---------- */
  var clipById = {};
  var dialog, frame, panel, lastFocus;

  function tiktokId(clip) {
    var m = String(clip.tiktok || "").match(/video\/(\d+)/);
    return m ? m[1] : (/^\d+$/.test(clip.id) ? clip.id : null);
  }

  function openLightbox(id, trigger) {
    var clip = clipById[id];
    if (!clip || !dialog) return;
    var vid = tiktokId(clip);
    if (!vid) { window.open(clip.tiktok || clip.facebook, "_blank", "noopener"); return; }
    lastFocus = trigger || document.activeElement;

    $("#lb-title").textContent = clip.title;
    var meta = ["<strong>" + formatViews(clip.views) + "</strong> lượt xem"];
    if (clip.cpv && !isUnset(clip.cpv)) meta.push("CPV " + escapeHtml(clip.cpv));
    if (clip.cpm && !isUnset(clip.cpm)) meta.push("CPM " + escapeHtml(clip.cpm));
    if (clip.brand) meta.push(escapeHtml(clip.brand));
    if (clip.date) meta.push(formatDate(clip.date));
    $("#lb-meta").innerHTML = meta.join(" · ");
    $("#lb-tiktok").href = clip.tiktok;
    var fb = $("#lb-facebook");
    if (clip.facebook) { fb.href = clip.facebook; fb.hidden = false; } else { fb.hidden = true; }

    frame.innerHTML = '<span class="lb-loading">Đang tải video…</span>';
    var iframe = document.createElement("iframe");
    iframe.src = "https://www.tiktok.com/player/v1/" + vid +
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
    frame.innerHTML = "";
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
    reveal($$(".section-head, .ads-stat, .about-photos, .about-text, .skill, .service, .process li, .tl-item, .contact-list li"));

    var grid = $("#clip-grid");
    grid.classList.add("is-loading");
    grid.innerHTML = new Array(9).join('<li aria-hidden="true"><span class="clip-media"></span></li>');

    getJSON("data/clips.json")
      .then(function (all) {
        var clips = visible(all);
        clips.forEach(function (c) { clipById[c.id] = c; });
        initClips(clips);
        initHeroStats(clips);
        initShowreel(clips);
      })
      .catch(function (err) {
        console.warn("Không tải được data/clips.json:", err);
        grid.classList.remove("is-loading");
        grid.innerHTML = '<li class="grid-empty"><p class="section-desc">Không tải được danh sách video.</p></li>';
      });

    getJSON("data/posts.json")
      .then(function (all) { initPosts(visible(all)); })
      .catch(function (err) { console.warn("Không tải được data/posts.json:", err); initPosts([]); });

    getJSON("data/ads.json")
      .then(function (all) {
        var list = visible(all);
        list.forEach(function (c) { clipById[c.id] = clipById[c.id] || c; });
        initAds(list);
      })
      .catch(function (err) { console.warn("Không tải được data/ads.json:", err); });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
