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


from macrobot.puccinia import RustSegmenter
from macrobot.bgt import BgtSegmenter


def main():

    parser = argparse.ArgumentParser(description = 'Macrobot analysis software.')
    parser.add_argument('-s', '--source_path', required = True,
                        help = 'Directory containing images to segment.')
    parser.add_argument('-d', '--destination_path', required=True,
                        help='Directory to store the result images.')
    parser.add_argument('-p', '--procedure', required = True,
                        help = 'Pathogen, choose bgt or rust.')

    args = parser.parse_args()

    source_path = args.source_path
    destination_path = args.destination_path
    procedure = args.procedure
    # #images = os.listdir(img_dir)
    segmenter_class = {
        'rust': RustSegmenter,
        'mildew': BgtSegmenter,
    }.get(procedure)
    if not segmenter_class:
        raise argparse.ArgumentError("Invalid segmentation method '{}'".format(procedure))

    print(args, segmenter_class)

    experiments = os.listdir(source_path)
    #
    for experiment in experiments:

        try:
            dais = os.listdir(source_path + experiment + '/')
            for dai in dais:
                try:
                    os.makedirs(destination_path + experiment + '/' + dai + '/')

                except FileExistsError:
                    pass
                print ('\n=== Start Macrobot pipeline === \n Experiment: ' + experiment)
                file_results = open(destination_path + experiment + '/' + dai + '/' + str(experiment) + '_leaf.csv', 'a')
                file_results.write('index' + ';' + 'expNr' + ';' + 'barcode' + ';' + 'Plate_ID' + ';' + 'Lane_ID' + ';' + 'Leaf_ID' + ';' + '%_Inf' + '\n')

                plates = os.listdir(source_path + experiment + '/' + dai + '/')

                for plate in plates:
                    img_dir = source_path + experiment + '/' + dai + '/' + plate + '/'
                    images = [f for f in os.listdir(img_dir) if f.endswith('.tif')]
                    processor = segmenter_class(images, img_dir, destination_path, experiment, dai, file_results)
                    plate_id = processor.start_pipeline()





        except NotADirectoryError:
            print ('Skip ' + source_path + experiment + ' because it is not a directory.')

        print('\n=== End Macrobot pipeline ===')


if __name__ == "__main__":
    main()