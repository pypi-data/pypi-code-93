import numpy as np
from pyStarDB import sp_pystardb as star
import os
import glob
from cryoloBM.bmtool import BMTool
from argparse import ArgumentParser
import argparse

class Priors2StarTool(BMTool):

    def get_command_name(self) -> str:
        return "priors2star"

    def create_parser(self, parentparser : ArgumentParser) -> ArgumentParser:

        parser_priors2star = parentparser.add_parser(
            self.get_command_name(),
            help="Add filament prior information to star file.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        priors2star_required_group = parser_priors2star.add_argument_group(
            "Required arguments",
            "Add filament prior information to star",
        )

        priors2star_required_group.add_argument(
            "-i",
            "--input",
            required=True,
            help="Path to particles.star file.",
        )
        priors2star_required_group.add_argument(
            "-fi",
            "--fidinput",
            required=True,
            help="Input folder or file with *_fid.coords files from crYOLO .",
        )

        priors2star_required_group.add_argument(
            "-o",
            "--output",
            required=True,
            help="Output folder where to write the augmented star files..",
        )

        return parser_priors2star

    def run(self, args):


        if os.path.isfile(args.input):
            star_file = args.input
        else:
            raise ValueError("Can't find input star file.")

        if os.path.isfile(args.fidinput):
            fid_files = [args.fidinput]
        else:
            path = os.path.join(os.path.abspath(args.fidinput), "*_fid.coords")
            fid_files = glob.glob(path)

        # Find star fid paris
        outname = os.path.splitext(os.path.basename(star_file))[0] + "_with_prior.star"
        add_prior_to_star(
            in_star=star_file,
            coords_fid_paths=fid_files,
            output_star=os.path.join(args.output, outname),
        )

def match(tomofiles,fid_files):
    '''
    This functions gives the indices
    :param star_files:
    :param fid_files:
    :return: One list for every fid_file containing the relevant indices in tomofiles
    '''

    fid_index_list = []
    fid_file_basenames = [os.path.basename(file) for file in fid_files]

    for fid_file in fid_file_basenames:
        indicies = [row_index for row_index, tomopth in enumerate(tomofiles) if os.path.splitext(os.path.basename(tomopth))[0] in fid_file]
        fid_index_list.append(indicies)
    return fid_index_list


def add_prior_to_star(in_star, coords_fid_paths, output_star):
    '''

    :param in_star:
    :param coords_fid_path:
    :param ouput_star:
    :return:
    '''
    import copy
    from cryoloBM_tools import coords2warp

    os.makedirs(os.path.dirname(output_star), exist_ok=True)
    sfile = star.StarFile(in_star)
    relion_dataframe = sfile['']

    tomo_names = relion_dataframe['_rlnMicrographName']
    fid_index_lists = match(tomofiles=tomo_names,fid_files=coords_fid_paths)
    relion_dataframe_with_priors = copy.deepcopy(relion_dataframe)
    tubeindex = relion_dataframe_with_priors.columns.get_loc('_rlnHelicalTubeID')
    tiltindex = relion_dataframe_with_priors.columns.get_loc('_rlnAngleTiltPrior')
    psiindex = relion_dataframe_with_priors.columns.get_loc('_rlnAnglePsiPrior')
    flipindex = relion_dataframe_with_priors.columns.get_loc('_rlnAnglePsiFlipRatio')

    for i, fid_file in enumerate(coords_fid_paths):
        coords = np.atleast_2d(np.genfromtxt(fid_file))
        fid_indices = fid_index_lists[i]


        relion_dataframe_with_priors.iloc[fid_indices, tubeindex] = coords[:,3]
        relion_dataframe_with_priors.iloc[fid_indices,tiltindex] = 0
        relion_dataframe_with_priors.iloc[fid_indices,psiindex] = 0
        relion_dataframe_with_priors.iloc[fid_indices,flipindex] = 0
        npdata = coords2warp.add_prior_information(relion_dataframe_with_priors.iloc[fid_indices,:])
        relion_dataframe_with_priors.iloc[fid_indices, :] = npdata



    sfile.update('',relion_dataframe_with_priors, True)
    sfile.write_star_file(output_star)