import numpy as np
import cv2
import os
from macrobot.helpers import rgb_features
from macrobot import segmentation
from macrobot.mb_pipeline import MacrobotPipeline
from macrobot.prediction import predict_green_image
import glob
from macrobot.helpers import whitebalance

class NetBlotchSegmenter(MacrobotPipeline):
    """Macrobot analysis for Net Blotch pathogen."""

    NAME = 'NetBlotch'

    def preprocess_raw_images(self, image_lst):
        for image_name in image_lst:
            if not image_name.startswith("processed_"):
                # Load image
                image = cv2.imread(os.path.join(self.path, image_name), cv2.IMREAD_UNCHANGED)
                # Rotate 90 degrees clockwise
                rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
                # Get dimensions after rotation
                height, width = rotated_image.shape[:2]
                # Crop 150 pixels from top and bottom
                cropped_image = rotated_image[400:height - 400, :]
                # Save the processed image as needed
                if "_bg.tif" in image_name:
                    image_name = image_name.replace("_bg.tif", "_backlight.tif")
                cv2.imwrite(os.path.join(self.path, 'processed_' + image_name), cropped_image)
        images = [f for f in os.listdir(self.path) if f.endswith('.tif')]
        return images

    def do_whitebalance(self):
        """Calling white balance function in helpers module."""
        self.image_rgb = whitebalance(self.image_rgb, 0.2)

    def read_images(self):
        """We override this read function because plates from la trobe macrobot need to be preprocessed"""
        """Reading and resizing the images."""
        for image in self.image_list:

            if image.startswith("processed_"):
                #print (image, image.endswith('_backlight.tif'))

                if image.endswith('_backlight.tif'):
                    self.image_backlight = cv2.resize(cv2.imread(os.path.join(self.path, image), cv2.IMREAD_UNCHANGED),
                                                      (0, 0), fx=self.resize_scale, fy=self.resize_scale)
                elif image.endswith('_red.tif'):
                    self.image_red = cv2.resize(cv2.imread(os.path.join(self.path, image), cv2.IMREAD_GRAYSCALE), (0, 0),
                                                fx=self.resize_scale, fy=self.resize_scale)
                elif image.endswith('_blue.tif'):
                    self.image_blue = cv2.resize(cv2.imread(os.path.join(self.path, image), cv2.IMREAD_GRAYSCALE), (0, 0),
                                                 fx=self.resize_scale, fy=self.resize_scale)
                elif image.endswith('_green.tif'):
                    self.image_green = cv2.resize(cv2.imread(os.path.join(self.path, image), cv2.IMREAD_GRAYSCALE), (0, 0),
                                                  fx=self.resize_scale, fy=self.resize_scale)
                elif image.endswith('uvs.tif') or image.endswith('uv.tif'):
                    self.image_uvs = cv2.resize(cv2.imread(os.path.join(self.path, image), cv2.IMREAD_GRAYSCALE), (0, 0),
                                                fx=self.resize_scale, fy=self.resize_scale)
        assert self.image_backlight.shape == self.image_red.shape == self.image_blue.shape == self.image_green.shape == self.image_uvs.shape
    def get_frames(self, image_source):
        """Segment the white frame on a microtiter plate.
           Algorithm is based on Otsu thresholding of the UVS image.

           :param image_source: The UVS-image (x, y, 1) which is used as source for thresholding.
           :type image_source: numpy array.
           :return: The binary image after Otsu thresholding.
           :rtype: numpy array
        """
        # from skimage.filters import try_all_threshold
        # import matplotlib.pyplot as plt
        # fig, ax = try_all_threshold(image_source, figsize=(10, 8), verbose=False)
        # # Show the plot
        # plt.show()

        _, image_tresholded = cv2.threshold(image_source, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        kernel = np.ones((8,8), np.uint8)
        image_tresholded = cv2.dilate(image_tresholded, kernel, iterations=3)
        #cv2.imshow('', image_tresholded)
        #cv2.waitKey()
        return image_tresholded

    def get_leaves_binary(self):
        """Segment the single leaves."""

        # For la trobe setup we need to override this
        self.y_position = 700
        segmentation.segment_leaf_binary(self.lanes_roi_binary, self.lanes_roi_rgb, self.plate_id, 8, self.predicted_lanes,
                                         self.destination_path, self.y_position, self.experiment, self.dai, self.file_results,
                                         self.store_leaf_path, self.report_path)

    def get_lanes_rgb(self):
        """Calls segment_lanes_rgb to extract the RGB lanes within the white frames."""
        self.image_tresholded = self.get_frames(self.image_blue)
        self.lanes_roi_rgb, self.lanes_roi_backlight, self.numer_of_lanes = segmentation.segment_lanes_rgb(self.image_rgb,
                                                                                      self.image_backlight,
                                                                                      self.image_tresholded,
                                                                                    self.experiment,
                                                                                    self.plate_id)


    def get_features(self):
        """Feature extraction for Bgt based on Maxiumum intensity projection (MaxIP).


           :return: A list with the features per lane and it's position sorted left to right.
           :rtype: list with tuple(feature, position)
        """

        # We store the Max RGB images and the position for further analysis
        self.lanes_feature = []
        # For each RGB lane we extract max RGB features
        for lane in self.lanes_roi_rgb:
            copy_lane = np.copy(lane[1])
            B, G, R = cv2.split(copy_lane)
            self.lanes_feature.append([lane[0], G])
            cv2.imwrite(self.destination_path + '/' + str(lane[0]) + '.png', G)
            #cv2.imshow('', G)
            #cv2.waitKey()

        return self.lanes_feature

    def get_prediction_per_lane(self, plate_id, destination_path):
        """Predict the Bgt pathogen from the feature extraction method based on thresholding. 255 = pathogen, 0 = background

           :return: A list with the predictions per lane and it's position sorted left to right.
           :rtype: list with tuple(prediction, position)
        """
        self.predicted_lanes = []
        for i in range(len(self.lanes_feature)):
            predicted_image = predict_green_image(self.lanes_feature[i][1], self.lanes_roi_backlight[i][1],
                                              self.lanes_roi_rgb[i][1])
            cv2.imwrite(os.path.join(destination_path, plate_id + '_' + str(self.lanes_feature[i][0]) + '_disease_predict.png'), predicted_image)

            self.predicted_lanes.append([self.lanes_feature[i][0], predicted_image])
        return self.predicted_lanes
