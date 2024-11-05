# python cli.py -s //psg-09/Mikroskop/plates/ -d //psg-09/Mikroskop/Images/BluVisionMacro/test/ -p bgt

# The raw images from the Macrobot
# source_path = 'C:/Users/lueck/PycharmProjects/BluVision/tests/images/bgt/'
# source_path = 'C:/Users/lueck/PycharmProjects/BluVision/tests/images/brown_rust/'
# source_path = "//psg-09/Mikroskop/plates/JKI/Rust/Yellow/"
# source_path = "//psg-09/Mikroskop/plates/JKI/Rust/Brown/"
# source_path = "//psg-09/Mikroskop/plates/"

# source_path = "//psg-09/Mikroskop/Test/plates/JKI/17042018/"
# The path to store the results
# destination_path = 'C:/Users/lueck/PycharmProjects/BluVision/tests/results/'
# destination_path = "//psg-09/Mikroskop/Images/BluVisionMacro/JKI/Yellow/Macrobotv0.3/"
# destination_path = "//psg-09/Mikroskop/Images/BluVisionMacro/test/"

import os
import argparse
import re

from macrobot.puccinia import RustSegmenter
from macrobot.puccinia_ipk import RustSegmenterIPK
from macrobot.bgt import BgtSegmenter
from macrobot.bipolaris import BipolarisSegmenter
from macrobot.net_blotch_latrobe import NetBlotchSegmenter
from macrobot import orga


def main():

    parser = argparse.ArgumentParser(description='Macrobot analysis software.')
    parser.add_argument('-s', '--source_path', required=True,
                        help='Directory containing images to segment.')
    parser.add_argument('-d', '--destination_path', required=True,
                        help='Directory to store the result images.')
    parser.add_argument('-p', '--procedure', required=True,
                        help='Pathogen, choose mildew or rust.')


    #store_leaf_path = None

    # We first check weather the test images set was already downloaded, if not we store it locally
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(CURRENT_PATH, 'data')
    print (data_path)
    orga.download_test_images(data_path)

    # We get all the arguments from the user input
    args = parser.parse_args()

    # Source image path
    source_path = args.source_path
    if source_path == 'test_images':
        source_path = data_path

    if args.procedure == 'mildew':
        store_leaf_path = "//psg-09/Mikroskop/Training_data/PhenoDB/macrobot_rois/" + source_path.split('\\')[-3] + '/'\
                          + source_path.split('\\')[-2] + '/'
    else:
        store_leaf_path = "//psg-09/Mikroskop/Training_data/PhenoDB/macrobot_rois/" + source_path.split('\\')[-2] + '/'
    print (store_leaf_path)
    # Path to store the results
    destination_path = args.destination_path

    # Pathogen
    procedure = args.procedure
    segmenter_class = {
        'rust': RustSegmenter,
        'rust_ipk': RustSegmenterIPK,
        'mildew': BgtSegmenter,
        'bipolaris': BipolarisSegmenter,
        'netblotch': NetBlotchSegmenter
    }.get(procedure)
    if not segmenter_class:
        raise argparse.ArgumentError("Invalid segmentation method '{}'".format(procedure))

    print(args, segmenter_class)

    # We start the analysis in batch mode
    experiments = os.listdir(source_path)
    print (experiments)
    for experiment in experiments:
        try:
            dais = os.listdir(os.path.join(source_path, experiment))
            #print (dais)
            for dai in dais:
                try:
                    os.makedirs(os.path.join(destination_path, experiment, dai))
                except FileExistsError:
                    pass
                print ('\n=== Start Macrobot pipeline === \n Experiment: ' + experiment)
                file_results = open(os.path.join(destination_path, experiment, dai, str(experiment) + '_leaf.csv'), 'w')
                file_results.write('index' + ';' + 'expNr' + ';' + 'dai' +';' + 'Plate_ID' + ';' + 'Lane_ID' + ';' + 'Leaf_ID' + ';' + '%_Inf' + '\n')
                plates = os.listdir(os.path.join(source_path, experiment, dai))
                for plate in plates:
                    if not re.search('color', plate, re.IGNORECASE):
                        if not re.search('colour', plate, re.IGNORECASE):
                            img_dir = os.path.join(source_path, experiment, dai, plate)
                            images = [f for f in os.listdir(img_dir) if f.endswith('.tif')]
                            processor = segmenter_class(images, img_dir, destination_path, store_leaf_path, experiment, dai, file_results)
                            processor.start_pipeline()
        except NotADirectoryError:
            print ('Skip ' + source_path + experiment + ' because it is not a valid directory.')

        print('\n=== End Macrobot pipeline ===')


if __name__ == "__main__":
    main()