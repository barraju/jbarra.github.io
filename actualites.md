---
layout: default
title: Actualités
permalink: /actualites/
---

<ul class="news">
  {% assign news = site.data.news | sort: "date" | reverse %}
  {% for n in news %}
    <li>
      <time>{{ n.date | date: "%d/%m/%Y" }}</time>
      {{ n.text | markdownify | remove: "<p>" | remove: "</p>" }}
    </li>
  {% endfor %}
</ul>
