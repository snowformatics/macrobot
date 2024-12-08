import numpy as np


def predict_min_rgb(minrgb_image: np.ndarray, backlight_image: np.ndarray, rgb_image: np.ndarray) -> np.ndarray:
    """
    Predict the presence of the pathogen by thresholding the minRGB image. Used for BGT (Botrytis Gray Mold).

    This function analyzes the minimum RGB channel image to identify areas likely affected by the BGT pathogen.
    It applies dynamic thresholding based on the backlight image to account for variations in lighting conditions.

    Parameters
    ----------
    minrgb_image : np.ndarray
        The minimum RGB feature image. Expected to be a 3-channel image where each pixel contains the minimum
        values across the RGB channels.
    backlight_image : np.ndarray
        The backlight image used for necrosis detection. This grayscale image assists in determining
        dynamic threshold values to handle lighting inconsistencies.
    rgb_image : np.ndarray
        The original RGB image. This is used to further refine predictions based on color channel differences.

    Returns
    -------
    np.ndarray
        The predicted binary image after thresholding. In the output image, pixels with a value of 255
        indicate the presence of the pathogen, while pixels with a value of 0 represent the background.

    Example
    -------
    >>> predicted = predict_min_rgb(min_rgb, backlight, rgb)
    """

    # Initialize the predicted image with all pixels set to 255 (pathogen)
    predicted_image = np.ones(minrgb_image.shape[:2], dtype="uint8") * 255

    # Because of the IFF backlight bug, calculate the mean intensity of the backlight image to determine dynamic thresholding
    if backlight_image.mean() > 3000:
        backlight_threshold = int(backlight_image.mean() / 1.5)
    else:
        backlight_threshold = int(backlight_image.mean() / 2.0)

    # Iterate over each pixel in the minRGB image
    for i in range(minrgb_image.shape[0]):
        for j in range(minrgb_image.shape[1]):
            # Check if the red and blue channels are zero, focusing on the green channel
            if minrgb_image[i, j][0] == 0 and minrgb_image[i, j][2] == 0:
                # Note: 40 without white balance, 60 with
                # Threshold the green channel to identify pathogen presence
                if minrgb_image[i, j][1] < 60 or minrgb_image[i, j][1] > 130:
                    predicted_image[i, j] = 0
                else:
                    predicted_image[i, j] = 255

                # Use backlight threshold to exclude yellow leaves without pathogen
                # 250 for new images, 700 for old
                backlight_threshold = 150
                if backlight_image[i, j] < backlight_threshold:
                    predicted_image[i, j] = 255
                else:
                    predicted_image[i, j] = 0
            else:
                # Further refine prediction based on RGB channel differences
                if abs(int(rgb_image[i, j][2]) - int(rgb_image[i, j][1])) < 3:
                    if minrgb_image[i, j][2] < 40:
                        predicted_image[i, j] = 0
                    else:
                        predicted_image[i, j] = 255
                else:
                    predicted_image[i, j] = 0
    return predicted_image


def predict_max_rgb(maxrgb_image: np.ndarray, backlight_image: np.ndarray, rgb_image: np.ndarray) -> np.ndarray:
    """
    Predict the presence of the pathogen by thresholding the maxRGB image.

    This function analyzes the maximum RGB channel image to identify areas likely affected by the pathogen.
    It applies dynamic thresholding based on the backlight image to account for variations in lighting conditions.

    Parameters
    ----------
    maxrgb_image : np.ndarray
        The maximum RGB feature image. Expected to be a 3-channel image where each pixel contains the maximum
        values across the RGB channels.
    backlight_image : np.ndarray
        The backlight image used for necrosis detection. This grayscale image assists in determining
        dynamic threshold values to handle lighting inconsistencies.
    rgb_image : np.ndarray
        The original RGB image. This is used to further refine predictions based on color channel differences.

    Returns
    -------
    np.ndarray
        The predicted binary image after thresholding. In the output image, pixels with a value of 255
        indicate the presence of the pathogen, while pixels with a value of 0 represent the background.

    Example
    -------
    >>> predicted = predict_max_rgb(max_rgb, backlight, rgb)
    """
    # Initialize the predicted image with all pixels set to 255 (pathogen)
    predicted_image = np.ones(maxrgb_image.shape[:2], dtype="uint8") * 255

    # Calculate the mean intensity of the backlight image to determine dynamic thresholding
    if backlight_image.mean() > 3000:
        backlight_threshold = int(backlight_image.mean() / 1.5)
    else:
        backlight_threshold = int(backlight_image.mean() / 2.0)
    # Iterate over each pixel in the maxRGB image
    for i in range(maxrgb_image.shape[0]):
        for j in range(maxrgb_image.shape[1]):
            # Threshold the red channel to identify pathogen presence
            if maxrgb_image[i, j][2] > 40 and maxrgb_image[i, j][2] < 110:
                predicted_image[i, j] = 255
            else:
                predicted_image[i, j] = 0
            # Further thresholding based on green and red channels to exclude certain areas
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

    return predicted_image


