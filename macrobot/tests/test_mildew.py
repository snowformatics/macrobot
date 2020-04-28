import os
from macrobot.bgt import BgtSegmenter


def mildew_pipeline():
    source_path = "C:/Users/lueck/PycharmProjects/BluVision/tests/macrobot/images/bgt/"
    destination_path = "C:/Users/lueck/PycharmProjects/BluVision/tests/macrobot/results/"
    experiments = os.listdir(source_path)
    for experiment in experiments:
        try:
            dais = os.listdir(source_path + experiment + '/')
            for dai in dais:
                try:
                    os.makedirs(destination_path + experiment + '/' + dai + '/')
                except FileExistsError:
                    pass
                print('\n=== Start Macrobot pipeline === \n Experiment: ' + experiment)
                file_results = open(destination_path + experiment + '/' + dai + '/' + str(experiment) + '_leaf.csv',
                                    'a')
                file_results.write(
                    'index' + ';' + 'expNr' + ';' + 'barcode' + ';' + 'Plate_ID' + ';' + 'Lane_ID' + ';' + 'Leaf_ID' + ';' + '%_Inf' + '\n')

                plates = os.listdir(source_path + experiment + '/' + dai + '/')

                for plate in plates:
                    img_dir = source_path + experiment + '/' + dai + '/' + plate + '/'
                    images = [f for f in os.listdir(img_dir) if f.endswith('.tif')]
                    processor = BgtSegmenter(images, img_dir, destination_path, experiment, dai, file_results)
                    plate_id, numer_of_lanes, final_image_list, file_name = processor.start_pipeline()

                    #print (self.plate_id)

        except NotADirectoryError:
            print('Skip ' + source_path + experiment + ' because it is not a directory.')

        print('\n=== End Macrobot pipeline ===')

        return plate_id, numer_of_lanes, final_image_list, file_name

plate_id, numer_of_lanes, final_image_list, file_name = mildew_pipeline()


def test_number_of_ids():
    assert numer_of_lanes == 4


def test_plate_id():
    assert plate_id == "20190709_102939_exp40_P02-3"

#



    #

