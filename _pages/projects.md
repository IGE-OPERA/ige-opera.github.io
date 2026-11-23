---
title: " "
permalink: /projects/
layout: opera
---

# Current projects

{% assign current = site.data.projects | where: "status", "current" %}
{% include cards_grid.html items=current rows=true %}

# Past projects

{% assign past = site.data.projects | where: "status", "past" %}
{% include cards_grid.html items=past rows=true %}
