# About macrobot

Macrobot is an image analysis software for studying plant-pathogen interactions on macroscopic level. Currently the macrobot software can detect and quantify the following plant-pathogen interactions:
- Barley powdery mildew (Blumeria graminis f. sp hordei) on barely leaves 
- Wheat powdery mildew (Blumeria graminis f. sp tritici) on wheat leaves
- Wheat yellow rust (Puccinia graminis f.sp. tritici) on wheat leaves
- Wheat brown rust  (Puccinia dispersa f. sp. tritici) on wheat leaves

<img src="https://github.com/snowformatics/GSOC/blob/master/Slide1.png" width="50%" height="50%"><br>
Figure 1: Powdery mildew on barley plants

The hardware system is based on a custom fully automated multispectral 2D imaging station (Figure 2).

<img src="https://github.com/snowformatics/GSOC/blob/master/Bild8.png" width="50%" height="50%"><br>
Figure 2: Macrobot Module

See the macrobot hardware in action:
https://www.youtube.com/watch?v=SmoKQ_uMp34&t=56s

Our image analysis pipeline is aimed to detect macroscopic disease symptoms for barley and wheat powdery mildew (Figure 3) as well as yellow and brown rust. 

<img src="https://github.com/snowformatics/macrobot/blob/master/paper/figure.png" width="70%" height="70%"><br>
Figure 3: Software pipeline

# Documentation
A detailed documentation could be found here.


# Installation
->Install Anaconda (https://www.anaconda.com/distribution/)

`conda create --name macrobot python=3`

`conda activate macrobot`

`conda install pip`

`pip install macrobot`

Detailed installation instructions can be found here.

# Usage

1. Create a folder for the result. We will create a new folder on the desktop called mb_results.
2. Open the Ananconda prompt and activate your macrobot enviroment if you are not already there.`conda activate macrobot`
3. Macrobot is a command line program which requires the following arguments:
* source path (-s) - the path with the images coming from the Macrobot hardware system
* destination path (-d) - the path to store the results
* pathogen (-p) - which pathogen to predict ("mildew" or "rust")
4. For a test case we will use a test image set which will be autmatically downloaded by the start of the software. 
To tell the software to use the test images, we will enter "test_images" for the source path -s argument
5. Start the sofwtare with the following comand:`mb -s test_images -d C:\Users\lueck\Desktop\mb_results\ -p mildew`
6. In your destination folder should appear all results:
* A csv file with the predicted values per leaf
* A report html file in folder report which allows and easy control over the pipeline.
* Images created by the software (white=pathogen, red=leaf detection, black=background)

# Contributions:
We are strongly looking for contributions, some ideas how to support our software could be found here:
https://github.com/snowformatics/macrobot/wiki/Contributions

# References:
https://github.com/snowformatics/macrobot/wiki/References
