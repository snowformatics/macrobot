import numpy as np
import cv2
import os
from macrobot import segmentation
from macrobot.mb_pipeline import MacrobotPipeline
from macrobot.prediction import predict_green_image
from macrobot.helpers import whitebalance

class NetBlotchSegmenter(MacrobotPipeline):
    """
    Macrobot analysis pipeline for Net Blotch pathogen segmentation.

    This class extends the `MacrobotPipeline` to provide specialized
    functionality for segmenting and analyzing Net Blotch pathogens
    in microtiter plate images. The pipeline includes preprocessing,
    white balancing, lane segmentation, feature extraction, and
    pathogen prediction.

    Attributes
    ----------
    image_rgb : np.ndarray
        The RGB image being processed.
    image_backlight : np.ndarray
        The backlight image corresponding to the RGB image.
    image_red : np.ndarray
        The red channel image.
    image_blue : np.ndarray
        The blue channel image.
    image_green : np.ndarray
        The green channel image.
    image_uvs : np.ndarray
        The UVS image used for frame segmentation.
    lanes_roi_rgb : list
        List of tuples containing lane position and RGB ROI.
    lanes_roi_backlight : list
        List of tuples containing lane position and backlight ROI.
    lanes_roi_binary : list
        List of tuples containing lane position and binary lane images.
    lanes_feature : list
        List of features extracted from each lane.
    predicted_lanes : list
        List of predictions for each lane.
    numer_of_lanes : int
        Total number of lanes extracted.
    """

    NAME = 'NetBlotch'

    def preprocess_raw_images(self, image_lst: list) -> list:
        """
        Preprocess raw images by rotating and cropping.

        This method processes each image in the provided list by:
        1. Loading the image if it hasn't been processed yet.
        2. Rotating the image 90 degrees clockwise.
        3. Cropping 400 pixels from the top and bottom to remove unwanted regions.
        4. Saving the processed image with a 'processed_' prefix.

        Parameters
        ----------
        image_lst : list
            List of image filenames to preprocess.

        Returns
        -------
        list
            Updated list of processed image filenames ending with '.tif'.

        Example
        -------
        >>> processed_images = segmenter.preprocess_raw_images(['image1.tif', 'image2_bg.tif'])
        """
        print ('ok4', image_lst)
        for image_name in image_lst:
            if not image_name.startswith("processed_"):
                # Load the original image
                image_path = os.path.join(self.path, image_name)
                image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
                if image is None:
                    print(f"Warning: Unable to load image {image_path}. Skipping.")
                    continue

                # Rotate the image 90 degrees clockwise
                rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
                height, width = rotated_image.shape[:2]

                # Crop 400 pixels from the top and bottom
                cropped_image = rotated_image[400:height - 400, :]

                # Modify image name for backlight images
                if "_bg.tif" in image_name:
                    image_name = image_name.replace("_bg.tif", "_backlight.tif")

                # Save the processed image with 'processed_' prefix
                processed_image_name = f'processed_{image_name}'
                processed_image_path = os.path.join(self.path, processed_image_name)
                cv2.imwrite(processed_image_path, cropped_image)

        # Retrieve all processed images with '.tif' extension
        processed_images = [f for f in os.listdir(self.path) if f.endswith('.tif')]

        return processed_images

    def do_whitebalance(self) -> None:
        """
        Apply white balance to the RGB image.

        This method utilizes the `whitebalance` function from the helpers module
        to perform white balancing on the RGB image with a specified percentile.
        """
        self.image_rgb = whitebalance(self.image_rgb, perc=0.2)

    def read_images(self) -> None:
        """
        Override the base class read function to preprocess and load images.

        This method reads and resizes the processed images specific to La Trobe
        Macrobot plates. It handles different image types based on their filenames:
        - Backlight images
        - Red, Blue, Green channel images
        - UVS images

        Raises
        ------
        AssertionError
            If the shapes of all loaded images do not match.
        """

        for image in self.image_list:
            if image.startswith("processed_"):
                image_path = os.path.join(self.path, image)
                #print (image_path)
                if image.endswith(('_backlight.tif', '_bg.tiff', '_backlight.tiff')):
                    # Load and resize backlight image
                    self.image_backlight = cv2.resize(
                        cv2.imread(image_path, cv2.IMREAD_UNCHANGED),
                        (0, 0),
                        fx=self.resize_scale,
                        fy=self.resize_scale
                    )
                elif image.endswith(('_red.tif', '_red.tiff')):
                    # Load and resize red channel image in grayscale
                    self.image_red = cv2.resize(
                        cv2.imread(image_path, cv2.IMREAD_GRAYSCALE),
                        (0, 0),
                        fx=self.resize_scale,
                        fy=self.resize_scale
                    )
                elif image.endswith(('_blue.tif','_blue.tiff')):
                    # Load and resize blue channel image in grayscale
                    self.image_blue = cv2.resize(
                        cv2.imread(image_path, cv2.IMREAD_GRAYSCALE),
                        (0, 0),
                        fx=self.resize_scale,
                        fy=self.resize_scale
                    )
                elif image.endswith(('_green.tif', '_green.tiff')):
                    # Load and resize green channel image in grayscale
                    self.image_green = cv2.resize(
                        cv2.imread(image_path, cv2.IMREAD_GRAYSCALE),
                        (0, 0),
                        fx=self.resize_scale,
                        fy=self.resize_scale
                    )
                elif image.endswith(('uvs.tif', 'uv.tif', 'uvs.tiff')):
                    # Load and resize UVS image in grayscale
                    self.image_uvs = cv2.resize(
                        cv2.imread(image_path, cv2.IMREAD_GRAYSCALE),
                        (0, 0),
                        fx=self.resize_scale,
                        fy=self.resize_scale
                    )

        # Ensure all loaded images have the same dimensions
        assert self.image_backlight.shape == self.image_red.shape == self.image_blue.shape == \
               self.image_green.shape == self.image_uvs.shape, \
            "Mismatch in image dimensions among backlight, red, blue, green, and UVS images."


    def get_frames(self, image_source: np.ndarray) -> np.ndarray:
        """
        Segment the white frame on a microtiter plate using Otsu's thresholding.

        This method processes the provided UVS image to identify the white frames
        surrounding the lanes by applying Otsu's thresholding and dilation.

        Parameters
        ----------
        image_source : np.ndarray
            The UVS image (grayscale) used as the source for thresholding.

        Returns
        -------
        np.ndarray
            The binary image after applying Otsu's thresholding and dilation.

        Example
        -------
        >>> binary_frames = segmenter.get_frames(segmenter.image_uvs)
        """

        # Apply Otsu's thresholding to invert the image (white frames become white)
        _, image_tresholded = cv2.threshold(image_source, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        # Define a kernel for dilation to strengthen frame boundaries
        kernel = np.ones((8,8), np.uint8)
        image_tresholded = cv2.dilate(image_tresholded, kernel, iterations=3)

        return image_tresholded

    def get_leaves_binary(self) -> None:
        """
        Segment individual leaves from binary lane images.

        This method delegates the leaf segmentation process to the
        `segment_leaf_binary` function within the `segmentation` module. It
        processes the binary lane images to identify and segment individual leaves
        for further analysis and prediction.
        """

        segmentation.segment_leaf_binary(self.lanes_roi_binary, self.lanes_roi_rgb, self.plate_id, self.predicted_lanes,
                                         self.destination_path, self.experiment, self.dai, self.file_results,
                                         self.store_leaf_path, self.setting_file)

    def get_lanes_rgb(self) -> None:
        """
        Extract RGB lanes within the white frames.

        This method performs the following steps:
        1. Segments the white frames using the blue image.
        2. Extracts RGB and backlight lane ROIs within the identified frames.
        3. Sorts the lanes from left to right based on their x-coordinate positions.
        """
        # Segment white frames from the blue image
        self.image_tresholded = self.get_frames(self.image_blue)
        # Extract RGB and backlight lanes within the white frames
        self.lanes_roi_rgb, self.lanes_roi_backlight, self.numer_of_lanes = segmentation.segment_lanes_rgb(self.image_rgb,
                                                                                      self.image_backlight,
                                                                                      self.image_tresholded,
                                                                                    self.experiment,
                                                                                    self.plate_id, self.setting_file)


    def get_features(self) -> list:
        """
        Extract features for each lane based on the green channel.

        This method extracts the green channel from each RGB lane ROI and stores
        it as a feature for further pathogen prediction.

        Returns
        -------
        list
            A list of lists, each containing the lane position and its corresponding
            green channel feature.

        Example
        -------
        >>> features = segmenter.get_features()
        """

        # We store the Max RGB images and the position for further analysis
        self.lanes_feature = []
        # Iterate over each RGB lane ROI to extract green channel features
        for lane in self.lanes_roi_rgb:
            # Make a copy to avoid modifying the original lane image
            copy_lane = np.copy(lane[1])
            # Split the RGB channels
            B, G, R = cv2.split(copy_lane)
            # Store the green channel and its position
            self.lanes_feature.append([lane[0], G])

        return self.lanes_feature

    def get_prediction_per_lane(self, plate_id: str, destination_path: str) -> list:
        """
        Predict the presence of Net Blotch pathogen in each lane.

        This method performs pathogen prediction for each lane based on the
        extracted green channel features and backlight images. It saves the
        prediction images and records the predictions for further analysis.

        Parameters
        ----------
        plate_id : str
            The identifier for the specific plate being processed.
        destination_path : str
            The directory path where the prediction result images will be stored.

        Returns
        -------
        list
            A list of lists, each containing the lane position and its corresponding
            predicted binary image.

        Example
        -------
        >>> predictions = segmenter.get_prediction_per_lane("PlateA1", "/path/to/destination")
        """

        self.predicted_lanes = []
        # Iterate over each lane feature to perform prediction
        for i in range(len(self.lanes_feature)):
            # Perform pathogen prediction using the green channel and backlight image
            predicted_image = predict_green_image(self.lanes_feature[i][1], self.lanes_roi_backlight[i][1],
                                              self.lanes_roi_rgb[i][1])
            cv2.imwrite(os.path.join(destination_path, plate_id + '_' + str(self.lanes_feature[i][0]) + '_disease_predict.png'), predicted_image)

            # Store the prediction and its lane position
            self.predicted_lanes.append([self.lanes_feature[i][0], predicted_image])
        return self.predicted_lanes
