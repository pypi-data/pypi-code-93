# SonusAI Utilities for Metrics and Model Training and Validation
import h5py
import numpy as np

from tensorflow.keras.models import Model


def cmmetrics(cmall, bmode=True):
    # Calculates metrics from a confusion matrix of nclass x nclass or
    # sets of cm S1 x S2 x ... x nclass x nclass where the sum is taken over
    # all the other dimensions and metrics are calculated on this sum.
    #
    # bmode sets binary mode where if True and nclass=2 then only the last (-1)
    # dimension of metrics is returned (the positive metrics), i.e. a 1x10 array.
    #
    # Returns:
    # metrics  nclass x 10       [ACC, TPR, PPV, TNR, FPR, HITFA, F1, MCC, NT, PT, TP, FP]
    # cmsum    nclass x nclass   Sum of all sum counts

    if cmall.shape[-1] != cmall.shape[-2]:
        print('Error: confusion matrix must be a square matrix.')
        exit()

    nclass = cmall.shape[-1]
    ndimsum = np.ndim(cmall) - 2
    if ndimsum == 0:
        cmsum = cmall
    else:
        dsi = tuple([i for i in range(0, cmall.ndim - 2)])
        cmsum = np.sum(cmall, dsi)  # sum over all dims except -2,-1

    # If binary, drop dim0 stats which are redundant
    # if nclass == 1:
    #     mcm = mcm[1:, :, :]

    metrics = np.zeros((nclass, 12))
    mcm = np.zeros((nclass, 2, 2))
    TC = np.sum(np.sum(cmsum))
    eps = np.finfo(float).eps

    for nci in range(nclass):
        mcm[nci, 1, 1] = cmsum[nci, nci]  # TP True positive
        mcm[nci, 1, 0] = np.sum(cmsum[nci, :]) - mcm[nci, 1, 1]  # FN False negative = true but predicted negative
        mcm[nci, 0, 1] = np.sum(cmsum[:, nci]) - mcm[nci, 1, 1]  # FP False positive
        mcm[nci, 0, 0] = TC - np.sum(mcm[nci, :, :])  # TN True negative = false and predicted negative
        # True negative
        TN = mcm[nci, 0, 0]
        # False positive
        FP = mcm[nci, 0, 1]
        # False negative
        FN = mcm[nci, 1, 0]
        # True positive
        TP = mcm[nci, 1, 1]
        # Accuracy
        ACC = (TP + TN) / (TP + TN + FP + FN + eps)
        # True positive rate, sensitivity, recall, hit rate (note eps in numerator)
        # When ``true positive + false negative == 0``, recall is undefined, set to 0
        TPR = (TP) / (TP + FN + eps)
        # Precision, positive predictive value
        # When ``true positive + false positive == 0``, precision is undefined, set to 0
        PPV = TP / (TP + FP + eps)
        # Specificity i.e., selectivity, or true negative rate
        TNR = TN / (TN + FP + eps)
        # False positive rate = 1-specificity, roc x-axis
        FPR = FP / (TN + FP + eps)
        # HitFA used by some separation research, close match to MCC
        HITFA = TPR - FPR
        # F1 harmonic mean of precision, recall = 2*PPV*TPR / (PPV + TPR)
        F1 = 2 * TP / (2 * TP + FP + FN + eps)
        # Matthew correlation coefficient
        MCC = (TP * TN - FP * FN) / (np.sqrt((TP + FP) * (TP + FN) * (TN + FP) * (TN + FN)) + eps)
        # Num. negatives total (truth), also = TN+FP denom of FPR
        NT = sum(mcm[nci, 0, :])
        # Num. positives total (truth), also = FN+TP denom of TPR, precision
        PT = sum(mcm[nci, 1, :])
        metrics[nci] = [ACC, TPR, PPV, TNR, FPR, HITFA, F1, MCC, NT, PT, TP, FP]

    if nclass == 2 and bmode:
        # If binary, drop dim0 stats which are redundant
        mcm = mcm[1:, :, :]
        metrics = metrics[1:, :]

    return metrics, mcm, cmsum


