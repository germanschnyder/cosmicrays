from numpy import percentile
from numpy.matlib import mean, std, asarray
from scipy.stats import skew
from collections import OrderedDict


def calculate(crs, normalized_img):
    """
    :param crs: cosmic rays list
    :param normalized_img: 2D image normalized by exposition time
    :return: a map with statistics about crs
    """

    # Calculate basic statistics on connected objects

    pixel_count = [cr.area for cr in crs]
    len_mean = mean(pixel_count)
    len_std = std(pixel_count)
    len_skew = skew(asarray(pixel_count))
    len_percentiles = percentile(pixel_count, [10, 25, 50, 75, 90])

    len_10_percentile = len_percentiles[0]
    len_25_percentile = len_percentiles[1]
    len_50_percentile = len_percentiles[2]
    len_75_percentile = len_percentiles[3]
    len_90_percentile = len_percentiles[4]

    # Calculate flux based on cr intensity
    flux_total = normalized_img.sum()
    flux_mean = flux_total / len(crs)

    # For each CR get its flux by summing up the pixels
    flux_crs = []

    for cr in crs:
        flux = 0
        for coord in cr.coords:
            flux += normalized_img[coord[0]][coord[1]]
            flux_crs.append(flux)

    flux_std = std(flux_crs)
    flux_skew = skew(asarray(flux_crs))
    flux_percentiles = percentile(flux_crs, [10, 25, 50, 75, 90])

    flux_10_percentile = flux_percentiles[0]
    flux_25_percentile = flux_percentiles[1]
    flux_50_percentile = flux_percentiles[2]
    flux_75_percentile = flux_percentiles[3]
    flux_90_percentile = flux_percentiles[4]

    res = OrderedDict()
    
    res["len_mean"] = len_mean
    res["len_std"] = len_std
    res["len_skew"] = len_skew
    res["len_10_percentile"] = len_10_percentile
    res["len_25_percentile"] = len_25_percentile
    res["len_50_percentile"] = len_50_percentile
    res["len_75_percentile"] = len_75_percentile
    res["len_90_percentile"] = len_90_percentile
    res["flux_total"] = flux_total
    res["flux_mean"] = flux_mean
    res["flux_std"] = flux_std
    res["flux_skew"] = flux_skew
    res["flux_10_percentile"] = flux_10_percentile
    res["flux_25_percentile"] = flux_25_percentile
    res["flux_50_percentile"] = flux_50_percentile
    res["flux_75_percentile"] = flux_75_percentile
    res["flux_90_percentile"] = flux_90_percentile
    
    return res
