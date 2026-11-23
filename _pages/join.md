---
title: " "
permalink: /join/
layout: opera
---

# Join us

OPERA is a research group at the [Institut des Géosciences de l'Environnement](https://www.ige-grenoble.fr/?lang=en) (IGE), Université Grenoble Alpes & CNRS, in Grenoble, France. We work on open computational earth and climate science — process-based models, data-driven and hybrid approaches, and the systems that tie them together.

## Open positions

{% assign positions = site.data.positions | where: "status", "open" %}

{% if positions.size > 0 %}
  {% include cards_grid.html items=positions %}
{% else %}
<p class="opera-notice">
  There are no open positions at the moment.
</p>
<p>
  We are always happy to hear from talented people: if you would like to do a PhD, a postdoc
  or an internship with us, get in touch with the <a href="{{ '/people/' | relative_url }}">team members</a> whose
  research is closest to yours — spontaneous applications are welcome anytime. New positions
  are also expected to open soon, so watch this page.
</p>
{% endif %}

## Practical information

- recruitment for permanent positions at IGE goes through [CNRS](https://cnrs.fr) and [Université Grenoble Alpes](https://www.univ-grenoble-alpes.fr),
- PhD positions are typically advertised in spring for a start in autumn,
- internships (Master level) are often available — write to us with your CV and interests,
- we support open science: your work with us will be public, reproducible and free.
