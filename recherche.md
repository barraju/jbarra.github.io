---
layout: default
title: Recherche
order: 2
nav: true
permalink: /recherche/
---

Ma thèse porte sur la **commande prédictive robuste** (MPC) de systèmes
énergétiques soumis à des incertitudes de prévision. Je m'intéresse en
particulier aux garanties de stabilité et de faisabilité des lois de
commande, ainsi qu'à leur implémentation temps réel.

## Thématiques

- Commande prédictive robuste et *tube-based* MPC
- Estimation d'état et observateurs distribués
- Systèmes énergétiques : micro-réseaux, stockage, *smart grids*
- Optimisation sous incertitudes (LMIs, programmation semi-définie)

## Projets

{% for p in site.data.projects %}
<div class="card">
  <h3>{{ p.title }}</h3>
  <p class="meta">{{ p.period }} · {{ p.role }}{% if p.funding %} · {{ p.funding }}{% endif %}</p>
  <p>{{ p.description }}</p>
</div>
{% endfor %}

## Mots-clés

`MPC` · `commande robuste` · `observateurs` · `systèmes non linéaires` · `micro-réseaux` · `CasADi`
