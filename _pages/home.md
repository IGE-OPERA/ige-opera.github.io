---
layout: splash
permalink: /
hidden: true
header:
   overlay_color: "#578BBD"
excerpt: 
    "Open computational earth and climate science research"


intro:
#  - image_path: "/assets/images/open-logo.png" 
  - image_path: "/assets/images/logo-no-text.png"
#  - excerpt: "Our research group uses open science methodologies to foster to advance understanding of key environmental and climate processes across the atmosphere, land surface, cryosphere, and ocean."
  - excerpt: "Our research group uses **open science** methodologies to foster **interdisciplinary science** to advance understanding of key environmental and **climate** processes."

geoscience:
  - image_path: "/assets/images/home/atmosphere.png"
    title: "Atmosphere"
    excerpt: "Atmospheric aerosols, clouds, atmosphere-surface interactions"
  - image_path: "/assets/images/home/osbl-processes.png"
    title: "Ocean"
    excerpt: "Near surface ocean processes, air-sea exchanges, remote sensing"
  - image_path: "/assets/images/home/climate.png"
    title: "Climate"
    excerpt: "Climate modeling and prediction"

methods:
  - image_path: "/assets/images/home/calibrate.png"
    title: "Physics-based modeling"
    excerpt: "Development, calibration, evaluation, uncertainty quantification"
  - image_path: "/assets/images/home/ai.png"
#    title: "AI for modeling and inversion"
    title: "ML-based approaches "
    excerpt: "Hybrid modelling, differentiable programming, neural data assimilation"
  - image_path: "/assets/images/home/modularity.png"
    title: "Numerical system design"
    excerpt: "Modularity, interoperability of models and monitoring systems"

---

{% include feature_row id="intro" type="center" %}

<h1 style="text-align:center;color:#578BBD">Research themes</h1>


{% include feature_row id="geoscience"  %}


<h1 style="text-align:center;color:#578BBD;">Computational tools </h1>

 
{% include feature_row id="methods" %}


