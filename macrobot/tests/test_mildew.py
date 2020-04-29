import os
import difflib
import numpy as np

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
                file_results = open(destination_path + experiment + '/' + dai + '/' + str(experiment) + '_leaf.csv', 'w')
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


# We run the entire pipeline with one test plate to get all the results we need for testing
plate_id, numer_of_lanes, final_image_list, file_name = mildew_pipeline()


# Start testing each step of the pipeline
def test_number_of_ids():
    assert numer_of_lanes == 4


def test_plate_id():
    assert plate_id == "20190709_102939_exp40_P02-3"


def test_csv_file():
    csv1 = open(file_name, "r").readlines()
    csv2 = open("gb2_exp40_leaf.csv", "r").readlines()
    assert list(difflib.unified_diff(csv1, csv2)) == []


def test_image_tresholded():
    data = np.load("image_tresholded.npy")
    assert np.array_equal(final_image_list[0], data)


def test_image_backlight():
    data = np.load("image_backlight.npy")
    assert np.array_equal(final_image_list[1], data)


def test_image_red():
    data = np.load("image_red.npy")
    assert np.array_equal(final_image_list[2], data)


def test_image_blue():
    data = np.load("image_blue.npy")
    assert np.array_equal(final_image_list[3], data)


def test_image_green():
    data = np.load("image_green.npy")
    assert np.array_equal(final_image_list[4], data)


def test_image_rgb():
    data = np.load("image_rgb.npy")
    assert np.array_equal(final_image_list[5], data)


def test_image_uvs():
    data = np.load("image_uvs.npy")
    assert np.array_equal(final_image_list[6], data)


def test_lanes_roi_rgb():
    data = np.load("lanes_roi_rgb.npy", allow_pickle=True)
    for i in range(len(final_image_list[7])):
        assert np.array_equal(final_image_list[7][i][1], data[i][1])
        assert np.array_equal(final_image_list[7][i][0], data[i][0])


def test_lanes_roi_binary():
    data = np.load("lanes_roi_binary.npy", allow_pickle=True)
    for i in range(len(final_image_list[8])):
        assert np.array_equal(final_image_list[8][i][1], data[i][1])
        assert np.array_equal(final_image_list[8][i][0], data[i][0])


def test_lanes_roi_minrgb():
    data = np.load("lanes_roi_minrgb.npy", allow_pickle=True)
    for i in range(len(final_image_list[9])):
        assert np.array_equal(final_image_list[9][i][1], data[i][1])
        assert np.array_equal(final_image_list[9][i][0], data[i][0])


def test_predicted_lanes():
    data = np.load("predicted_lanes.npy", allow_pickle=True)
    for i in range(len(final_image_list[10])):
        assert np.array_equal(final_image_list[10][i][1], data[i][1])
        assert np.array_equal(final_image_list[10][i][0], data[i][0])