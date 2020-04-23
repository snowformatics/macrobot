import numpy as np

from macrobot.helpers import rgb_features, whitebalance

array = np.array([[[1,2,3], [1,2,3], [1,2,3]],
                  [[4,5,6], [4,5,6], [4,5,6]],
                  [[7,8,9], [7,8,9], [7,8,9]]])


def test_min_rgb():
    image_array = np.copy(array)
    min_rgb_test_data = np.load('min_rgb_data.npy')
    min_rgb_featrue = rgb_features(image_array, 'minimum')
    np.testing.assert_array_equal(min_rgb_featrue, min_rgb_test_data)


def test_max_rgb():
    max_rgb_test_data = np.load('max_rgb_data.npy')
    image_array = np.copy(array)
    max_rgb_featrue = rgb_features(image_array, 'maximum')
    np.testing.assert_array_equal(max_rgb_featrue, max_rgb_test_data)


def test_whitebalance():
    whitebalance_test_data = np.load('whitebalance_data.npy')
    image_array = np.copy(array)
    wb = whitebalance(image_array)
    np.testing.assert_array_equal(wb, whitebalance_test_data)

