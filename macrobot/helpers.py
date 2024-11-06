# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Image helper functions.
"""

import numpy as np
import cv2

__author__ = "Stefanie Lueck"
__copyright__ = "Stefanie Lueck"
__license__ = "NonCommercial-ShareAlike 2.0 Generic (CC BY-NC-SA 2.0) License"


def wb_helper(channel, perc):

    """Performing a white balance on a single channel.

       :param channel: 1-channel image.
       :type channel: numpy array.
       :param perc: Percentile.
       :type perc: float
       :return: The channel after white balance.
       :rtype: numpy array
        """

    mi, ma = (np.percentile(channel, perc), np.percentile(channel, 100.0 - perc))
    channel = np.uint8(np.clip((channel - mi) * 255.0 / (ma - mi), 0, 255))
    return channel


def whitebalance(image, perc):
    """Performing a white balance on a 3-channel image.

       Similar to GIMP white balance method.

       :param image: 3-channel image.
       :type image: numpy array.
       :return: The 3-channel image after white balance.
       :rtype: numpy array
            """
    image_split = np.dsplit(image, image.shape[-1])
    image_wb = np.dstack([wb_helper(channel, perc) for channel in (image_split[0], image_split[1], image_split[2])])
    return image_wb


def rgb_features(image_array, feature_type):
    """Extract min or max intensity projection.

       Example Maximum RGB=[50,100,79] -> max_rgb=[0, 100, 0]

       Example Minimum RGB=[50,100,79] -> min_rgb=[50, 0, 0].

       :param image_array: 3-channel image.
       :type image_array: numpy array.
       :param feature_type: minimum or maximum
       :type feature_type: numpy array.
       :return: The 3-channel image after intensity projection.
       :rtype: numpy array
        """
    # Split the image into channels
    [R, G, B] = np.dsplit(image_array, image_array.shape[-1])

    if feature_type == "minimum":
        # find the minimum pixel intensity values for each (x, y)-coordinate
        M = np.minimum(np.minimum(R, G), B)
        R[R > M] = 0
        G[G > M] = 0
        B[B > M] = 0

    elif feature_type == "maximum":
        M = np.maximum(np.maximum(R, G), B)
        R[R < M] = 0
        G[G < M] = 0
        B[B < M] = 0
    else:
        print("Sorry, filter type not supported!")

    # Stack channels into RGB image
    return np.dstack((R, G, B))


def get_saturation(image):
    """Extract the saturation channel of a 3-channel image from the HSV color space.

       :param image: 3-channel image.
       :type image: numpy array.

       :return: The 1-channel image saturation channel.
       :rtype: numpy array
        """
    hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    sat = hsv_image[:, :, 1]
    return sat


# def save_img_array():
#     # l = [(self.image_tresholded, 'image_tresholded_array')
#     # , (self.image_backlight, "image_backlight")
#     # , (self.image_red, "image_red")
#     # , (self.image_blue, "image_blue")
#     # , (self.image_green, "image_green")
#     # , (self.image_rgb, "image_rgb")
#     # , (self.image_uvs, "image_uvs")
#     # , (self.lanes_roi_rgb, "lanes_roi_rgb")
#     # , (self.lanes_roi_backlight, "lanes_roi_backlight")
#     # , (self.lanes_roi_binary, "lanes_roi_binary")
#     # , (self.lanes_roi_minrgb, "lanes_roi_minrgb")
#     # , (self.predicted_lanes, "predicted_lanes")]
#     #
#     l =  [(lanes_roi_rgb, "lanes_roi_rgb")]
#
#     #print (self.image_tresholded[0])
#     #np.save('test', self.image_tresholded)
#
#     for x in l:
#         np.save(x[1], x[0])
#
#     # x = np.load('image_tresholded_array.npy')
#     # print(x[0])
