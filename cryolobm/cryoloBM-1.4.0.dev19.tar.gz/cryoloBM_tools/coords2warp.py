import os
import glob
import numpy as np
import pandas as pd
from pyStarDB import sp_pystardb as star
from cryoloBM.bmtool import BMTool
import argparse

from argparse import ArgumentParser

class Coords2WarpTool(BMTool):

    def get_command_name(self) -> str:
        return "coords2warp"

    def create_parser(self, parser) -> ArgumentParser:

        parser_coords2warp = parser.add_parser(
            self.get_command_name(),
            help="Converts coords file to Warp compatible star file.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        c2w_required_group = parser_coords2warp.add_argument_group(
            "Required arguments",
            "Converts .coords to a WARP compatible .star file.",
        )

        c2w_required_group.add_argument(
            "-i",
            "--input",
            required=True,
            help="Input folder or file. Files should be coords format. If the .coords provides a filament id, prior information are automatically added.",
        )

        c2w_required_group.add_argument(
            "-o",
            "--output",
            required=True,
            help="Output folder where to write the WARP compatible star file.",
        )

        c2w_required_group.add_argument(
            "--scale",
            type=float,
            default=1.0,
            help="Coordinates get scaled by this factor. This is useful incase you have .coords files from binned reconstructions.",
        )

        c2w_required_group.add_argument(
            "--apix",
            required=True,
            type=float,
            help="Pixel size in Angstrom after scaling. This value filled into the _rlnDetectorPixelSize column within the star file.",
        )

        c2w_required_group.add_argument(
            "--mag",
            type=float,
            default=10000,
            help="Magnification",
        )

        return parser_coords2warp

    def run(self, args):
        convert(
            input_path=args.input,
            output_path=args.output,
            scale=args.scale,
            pixelsize=args.apix,
            magnification=args.mag
        )

def calang(current_point,previous_point, xyz_indices = [0,1,2]):
    '''
    Calculate the the tilt and psi angle of a certain point based on its coords and the point before it.
    :param current_point:
    :param previous_point:
    :return: tilt and psi angle
    '''

    p_x = float(current_point[xyz_indices[0]])
    p_y = float(current_point[xyz_indices[1]])
    p_z = float(current_point[xyz_indices[2]])
    pminus_x = float(previous_point[xyz_indices[0]])
    pminus_y = float(previous_point[xyz_indices[1]])
    pminus_z = float(previous_point[xyz_indices[2]])

    vector = [p_x-pminus_x,p_y-pminus_y,p_z-pminus_z]
    psi = -np.arctan2(vector[1],vector[0])*180/np.pi
    xylength = np.sqrt(vector[0]**2+vector[1]**2)
    tilt = -np.arctan2(xylength,vector[2])*180/np.pi
    tilt = tilt+180

    return tilt, psi

def add_prior_information(rlndata):
    xindex, yindex, zindex, tilt_index, angle_index, id_index = [rlndata.columns.get_loc(c) for c in ['_rlnCoordinateX', '_rlnCoordinateY', '_rlnCoordinateZ', '_rlnAngleTiltPrior', '_rlnAnglePsiPrior', '_rlnHelicalTubeID']]
    npdata = rlndata.to_numpy()
    filids = np.unique(npdata[:,id_index])

    for filid in filids:
        filmask = npdata[:, id_index] == filid
        rlndata_fil = npdata[filmask]

        for row in range(rlndata_fil.shape[0]):
            if row == 0:
                tilt, psi = calang(rlndata_fil[1,:],rlndata_fil[row,:], xyz_indices=[xindex,yindex,zindex])
            elif row == (rlndata_fil.shape[0]-1):
                tilt, psi = calang(rlndata_fil[row,:],rlndata_fil[-2,:], xyz_indices=[xindex,yindex,zindex])
            else:
                tilt_1, psi_1 = calang(rlndata_fil[row,:],rlndata_fil[row-1,:], xyz_indices=[xindex,yindex,zindex])
                tilt_2, psi_2 = calang(rlndata_fil[row+1, :], rlndata_fil[row, :], xyz_indices=[xindex,yindex,zindex])
                tilt = np.mean([tilt_1,tilt_2])
                psi = np.mean([psi_1,psi_2])

            rlndata_fil[row, tilt_index] = tilt
            rlndata_fil[row, angle_index] = psi
        npdata[filmask] = rlndata_fil
    return npdata

def convert(
        input_path,
        output_path,
        pixelsize,
        magnification,
        scale):
    '''
    :param input_path: Input path with .coords files
    :param output_path: Path to folder where results should be written
    :param pixelsize: Pixel size in angstrom
    :param magnification: Magnification value
    :param scale: All coordaintes get scaled by this factor
    :return: None
    '''
    print("CONVERT!")
    os.makedirs(output_path, exist_ok=True)
    if os.path.isfile(input_path):
        files = [input_path]
    else:
        path = os.path.join(os.path.abspath(input_path), "*.coords")
        files = glob.glob(path)
    all_relion_data = []
    for pth in files:
        coords = np.atleast_2d(np.genfromtxt(pth))
        has_fid = coords.shape[1]==4
        micrographname = os.path.splitext(os.path.basename(pth))[0]
        if has_fid:
            micrographname = micrographname[:-4] # remove _fid
        micrographname = micrographname + ".tomostar"
        columns = ['_rlnMicrographName', '_rlnCoordinateX', '_rlnCoordinateY', '_rlnCoordinateZ', '_rlnMagnification','_rlnDetectorPixelSize']
        if has_fid:
            columns.append('_rlnHelicalTubeID')
            columns.append('_rlnAngleTiltPrior')
            columns.append('_rlnAnglePsiPrior')
            columns.append('_rlnAnglePsiFlipRatio')

        rlndata = np.zeros(shape=(coords.shape[0], len(columns)))

        for i, row in enumerate(coords):
            #rlndata[i, 0] = micrographname
            rlndata[i, 1] = float(row[0])*scale
            rlndata[i, 2] = float(row[1])*scale
            rlndata[i, 3] = float(row[2])*scale
            rlndata[i, 4] = magnification
            rlndata[i, 5] = pixelsize
            if has_fid:
                rlndata[i, 6] = row[3]



        df = pd.DataFrame(rlndata, columns=columns)

        if has_fid:
            # Calculate and add prio
            add_prior_information(df)

        df.iloc[:,0] = micrographname
        all_relion_data.append(df)
    df = pd.concat(all_relion_data)
    output_file_path = os.path.join(output_path, "particles_warp.star")
    sfile = star.StarFile(output_file_path)
    sfile.update('', df, True)
    sfile.write_star_file(overwrite=True)
