import numpy as np
import cv2


def predict_min_rgb(minrgb_image, backlight_image, rgb_image):
    """Predict the pathogen by thresholding the minRGB image. Used for BGT.

       :param minrgb_image: The min RGB feature image.
       :type minrgb_image: numpy array.
       :param backlight_image: The backlight image used for necrosis detection.
       :type backlight_image: numpy array.
       :param rgb_image: The RGB image.
       :type rgb_image: numpy array.
       :return: The predicted image after thresholding.  255 = pathogen, 0 = background
       :rtype: numpy array
    """

    predicted_image = np.ones(minrgb_image.shape[:2], dtype="uint8") * 255

    # Because of the IFF backlight bug, we need a dynamic threshold for a yellow leaf filter, 2.0 is better if no
    # bug appears, otherwise 1.5
    if backlight_image.mean() > 3000:
        backlight_threshold = int(backlight_image.mean() / 1.5)
    else:
        backlight_threshold = int(backlight_image.mean() / 2.0)

    for i in range(minrgb_image.shape[0]):
        for j in range(minrgb_image.shape[1]):
            if minrgb_image[i, j][0] == 0 and minrgb_image[i, j][2] == 0:
                # Note: 40 without white balance, 60 with
                if minrgb_image[i, j][1] < 60 or minrgb_image[i, j][1] > 130:
                    predicted_image[i, j] = 0
                else:
                    predicted_image[i, j] = 255

                # This is a feature for excluding yellow leaves without pathogen, the backlight images gives bright
                # signal which we use as threshold
                # 250 for new images, 700 for old
                backlight_threshold = 150
                if backlight_image[i, j] < backlight_threshold:
                    predicted_image[i, j] = 255
                else:
                    predicted_image[i, j] = 0
            else:
                if abs(int(rgb_image[i, j][2]) - int(rgb_image[i, j][1])) < 3:
                    if minrgb_image[i, j][2] < 40:
                        predicted_image[i, j] = 0
                    else:
                        predicted_image[i, j] = 255
                else:
                    predicted_image[i, j] = 0
    return predicted_image


def predict_max_rgb(maxrgb_image, backlight_image, rgb_image):
    """Predict the pathogen by thresholding the maxRGB image. Used for BGT.

       :param maxrgb_image: The max RGB feature image.
       :type maxrgb_image: numpy array.
       :param backlight_image: The backlight image used for necrosis detection.
       :type backlight_image: numpy array.
       :param rgb_image: The RGB image.
       :type rgb_image: numpy array.
       :return: The predicted image after thresholding.  255 = pathogen, 0 = background
       :rtype: numpy array
    """

    predicted_image = np.ones(maxrgb_image.shape[:2], dtype="uint8") * 255
    #cv2.imwrite('out.png', maxrgb_image)
    #cv2.imshow('', maxrgb_image)
    #cv2.waitKey()

    # Because of the IFF backlight bug, we need a dynamic threshold for a yellow leaf filter, 2.0 is better if no
    # bug appears, otherwise 1.5
    if backlight_image.mean() > 3000:
        backlight_threshold = int(backlight_image.mean() / 1.5)
    else:
        backlight_threshold = int(backlight_image.mean() / 2.0)

    for i in range(maxrgb_image.shape[0]):
        for j in range(maxrgb_image.shape[1]):

            if maxrgb_image[i, j][2] > 40 and maxrgb_image[i, j][2] < 110:
                predicted_image[i, j] = 255
            else:
                predicted_image[i, j] = 0
            if maxrgb_image[i, j][1] > 50 and maxrgb_image[i, j][2] > 50:
                predicted_image[i, j] = 0

            #This is a feature for excluding yellow leaves without pathogen, the backlight images gives bright
            #signal which we use as threshold
            #250 for new images, 700 for old
            # backlight_threshold = 150
            # if backlight_image[i, j] < backlight_threshold:
            #     predicted_image[i, j] = 0
            # else:
            #     predicted_image[i, j] = 255
            # else:
            #
            #     if abs(int(rgb_image[i, j][2]) - int(rgb_image[i, j][1])) < 3:
            #         if maxrgb_image[i, j][2] < 60:
            #             predicted_image[i, j] = 255
            #         else:
            #             predicted_image[i, j] = 0
            #     else:
            #         predicted_image[i, j] = 0
    #cv2.imshow('', predicted_image)
    #cv2.waitKey()
    return predicted_image


def predict_saturation(image_saturation, image_backlight):
    """Predict the pathogen by thresholding the saturation image. Used for Rust.

           :param image_saturation: The saturation feature image of HSV color space.
           :type image_saturation: numpy array.
           :param image_backlight: The backlight image used for necrosis detection.
           :type image_backlight: numpy array.
           :return: The predicted image after thresholding.  255 = pathogen, 0 = background
           :rtype: numpy array
        """

    predicted_image = np.ones(image_saturation.shape[:2], dtype="uint8") * 255
    for i in range(image_saturation.shape[0]):
        for j in range(image_saturation.shape[1]):
            if image_saturation[i, j] > 130 and image_backlight[i, j] < 1000:
                predicted_image[i, j] = 255
            else:
                predicted_image[i, j] = 0
    return predicted_image


def predict_leaf(predicted_image, leaf_binary_image):
    """Predict the pathogen per leaf.

       :param predicted_image: The predicted image with the pathogen. 255 = pathogen, 0 = background
       :type predicted_image: numpy array.
       :param leaf_binary_image: The binary leaf image to extract the leaf.
       :type leaf_binary_image: numpy array.
       :return: The infected area in percent. black_pixels * 100 / white_pixels
       :rtype: numpy array
        """

    white_counter = 0
    black_counter = 0

    image_result = np.ones(predicted_image.shape[:2], dtype="uint8") * 255
    for i in range(leaf_binary_image.shape[0]):
        for j in range(leaf_binary_image.shape[1]):
            if leaf_binary_image[i, j] == 255:
                white_counter += 1
                if predicted_image[i, j] == 0:
                    image_result[i, j] = 0
                    black_counter += 1
                else:
                    image_result[i, j] = 255
    #cv2.imshow('', image_result)
    #cv2.waitKey(0)
    return (round(100-(black_counter * 100 / white_counter)))
