#!/usr/bin/env python3
"""Synchronise la section publications de publications.html avec l'API HAL
et régénère assets/publications.bib.

À configurer une fois : IDHAL (votre identifiant HAL, visible dans l'URL de
votre profil) et NOM (votre nom de famille, pour le surlignage des auteurs).
Le script ne modifie que le bloc entre les marqueurs PUBLICATIONS:AUTO.
En cas d'échec de l'API, les fichiers ne sont pas modifiés."""

import html, json, os, re, sys, unicodedata, urllib.parse, urllib.request

IDHAL  = os.environ.get("HAL_IDHAL", "MON_ID_HAL")   # ex. "jbarra"
NOM    = os.environ.get("HAL_NOM", "Barra")          # surlignage dans la liste d'auteurs
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE   = os.path.join(RACINE, "publications.html")
BIB    = os.path.join(RACINE, "assets", "publications.bib")

DEBUT, FIN = "<!-- PUBLICATIONS:AUTO:DEBUT -->", "<!-- PUBLICATIONS:AUTO:FIN -->"

URL_API = ("https://api.archives-ouvertes.fr/search/?q=authIdHal_s:{id}"
           "&rows=200&wt=json&sort=producedDateY_i%20desc"
           "&fl=title_s,authFullName_s,journalTitle_s,conferenceTitle_s,"
           "bookTitle_s,doiId_s,halId_s,type_s,producedDateY_i"
           ).format(id=urllib.parse.quote(IDHAL))

# type_s HAL -> data-type des filtres du site (adaptez si vous ajoutez un filtre)
TYPES  = {"ART": "journal", "COMM": "conference", "POSTER": "conference",
          "COUV": "journal", "OUV": "journal"}
# type_s HAL -> type d'entrée BibTeX
BIBTEX = {"ART": "article", "COMM": "inproceedings", "POSTER": "inproceedings",
          "COUV": "incollection", "OUV": "book", "THESE": "phdthesis"}

def premier(v, defaut=""):
    if isinstance(v, list):
        return v[0] if v else defaut
    return v if v else defaut

def sans_accents(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if not unicodedata.combining(c))

def interroger_hal():
    req = urllib.request.Request(URL_API,
                                 headers={"User-Agent": "cdurand.github.io-sync/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("response", {}).get("docs", [])

def bloc_bibtex(p, annee):
    titre   = premier(p.get("title_s"), "Sans titre")
    auteurs = p.get("authFullName_s") or ["Anonyme"]
    etype   = BIBTEX.get(p.get("type_s", ""), "misc")
    champ   = "journal" if etype in ("article", "book") else "booktitle"
    lieu    = premier(p.get("journalTitle_s") or p.get("conferenceTitle_s")
                      or p.get("bookTitle_s"), "")
    doi, halid = premier(p.get("doiId_s")), premier(p.get("halId_s"))
    cle = "{}{}{}".format(sans_accents(auteurs[0].split()[-1]).lower(), annee,
                          (halid.replace("hal-", "") or "x").lower())
    lignes = ["@{}{{{},".format(etype, cle),
              "  title  = {{{}}},".format(titre),
              "  author = {{{}}},".format(" and ".join(auteurs))]
    if lieu:
        lignes.append("  {} = {{{}}},".format(champ, lieu))
    lignes.append("  year   = {{{}}},".format(annee))
    if doi:
        lignes.append("  doi    = {{{}}},".format(doi))
    if halid:
        lignes.append("  url    = {{https://hal.science/{}}}".format(halid))
    lignes.append("}")
    return "\n".join(lignes)

def bloc_html(p, annee):
    titre   = html.escape(premier(p.get("title_s"), "Sans titre"))
    auteurs = p.get("authFullName_s") or []
    dtype   = TYPES.get(p.get("type_s", ""), "journal")
    lieu    = premier(p.get("journalTitle_s") or p.get("conferenceTitle_s")
                      or p.get("bookTitle_s"), "")
    doi, halid = premier(p.get("doiId_s")), premier(p.get("halId_s"))
    a_html = ", ".join(
        '<span class="me">{}</span>'.format(html.escape(a)) if NOM.lower() in a.lower()
        else html.escape(a) for a in auteurs)
    actions = []
    if halid:
        actions.append('<a class="button" href="https://hal.science/{}">HAL</a>'.format(halid))
    if doi:
        actions.append('<a class="button" href="https://doi.org/{}">DOI</a>'.format(html.escape(doi)))
    if halid:
        actions.append('<a class="button" href="https://hal.science/{}/document">PDF</a>'.format(halid))
    actions.append('<button class="button copy-bibtex" type="button">BibTeX</button>')
    bibtex = bloc_bibtex(p, annee).replace("</script", "<\\/script")
    return ('<article class="pub" data-type="{dtype}">\n'
            '  <p class="title">{titre}</p>\n'
            '  <p>{auteurs}</p>\n'
            '  <p class="venue">{lieu}{sep} {annee}</p>\n'
            '  <div class="actions">\n    {actions}\n  </div>\n'
            '  <script type="text/plain" class="bibtex">{bibtex}</script>\n'
            '</article>').format(dtype=dtype, titre=titre, auteurs=a_html,
                                 lieu=html.escape(lieu), sep="," if lieu else "",
                                 annee=annee, actions="\n    ".join(actions),
                                 bibtex=bibtex)

def generer(docs):
    par_annee = {}
    for p in docs:
        par_annee.setdefault(premier(p.get("producedDateY_i"), ""), []).append(p)
    morceaux = []
    for annee in sorted(par_annee, reverse=True):
        morceaux.append("<h2>{}</h2>".format(annee))
        morceaux.extend(bloc_html(p, annee) for p in par_annee[annee])
    return DEBUT + "\n" + "\n".join(morceaux) + "\n" + FIN

def main():
    docs = interroger_hal()
    if not docs:
        sys.exit("HAL : aucune publication pour authIdHal_s=%s — vérifiez l'identifiant." % IDHAL)
    nouveau = generer(docs)
    with open(PAGE, encoding="utf-8") as f:
        page = f.read()
    if DEBUT not in page or FIN not in page:
        sys.exit("Marqueurs PUBLICATIONS:AUTO absents de publications.html.")
    page2 = re.sub(re.escape(DEBUT) + r".*?" + re.escape(FIN),
                   lambda _: nouveau, page, flags=re.S)
    if page2 != page:
        with open(PAGE, "w", encoding="utf-8") as f:
            f.write(page2)
    bibs = "\n\n".join(bloc_bibtex(p, premier(p.get("producedDateY_i"), "")) for p in docs)
    os.makedirs(os.path.dirname(BIB), exist_ok=True)
    with open(BIB, "w", encoding="utf-8") as f:
        f.write(bibs + "\n")
    print("OK : %d publications — page %s, publications.bib régénéré."
          % (len(docs), "mise à jour" if page2 != page else "inchangée"))

if __name__ == "__main__":
    main()