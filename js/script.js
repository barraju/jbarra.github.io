/* cdurand.github.io — lightweight interactions, no dependency
   1) light/dark theme (persisted)  2) collapsible news
   3) publication filters + search  4) copy BibTeX
   5) active nav link               6) footer "last updated" */
(function () {
  "use strict";
  var root = document.documentElement;

  /* 1. Theme */
  var themeBtn = document.getElementById("theme-toggle");
  function currentTheme() {
    return root.dataset.theme ||
      (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }
  function paintThemeBtn() {
    if (themeBtn) themeBtn.textContent = currentTheme() === "dark" ? "☀️" : "🌙";
  }
  if (themeBtn) {
    paintThemeBtn();
    themeBtn.addEventListener("click", function () {
      root.dataset.theme = currentTheme() === "dark" ? "light" : "dark";
      try { localStorage.setItem("theme", root.dataset.theme); } catch (e) { /* storage unavailable */ }
      paintThemeBtn();
    });
  }

  /* 2. News: show the first VISIBLE items, toggle the rest */
  var newsList = document.getElementById("news-list");
  var newsBtn = document.getElementById("news-toggle");
  if (newsList && newsBtn) {
    var VISIBLE = 3;
    var items = Array.prototype.slice.call(newsList.children);
    if (items.length > VISIBLE) {
      var collapsed = true;
      items.slice(VISIBLE).forEach(function (li) { li.hidden = true; });
      newsBtn.hidden = false;
      newsBtn.addEventListener("click", function () {
        collapsed = !collapsed;
        items.slice(VISIBLE).forEach(function (li) { li.hidden = collapsed; });
        newsBtn.textContent = collapsed ? "Show all news ↓" : "Show fewer news ↑";
      });
    }
  }

  /* 3. Publications: type filters + text search, combined */
  var filterBtns = Array.prototype.slice.call(document.querySelectorAll(".filter"));
  var pubs = Array.prototype.slice.call(document.querySelectorAll(".pub[data-type]"));
  var searchBox = document.getElementById("pub-search");
  var noResult = document.getElementById("no-result");
  if (filterBtns.length > 0 && pubs.length > 0) {
    var activeType = "all";
    var query = "";
    function applyPubs() {
      var shown = 0;
      pubs.forEach(function (p) {
        var okType = activeType === "all" || p.getAttribute("data-type") === activeType;
        var okQuery = !query || p.textContent.toLowerCase().indexOf(query) !== -1;
        p.hidden = !(okType && okQuery);
        if (okType && okQuery) shown++;
      });
      if (noResult) noResult.hidden = shown !== 0;
    }
    filterBtns.forEach(function (b) {
      b.addEventListener("click", function () {
        filterBtns.forEach(function (x) { x.classList.toggle("active", x === b); });
        activeType = b.getAttribute("data-filter") || "all";
        applyPubs();
      });
    });
    if (searchBox) {
      searchBox.addEventListener("input", function () {
        query = searchBox.value.trim().toLowerCase();
        applyPubs();
      });
    }
  }

  /* 4. Copy BibTeX */
  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest ? ev.target.closest(".copy-bibtex") : null;
    if (!btn) return;
    var pub = btn.closest(".pub");
    var block = pub && pub.querySelector(".bibtex");
    if (!block) return;
    var text = block.textContent.replace(/^\s+|\s+$/g, "");
    function done() {
      var old = btn.textContent;
      btn.textContent = "Copied ✓";
      btn.disabled = true;
      window.setTimeout(function () { btn.textContent = old; btn.disabled = false; }, 1500);
    }
    function fallback() {
      var area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();
      try { document.execCommand("copy"); done(); } catch (e) { /* silent */ }
      document.body.removeChild(area);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, fallback);
    } else { fallback(); }
  });

  /* 5. Highlight the current page in the nav */
  var here = (location.pathname.split("/").pop() || "index.html").toLowerCase();
  Array.prototype.forEach.call(document.querySelectorAll("nav a[href]"), function (a) {
    if ((a.getAttribute("href") || "").toLowerCase() === here) {
      a.classList.add("active");
      a.setAttribute("aria-current", "page");
    }
  });

  /* 6. "Last updated" from the served file date */
  var stamps = document.querySelectorAll("[data-last-updated]");
  if (stamps.length > 0 && document.lastModified) {
    var d = new Date(document.lastModified);
    if (!isNaN(d.getTime())) {
      var label = d.toLocaleDateString("en-GB", { year: "numeric", month: "long", day: "numeric" });
      Array.prototype.forEach.call(stamps, function (el) {
        el.textContent = "Last updated " + label + ".";
      });
    }
  }
})();