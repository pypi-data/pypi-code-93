import numpy as np
from cygnsslib import create_kml_from_list_points

lyr_name = "Yanco"
point_names = ["Y1", "Y2", "Y3", "Y4", "Y5", "Y6", "Y7", "Y8", "Y9", "Y10", "Y11", "Y12", "Y13"]
loc_list = np.array([[-34.62888, 145.84895], [-34.65478, 146.11028], [-34.621, 146.424], [-34.71943, 146.02003], [-34.72835, 146.29317], [-34.84262, 145.86692],
                     [-34.85183, 146.1153], [-34.84697, 146.41398], [-34.96777, 146.01632], [-35.00535, 146.30988], [-35.10975, 145.93553], [-35.0696, 146.16893],
                     [-35.09025, 146.30648]])
cnt_point = np.average(loc_list, axis=0)

out_kml = "Yanco_site.kml"
create_kml_from_list_points(loc_list, loc_names=point_names, out_kml=out_kml, lyr_name=lyr_name)
print("Center point: lat: {:f}, long: {:f}".format(cnt_point[0], cnt_point[1]))
