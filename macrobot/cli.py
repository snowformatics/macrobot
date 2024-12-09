import os
import argparse
import re
from pathlib import Path
from macrobot.puccinia import RustSegmenter
from macrobot.puccinia_ipk import RustSegmenterIPK
from macrobot.bgt import BgtSegmenter
from macrobot.bipolaris import BipolarisSegmenter
from macrobot.net_blotch_latrobe import NetBlotchSegmenter
from macrobot import orga


def main():
    # Create argument parser to handle command-line inputs
    parser = argparse.ArgumentParser(description='Macrobot analysis software.')
    parser.add_argument('-s', '--source_path', required=True,
                        help='Directory containing images to segment.')
    parser.add_argument('-d', '--destination_path', required=True,
                        help='Directory to store the result images.')
    parser.add_argument('-p', '--procedure', required=True,
                        choices=['rust', 'rust_ipk', 'mildew', 'bipolaris', 'netblotch'],
                        help='Pathogen to analyze: rust, rust_ipk, mildew, bipolaris, or netblotch.')
    parser.add_argument('-hw', '--hardware', required=True,
                        choices=['ipk', 'latrobe'],
                        help='Hardware type: "ipk" or "latrobe".')

    # Define current path and set up the data directory for test images
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(CURRENT_PATH, 'data')

    # Download test images if they are not already available locally
    orga.download_test_images(data_path)

    # Parse command-line arguments
    args = parser.parse_args()

    # Assign the source path from arguments, default to test images if specified
    source_path = args.source_path
    if source_path == 'test_images':
        source_path = data_path

    # # Define the storage path for leaf segmentation data
    # if args.procedure == 'mildew':
    #     # For mildew, use an additional level in the directory structure
    #     store_leaf_path = "//psg-09/Mikroskop/Training_data/PhenoDB/macrobot_rois/" + source_path.split('\\')[-3] + '/'\
    #                       + source_path.split('\\')[-2] + '/'
    # else:
    #     # For other pathogens, use a simpler structure
    #     store_leaf_path = "//psg-09/Mikroskop/Training_data/PhenoDB/macrobot_rois/" + source_path.split('\\')[-2] + '/'

    # Set the destination path where results will be saved
    destination_path = args.destination_path

    # Determine the segmentation method based on the selected procedure
    segmenter_class = {
        'rust': RustSegmenter,
        'rust_ipk': RustSegmenterIPK,
        'mildew': BgtSegmenter,
        'bipolaris': BipolarisSegmenter,
        'netblotch': NetBlotchSegmenter
    }.get(args.procedure)

    # Raise an error if an invalid procedure is provided
    if not segmenter_class:
        raise argparse.ArgumentError(None, f"Invalid segmentation method '{args.procedure}'")

    # Set the setting_file based on the hardware parameter
    if args.hardware == 'ipk':
        setting_file = "settings_ipk.ini"
        # For IPK, we collect training data
        path = Path(source_path)
        store_leaf_path = Path('//psg-09/Mikroskop/Images/Training_data_hsm/').joinpath(*path.parts[-2:])
        #print (store_leaf_path)
    elif args.hardware == 'latrobe':
        setting_file = "settings_latrobe.ini"
        store_leaf_path = None
    else:
        # This else block is optional since argparse enforces choices
        raise ValueError(f"Unsupported hardware type: {args.hardware}")

    # List all experiments (subdirectories) in the source directory
    experiments = os.listdir(source_path)
    for experiment in experiments:
        try:
            # For each experiment, list all 'dai' (days after inoculation) subdirectories
            dais = os.listdir(os.path.join(source_path, experiment))

            for dai in dais:
                # Create output directory for the current 'dai' (if it doesn't already exist)
                os.makedirs(os.path.join(destination_path, experiment, dai), exist_ok=True)

                # Print progress information
                print(f'\n=== Start Macrobot pipeline === \n Experiment: {experiment}')

                # Open a CSV file to record results for the current experiment and dai
                file_results = open(os.path.join(destination_path, experiment, dai, f'{experiment}_leaf.csv'), 'w')
                file_results.write('index;expNr;dai;Plate_ID;Lane_ID;Leaf_ID;%_Inf\n')

                # List all plates in the current 'dai' directory
                plates = os.listdir(os.path.join(source_path, experiment, dai))

                for plate in plates:
                    # Skip directories that don't match the required naming conventions (e.g., color/colour)
                    if not re.search('color', plate, re.IGNORECASE) and not re.search('colour', plate, re.IGNORECASE):
                        # Define the image directory for the current plate
                        img_dir = os.path.join(source_path, experiment, dai, plate)

                        # Get all .tif images from the directory
                        images = [f for f in os.listdir(img_dir) if f.endswith('.tif')]

                        # Initialize the segmentation processor for the current plate
                        processor = segmenter_class(
                            images,
                            img_dir,
                            destination_path,
                            store_leaf_path,
                            experiment,
                            dai,
                            file_results,
                            setting_file  # Pass the setting_file parameter
                        )

                        # Start the segmentation pipeline
                        processor.start_pipeline()
        except NotADirectoryError:
            # Skip any files or invalid directories in the source path
            print(f'Skip {os.path.join(source_path, experiment)} because it is not a valid directory.')

        # Print completion message for the current experiment
        print('\n=== End Macrobot pipeline ===')


if __name__ == "__main__":
    main()