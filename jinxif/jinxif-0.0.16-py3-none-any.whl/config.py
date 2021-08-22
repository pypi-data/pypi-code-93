####
# title: config.py
#
# language: Python3.8
# date: 2021-04-23
# license: GPL>=v3
# author: Jenny, bue
#
# description:
#   jinxif file name nomenclature, lab, or workplace dependent constants and fuctions are kept here
#####

# library
import os
import stat

# (CHANGE ME)

# const

# standard marker spelling
# fundamental marke nameing convention rules:
# 1. marker names can not contain underscores, never!
es_marker_standard = {
    '53BP1',
    'AR','Arg1','aSMA',
    'BAX','BCL2','BMP2','BMP4','BMP6',
    'CAV1','CC3','CC3-488','CC3-647','CCND1',
    'CD3','CD4','CD8','CD11b','CD11c','CD20','CD31','CD44','CD45','CD68','CD74','CD90','CD103',
    'CGA',
    'CK5','CK7','CK8','CK14','CK17','CK18','CK19',
    'ColI','ColIV','ColVI','CoxIV',
    'cPARP',
    'CSF1R',
    'DAPI0','DAPI1','DAPI2','DAPI3','DAPI4','DAPI5','DAPI5Q','DAPI6','DAPI6Q','DAPI7','DAPI7Q','DAPI8','DAPI9','DAPI10','DAPI11','DAPI12',
    'Ecad','EGFR','EpCAM','ER',
    'F4-80','FN1','FoxP3',
    'Gal3','GATA3','GATA6','gH2AX','Glut1','GRNZB',
    'H3K4','H3K27','HER2','HIF1a',
    'Ki67',
    'LamAC','LamB1','LamB2','LYVE1',
    'MHCII','MSH2','MSH6','MUC1',
    'NFkB',
    'PCNA','PD1','PDGFRa','PDL1','PDL1ab','PDL1d','PDPN','PgR','PgRc4',
    'p63','pAKT','pERK','pHH3','pMYC','pRB','pS62MYC','pS6RP','panCK',
    'R00c2','R00c3','R00c4', 'R00c5',
    'R0c2','R0c3','R0c4','R0c5',
    'R1c2','R1c3', 'R1c4', 'R1c5',
    'R2c2', 'R2c3', 'R2c4', 'R2c5',
    'R3c2', 'R3c3', 'R3c4', 'R3c5',
    'R4c2', 'R4c3', 'R4c4', 'R4c5',
    'R5c2', 'R5c3', 'R5c4', 'R5c5',
    'R6c2', 'R6c3', 'R6c4', 'R6c5',
    'R7c2', 'R7c3', 'R7c4', 'R7c5',
    'R8c2', 'R8c3', 'R8c4', 'R8c5',
    'R9c2', 'R9c3', 'R9c4', 'R9c5',
    'R5Qc2','R5Qc3','R5Qc4','R5Qc5',
    'R6Qc2','R6Qc3','R6Qc4','R6Qc5',
    'R7Qc2','R7Qc3','R7Qc4','R7Qc5',
    'R8Qc2','R8Qc3','R8Qc4','R8Qc5',
    'R10Qc2','R10Qc3','R10Qc4','R10Qc5',
    'R11Qc2','R11Qc3','R11Qc4','R11Qc5',
    'R12Qc2','R12Qc3','R12Qc4','R12Qc5',
    'R13Qc2','R13Qc3','R13Qc4','R13Qc5',
    'R14Qc2','R14Qc3','R14Qc4','R14Qc5',
    'RAD51',
    'S100','S100A6','SOX9','SYP',
    'TFF1','TUBB3',
    'Vim',
    'ZEB1',
}

