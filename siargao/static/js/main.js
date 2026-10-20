// SiargaoHotels.ph — small, dependency-free interactions (Bootstrap's bundle handles tabs, dropdowns, modals).
(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------------------------------------------------- header: solid once you scroll off the hero */
  const header = $(".site-header");
  if (header && header.classList.contains("header-overlay")) {
    const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 40);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    // An opened mobile menu needs the solid header too
    $("#mainNav")?.addEventListener("show.bs.collapse", () => header.classList.add("scrolled"));
    $("#mainNav")?.addEventListener("hidden.bs.collapse", onScroll);
  }

  /* ---------------------------------------------------------- search tabs: sliding underline */
  const ink = $(".search-tab-ink");
  if (ink) {
    const moveInk = () => {
      const active = $(".search-tab.active");
      if (!active) return;
      ink.style.width = `${active.offsetWidth}px`;
      ink.style.transform = `translateX(${active.offsetLeft}px)`;
    };
    $$(".search-tab").forEach((t) => t.addEventListener("shown.bs.tab", moveInk));
    window.addEventListener("resize", moveInk);
    document.fonts?.ready.then(moveInk);
    moveInk();
  }

  /* ---------------------------------------------------------- guests picker (+/- and summary) */
  $$(".guests-picker").forEach((picker) => {
    const summary = $(".guests-summary", picker);
    const field = (n) => $(`input[name="${n}"]`, picker);
    const refresh = () => {
      const a = +field("adults").value, c = +field("children").value, r = field("rooms");
      summary.textContent = `${a} Adult${a !== 1 ? "s" : ""} - ${c} Child${c !== 1 ? "ren" : ""}` +
        (r ? ` · ${r.value} Room${+r.value !== 1 ? "s" : ""}` : "");
    };
    $$(".qty button", picker).forEach((btn) => btn.addEventListener("click", () => {
      const input = $("input", btn.parentElement);
      input.value = Math.min(Math.max((+input.value || 0) + (+btn.dataset.step), +input.min || 0), +input.max || 99);
      input.dispatchEvent(new Event("change", { bubbles: true }));
    }));
    $$("input", picker).forEach((i) => i.addEventListener("change", refresh));
  });

  /* ---------------------------------------------------------- keep end date after start date */
  $$("form").forEach((form) => {
    const start = $('input[name="start"]', form), end = $('input[name="end"]', form);
    if (!start || !end) return;
    start.addEventListener("change", () => {
      if (!start.value) return;
      const d = new Date(start.value);
      d.setDate(d.getDate() + 1);
      const min = d.toISOString().slice(0, 10);
      end.min = min;
      if (!end.value || end.value < min) { end.value = min; end.dispatchEvent(new Event("change", { bubbles: true })); }
    });
  });

  $$(".auto-submit").forEach((el) => el.addEventListener("change", () => el.form.submit()));

  /* ---------------------------------------------------------- listing cards: browse photos in place */
  $$(".listing-card").forEach((card) => {
    const track = $(".card-track", card);
    const dots = $$(".card-dots span", card);
    if (!track || dots.length < 2) return;
    let i = 0;
    const go = (n) => {
      i = (n + dots.length) % dots.length;
      track.style.transform = `translateX(-${i * 100}%)`;
      dots.forEach((d, k) => d.classList.toggle("on", k === i));
    };
    $(".card-nav.prev", card).addEventListener("click", () => go(i - 1));
    $(".card-nav.next", card).addEventListener("click", () => go(i + 1));
    let x0 = null;  // swipe on touch screens
    track.addEventListener("touchstart", (e) => { x0 = e.touches[0].clientX; }, { passive: true });
    track.addEventListener("touchend", (e) => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 35) { e.preventDefault(); go(dx < 0 ? i + 1 : i - 1); }
      x0 = null;
    });
  });

  /* ---------------------------------------------------------- saved places (hearts) */
  const KEY = "sh_saved";
  const readSaved = () => { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch { return []; } };
  const writeSaved = (ids) => { try { localStorage.setItem(KEY, JSON.stringify(ids)); } catch { /* private mode */ } };
  const paintHearts = () => {
    const saved = readSaved();
    $$(".heart").forEach((h) => {
      const on = saved.includes(+h.dataset.id);
      h.setAttribute("aria-pressed", on);
      $("i", h).className = on ? "bi bi-heart-fill" : "bi bi-heart";
    });
    const badge = $(".wish-count");
    if (badge) { badge.textContent = saved.length; badge.hidden = !saved.length; }
  };
  document.addEventListener("click", (e) => {
    const h = e.target.closest(".heart");
    if (!h) return;
    e.preventDefault();
    const id = +h.dataset.id;
    const saved = readSaved();
    writeSaved(saved.includes(id) ? saved.filter((x) => x !== id) : [id, ...saved]);
    h.classList.remove("pop"); void h.offsetWidth; h.classList.add("pop");
    paintHearts();
  });
  paintHearts();
  // Wishlist page: the list lives in this browser, so load it on arrival
  const wl = $("#wishlist");
  if (wl && !wl.dataset.loaded) {
    location.replace(`${location.pathname}?ids=${readSaved().join(",")}`);
  }

  /* ---------------------------------------------------------- island map */
  const mapData = $("#town-data");
  if (mapData) {
    const towns = Object.fromEntries(JSON.parse(mapData.textContent).map((t) => [t.slug, t]));
    const archives = JSON.parse($("#town-archives").textContent);
    const card = $(".town-card");
    const set = (sel, prop, val) => { $(sel, card)[prop] = val; };
    const show = (slug, animate = true) => {
      const t = towns[slug];
      if (!t) return;
      $$(".pin").forEach((p) => p.classList.toggle("active", p.dataset.slug === slug));
      $(".town-img", card).src = t.image;
      $(".town-img", card).alt = `${t.name}, Siargao`;
      set(".town-name", "textContent", t.name);
      set(".town-blurb", "textContent", t.blurb);
      [["stays", t.hotels], ["tours", t.tours], ["cars", t.cars]].forEach(([k, n]) => {
        const a = $(`.t-${k}`, card);
        $("strong", a).textContent = n;
        a.href = `${archives[k]}?location=${slug}`;
        a.classList.toggle("is-zero", !n);
      });
      const link = $(".town-link", card);
      link.href = t.url;
      link.textContent = `Explore ${t.name}`;
      if (animate && !reduceMotion) { card.classList.remove("swap"); void card.offsetWidth; card.classList.add("swap"); }
    };
    $$(".pin").forEach((pin) => {
      pin.addEventListener("click", () => show(pin.dataset.slug));
      pin.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); show(pin.dataset.slug); }
      });
      pin.addEventListener("mouseenter", () => { if (window.matchMedia("(hover: hover)").matches) show(pin.dataset.slug); });
    });
    show(($(".pin.active") || $(".pin"))?.dataset.slug, false);
  }

  /* ---------------------------------------------------------- listing page: live price estimate */
  const book = $("#book-form");
  if (book && book.dataset.quote) {
    const box = $(".quote", book), desc = $(".quote-desc", book), total = $(".quote-total", book), err = $(".quote-error", book);
    let timer, seq = 0;
    const update = () => {
      const fd = new FormData(book);
      const start = fd.get("start"), end = fd.get("end");
      if (!start || (book.querySelector('input[name="end"]') && (!end || end <= start))) { box.hidden = true; return; }
      const params = new URLSearchParams();
      ["listing_id", "room_id", "start", "end", "adults", "children", "rooms"].forEach((k) => fd.get(k) && params.set(k, fd.get(k)));
      const mine = ++seq;
      box.hidden = false; box.classList.add("loading");
      fetch(`${book.dataset.quote}?${params}`)
        .then((r) => r.json())
        .then((q) => {
          if (mine !== seq) return;
          box.classList.remove("loading");
          err.hidden = !q.error;
          if (q.error) { err.textContent = q.error; return; }
          desc.textContent = q.desc;
          total.textContent = q.total_fmt;
        })
        .catch(() => { box.hidden = true; });
    };
    book.addEventListener("change", () => { clearTimeout(timer); timer = setTimeout(update, 150); });
    update();
  }

  /* ---------------------------------------------------------- phones: booking bar until the booking box is on screen */
  const bar = $(".mobile-book"), target = $("#booking");
  if (bar && target && "IntersectionObserver" in window) {
    let pastTop = false, boxVisible = false;
    const paint = () => bar.classList.toggle("show", pastTop && !boxVisible);
    new IntersectionObserver(([e]) => { boxVisible = e.isIntersecting; paint(); }).observe(target);
    window.addEventListener("scroll", () => { pastTop = window.scrollY > 500; paint(); }, { passive: true });
    $("a", bar).addEventListener("click", (e) => {
      e.preventDefault();
      target.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
    });
  }

  /* ---------------------------------------------------------- listing page odds and ends */
  $$(".choose-room").forEach((btn) => btn.addEventListener("click", () => {
    const sel = $("#room-select");
    if (sel) { sel.value = btn.dataset.room; sel.dispatchEvent(new Event("change", { bubbles: true })); }
    $("#book-form")?.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "center" });
  }));
  $$(".open-inquiry").forEach((a) => a.addEventListener("click", (e) => {
    e.preventDefault();
    const tab = $('[data-bs-target="#inquiry-pane"]');
    if (tab && window.bootstrap) { bootstrap.Tab.getOrCreateInstance(tab).show(); tab.scrollIntoView({ behavior: "smooth", block: "center" }); }
  }));
  $$(".gallery-item").forEach((a) => a.addEventListener("click", () => {
    const el = $("#galleryCarousel");
    if (el && window.bootstrap) bootstrap.Carousel.getOrCreateInstance(el).to(+a.dataset.index);
  }));
})();
