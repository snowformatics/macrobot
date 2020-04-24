============
Introduction
============


BluVision
=========
BluVision is a software and hardware framework for high-throughput image acquisition and analysis of microscopic and macroscopic images in plant pathology.

Deep investigation of the intimate details of the plant-pathogen interactions is essential to truly understand the defense mechanism of the plants and the evading strategies of the pathogens. By using this knowledge in plant breeding we may significantly diminish the enormous disease-related losses in agriculture by simultaneous reduction of application of potentially hazardous pesticides. We have developed the BluVision image analysis Framework for studying plant-pathogen interactions on micro- and macroscopic level. The system is build to cover the complete life cycle (Figure 1) of the important barley and wheat pathogen powdery mildew  by collecting and analyzing image data from three key developmental stages but can be applied also to other plant-pathogen interactions.
BluVision is written in Python 3.

.. image:: images/cycle.png


Macrobot Module
===============

The macroscopic module is based on a custom fully automated multispectral 2D imaging station called Macrobot (Figure 2).

.. image:: images/macrobot.png

Young seedling plants are cut into small peaces and arranged on a microplate (white frames would fix the leaves). The seedlings are infected with a pathogen and after an incubation time (6-15 days) the pathogen develops visible symptoms (Figure 3).

.. image:: images/plate.png

After image acquisition with the Macrobot hardware, the macrobot analysis pipeline could be started.