def metricsavg(metrics):
    # compute metric averages for several averaging methods over clsasses.
    # for binary these have no meaning macro-avg == statistics of pos. class
    # mavg[0,:]  macro-avg  [PPV, TPR, F1, FPR, ACC, TPSUM]
    # mavg[1,:]  micro-avg  [PPV, TPR, F1, FPR, ACC, TPSUM]  # Note, PPV=TPR=F1=ACC
    # mavg[2,:]  weight-avg [PPV, TPR, F1, FPR, ACC, TPSUM]
    eps = np.finfo(float).eps
    NC = np.shape(metrics)[0]  # num classes, assumes cm is proper square shape
    mavg = np.zeros((3, 6), 'float32')
    s = np.sum(metrics[:, 9].astype(int))  # support = sum (true pos total = FN+TP ) over classes
    # macro average
    mavg[0, :] = [np.mean(metrics[:, 2]), np.mean(metrics[:, 1]), np.mean(metrics[:, 6]),
                  np.mean(metrics[:, 4]), np.mean(metrics[:, 0]), s]
    # micro average, micro-F1 = micro-precision = micro-recall = accuracy
    if NC > 1:
        tp_sum = np.sum(metrics[:, 10])  # TP all classes
        rm = tp_sum / (np.sum(metrics[:, 9]) + eps)  # micro mean PPV = TP / (PT=FN+TP)
        fp_sum = np.sum(metrics[:, 11])  # FP all classes
        fpm = fp_sum / (np.sum(metrics[:, 8]) + eps)  # micro mean FPR = FP / (NT=TN+FP)
        # pm  = tp_sum / (tp_sum + fp_sum + eps)      # micro mean TPR = TP / (TP+FP) (note: same as rm for micro-avg)
        mavg[1, :] = [rm, rm, rm, fpm, rm, s]  # specific format, last 3 are unique
        # weighted average TBD
        # mavg[2,:] =
    else:  # binary case, all are same
        mavg[1, :] = mavg[0, :]
        mavg[2, :] = mavg[0, :]

    return mavg


def ohmetrics(truth, pred, pthrmode=0, nclass=-1):
    from sklearn.metrics import confusion_matrix

    # Calculates metrics from one-hot prediction and truth data where input
    # is one-hot probabilities for each clase with size frames x nclasses or 
    # frames x timesteps x nclasses.
    #
    # nclass is inferred from truth dims by default (nclass=-1).  Only set
    # in case of binary 2-dim input FxT with timestep, then must set nclass=1.
    # 
    # returns metrics over all frames+timesteps:
    # mcm      nclass x 2 x 2    multiclass confusion matrix count ove
    # metrics  nclass x 10       [ACC, TPR, PPV, TNR, FPR, HITFA, F1, MCC, NT, PT, TP, FP]
    # cm, cmn: nclass x nclass   confusion matrix, normalized confusion matrix
    # rmse:    nclass x 1        root mean sq err over all frames+timesteps

    # eps = np.finfo(float).eps

    if truth.shape != pred.shape:
        print('Error: shape of truth and pred are not equal.')
        exit()

    # truth,pred can be either frames x nclass, or frames x tstep x nclass
    # in binary case, nclass == 1 and dim may not exist
    if truth.ndim == 3 or (truth.ndim == 2 and nclass == 1):  # flatten
        # F = truth.shape[0]
        # tsteps = truth.shape[1]
        if truth.ndim == 2:
            nclass = 1
        else:
            nclass = truth.shape[2]

        truth = np.reshape(truth, (truth.shape[0] * truth.shape[1], truth.shape[2]))
        pred = np.reshape(pred, (pred.shape[0] * pred.shape[1], pred.shape[2]))
    else:
        # F = truth.shape[0]
        # tsteps = 0
        if truth.ndim == 1:
            nclass = 1
        else:
            nclass = truth.shape[1]

    rmse = np.sqrt(np.mean(np.square(truth - pred), axis=0))

    if pthrmode == 0 and nclass > 1:
        pthr = 0.5  # multiclass, singlelabel (argmax) or multilabel case default
    else:
        if nclass == 1 and pthrmode == 0:
            pthr = 0.5  # binary case default >= 0.5 which is equiv to argmax()
        else:
            pthr = pthrmode  # any case using specified threshold

    # Convert continuous probabilities to binary via argmax() or thr comparison
    # and create labels of int encoded (0:nclass-1), and then equiv. one-hot
    if nclass == 1:  # If binary
        bmode = True
        labels = ([i for i in range(0, 2)])  # int encoded 0,1
        plabel = np.int8(pred >= pthr)  # Fx1, default 0.5 is equiv. to argmax()
        tlabel = np.int8(truth >= pthr)  # Fx1
        predb = plabel
        truthb = tlabel
    else:
        bmode = False
        labels = ([i for i in range(0, nclass)])  # int encoded 0,...,nclass-1
        if pthrmode == 0:  # multiclass, use argmax (i.e. single label mutex)
            plabel = np.argmax(pred, axis=-1)  # Fx1 labels
            tlabel = np.argmax(truth, axis=-1)  # Fx1 labels
            predb = np.zeros(pred.shape, dtype=np.int8)  # FxC one-hot binary
            truthb = np.zeros(truth.shape, dtype=np.int8)  # FxC one-hot binary
            predb[np.arange(predb.shape[0]), plabel] = 1
            truthb[np.arange(truthb.shape[0]), tlabel] = 1
        else:  # multiclass prob threshold comparison (i.e. multi-label)
            plabel = np.int8(pred >= pthr)  # FxC multilabel oh decision
            tlabel = np.int8(truth >= pthr)  # FxC multilabel oh decision

    # Create nclass x nclass normalized confusion matrix
    cmn = confusion_matrix(tlabel, plabel, labels=labels, normalize='true')

    # Create nclass x nclass confusion matrix
    cm = confusion_matrix(tlabel, plabel, labels=labels)

    (metrics, mcm, _) = cmmetrics(cm, bmode)

    return mcm, metrics, cm, cmn, rmse