# fundamental standard cytoplasm marker nameing convention rules:
# this set is dependent on what we use for cytoplasm segmentation. in our case usually only Ecad or panCK.
# in our case usually only Ecad or panCK.
# 1. markers have to be in the es_marker_standard set.
es_cytoplasmmarker_standard = {
    'aSMA','Arg1',
    'BAX','BCL2','BMP2','BMP4','BMP6',
    'CAV1','CGA','CK5','CSF1R','CD44',
    'CK7','CK8','CK14','CK17','CK18','CK19','panCK',
    'Ecad','EGFR','EpCAM',
    'Gal3','Glut1',
    'HER2',
    'LYVE1',
    'MUC1',
    'NFkB',
    'PDGFRa','PDL1',
    'p63''pAKT''pERK','pS6RP',
    'S100','S100A6','SYP',
    'TFF1','TUBB3',
    'Vim',

    # miltenyi
    'Actin-SmoothM',
    'b-Tubulin',
    'bActin',
    'Bcl-2',
    'Calponin',
    'CD123',
    'CD134',
    'CD138-SDC1',
'    CD162',
    'CD20-Cytoplasmic',
    'CD209',
    'CD271',
    'CD326',
    'CD44',
    'CD90',
    'Cytokeratin-14',
    'Cytokeratin-5-6',
    'Cytokeratin-7',
    'Cytokeratin-8',
    'Cytokeratin-CK5',
    'Cytokeratin-HMW',
    'Desmin-CMV',
    'HLA-DR',
    'HLA-DR-DP-DQ',
    'MelanA',
    'Melanosome-HMB45',
    'Myosin-HC',
    'pan_Cytokeratin',
    'Podoplanin',
    'Vimentin',
}

# fundamental marker_partition nameing convention rules:
# 1. valid standard cellpartition are: Nuclei, Ring, Nucmem, Cellmem
# 2. marker and partition have to be separated by underscore!
# 3. marker names can not contain underscores, never!
# 4. markers have to be in the es_marker_standard set.
es_markerpartition_standard = {
    '53BP1_Nuclei',
    'AR_Nuclei', 'Arg1_Ring', 'aSMA_Ring',
    'BAX_Ring', 'BCL2_Ring', 'BMP2_Ring', 'BMP4_Ring', 'BMP6_Ring',
    'CAV1_Ring', 'CC3_Nuclei','CC3-488_Nuclei','CC3-647_Nuclei','CCND1_Nuclei',
    'CD3_Ring', 'CD4_Ring', 'CD8_Ring', 'CD11b_Ring', 'CD11c_Ring', 'CD20_Ring', 'CD31_Ring', 'CD44_Ring', 'CD45_Ring', 'CD68_Ring', 'CD74_Ring', 'CD90_Ring', 'CD103_Ring',
    'CGA_Ring',
    'CK5_Ring', 'CK7_Ring', 'CK8_Ring', 'CK14_Ring', 'CK17_Ring', 'CK18_Ring', 'CK19_Ring',
    'ColI_Ring', 'ColIV_Ring', 'ColVI_Ring', 'CoxIV_Ring',
    'cPARP_Nuclei',
    'CSF1R_Ring',
    'DAPI_Nuclei',
    'Ecad_Ring','Ecad_Cellmem', 'EGFR_Ring','EGFR_Cellmem', 'EpCAM_Ring','EpCAM_Cellmem', 'ER_Nuclei',
    'F4-80_Ring', 'FN1_Ring', 'FoxP3_Nuclei',
    'Gal3_Ring', 'GATA3_Nuclei', 'GATA6_Nuclei', 'gH2AX_Nuclei', 'Glut1_Ring', 'GRNZB_Nuclei',
    'H3K4_Nuclei', 'H3K27_Nuclei', 'HER2_Ring','HER2_Cellmem', 'HIF1a_Nuclei',
    'Ki67_Nuclei', 'Ki67r_Nuclei', # special
    'LamAC_Nuclei', 'LamB1_Nuclei', 'LamB2_Nuclei', 'LYVE1_Ring',
    'MHCII_Ring', 'MSH2_Nuclei', 'MSH6_Nuclei', 'MUC1_Ring',
    'NFkB_Ring',
    'PCNA_Nuclei', 'PD1_Ring', 'PDGFRa_Ring', 'PDL1_Ring', 'PDL1ab_Ring', 'PDL1d_Ring', 'PDPN_Ring', 'PgR_Nuclei', 'PgRb_Nuclei', 'PgRc4_Nuclei',  # special
    'p63_Nuclei','p63_Ring', 'pAKT_Ring', 'pAKT_Cellmem', 'pERK_Nuclei', 'pERK_Ring', 'pHH3_Nuclei', 'pMYC_Nuclei', 'pRB_Nuclei',  'pS62MYC_Nuclei', 'pS6RP_Ring', 'panCK_Ring', # kicked pRb_Nuclei
    'RAD51_Nuclei',
    'S100_Ring', 'S100A6_Ring', 'SOX9_Nuclei', 'SYP_Ring',
    'TFF1_Ring', 'TUBB3_Ring',
    'Vim_Ring',
    'ZEB1_Nuclei',

    # mitlenyi
    'Actin-SmoothM_Ring',  # aSMA
    'b-Tubulin_Ring',  # b-Tubulin-3  TUBB3
    'bActin_Ring',  # ACTB
    'Bcl-2_Ring',  # BCL2
    'beta-Catenin_Nuclei',  # CTNNB1
    'beta-Catenin_Ring',  # CTNNB1
    'Calponin_Ring',  # CNN1
    'CD123_Ring',  # IL3R
    'CD134_Ring',  # TNFRSF4/OX40 receptor
    'CD138-SDC1_Ring',  # SCD1: Syndecan-1
'    CD162_Ring',  # SELPLG/PSGL-1 :L P-selectin glycoprotein ligand-1
    'CD20-Cytoplasmic_Ring',  # CD20
    'CD209_Ring',  # DC-SIGN
    'CD223_Ring',  # LAG-3: Lymphocyte-activation gene 3 -- T cell activation ligand
    'CD271_Ring',  # NGFR: Low-affinity nerve growth factor receptor
    'CD279_Ring',  # PD-1: Programmed cell death protein 1
    #'CD3_Ring',  # same
    'CD326_Ring',  # EPCAM
    #'CD44_Ring',  # same
    #'CD45_Ring',  # same
    'CD45RA_Ring',  # Naive T lymphocytes
    'CD45RO_Ring',  # Activated and memory T lymphocytes
    'CD66b_Ring',  # Granulocyte
    #'CD8_Ring',  # same
    #'CD90_Ring',  # same
    'Cytokeratin-14_Ring',  # CK14
    'Cytokeratin-5-6_Ring',  # CK5_CK6
    'Cytokeratin-7_Ring',  # CK7
    'Cytokeratin-8_Ring',  # CK8
    'Cytokeratin-CK5_Ring',  # CK5
    'Cytokeratin-HMW_Ring',  # CK
    'Desmin-CMV_Ring',  # muscle-specific, type III intermediate filament
    'EZH2_Nuclei',
    'HLA-DR_Ring',  # Human Leukocyte Antigen – DR isotype
    'HLA-DR-DP-DQ_Ring',  # Human Leukocyte Antigen – DR, DP, DQ,  isotypes
    'Ki-67_Nuclei',  # Ki67
    'MelanA_Ring',  # melanocyte specific
    'Melanosome-HMB45_Ring',  #? melanocyte specific
    'Myosin-HC_Ring',  # muscle-specific, type III intermediate filament
    'p53_Nuclei',
    'pan_Cytokeratin_Ring',  # panCK ring, cytoplasm
    #'PCNA_Nuclei', # same
    'Podoplanin_Ring',
    'TTF-1_Nuclei',  # TTF1 Transcription termination factor 1
    'Vimentin_Ring',  # Vim
    'WT_Nuclei',  # Wilms Tumor Protein
}


