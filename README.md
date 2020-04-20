# macrobot_paper
# Installation

## Via Ananaconda (recommended):
1.) Install Anaconda (https://www.anaconda.com/distribution/)

2.) Open Anaconda prompt and create a new enviroment: 

**conda create --name macrobot python=3**

3.) Activate enviroment:

**conda activate macrobot**

4.) Install macrobot software:

**pip install macrobot-paper**

5.) Test macrobot software:

**mb -s C:\ -d C:\ -p bgt**
 


## After you run the last command, the cmd should print out:

It's alive!

Namespace(destination_path='C:\\', procedure='bgt', source_path='C:\\')



## Manual installation:
pip install numpy

pip install -c conda-forge scikit-image

pip install -c conda-forge opencv

pip install macrobot-paper
