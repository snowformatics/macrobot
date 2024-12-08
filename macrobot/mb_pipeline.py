#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import os
from configparser import ConfigParser
from macrobot.helpers import whitebalance
from macrobot import orga
from macrobot import segmentation

class MacrobotPipeline(object):
    """
    Macrobot pipeline main class for pathogen segmentation.

    This class defines the base pipeline structure for preprocessing images, extracting features,
    and predicting pathogens on microtiter plates. Derived classes should override specific methods
    to handle different pathogens.

    Attributes:
        image_list (list): A list of image file names for the plate (red, blue, green, backlight, UVS).
        path (str): Path to the raw images from macrobot acquisition.
        destination_path (str): Path to store results (images, reports, etc.).
        store_leaf_path (str): Path to store segmented leaves.
        experiment (str): Experiment name.
        dai (str): Days after inoculation.
        file_results (file): CSV file for pathogen predictions.
        plate_id (str): Plate ID derived from the first image name.
        resize_scale (float): Scaling factor for resizing images.
        y_position (float): Y-coordinate for leaves segmentation.
        whitebalance (float): White balance factor for RGB correction.
        leaves_per_lane (float): Number of leaves per lane.
    """
    NAME = "invalid"

    def __init__(self, image_list, path_source, destination_path, store_leaf_path, experiment, dai, file_results,
                 setting_file):
        """
        Initialize the MacrobotPipeline with configuration and file details.

        :param image_list: List of image filenames for the plate.
        :param path_source: Path to the directory containing raw images.
        :param destination_path: Path for storing processed results.
        :param store_leaf_path: Path for storing segmented leaves.
        :param experiment: Experiment identifier.
        :param dai: Days after inoculation.
        :param file_results: Output CSV file for pathogen predictions.
        :param settings_file: Setting file for parameters.
        """
        # Load configuration settings
        config = ConfigParser()
        config.read(setting_file)
        self.setting_file = setting_file
        # Assign attributes from input parameters and configuration
        self.image_list = image_list
        self.path = path_source
        self.destination_path = destination_path
        self.store_leaf_path = store_leaf_path
        self.file_results = file_results
        self.experiment = experiment
        self.dai = dai
        self.resize_scale = config.getfloat('HARDWARE1', 'scaling_factor')
        self.numer_of_lanes = None
        self.image_tresholded = None
        self.plate_id = self.image_list[0].rsplit('_', 2)[0]
        self.y_position = config.getfloat('SEGMENTATION', 'y_position')
        self.whitebalance = config.getfloat('SEGMENTATION', 'whitebalance')
        self.leaves_per_lane = config.getfloat('SEGMENTATION', 'leaves_per_lane')

    def create_folder_structure(self):
        """
        Create the required folder structure for storing results and reports.

        This method ensures the destination and report folders are properly organized.
        """
        base_path = os.path.join(self.destination_path, self.experiment, self.dai, self.plate_id)
        report_path = os.path.join(base_path, 'report')

        # Create directories if they don't exist
        os.makedirs(base_path, exist_ok=True)
        os.makedirs(report_path, exist_ok=True)

        # Update destination and report paths
        self.destination_path = base_path
        self.report_path = report_path

    def preprocess_raw_images(self, image_list):
        """Placeholder for raw image preprocessing. Can be overridden for specific use cases."""
        return image_list

    def read_images(self):
        """
        Read and resize the input images based on the scaling factor.

        This method loads the red, blue, green, backlight, and UVS images from the source
        directory and resizes them to a uniform scale.
        """
        for image in self.image_list:

            # Read and resize the images based on their suffix
            if image.endswith('_backlight.tif'):
                self.image_backlight = cv2.resize(cv2.imread(os.path.join(self.path, image), cv2.IMREAD_UNCHANGED), (0, 0), fx=self.resize_scale, fy=self.resize_scale)
            elif image.endswith('_red.tif'):
                self.image_red = cv2.resize(cv2.imread(os.path.join(self.path, image), cv2.IMREAD_GRAYSCALE), (0, 0), fx=self.resize_scale, fy=self.resize_scale)
            elif image.endswith('_blue.tif'):
                self.image_blue = cv2.resize(cv2.imread(os.path.join(self.path, image), cv2.IMREAD_GRAYSCALE), (0, 0), fx=self.resize_scale, fy=self.resize_scale)
            elif image.endswith('_green.tif'):
                self.image_green = cv2.resize(cv2.imread(os.path.join(self.path, image), cv2.IMREAD_GRAYSCALE), (0, 0), fx=self.resize_scale, fy=self.resize_scale)
            elif image.endswith('uvs.tif') or image.endswith('uv.tif'):
                self.image_uvs = cv2.resize(cv2.imread(os.path.join(self.path, image), cv2.IMREAD_GRAYSCALE), (0, 0), fx=self.resize_scale, fy=self.resize_scale)

        # Ensure all images have the same dimensions
        assert self.image_backlight.shape == self.image_red.shape == self.image_blue.shape == self.image_green.shape == self.image_uvs.shape

    def merge_channels(self):
        """
        Combine the red, green, and blue grayscale images into a 3-channel RGB image.
        """
        self.image_rgb = np.dstack((self.image_blue, self.image_green, self.image_red))

    def do_whitebalance(self):
        """
        Apply white balance to the RGB image using a scaling factor from the configuration.
        """
        self.image_rgb = whitebalance(self.image_rgb, self.whitebalance)

    def get_lanes_rgb(self):
        """Placeholder to extract RGB lanes. Should be overridden for pathogen-specific processing."""
        pass

    def get_lanes_binary(self):
        """
        Generate binary masks for the segmented lanes.

        This method calls `segment_lanes_binary` to create binary representations
        of the detected lanes.
        """
        self.lanes_roi_binary = segmentation.segment_lanes_binary(self.lanes_roi_backlight, self.setting_file)

    def get_leaves_binary(self):
        """
        Segment individual leaves within the lanes.

        This method calls `segment_leaf_binary` to identify and segment individual
        leaves, saving results to the specified paths.
        """

        segmentation.segment_leaf_binary(
            self.lanes_roi_binary, self.lanes_roi_rgb, self.plate_id, self.leaves_per_lane,
            self.predicted_lanes, self.destination_path, self.y_position, self.experiment,
            self.dai, self.file_results, self.store_leaf_path, self.report_path, self.setting_file
        )

    def get_features(self):
        """Placeholder for feature extraction. Should be overridden for pathogen-specific processing."""
        pass

    def get_prediction_per_lane(self):
        """Placeholder for pathogen prediction. Should be overridden for pathogen-specific processing."""
        pass

    def save_images_for_report(self):
        """
        Save key images (e.g., RGB and thresholded) for report generation.
        """
        cv2.imwrite(os.path.join(self.report_path, 'rgb_image.png'), self.image_rgb)
        cv2.imwrite(os.path.join(self.report_path, 'threshold_image.png'), self.image_tresholded)

    def create_report(self):
        """
        Generate a summary report for the plate using the `orga` module.
        """
        orga.create_report(self.plate_id, self.report_path)

    def start_pipeline(self):
        """
        Start the Macrobot analysis pipeline.

        This method orchestrates the entire pipeline, including folder creation,
        image preprocessing, feature extraction, and pathogen prediction.
        """
        print(f'...Analyzing plate {self.plate_id}')

        # 1. Create folder structure
        self.create_folder_structure()

        # 2. Read and preprocess images
        # For la trobe hardware the images need to be preprocessed (rotate etc)
        # For IPK we just return the original image list
        self.image_list = self.preprocess_raw_images(self.image_list)
        self.read_images()
        self.merge_channels()
        self.do_whitebalance()

        # 3. Segment and analyze lanes
        self.get_lanes_rgb()
        self.get_lanes_binary()

        # 4. Extract features and predict pathogen presence
        self.get_features()
        self.get_prediction_per_lane(self.plate_id, self.destination_path)

        # 5. Segment leaves and save results
        self.get_leaves_binary()
        self.save_images_for_report()

        # 6. Generate a report
        self.create_report()

        # Return summary data
        final_image_list = [
            self.image_tresholded, self.image_backlight, self.image_red, self.image_blue,
            self.image_green, self.image_rgb, self.image_uvs, self.lanes_roi_rgb,
            self.lanes_roi_binary, self.lanes_feature, self.predicted_lanes
        ]

        return self.plate_id, self.numer_of_lanes, final_image_list, self.file_results.name