def print_mccm(f, cm, norm=0):
    # Print to file handle f confusion matrix
    # if norm is 0 (default) then print standard non-normalized cm, else 
    # if 1 or non-zero for normalized cm 
    NC = np.shape(cm)[0]  # num classes, assumes cm is proper square shape
    RC = np.sum(cm, 1)  # Row count for normalized cm, if requested
    TC = np.sum(RC)  # total count

    if norm == 0:
        print('Confusion Matrix with nclass, total count: {},{}:'.format(NC, TC), file=f)
        with np.printoptions(suppress=True):
            print('{}'.format(cm.astype(int)), file=f)
    else:
        eps = np.finfo(float).eps
        normv = (np.tile(np.reshape(RC, (NC, 1)), (1, NC)) + eps)
        ncm = cm / normv  # element by element
        print('Normalized Confusion Matrix (%) with nclass, total count: {},{}:'.format(NC, TC), file=f)
        with np.printoptions(precision=2, suppress=True):
            print('{}'.format(np.round(ncm * 100, 0).astype(int)), file=f)

    return


def print_metricsummary(metrics, target_names=None, per_class=1, digits=2):
    # Print  metric summary into string var report, where simplest usage is
    # print(print_metricsummary(metrics))
    #                 PPV     TPR      f1     FPR     ACC  csupport
    #     Class 1     0.71    0.80    0.75    0.00    0.99      44
    #     Class 2     0.90    0.76    0.82    0.00    0.99     128
    #     Class 3     0.86    0.82    0.84    0.04    0.93     789
    #     Class 4     0.94    0.96    0.95    0.18    0.92    2807
    #
    # micro-avg                            0.027    0.92    3768
    # macro avg     0.85    0.83    0.84    0.05    0.96    3768
    #
    # metrics is data from cmmmetrics() that calcs confusion matrices.
    # If per_class != 0 (default) then print metrics per class in addition
    # to a total summary at the end (mean over classes).
    # Set to 0 to disable this and print only all-class average summary.
    NC = np.shape(metrics)[0]  # num classes, assumes metrics is from cmmetrics()

    if target_names is None or len(target_names) != NC:
        # target_names = ['%s' % l for l in labels]
        target_names = ([f'Class {i}' for i in range(1, NC + 1)])

    # format from sklearn,  headers = ["precision", "recall", "f1-score", "support"]
    headers = ["PPV", "TPR", "f1", "FPR", "ACC", "support"]
    p = metrics[:, 2]
    r = metrics[:, 1]
    fpr = metrics[:, 4]
    f1 = metrics[:, 6]
    acc = metrics[:, 0]
    s = metrics[:, 9].astype(int)
    rows = zip(target_names, p, r, f1, fpr, acc, s)

    longest_last_line_heading = 'weighted avg'
    name_width = max(len(cn) for cn in target_names)
    width = max(name_width, len(longest_last_line_heading), digits)
    head_fmt = '{:>{width}s} ' + ' {:>7}' * len(headers)
    report = head_fmt.format('', *headers, width=width)
    report += '\n'
    row_fmt = '{:>{width}s} ' + ' {:>7.{digits}f}' * 5 + ' {:>7}\n'
    for row in rows:
        report += row_fmt.format(*row, width=width, digits=digits)
    report += '\n'

    if NC > 1:  # Binary does not require average
        # compute averages, all options are average_options = ('micro', 'macro', 'weighted', 'samples')
        average_options = ('micro', 'macro')  # TBD 
        micro_is_accuracy = True
        mavg = metricsavg(metrics)  # [PPV, TPR, F1, FPR, ACC, TPSUM]
        for average in average_options:
            if average.startswith('micro') and micro_is_accuracy:
                line_heading = 'micro-avg'
            else:
                line_heading = average + ' avg'

            # compute averages with specified averaging method
            if average == 'macro':
                idx = 0
                # [np.mean(p), np.mean(r), np.mean(f1), np.mean(fpr), np.mean(acc), np.sum(s)]
                avg = [mavg[idx, 0], mavg[idx, 1], mavg[idx, 2],
                       mavg[idx, 3], mavg[idx, 4], mavg[idx, 5].astype(int)]
            elif average == 'micro':
                # micro-mode : micro-F1 = micro-precision = micro-recall = accuracy
                idx = 1
                avg = [mavg[idx, 0], mavg[idx, 1], mavg[idx, 2],
                       mavg[idx, 3], mavg[idx, 4], mavg[idx, 5].astype(int)]
            elif average == 'weighted':
                avg = mavg[2, :]  # TBD

            if line_heading == 'micro-avg':
                row_fmt_accuracy = '{:>{width}s} ' + \
                                   ' {:>7.{digits}}' * 4 + ' {:>7.{digits}f}' + \
                                   ' {:>7}\n'
                report += row_fmt_accuracy.format(line_heading, '', '', '',
                                                  *avg[3:], width=width,
                                                  digits=digits)
            else:
                report += row_fmt.format(line_heading, *avg,
                                         width=width, digits=digits)

    # if per_class!=0:
    #     print('Metrics summary per class:')
    #     with np.printoptions(precision=2, suppress=True):
    #         print('ACC(%): {}'.format(np.round(metrics[:,0]*100,0).astype(int)),file=f)
    #         print('TPR(%): {}'.format(np.round(metrics[:,1]*100,0).astype(int)),file=f)
    #         print('PPV(%): {}'.format(np.round(metrics[:,2]*100,0).astype(int)),file=f)
    #         print('FPR(%): {}'.format(np.round(metrics[:,4]*100,0).astype(int)),file=f)                                    
    #         print('F1    : {}'.format(np.round(metrics[:,5],2)),file=f)
    #         print('MCC   : {}'.format(np.round(metrics[:,6],2)),file=f)

    return report


