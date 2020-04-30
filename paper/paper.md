---
title: 'Macrobot - A software for automated powdery mildew and rust disease quantification.'
tags:
  - plant phenotyping
  - powdery mildew
  - barley
  - wheat
  - rust
  - pucchinia
  - python
  - pathogen
authors:
 - name: Stefanie Lueck
   orcid: 0000-0003-0536-835X
   affiliation: 1
 - name: Dimitar Douchkov
   orcid: 0000-0001-6603-4930
   affiliation: 1
affiliations:
 - name: Leibniz-Institut für Pflanzengenetik und Kulturpflanzenforschung Gatersleben, Stadt Seeland, Sachsen-Anhalt
   index: 1
date: 20 April 2020
bibliography: paper.bib
---
 
# Summary
Crop protection is mostly provided by the application of chemical agents, which can be harmful to the environment while a more sustainable disease control is resistance breeding. The plant breeding is as old as the domestication of the first agricultural plants (>10 000 years). The “Green revolution” of the 1950-1960 or the more recent genomics revolution introduced many new approaches and technologies but the observation methods of the breeders remained mostly unchanged. Typically, a breeder will look on the appearance (phenotype) of the plant and will select for plants that carry favorable traits, such as higher grain yield or stronger resistance to diseases. Introducing of the so-called molecular markers was the first significant improvement to boost dramatically breeding research.

Recently, new observation methods for so-called phenotyping were introduced, thus providing the fundament for another breeding revolution. However, phenotyping of the early, and most critical stages of the interactions between plants and pathogens, was significantly embarrassed by a lack of technology for high-throughput automated ... . To meet this challenge, we have developed the Macrobot software  aimed to allow strictly quantitative assessment of disease and host responses on macroscopic level.

The hardware module is based on a custom fully automated multispectral 2D imaging station [@Lueck2020.03.16.993451].
  
# Conclusions
 Deep investigation of the intimate details of the plant-pathogen interactions is essential to truly understand the defense mechanism of the plants and the evading strategies of the pathogens. By using this knowledge in plant breeding we may significantly diminish the enormous disease-related losses in agriculture by simultaneous reduction of application of potentially hazardous pesticides. We have developed an image analysis Framework for studying plant-pathogen interactions on macroscopic level.
 
# Installation
Macrobot software can simply be installed with Ananconda and pip (pip install macrobot). <br>
It requires Python 3.7 or higher, numpy [@doi:10.1109/MCSE.2011.37], scikit-image [@scikit-image], opencv-python [@opencv_library], pytest and jinja2. 

  
# References
