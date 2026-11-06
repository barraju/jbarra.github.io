---
layout: default
title: Contact
order: 6
nav: true
permalink: /contact/
---

N'hésitez pas à me contacter pour toute question sur mes travaux, une
collaboration ou une proposition de stage.

- ✉️ **E-mail** : <a href="mailto:{{ site.email }}">{{ site.email }}</a>
- 🏢 **Bureau** : bâtiment B, bureau 214
- 📍 **Adresse** : {{ site.lab }}, {{ site.university }}, 1 avenue de l'Université

## Me retrouver ailleurs

<ul>
  {% if site.orcid %}<li><a href="https://orcid.org/{{ site.orcid }}">ORCID</a></li>{% endif %}
  {% if site.scholar_id %}<li><a href="https://scholar.google.com/citations?user={{ site.scholar_id }}">Google Scholar</a></li>{% endif %}
  {% if site.github_username %}<li><a href="https://github.com/{{ site.github_username }}">GitHub</a></li>{% endif %}
  {% if site.linkedin_username %}<li><a href="https://www.linkedin.com/in/{{ site.linkedin_username }}">LinkedIn</a></li>{% endif %}
</ul>