def print_cm(cm, labels=None):
    # print confusion matrix from float variable cm and optional labels list
    str = '{}\n'.format(cm.astype(int))  # TBD just print as int (trunc)

    return str


def print_metsnrsummary(mstat, smetrics, snrfloat, tasnridx):
    # print metric summary for each SNR
    # mstat:    config params like target snr, levels, etc. [NNF, NTF, NSNR, NAUG, 23]
    # smetrics: metric data summed by SNR, must be shape [NSNR, NCLASS, 12]
    # snrfloat: snr values for each NSNR dim in mstat & metsnr
    # tasnridx: index into snrfloat sorted (i.e. for highest to lowest snr)
    #
    # mstat fields:
    # [mi, tsnr, ssnrmean, ssnrmax, ssnrpk80, tgain, metrics[tridx,12], TN, FN, FP, TP, rmse[tridx]
    # metsnr fields: ACC, TPR, PPV, TNR, FPR, HITFA, F1, MCC, NT, PT, TP, FP]

    NNF, NTF, NSNR, NAUG, _ = mstat.shape
    NMIX = NNF * NTF * NSNR * NAUG
    NCLASS = smetrics.shape[1]

    str = '--- NN Performance over {} mixtures per Global SNR ---\n'.format(NMIX / NSNR)
    str = str + '| SNR |  PPV% |  TPR% |  F1%  |  FPR% |  ACC% | SgSNRavg | SgSNR80p |\n'
    for si in range(NSNR):
        snri = tasnridx[si]
        tmpif = np.isfinite(mstat[:, :, snri, :, 2])
        mssnravg = np.mean(mstat[:, :, snri, :, 2][tmpif])  # mean segmsnr, unweighted avg, ignoring nans
        tmpif = np.isfinite(mstat[:, :, snri, :, 4])
        segsnr80pc = np.mean(mstat[:, :, snri, :, 4][tmpif])  # segmsnr80pc, unweighted avg, ignoring nans
        metavg = metricsavg(smetrics[snri, :, :])  # multiclass uses class averages
        # metavg fields: [PPV, TPR, F1, FPR, ACC, TPSUM]
        str = str + '| {:+3.0f} | {:5.1f} | {:5.1f} | {:5.1f} | {:5.1f} | {:5.1f} |   {:+3.0f}    |   {:+3.0f}    |\n'.format(
            max(min(round(mstat[0, 0, snri, 0, 1]), 99), -99),  # target snr, should be same all mixtures
            metavg[0, 0] * 100,  # PPV macro avg
            metavg[0, 1] * 100,  # TPR macro avg
            metavg[0, 2] * 100,  # F1 macro avg
            metavg[1, 3] * 100,  # FPR micro avg
            metavg[1, 4] * 100,  # ACC micro-avg = F1 micro-avg = PPV micro-avg = TPR micro-avg
            max(min(round(mssnravg), 99), -99),  # mean segsnr avg over mixtures
            max(min(round(segsnr80pc), 99), -99))  # segsnr 80th percentile avg over mixutres

    if NCLASS > 1:
        str = str + 'PPV,TPR,F1 are macro-avg, FPR, ACC are micro-avg over {:>6} classes.\n'.format(NCLASS)

    return str


