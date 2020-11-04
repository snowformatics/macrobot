# About macrobot

Macrobot is an image analysis software for studying plant-pathogen interactions on macroscopic level. Currently the macrobot software can detect and quantify the following plant-pathogen interactions:
- Barley powdery mildew (Blumeria graminis f. sp hordei)
- Wheat powdery mildew (Blumeria graminis f. sp tritici)
- Wheat yellow (stripe) rust (Puccinia striiformis f.sp. tritici)
- Wheat brown (leaf) rust (P. graminis f. sp. tritici)

<img src="https://github.com/snowformatics/macrobot/blob/master/docs/images/Slide1.png" width="50%" height="50%"><br>
Figure 1: Powdery mildew on barley plants

The hardware system is based on a custom fully automated multispectral 2D imaging station (Figure 2).

<img src="https://github.com/snowformatics/macrobot/blob/master/docs/images/Bild8.png" width="50%" height="50%"><br>
Figure 2: Macrobot Module

See the macrobot hardware in action:
https://www.youtube.com/watch?v=SmoKQ_uMp34&t=56s

The entire pipline from image aquisition to image analysis is shown in Figure 3.

<img src="https://github.com/snowformatics/macrobot/blob/master/paper/figure.png" width="70%" height="70%"><br>
Figure 3: Software pipeline

# Citation

Lueck et al., (2020). BluVision Macro - a software for automated powdery mildew and rust disease quantification on detached leaves.. Journal of Open Source Software, 5(51), 2259, https://doi.org/10.21105/joss.02259

# Documentation
https://macrobot.readthedocs.io/en/latest/index.html


# Installation
Macrobot software was build and successfully tested on Windows operation system (Windows 7 and 10).

->Install Anaconda (https://www.anaconda.com/distribution/)

`conda create --name macrobot python=3.8`

`conda activate macrobot`

`conda install pip`

`pip install macrobot`


# Usage

1. Create a folder for the result. We will create a new folder on the desktop called mb_results.
2. Open the Ananconda prompt and activate your macrobot enviroment if you are not already there.<br/>`conda activate macrobot`<br/>
3. Macrobot is a command line program which requires the following arguments:
* source path (-s) - the path with the images coming from the Macrobot hardware system
* destination path (-d) - the path to store the results
* pathogen (-p) - which pathogen to predict ("mildew" or "rust")
4. For a test case we will use a test image set which will be autmatically downloaded by the start of the software. 
To tell the software to use the test images, we will enter "test_images" for the source path -s argument
5. Start the sofwtare with the following comand (adapt the destination path):<br/>`mb -s test_images -d C:\Users\name\Desktop\mb_results\ -p mildew`<br/>
6. In your destination folder should appear all results:
* A csv file with the predicted values per leaf
* A report html file in folder report which allows and easy control over the pipeline.
* Images created by the software (white=pathogen, red=leaf detection, black=background)

If you want to use a real world experiments, make sure to provide the following folder structure with five images per plate (see documentation)

# Tests
cd to installation path and test folder e.g. d:\Anaconda\envs\mb_test\Lib\site-packages\macrobot\tests

Run pytest:

`pytest`


# Contributions:
We are strongly looking for contributions, some ideas how to support our software could be found here:
https://github.com/snowformatics/macrobot/wiki/Contributions

# References:
https://github.com/snowformatics/macrobot/wiki/References