def predict_green_image(green_image: np.ndarray, backlight_image: np.ndarray, rgb_image: np.ndarray) -> np.ndarray:
    """
    Predict the presence of the pathogen by thresholding the green channel image. Used for Net Blotch.

    This function analyzes the green channel image to identify areas likely affected by the Net Blotch pathogen.
    It applies thresholding based on the backlight image to account for variations in lighting conditions.

    Parameters
    ----------
    green_image : np.ndarray
        The green channel feature image. Expected to be a single-channel grayscale image.
    backlight_image : np.ndarray
        The backlight image used for necrosis detection. This grayscale image assists in determining
        dynamic threshold values to handle lighting inconsistencies.
    rgb_image : np.ndarray
        The original RGB image. Currently not utilized in this function but included for consistency.

    Returns
    -------
    np.ndarray
        The predicted binary image after thresholding. In the output image, pixels with a value of 255
        indicate the presence of the pathogen, while pixels with a value of 0 represent the background.

    Example
    -------
    >>> predicted = predict_green_image(green_img, backlight, rgb)
    """

    # Initialize the predicted image with all pixels set to 255 (pathogen)
    predicted_image = np.ones(green_image.shape[:2], dtype="uint8") * 255

    # Calculate the mean intensity of the backlight image to determine dynamic thresholding
    if backlight_image.mean() > 3000:
        backlight_threshold = int(backlight_image.mean() / 1.5)
    else:
        backlight_threshold = int(backlight_image.mean() / 2.0)

    # Iterate over each pixel in the green channel image
    for i in range(green_image.shape[0]):
        for j in range(green_image.shape[1]):
            # Threshold the green channel to identify pathogen presence
            if green_image[i, j] < 28:
                predicted_image[i, j] = 255
            else:
                predicted_image[i, j] = 0


    return predicted_image


def predict_saturation(image_saturation: np.ndarray, image_backlight: np.ndarray) -> np.ndarray:
    """
    Predict the presence of the pathogen by thresholding the saturation channel image. Used for Rust.

    This function analyzes the saturation channel of the HSV color space to identify areas likely affected by the Rust pathogen.
    It applies thresholding based on both saturation values and the backlight image to enhance prediction accuracy.

    Parameters
    ----------
    image_saturation : np.ndarray
        The saturation feature image from the HSV color space. Expected to be a single-channel grayscale image.
    image_backlight : np.ndarray
        The backlight image used for necrosis detection. This grayscale image assists in determining
        additional threshold criteria to handle variations in lighting conditions.

    Returns
    -------
    np.ndarray
        The predicted binary image after thresholding. In the output image, pixels with a value of 255
        indicate the presence of the pathogen, while pixels with a value of 0 represent the background.

    Example
    -------
    >>> predicted = predict_saturation(saturation_img, backlight)
    """
    # Initialize the predicted image with all pixels set to 255 (pathogen)
    predicted_image = np.ones(image_saturation.shape[:2], dtype="uint8") * 255

    # Iterate over each pixel in the saturation image

    for i in range(image_saturation.shape[0]):
            for j in range(image_saturation.shape[1]):
                if image_saturation[i, j] > 130 and image_backlight[i, j] < 1000:
                    predicted_image[i, j] = 255
                else:
                    predicted_image[i, j] = 0
    return predicted_image


def predict_leaf(predicted_image: np.ndarray, leaf_binary_image: np.ndarray) -> float:
    """
    Calculate the percentage of infection per leaf based on predicted and binary images.

    This function compares the predicted pathogen image with the binary leaf image to determine the
    extent of infection. It calculates the infected area as a percentage of the total leaf area.

    Parameters
    ----------
    predicted_image : np.ndarray
        The predicted binary image indicating pathogen presence. Pixels with a value of 255 represent
        pathogen-infected areas, while pixels with a value of 0 represent the background.
    leaf_binary_image : np.ndarray
        The binary leaf image used to define the area of the leaf. Pixels with a value of 255 represent
        the leaf, while pixels with a value of 0 represent the background.

    Returns
    -------
    float
        The percentage of the leaf area infected by the pathogen, calculated as:
        (black_pixels / white_pixels) * 100
        where black_pixels represent infected areas and white_pixels represent healthy leaf areas.

    Example
    -------
    >>> infection_percentage = predict_leaf(predicted_img, leaf_binary_img)
    """

    # Initialize counters for white and black pixels
    white_counter = 0  # Total leaf area
    black_counter = 0  # Infected area

    # Initialize the result image (optional visualization, currently unused)
    image_result = np.ones(predicted_image.shape[:2], dtype="uint8") * 255

    # Iterate over each pixel in the binary images
    for i in range(leaf_binary_image.shape[0]):
        for j in range(leaf_binary_image.shape[1]):
            if leaf_binary_image[i, j] == 255:
                white_counter += 1 # Count the total leaf area
                if predicted_image[i, j] == 0:
                    image_result[i, j] = 0
                    black_counter += 1 # Count the infected area
                else:
                    image_result[i, j] = 255
    # Calculate the percentage of infection
    return (round(100-(black_counter * 100 / white_counter)))
