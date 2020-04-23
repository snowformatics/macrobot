import os


def test_bgt_pipeline():
    os.chdir("..")
    result = os.system('python cli.py -s //psg-09/Mikroskop/plates/Macrobot_Analysis/ -d //psg-09/Mikroskop/Images/BluVisionMacro/test/ -p mildew' )
    os.chdir(os.getcwd() + "/tests/")

#

