import colorsys
import csv
import inspect
import os
import pickle
from collections import OrderedDict

import SimpleITK as sitk
import numpy as np
import plotly.graph_objects as go
import seaborn as sns
from matplotlib import pyplot as plt
from medpy import metric

from headctools import utilities as utils
# import utilities as utils

sns.set()
sns.set_context("paper")


# plt.style.use('ggplot')
# sns.set_style({"axes.grid": "False"})

def get_files_and_filter(folders, file_identifier=None, file_ext='.nii.gz'):
    """ From a list of folders get another list of its files and filter them by pred_folder following the corresponding elem.
        in file_identifiers.

        For example: folders = ['/usr/folderA', '/usr/folderB'] and file_identifiers =  ['_important', '_relevant']
        if:
        /usr/folderA has the files: ['file1_important.zip', 'file2_other.zip', 'file3_important.zip']
        /usr/folderB has the files: ['file1_other.zip', 'file2_relevant.zip']

        The output will be: [['file1_important.zip', 'file3_important.zip'], ['file2_relevant.zip']]


    :param folders: list of folders to explore.
    :param file_identifier: list of patterns in each pred_folder to find.
    :return: list of lists having the files in each pred_folder that match the corresponding pattern.
    """
    filenames_in_each_folder = []
    for i, folder in enumerate(folders):
        files_in_folder = []
        for name in os.listdir(folder):
            if file_identifier:
                if file_identifier[i] + file_ext not in name:
                    continue
                files_in_folder.append(os.path.join(folder, name))
        filenames_in_each_folder.append(files_in_folder)

    tams = [len(folder) for folder in filenames_in_each_folder]
    if len(np.unique(tams)) > 1:
        print("Warning: Each pred_folder has a different amount of files!")

    return filenames_in_each_folder


def get_metric_fn(metric_str):
    if metric_str == 'dice':
        return metric.binary.dc
    if metric_str == 'hausdorff':
        return metric.binary.hd
    if metric_str == 'volumes':
        return get_volumes
    if metric_str == 'vol_err':
        return volume_relative
    else:
        return None


def get_volumes(im1, im2, spacing=None):
    """ Get a tuple with the volumes of both images. If the spacing is not provided it'sh assumed to be 1 in each dimension.

    :param im1: numpy image.
    :param im2: numpy image.
    :param spacing: spacing (distance between pxiels in each coordinate) of the images.
    :return:
    """
    if not spacing:
        spacing = np.ones(len(im1.shape))

    vol_voxel = np.prod(spacing)  # sp[0] * sp[1] * sp[2]
    vol1 = np.count_nonzero(im1) * vol_voxel
    vol2 = np.count_nonzero(im2) * vol_voxel
    return (vol1, vol2)


def volume_relative(im1, im2, spacing=None, v_abs=True):
    """ Get the volumes of each image and calculate the relative error to the first image.

    :param im1: numpy image.
    :param im2: numpy image.
    :param spacing: spacing (distance between pxiels in each coordinate) of the images.
    :return:
    """
    if not spacing:
        spacing = np.ones(len(im1.shape))

    vol_voxel = np.prod(spacing)  # sp[0] * sp[1] * sp[2]
    vol1 = np.count_nonzero(im1) * vol_voxel
    vol2 = np.count_nonzero(im2) * vol_voxel
    err = np.abs(vol1 - vol2) if not v_abs else np.abs((vol1 - vol2))/1000
    return err


def boxplot_matplotlib(stats_dict, measure, append=None):
    if append:
        print("Append mode not supported yet.")
    dice, ax = plt.subplots(figsize=(8, 6))
    plt.yscale("linear")
    lst = list(stats_dict[measure].values())
    lst = [list(lst[i].values()) for i in range(len(lst))]

    plt.boxplot(lst, showmeans=True)
    ax.set_xlabel('Method')
    plt.title('({}) {}'.format(str(inspect.stack()[1].function), measure))
    ax.set_ylabel(measure)

    labels = list(stats_dict[measure].keys())
    ax.set_xticklabels(labels)

    # The same but in log scale
    dice, ax = plt.subplots(figsize=(8, 6))
    plt.yscale("log")
    plt.boxplot(lst, showmeans=True)
    ax.set_xlabel('Method')
    plt.title('({}) {}'.format(str(inspect.stack()[1].function), measure))
    ax.set_ylabel(measure + ' (log scale)')

    labels = list(stats_dict[measure].keys())
    ax.set_xticklabels(labels)

    # plt.xticks(rotation=30, horizontalalignment='right')

    # if name is None:
    #     svPath = os.path.join(save_path, measure + '.png')
    # else:
    #     svPath = os.path.join(save_path, measure + name + '.png')
    # plt.savefig(svPath)
    # print("Output path: ", svPath)