def calc_cweights(truth, oweight=-1, oweight_idx=-1):
    # Calculate class weights with support for non-existent classes (a problem with sklearn)
    # where non-existent class gets a weight of 0 (instead of inf)
    # Includes optional weighting of an "other" class if specified
    # ref: cweights = class_weight.compute_class_weight(class_weight='balanced', classes=clabels, y=tlabels)
    # Inputs:
    #   truth    size FxTSxNCL or FxNCL truth data in one-hot format
    #   oweight  weight of the "other" class
    #            >1 will increase weighting/importance relative to the true count
    #            0>oweight<1 will decrease weighting/importance relative
    #            <0 disable, use true count (default = -1)
    #   oweight_idx index of other class in one-hot mode, default = NCL-1 (the last)
    from numpy import inf

    (F, NCL) = truth.shape

    if NCL > 1:
        # clabels = list(range(0,NCL))            # NCLASS labels 0:nclass-1
        tlabels = np.argmax(truth, axis=-1)  # Fx1 labels from one-hot, last dim
        cnt = np.bincount(tlabels, minlength=NCL).astype(float)
    else:
        # clabels = list(range(0,2))        # [0,1] binary case
        NCL = 2
        tlabels = np.int8(truth >= 0.5)[:, 0]  # quantize to binary and shape (F,) for bincount
        cnt = np.bincount(tlabels, minlength=NCL).astype(float)

    if oweight > 0:
        if oweight_idx < 0:
            oweight_idx = NCL - 1  # default to last class        
        cnt[oweight_idx] = cnt[oweight_idx] / oweight

    cweights = F / (NCL * cnt)  # avoid sklearn problem with absent classes
    cweights[cweights == inf] = 0  # just assign non-existent class weight of 0 

    return cweights


def calc_sweights(cweights, truth):
    # Calculate sample_weight from class weights and a given truth with 2D or 3D shape 
    # Supports one-hot encoded multi-class or binary truth/labels
    # Note returns sum of weighted truth over classes, thus should also work for multi-label ? TBD
    # Inputs:
    #   cweights NCx1 weights for each class
    #   truth    BSxNTxNC or BSxNC (no timesteps) where BS=batch_size, TS=tsteps
    # Returns:
    #   sweights BSxNTx1 or (BS,)
    ts = truth.shape
    cs = cweights.shape

    if ts[-1] == 1 and cs[0] == 2:  # Binary truth needs 2nd "none" truth dimension
        truth = np.concatenate((truth, 1 - truth), axis=1)

    sweights = np.sum(cweights * truth, axis=-1)  # broadcast NCx1 over BSxNC or BSxNTxNC
    return sweights


