import cv2
import numpy as np
import os
from operator import itemgetter
from skimage.filters import threshold_otsu
from skimage import img_as_uint
from configparser import ConfigParser
from macrobot.prediction import predict_leaf

def segment_lanes_rgb(rgb_image: np.ndarray, image_backlight: np.ndarray, image_thresholded: np.ndarray,
                     experiment: str, plate_id: str, setting_file: str) -> tuple:
    """
    Extract lanes between white frames from an RGB image.

    This function identifies and extracts lanes from the provided RGB image by:
    1. Loading segmentation parameters from a configuration file.
    2. Applying a white border to the thresholded image to handle misaligned plates.
    3. Finding and filtering contours based on area, solidity, and aspect ratio.
    4. Extracting regions of interest (ROIs) within the identified frames.
    5. Sorting the extracted lanes from left to right based on their x-coordinate positions.

    Parameters
    ----------
    rgb_image : np.ndarray
        A 3-channel RGB image from which lanes will be extracted.
    image_backlight : np.ndarray
        The backlight image corresponding to the RGB image.
    image_thresholded : np.ndarray
        A thresholded binary image used to identify the frames for lane extraction.
    experiment : str
        The name or identifier of the current experiment.
    plate_id : str
        The identifier for the specific plate being processed.
    setting_file : str
        Path to the configuration file containing segmentation parameters.

    Returns
    -------
    tuple
        A tuple containing:
            - lanes_roi_rgb (list): List of tuples with lane position and RGB ROI.
            - lanes_roi_backlight (list): List of tuples with lane position and backlight ROI.
            - lane_count (int): Total number of lanes extracted.

    Raises
    ------
    ConfigParser.Error
        If the configuration file cannot be read or lacks required parameters.

    Example
    -------
    >>> lanes_rgb, lanes_backlight, count = segment_lanes_rgb(rgb_img, backlight_img, thresh_img,
                                                              "Experiment1", "PlateA1", "settings.ini")
    """
    # Initialize ConfigParser and load settings
    config = ConfigParser()
    config.read(setting_file)

    # Retrieve segmentation parameters from the configuration file
    last_x = config.getint('SEGMENTATION', 'last_x')
    min_frame_area = config.getint('SEGMENTATION', 'min_frame_area')
    max_frame_area = config.getint('SEGMENTATION', 'max_frame_area')
    max_solidity = config.getfloat('SEGMENTATION', 'max_solidity')
    max_ratio = config.getfloat('SEGMENTATION', 'max_ratio')
    offset_width = config.getint('SEGMENTATION', 'offset_width')
    offset_height = config.getint('SEGMENTATION', 'offset_height')
    offset_x = config.getint('SEGMENTATION', 'offset_x')
    offset_y = config.getint('SEGMENTATION', 'offset_y')
    width_min = config.getint('SEGMENTATION', 'width_min')
    width_max = config.getint('SEGMENTATION', 'width_max')
    max_x_distance = config.getint('SEGMENTATION', 'max_x_distance')
    bordersize = config.getint('SEGMENTATION', 'bordersize')
    lane_positions = [int(x) for x in config.get('SEGMENTATION', 'lane_positions').split(',')]

    lane_position = None

    # Apply a white border to the thresholded image to handle potential misalignments
    border = cv2.copyMakeBorder(
        image_thresholded,
        top=bordersize,
        bottom=bordersize,
        left=bordersize,
        right=bordersize,
        borderType=cv2.BORDER_CONSTANT,
        value=[255, 255, 255]
    )
    image_thresholded = border

    # Find contours in the thresholded image
    contours, hierarchy = cv2.findContours(image_thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize a list to store lane information
    lanes = []

    # Iterate over each contour to identify valid lanes
    for cnt in contours:
        contour_area = cv2.contourArea(cnt)
        if min_frame_area < contour_area < max_frame_area:
            # Calculate solidity to filter out non-rectangular contours
            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            solidity = float(contour_area) / hull_area

            if solidity < max_solidity:
                x, y, width, height = cv2.boundingRect(cnt)

                # Filter based on aspect ratio to ensure lane shape
                if (float(width) / float(height)) < max_ratio:
                    # Ensure lanes are sufficiently spaced horizontally
                    if abs(last_x - x) > max_x_distance:
                        last_x = x
                        # Apply offsets and adjust width and height
                        width = width - offset_width
                        x = x + offset_x
                        y = y + offset_y
                        height = height - offset_height

                        # Validate lane dimensions
                        if width_min < width < width_max:
                            # Extract ROI for both RGB and backlight images
                            lane_roi = rgb_image[y:y + height, x:x + width]
                            lane_roi_backlight = image_backlight[y:y + height, x:x + width]
                            lanes.append((lane_roi, int(x), lane_roi_backlight))

    # Sort lanes based on their x-coordinate positions (left to right)
    lanes = sorted(lanes, key=itemgetter(1))

    # Warn if fewer than expected lanes are found
    if len(lanes) < 4:
        print(f'Warning, < 4 lanes! Found: {len(lanes)}')
        with open('log.txt', 'a') as log_file:
            log_file.write(f"{experiment}\t{plate_id}\tWarning, < 4 lanes! Found: {len(lanes)}\n")

    # Initialize lists to store sorted ROI information
    lanes_roi_rgb = []
    lanes_roi_backlight = []

    # Assign lane positions based on predefined lane_positions
    for lane in lanes:
        x_position = lane[1]
        if x_position < lane_positions[0]:
            lane_position = 1
        elif lane_positions[1] < x_position <= lane_positions[2]:
            lane_position = 2
        elif lane_positions[3] < x_position < lane_positions[4]:
            lane_position = 3
        elif x_position > lane_positions[4]:
            lane_position = 4
        else:
            lane_position = None  # Handle unexpected positions if necessary

        # Append the ROI and its position to the respective lists
        lanes_roi_rgb.append([lane_position, lane[0]])
        lanes_roi_backlight.append([lane_position, lane[2]])

    return lanes_roi_rgb, lanes_roi_backlight, len(lanes)


def segment_lanes_binary(lanes_roi_backlight: list, setting_file: str) -> list:
    """
    Convert backlight lane ROIs to binary images using Otsu's thresholding.

    This function processes each backlight lane ROI by applying Otsu's thresholding
    to generate a binary image suitable for leaf segmentation. It also attempts to
    separate touching leaves by analyzing row-wise pixel intensities.

    Parameters
    ----------
    lanes_roi_backlight : list
        A list of tuples containing lane positions and corresponding backlight ROIs.
    setting_file : str
        Path to the configuration file containing segmentation parameters.

    Returns
    -------
    list
        A list of lists, each containing the lane position and its corresponding
        binary image.

    Raises
    ------
    ConfigParser.Error
        If the configuration file cannot be read or lacks required parameters.

    Example
    -------
    >>> binary_lanes = segment_lanes_binary(lanes_backlight, "settings.ini")
    """
    # Initialize ConfigParser and load settings
    config = ConfigParser()
    config.read(setting_file)
    noise_thresh = config.getint('SEGMENTATION', 'noise_thresh')

    # Initialize a list to store binary lane images
    lanes_roi_binary = []

    # Iterate over each backlight lane ROI
    for lane in lanes_roi_backlight:
        lane_position, lane_image_backlight = lane

        # Apply Otsu's thresholding to obtain a binary image
        otsu_threshold = threshold_otsu(lane_image_backlight)
        thresholded_lane = lane_image_backlight < otsu_threshold
        thresholded_lane = img_as_uint(thresholded_lane)

        # Initialize a white binary image
        image_binary_lane = np.ones(lane_image_backlight.shape[:2], dtype="uint8") * 255

        # Analyze row-wise mean to identify noise rows
        mean_rows = thresholded_lane.mean(axis=1)
        noise_row_nr = [idx - 1 for idx, row in enumerate(mean_rows) if row < noise_thresh]

        # Segment the binary image by zeroing out noise rows
        for i in range(lane_image_backlight.shape[0]):
            if i in noise_row_nr:
                image_binary_lane[i, :] = 0
            else:
                image_binary_lane[i, :] = thresholded_lane[i, :]

        # Append the binary lane image and its position to the list
        lanes_roi_binary.append([lane_position, image_binary_lane])

    return lanes_roi_binary


def segment_leaf_binary(lanes_roi_binary: list, lanes_roi_rgb: list, plate_id: str, predicted_lanes: list,
                        destination_path: str, experiment: str, dai: str, file_results, store_leaf_path: str,
                        setting_file: str) -> None:
    """
    Segment individual leaves from binary lane images and perform infection prediction.

    This function processes each binary lane to identify and segment individual leaves by:
    1. Loading segmentation parameters from a configuration file.
    2. Eroding the binary image to remove small artifacts.
    3. Finding contours corresponding to leaves and filtering based on size.
    4. Extracting bounding boxes for each leaf and performing infection prediction.
    5. Saving segmented leaf images and recording prediction results.

    Parameters
    ----------
    lanes_roi_binary : list
        A list of tuples containing lane positions and corresponding binary lane images.
    lanes_roi_rgb : list
        A list of tuples containing lane positions and corresponding RGB lane ROIs.
    plate_id : str
        The identifier for the specific plate being processed.
    predicted_lanes : list
        A list of tuples containing lane positions and corresponding predicted lane images.
    destination_path : str
        The directory path where the final result images and CSV files will be stored.
    experiment : str
        The name or identifier of the current experiment.
    dai : str
        Days after inoculation (experimental time point).
    file_results : file object
        The CSV file object where prediction results per leaf will be recorded.
    store_leaf_path : str
        The directory path where individual leaf images will be saved.
    setting_file : str
        Path to the configuration file containing segmentation parameters.

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If lane positions between binary and RGB lanes do not match.
    ConfigParser.Error
        If the configuration file cannot be read or lacks required parameters.

    Example
    -------
    >>> segment_leaf_binary(binary_lanes, rgb_lanes, "PlateA1", predicted_lanes, "/results",
                           "Experiment1", "5", csv_file, "/leaves", "settings.ini")
    """
    # Initialize ConfigParser and load settings
    config = ConfigParser()
    config.read(setting_file)
    y_position = config.getint('SEGMENTATION', 'y_position')
    min_leaf_size = config.getint('SEGMENTATION', 'min_leaf_size')
    leaves_per_lane = config.getint('SEGMENTATION', 'leaves_per_lane')

    # Iterate over each lane by index
    for lane_id in range(len(lanes_roi_binary)):
        binary_lane_position, image_binary_lane = lanes_roi_binary[lane_id]
        rgb_lane_position, image_RGB_lane = lanes_roi_rgb[lane_id]
        predicted_lane_position, image_prediction_lane = predicted_lanes[lane_id]

        # Ensure lane positions match across different lane representations
        assert binary_lane_position == rgb_lane_position == predicted_lane_position, \
            "Lane positions do not match across binary, RGB, and predicted lanes."

        # Erode the binary image to remove small noise
        kernel = np.ones((3, 3), np.uint8)
        image_binary_lane = cv2.erode(image_binary_lane, kernel, iterations=1)

        # Initialize leaf ID counter
        leaf_id = 1

        # Find contours in the binary lane image
        contours, hierarchy = cv2.findContours(image_binary_lane, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours.reverse()  # Optional: Process contours in reverse order if needed

        # Iterate over each contour to identify valid leaves
        for cnt in contours:
            contour_area = cv2.contourArea(cnt)
            if contour_area > min_leaf_size:
                x, y, w, h = cv2.boundingRect(cnt)

                # Extract bounding boxes for prediction and binary images
                bb_leaf_prediction = image_prediction_lane[y:y + h, x:x + w]
                bb_leaf_binary = image_binary_lane[y:y + h, x:x + w]

                # Exclude leaves located below a certain y-position to avoid false positives
                if y < y_position:
                    hull = cv2.convexHull(cnt)
                    bb_leaf_rgb = image_RGB_lane[y:y + h, x:x + w]

                    # Save RGB leaf image if path is provided
                    if store_leaf_path:
                        leaf_rgb_path = os.path.join(store_leaf_path,
                                                     f"{experiment}_{plate_id}_{leaf_id}_rgb.png")
                        cv2.imwrite(leaf_rgb_path, bb_leaf_rgb)

                    # Create a mask for the convex hull of the leaf
                    mask = np.ones(image_binary_lane.shape[:2], dtype="uint8") * 255
                    cv2.drawContours(mask, [hull], -1, 0, -1)

                    # Process only a limited number of leaves per lane
                    if leaf_id <= leaves_per_lane:
                        x2, y2, w2, h2 = cv2.boundingRect(hull)

                        # Draw convex hull on the RGB lane image for visualization
                        cv2.drawContours(image_RGB_lane, [hull], -1, (0, 0, 255), 2)

                        # Convert prediction lane to RGB for visualization
                        image_prediction_lane_rgb = cv2.cvtColor(image_prediction_lane, cv2.COLOR_GRAY2RGB)
                        bb_leaf_prediction2 = image_prediction_lane_rgb[y2:y2 + h2, x2:x2 + w2]

                        # Save binary prediction image if path is provided
                        if store_leaf_path:
                            leaf_binary_path = os.path.join(store_leaf_path,
                                                            f"{experiment}_{plate_id}_{leaf_id}_binary.png")
                            cv2.imwrite(leaf_binary_path, bb_leaf_prediction2)

                        # Draw convex hull on the prediction lane image for visualization
                        cv2.drawContours(image_prediction_lane_rgb, [hull], -1, (0, 0, 255), 2)

                        # Perform infection prediction on the leaf
                        percent_infection = predict_leaf(bb_leaf_prediction, bb_leaf_binary)

                        # Generate a unique identifier for the leaf
                        unique_ID = f"{experiment}_{plate_id.split('_')[-1]}_{rgb_lane_position}"

                        # Record prediction results in the CSV file
                        file_results.write(f"{unique_ID};{experiment};{dai};{plate_id};"
                                           f"{rgb_lane_position};{leaf_id};{percent_infection}\n")

                    leaf_id += 1

        # Save the annotated RGB lane image with predictions
        prediction_image_path = os.path.join(destination_path,
                                             f"{plate_id}_{rgb_lane_position}_leaf_predict.png")
        cv2.imwrite(prediction_image_path, image_RGB_lane)
