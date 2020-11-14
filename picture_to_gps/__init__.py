from .picture_to_gps import *

path = "example/visugpx.png"
gpx_extractor = GPXExtractor(path)
gpx_extractor.convert()