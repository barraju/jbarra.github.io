---
layout: default
title: Enseignement
order: 4
nav: true
permalink: /enseignement/
---

Dans le cadre de mon contrat doctoral, j'assure un service de 64 h
équivalent TD par an à l'{{ site.university }}.

{% assign grand_total = 0 %}
{% for y in site.data.teaching %}
{% assign year_total = 0 %}
{% for c in y.courses %}
{% assign year_total = year_total | plus: c.hours %}
{% endfor %}
{% assign grand_total = grand_total | plus: year_total %}

<h2>{{ y.year }} <span class="meta">— {{ year_total }} h</span></h2>

<table class="courses">
  <thead>
    <tr><th>Module</th><th>Niveau</th><th>Type</th><th>Volume</th><th>Établissement</th></tr>
  </thead>
  <tbody>
    {% for c in y.courses %}
    <tr>
      <td>{{ c.name }}</td><td>{{ c.level }}</td><td>{{ c.kind }}</td>
      <td>{{ c.hours }} h</td><td>{{ c.institution }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% endfor %}

<p><strong>Total cumulé depuis le début de la thèse : {{ grand_total }} h.</strong></p>
