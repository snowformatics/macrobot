# About macrobot

Macrobot is an image analysis software for studying plant-pathogen interactions on macroscopic level. Currebntly the macrobot sofwtare could detetc and quantify the following plant-pathogen interactions:
- Barley powdery mildew (Blumeria graminis f. sp hordei) on barely leaves 
- Wheat powdery mildew (Blumeria graminis f. sp tritici) on wheat leaves
- Wheat yellow rust (Puccinia graminis f.sp. tritici) on wheat leaves
- Wheat brown rust  (Puccinia dispersa f. sp. tritici) on wheat leaves

<img src="https://github.com/snowformatics/GSOC/blob/master/Slide1.png" width="70%" height="70%"><br>
Figure 1: Powdery mildew on barley plants

The hardware system is based on a custom fully automated multispectral 2D imaging station (Figure 2).

<img src="https://github.com/snowformatics/GSOC/blob/master/Bild8.png" width="70%" height="70%"><br>
Figure 2: Macrobot Module

See the macrobot hardware in action:
https://www.youtube.com/watch?v=SmoKQ_uMp34&t=56s

Our image analysis pipeline is aimed to detect macroscopic disease symptoms for barley and wheat powdery mildew (Figure 3) as well as yellow and brown rust. 

<img src="https://github.com/snowformatics/GSOC/blob/master/Bild10.png" width="70%" height="70%"><br>
Figure 3: Blumeria graminis prediction on barley leafs


# Installation

## Via Ananaconda (recommended):
1.) Install Anaconda (https://www.anaconda.com/distribution/)

2.) Open Anaconda prompt and create a new enviroment: 

**conda create --name macrobot python=3**

3.) Activate enviroment:

**conda activate macrobot**

4.) Install macrobot software:

**pip install macrobot**

5.) Test macrobot software:

**mb -s C:\ -d C:\ -p bgt**

## After you run the last command, the cmd should print out:

Namespace(destination_path='C:\\', procedure='bgt', source_path='C:\\')

## Installing by pip:
pip install macrobot

# Contributions:
https://github.com/snowformatics/macrobot/wiki/Contributions

# References:
https://github.com/snowformatics/macrobot/wiki/References
