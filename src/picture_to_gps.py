import cv2
import numpy as np
from gpx_converter import Converter

DEBUG=True

class GPXExtractor():
    """
     Extract GPS points from a route map picture with python/OpenCV

     -------> x (longitude)
     |
     |
     |
     v y (latitude)
    """
    def __init__(self, path):
        self.img = cv2.imread(path)
        self.x_dim = self.img.shape[1]
        self.y_dim = self.img.shape[0]
        self.init_coord_system()

    def init_coord_system(self):
        """
        Initialize coordinates system
        """
        self.top_left_coord = (47.16878, -1.535)
        self.bottom_righ_coord = (47.0471, -1.2264 )

        total_lat = self.bottom_righ_coord[0]-self.top_left_coord[0]
        total_lon = self.bottom_righ_coord[1]-self.top_left_coord[1]

        self.step_x = total_lon/self.x_dim
        self.step_y = total_lat/self.y_dim

    def pixel_to_gps_coord(self, local_coord):
        """
        Convert a pixel position (x,y) to gps coordinates (lon,lat)
        """
        print(local_coord)
        lat = self.top_left_coord[0] + self.step_y*local_coord[1]
        lon = self.top_left_coord[1] + self.step_x*local_coord[0]
        return (lat,lon)

    def pixels_to_gps_coord(self, local_coord_list):
        """
        Convert a list of pixel positions (x,y) to a list of gps coordinates (lon,lat)
        """
        gps_coords = []
        for local_coord in local_coord_list:
            gps_coords.append(self.pixel_to_gps_coord(local_coord))
        return gps_coords

    def compute_trace_mask(self):
        """
        Applies a threshold to an image based on a color
        """
        # WIP: parameter for visugps.png
        bgr_color = np.array([241,70,74])
        upper = bgr_color + 50
        lower = bgr_color - 50

        trace_mask = cv2.inRange(self.img, lower, upper)

        element = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
        trace_mask = cv2.erode(trace_mask, element, iterations = 1)
        return trace_mask

    def compute_trace_points(self, mask):
        """
        Return a list of points every 5 pixels (if possible) based on the given mask
        """
        # WIP: remove cmp

        #points_mask = np.zeros(mask.shape[::-1],np.uint8)
        points_list = []

        pixel_points = cv2.findNonZero(mask)
        first_non_zero_point = pixel_points[0][0]
        print("First point: " + str(first_non_zero_point[1]) + " "  + str(first_non_zero_point[0]))
        print(mask[first_non_zero_point[1], first_non_zero_point[0]])
        next_point = first_non_zero_point
        self.img = cv2.circle(self.img, (next_point[0], next_point[1]), 2, (0,255,0), 1)
        cmp = 0
        points_list.append([first_non_zero_point[0], first_non_zero_point[1]])

        circuit = False

        while not next_point is None and cmp<2000 and not circuit:
            new_next_point = self.get_next_point(mask, next_point, points_list)
            next_point = new_next_point
            #print("!!Point: " +  str(next_point))
            if next_point:
                #points_mask[next_point[0], next_point[1]] = 255
                self.img = cv2.circle(self.img, (next_point[0], next_point[1]), 1, (0,255,255), 1)
                points_list.append(next_point)
                cmp+=1
                #print(next_point)
                #print(points_list[0])
                #print(np.linalg.norm(np.asarray(next_point)-np.asarray(points_list[0])))
                if np.linalg.norm(np.asarray(next_point)-np.asarray(points_list[0]))<5:
                    circuit = True

        if circuit:
            print("Circuit finished")
        print("Number of point = " + str(cmp))

        return points_list


    def get_next_point(self, mask, cur_point, points_list):
        """
        Search the next pixel on the mask in a radius of 5 pixels 
        """

        # Center coordinates
        center_coordinates = (cur_point[0], cur_point[1])

        # Radius of circle
        radius = 5
        max_radius = 50

        # Line thickness of 2 px
        thickness = 2

        if len(points_list) > 3:
            to_test_points = points_list[-20:]
        else:
            to_test_points = points_list

        #print(to_test_points)

        while radius < max_radius:
            # Using cv2.circle() method
            # Draw a circle with blue line borders of thickness of 2 px
            img = np.zeros((2000,2000),np.uint8)
            cv2.circle(img, center_coordinates, radius, 255, thickness)
            points = np.transpose(np.where(img==255))

            for point in points:
                if mask[point[0], point[1]]!=0:
                    the_point = [point[1], point[0]]
                    #print("Cur point:" + str(the_point))

                    point_ok=True

                    for test_point in to_test_points:
                        #print("Test point:" + str(test_point))
                        #print(np.linalg.norm(np.asarray(the_point)-np.asarray(test_point)))
                        if np.linalg.norm(np.asarray(the_point)-np.asarray(test_point))<5:
                            #print("Prev point:" + str(prev_point))
                            #print("The point:" + str(the_point))
                            point_ok=False
                            break

                    if point_ok:
                        return the_point

            radius += 5
            print("Current radius = " + str(radius))
        return None

    def convert(self):
        """
        Extract GPS points from a route map picture with python/OpenCV and save it in a gpx file 
        """
        trace_mask = self.compute_trace_mask()
        pixel_points = self.compute_trace_points(trace_mask)
        if DEBUG:
            cv2.imshow("trace_mask", trace_mask)
            cv2.imshow("Points", self.img)

        gps_coords = self.pixels_to_gps_coord(pixel_points)
        np.savetxt("foo.csv",
            np.asarray(gps_coords),
            delimiter=",",
            header="latitude,longitude",
            comments='')
        Converter(input_file='foo.csv').csv_to_gpx(lats_colname='latitude',
                                                 longs_colname='longitude',
                                                 output_file='foo.gpx')
        if DEBUG:
            cv2.waitKey(0)

if __name__ == "__main__":
    gpx_extractor = GPXExtractor("example/visugpx.png")
    gpx_extractor.convert()