# fundamental nameing convention rules:
# 1. slide, mscene, and scene can not conatin underscores. never!
# 2. cmIF round numbers have to be given as integers. E.g. 7
# 3. quenching rounds, used for autofluorescence subtraction,
#    have to be labeled with the alphabetic character specified in s_quenching (E.g. Q) behind the previous cmIF round integr. (E.g. 7Q)
# 4. the markers specifield in the filename have not to include the DAPI channel!
# 5. subfolders have to start with slide (though can be slide_mscene or slide_pxscene or slide what ever).
# all the rest can be adjusted to your labs need by carefully chaning the information in d_nconv.

# nameing convention
d_nconv = {

    ##########
    # wetlab #
    ##########
    # microscopy specification
    # (adjust to your labs specifictaion)
    's_marker_dapi': 'DAPI',  # bue 20210812: works for miltenyi too, does not have to be DAPIV0!

    # czi axom
    's_round_czi': 'R',
    's_quenching_czi': 'Q',  # one character string used to label quenching rounds
    's_sep_marker_czi': '.',  #!
    's_sep_markerclone_czi': None,  #!
    's_color_czi': 'c',
    's_color_dapi_czi': 'c1',
    'ls_color_order_czi': ['c1','c2','c3','c4','c5','c6','c7','c8'],  # bue: this is in the filenames, but not inside the files!

    # ome.tiff miltenyi
    # bue 20210811 challanges:
    's_round_mics': 'C-',
    's_quenching_mics': None,  # one character string used to label quenching rounds
    's_sep_marker_mics': None,  #!
    's_sep_markerclone_mics': '__',  #!
    's_color_mics': '',
    's_color_dapi_mics': 'DAPI',
    'ls_color_order_mics': ['DAPI','FITC','PE','APC'],

    # tiff jinxif
    # bue 20210812: rounds are still often hardcoded.
    's_round_jinxif': 'R',
    's_quenching_jinxif': 'Q',  # one character string used to label quenching rounds
    's_sep_marker_jinxif': '.',  #!
    's_sep_markerclone_jinxif': None,  #!
    's_color_jinxif': 'c',
    's_color_dapi_jinxif': 'c1',
    'ls_color_order_jinxif': ['c1','c2','c3','c4','c5','c6','c7','c8'],


    #########
    # paths #
    #########

    # czi: czi path to original folder below slide
    # (adjust to your labs specifictaion, though all format variables have to be used in this order)
    's_czidir': './CziImages/',  # Cyclic_Image/{batch}/
    's_format_czidir_original': '{}{}/original/',  # s_czidir, s_slide
    's_format_czidir_splitscene': '{}{}/splitscenes/',  # s_czidir, s_slide

    # ome.tiff miltenyi: path
    's_micsdir': './MicsImages/',

    # raw : raw path per slide
    # (adjust to your labs specifictaion, though all format variables have to be used in this order)
    's_rawdir': './RawImages/',
    's_format_rawdir': '{}{}/',  # s_rawdir, s_slide

    # regist : registration path per slide_pxscene
    # (adjust to your labs specifictaion, though all format variables have to be used in this order)
    's_regdir': './RegisteredImages/',
    's_format_regdir': '{}{}/',  # s_regdir, s_slide_pxscene

    # afsub : autofluorescence subtracted path per slide_pxscene
    # (adjust to your labs specifictaion, though all format variables have to be used in this order)
    's_afsubdir': './SubtractedRegisteredImages/',
    's_format_afsubdir': '{}{}/',  # s_afsubdir, s_slide_pxscene

    # segment : cellpose segementation path per slide_pxscene
    # (adjust to your labs specifictaion, though all format variables have to be used in this order)
    's_segdir': './Segmentation/',
    's_format_segdir_cellpose': '{}{}_CellposeSegmentation/',  # s_segdir, s_slide_pxscene

    # qc : quality control result path (adjust to your labs specifictaion)
    # (adjust to your labs specifictaion)
    's_qcdir': './QC/',

    # meta: metadata result path
    # (adjust to your labs specifictaion)
    's_metadir': './MetaImages/',


    ###############
    # input files #
    ###############

    # @ axon czi files
    # (adjust to your labs specifictaion, though all information have to be found)
    's_regex_czi_original': r'^(R[^_]+)_([^_]+)_([^_]+)_(.*)\.(czi)', # 4 markers separated by dots!
    'di_regex_czi_original': {'round':1, 'markers':2, 'slide':3, 'scanid':4, 'filetype':5}, # used? scanid filetype
    #'s_regex_czi_stitched': r'^(R[^_]+)_([^_]+_[^_]+_[^_]+_[^_]+)_([^_]+)_(.*)-([^\.]+)\.(czi)$', # 4 markers separated by underscore1
    #'di_regex_czi_stitched': {'round':1, 'markers':2, 'slide':3, 'scanid':4, 'mscene':5, 'filetype':6}, # used? scanid
    's_regex_czi_splitscene': r'^(R[^_]+)_([^_]+)_([^_]+)_([^-]*)-([^\.]+)\.(czi)$', # 4 markers separated by dots!
    'di_regex_czi_splitscene': {'round':1, 'markers':2, 'slide':3, 'scanid':4, 'mscene':5, 'filetype':6}, # used? scanid filetype

    # @ miltenyi ome.tiff fils
    's_regex_tiff_mics': r'(R-[^_]+_W-[^_]+)_(G-[^_]+)_(C-[^_]+)_([^\.]+)\.([^_]+)_([^\.]+)\.([^\.]+)\.(ome\.tiff?)',
    'di_regex_tiff_mics': {'slide':1, 'scene':2, 'round':3, 'marker_clone':4, 'color':5, 'exposure_time_ms':6, 'imagetype':7, 'filetype':8}, # used? filetype

    # @ raw tiff files
    # (adjust to your labs specifictaion, though all information have to be found)
    's_regex_tiff_raw': r'^(R[^_]+)_([^_]+)_([^_]+)_([^-]*)-([^_]+)_([^_]+)_([^\.]+)\.(tiff?)',  # 4 markers separated by dots!
    'di_regex_tiff_raw': {'round':1, 'markers':2, 'slide':3, 'scanid':4, 'mscene':5, 'color':6, 'imagetype':7, 'filetype':8},  # used? scanid filetype


    #################
    # output files #
    ################
    # @ imgmeta files
    's_format_csv_sceneposition': '{}_ScenePositions_xy.csv',  # s_slide
    's_format_csv_exposuretime': '{}_ExposureTimes_ms.csv',  # s_slide
    's_format_csv_etmatrix': '{}_exposure_time_ms_matrix.csv',  # s_batch
    's_format_png_etmatrix': '{}_exposure_time_ms_matrix.png',  # s_batch
    's_format_json_etcorrect': '{}_ExposureTimeCorrect.json',  # s_batch

    # @ reg tiff files
    's_format_json_crop': '{}_CropCoordinate.json',  # s_batch
    # bue 20210706: currently registration file name is hardcoded in matlab code!
    's_format_tiff_reg': 'Registered-{}{}_{}_{}_{}_{}_{}.tif',  # s_round, i_round, s_markers, s_slide, s_scene, color, imagetype
    's_regex_tiff_reg': r'^Registered-([^_]+)_([^_]+)_([^_]+)_([^_]+)_([^_]+)_([^\.]+)\.(tiff?)$',
    'di_regex_tiff_reg': {'round':1, 'markers':2, 'slide':3, 'scene':4, 'color':5, 'imagetype':6, 'filetype':7},

    # @ afsub tiff files: autofluorescent subtracted registered tiff file
    # bue 20210706: format should be comatibel with registration
    's_format_tiff_afsubreg': 'Registered-{}{}_{}_{}_{}_{}_Sub{}.tif',  # s_round, i_round, s_markers, s_slide, s_scene, color, imagetype
    's_format_tiff_micsstitchline' : '{}_Mics_StitchLineMask.npy',  # slide_scene  milteny only

    # @ thresh
    's_format_csv_threshold': 'thresh_{}_Threshold_{}.csv',  # s_slide, s_input

    # @ segment and feat: basin files format string, regex string, and variabel position dictionary
    's_format_tiff_celllabel_nuc': '{}_nuc{}_NucleiSegmentationBasins.tif',  # s_slide_pxscene, i_nuc_diam
    's_regex_tiff_celllabel_nuc': r'^([^_]+)_([^_]+)_nuc(\d+)_NucleiSegmentationBasins.tif$',  # s_slide_pxscene, i_nuc_diam
    's_format_tiff_celllabel_cell': '{}_{}_cell{}_CellSegmentationBasins.tif',  # s_slide_pxscene, ls.seg.marker, i_cell_diam
    's_regex_tiff_celllabel_cell': r'^([^_]+)_([^_]+)_([^_]+)_cell(\d+)_CellSegmentationBasins.tif$',  # s_slide_pxscene, ls.seg.marker, i_cell_diam
    's_format_tiff_celllabel_nuccellmatched': '{}_{}_nuc{}_cell{}_matched_CellSegmentationBasins.tif',  # s_slide_pxscene, ls.seg.marker, i_nuc_diam, i_cell_diam
    's_regex_tiff_celllabel_nuccellmatched': r'^([^_]+)_([^_]+)_([^_]+)_nuc(\d+)_cell(\d+)_matched_CellSegmentationBasins.tif$',  # s_slide_pxscene, ls.seg.marker, i_nuc_diam, i_cell_diam # JE-TMA-48b_scene001_Ecad _nuc30_cell30_matched_CellSegmentationBasins.tif
    'di_regex_tiff_celllabel_nuccellmatched':{'s_slide':1, 's_pxscene':2, 's_seg_markers':3, 'i_nuc_diam':4, 'i_cell_diam':5},
    's_format_tiff_celllabel_nuccellmatchedfeat': '{}_{}_nuc{}_cell{}_matched_exp5_CellSegmentationBasins.tif',  # s_slide_pxscene, ls.seg.marker, i_nuc_diam, i_cell_diam
    #'s_regex_tiff_celllabel_nuccellmatchedfeat': r'^([^_]+)_([^_]+)_([^_]+)_nuc(\d+)_cell(\d+)_matched_exp5_CellSegmentationBasins.tif$',  # s_slide_pxscene, ls.seg.markers, i_nuc_diam, i_cell_diam

    # @ segment : projection for segementation, and variabel position dictionary
    's_format_png_nucprojection': '{}_nuc{}_NucleiProjection.png',  # s_slide_pxscene, i_nuc_diam
    's_format_png_cellprojection': '{}_{}_cell{}_CellProjection.png',  # s_slide_pxscene, s.seg.markers, i_cell_diam

    # @ feat : celltouch by segmentation json file and feature csv files
    's_format_json_celltouch_segmentation': 'celltouch_segmentation_{}.json', # s_slide
    's_format_csv_controidxy': 'features_{}_CentroidXY.csv',  # s_slide   # centroid xy information
    's_format_csv_patched_shape_meanintenisty': 'features_{}_patched_MeanIntensity_Shape_{}_{}.csv', # s_slide, s_filter_dapi, s_input
    's_format_csv_raw_centroid_shape_meanintenisty': 'features_{}_raw_MeanIntensity_Shape_Centroid_{}.csv',  # s_slide, s_input
}


