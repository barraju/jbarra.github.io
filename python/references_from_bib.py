#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Régénère la section publications de publications.html depuis
assets/publications.bib (bibliothèque standard uniquement).

- Ne modifie QUE le bloc entre les marqueurs PUBLICATIONS:AUTO:DEBUT/FIN :
  les filtres, la recherche et le reste de la page sont conservés.
- Le HTML généré reprend les classes du site, donc le filtre, la recherche
  et la copie BibTeX continuent de fonctionner.
- En cas de problème (marqueurs absents, bib vide), rien n'est écrit.

A faire à chaque nouvelle publi
Usage : python3 scripts/gen_publications.py [--bib CHEMIN] [--page CHEMIN]
"""

import argparse, html, os, re, sys

# ----------------- Configuration -----------------
NOM    = "Barra"     # votre nom : surligné dans la liste des auteurs
PRESET = "fr"        # "fr" = site français (.titre/.moi/.lieu/.bouton),
                     # "en" = site anglais (title/me/venue/button)
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PRESETS = {
    "fr": {
        "titre": "titre", "moi": "moi", "lieu": "lieu", "bouton": "bouton",
        "copie": "copier-bibtex", "type_journal": "revue", "lien": "Lien",
        "sans_date": "s.d.", "sans_titre": "Sans titre",
        "labels": {"phdthesis": "Thèse de doctorat",
                   "mastersthesis": "Mémoire de master",
                   "techreport": "Rapport technique",
                   "book": "Ouvrage", "incollection": "Chapitre d'ouvrage",
                   "misc": ""},
    },
    "en": {
        "titre": "title", "moi": "me", "lieu": "venue", "bouton": "button",
        "copie": "copy-bibtex", "type_journal": "journal", "lien": "Link",
        "sans_date": "n.d.", "sans_titre": "Untitled",
        "labels": {"phdthesis": "Ph.D. thesis",
                   "mastersthesis": "M.Sc. thesis",
                   "techreport": "Technical report",
                   "book": "Book", "incollection": "Book chapter",
                   "misc": ""},
    },
}

# type BibTeX -> data-type du filtre du site. Tout type non listé est
# classé par défaut dans le filtre « revues/journals » pour rester visible
# sous l'un des filtres existants (Toutes / Conférences / Revues).
TYPES_SITE = {"inproceedings": "conference", "conference": "conference"}

DEBUT, FIN = "<!-- PUBLICATIONS:AUTO:DEBUT -->", "<!-- PUBLICATIONS:AUTO:FIN -->"

# ----------------- Mini-parseur BibTeX -----------------
def sauter_bloc(texte, pos):
    """Index juste après l'accolade fermante qui équilibre texte[pos] == '{'."""
    profondeur, i = 0, pos
    while i < len(texte):
        if texte[i] == "{":
            profondeur += 1
        elif texte[i] == "}":
            profondeur -= 1
            if profondeur == 0:
                return i + 1
        i += 1
    return len(texte)

def lire_valeur(texte, pos, fin):
    if pos >= fin:
        return "", pos
    c = texte[pos]
    if c == "{":
        f = sauter_bloc(texte, pos)
        return texte[pos + 1:f - 1], f
    if c == '"':
        f = texte.find('"', pos + 1)
        if f == -1 or f > fin:
            f = fin
        return texte[pos + 1:f], f + 1
    m = re.match(r"[^,\s}]+", texte[pos:fin])
    return (m.group(0), pos + m.end()) if m else ("", pos)

def lire_bibtex(texte):
    """Renvoie une liste d'entrées {type, cle, brut, champs}.
    Gère les entrées standards ; ignore @comment/@preamble/@string."""
    entrees, i, n = [], 0, len(texte)
    while i < n:
        debut = texte.find("@", i)
        if debut == -1:
            break
        m = re.match(r"@(\w+)\s*\{", texte[debut:])
        if not m:
            i = debut + 1
            continue
        etype = m.group(1).lower()
        ouvrante = debut + m.end() - 1
        fermante = sauter_bloc(texte, ouvrante)
        brut = texte[debut:fermante]
        if etype in ("comment", "preamble", "string"):
            i = fermante
            continue
        corps = texte[ouvrante + 1:fermante - 1]
        mvirgule = corps.find(",")
        cle = corps[:mvirgule].strip() if mvirgule != -1 else corps.strip()
        champs = {}
        pos = mvirgule + 1 if mvirgule != -1 else 0
        while pos < len(corps):
            mc = re.match(r"\s*(\w+)\s*=\s*", corps[pos:])
            if not mc:
                pos += 1
                continue
            nom = mc.group(1).lower()
            pos += mc.end()
            val, pos = lire_valeur(corps, pos, len(corps))
            champs[nom] = val.strip()
            pos += re.match(r"\s*,?\s*", corps[pos:]).end()
        entrees.append({"type": etype, "cle": cle, "brut": brut, "champs": champs})
        i = fermante
    return entrees

# ----------------- Nettoyage LaTeX minimal -----------------
ACCENTS = {"'a": "á", "'e": "é", "'i": "í", "'o": "ó", "'u": "ú", "'y": "ý",
           "'A": "Á", "'E": "É", "'I": "Í", "'O": "Ó", "'U": "Ú",
           "`a": "à", "`e": "è", "`i": "ì", "`o": "ò", "`u": "ù",
           "^a": "â", "^e": "ê", "^i": "î", "^o": "ô", "^u": "û",
           '"a': "ä", '"e': "ë", '"i': "ï", '"o': "ö", '"u': "ü",
           "~n": "ñ", "~N": "Ñ"}

def nettoyer(s):
    s = re.sub(r"\\c\{?\s*c\s*\}?", "ç", s)
    s = s.replace(r"\ss", "ß")
    s = re.sub(r"\\(['`^\"~])(\w)",
               lambda m: ACCENTS.get(m.group(1) + m.group(2), m.group(0)), s)
    s = re.sub(r"\\(?:emph|textit|textbf|textsc|url)\{([^{}]*)\}", r"\1", s)
    s = (s.replace("\\&", "&").replace("\\%", "%").replace("\\_", "_")
          .replace("---", "—").replace("--", "–").replace("~", " "))
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()

def auteurs_liste(auteurs):
    if not auteurs:
        return []
    parties = re.split(r"\s+and\s+", auteurs, flags=re.I)
    return [nettoyer(p) for p in parties if p.strip()]

def annee_de(champs):
    for cle in ("year", "date"):
        v = champs.get(cle)
        if v:
            m = re.search(r"\d{4}", v)
            if m:
                return m.group(0)
    return ""

# ----------------- Génération HTML -----------------
def segments_venue(e, preset):
    c, t = e["champs"], e["type"]
    if t == "article":
        parties = []
        if c.get("journal"): parties.append(nettoyer(c["journal"]))
        if c.get("volume"):  parties.append("vol. " + nettoyer(c["volume"]))
        if c.get("number"):  parties.append("no. " + nettoyer(c["number"]))
        if c.get("pages"):   parties.append("pp. " + nettoyer(c["pages"]))
        return parties
    for src in ("booktitle", "school", "institution", "publisher", "howpublished"):
        if c.get(src):
            return [nettoyer(c[src])]
    return []

def lien(cls, href, label):
    return '<a class="{}" href="{}">{}</a>'.format(
        cls, html.escape(href, quote=True), html.escape(label))

def boutons_de(e, preset):
    c, cls, b = e["champs"], preset["bouton"], []
    url, doi = (c.get("url") or "").strip(), (c.get("doi") or "").strip()
    if "hal.science" in url:
        b.append(lien(cls, url, "HAL"))
        b.append(lien(cls, url.rstrip("/") + "/document", "PDF"))
    elif "arxiv.org" in url:
        b.append(lien(cls, url, "arXiv"))
    elif url:
        b.append(lien(cls, url, preset["lien"]))
    if doi and "doi.org" not in url:
        b.append(lien(cls, "https://doi.org/" + doi, "DOI"))
    pdf = c.get("pdf") or ""
    mpdf = re.search(r"([^:;]+\.pdf)", pdf)
    if mpdf and not any(">PDF<" in x for x in b):
        href = mpdf.group(1) if mpdf.group(1).startswith("http") \
               else "assets/" + os.path.basename(mpdf.group(1))
        b.append(lien(cls, href, "PDF"))
    b.append('<button class="{c} {copie}" type="button">BibTeX</button>'
             .format(c=cls, copie=preset["copie"]))
    return b

def article_html(e, preset):
    c = e["champs"]
    annee = annee_de(c)
    dtype = TYPES_SITE.get(e["type"], preset["type_journal"])
    cle = re.sub(r"[^A-Za-z0-9_-]", "", e["cle"]) or "pub"
    titre = nettoyer(c.get("title")) or preset["sans_titre"]
    auteurs = auteurs_liste(c.get("author"))
    a_html = ", ".join(
        '<span class="{moi}">{a}</span>'.format(moi=preset["moi"], a=html.escape(x))
        if NOM.lower() in x.lower() else html.escape(x) for x in auteurs)
    label = preset["labels"].get(e["type"], "")
    segments = (([label] if label else []) + segments_venue(e, preset)
                + ([annee] if annee else []))
    brut = e["brut"].replace("</script", "<\\/script")
    return ('<article class="pub" data-type="{dtype}" id="{cle}">\n'
            '  <p class="{titre}">{titre_txt}</p>\n'
            '  <p>{auteurs}</p>\n'
            '  <p class="{lieu}">{venue}</p>\n'
            '  <div class="actions">\n    {boutons}\n  </div>\n'
            '  <script type="text/plain" class="bibtex">{brut}</script>\n'
            '</article>').format(dtype=dtype, cle=cle, titre=preset["titre"],
                                 titre_txt=html.escape(titre), auteurs=a_html,
                                 lieu=preset["lieu"], venue=html.escape(", ".join(segments)),
                                 boutons="\n    ".join(boutons_de(e, preset)), brut=brut)

def generer(entrees, preset):
    vues, deja_vus = [], set()
    for e in entrees:
        if e["cle"] and e["cle"] in deja_vus:
            print("avertissement : clé dupliquée ignorée :", e["cle"])
            continue
        deja_vus.add(e["cle"])
        vues.append(e)
    par_annee = {}
    for e in vues:
        par_annee.setdefault(annee_de(e["champs"]) or preset["sans_date"], []).append(e)
    morceaux = []
    for annee in sorted(par_annee, reverse=True):
        morceaux.append("<h2>{}</h2>".format(html.escape(annee)))
        morceaux.extend(article_html(e, preset) for e in par_annee[annee])
    return DEBUT + "\n" + "\n\n".join(morceaux) + "\n" + FIN

# ----------------- Main -----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bib", default=os.path.join(RACINE, "assets", "publications.bib"))
    ap.add_argument("--page", default=os.path.join(RACINE, "publications.html"))
    args = ap.parse_args()
    preset = PRESETS[PRESET]

    if not os.path.exists(args.bib):
        sys.exit("Fichier BibTeX introuvable : %s" % args.bib)
    with open(args.bib, encoding="utf-8") as f:
        entrees = lire_bibtex(f.read())
    if not entrees:
        sys.exit("Aucune entrée BibTeX trouvée dans %s" % args.bib)

    with open(args.page, encoding="utf-8") as f:
        page = f.read()
    if DEBUT not in page or FIN not in page:
        sys.exit("Marqueurs PUBLICATIONS:AUTO absents de %s — encadrez la "
                 "section à générer, puis relancez." % args.page)

    nouveau = generer(entrees, preset)
    page2 = re.sub(re.escape(DEBUT) + r".*?" + re.escape(FIN),
                   lambda _: nouveau, page, flags=re.S)
    if page2 != page:
        with open(args.page, "w", encoding="utf-8") as f:
            f.write(page2)
    annees = sorted({annee_de(e["champs"]) for e in entrees if annee_de(e["champs"])},
                    reverse=True)
    print("OK : %d publications (%s) — %s"
          % (len(entrees),
             " → ".join([annees[-1], annees[0]]) if annees else "sans date",
             "page mise à jour" if page2 != page else "page inchangée"))

if __name__ == "__main__":
    main()