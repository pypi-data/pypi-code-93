#####
# title: template_registration.py 
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-04-23
#
# description:
#     template script for python based IF image registration, 
#     for one slide, one microscopy scene, all microscopy channle cyclic images.
#
# instruction:
#     use mplex_image.regist.registration function to edit and run this template.
#
# input: 
#     tiffs or big tiffs (>4GB) with filename eding in s_regex_ext.
#     there can be as many files in the s_src_dir input folder as they want,
#     though s_regex_round, s_regex_marker, s_regex_micchannel and
#     s_imgall_glob, s_imgdapi_glob, s_imgdapi_ref_glob, have to be slide_mscene specific,
#     what ever naming convention you follow.
#
#     E.g. ChinLab filename convention is:
#     Rx_Bi.o.mark.ers_Slidename-Section(-Scene)_xxx_xx_x_cx_ORG.tif,
#     where c1 is DAPI and x can be variable (i.e. from axioscan)
# 
# output:
#     the output tiff files in m_dst_dir folder will follow the namingconvention:
#     Registered-round<>marker<>slidepxscene<>micchanel<>ext
#     make sure that you integarte a separater (symbolized by <>) into your regex patterns.
#####

# input parameters
spy_slide = 's_slide' # slide label wich will be used in the filename
spy_mscene = 's_mscene'  # 
dpy_crop = sdl_crop  # crop corinates dictionary for one mscene maybe many pxscene where px_scene is the key
spy_regex_ext = s_regex_ext  # file extension rexgex pattern
spy_regex_round = s_regex_round  # staining round regexp pattern
spy_regex_marker = s_regex_marker  # stain regex pattern
spy_regex_micchannel = s_regex_micchannel  # microscopy channel regex pattern
spy_imgall_glob = s_imgall_glob  # slide_mscene specific image glob pattern for all channels
spy_imgdapi_glob = s_imgdapi_glob  # slide_mscene specific dapi channel image glob pattern
spy_imgdapi_ref_glob = s_imgdapi_ref_glob  # slide_mscene specific round 1 dapi channel image glob pattern
spy_src_dir = s_src_dir  # location of raw images folder
spy_dst_dir = s_src_dir  # location of folder where registered images will be stored
spy_qcregistration_dir = s_qcregistration_dir  # location of folder where possible qc plots will be stored
ipy_npoint = i_npoint  # number of features to detect in image (default = 10000)






    # bue: use sililar regexcode for getting files as in matlab
    # bue: this should get as slurm script
ster registration for one slide one microscopy scene one px scene cyclic images
    # for each dapi file roundx

        # actual registration
        moving_pts, target_pts, transformer = register.register(s_target_file, s_moving_file, s_qcregistration_dir=s_qcregistration_dir)

        # for each dapi and non-dapi channel

            # load image
            a_moving = io.imread(s_moving_channel)
            # apply transform
            warped_img, warped_pts = register.apply_transform(a_moving, a_target, moving_pts, target_pts, transformer)
            warped_img = util.img_as_uint(warped_img)
            # apply isaac finetunei
            
            # crop to pxscene
                    #l_crop = ddd_crop[s_slide][s_mscene]
                    #if not (l_crop is None):
                    #   pass

                # save image
                # os.makedirs()
                io.imsave(
                    f"{s_regdir}/{s_slide}-Scene-{i_scene}/Registered-{s_moving_channel.split(s_slide)[0]}{s_slide}-Scene-{s_moving_channel.split('-Scene-')[1]}",
                    warped_img
                )