# plt.rcParams['lines.solid_capstyle'] = 'round'


def expand(x, y, gap=1e-4):
    add = np.tile([0, gap, np.nan], 1)
    x1 = np.repeat(x, 3) + add
    y1 = np.repeat(y, 3) + add
    return x1, y1


def change_brightness(color, factor):
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)

    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    r, g, b = colorsys.hsv_to_rgb(h, s, v * factor)

    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    return '#' + hex(int(r))[2:].zfill(2) + hex(int(g))[2:].zfill(2) + hex(int(b))[2:].zfill(2)


def volumeplot_matplotlib(stats, method, append=None, cmap='CMRmap', legend_style='reference', legend_text='Patient ',
                          save_path=None):
    """

    :param stats:
    :param method:
    :param append:
    :param cmap:
    :param legend_style: 'reference', 'customtext' (takes legend_text) or 'none'
    :param legend_text:
    :return:
    """
    plt.figure(figsize=(6, 6))

    # coordsxy = (*zip(*stats[method].values()),)
    # plt.scatter(coordsxy[0], coordsxy[1], c='#'+str(hex(np.random.randint(16777215)))[2:].zfill(6))

    short_names = np.unique([utils.crop_str_from_n_ocurrence(name, '_', 1) for name in list(stats[method].keys())])
    cmap = plt.get_cmap(cmap)
    colors = cmap(np.linspace(0, .85, len(short_names)))

    grayscale_dots = True
    div_n = 1000  # mm3 --> cm3

    for key in stats[method].keys():
        color = colors[
            np.where(short_names == utils.crop_str_from_n_ocurrence(key, '_', 1))] if not grayscale_dots else '#888888'

        # color = hex_color(utils.crop_str_from_n_ocurrence(key, '_', 1))
        # color = '#888888'
        plt.scatter(*expand(stats[method][key][0] / div_n, stats[method][key][1] / div_n), c=color, alpha=.2,
                    label=utils.crop_str_from_n_ocurrence(key, '_', 1), linewidths=1)

    min_val = min(min(*stats[method].values()))
    max_val = max(max(*stats[method].values()))

    if append:
        for key in append.stats_dict['volumes'][method].keys():
            color = colors[np.where(short_names == utils.crop_str_from_n_ocurrence(key, '_', 1))]
            # color = idx(utils.crop_str_from_n_ocurrence(key, '_', 1))
            plt.scatter(append.stats_dict['volumes'][method][key][0] / div_n,
                        append.stats_dict['volumes'][method][key][1] / div_n, c=color, alpha=1,
                        label=utils.crop_str_from_n_ocurrence(key, '_', 1), s=100, edgecolors='#000000', linewidths=.5,
                        marker='X')

        min_val = min(min_val, min(min(*append.stats_dict['volumes'][method].values())))
        min_val = min(0, min_val)
        max_val = max(max_val, max(max(*append.stats_dict['volumes'][method].values())))

    if legend_style == 'reference':
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip([labels[-1], labels[1]], [handles[-1], handles[1]]))
        # text_labels = ["Real image " + str(i) for i in range(1, 1 + len(by_label.keys()))]
        text_labels = ["Real image", "Simulated image"]
        plt.legend(by_label.values(), text_labels)
    elif legend_style == 'customtext':
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        text_labels = [legend_text + str(i) for i in range(1, 1 + len(by_label.keys()))]
        plt.legend(by_label.values(), text_labels)
    else:
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())

    max_val = max(max_val, 400000)
    plt.plot([min_val / div_n, max_val / div_n], [min_val / div_n, max_val / div_n], c='#000000')

    font_s = 12
    title_s = font_s - 1
    tick_s = font_s
    label_s = tick_s

    plt.tick_params(axis='x', labelsize=tick_s)
    plt.tick_params(axis='y', labelsize=tick_s)

    plt.xlabel('Volume using ' + method, fontsize=label_s)
    plt.ylabel('Volume of the GT', fontsize=label_s)
    plt.title('Volume comparison: Ground Truth vs {} (in cm$^3$)'.format(method), fontsize=title_s)
    plt.axis('equal')
    plt.tight_layout()
    plt.xlim((-10, 430))
    plt.ylim((-10, 430))

    if save_path:
        fpath, ext = os.path.splitext(save_path)
        save_path = fpath + '_' + method + ext
        plt.savefig(save_path)


def hex_color(file_name):
    seed_from_name = utils.str_to_num(utils.crop_str_from_n_ocurrence(file_name, '_'), max_n=16777215)
    np.random.seed(seed_from_name)
    return '#' + str(hex(np.random.randint(16777215)))[2:].zfill(6)


