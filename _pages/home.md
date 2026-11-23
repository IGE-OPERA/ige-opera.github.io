---
layout: opera-home
permalink: /
hidden: true
excerpt: "Open computational earth and climate science research"
---

{% include opera/hero.html %}

<section class="opera-section opera-section--themes">

  <h2 class="opera-section__title">Research themes</h2>
  <p class="opera-section__lead">
    Three components of the Earth system, studied <strong>in the context of climate change</strong> —
    from process understanding to models, data and predictions.
  </p>

  {% include cards_grid.html items=site.data.themes %}

  <p class="opera-section__more">
    <a href="{{ '/research/' | relative_url }}">Read more about our research &rarr;</a>
  </p>

</section>

<section class="opera-section opera-section--methods">

  <h2 class="opera-section__title">Advancing computational methods</h2>
  <p class="opera-section__lead">
    We develop, calibrate and evaluate process-based community models; we explore data-driven and
    hybrid approaches; and we rethink the design of the numerical systems that carry our science.
  </p>

  {% include cards_grid.html items=site.data.methods %}

  <p class="opera-section__more">
    <a href="{{ '/research/#advancing-computational-methods' | relative_url }}">How we work &rarr;</a>
  </p>

</section>

<section class="opera-band opera-band--emerging">

  <h2 class="opera-band__title">Emerging activities</h2>
  <p class="opera-band__text">
    Beyond climate, OPERA is opening new domains: physics-informed machine learning for
    <strong>glaciology</strong> and <strong>paleomagnetism</strong>, with
    <a href="{{ '/people/' | relative_url }}">Facundo Sapienza</a> and the SIDERAL project.
  </p>
  <p class="opera-band__actions"><a href="{{ '/research/#emerging-activities' | relative_url }}" class="btn btn--outline">Read more</a></p>

</section>

<section class="opera-section opera-section--news">

  <h2 class="opera-section__title">Latest news</h2>

  {% assign news = site.data.news | sort: "date" | reverse %}
  <ul class="opera-news">

    {% for n in news limit: 3 %}
      <li class="opera-news__item">
        <span class="opera-news__date">{{ n.date | date: "%b %Y" }}</span>
        <span class="opera-news__content">
          <strong>{{ n.title }}</strong>
          {% if n.text %}<br>{{ n.text }}{% endif %}
          {% if n.url %}<br><a href="{{ n.url }}">{{ n.url_label | default: "Read more" }}</a>{% endif %}
        </span>
      </li>
    {% endfor %}

  </ul>

  <p class="opera-section__more">
    <a href="{{ '/join/' | relative_url }}">Working with us &rarr;</a>
  </p>

</section>

<section class="opera-band opera-band--cta">

  <h2 class="opera-band__title">Open science, open tools, open group.</h2>
  <p class="opera-band__actions">
    <a href="{{ '/publications/' | relative_url }}" class="btn btn--primary btn--large">Our publications</a>
    <a href="{{ '/software/' | relative_url }}" class="btn btn--outline btn--large">Our software</a>
  </p>

</section>
