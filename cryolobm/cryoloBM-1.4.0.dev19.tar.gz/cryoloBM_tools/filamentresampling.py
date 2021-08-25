
from typing import List, Dict
from cryolo.utils import Filament, resample_filaments, BoundBox
from cryoloBM.bmtool import BMTool
from argparse import ArgumentParser
import argparse
import numpy as np
import os

class FilamentResampler():

    def __init__(
            self,
            box_distance: float,
    ):
        self.box_distance = box_distance

    def resampling(self, filaments : List[Filament]) -> List[Filament]:
        """

        :param filaments: List of filaments
        :param boxdistance: box distance
        :return: List of resampled filaments
        """
        return resample_filaments(filaments, self.box_distance)

class FilamentResampleTool(BMTool):

    def get_command_name(self) -> str:
        return "resample"

    def create_parser(self, parser) -> ArgumentParser:

        filament_parser = parser.add_parser(
            self.get_command_name(),
            help="Resamples 3D filaments coords (.coords format) to different box distance. "
                 "This tool is provisional and might disappear in future versions.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        req_group = filament_parser.add_argument_group(
            "Required arguments",
            "Resamples filaments coords to different box distance",
        )

        req_group.add_argument(
            "-i",
            "--input",
            required=True,
            help="Path to folder with .coords input files. Only those with FID can be used as input.",
        )
        req_group.add_argument(
            "-d",
            "--distance",
            required=True,
            type=float,
            help="New box distance.",
        )

        req_group.add_argument(
            "-o",
            "--output",
            required=True,
            help="Output folder where to write the resampled filaments. ",
        )

        return filament_parser

    def coords_to_filaments(self, data : np.array) -> List[Filament]:
        fils = []
        for id in np.unique(data[:,3]):
            boxes = []
            for row in data[data[:,3]==id]:
                x = row[0]
                y = row[1]
                z = row[2]
                boxes.append(BoundBox(x=x,y=y,z=z,h=0,w=0))
            f = Filament(boxes)
            f.meta["fid"] = id
            fils.append(f)
        return fils

    def filaments_to_coords(self, filaments : List[Filament]) -> np.array:

        Npos = np.sum([len(fil.boxes) for fil in filaments])

        coords_array = np.zeros(shape=(Npos,4))

        pos_counter = 0

        for fid, fil in enumerate(filaments):
            for box in fil.boxes:
                coords_array[pos_counter, 0] = box.x
                coords_array[pos_counter, 1] = box.y
                coords_array[pos_counter, 2] = box.z
                coords_array[pos_counter, 3] = fid + 1
                pos_counter = pos_counter + 1

        return coords_array



    def is_valid(self, data : np.array) -> bool:
        """
        Checks if it is valid .coords file
        :param data:
        :return:
        """
        return data.shape[1] == 4


    def get_data(self, files : List[str]) -> Dict[str, List[Filament]]:
        datasets = {}
        # Get data
        for file in files:
            data = np.genfromtxt(file)

            if self.is_valid(data) == False:
                continue

            filaments = self.coords_to_filaments(data)
            datasets[file] = filaments

        return datasets

    def write_data(self, dataset : Dict[str, List[Filament]], output_folder : str):

        out_fid = os.path.join(output_folder,"COORDS_FID")
        out_nofid = os.path.join(output_folder,"COORDS")
        os.makedirs(out_fid)
        os.makedirs(out_nofid)

        for file in dataset:
            filaments = dataset[file]
            coords = self.filaments_to_coords(filaments)

            filename = os.path.basename(file)
            outpath_fid = os.path.join(out_fid,filename)
            outpath_nofid = os.path.join(out_nofid, filename.replace("_fid",""))

            np.savetxt(outpath_fid, coords, fmt='%f')
            np.savetxt(outpath_nofid, coords[:,:3], fmt='%f')





    def do_resampling(self, data : Dict[str, List[Filament]], box_distance : float) -> Dict[str, List[Filament]]:

        resampeld_filaments = {}
        resampler = FilamentResampler(box_distance=box_distance)
        for file in data:
            filaments = data[file]
            filaments = resampler.resampling(filaments)
            resampeld_filaments[file] = filaments
        return resampeld_filaments

    def run(self, args):
        import os
        import glob
        input_dir = args.input
        path = os.path.join(os.path.abspath(input_dir), "*.coords")
        files = glob.glob(path)
        new_distance = args.distance
        outputpath = args.output

        print("Load data")
        datasets = self.get_data(files)

        print("Resample data")
        datasets_resampeld = self.do_resampling(data=datasets,box_distance=new_distance)

        print("Write data")
        self.write_data(datasets_resampeld,output_folder=outputpath)

        print("Done")






