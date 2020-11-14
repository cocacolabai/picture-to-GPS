"""
Extract GPS points from a route map picture with python/OpenCV
"""
from .picture_to_gps import *

gpx_extractor = GPXExtractor("example/visugpx.png")
gpx_extractor.convert()
