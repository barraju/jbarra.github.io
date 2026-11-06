---
layout: default
title: Publications
order: 3
nav: true
permalink: /publications/
---

{% assign me_bold = site.author | prepend: "<strong>" | append: "</strong>" %}
{% assign groups = site.data.publications | group_by_exp: "p", "p.year" | sort: "name" | reverse %}

{% for g in groups %}
<h2>{{ g.name }}</h2>
{% for p in g.items %}
{% include publication.html pub=p me=me_bold %}
{% endfor %}
{% endfor %}

<p>
  Retrouvez ces publications sur
  {% if site.scholar_id %}<a href="https://scholar.google.com/citations?user={{ site.scholar_id }}">Google Scholar</a>{% endif %}
  {% if site.scholar_id and site.orcid %} et {% endif %}
  {% if site.orcid %}<a href="https://orcid.org/{{ site.orcid }}">ORCID</a>{% endif %}.
</p>
<p><a class="btn" href="{{ '/publications.bib' | relative_url }}">Exporter tout le BibTeX</a></p>
