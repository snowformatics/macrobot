import os
import difflib
import numpy as np
from macrobot.bgt import BgtSegmenter

test_path = os.path.dirname(os.path.abspath(__file__))


def mildew_pipeline():
    source_path = os.path.join(os.path.dirname(test_path), 'data')
    destination_path = os.path.join(os.path.dirname(test_path), 'results')
    store_leaf_path = None

    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    experiments = os.listdir(source_path)

    for experiment in experiments:
        try:
            dais = os.listdir(os.path.join(source_path, experiment))
            for dai in dais:
                try:
                    os.makedirs(os.path.join(destination_path, experiment, dai))
                except FileExistsError:
                    pass
                print('\n=== Start Macrobot pipeline === \n Experiment: ' + experiment)
                file_results = open(os.path.join(destination_path, experiment, dai, str(experiment) + '_leaf.csv'), 'w')
                file_results.write(
                    'index' + ';' + 'expNr' + ';' + 'barcode' + ';' + 'Plate_ID' + ';' + 'Lane_ID' + ';' + 'Leaf_ID' + ';' + '%_Inf' + '\n')

                plates = os.listdir(os.path.join(source_path, experiment, dai))

                for plate in plates:
                    img_dir = os.path.join(source_path, experiment, dai, plate)
                    images = [f for f in os.listdir(img_dir) if f.endswith('.tif')]
                    processor = BgtSegmenter(images, img_dir, destination_path, store_leaf_path, experiment, dai, file_results)
                    plate_id, numer_of_lanes, final_image_list, file_name = processor.start_pipeline()

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
    csv2 = open(os.path.join(test_path, "gb2_exp40_leaf.csv"), "r").readlines()
    assert list(difflib.unified_diff(csv1, csv2)) == []


def test_image_tresholded():
    data = np.load(os.path.join(test_path, "image_tresholded.npy"))
    assert np.array_equal(final_image_list[0], data)


def test_image_backlight():
    data = np.load(os.path.join(test_path, "image_backlight.npy"))
    assert np.array_equal(final_image_list[1], data)


def test_image_red():
    data = np.load(os.path.join(test_path, "image_red.npy"))
    assert np.array_equal(final_image_list[2], data)


def test_image_blue():
    data = np.load(os.path.join(test_path, "image_blue.npy"))
    assert np.array_equal(final_image_list[3], data)


def test_image_green():
    data = np.load(os.path.join(test_path, "image_green.npy"))
    assert np.array_equal(final_image_list[4], data)


def test_image_rgb():
    data = np.load(os.path.join(test_path, "image_rgb.npy"))
    assert np.array_equal(final_image_list[5], data)


def test_image_uvs():
    data = np.load(os.path.join(test_path, "image_uvs.npy"))
    assert np.array_equal(final_image_list[6], data)


def test_lanes_roi_rgb():
    data = np.load(os.path.join(test_path, "lanes_roi_rgb.npy"), allow_pickle=True)
    for i in range(len(final_image_list[7])):
        assert np.array_equal(final_image_list[7][i][1], data[i][1])
        assert np.array_equal(final_image_list[7][i][0], data[i][0])


def test_lanes_roi_binary():
    data = np.load(os.path.join(test_path, "lanes_roi_binary.npy"), allow_pickle=True)
    for i in range(len(final_image_list[8])):
        assert np.array_equal(final_image_list[8][i][1], data[i][1])
        assert np.array_equal(final_image_list[8][i][0], data[i][0])


def test_lanes_roi_minrgb():
    data = np.load(os.path.join(test_path, "lanes_roi_minrgb.npy"), allow_pickle=True)
    for i in range(len(final_image_list[9])):
        assert np.array_equal(final_image_list[9][i][1], data[i][1])
        assert np.array_equal(final_image_list[9][i][0], data[i][0])


def test_predicted_lanes():
    data = np.load(os.path.join(test_path, "predicted_lanes.npy"), allow_pickle=True)
    for i in range(len(final_image_list[10])):
        assert np.array_equal(final_image_list[10][i][1], data[i][1])
        assert np.array_equal(final_image_list[10][i][0], data[i][0])