def reshape_inputs(feature, truth, batch_size, tstep=0, flatten=False, add1ch=False):
    # Check sonusai feature and truth data and reshape feature of size FxSxB into
    # one of several options:
    # If timestep > 0: (i.e. for recurrent NNs):
    #   no-flatten, no-channel (keep 2D feature)   sequences x tsteps x S   x B     (4-dim)
    #   flatten, no-channel:                       sequences x tsteps x B*S         (3-dim)
    #   no-flatten, add-1channel:                  sequences x tsteps x S   x B x 1 (5-dim)
    #   flatten, add-1channel:                     sequences x tsteps x B*S x 1     (4-dim)
    #
    # If timestep == 0, then do not add tstep dimension
    #
    # The # samples are trimmed to be a multiple of batch_size (Keras requirement), for
    # both feature, truth.
    # Channel is added to last/outer dimension for channel_last support in Keras/TF
    #
    # Returns:
    #   f, t,       reshaped feature and truth ()
    #   in_shape    input shape for model (tsteps x feature)
    #   NCL         number of classes in truth = output length of nn model
    #   cweights    weights of each class in truth, per sklearn compute_weights()
    #   str         string with report with info on data and operations done
    # 
    # from sklearn.utils import class_weight

    f = feature
    t = truth

    (F, S, B) = f.shape
    (Ft, NCL) = t.shape
    if F != Ft:  # Double-check correctness of input file(s)
        str = 'Frames in feature and truth do not match, exiting ...\n'
        exit()
    else:
        str = 'Training/truth shape: {}x{}x{}, nclass/outlen = {}\n'.format(F, S, B, NCL)
        str = str + 'Reshape request: tsteps {}, batchsize {}, flatten={}, add1ch={}\n'.format(
            tstep, batch_size, flatten, add1ch)

    # Compute class weights by hand as sklearn does not handle non-existent classes
    cweights = calc_cweights(t)

    # calc new input shape only and return
    if batch_size == -1:
        if flatten:
            in_shape = [S * B]
        else:
            in_shape = [S, B]

        if tstep > 0:
            in_shape = np.concatenate(([tstep], in_shape[0:]), axis=0)

        if add1ch:
            in_shape = np.concatenate((in_shape[0:], [1]), axis=0)

        return f, t, in_shape, NCL, cweights, str  # quick

    if flatten:
        str = str + 'Flattening {}x{} feature to {}\n'.format(S, B, S * B)
        f = np.reshape(f, (F, S * B))

    # Reshape for Keras/TF recurrent models that require timestep/sequence length dimension
    if tstep > 0:
        sequences = F // tstep

        # Remove frames if remainder, not fitting into a multiple of new # sequences
        frem = F % tstep
        brem = (F // tstep) % batch_size
        bfrem = brem * tstep
        sequences = sequences - brem
        fr2drop = frem + bfrem
        if fr2drop:
            str = str + 'Dropping {} frames for new # of sequences to fit in multiple of batch_size\n'.format(fr2drop)
            if f.ndim == 2:
                f = f[0:-fr2drop, :]  # Flattened input
            elif f.ndim == 3:
                f = f[0:-fr2drop, :, :]  # Un-flattened input

            t = t[0:-fr2drop, :]

        # Do the reshape
        str = str + 'Reshape for timestep = {}, new # of sequences (batches) = {}\n'.format(tstep, sequences)
        if f.ndim == 2:  # Flattened input
            # str=str+'Reshaping 2 dim\n'
            f = np.reshape(f, (sequences, tstep, S * B))  # was frames x B*T
            t = np.reshape(t, (sequences, tstep, NCL))  # was frames x nclass
        elif f.ndim == 3:  # Unflattened input
            # str=str+'Reshaping 3 dim\n'
            f = np.reshape(f, (sequences, tstep, S, B))  # was frames x B x T
            t = np.reshape(t, (sequences, tstep, NCL))  # was frames x nclass
    else:
        # Drop frames if remainder, not fitting into a multiple of new # sequences (Keras req)
        fr2drop = f.shape[0] % batch_size
        if fr2drop > 0:
            str = str + 'Dropping {} frames for total to be a multiple of batch_size\n'.format(fr2drop)
            f = f[0:-fr2drop, ]
            t = t[0:-fr2drop, ]

    # Add channel dimension if required for input to model (i.e. for cnn type input)
    if add1ch:
        # str=str+'Adding channel dimension to feature\n'
        f = np.expand_dims(f, axis=f.ndim)  # add as last/outermost dim

    in_shape = f.shape
    in_shape = in_shape[1:]  # remove frame dim size

    str = str + 'Feature final shape: {}\n'.format(f.shape)
    str = str + 'Input shape final (includes timesteps): {}\n'.format(in_shape)
    str = str + 'Truth final shape: {}\n'.format(t.shape)
    return f, t, in_shape, NCL, cweights, str


def version():
    import subprocess
    proc = subprocess.Popen(['sonusai-version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf8')
    ver = proc.communicate()[0].rstrip()
    return 'sonusai version {}'.format(ver)


def trim_docstring(docstring):
    from sys import maxsize

    if not docstring:
        return ''

    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count)
    indent = maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off leading blank lines:
    while trimmed and not trimmed[0]:
        trimmed.pop()
    # Return a single string
    return '\n'.join(trimmed)


def read_feature_data(filename):
    import json
    with h5py.File(name=filename, mode='r') as f:
        feature_data = {'config': json.loads(f.attrs['config']),
                        'feature': np.array(f['feature']),
                        'feature_samples': np.array(f['feature_samples']),
                        'mixture_database': json.loads(f.attrs['mixture_database']),
                        'noise_augmentations': json.loads(f.attrs['noise_augmentations']),
                        'noise_files': json.loads(f.attrs['noise_files']),
                        'segsnr': np.array(f['segsnr']),
                        'target_augmentations': json.loads(f.attrs['target_augmentations']),
                        'target_files': json.loads(f.attrs['target_files']),
                        'truth': np.array(f['truth'])
                        }

        if 'mixture' in f.keys():
            feature_data['mixture'] = np.array(f['mixture'])

        if 'target' in f.keys():
            feature_data['target'] = np.array(f['target'])

        if 'noise' in f.keys():
            feature_data['noise'] = np.array(f['noise'])

        return feature_data


def sonus_onnx(model: Model, name: str = 'model', file_pfx: str = '', is_flattened: bool = True, has_timestep: bool = True,
               has_channel: bool = False, is_mutex: bool = True):
    # Create onnx model from keras model and write onnx model file if file_pfx provided.
    #   model           keras model
    #   name            model name
    #   file_pfx        filename prefix to save onnx model (do not save if empty)
    #   is_flattened    model feature data is flattened
    #   has_timestep    model has timestep dimension
    #   has_channel     model has channel dimension
    #   is_mutex        model label output is mutually exclusive
    import keras2onnx

    output_str = ''

    # convert to onnx model
    onnx_model = keras2onnx.convert_keras(model, name, debug_mode=True)

    # Replace stateful GRUs with custom layers
    from tensorflow.keras.layers import GRU
    stateful_gru_names = []
    for i in range(len(model.layers)):
        layer = model.layers[i]
        if isinstance(layer, GRU):
            if layer.stateful:
                stateful_gru_names.append(layer.name)

    for i in range(len(onnx_model.graph.node)):
        node = onnx_model.graph.node[i]
        if node.name in stateful_gru_names:
            node.op_type = 'DeepCpuGruStateful'

    # Add metadata to model
    f_flag = onnx_model.metadata_props.add()
    f_flag.key = 'is_flattened'
    f_flag.value = str(is_flattened)

    t_flag = onnx_model.metadata_props.add()
    t_flag.key = 'has_timestep'
    t_flag.value = str(has_timestep)

    c_flag = onnx_model.metadata_props.add()
    c_flag.key = 'has_channel'
    c_flag.value = str(has_channel)

    m_flag = onnx_model.metadata_props.add()
    m_flag.key = 'is_mutex'
    m_flag.value = str(is_mutex)

    # save the model in ONNX format
    if file_pfx != '':
        file_name = file_pfx + '.onnx'
        output_str = 'onnx model saved to {}'.format(file_name)
        keras2onnx.save_model(onnx_model, file_name)

    return onnx_model, output_str
