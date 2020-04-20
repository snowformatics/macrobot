import numpy as np
import cv2
from skimage.filters import threshold_triangle
from skimage import img_as_uint

# from src.macrobot.helpers import get_saturation
# from src.macrobot import segmentation
# from src.macrobot.mb_pipeline import MacrobotPipeline
# from src.macrobot.prediction import predict_saturation

from macrobot.helpers import get_saturation
from macrobot import segmentation
from macrobot.mb_pipeline import MacrobotPipeline
from macrobot.prediction import predict_saturation


class RustSegmenter(MacrobotPipeline):
    """Macrobot analysis for Puccinia plant pathogen.
       Currently works for leaf and stripe rust.
    """

    NAME = 'RUST'

    def get_frames(self, image_source):
        """Segment the white frame on a microtiter plate.
           Algorithm is based on Triangle thresholding of the green channel image.

           :param image_source: The green channel image (x, y, 1) which is used as source for thresholding.
           :type image_source: numpy array.
           :return: The binary image after thresholding.
           :rtype: numpy array
        """

        thresholded_lane = threshold_triangle(image_source)
        thresholded_lane = image_source < thresholded_lane
        image_tresholded = img_as_uint(thresholded_lane)
        image_tresholded = image_tresholded.astype(np.uint8)
        # Add some dilation transformations to separate connected frames
        kernel = np.ones((5, 5), np.uint8)
        image_tresholded = cv2.dilate(image_tresholded, kernel, iterations=5)
        return image_tresholded

    def get_lanes_rgb(self):
        """Calls segment_lanes_rgb to extract the RGB lanes within the white frames."""
        image_tresholded = self.get_frames(self.image_green)
        # We overwrite the y position for yellow rust because leaves are a bit lower on plates for bgt
        self.y_position = 850
        self.lanes_roi_rgb, self.lanes_roi_backlight = segmentation.segment_lanes_rgb(self.image_rgb,
                                                                                      self.image_backlight,
                                                                                      image_tresholded)
    def get_features(self):
        """Feature extraction for Rust based on thresholding the saturation channel.

           :return: A list with the features per lane and it's position sorted left to right.
           :rtype: list with tuple(feature, position)
        """
        # We store the saturated images and the position for further analysis
        self.lanes_sat = []
        # For each RGB lane we extract the features
        for lane in self.lanes_roi_rgb:
            copy_lane = np.copy(lane[1])
            saturation_feature = get_saturation(copy_lane)
            self.lanes_sat.append([lane[0], saturation_feature])
        return self.lanes_sat

    def get_prediction_per_lane(self, plate_id, destination_path):
        """Predict the Rust pathogen from the feature extraction method based on thresholding. 255 = pathogen, 0 = background

           :return: A list with the predictions per lane and it's position sorted left to right.
           :rtype: list with tuple(prediction, position)
        """
        self.predicted_lanes = []
        for lane_id in range(len(self.lanes_sat)):
            predicted_image = predict_saturation(self.lanes_sat[lane_id][1], self.lanes_roi_backlight[lane_id][1])
            cv2.imwrite(destination_path + plate_id + '_' + str(self.lanes_sat[lane_id][0]) + '_disease_predict.png', predicted_image)
            self.predicted_lanes.append([self.lanes_sat[lane_id][0], predicted_image])
        return self.predicted_lanes