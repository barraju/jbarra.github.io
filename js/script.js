/* cdurand.github.io — interactions légères, sans dépendance
   1) bascule thème clair/sombre (mémorisée)  2) actualités repliables
   3) filtre des publications                 4) copie du BibTeX */
(function () {
  "use strict";

  /* ---------- 1. Thème clair / sombre ---------- */
  var racine = document.documentElement;
  var boutonTheme = document.getElementById("bascule-theme");

  function themeEffectif() {
    return racine.dataset.theme ||
      (window.matchMedia("(prefers-color-scheme: dark)").matches ? "sombre" : "clair");
  }
  function majBoutonTheme() {
    if (boutonTheme) boutonTheme.textContent = themeEffectif() === "sombre" ? "☀️" : "🌙";
  }
  if (boutonTheme) {
    majBoutonTheme();
    boutonTheme.addEventListener("click", function () {
      var suivant = themeEffectif() === "sombre" ? "clair" : "sombre";
      racine.dataset.theme = suivant;
      try { localStorage.setItem("theme", suivant); } catch (e) { /* stockage indisponible */ }
      majBoutonTheme();
    });
  }

  /* ---------- 2. Actualités : voir tout / réduire ---------- */
  var listeActus = document.getElementById("liste-actus");
  var basculeActus = document.getElementById("bascule-actus");
  if (listeActus && basculeActus) {
    var visibles = 2;
    var items = Array.prototype.slice.call(listeActus.children);
    if (items.length > visibles) {
      var replie = true;
      items.slice(visibles).forEach(function (li) { li.hidden = true; });
      basculeActus.hidden = false;
      basculeActus.addEventListener("click", function () {
        replie = !replie;
        items.slice(visibles).forEach(function (li) { li.hidden = replie; });
        basculeActus.textContent = replie ? "Voir toutes les actualités ↓" : "Réduire les actualités ↑";
      });
    }
  }

  /* ---------- 3. Filtre des publications ---------- */
  var filtres = document.querySelectorAll(".filtre");
  var pubs = document.querySelectorAll(".pub[data-type]");
  if (filtres.length > 0 && pubs.length > 0) {
    filtres.forEach(function (bouton) {
      bouton.addEventListener("click", function () {
        filtres.forEach(function (b) { b.classList.toggle("actif", b === bouton); });
        var cible = bouton.getAttribute("data-filtre");
        pubs.forEach(function (p) {
          p.hidden = (cible !== "toutes") && (p.getAttribute("data-type") !== cible);
        });
      });
    });
  }

  /* ---------- 4. Copier le BibTeX d'une publication ---------- */
  document.addEventListener("click", function (ev) {
    var bouton = ev.target.closest ? ev.target.closest(".copier-bibtex") : null;
    if (!bouton) return;
    var pub = bouton.closest(".pub");
    var bloc = pub && pub.querySelector(".bibtex");
    if (!bloc) return;
    var texte = bloc.textContent.replace(/^\s+|\s+$/g, "");

    function confirmation() {
      var ancien = bouton.textContent;
      bouton.textContent = "Copié ✓";
      bouton.disabled = true;
      window.setTimeout(function () { bouton.textContent = ancien; bouton.disabled = false; }, 1500);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(texte).then(confirmation, function () { secours(texte, confirmation); });
    } else {
      secours(texte, confirmation);
    }
  });

  function secours(texte, apres) {
    var zone = document.createElement("textarea");
    zone.value = texte;
    zone.setAttribute("readonly", "");
    zone.style.position = "fixed";
    zone.style.opacity = "0";
    document.body.appendChild(zone);
    zone.select();
    try { document.execCommand("copy"); apres(); } catch (e) { /* échec silencieux */ }
    document.body.removeChild(zone);
  }
})();