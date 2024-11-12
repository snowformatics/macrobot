import cv2
import numpy as np
import os
from operator import itemgetter
from skimage.filters import threshold_otsu
from skimage import img_as_uint
from configparser import ConfigParser

from macrobot.prediction import predict_leaf


class Segmentation:
    def __init__(self, hardware):
        """Initialize the SegmentationConfig class and load configuration settings."""
        #self.load_config(hardware)
        self.hardware = hardware

    def load_config(self, hardware):
        """Load and scale configuration settings based on the selected hardware."""
        # Load configuration
        config = ConfigParser()
        config.read('settings.ini')
        #print (hardware)

        # Load hardware-specific settings
        image_width = config.getint(hardware, 'image_width')
        image_height = config.getint(hardware, 'image_height')
        scaling_factor = config.getfloat(hardware, 'scaling_factor')
        # Load cropping values from the config
        crop_left = config.getint(hardware, 'crop_left')
        crop_right = config.getint(hardware, 'crop_right')
        crop_top = config.getint(hardware, 'crop_top')
        crop_bottom = config.getint(hardware, 'crop_bottom')

        # Step 1: Apply cropping
        cropped_width = image_width - crop_left - crop_right
        cropped_height = image_height - crop_top - crop_bottom

        # Step 2: Apply scaling
        image_width = int(cropped_width * scaling_factor)
        image_height = int(cropped_height * scaling_factor)

        # # # Output the results
        # print("Final dimensions after cropping and scaling:")
        # print(f"Width: {image_width}")
        # print(f"Height: {image_height}")

        # Load baseline (HARDWARE1) settings for scaling reference
        baseline_width = config.getint('HARDWARE1', 'image_width')
        baseline_height = config.getint('HARDWARE1', 'image_height')

        # Calculate scaling ratios based on the hardware-specific image dimensions
        width_ratio = image_width / baseline_width
        height_ratio = image_height / baseline_height

        # Load and scale segmentation parameters
        self.last_x = config.getint('SEGMENTATION', 'last_x')
        self.min_frame_area = int(config.getint('SEGMENTATION', 'min_frame_area') * width_ratio * height_ratio)
        self.max_frame_area = int(config.getint('SEGMENTATION', 'max_frame_area') * width_ratio * height_ratio)
        self.max_solidity = config.getfloat('SEGMENTATION', 'max_solidity')
        self.max_ratio = config.getfloat('SEGMENTATION', 'max_ratio')
        self.offset_width = int(config.getint('SEGMENTATION', 'offset_width')* width_ratio * height_ratio)
        self.offset_height = int(config.getint('SEGMENTATION', 'offset_height') * width_ratio * height_ratio)
        self.offset_x = int(config.getint('SEGMENTATION', 'offset_x') * width_ratio * height_ratio)
        self.offset_y = int(config.getint('SEGMENTATION', 'offset_y') * width_ratio * height_ratio)
        self.width_min = int(config.getint('SEGMENTATION', 'width_min') * width_ratio * height_ratio)
        self.width_max = int(config.getint('SEGMENTATION', 'width_max') * width_ratio * height_ratio)
        self.max_x_distance = int(config.getint('SEGMENTATION', 'max_x_distance') * width_ratio * height_ratio)
        self.bordersize = config.getint('SEGMENTATION', 'bordersize')
        self.noise_thresh = config.getint('SEGMENTATION', 'noise_thresh')
        self.min_leaf_size = int(config.getint('SEGMENTATION', 'min_leaf_size') * width_ratio * height_ratio)
        self.y_position = int(config.getint('SEGMENTATION', 'y_position') * width_ratio * height_ratio)
        self.leaves_per_lane = config.getint('SEGMENTATION', 'leaves_per_lane')
        self.lane_positions = [int(int(x) * width_ratio * height_ratio) for x in
                               config.get('SEGMENTATION', 'lane_positions').split(',')]

        # # """Print all loaded configuration settings."""
        # print("Loaded Configuration Settings:")
        # print(f"  last_x = {self.last_x}")
        # print(f"  min_frame_area = {self.min_frame_area}")
        # print(f"  max_frame_area = {self.max_frame_area}")
        # print(f"  max_solidity = {self.max_solidity}")
        # print(f"  max_ratio = {self.max_ratio}")
        # print(f"  offset_width = {self.offset_width}")
        # print(f"  offset_height = {self.offset_height}")
        # print(f"  offset_x = {self.offset_x}")
        # print(f"  offset_y = {self.offset_y}")
        # print(f"  width_min = {self.width_min}")
        # print(f"  width_max = {self.width_max}")
        # print(f"  max_x_distance = {self.max_x_distance}")
        # print(f"  bordersize = {self.bordersize}")
        # print(f"  noise_thresh = {self.noise_thresh}")
        # print(f"  min_leaf_size = {self.min_leaf_size}")
        # print(f"  y_position = {self.y_position}")
        # print(f"  leaves_per_lane = {self.leaves_per_lane}")
        # print(f"  lane_positions = {self.lane_positions}")

    def segment_lanes_rgb(self, rgb_image, image_backlight, image_tresholded, experiment, plate_id):
        """Extracts and sorts the lanes in an RGB image based on detected frames in a thresholded image."""
        self.load_config(self.hardware)
        # Initialize last_x to None to track the last x position within the loop
        last_x = None

        # Apply a white border around the threshold image to handle possible shifts in plate position
        image_tresholded = cv2.copyMakeBorder(
            image_tresholded,
            top=self.bordersize,
            bottom=self.bordersize,
            left=self.bordersize,
            right=self.bordersize,
            borderType=cv2.BORDER_CONSTANT,
            value=[255, 255, 255]
        )

        # Detect contours in the thresholded image to locate frames around lanes
        contours, _ = cv2.findContours(image_tresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #cv2.drawContours(rgb_image, contours, -1, (0, 0, 255), 3)

        lanes = []

        # Iterate over each detected contour and filter based on size and solidity
        for cnt in contours:
            area = cv2.contourArea(cnt)

            if self.min_frame_area < area < self.max_frame_area:

                hull = cv2.convexHull(cnt)
                solidity = float(area) / cv2.contourArea(hull)

                # Filter based on shape and solidity to identify lane frames
                if solidity < self.max_solidity:
                    x, y, width, height = cv2.boundingRect(cnt)

                    if last_x is None or (
                            float(width) / height < self.max_ratio and abs(last_x - x) > self.max_x_distance):
                        last_x = x  # Update last_x after checking the condition

                        x += self.offset_x
                        y += self.offset_y
                        width -= self.offset_width
                        height -= self.offset_height


                        # Ensure detected frames meet the min/max width requirements
                        if self.width_min < width < self.width_max:
                            lane_roi = rgb_image[y:y + height, x:x + width]
                            lane_roi_backlight = image_backlight[y:y + height, x:x + width]
                            lanes.append((lane_roi, x, lane_roi_backlight))

        # Sort lanes by their horizontal position (left to right)
        lanes = sorted(lanes, key=itemgetter(1))

        lanes_roi_rgb, lanes_roi_backlight = [], []

        # Assign lane positions based on thresholds from the config
        for lane in lanes:

            if lane[1] < self.lane_positions[0]:
                lane_position = 1
            elif lane[1] > self.lane_positions[1] and lane[1] <= self.lane_positions[2]:
                lane_position = 2
            elif lane[1] > self.lane_positions[3] and lane[1] < self.lane_positions[4]:
                lane_position = 3
            elif lane[1] > self.lane_positions[4]:
                lane_position = 4

            lanes_roi_rgb.append([lane_position, lane[0]])
            lanes_roi_backlight.append([lane_position, lane[2]])

        return lanes_roi_rgb, lanes_roi_backlight, len(lanes)

    def segment_lanes_binary(self, lanes_roi_backlight):
        """Converts backlight lanes to binary images for leaf segmentation using Otsu thresholding."""
        self.load_config(self.hardware)
        lanes_roi_binary = []
        for lane in lanes_roi_backlight:
            # Apply Otsu's thresholding to generate a binary image
            thresholded_lane = lane[1] < threshold_otsu(lane[1])
            thresholded_lane = img_as_uint(thresholded_lane)
            image_binary_lane = np.ones(thresholded_lane.shape, dtype="uint8") * 255

            # Identify noisy rows based on intensity and adjust binary image accordingly
            mean_rows = thresholded_lane.mean(axis=1)
            noise_row_nr = [i for i, row in enumerate(mean_rows) if row < self.noise_thresh]

            for i in range(thresholded_lane.shape[0]):
                for j in range(thresholded_lane.shape[1]):
                    if i in noise_row_nr:
                        image_binary_lane[i, j] = 0
                    else:
                        image_binary_lane[i, j] = thresholded_lane[i, j]

            lanes_roi_binary.append([lane[0], image_binary_lane])
        return lanes_roi_binary

    def segment_leaf_binary(self, lanes_roi_binary, lanes_roi_rgb, plate_id, leaves_per_lane, predicted_lanes, destination_path,
                            y_position, experiment, dai, file_results, store_leaf_path, report_path, report=True):
        """Segments leaves in binary lane images by filtering based on contours."""
        self.load_config(self.hardware)
        #print (y_position)
        #print (self.y_position)

        for lane_id in range(len(lanes_roi_binary)):
            # Ensure each lane has matching RGB and binary images
            assert lanes_roi_binary[lane_id][0] == lanes_roi_rgb[lane_id][0]
            image_binary_lane = cv2.erode(lanes_roi_binary[lane_id][1], np.ones((3, 3), np.uint8), iterations=1)
            image_RGB_lane = lanes_roi_rgb[lane_id][1]
            image_prediction_lane = predicted_lanes[lane_id][1]
            leaf_id = 1

            # Find contours in the binary lane image for leaf segmentation
            contours, _ = cv2.findContours(image_binary_lane, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in reversed(contours):
                if cv2.contourArea(cnt) > self.min_leaf_size:
                    x, y, w, h = cv2.boundingRect(cnt)

                    # Filter out any objects that exceed the Y-position threshold
                    if y < self.y_position:
                        hull = cv2.convexHull(cnt)
                        bb_leaf_rgb = image_RGB_lane[y:y + h, x:x + w]
                        if store_leaf_path:
                            cv2.imwrite(os.path.join(store_leaf_path, f"{experiment}_{plate_id}_{leaf_id}_rgb.png"),
                                        bb_leaf_rgb)

                        # If within the max leaves per lane, analyze and store results
                        if leaf_id <= self.leaves_per_lane:
                            #print (plate_id)
                            cv2.drawContours(image_RGB_lane, [hull], -1, (0, 0, 255), 2)
                            percent_infection = predict_leaf(image_prediction_lane[y:y + h, x:x + w],
                                                             image_binary_lane[y:y + h, x:x + w])

                            unique_ID = f"{experiment}_{plate_id.split('_')[-1]}_{lanes_roi_rgb[lane_id][0]}"
                            #print (plate_id)
                            file_results.write(
                                f"{unique_ID};{experiment};{dai};{plate_id};{lanes_roi_rgb[lane_id][0]};{leaf_id};{percent_infection}\n")
                        leaf_id += 1

            # Save annotated RGB lane image showing segmented leaves
            cv2.imwrite(os.path.join(destination_path, f"{plate_id}_{lanes_roi_rgb[lane_id][0]}_leaf_predict.png"),
                        image_RGB_lane)

# import cv2
# import numpy as np
# import os
# from operator import itemgetter
# from skimage.filters import threshold_otsu
# from skimage import img_as_uint
#
# from macrobot.prediction import predict_leaf
#
#
# def segment_lanes_rgb(rgb_image, image_backlight, image_tresholded, experiment, plate_id):
#     """Extraction the lanes between the white frames.
#        First we find and filter the contours of the threshold image to find the frames.
#        Then we extract a rectangle inside the white frames and oder the position from left to right.
#
#        :param rgb_image: 3-channel RGB image to extract the lanes.
#        :type rgb_image: numpy array.
#        :param image_backlight: The backlight image.
#        :type image_backlight: numpy array.
#        :param image_tresholded: The threshold image we use as source to find the frames.
#        :type image_tresholded: numpy array.
#        :return: Two list with contains the RGB and backlight lanes and their positions as tuple(image, position).
#        :rtype: list
#         """
#
#
#     # Parameters for frame and lane size and shape
#     last_x = 1000
#     min_frame_area = 45000 #45000
#     max_frame_area = 150000
#     max_solidity = 0.5
#     max_ratio = 1.0
#     # for shifted plates!
#     #max_x_distance = 95
#
#     offset_width = 160
#     offset_height = 70
#     offset_x = 80
#     offset_y = 70
#     # only la torbe
#     width_min = 120
#     max_x_distance = 40
#     # rest #150 #145!!!
#     #width_min = 150
#     #max_x_distance = 50
#
#     width_max = 250
#     lane_position = None
#
#
#     # We have to apply a border (white frame) around the threhsold image in case the plates was with worng position
#     # during image aquisition
#     bordersize = 5
#     border = cv2.copyMakeBorder(
#         image_tresholded,
#         top=bordersize,
#         bottom=bordersize,
#         left=bordersize,
#         right=bordersize,
#         borderType=cv2.BORDER_CONSTANT,
#         value=[255, 255, 255]
#     )
#     image_tresholded = border
#     # Get the contours of threshold image
#     contours, hierarchy = cv2.findContours(image_tresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#     # cv2.drawContours(rgb_image, contours, -1, (0, 0, 255), 3)
#     # cv2.imshow('', rgb_image)
#     # cv2.waitKey()
#
#     # We temporarily store the position, rgb and backlight roi in a list
#     lanes = []
#     for cnt in contours:
#
#         if cv2.contourArea(cnt) > min_frame_area and cv2.contourArea(cnt) < max_frame_area:
#
#             # For frame shape, solidity is a good feature and we filter by size
#             area = cv2.contourArea(cnt)
#             hull = cv2.convexHull(cnt)
#             hull_area = cv2.contourArea(hull)
#             solidity = float(area) / hull_area
#            # print (solidity)
#
#             if solidity < max_solidity:
#                 x, y, width, height = cv2.boundingRect(cnt)
#
#                 if float(width)/float(height) < max_ratio:
#                     #print (abs(last_x - x))
#                     if abs(last_x - x) > max_x_distance:
#
#                         last_x = x
#                         width = width - offset_width
#                         x = x + offset_x
#                         y = y + offset_y
#                         height = height - offset_height
#                         #print (width)
#                         if width > width_min and width < width_max:
#                             #print(cv2.contourArea(cnt))  #
#                             lane_roi = rgb_image[y:y + height, x:x + width]
#                             lane_roi_backlight = image_backlight[y:y + height, x:x + width]
#                             lanes.append((lane_roi, int(x), lane_roi_backlight))
#
#     # We sort the lanes by position from left to right
#     lanes = sorted(lanes, key=itemgetter(1))
#
#
#     if len(lanes) < 4:
#         print ('Warning, < 4 lanes!', str(len(lanes)))
#         log_file = open('log.txt', 'a')
#         print (experiment, plate_id)
#         log_file.write(experiment + '\t' + plate_id + '\t' + 'Warning, < 4 lanes!' + str(len(lanes)) + '\n')
#
#     # We store the rgb roi + position and backlight roi + position inside a separate list and return it for further
#     # analysis
#     lanes_roi_rgb = []
#     lanes_roi_backlight = []
#
#     # We check for missing lanes and get the correct lane number by plate position
#
#     for lane in lanes:
#         if lane[1] == None:
#             print ('None')
#         #print (lane[1])
#         #cv2.imshow('', lane[0])
#         #cv2.waitKey(0)
#         if lane[1] < 270:
#             lane_position = 1
#         elif lane[1] > 400 and lane[1] <= 675:
#             lane_position = 2
#         elif lane[1] > 790 and lane[1] < 1100:
#             lane_position = 3
#         elif lane[1] > 1100:
#             lane_position = 4
#
#         lanes_roi_rgb.append([lane_position, lane[0]])
#         lanes_roi_backlight.append([lane_position, lane[2]])
#
#     return lanes_roi_rgb, lanes_roi_backlight, len(lanes)
#
#
# def segment_lanes_binary(lanes_roi_backlight):
#     """Threshold the lanes by Otsu method to get a binary image for leaf segmentation.
#        The backlight image is used for this step.
#
#        :param lanes_roi_backlight: The lanes of the backlight image as list of tuple(image, position).
#        :type lanes_roi_backlight: list
#        :return: Two list with contains the backlight lanes as binary image and it's positions as tuple(image, position).
#        :rtype: list
#         """
#
#     # We store the position and the binary lane roi in a list for further analysis
#     lanes_roi_binary = []
#
#     # We loop over all lanes:
#     for lane in lanes_roi_backlight:
#
#         # Otsu thresholding with skimage (performance is better then with opencv)
#         thresholded_lane = threshold_otsu(lane[1])
#         thresholded_lane = lane[1] < thresholded_lane
#         thresholded_lane = img_as_uint(thresholded_lane)
#
#         # We store the binary lane in a new array
#         image_binary_lane = np.ones(lane[1].shape[:2], dtype="uint8") * 255
#
#         # Try to separate touching leaves if rows contain mostly white pixels
#         mean_rows = thresholded_lane.mean(axis=1)
#         noise_row_nr = []
#         counter = 0
#         noise_thresh = 50
#         for row in mean_rows:
#             if row < noise_thresh:
#                 noise_row_nr.append(counter - 1)
#             counter += 1
#
#         # Segment the final image_name
#         for i in range(lane[1].shape[0]):
#             for j in range(lane[1].shape[1]):
#                 if i in noise_row_nr:
#                     image_binary_lane[i, j] = 0
#                 else:
#                     image_binary_lane[i, j] = thresholded_lane[i, j]
#
#         lanes_roi_binary.append([lane[0], image_binary_lane])
#     return lanes_roi_binary
#
#
# def segment_leaf_binary(lanes_roi_binary, lanes_roi_rgb, plate_id, leaves_per_lane, predicted_lanes, destination_path,
#                         y_position, experiment, dai, file_results, store_leaf_path, report_path, report=True):
#     """Threshold the leaves by finding and filtering the contours of the binary lane image.
#
#        :param lanes_roi_binary: The lanes of the binary image as list of tuple(image, position).
#        :type lanes_roi_backlight: list
#        :param lanes_roi_rgb: The lanes of the RGB image as list of tuple(image, position).
#        :type lanes_roi_rgb: list
#        :param plate_id: The plate ID.
#        :type plate_id: str
#        :param leaves_per_lane: maximum leaves per lane.
#        :type leaves_per_lane: int
#        :param predicted_lanes: The lanes of the predicted image as list of tuple(image, position).
#        :type predicted_lanes: list
#        :param destination_path: The path to store the final result images and csv file.
#        :type destination_path: str
#        :param y_position: Y Position for the leaves.
#        :type y_position: int
#        :param experiment: The experiment name.
#        :type experiment: str
#        :param dai: Days after inoculation.
#        :type dai: str
#        :param file_results: The CSV file for each experiments which contains the pathogen prediction per leaf.
#        :type file_results: file object
#        :return: Two list with contains the backlight lanes as binary image and it's positions as tuple(image, position).
#        :rtype: list
#         """
#     #print (y_position)
#     # We loop over all lanes:
#     for lane_id in range(len(lanes_roi_binary)):
#
#         # RGB and binary lane must have the same positions
#         assert lanes_roi_binary[lane_id][0] == lanes_roi_rgb[lane_id][0]
#
#         # We get the binary lane image and close small holes
#         image_binary_lane = lanes_roi_binary[lane_id][1]
#         kernel = np.ones((3, 3), np.uint8)
#         image_binary_lane = cv2.erode(image_binary_lane, kernel, iterations=1)
#
#         # We get the corresponding RGB lane
#         image_RGB_lane = lanes_roi_rgb[lane_id][1]
#
#
#         # We get the corresponding Prediction lane
#         image_prediction_lane = predicted_lanes[lane_id][1]
#
#         # Some fixed variables (was 4000)
#         leaf_id = 1
#         min_leaf_size = 3000
#         #max_leaf_size = 150
#
#         # We extract the contours and filter then by the leaf size
#         contours, hierarchy = cv2.findContours(image_binary_lane, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#         contours.reverse()
#
#         #cv2.drawContours(image_binary_lane, contours, -1, (0, 0, 255), 3)
#         #cv2.imshow('', image_binary_lane)
#         #cv2.waitKey()
#
#         for cnt in contours:
#             if cv2.contourArea(cnt) > min_leaf_size:
#                # print (len(cnt))
#                 # We exclude all objects at the end of the lane, those are mostly false positives
#                 x, y, w, h = cv2.boundingRect(cnt)
#
#                 # Bounding box for web page and prediction
#                 bb_leaf_prediction = image_prediction_lane[y:y + h, x:x + w]
#                 bb_leaf_binary = image_binary_lane[y:y + h, x:x + w]
#
#                 if y < y_position:
#                     hull = cv2.convexHull(cnt)
#                     bb_leaf_rgb = image_RGB_lane[y:y + h, x:x + w]
#                     if store_leaf_path:
#                         cv2.imwrite(os.path.join(store_leaf_path, str(experiment) + '_' + str(plate_id) + '_' + str(leaf_id) + '_rgb.png'), bb_leaf_rgb)
#                     #cv2.imshow('', bb_leaf_rgb)
#                     #cv2.waitKey(0)
#
#                     # We create a binary image for each leaf
#                     mask = np.ones(image_binary_lane.shape[:2], dtype="uint8") * 255
#                     cv2.drawContours(mask, [hull], -1, 0, -1)
#
#                     #print(f"{leaf_counter:02d}")
#
#                     # We draw all contours on the RGB image, this will be used as documentation image
#                     if int(leaf_id) <= leaves_per_lane:
#                         x2, y2, w2, h2 = cv2.boundingRect(hull)
#                         #bb_leaf_rgb2 = image_RGB_lane[y2:y2 + h2, x2:x2 + w2]
#
#                         cv2.drawContours(image_RGB_lane, [hull], -1, (0, 0, 255), 2)
#
#                         image_prediction_lane_rgb = cv2.cvtColor(image_prediction_lane, cv2.COLOR_GRAY2RGB)
#                         bb_leaf_prediction2 = image_prediction_lane_rgb[y2:y2 + h2, x2:x2 + w2]
#                         if store_leaf_path:
#                             cv2.imwrite(os.path.join(store_leaf_path, str(experiment) + '_' + str(plate_id) + '_' + str(
#                                 leaf_id) + '_binary.png'), bb_leaf_prediction2)
#                         cv2.drawContours(image_prediction_lane_rgb, [hull], -1, (0, 0, 255), 2)
#
#                         # We export the results in a csv file
#                         # ToDo outsource
#                         percent_infection = predict_leaf(bb_leaf_prediction, bb_leaf_binary)
#                         #unique_ID = str(experiment) + '_' + str(plate_id) + '_' + str(lanes_roi_rgb[lane_id][0])
#                         unique_ID = str(experiment) + '_' + str(plate_id.split('_')[-1]) + '_' + str(lanes_roi_rgb[lane_id][0])
#                         #print (str(plate_id.split('_')[-1]), plate_id, unique_ID)
#                         #id2 = str(experiment) + '_' + str(plate_id) + '_' + str(lanes_roi_rgb[lane_id][0]) + '_' + str(leaf_id)
#                         file_results.write(str(unique_ID) + ';' + str(experiment) + ';' + str(dai) + ';' +
#                                            str(plate_id) + ';' + str(lanes_roi_rgb[lane_id][0]) + ';' + str(leaf_id) + ';' +
#                                            str(percent_infection) + '\n')
#
#
#                     leaf_id += 1
#
#         cv2.imwrite(os.path.join(destination_path, plate_id + '_' + str(lanes_roi_rgb[lane_id][0]) + '_leaf_predict.png'), image_RGB_lane)
#         # if report:
#         #     cv2.imwrite(report_path + str(lanes_roi_rgb[lane_id][0]) + '_leaf.png', image_RGB_lane)
#
#
