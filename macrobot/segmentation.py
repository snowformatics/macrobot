import cv2
import numpy as np
from operator import itemgetter
from skimage.filters import threshold_otsu
from skimage import img_as_uint

from macrobot.prediction import predict_leaf


def segment_lanes_rgb(rgb_image, image_backlight, image_tresholded):
    """Extraction the lanes between the white frames.
       First we find and filter the contours of the threshold image to find the frames.
       Then we extract a rectangle inside the white frames and oder the position from left to right.

       :param rgb_image: 3-channel RGB image to extract the lanes.
       :type rgb_image: numpy array.
       :param image_backlight: The backlight image.
       :type image_backlight: numpy array.
       :param image_tresholded: The threshold image we use as source to find the frames.
       :type image_tresholded: numpy array.
       :return: Two list with contains the RGB and backlight lanes and their positions as tuple(image, position).
       :rtype: list
        """


    # Parameters for frame and lane size and shape
    last_x = 1000
    min_frame_area = 49000
    max_frame_area = 150000
    max_solidity = 0.5
    max_ratio = 1.0
    max_x_distance = 95
    offset_width = 160
    offset_height = 70
    offset_x = 80
    offset_y = 70
    width_min = 150
    width_max = 250
    lane_position = None

    # Get the contours of threshold image
    contours, hierarchy = cv2.findContours(image_tresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #cv2.drawContours(rgb_image, contours, -1, (0, 0, 255), 3)
    #cv2.imshow('', image_tresholded)
    #cv2.waitKey()

    # We temporary store the position, rgb and backlight roi in a list
    lanes = []
    for cnt in contours:
        if cv2.contourArea(cnt) > min_frame_area and cv2.contourArea(cnt) < max_frame_area:
            # For frame shape, solidity is a good feature and we filter by size
            area = cv2.contourArea(cnt)
            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            solidity = float(area) / hull_area

            if solidity < max_solidity:
                x, y, width, height = cv2.boundingRect(cnt)
                if float(width)/float(height) < max_ratio:
                    if abs(last_x - x) > max_x_distance:
                        last_x = x
                        width = width - offset_width
                        x = x + offset_x
                        y = y + offset_y
                        height = height - offset_height
                        if width > width_min and width < width_max:
                            lane_roi = rgb_image[y:y + height, x:x + width]
                            lane_roi_backlight = image_backlight[y:y + height, x:x + width]
                            lanes.append((lane_roi, int(x), lane_roi_backlight))

    # We sort the lanes by position from left to right
    lanes = sorted(lanes, key=itemgetter(1))

    if len(lanes) < 4:
        print ('Warning, < 4 lanes!', str(len(lanes)))

    # We store the rgb roi + position and backlight roi + position inside a separate list and return it for further
    # analysis
    lanes_roi_rgb = []
    lanes_roi_backlight = []

    # We check for missing lanes and get the correct lane number by plate position
    for lane in lanes:
        if lane[1] < 260:
            lane_position = 1
        elif lane[1] > 400 and lane[1] <= 615:
            lane_position = 2
        elif lane[1] > 800 and lane[1] < 1100:
            lane_position = 3
        elif lane[1] > 1100:
            lane_position = 4

        lanes_roi_rgb.append([lane_position, lane[0]])
        lanes_roi_backlight.append([lane_position, lane[2]])

    return lanes_roi_rgb, lanes_roi_backlight, len(lanes)


def segment_lanes_binary(lanes_roi_backlight):
    """Threshold the lanes by Otsu method to get a binary image for leaf segmentation.
       The backlight image is used for this step.

       :param lanes_roi_backlight: The lanes of the backlight image as list of tuple(image, position).
       :type lanes_roi_backlight: list
       :return: Two list with contains the backlight lanes as binary image and it's positions as tuple(image, position).
       :rtype: list
        """

    # We store the position and the binary lane roi in a list for further analysis
    lanes_roi_binary = []

    # We loop over all lanes:
    for lane in lanes_roi_backlight:

        # Otsu thresholding with skimage (performance is better then with opencv)
        thresholded_lane = threshold_otsu(lane[1])
        thresholded_lane = lane[1] < thresholded_lane
        thresholded_lane = img_as_uint(thresholded_lane)

        # We store the binary lane in a new array
        image_binary_lane = np.ones(lane[1].shape[:2], dtype="uint8") * 255

        # Try to separate touching leaves if rows contain mostly white pixels
        mean_rows = thresholded_lane.mean(axis=1)
        noise_row_nr = []
        counter = 0
        noise_thresh = 50
        for row in mean_rows:
            if row < noise_thresh:
                noise_row_nr.append(counter - 1)
            counter += 1

        # Segment the final image_name
        for i in range(lane[1].shape[0]):
            for j in range(lane[1].shape[1]):
                if i in noise_row_nr:
                    image_binary_lane[i, j] = 0
                else:
                    image_binary_lane[i, j] = thresholded_lane[i, j]

        lanes_roi_binary.append([lane[0], image_binary_lane])
    return lanes_roi_binary


def segment_leaf_binary(lanes_roi_binary, lanes_roi_rgb, plate_id, leaves_per_lane, predicted_lanes, destination_path,
                        y_position, experiment, dai, file_results, report_path, report=True):
    """Threshold the leaves by finding and filtering the contours of the binary lane image.

       :param lanes_roi_binary: The lanes of the binary image as list of tuple(image, position).
       :type lanes_roi_backlight: list
       :param lanes_roi_rgb: The lanes of the RGB image as list of tuple(image, position).
       :type lanes_roi_rgb: list
       :param plate_id: The plate ID.
       :type plate_id: str
       :param leaves_per_lane: maximum leaves per lane.
       :type leaves_per_lane: int
       :param predicted_lanes: The lanes of the predicted image as list of tuple(image, position).
       :type predicted_lanes: list
       :param destination_path: The path to store the final result images and csv file.
       :type destination_path: str
       :param y_position: Y Position for the leaves.
       :type y_position: int
       :param experiment: The experiment name.
       :type experiment: str
       :param dai: Days after inoculation.
       :type dai: str
       :param file_results: The CSV file for each experiments which contains the pathogen prediction per leaf.
       :type file_results: file object
       :return: Two list with contains the backlight lanes as binary image and it's positions as tuple(image, position).
       :rtype: list
        """

    # We loop over all lanes:
    for lane_id in range(len(lanes_roi_binary)):

        # RGB and binary lane must have the same positions
        assert lanes_roi_binary[lane_id][0] == lanes_roi_rgb[lane_id][0]

        # We get the binary lane image and close small holes
        image_binary_lane = lanes_roi_binary[lane_id][1]
        kernel = np.ones((3, 3), np.uint8)
        image_binary_lane = cv2.erode(image_binary_lane, kernel, iterations=1)

        # We get the corresponding RGB lane
        image_RGB_lane = lanes_roi_rgb[lane_id][1]


        # We get the corresponding Prediction lane
        image_prediction_lane = predicted_lanes[lane_id][1]

        # Some fixed variables (was 4000)
        leaf_id = 1
        min_leaf_size = 3000

        # We extract the contours and filter then by the leaf size
        contours, hierarchy = cv2.findContours(image_binary_lane, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours.reverse()

        for cnt in contours:
            if cv2.contourArea(cnt) > min_leaf_size:
                # We exclude all objects at the end of the lane, those are mostly false positives
                x, y, w, h = cv2.boundingRect(cnt)

                # Bounding box for web page and prediction
                bb_leaf_prediction = image_prediction_lane[y:y + h, x:x + w]
                bb_leaf_binary = image_binary_lane[y:y + h, x:x + w]


                if y < y_position:
                    hull = cv2.convexHull(cnt)
                    bb_leaf_rgb = image_RGB_lane[y:y + h, x:x + w]
                    #cv2.imwrite('test' + str(leaf_id) + '.png', bb_leaf_rgb)
                    #cv2.imshow('', bb_leaf_rgb)
                    #cv2.waitKey(0)

                    # We create a binary image for each leaf
                    mask = np.ones(image_binary_lane.shape[:2], dtype="uint8") * 255
                    cv2.drawContours(mask, [hull], -1, 0, -1)

                    #print(f"{leaf_counter:02d}")

                    # We draw all contours on the RGB image, this will be used as documentation image
                    if int(leaf_id) <= leaves_per_lane:
                        x2, y2, w2, h2 = cv2.boundingRect(hull)
                        #bb_leaf_rgb2 = image_RGB_lane[y2:y2 + h2, x2:x2 + w2]

                        cv2.drawContours(image_RGB_lane, [hull], -1, (0, 0, 255), 2)

                        image_prediction_lane_rgb = cv2.cvtColor(image_prediction_lane, cv2.COLOR_GRAY2RGB)
                        cv2.drawContours(image_prediction_lane_rgb, [hull], -1, (0, 0, 255), 2)


                        # cv2.drawContours(bb_leaf_rgb, [hull], -1, (0, 0, 255), 2)


                        bb_leaf_prediction2 = image_prediction_lane_rgb[y2:y2 + h2, x2:x2 + w2]
                        #cv2.imshow('', bb_leaf_prediction2)
                        #cv2.waitKey(0)
                        #cv2.imwrite('test2' + str(leaf_id) + '.png', bb_leaf_prediction2)

                        # We export the results in a csv file
                        # ToDo outsource
                        percent_infection = predict_leaf(bb_leaf_prediction, bb_leaf_binary)
                        unique_ID = str(experiment) + '_' + str(plate_id) + '_' + str(lanes_roi_rgb[lane_id][0])
                        file_results.write(str(unique_ID) + ';' + str(experiment) + ';' + 'NA' + ';' +
                                           str(plate_id) + ';' + str(lanes_roi_rgb[lane_id][0]) + ';' + str(leaf_id) + ';' +
                                           str(percent_infection) + '\n')


                    leaf_id += 1

        cv2.imwrite(destination_path + plate_id + '_' + str(lanes_roi_rgb[lane_id][0]) + '_leaf_predict.png', image_RGB_lane)
        # if report:
        #     cv2.imwrite(report_path + str(lanes_roi_rgb[lane_id][0]) + '_leaf.png', image_RGB_lane)