# functions
def slurmbatch(
        s_pathfile_sbatch,
        s_srun_cmd,
        s_jobname = None,
        s_partition = None,
        s_gpu = None,
        s_mem = None,
        s_time = None,
        s_account = None,
    ):
    '''
    version: 2021-04-21

    input:
        s_pathfile_sbatch: path and filename of the sbatch file that is generated.
        s_srun_cmd: commandline command to be run via srun.
        s_jobname: 8 letter job name to be displayed at squeue.
            if None, the first 8 letters form the s_pathfile_sbatch filename will be taken.
        s_partition: slurm cluster partition to use.
            OHSU ACC options are 'exacloud', 'light', (and 'gpu').
            the default is tweaked to OHSU ACC settings.
        s_gpu: slurm cluster gpu allocation.
            OHSU ACC options are any 'gpu:1', faster 'gpu:v100:1', slower 'gpu:p100:1',
            not rapids compatible is 'gpu:rtx2080:1'.
        s_mem: slurm cluster memory allocation. format '64G'.
        s_time: slurm cluster time allocation in hour or day format.
            OHSU ACC max is '36:00:00' [hour] or '30-0' [day].
            the related qos code is tewaked to OHSU ACC settings.
        s_account: slurm cluster account to credit time from.
            my OHSU ACC options are 'gray_lab', 'chin_lab', 'heiserlab'.

    output:
        executable sbatch file generated at s_pathfile_sbatch.

    description:
        generate an executable slurm sbatch file.
        this code might be very specific to the OHSU ACC exacloud cluster.
    '''
    # bash shebang
    s_batchfile = '#!/bin/bash\n'
    # partition
    if not (s_gpu is  None):
        s_partition = 'gpu'
    s_batchfile += f'#SBATCH --partition={s_partition}\n'
    # gpu
    if not (s_gpu is None):
        s_batchfile += f'#SBATCH --gres={s_gpu}\n'
    # ram
    if not (s_mem is None):
        s_batchfile += f'#SBATCH --mem={s_mem}\n'
    # time and qos
    if not (s_time is None):
        s_batchfile += f'#SBATCH --time={s_time}\n'
        if (s_time.find('-') > -1) and (float(s_time.replace('-','.')) > 1.5):
            if (s_gpu != None):
                s_qos = 'gpu_long_jobs'
            elif (float(s_time.replace('-','.')) > 10):
                s_qos = 'very_long_jobs'
            else:
                s_qos = 'long_jobs'
            # add sbatch entry
            s_batchfile += f'#SBATCH --qos={s_qos}\n'
    # account
    if not (s_account is None):
        s_batchfile += f'#SBATCH -A {s_account}\n'
    # job name
    if not (s_jobname is None):
        s_batchfile += f'#SBATCH --job-name={s_jobname}\n'
    # run dmc
    s_batchfile += f'srun {s_srun_cmd} 2>&1\n'
    # generate sbatch file
    with open(s_pathfile_sbatch, 'w') as f:
        f.write(s_batchfile)
    # make sbatch file executable for current user
    os.chmod(s_pathfile_sbatch, os.stat(s_pathfile_sbatch).st_mode | stat.S_IEXEC)  # bue: the | is a bit wise OR operator