def boxplot_plotly(stats_dict, measure, colors=None, append=None, title=None, yaxis=None, save_path=None,
                   def_plot=True,
                   log_plot=False):
    default_color = True if not colors else False
    methods = list(stats_dict[measure].values())
    methods = [list(methods[i].values()) for i in range(len(methods))]

    if append:
        a_methods = list(append.stats_dict[measure].values())
        a_methods = [list(a_methods[i].values()) for i in range(len(a_methods))]

    title = '({}) {}'.format(str(inspect.stack()[1].function), measure) if not title else title

    layout = go.Layout(
        autosize=False,
        width=650,
        height=650,
        margin=go.layout.Margin(
            l=10,
            r=10,
            b=40,
            t=40,
            pad=4
        )
    )

    fig = go.Figure(layout=layout)

    for i, method in enumerate(methods):
        if default_color:
            colors = ['#3D9970'] * len(method)
        elif len(colors) == 1 and type(colors) == list:
            colors = colors * len(method)
        elif len(colors) < len(method) and type(colors) == list:
            colors = colors * int((len(method) + 1) // len(colors))
        elif colors == 'random':
            colors = [hex_color(method_name) for method_name in list(stats_dict[measure].keys())] * len(method)

        fig.add_trace(go.Box(
            y=method,
            x=[''] * 10,
            name=list(stats_dict[measure].keys())[i],
            marker_color=colors[i],
            boxmean=True
        ))

    if append:
        for i, method in enumerate(a_methods):
            fig.add_trace(go.Box(
                y=method,
                x=[''] * 10,
                name=list(append.stats_dict[measure].keys())[i],
                marker_color=hex_color(hex_color(hex_color(colors[i]))),
                boxmean=True
            ))

    yaxis = measure if not yaxis else yaxis

    fig.update_layout(
        yaxis_title=yaxis,
        title=title,
        title_x=0.5,
        boxmode='group',
        plot_bgcolor='#eaeaf2',
        font=dict(
            family="DejaVu Sans, monospace",
            size=20,
            color="#000000"
        ),
        showlegend=True,
        margin=dict(l=10, r=10, t=65, b=10)
    )

    if def_plot:
        if measure == 'dice':
            fig.update_yaxes(range=[0, 1])
        else:
            fig.update_yaxes(range=[0, 180])

        fig.show()
        if save_path:
            fig.write_image(save_path)

    if log_plot:
        fig.update_layout(
            title=title + ' (log scale)',
            title_x=0.5,
            yaxis_type="log")

        fig.update_layout(
            title=title + ' (log scale)',
            title_x=0.5,
            yaxis_type="log")

        fig.show()

        if save_path:
            fpath, ext = os.path.splitext(save_path)
            save_path_log = fpath + '_log' + ext
            fig.write_image(save_path_log)


class MethodCompare(object):
    def __init__(self, folders=None, file_identifiers=None, method_names=None, cache_name=None):
        super(MethodCompare, self).__init__()
        self.spacings = []
        self.stats_dict = dict()
        self.folders = folders
        self.method_names = method_names
        self.file_identifiers = file_identifiers
        self.filenames = None
        self.metrics = None
        self.image_ext = '.nii.gz'
        self.cache_name = cache_name

    def get_files(self):
        if len(self.folders) != len(self.file_identifiers) and len(self.file_identifiers) != len(self.method_names):
            print('The input arrays have different lenghts (folders: {} file_identifiers: {} '
                  'method_names: {}).'.format(self.folders, self.file_identifiers, self.method_names))
            return None

        self.filenames = get_files_and_filter(self.folders, self.file_identifiers, self.image_ext)

    def compute_metric(self, metric):
        if len(self.filenames) < 2:  # Check no. folders > 1
            print("At least 2 folders are needed for comparison. Add more folders and try again")
            return None

        ground_truth = dict()
        out_metric = dict()
        metric_fn = get_metric_fn(metric)

        print("    processing folders")
        for i, folder in enumerate(self.filenames):  # different list with the same filenames but different endings
            spacings_current = []
            if i == 0:  # The first pred_folder is the ground-truth.
                for gt_file in folder:
                    f_name = os.path.split(gt_file.replace(self.file_identifiers[0], ''))[1]
                    sitk_gtimg = sitk.ReadImage(gt_file)
                    ground_truth[f_name] = sitk.GetArrayFromImage(sitk_gtimg)
                    spacings_current.append(sitk_gtimg.GetSpacing())
                self.spacings.append(spacings_current)  # GT spacings
                continue  # I wont compare the GT with itself so I skip this one.

            metric_output = dict()
            spacings_current = []
            for j, filepath in enumerate(folder):  # Compare each file with the corresponding file of the GT.
                sitk_img = sitk.ReadImage(filepath)
                im_method = sitk.GetArrayFromImage(sitk_img)
                spacings_current.append(sitk_img.GetSpacing())
                common_fname = os.path.split(filepath.replace(self.file_identifiers[i], ''))[1]
                if metric in ['hausdorff', 'volumes', 'vol_err']:  # In this metric I have to pass also the spacing
                    if metric == 'hausdorff' and (not ground_truth[common_fname].sum() or not im_method.sum()):
                        print("Skipped hd calculation for {}.".format(filepath))
                        continue
                    metric_output[common_fname] = metric_fn(im_method.astype(np.int8),
                                                            ground_truth[common_fname].astype(np.int8),
                                                            spacings_current[j])
                else:
                    metric_output[common_fname] = metric_fn(im_method, ground_truth[common_fname])
            self.spacings.append(spacings_current)  # GT spacings
            out_metric[self.method_names[i]] = metric_output
        return out_metric

    def create_metric_dict(self):
        self.stats_dict = dict()
        for metric_str in self.metrics:
            print("  Metric: {}.".format(metric_str))
            self.stats_dict[metric_str] = self.compute_metric(metric_str)

    def get_stats_dict(self, plot=False, output_folder=None):
        if not self.folders or not self.method_names or not self.file_identifiers:
            print("You must set folders, method_names and file_identifiers first.")
            return None

        print("Stats dict:\ngathering filenames...", end='')
        self.get_files()  # Explore the folders and grab the filepaths associated with the corresponding identifier
        print("done.")
        if not self.filenames:
            print("No files were detected in the provided folders. Please check the paths and file identifiers.")
            print(self.folders, self.file_identifiers)
            return None

        print("comparing files...")
        self.create_metric_dict()  # From the filepaths array compare the files using the given metrics
        print("done.")

        print("Plotting stats dict...", end='')
        if plot:
            self.plot_stats_dict()
        print("done.")

        return self.stats_dict

    def plot_stats_dict(self, append=None, library='plotly', title=None, yaxis=None, def_plot=True, log_plot=False):
        """ From the stats_dict dictionary previously created, draw the corresponding plots. It may be a boxplot or
        scatter-plot.

        :return:
        """
        print("Saving image: ", end='')
        for measure, stats in self.stats_dict.items():
            save_path = 'figures/' + measure + '_' + self.cache_name + '.png'
            print('  ' + save_path)
            if measure in ['dice', 'hausdorff', 'vol_err']:  # Boxplots
                if library == 'matplotlib':
                    boxplot_matplotlib(self.stats_dict, measure, append)
                else:
                    colors = ['#339966', '#4700b3', '#999900', '#004d99', '#ab2222']
                    boxplot_plotly(self.stats_dict, measure, colors=colors, append=append, title=title, yaxis=yaxis,
                                   save_path=save_path, def_plot=def_plot, log_plot=log_plot)
            elif measure in ['volumes']:  # Scatterplot and identity line
                for method in stats:
                    volumeplot_matplotlib(stats, method, append, save_path=save_path)
                    # volumeplot_plotly(stats, method)

    def append_stats(self, csv_path, param, method_name=None):
        if not method_name:
            method_name = os.path.splitext(os.path.split(csv_path)[1])[0]

        with open(csv_path) as csv_file:
            sniffer = csv.Sniffer()
            has_header = sniffer.has_header(csv_file.read(2048))

        with open(csv_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            for i, row in enumerate(csv_reader):
                if i == 0 and has_header:
                    continue
                if i == 1:
                    if param not in self.stats_dict:
                        self.stats_dict[param] = dict()
                    self.stats_dict[param][method_name] = dict()

                if len(row) == 3:  # tuple
                    self.stats_dict[param][method_name][row[0]] = (int(row[1]), int(row[2]))
                else:
                    self.stats_dict[param][method_name][row[0]] = int(row[1])

    def get_volerr_from_vols(self, method_name):
        if 'volumes' in self.stats_dict:
            if method_name in self.stats_dict['volumes']:
                self.stats_dict['vol_err'][method_name] = dict()
                for i, tup in enumerate(list(self.stats_dict['volumes'][method_name].values())):
                    f_name = list(self.stats_dict['volumes'][method_name].keys())[i]
                    self.stats_dict['vol_err'][method_name][f_name] = abs(tup[1] - tup[0])/1000

    def load_stats_and_plot(self, metrics_dict):
        for metric in metrics_dict.keys():
            if self.cache_name:
                cached_fname = 'figures/cache/' + self.cache_name + '_' + metric + '.P'
                if os.path.isfile(cached_fname):
                    print("Using cached metrics:  " + cached_fname)
                    self = read_cache(cached_fname)
                else:
                    self.metrics = [metric]
                    self.get_stats_dict()

                    print("Saving metrics cache:  " + cached_fname)
                    write_cache(cached_fname, self)
            else:
                print("Metrics results are not saved.")
                self.metrics = [metric]
                self.get_stats_dict()

            self.plot_stats_dict(title=metrics_dict[metric]['title'], yaxis=metrics_dict[metric]['yaxis'])


def read_cache(fpath):
    with open(fpath, "rb") as f:
        loaded = pickle.load(f)
    return loaded


def write_cache(fpath, content):
    with open(fpath, "wb") as f:
        pickle.dump(content, f)


def volumes_flaps(real_f, sim_f, f_indent_real, f_ident_sim, met_names,
                  abc_csv_path, cached_sim_path, cached_real_path):
    if os.path.isfile(cached_sim_path) and os.path.isfile(cached_real_path):
        sk_flap_simulated = read_cache(cached_sim_path)
        sk_flap_real = read_cache(cached_real_path)
    else:
        sk_flap_real = MethodCompare()
        sk_flap_real.folders = real_f
        sk_flap_real.file_identifiers = f_indent_real
        sk_flap_real.method_names = met_names
        sk_flap_real.metrics = ['volumes']

        sk_flap_real.get_stats_dict()

        sk_flap_simulated = MethodCompare()
        sk_flap_simulated.folders = sim_f
        sk_flap_simulated.file_identifiers = f_ident_sim
        sk_flap_simulated.method_names = met_names
        sk_flap_simulated.metrics = ['volumes']

        sk_flap_simulated.get_stats_dict()

        write_cache(cached_sim_path, sk_flap_simulated)
        write_cache(cached_real_path, sk_flap_real)

    sk_flap_real.append_stats(abc_csv_path, 'volumes', method_name='ABC')
    sk_flap_simulated.append_stats(abc_csv_path, 'volumes', method_name='ABC')

    sk_flap_simulated.cache_name = 'flaps_real_and_simulated'
    sk_flap_simulated.plot_stats_dict(append=sk_flap_real)


def vol_errs(im_f, f_ident, met_names, append_data, cache_name, cached_f):
    if os.path.isfile(cached_f):
        imgs_comp = read_cache(cached_f)
    else:
        imgs_comp = MethodCompare()
        imgs_comp.folders = im_f
        imgs_comp.file_identifiers = f_ident
        imgs_comp.method_names = met_names
        imgs_comp.metrics = ['volumes', 'vol_err']

        imgs_comp.get_stats_dict()

        write_cache(cached_f, imgs_comp)

    imgs_comp.append_stats(append_data['csv'], append_data['metric'], method_name=append_data['method_name'])
    imgs_comp.get_volerr_from_vols(method_name=append_data['method_name'])
    imgs_comp.cache_name = cache_name
    imgs_comp.plot_stats_dict(title='Volume absolute error (in cm3)', yaxis='absolute error', def_plot=False, log_plot=True)


if __name__ == '__main__':
    volumes_real = ['/home/fmatzkin/Code/datasets/SamCook-FAVO/volumes',
                  '/home/fmatzkin/Code/datasets/SamCook-FAVO/volumes',
                  '/home/fmatzkin/Code/datasets/SamCook-FAVO/volumes']

    # volumes_simulated = []

    file_identifiers_vol_r = ['_image_preoplvlsets',
                             '_image_sum_brlvlsets5',
                             '_image_i_brlvlsets5']
    method_names_fl = ['Ground-Truth', 'REC-LS', 'NR-LS']
    cache_name_vol_r = 'volumes_real'
    compare_vol_real = MethodCompare(volumes_real, file_identifiers_vol_r,
                                    method_names_fl, cache_name_vol_r)
    metrics_dict_vol_r = {
        'dice': {'title': 'Dice coefficient', 'yaxis': 'Dice coefficient'},
        'hausdorff': {'title': 'Hausdorff coefficient',
                      'yaxis': 'Hausdorff coefficient'}
    }

    # file_identifiers_vol_s = ['_image_preoplvlsets',
    #                          '_image_sum_brlvlsets5',
    #                          '_image_i_brlvlsets5']
    # cache_name_vol_s = 'volumes_simulated'
    # compare_vol_simulated = MethodCompare(volumes_simulated,
    #                                      file_identifiers_vol_s,
    #                                      method_names_fl, cache_name_vol_s)
    # metrics_dict_vol_s = {
    #     'dice': {'title': 'Dice coefficient', 'yaxis': 'Dice coefficient'},
    #     'hausdorff': {'title': 'Hausdorff coefficient',
    #                   'yaxis': 'Hausdorff coefficient'}}

    compare_vol_real.load_stats_and_plot(metrics_dict_vol_r)  # DICE/HD
    volumes_flaps(flaps_real, flaps_simulated, file_identifiers_fl_r,
                  file_identifiers_fl_s, method_names_fl, abc_csv_p,
                  cached_sim_p,
                  cached_real_p)  # FLAPS - SIMULATED + REAL - Volume scatterplot

    plt.show()













    # flaps_real = ['../image/all/clip90-91_sp2-2-2-rigid/cr_gt',
    #               '../image/all/clip90-91_sp2-2-2-rigid/pred_PCA',
    #               '../image/all/clip90-91_sp2-2-2-rigid/pred_a_CR_AE_200302_800_1e-4_dice_bz9',
    #               '../image/all/clip90-91_sp2-2-2-rigid/pred_a_CR_200302_800_1e-4_dice_bz9_ep350',
    #               '../image/all/clip90-91_sp2-2-2-rigid/pred_a_FRUnet_200303_1000_1e-4_dice_bz9_ep350']
    # flaps_simulated = ['../image/normal/clip90-91_sp2-2-2-rigid/scr200302/pred_a_FRUnet_200303_1000_1e-4_dice_bz9_ep350',
    #                    '../image/normal/clip90-91_sp2-2-2-rigid/scr200302/pred_PCA',
    #                    '../image/normal/clip90-91_sp2-2-2-rigid/scr200302/pred_a_CR_AE_200302_800_1e-4_dice_bz9',
    #                    '../image/normal/clip90-91_sp2-2-2-rigid/scr200302/pred_a_CR_200302_800_1e-4_dice_bz9_ep350',
    #                    '../image/normal/clip90-91_sp2-2-2-rigid/scr200302/pred_a_FRUnet_200303_1000_1e-4_dice_bz9_ep350']

    # skulls_real = ['../image/all/clip90-91_sp2-2-2-rigid/cr_gt',
    #                '../image/all/clip90-91_sp2-2-2-rigid/pred_PCA',
    #                '../image/all/clip90-91_sp2-2-2-rigid/pred_a_CR_AE_200302_800_1e-4_dice_bz9',
    #                '../image/all/clip90-91_sp2-2-2-rigid/pred_a_CR_200302_800_1e-4_dice_bz9_ep350']
    # skulls_simulated = [
    #     '../image/normal/clip90-91_sp2-2-2-rigid/scr200302/pred_a_CR_200302_800_1e-4_dice_bz9_ep350',
    #     '../image/normal/clip90-91_sp2-2-2-rigid/scr200302/pred_PCA',
    #     '../image/normal/clip90-91_sp2-2-2-rigid/scr200302/pred_a_CR_AE_200302_800_1e-4_dice_bz9',
    #     '../image/normal/clip90-91_sp2-2-2-rigid/scr200302/pred_a_CR_200302_800_1e-4_dice_bz9_ep350']

    # # SKULLS - REAL - DICE/HD
    # file_identifiers_sk_r = ['_prev', '_pca', '_reconstr', '_reconstr']
    # method_names_sk_r = ['Ground Truth (full skull)', 'PCA-Full', 'Autoencoder-Full', 'UNet-Full']
    # cache_name_sk_r = 'skulls_real'
    # compare_sk_real = MethodCompare(skulls_real, file_identifiers_sk_r, method_names_sk_r, cache_name_sk_r)
    # metrics_dict_sk_r = {'dice': {'title': 'Dice coefficient', 'yaxis': 'Dice coefficient'},
    #                      'hausdorff': {'title': 'Hausdorff coefficient', 'yaxis': 'Hausdorff coefficient'}}
    #
    # # SKULLS - SIMULATED - DICE/HD
    # file_identifiers_sk_s = ['_groundtruth', '_sim_pca', '_sim_reconstr', '_sim_reconstr']
    # method_names_sk_s = ['Ground Truth (full skull)', 'PCA-Full', 'Autoencoder-Full', 'UNet-Full']
    # cache_name_sk_s = 'skulls_simulated'
    # compare_sk_simulated = MethodCompare(skulls_simulated, file_identifiers_sk_s, method_names_sk_s, cache_name_sk_s)
    # metrics_dict_sk_s = {'dice': {'title': 'Dice coefficient', 'yaxis': 'Dice coefficient'},
    #                      'hausdorff': {'title': 'Hausdorff coefficient', 'yaxis': 'Hausdorff coefficient'}}

    # FLAPS - REAL - DICE/HD
    # file_identifiers_fl_r = ['_diff_clean', '_pca_diff', '_diff', '_diff', '_reconstr']
    # method_names_fl = ['Ground-Truth', 'RS-PCA', 'RS-AE', 'RS-UNet', 'DE-UNet']
    # cache_name_fl_r = 'flaps_real'
    # compare_fl_real = MethodCompare(flaps_real, file_identifiers_fl_r, method_names_fl, cache_name_fl_r)
    # metrics_dict_fl_r = {'dice': {'title': 'Dice coefficient', 'yaxis': 'Dice coefficient'},
    #                      'hausdorff': {'title': 'Hausdorff coefficient', 'yaxis': 'Hausdorff coefficient'}}
    #
    # # FLAPS - SIMULATED - DICE/HD
    # file_identifiers_fl_s = ['_groundtruth', '_sim_pca_diff', '_sim_diff', '_sim_diff', '_sim_reconstr']
    # cache_name_fl_s = 'flaps_simulated'
    # compare_fl_simulated = MethodCompare(flaps_simulated, file_identifiers_fl_s, method_names_fl, cache_name_fl_s)
    # metrics_dict_fl_s = {'dice': {'title': 'Dice coefficient', 'yaxis': 'Dice coefficient'},
    #                      'hausdorff': {'title': 'Hausdorff coefficient', 'yaxis': 'Hausdorff coefficient'}}
    #
    # # FLAPS - SIMULATED + REAL - Volume scatterplot
    # abc_csv_p = '../image/all/clip90-91_sp2-2-2-rigid/abc_test.csv'
    # cached_sim_p = 'figures/cache/flaps_simulated_volumes.P'
    # cached_real_p = 'figures/cache/flaps_real_volumes.P'
    #
    # # FLAPS - REAL - Volume relative errors
    # append_data = {'csv': abc_csv_p, 'metric': 'volumes', 'method_name': 'ABC', 'title': 'Volume relative error',
    #                'yaxis': 'relative error'}
    # cached_volr_f = 'figures/cache/flaps_real_vol_err.P'

    # Test zone
    # compare_sk_real.load_stats_and_plot(metrics_dict_sk_r)  # SKULLS - REAL - DICE/HD
    # compare_sk_simulated.load_stats_and_plot(metrics_dict_sk_s)  # SKULLS - SIMULATED - DICE/HD
    # compare_fl_real.load_stats_and_plot(metrics_dict_fl_r)  # FLAPS - REAL - DICE/HD
    # compare_fl_simulated.load_stats_and_plot(metrics_dict_fl_s)  # FLAPS - SIMULATED - DICE/HD
    # volumes_flaps(flaps_real, flaps_simulated, file_identifiers_fl_r, file_identifiers_fl_s, method_names_fl, abc_csv_p,
    #               cached_sim_p, cached_real_p)  # FLAPS - SIMULATED + REAL - Volume scatterplot
    # vol_errs(flaps_real, file_identifiers_fl_r, method_names_fl, append_data, cache_name_fl_r,
    #          cached_volr_f)  # FLAPS- REAL - Volume relative errors
    #
    # plt.show()

    # ---------------------------
    # flaps_real = ['../image/all/clip90-91_sp2-2-2-rigid/cr_gt',
    #               '../image/all/clip90-91_sp2-2-2-rigid/pred_PCA',
    #               '../image/all/clip90-91_sp2-2-2-rigid/pred_a_CR_AE_200302_800_1e-4_dice_bz9',
    #               '../image/all/clip90-91_sp2-2-2-rigid/pred_a_FRUnet_200303_1000_1e-4_dice_bz9_ep350']
    # flaps_simulated = ['../image/normal/clip90-91_sp2-2-2-rigid/scr200302/pred_a_FRUnet_200303_1000_1e-4_dice_bz9_ep350',
    #                    '../image/normal/clip90-91_sp2-2-2-rigid/scr200302/pred_PCA',
    #                    '../image/normal/clip90-91_sp2-2-2-rigid/scr200302/pred_a_CR_AE_200302_800_1e-4_dice_bz9',
    #                    '../image/normal/clip90-91_sp2-2-2-rigid/scr200302/pred_a_FRUnet_200303_1000_1e-4_dice_bz9_ep350']
    # skulls_real = ['../image/all/clip90-91_sp2-2-2-rigid/cr_gt',
    #                '../image/all/clip90-91_sp2-2-2-rigid/pred_PCA',
    #                '../image/all/clip90-91_sp2-2-2-rigid/pred_a_CR_AE_200302_800_1e-4_dice_bz9',
    #                '../image/all/clip90-91_sp2-2-2-rigid/pred_a_CR_200302_800_1e-4_dice_bz9_ep350']
    # skulls_simulated = [
    #     '../image/normal/clip90-91_sp2-2-2-rigid/scr200302/pred_a_CR_200302_800_1e-4_dice_bz9_ep350',
    #     '../image/normal/clip90-91_sp2-2-2-rigid/scr200302/pred_PCA',
    #     '../image/normal/clip90-91_sp2-2-2-rigid/scr200302/pred_a_CR_AE_200302_800_1e-4_dice_bz9',
    #     '../image/normal/clip90-91_sp2-2-2-rigid/scr200302/pred_a_CR_200302_800_1e-4_dice_bz9_ep350', ]
    #
    # # SKULLS - REAL - DICE/HD
    # file_identifiers_sk_r = ['_prev', '_pca', '_reconstr', '_reconstr']
    # method_names_sk_r = ['Ground Truth (full skull)', 'PCA-Full', 'Autoencoder-Full', 'UNet-Full']
    # cache_name_sk_r = 'skulls_real'
    # compare_sk_real = MethodCompare(skulls_real, file_identifiers_sk_r, method_names_sk_r, cache_name_sk_r)
    # metrics_dict_sk_r = {'dice': {'title': 'Dice coefficient', 'yaxis': 'Dice coefficient'},
    #                      'hausdorff': {'title': 'Hausdorff coefficient', 'yaxis': 'Hausdorff coefficient'}}
    #
    # # SKULLS - SIMULATED - DICE/HD
    # file_identifiers_sk_s = ['_groundtruth', '_sim_pca', '_sim_reconstr', '_sim_reconstr']
    # method_names_sk_s = ['Ground Truth (full skull)', 'PCA-Full', 'Autoencoder-Full', 'UNet-Full']
    # cache_name_sk_s = 'skulls_simulated'
    # compare_sk_simulated = MethodCompare(skulls_simulated, file_identifiers_sk_s, method_names_sk_s, cache_name_sk_s)
    # metrics_dict_sk_s = {'dice': {'title': 'Dice coefficient', 'yaxis': 'Dice coefficient'},
    #                      'hausdorff': {'title': 'Hausdorff coefficient', 'yaxis': 'Hausdorff coefficient'}}
    #
    # # FLAPS - REAL - DICE/HD
    # file_identifiers_fl_r = ['_diff_clean', '_pca_diff', '_diff', '_reconstr']
    # method_names_fl = ['Ground Truth (flap)', 'PCA-Full (diff)', 'Autoencoder-Full (diff)', 'UNet-Flap']
    # cache_name_fl_r = 'flaps_real'
    # compare_fl_real = MethodCompare(flaps_real, file_identifiers_fl_r, method_names_fl, cache_name_fl_r)
    # metrics_dict_fl_r = {'dice': {'title': 'Dice coefficient', 'yaxis': 'Dice coefficient'},
    #                      'hausdorff': {'title': 'Hausdorff coefficient', 'yaxis': 'Hausdorff coefficient'}}
    #
    # # FLAPS - SIMULATED - DICE/HD
    # file_identifiers_fl_s = ['_groundtruth', '_sim_pca_diff', '_sim_diff', '_sim_reconstr']
    # cache_name_fl_s = 'flaps_simulated'
    # compare_fl_simulated = MethodCompare(flaps_simulated, file_identifiers_fl_s, method_names_fl, cache_name_fl_s)
    # metrics_dict_fl_s = {'dice': {'title': 'Dice coefficient', 'yaxis': 'Dice coefficient'},
    #                      'hausdorff': {'title': 'Hausdorff coefficient', 'yaxis': 'Hausdorff coefficient'}}
    #
    # # FLAPS - SIMULATED + REAL - Volume scatterplot
    # abc_csv_p = '../image/all/clip90-91_sp2-2-2-rigid/abc_test.csv'
    # cached_sim_p = 'figures/cache/flaps_simulated_volumes.P'
    # cached_real_p = 'figures/cache/flaps_real_volumes.P'
    #
    # # FLAPS - REAL - Volume relative errors
    # append_data = {'csv': abc_csv_p, 'metric': 'volumes', 'method_name': 'ABC', 'title': 'Volume relative error',
    #                'yaxis': 'relative error'}
    # cached_volr_f = 'figures/cache/flaps_real_vol_err.P'
    #
    # # Test zone
    # # compare_sk_real.load_stats_and_plot(metrics_dict_sk_r)  # SKULLS - REAL - DICE/HD
    # # compare_sk_simulated.load_stats_and_plot(metrics_dict_sk_s)  # SKULLS - SIMULATED - DICE/HD
    # # compare_fl_real.load_stats_and_plot(metrics_dict_fl_r)  # FLAPS - REAL - DICE/HD
    # # compare_fl_simulated.load_stats_and_plot(metrics_dict_fl_s)  # FLAPS - SIMULATED - DICE/HD
    # # volumes_flaps(flaps_real, flaps_simulated, file_identifiers_fl_r, file_identifiers_fl_s, method_names_fl, abc_csv_p,
    # #               cached_sim_p, cached_real_p)  # FLAPS - SIMULATED + REAL - Volume scatterplot
    # vol_errs(flaps_real, file_identifiers_fl_r, method_names_fl, append_data, cache_name_fl_r,
    #          cached_volr_f)  # FLAPS- REAL - Volume relative errors
    #
    # plt.show()
