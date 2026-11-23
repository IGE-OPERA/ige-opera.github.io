---
title: " "
permalink: /software/
layout: opera

community_models:
  - image_path: "/assets/images/software/NEMO.png"
    title: "NEMO"
    excerpt: "OPERA contributes to improving the representation of uncertainties and introducing ML components within NEMO, the european ocean / sea-ice modelling framework."
    url: "https://www.nemo-ocean.eu"
    btn_label: "Learn more"
  - image_path: "assets/images/software/WRF-Chem-Polar.png"
    title: "WRF-Chem-Polar"
    excerpt: "OPERA co-leads developement of a regional chemistry-climate model based on WRF-Chem, with enhancements for the polar regions, developed at IGE and LATMOS in France."
    url: "https://wrf-chem-polar.eu"
    btn_label: "Learn more"
  - image_path: "assets/images/software/LMDZ.png"
    title: "LMDZ"
    excerpt: "OPERA contributes to the development of empirical run-time bias-corrections in LMDZ, including ML-based implementations, and focuses on regional-scale applications."
    url: "https://lmdz.lmd.jussieu.fr/"
    btn_label: "Learn more"
  - image_path: "assets/images/software/GEOS-Chem.png"
    title: "GEOS-Chem"
    excerpt: "OPERA contributes to improving the representation of atmospheric microplastics in the GEOS-Chem global atmospheric chemistry model"
    url: "https://geoschem.github.io/index.html"
    btn_label: "Learn more"
  - image_path: "/assets/images/software/legoESM.jpg"
    title: "legoESM"
    excerpt: "OPERA contributes to legoESM, a fully differentiable Earth System Model in JAX — atmosphere, ocean, land, sea ice and lakes, coupled through one interface, with end-to-end gradients."
    url: "https://github.com/climate-federation/legoESM"
    btn_label: "Learn more"
  - image_path: "/assets/images/software/odinn.jpg"
    title: "ODINN.jl"
    excerpt: "OPERA contributes to ODINN.jl, open-source glacier evolution modelling with neural differential equations — physics-informed machine learning in Julia."
    url: "https://github.com/ODINN-SciML/ODINN.jl"
    btn_label: "Learn more"

opera_software:
  - title: "JaxParrow"
    excerpt: "Cyclogeostrophic surface currents computed with a minimisation-based approach, in JAX."
    url: "https://github.com/IGE-OPERA/jaxparrow"
    btn_label: "Learn more"
  - title: "eophis"
    excerpt: "Couple Python scripts and tools into Fortran Earth system models through the OASIS3-MCT coupler."
    url: "https://github.com/IGE-OPERA/eophis"
    btn_label: "Learn more"
  - title: "widetrax"
    excerpt: "Cloud-ready toolbox for manipulating wide-swath altimetry ocean data."
    url: "https://github.com/IGE-OPERA/widetrax"
    btn_label: "Learn more"
  - title: "tunax"
    excerpt: "Automatic calibration of vertical ocean physics, in JAX."
    url: "https://github.com/IGE-OPERA/tunax"
    btn_label: "Learn more"
  - title: "Aronnax"
    excerpt: "Python wrapper for the ocean general circulation model NEMO v5.0.1 — drive the Fortran time loop and exchange model variables from Python."
    url: "https://github.com/IGE-OPERA/Aronnax"
    btn_label: "Learn more"
---

# Software

## Community models

Part of our research contributes to the community models that carry climate and
environmental science:

{% include cards_grid.html items=page.community_models rows=true %}

## OPERA software

Our own open-source tools, developed in the open in the
[IGE-OPERA GitHub organisation](https://github.com/IGE-OPERA?view_as=public):

{% include cards_grid.html items=page.opera_software rows=true %}

## More on our GitHub

- **[swot-omip](https://github.com/IGE-OPERA/swot-omip)** — leveraging SWOT ocean data to assess ocean circulation models
- **[ocean-sea-ice-emulators-living-review](https://github.com/IGE-OPERA/ocean-sea-ice-emulators-living-review)** — a living review of deep emulators for ocean and sea-ice modelling and forecasting
