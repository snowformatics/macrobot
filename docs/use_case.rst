================
Use case example
================


1. Create a folder for the result. We will create a new folder on the desktop called mb_results.
2. Open the Ananconda prompt and activate your macrobot enviroment if you are not already there.

``conda activate macrobot``

3. Macrobot is a command line program which requires the following arguments:

* source path (-s) - the path with the images coming from the Macrobot hardware system
* destination path (-d) - the path to store the results
* pathogen (-p) - which pathogen to predict ("mildew" or "rust")

4. For a test case we will use a test image set which will be autmatically downloaded by the start of the software. To tell the software to use the test images, we will enter "test_images" for the source path -s argument

5. Start the sofwtare with the following comand (adapt the destination path):

``mb -s test_images -d C:\Users\name\Desktop\mb_results\ -p mildew``

6. In your destination folder should appear all results:

* A csv file with the predicted values per leaf
* A report html file in folder report which allows and easy control over the pipeline.
* Images created by the software (white=pathogen, red=leaf detection, black=background)

If you want to use a real world experiments, make sure to provide the following folder structure with five images per plate:

my_folder

---experiment1

-----dai

-------plateID

---------plateID_backlight.tif

---------plateID_blue.tif

---------plateID_green.tif

---------plateID_red.tif

---------plateID_uvs.tif

-------plateID2

---------plateID2_backlight.tif

---------plateID2_blue.tif

---------plateID2_green.tif

---------plateID2_red.tif <

---------plateID2_uvs.tif

---experiment2

-----dai

-------plateID

---------plateID_backlight.tif

---------plateID_blue.tif

---------plateID_green.tif

---------plateID_red.tif

---------plateID_uvs.tif
