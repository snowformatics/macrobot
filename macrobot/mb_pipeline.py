#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main class for the Macrobot pathogen segmentation pipelines.
Version 0.4
"""

__author__ = "Stefanie Lueck"
__copyright__ = "Stefanie Lueck"
__license__ = "NonCommercial-ShareAlike 2.0 Generic (CC BY-NC-SA 2.0) License"

import cv2
import numpy as np
import os

from macrobot.helpers import whitebalance
from macrobot import segmentation


class MacrobotPipeline(object):
    """Macrobot pipeline main class.

    :param image_list: A list of all images names per plate (green channel, blue channel, red channel, backlight image, UVS image.
    :type image_list: list
    :param path: The path which contains the raw images coming from the macrobot image acquisition.
    :type path: str
    :param destination_path: The path to store the final result images and csv file.
    :type destination_path: str
    :param file_results: The CSV file for each experiments which contains the pathogen prediction per leaf.
    :type file_results: file object
    :param experiment: The experiment name.
    :type experiment: str
    :param dai: Days after inoculation.
    :type dai: str
    :param resize_scale: Scale for resizing the images.
    :type resize_scale: float
    :param plate_id: Plate ID without the barcode.
    :type plate_id: str
    :param report_data: A list containing all important data to generate a report.
    :type report_data: list
    :param y_position: Y Position for the leaves.
    :type y_position: int
    """
    NAME = "invalid"

    def __init__(self, image_list, path_source, destination_path, experiment, dai, file_results):
        self.image_list = image_list
        self.path = path_source
        self.destination_path = destination_path
        self.file_results = file_results
        self.experiment = experiment
        self.dai = dai
        self.resize_scale = 0.5
        self.report_data = []
        self.numer_of_lanes = None
        # self.image_backlight = None
        # self.image_red = None
        # self.image_blue = None
        # self.image_green = None
        # self.image_rgb = None
        # self.image_uvs = None
        # self.lanes_roi_rgb = None
        # self.lanes_roi_backlight = None
        # self.lanes_roi_binary = None
        # self.lanes_roi_minrgb = None
        # self.predicted_lanes = None
        # self.lanes_sat = None
        self.plate_id = self.image_list[0].rsplit('_', 2)[0]
        self.y_position = 800   # Position for leaves
        print('...Analyzing plate ' + self.plate_id)

    def create_folder_structure(self):
        """Create all necessary folders."""

        try:
            os.makedirs(self.destination_path + self.experiment + '/' + self.dai + '/' + self.plate_id + '/')
            os.makedirs(self.destination_path + '/report/')
        except FileExistsError:
            pass
        # Overwrite destination path.
        self.destination_path = self.destination_path + self.experiment + '/' + self.dai + '/' + self.plate_id + '/'
        self.report_path = self.destination_path + '/report/'


    def read_images(self):
        """Reading and resizing the images."""
        for image in self.image_list:
            if image.endswith('_backlight.tif'):
                self.image_backlight = cv2.resize(cv2.imread(self.path + image, cv2.IMREAD_UNCHANGED), (0, 0), fx=self.resize_scale, fy=self.resize_scale)
            elif image.endswith('_red.tif'):
                self.image_red = cv2.resize(cv2.imread(self.path + image, cv2.IMREAD_GRAYSCALE), (0, 0), fx=self.resize_scale, fy=self.resize_scale)
            elif image.endswith('_blue.tif'):
                self.image_blue = cv2.resize(cv2.imread(self.path + image, cv2.IMREAD_GRAYSCALE), (0, 0), fx=self.resize_scale, fy=self.resize_scale)
            elif image.endswith('_green.tif'):
                self.image_green = cv2.resize(cv2.imread(self.path + image, cv2.IMREAD_GRAYSCALE), (0, 0), fx=self.resize_scale, fy=self.resize_scale)
            elif image.endswith('uvs.tif') or image.endswith('uv.tif'):
                self.image_uvs = cv2.resize(cv2.imread(self.path + image, cv2.IMREAD_GRAYSCALE), (0, 0), fx=self.resize_scale, fy=self.resize_scale)
        assert self.image_backlight.shape == self.image_red.shape == self.image_blue.shape == self.image_green.shape == self.image_uvs.shape

    def merge_channels(self):
        """Merging blue, red and green image to create a true 3-channel RGB image."""
        self.image_rgb = np.dstack((self.image_blue, self.image_green, self.image_red))


    def do_whitebalance(self):
        """Calling white balance function in helpers module."""
        self.image_rgb = whitebalance(self.image_rgb)
        cv2.imwrite('RGB_image.png', self.image_rgb)

    def get_lanes_rgb(self):
        """Extracts the lanes of the RGB image. Different for each pathogen. Should be overwritten."""
        pass

    def get_lanes_binary(self):
        """Create a binary image from the lanes."""
        self.lanes_roi_binary = segmentation.segment_lanes_binary(self.lanes_roi_backlight)

    def get_leaves_binary(self):
        """Segment the single leaves."""
        segmentation.segment_leaf_binary(self.lanes_roi_binary, self.lanes_roi_rgb, self.plate_id, 8, self.predicted_lanes,
                                         self.destination_path, self.y_position, self.experiment, self.dai, self.file_results)

    def get_features(self):
        """Features extraction. Different for each pathogen should be overridden"""
        pass

    def get_prediction_per_lane(self):
        """Predict pathogen. Different for each pathogen should be overridden"""
        pass

    def create_report(self):
        import jinja2
        import os
        path = os.path.join(os.path.dirname(__file__), '.')
        templateLoader = jinja2.FileSystemLoader(searchpath=path)
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = "report.html"
        #hello = "hello..... "
        hello =  str(self.numer_of_lanes)
        template = templateEnv.get_template(TEMPLATE_FILE)
        outputText = template.render(value=hello)  # this is where to put args to the template renderer
        print(outputText)
        # to save the results
        print (self.report_path)
        print (self.plate_id )
        with open(self.report_path + self.plate_id + ".html", "w") as fh:
            fh.write(outputText)



    # def get_prediction_per_leaf(self):
    #     pass
    #
    # def results_per_leaf(self):
    #     pass
    #
    # def results_per_lane(self):
    #     pass
    #
    # def write_image(self):
    #     pass

    # def process(self):
    #     # override in derived classes to perform an actual segmentation
    #     pass

    def start_pipeline(self):
        """Starts the Macrobot analysis pipeline."""

        # 1. Create necessary folder structure
        self.create_folder_structure()
        # 2. Read images
        self.read_images()
        # 3. Create true RGB image.
        self.merge_channels()
        # 4. Whitebalance RGB image
        self.do_whitebalance()
        # 5. Segment the 4 lanes.
        self.get_lanes_rgb()
        # # 6. Binary lanes
        # self.get_lanes_binary()
        # # 7. Feature extraction for pathogen.
        # self.get_features()
        # # 8. Predict pathogen.
        # self.get_prediction_per_lane(self.plate_id, self.destination_path)
        # # 9. Segment leaves.
        # self.get_leaves_binary()

        self.create_report()

        #self.process()