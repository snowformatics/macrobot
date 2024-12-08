#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Image helper functions for performing white balance, extracting RGB features,
and obtaining the saturation channel from images.

This module provides utility functions to assist in image processing tasks such as
white balancing single or multi-channel images, extracting minimum or maximum intensity
projections from RGB images, and retrieving the saturation component from an image
in the HSV color space.
"""

import numpy as np
import cv2

def wb_helper(channel: np.ndarray, perc: float) -> np.ndarray:
    """
    Perform white balancing on a single image channel using percentile-based scaling.

    This function adjusts the intensity values of a single channel by clipping the
    lower and upper percentiles and scaling the remaining values to span the full
    0-255 range. This helps in normalizing the brightness and contrast of the channel.

    Parameters
    ----------
    channel : numpy.ndarray
        A 1-channel image represented as a NumPy array.
    perc : float
        The percentile value used for clipping. Typically a small percentage like 1 or 2.

    Returns
    -------
    numpy.ndarray
        The white-balanced channel as a 1-channel NumPy array with dtype `uint8`.

    Example
    -------
    >>> balanced_channel = wb_helper(channel, 1.0)
    """
    # Calculate the lower and upper percentile values
    mi = np.percentile(channel, perc)
    ma = np.percentile(channel, 100.0 - perc)

    # Clip the channel to the percentile range and scale to [0, 255]
    scaled_channel = (channel - mi) * 255.0 / (ma - mi)
    channel_balanced = np.clip(scaled_channel, 0, 255).astype(np.uint8)

    return channel_balanced


def whitebalance(image: np.ndarray, perc: float = 1.0) -> np.ndarray:
    """
    Perform white balancing on a 3-channel RGB image using percentile-based scaling.

    This function applies white balancing to each of the three color channels
    (Red, Green, Blue) individually. It is similar to the white balance method used
    in GIMP, aiming to correct color casts and normalize the overall color distribution.

    Parameters
    ----------
    image : numpy.ndarray
        A 3-channel RGB image represented as a NumPy array.
    perc : float, optional
        The percentile value used for clipping in each channel. Defaults to 1.0.

    Returns
    -------
    numpy.ndarray
        The white-balanced 3-channel RGB image as a NumPy array with dtype `uint8`.

    Example
    -------
    >>> balanced_image = whitebalance(image, perc=1.0)
    """
    # Split the image into its individual color channels
    image_split = np.dsplit(image, image.shape[-1])

    # Apply white balancing to each channel using the helper function
    balanced_channels = [wb_helper(channel, perc) for channel in image_split]

    # Merge the balanced channels back into a single image
    image_wb = np.dstack(balanced_channels)

    return image_wb


def rgb_features(image_array: np.ndarray, feature_type: str) -> np.ndarray:
    """
    Extract minimum or maximum intensity projection from a 3-channel RGB image.

    Depending on the specified `feature_type`, this function either retains the
    minimum or maximum intensity values across the RGB channels for each pixel,
    setting the other channels to zero. This highlights specific color features
    based on intensity projections.

    Parameters
    ----------
    image_array : numpy.ndarray
        A 3-channel RGB image represented as a NumPy array.
    feature_type : str
        The type of intensity projection to perform. Accepted values are
        "minimum" or "maximum".

    Returns
    -------
    numpy.ndarray
        The resulting 3-channel RGB image after applying the intensity projection.
        Pixels not matching the projection criteria are set to zero.

    Raises
    ------
    ValueError
        If `feature_type` is not "minimum" or "maximum".

    Example
    -------
    >>> min_projection = rgb_features(image_array, feature_type="minimum")
    >>> max_projection = rgb_features(image_array, feature_type="maximum")
    """
    # Split the image into individual R, G, B channels
    R, G, B = np.dsplit(image_array, image_array.shape[-1])

    # Debug: Print shape of individual channels
    # print(f"R shape: {R.shape}, G shape: {G.shape}, B shape: {B.shape}")

    if feature_type.lower() == "minimum":
        # Compute the minimum intensity across R, G, B channels for each pixel
        M = np.minimum(np.minimum(R, G), B)

        # Debug: Print a sample of minimum values
        # print(f"Sample minimum values: {M.ravel()[:5]}")

        # Zero out pixels in each channel that are greater than the minimum
        R[R > M] = 0
        G[G > M] = 0
        B[B > M] = 0

    elif feature_type.lower() == "maximum":
        # Compute the maximum intensity across R, G, B channels for each pixel
        M = np.maximum(np.maximum(R, G), B)

        # Debug: Print a sample of maximum values
        # print(f"Sample maximum values: {M.ravel()[:5]}")

        # Zero out pixels in each channel that are less than the maximum
        R[R < M] = 0
        G[G < M] = 0
        B[B < M] = 0
    else:
        raise ValueError("Unsupported feature_type! Choose 'minimum' or 'maximum'.")

    # Merge the processed channels back into a single RGB image
    feature_image = np.dstack((R, G, B))

    return feature_image


def get_saturation(image: np.ndarray) -> np.ndarray:
    """
    Extract the saturation channel from a 3-channel RGB image in the HSV color space.

    This function converts the input RGB image to HSV (Hue, Saturation, Value) color
    space and retrieves the saturation component, which represents the intensity of
    color information in the image.

    Parameters
    ----------
    image : numpy.ndarray
        A 3-channel RGB image represented as a NumPy array.

    Returns
    -------
    numpy.ndarray
        A 1-channel image representing the saturation component as a NumPy array.

    Example
    -------
    >>> saturation_channel = get_saturation(image)
    """
    # Convert the RGB image to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    # Debug: Check the conversion result
    # print(f"Hue channel sample: {hsv_image[:, :, 0].ravel()[:5]}")

    # Extract the saturation channel (index 1)
    sat = hsv_image[:, :, 1]

    return sat