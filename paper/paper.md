---
title: 'BluVision Macro - a software for automated powdery mildew and rust disease quantification on detached leaves.'
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
 - name: Ulrike Beukert
   orcid: 0000-0002-9482-3512
   affiliation: 2
 - name: Dimitar Douchkov
   orcid: 0000-0001-6603-4930
   affiliation: 1
   
 
affiliations:
 - name: Leibniz-Institut für Pflanzengenetik und Kulturpflanzenforschung Gatersleben, Stadt Seeland, Sachsen-Anhalt
   index: 1
 - name: Julius Kühn-Institut Quedlinburg, Sachsen-Anhalt
   index: 2
   
date: 20 April 2020
bibliography: paper.bib
---
 
# Summary

Powdery mildews and rusts are in the Top 10 of the major fungal pathogens in plant pathology [@2012_2] [@2011_2]. The effect of powdery mildews on crop yields can amount to 40% of harvested grain [@2001]. Besides being an agriculturally important pathogen, the powdery mildews of wheat and barley are important models for studying the plant-pathogen interactions [@2014_2]. Wheat leaf rust and stripe rust are two other fungal pathogens, frequently causing epidemics with up to 70% yield losses [@2005] [@2011_2] in combination with a decreased grain quality [@2012]. 

Crop protection against pathogens is mostly provided by the application of chemical agents [@2013], however, many of them have detrimental effects on non-target species [@2016].  Therefore, the trend is towards reducing the pesticide application and development of alternative and integrated protection methods [@2011_3]. The most sustainable method for crop protection appears to be the use of natural genetic resources and breeding for disease resistance [@2009_3]. Plant breeding is as old as the domestication of the first agricultural plants (>10 000 years) [@2011_4]. The “Green revolution” [@2009] of the 1950-1960 and the more recent “omics” revolution (genomics, proteomics or metabolomics, etc.) [@2007] introduced many new approaches and technologies but the observation methods of the breeders remained mostly unchanged. Recently, new high-throughput observation methods for Phenomics [@2009_2] were introduced, thus providing the fundament for another breeding revolution. However, the powdery mildews and rusts are, as the majority of the plant pathogens, microscopic organisms in the initial and most critical stages of the infection process. Phenotyping of these early stages was significantly held back by the lack of technology for high-throughput phenotyping on a macroscopic and microscopic scale. 

To solve this problem, we have developed the BluVision Macro framework aimed to allow strictly quantitative assessment of disease and host responses on a macroscopic level. The system consists of a hardware part – the Macrobot [@2020] - a multimodal imaging station and robotized sample magazine/loader, and the BluVision Macro software, described in this article. The system is designed to work with samples placed in standard containers, so-called microtiter plates (MTP), which are well-established standard in biology and medicine. The loading of the MTPs to the imaging station and the image acquisition is fully automated. The system uses a 14-bit monochrome camera (Thorlabs 8050M-GE-TE) at a resolution of 3296×2472 px. The illumination is based on narrow bandwidth isotropic LED light sources (Metaphase Exolight-ISO-14-XXX-U) with 365nm (UV), 470nm (blue), 530nm (green) and 625nm (red) peak wavelength. For each plate monochrome images in all illumination, wavelengths are acquired separately and stored in 16-bit TIFF image files. Additionally, a background illumination image is taken and used for the separation of the foreground and background.

![Macrobot image acquisition and analysis workflow.\label{fig:example}](figure.png)




The image analysis pipeline currently contains software modules for powdery mildew of barley and wheat (*Blumeria graminis* f. sp. *hordei* resp. *tritici*), wheat stripe rust (*Puccinia striiformis* f.sp. *tritici*), wheat leaf rust (*P. triticina*), and will work without major modification also for barley leaf and stripe rusts and probably some other leaf disease with a similar appearance. Phenotyping of other disease and non-disease related phenotypes is possible but it will require developments of dedicated modules. The system is running in production mode and generates phenotyping data for powdery mildew and rust disease resistance screens at the Leibniz Institute of Plant Genetics and Crop Plant Research (IPK) in Gatersleben, Germany, and the Julius Kühn-Institute (JKI) in Quedlinburg, Germany.


 
# Installation
The macrobot software can simply be installed with Ananconda and pip and was build and tested on Wondows operation system. <br>
It requires Python 3.7 or higher, numpy [@doi:10.1109/MCSE.2011.37], scikit-image [@scikit-image], opencv-python [@opencv_library], pytest and jinja2. 

# Acknowledgment
This work was supported by grants from the German Federal Ministry of Research and Education (BMBF) – DPPN (FKZ 031A05) and Gene Bank 2.0  (FKZ 031B0184)

# References
