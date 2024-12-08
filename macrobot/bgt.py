import numpy as np
import cv2
import os
from macrobot.helpers import rgb_features
from macrobot import segmentation
from macrobot.mb_pipeline import MacrobotPipeline
from macrobot.prediction import predict_min_rgb



class BgtSegmenter(MacrobotPipeline):
    """
    Macrobot analysis pipeline for detecting the Blumeria graminis f. sp. tritici (Bgt) pathogen
    on microtiter plates.

    This class extends the `MacrobotPipeline` to provide specialized functionality for
    segmenting and analyzing Bgt pathogens in microtiter plate images. The pipeline includes
    preprocessing, lane segmentation, feature extraction using Minimum Intensity Projection (MinIP),
    and pathogen prediction based on RGB intensity features.
    """

    NAME = 'BGT'

    def get_frames(self, image_source: np.ndarray) -> np.ndarray:
        """
        Segment the white frame region on a microtiter plate using Otsu's thresholding.

        This method processes the provided UVS (Ultra Violet Saturated) image to identify the white frames
        surrounding the lanes by applying Otsu's thresholding and subsequent dilation. The resulting binary
        image highlights the white frame regions, which are then used to mask and extract lanes.

        Parameters
        ----------
        image_source : np.ndarray
            The UVS image (grayscale) used as the source for thresholding.

        Returns
        -------
        np.ndarray
            The binary image with the segmented white frame regions.

        Example
        -------
        >>> binary_frames = segmenter.get_frames(segmenter.image_uvs)
        """
        # Apply Otsu thresholding to segment the white frame
        _, image_tresholded = cv2.threshold(image_source, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Define a kernel for dilation to smooth and close gaps in the segmented frame
        kernel = np.ones((8, 8), np.uint8)
        image_tresholded = cv2.dilate(image_tresholded, kernel, iterations=3)

        return image_tresholded

    def get_lanes_rgb(self) -> None:
        """
        Extract the RGB lanes within the white frame region.

        This method performs the following steps:
        1. Generates a binary mask for the white frame using the UVS image.
        2. Utilizes the `segment_lanes_rgb` function from the segmentation module to detect and
           crop the lanes from RGB and backlight images based on the white frame mask.
        3. Stores the extracted lane regions and their positions for further analysis.

        Raises
        ------
        segmentation.SomeSegmentationError
            If lane segmentation fails due to unexpected image conditions.
        """
        # Generate a binary mask for the white frame using UVS image
        self.image_tresholded = self.get_frames(self.image_uvs)

        # Extract lanes using the mask and store lane data
        self.lanes_roi_rgb, self.lanes_roi_backlight, self.numer_of_lanes = segmentation.segment_lanes_rgb(
            self.image_rgb,
            self.image_backlight,
            self.image_tresholded,
            self.experiment,
            self.plate_id, self.setting_file
        )

    def get_features(self) -> list:
        """
        Extract features for Bgt detection using Minimum Intensity Projection (MinIP).

        This method computes the Minimum Intensity Projection for each detected RGB lane region.
        MinIP helps in identifying areas with lower intensity values, which are indicative of
        pathogen presence.

        Returns
        -------
        list of list
            A list where each sublist contains:
                - lane_position (int): The position of the lane.
                - min_rgb_feature (np.ndarray): The MinIP feature image extracted from the lane.

        Example
        -------
        >>> features = segmenter.get_features()
        """
        # Initialize a list to store features and positions
        self.lanes_feature = []

        # Loop through each detected lane and compute MinIP features
        for lane in self.lanes_roi_rgb:
            # Create a copy of the lane to avoid modifying the original data
            copy_lane = np.copy(lane[1])

            # Extract the minimum RGB features from the lane
            min_rgb_feature = rgb_features(copy_lane, "minimum")

            # Append lane position and extracted features to the list
            self.lanes_feature.append([lane[0], min_rgb_feature])

        return self.lanes_feature

    def get_prediction_per_lane(self, plate_id: str, destination_path: str) -> list:
        """
        Predict the presence of the Bgt pathogen in each lane using thresholding.

        This method performs pathogen prediction for each lane based on the extracted MinIP features
        and backlight images. The predictions are saved as binary images, and the results are
        stored for further analysis or reporting.

        Parameters
        ----------
        plate_id : str
            Identifier for the microtiter plate being processed.
        destination_path : str
            Directory path where the prediction result images will be saved.

        Returns
        -------
        list of list
            A list where each sublist contains:
                - lane_position (int): The position of the lane.
                - predicted_image (np.ndarray): The binary image prediction for the lane.
                  (255 = pathogen, 0 = background)

        Example
        -------
        >>> predictions = segmenter.get_prediction_per_lane("PlateA1", "/path/to/destination")
        """
        # Initialize a list to store predictions and positions
        self.predicted_lanes = []

        # Loop through each lane to generate predictions
        for i in range(len(self.lanes_feature)):
            # Predict pathogen presence using MinIP features and backlight information
            predicted_image = predict_min_rgb(
                self.lanes_feature[i][1],
                self.lanes_roi_backlight[i][1],
                self.lanes_roi_rgb[i][1]
            )

            # Save the predicted image with a descriptive filename
            cv2.imwrite(
                os.path.join(destination_path, f"{plate_id}_{self.lanes_feature[i][0]}_disease_predict.png"),
                predicted_image
            )

            # Append lane position and prediction result to the list
            self.predicted_lanes.append([self.lanes_feature[i][0], predicted_image])

        return self.predicted_lanes