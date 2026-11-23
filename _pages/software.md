---
title: " "
permalink: /software/
layout: opera

community_models:
  - image_path: "/assets/images/software/NEMO.png"
    title: "NEMO"
    excerpt: "OPERA contributes to improving the representation of uncertainties and introducing ML components within NEMO, the european ocean / sea-ice modelling framework."
    url: "https://www.nemo-ocean.eu"
    btn_class: "btn--primary"
    btn_label: "Learn more"
  - image_path: "assets/images/software/WRF-Chem-Polar.png"
    title: "WRF-Chem-Polar"
    excerpt: "OPERA co-leads developement of a regional chemistry-climate model based on WRF-Chem, with enhancements for the polar regions, developed at IGE and LATMOS in France."
    url: "https://wrf-chem-polar.eu"
    btn_class: "btn--primary"
    btn_label: "Learn more"
  - image_path: "assets/images/software/LMDZ.png"
    title: "LMDZ"
    excerpt: "OPERA contributes to the development of empirical run-time bias-corrections in LMDZ, including ML-based implementations, and focuses on regional-scale applications."
    url: "https://lmdz.lmd.jussieu.fr/"
    btn_class: "btn--primary"
    btn_label: "Learn more"
  - image_path: "assets/images/software/GEOS-Chem.png"
    title: "GEOS-Chem"
    excerpt: "OPERA contributes to improving the representation of atmospheric microplastics in the GEOS-Chem global atmospheric chemistry model"
    url: "https://geoschem.github.io/index.html"
    btn_class: "btn--primary"
    btn_label: "Learn more"

opera_software:
  - image_path: "/assets/images/home/methods-hybrid.svg"
    title: "legoESM"
    excerpt: "A differentiable Earth System Model in JAX — atmosphere, ocean, land, sea ice, lakes, coupler, end-to-end gradients."
    url: "https://github.com/climate-federation/legoESM"
    btn_label: "Code"
  - title: "ODINN.jl"
    excerpt: "Open-source glacier evolution modelling with neural differential equations — physics-informed machine learning in Julia."
    url: "https://github.com/ODINN-SciML/ODINN.jl"
    btn_label: "Code"
---

# Software

## Community models

Part of our research contributes to the community models that carry climate and
environmental science:

{% include cards_grid.html items=page.community_models %}

## OPERA software

We also develop our own open-source tools — most of them born from our research on
differentiable and hybrid Earth system modelling:

{% include cards_grid.html items=page.opera_software %}

## More on our GitHub

All our in-house development happens in the open on the
[IGE-OPERA GitHub organisation](https://github.com/IGE-OPERA?view_as=public). A few
repositories you may find useful:

- **[tunax](https://github.com/IGE-OPERA/tunax)** — automatic calibration of vertical ocean physics in JAX
- **[jaxparrow](https://github.com/IGE-OPERA/jaxparrow)** — cyclogeostrophic currents computed with a minimisation-based approach, in JAX
- **[eophis](https://github.com/IGE-OPERA/eophis)** — call Python scripts from Fortran ESMs through the OASIS3-MCT coupler
- **[widetrax](https://github.com/IGE-OPERA/widetrax)** — cloud-ready toolbox for wide-swath altimetry ocean data
- **[swot-omip](https://github.com/IGE-OPERA/swot-omip)** — leveraging SWOT ocean data to assess ocean circulation models
- **[ocean-sea-ice-emulators-living-review](https://github.com/IGE-OPERA/ocean-sea-ice-emulators-living-review)** — a living review of deep emulators for ocean and sea-ice modelling and forecasting
- **[gyres-experiment-template](https://github.com/IGE-OPERA/gyres-experiment-template)** — template for reproducible personal ocean-experiment ledgers
- **[code-reprohack](https://github.com/IGE-OPERA/code-reprohack)** — reviewing scientific software repositories, with a focus on reproducibility
