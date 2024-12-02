# About macrobot software

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
Macrobot software was build and successfully tested on Windows operating system (Windows 7 and 10).


### Option 1: Anaconda

Download and install Anaconda: (https://www.anaconda.com/distribution/)


### Option 2: Miniforge
> [!IMPORTANT]
Note: Due to Anaconda's licensing limitations (maximum of 200 users per organization), we recommend considering an alternative, Miniforge, especially for larger teams or open-source projects.

Miniforge is a lightweight, community-driven alternative to Anaconda. It provides similar functionality and is free from licensing restrictions.

Download Miniforge 3 for Windows operating system:
https://github.com/conda-forge/miniforge/releases/download/24.9.2-0/Miniforge3-Windows-x86_64.exe

Choose the installer appropriate for your operating system and follow the installation instructions provided on the download page.

### Install macrobot software
`conda create --name macrobot_env python=3.7`

`conda activate macrobot_env`

`conda install pip`

`pip install macrobot`


### Usage

1. Create a folder for the result. We will create a new folder on the desktop called mb_results.
2. Open the Ananconda prompt and activate your macrobot environment if you are not already there.<br/>`conda activate macrobot`<br/>
3. Macrobot is a command line program which requires the following arguments:
* source path (-s) - the path with the images coming from the Macrobot hardware system
* destination path (-d) - the path to store the results
* pathogen (-p) - which pathogen to predict ("mildew", "bipolaris" or "rust")
4. For a test case we will use a test image set which will be automatically downloaded by the start of the software.
To tell the software to use the test images, we will enter "test_images" for the source path -s argument
5. Start the software with the following command for mildew (adapt the destination path):

Mildew: <br/>`mb -s test_images -d C:\Users\name\Desktop\mb_results\ -p mildew`<br/> 
Rust:
<br/>`mb -s test_images -d C:\Users\name\Desktop\mb_results\ -p rust`<br/>
Bipolaris:
<br/>`mb -s test_images -d C:\Users\name\Desktop\mb_results\ -p bipolaris`<br/>
6. In your destination folder should appear all results:
* A csv file with the predicted values per leaf
* A report html file in folder report which allows and easy control over the pipeline.
* Images created by the software (white=pathogen, red=leaf detection, black=background)

If you want to use a real world experiments, make sure to provide the following folder structure with five images per plate (see documentation)

### Tests
cd to installation path and test folder e.g. d:\Anaconda\envs\mb_test\Lib\site-packages\macrobot\tests

Run pytest:

`pytest`


### Contributions:
We are strongly looking for contributions, some ideas how to support our software could be found here:
https://github.com/snowformatics/macrobot/wiki/Contributions

### References:
https://github.com/snowformatics/macrobot/wiki/References
