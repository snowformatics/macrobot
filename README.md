# About macrobot

Deep investigation of the intimate details of the plant-pathogen interactions is essential to truly understand the defense mechanism of the plants and the evading strategies of the pathogens. By using this knowledge in plant breeding we may significantly diminish the enormous disease-related losses in agriculture by simultaneous reduction of application of potentially hazardous pesticides. We have developed the BluVision image analysis Framework for studying plant-pathogen interactions on micro- and macroscopic level. The system is build to cover the complete life cycle (Figure 2) of the important barley and wheat pathogen powdery mildew (Blumeria graminis, Figure 1) by collecting and analyzing image data from three key developmental stages but can be applied also to other plant-pathogen interactions.

<img src="https://github.com/snowformatics/GSOC/blob/master/Slide1.png" width="70%" height="70%"><br>
Figure 1: Blumeria graminis on barley plants

<img src="https://github.com/snowformatics/GSOC/blob/master/Bild3.png" width="70%" height="70%"><br>
Figure 2: Blumeria graminis life cycle


# What software we create?
macrobot is a software and hardware framework for high-throughput image acquisition and analysis of macroscopic images in plant pathology (Figure 3). The system is based on a custom fully automated multispectral 2D imaging station (Figure 5).

<img src="https://github.com/snowformatics/GSOC/blob/master/Slide4.PNG" width="110%" height="110%"><br>
Figure 3: BluVision Framework

<img src="https://github.com/snowformatics/GSOC/blob/master/Bild8.png" width="70%" height="70%"><br>
Figure 5: BluVision Macro Module


Our image analysis pipeline is aimed to detect macroscopic disease symptoms (Figure 7). 

<img src="https://github.com/snowformatics/GSOC/blob/master/Bild10.png" width="70%" height="70%"><br>
Figure 7: Blumeria graminis prediction on barley leafs


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
