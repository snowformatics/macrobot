================================
Macrobot image analysis pipeline
================================

Overview
========
Image analysis pipeline consists of 4 major steps:

1.) Creating a true 3-channel RGB image from the blue, green and red channel image

.. image:: images/plate_ex.png

2.) Frame segmentation

.. image:: images/frame.png

3.) Leaf segmentation

.. image:: images/leaf.png

4.) Pathogen prediction (white is pathogen, black background)

.. image:: images/predict.png


Analysis time
=============

Analysis time is approximately 5 seconds per plate (Intel(R) Core(TM) i7-9700 CPU @ 3.00GHz; 32 GB RAM; Windows 10 x64).





