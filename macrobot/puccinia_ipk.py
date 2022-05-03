import numpy as np
import cv2
import os
from skimage.filters import threshold_triangle
from skimage import img_as_uint

from macrobot.helpers import get_saturation
from macrobot import segmentation
from macrobot.mb_pipeline import MacrobotPipeline
from macrobot.prediction import predict_saturation


class RustSegmenterIPK(MacrobotPipeline):
    """Macrobot analysis for Puccinia plant pathogen.
       Currently works for leaf and stripe rust.
    """

    NAME = 'RUST_IPK'

# IPK Hardware
    def get_frames(self, image_source):
        """Segment the white frame on a microtiter plate.
           Algorithm is based on Otsu thresholding of the UVS image.

           :param image_source: The UVS-image (x, y, 1) which is used as source for thresholding.
           :type image_source: numpy array.
           :return: The binary image after Otsu thresholding.
           :rtype: numpy array
        """
        _, image_tresholded = cv2.threshold(image_source, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = np.ones((8, 8), np.uint8)
        image_tresholded = cv2.dilate(image_tresholded, kernel, iterations=3)
        # cv2.imshow('', image_tresholded)
        # cv2.waitKey()
        return image_tresholded

    def get_lanes_rgb(self):
        """Calls segment_lanes_rgb to extract the RGB lanes within the white frames."""
        self.image_tresholded = self.get_frames(self.image_uvs)
        self.lanes_roi_rgb, self.lanes_roi_backlight, self.numer_of_lanes = segmentation.segment_lanes_rgb(self.image_rgb,
                                                                                      self.image_backlight,
                                                                                      self.image_tresholded
                                                                                      )

    def get_features(self):
        """Feature extraction for Rust based on thresholding the saturation channel.

           :return: A list with the features per lane and it's position sorted left to right.
           :rtype: list with tuple(feature, position)
        """
        # We store the saturated images and the position for further analysis
        self.lanes_feature = []
        # For each RGB lane we extract the features
        for lane in self.lanes_roi_rgb:
            copy_lane = np.copy(lane[1])
            saturation_feature = get_saturation(copy_lane)
            self.lanes_feature.append([lane[0], saturation_feature])
        return self.lanes_feature

    def get_prediction_per_lane(self, plate_id, destination_path):
        """Predict the Rust pathogen from the feature extraction method based on thresholding. 255 = pathogen, 0 = background

           :return: A list with the predictions per lane and it's position sorted left to right.
           :rtype: list with tuple(prediction, position)
        """
        self.predicted_lanes = []
        for lane_id in range(len(self.lanes_feature)):
            predicted_image = predict_saturation(self.lanes_feature[lane_id][1], self.lanes_roi_backlight[lane_id][1])
            cv2.imwrite(os.path.join(destination_path, plate_id + '_' + str(self.lanes_feature[lane_id][0]) + '_disease_predict.png'), predicted_image)
            self.predicted_lanes.append([self.lanes_feature[lane_id][0], predicted_image])
        return self.predicted_lanes