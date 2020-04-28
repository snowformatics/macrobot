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

plate_id, numer_of_lanes, final_image_list, file_name = mildew_pipeline()



def test_number_of_ids():
    assert numer_of_lanes == 4


def test_plate_id():
    assert plate_id == "20190709_102939_exp40_P02-3"


def test_csv_file():
    csv1 = open(file_name, "r").readlines()
    csv2 = open("gb2_exp40_leaf.csv", "r").readlines()
    assert list(difflib.unified_diff(csv1, csv2)) == []

# final_image_list = [self.image_tresholded , self.image_backlight, self.image_red, self.image_blue,
#                             self.image_green, self.image_rgb, self.image_uvs, self.lanes_roi_rgb,self.lanes_roi_binary,
#                             self.lanes_roi_minrgb, self.predicted_lanes]


def test_image_backlight():
    np.save("test1.npy", final_image_list[1])
    data1 = np.fromfile("image_backlight.npy")
    data2 = np.fromfile('test1.npy')
    print (final_image_list[1])
    print(data1, data2)
    assert np.array_equal(data1, data2)


def test_image_red():
    np.save("test2.npy", final_image_list[2])
    data1 = np.fromfile("image_red.npy")
    data2 = np.fromfile('test2.npy')
    assert np.array_equal(data1, data2)


def test_image_blue():
    np.save("test.npy", final_image_list[3])
    data1 = np.fromfile("image_blue.npy")
    data2 = np.fromfile('test.npy')
    assert np.array_equal(data1, data2)


def test_image_green():
    np.save("test.npy", final_image_list[4])
    data1 = np.fromfile("image_green.npy")
    data2 = np.fromfile('test.npy')
    assert np.array_equal(data1, data2)


# def test_image_rgb():
#     np.save("test.npy", final_image_list[5])
#     data1 = np.fromfile("image_rgb.npy")
#     data2 = np.fromfile('test.npy')
#     np.assert_allclose(data1, data2, rtol=1e-1, atol=0)
#     #assert np.array_equal(data1, data2)

def test_image_uvs():
    np.save("test.npy", final_image_list[6])
    data1 = np.fromfile("image_uvs.npy")
    data2 = np.fromfile('test.npy')
    assert np.array_equal(data1, data2)


def test_lanes_roi_rgb():
    np.save("test.npy", final_image_list[7])
    data1 = np.fromfile("lanes_roi_rgb.npy")
    data2 = np.fromfile('test.npy')
    print (data1, data2)
    assert np.array_equal(data1, data2)