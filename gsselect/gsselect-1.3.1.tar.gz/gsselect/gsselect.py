#!/usr/bin/env python

# Pick Gemini guide stars
# Python version of gsselect.pro
# Bryan Miller

from __future__ import print_function
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import use as pltuse
import astropy.units as u
import astropy.io.fits as pyfits
from astropy.io.votable import parse_single_table
from astropy.coordinates import SkyCoord
from astropy.modeling import rotations
from astropy.wcs import WCS
import re

# local scripts
from gsselect.inpoly import inpoly
from gsselect.gemcats import gemdssfile, gemgstable


def rlimits(inst, wfs, site, verbose=False):

    """
    Radius limits for guide star searches

    Parameters
        inst:       Instrument ['GMOS-S','F2']
        wfs:        Wavefront sensor ['OIWFS', 'PWFS1', 'PWFS2']
        site:       Gemini site ['N','S','mko','cpo'], not currently used, for backwards compatibility
        verbose     Verbose output?

    Return
        rmin [arcmin]
        rmax [arcmin]
    """

    rmin = 0.0
    rmax = 0.0

    # oimin = {'GMOS-N': 0.33, 'GMOS-S': 0.33, 'F2':0.33, 'GNIRS': 0.2}
    # oimax = {'GMOS-N': 4.8, 'GMOS-S': 4.8, 'F2':3.75, 'GNIRS': 1.5}
    oimin = {'GMOS-N': 0.33, 'GMOS-S': 0.33, 'F2': 0.33}
    oimax = {'GMOS-N': 4.8, 'GMOS-S': 4.8, 'F2': 3.75}

    p2min = {'GMOS-N': 5.3, 'GMOS-S': 5.3, 'F2': 5.3, 'GNIRS': 4.8, 'NIFS': 4.0,
             'NIRIF/6': 5.2, 'NIRIF/14': 4.8, 'NIRIF/32': 4.3}
    p1min = {'GMOS-N': 5.8, 'GMOS-S': 5.8, 'F2': 5.8, 'GNIRS': 5.0, 'NIFS': 4.8,
             'NIRIF/6': 5.7, 'NIRIF/14': 5.3, 'NIRIF/32': 4.8}
    pmax = 6.9

    if wfs == 'OIWFS':
        try:
            rmin = oimin[inst]
            rmax = oimax[inst]
        except Exception:
            if verbose:
                print('Only GMOS-N, GMOS-S, and F2 have supported OIs.')
    elif wfs == 'PWFS2':
        rmin = p2min[inst]
        rmax = pmax
    elif wfs == 'PWFS1':
        rmin = p1min[inst]
        rmax = pmax

    return rmin, rmax


def maglimits(inst, wfs, site, iq, cc, sb, verbose=False):
    """
    Magnitude correction for conditions

    Parameters
        inst:       Instrument ['GMOS', 'F2']
        wfs:        Wavefront sensor ['OIWFS', 'PWFS1', 'PWFS2']
        site:       Gemini site ['N', 'S', 'mko', 'cpo']
        iq:         Image quality constraint ['20', '70', '85', 'Any']
        cc:         Cloud cover constraint [0.0, -0.3, -1.0, -3.0]
        sb:         Sky brightness constraint ['20', '50', '80', 'Any']
        verbose     Verbose output?

    Return
        magbright
        mangmax
    """

    magbright = 9999.
    magfaint = 9999.

    # limiting magnitudes are r-band except GNIRS OI (K-band)
    # oifaint = {'GMOS-N': 16.95, 'GMOS-S': 15.65, 'F2': 16.15, 'GNIRS': 0.0}
    # oibright = {'GMOS-N': 6.0, 'GMOS-S': 6.0, 'F2': 6.0, 'GNIRS': 14.0}
    oifaint = {'GMOS-N': 16.95, 'GMOS-S': 15.65, 'F2': 16.15}
    oibright = {'GMOS-N': 6.0, 'GMOS-S': 6.0, 'F2': 6.0}

    p1faint = {'N': 15.65, 'S': 14.15}
    p1bright = {'N': 7.0, 'S': 7.0}

    p2faint = {'N': 15.65, 'S': 15.65}
    p2bright = {'N': 7.0, 'S': 7.0}

    # Magnitude corrections for conditions
    dmag = 0.0
    dmcc = [0.0, -0.3, -1.0, -3.0]
    try:
        ii = ['50', '70', '80', 'Any'].index(cc)
    except Exception:
        if verbose:
            print("cc must be one of '50','70','80','Any'")
        return magbright, magfaint
    dmag += dmcc[ii]

    dmiq = [0.25, 0.0, -0.25, -1.25]
    try:
        ii = ['20', '70', '85', 'Any'].index(iq)
    except Exception:
        if verbose:
            print("iq must be one of '20','70','85','Any'")
        return magbright, magfaint
    dmag += dmiq[ii]

    dmsb = [0.1, 0.0, -0.1, -0.2]
    try:
        ii = ['20', '50', '80', 'Any'].index(sb)
    except Exception:
        if verbose:
            print("sb must be one of '20','50','80','Any'")
        return magbright, magfaint
    dmag += dmsb[ii]
    if verbose:
        print('Dmag = ', dmag)

    if wfs == 'OIWFS':
        try:
            magbright = oibright[inst] + dmag
            magfaint = oifaint[inst] + dmag
        except Exception:
            if verbose:
                print('Only GMOS-N, GMOS-S, and F2 have supported OIs.')
    elif wfs == 'PWFS1':
        magbright = p1bright[site] + dmag
        magfaint = p1faint[site] + dmag
    elif wfs == 'PWFS2':
        magbright = p2bright[site] + dmag
        magfaint = p2faint[site] + dmag

    return magbright, magfaint


def f2oifov(pad=0.0, mcao=False, port='side', verbose=False):
    """
    Make a polygon of the F2 OI FOV

    Parameters
        pad:     Padding from edge of FoV to account for uncertainties in the edge [arcsec]
        mcao:    Using F2 with MCAO (f/33)
        port:    ISS port, either 'side' or 'up'
        verbose: Verbose output
    Returns
        xc, yc  Coordinates of vertices [arcmin]
    """
    # From f2oifov.pro
    # 2018oct27
    # 2021may07 - 3 circle geometry from Gabriel's sketch

    try:
        ii = ['side', 'up'].index(port.lower())
    except Exception:
        print('PORT must be "side" or "up".')
        return

    # degrees per radian
    degrad = 180./np.pi

    # telescope plate scale arcmin/mm
    if mcao:
        aminmm = 0.987/60.
    else:
        aminmm = 1.611444/60.

    # first, smaller circle, centered on base position (dewar window)
    r1 = 0.5*279.40*aminmm - pad/60.
    x1 = 0.0
    y1 = 0.0

    # second circle for pickoff arm
    # From original diagram in requirements document
    # r2=0.5*396.25*aminmm - pad/60.
    # x2 = 170.25*aminmm
    # From Gabriel's figure sketch-gpz294-revB.pdf
    # Radius of pickoff arm
    r2 = 191.0286*aminmm - pad/60.
    # Distance between center of F2 FoV and pickoff pivot
    x2 = (250.5934 - 77.6653)*aminmm
    y2 = 0.0

    # Third circle, with radius of base + pickoff
    x3 = 250.5934*aminmm
    y3 = 0.0
    r3 = 268.6939*aminmm - pad/60.

    # angle of intersection with second circle, use law of cosines
    aisect = np.arccos((x2**2 + r1**2 - r2**2)/(2.*x2*r1))
    aisect2 = np.arcsin(r1*np.sin(aisect)/r2)
    if verbose:
        print(aisect*degrad, aisect2*degrad)

    # angle of intersection with third circle, use law of cosines
    aisect3 = np.arccos((x3**2 + r1**2 - r3**2)/(2.*x3*r1))
    aisect3b = np.arcsin(r1*np.sin(aisect)/r3)
    if verbose:
        print(aisect3*degrad, aisect3b*degrad)

    # angle of intersection with linear cut
    aicut = np.arccos(113.0/139.7)

    theta = np.array(range(361)) / degrad

    # Chord on Circle 1 between Circle 3 and the vertical cut, +Y
    ii1 = np.where(np.logical_and((theta <= aisect3), (theta >= aicut)))[0]
    # Cord on circle 3 (+Y)
    ii2 = np.where(np.logical_and((theta > np.pi - aisect3b), (theta <= np.pi)))[0]
    # Chord on circle 2 (-Y)
    ii3 = np.where(np.logical_and((theta > np.pi), (theta < np.pi + aisect2)))[0]
    # Chord on Circle 1 (-Y) between Circle 2 and vertical cut
    ii4 = np.where(np.logical_and((theta >= 2.*np.pi - aisect), (theta <= 2.*np.pi - aicut)))[0]

    xc1 = x1 + r1*np.cos(theta)
    yc1 = y1 + r1*np.sin(theta)
    xc2 = x2 + r2*np.cos(theta)
    yc2 = y2 + r2*np.sin(theta)
    xc3 = x3 + r3*np.cos(theta)
    yc3 = y3 + r3*np.sin(theta)

    xc = xc1[ii1]
    yc = yc1[ii1]

    xc = np.append(xc, xc3[ii2])
    yc = np.append(yc, yc3[ii2])

    xc = np.append(xc, xc2[ii3])
    yc = np.append(yc, yc2[ii3])

    xc = np.append(xc, xc1[ii4])
    yc = np.append(yc, yc1[ii4])

    xc = np.append(xc, xc[0])
    yc = np.append(yc, yc[0])

    # if verbose:
    #     [print(xc[jj], yc[jj]) for jj in range(len(xc))]

    if verbose:
        plt.plot(xc3, yc3)
        plt.plot(xc2, yc2)
        plt.plot(xc1, yc1)
        plt.plot(xc, yc, linewidth=4, linestyle='--')
        plt.xlim = (-5, 11)
        plt.ylim = (-6, 6)
        plt.show()

    # output
    if port == 'side':
        xc = -xc  # make lozenge west of base

    return xc, yc


def gspick(xgs, ygs, xfov, yfov, mag, mmin, mmax, r, rmin, rweight):
    """
    Function for selecting guide star within WFS FOV
    Bryan Miller
    2006apr17 from gspick.pro

    Parameters
        xgs, ygs:   X, Y coordinates of guide stars from base
        xfov, yfov: X, Y coordinates of WFS FoV (polygon)
        mag:        Magnitudes of guide stars
        mmin:       Bright magnitude limit
        mmax:       Faint magnitude limit
        r:          Radial distance of guide stars from base
        rmin:       Minimum radial distance
        rweight:    Radial weighting term (larger to weight radial distance over brightness)

    Returns
        iout: index of selected guide star
    """

    iout = -1

    # Weight magnitudes by radial distance to select guide stars further from center
    wmag = mag - rweight * r

    # pick objects in FOV
    nv = len(xfov)
    if xfov[0] == xfov[-1] and yfov[0] == yfov[-1]:
        nv -= 1
    ib = inpoly(xfov[:nv], yfov[:nv], xgs, ygs)
    iin = np.where(ib)[0]

    if True in ib:
        ir = np.where(np.logical_and(r[iin] > rmin.data, np.logical_and(mag[iin] > mmin, mag[iin] <= mmax)))[0]
        if len(ir) > 1:
            im = np.where(wmag[iin[ir]] == min(wmag[iin[ir]]))[0]
            iout = iin[ir[im]][0]
        elif len(ir) == 1:
            iout = iin[ir[0]]

    return iout


def gsselect(target, ra, dec, pa=0.0, wfs='OIWFS', ifu='none',
             site='N', pamode='flip', cat='UCAC4', chopping=False,
             imdir='./', overwrite=False, rmin=-1.0, pad=0.0, inst='GMOS', port='side',
             testpa=False, degstep=-1., iq='70', cc='50', sb='50',
             display=False, figout=False, figfile='default', dpi=75, verbose=False):

    """Gemini guide star selection
       Based on gsselect.pro
       Bryan Miller

       Parameters
        target:     Target name [string]
        ra:         RA of base position [sexigesimal string]
        dec:        Dec of base position [sexigesimal string]
        pa:         Initial position angle [deg]
        wfs:        Wavefront sensor ['OIWFS', 'PWFS1', 'PWFS2']
        ifu:        GMOS IFU ['none', 'two', 'red', 'blue']
        site:       Gemini site ['N','S','mko','cpo']
        pamode:     PA mode ['fixed', 'flip', 'find']
        cat:        Guide star catalog ['UCAC4']
        chopping:   Chopping with P1/P2 (changes magnitude limits)
        imdir:      Directory for storing DSS images, guide star catalogs, and pngs of the field
        overwrite:  Overwrite DSS and vot files with new versions, otherwise use saved versions
        rmin:       Minimum radius from base [armin], -1 to use default values
        pad:        Padding applied to WFS FoV (to account for uncertainties in shape) [arcsec]
        inst:       Instrument ['GMOS','F2','GNIRS','NIFS','NIRIF/6','NIRIF/14','NIRIF/32']
        port:       ISS port ['side','up']
        testpa:     Test different PAs (not implemented)
        degstep:    Step in PAs (not implemented)
        iq:         Image quality constraint ['20','70','85','Any']
        cc:         Cloud cover constraint ['50', '70', '80', 'Any']
        sb:         Sky brightness constraint ['20','50','80','Any']
        display:    Display image of field with FoV?
        figout:     Output a png of the field?
        figfile:    Name of output png, if 'default' then use the target name
        dpi:        DPI for output figure, default=75
        verbose:    Verbose output?

       Returns
        gstarg:     Name of guide star [string]
        gsra:       RA of guide star [sexigesimal string]
        dec:        Dec of guide star [sexigesimal string]
        pa:         Final position angle [deg]

    """

    degrad = 180. / np.pi
    radeg = np.pi / 180.
    dpa = 0.0

    # Output parameters
    gstarg = ''
    gsra = ''
    gsdec = ''
    gsmag = 0.0

    l_pa = pa
    l_pamode = pamode.lower()
    try:
        ii = ['fixed', 'flip', 'find'].index(l_pamode)
    except Exception:
        if verbose:
            print("PA modes are: 'fixed', 'flip', 'find'")
        return gstarg, gsra, gsdec, gsmag, l_pa

    # GN and GS site information
    # lat = [19.8238, -30.24075]
    # long = [-155.46905, -70.736694]
    # elev = [4213., 2722.]

    if 's' in site.lower() or "cpo" in site.lower():
        l_site = 'S'
        isite = 1
        # utcoffset = -4.0 * u.hour + dst * u.hour
    elif 'n' in site.lower() or "mko" in site.lower():
        l_site = 'N'
        isite = 0
        # utcoffset = 10.0 * u.hour
    else:
        print('Site must be "cpo" or "mko" or include a "S" or "N".')
        return

    # Instrument
    l_inst = inst.upper()
    if 'GMOS' in l_inst:
        l_inst = 'GMOS-' + l_site
    try:
        ii = ['GMOS-S', 'GMOS-N', 'F2', 'GNIRS', 'NIFS', 'NIRIF/6', 'NIRIF/14', 'NIRIF/32'].index(l_inst)
    except Exception:
        if verbose:
            print("Currently supported instruments are: 'GMOS-S', 'GMOS-N', 'F2', 'GNIRS', 'NIFS', 'NIRIF/6', "
                  "'NIRIF/14', 'NIRIF/32'")
        return gstarg, gsra, gsdec, gsmag, l_pa
    if verbose:
        print('Instrument: ', l_inst)

    # IFU
    try:
        iifu = ['none', 'two', 'red', 'blue'].index(ifu.lower())
    except Exception:
        if verbose:
            print("IFU options: 'none','two', 'red', 'blue'")
        return gstarg, gsra, gsdec, gsmag, l_pa

    # WFS
    l_wfs = wfs.upper()
    try:
        ii = ['OIWFS', 'PWFS1', 'PWFS2'].index(l_wfs)
    except Exception:
        if verbose:
            print("Supported WFS are: 'OIWFS','PWFS1','PWFS2'")
        return gstarg, gsra, gsdec, gsmag, l_pa

    if verbose:
        print('WFS: ', l_wfs)

    l_target = re.sub(' ', '', target)

    tcoo = SkyCoord(ra.strip(), dec.strip(), frame='icrs', unit=(u.hr, u.deg))
    l_ra = tcoo.ra.to_string(u.hour, sep=':')
    l_dec = tcoo.dec.to_string(u.deg, sep=':')
    if '-' not in l_dec and l_dec[0] != '+':
        l_dec = '+' + l_dec

    # Step for PA search (not yet implemented)
    # if degstep == -1.:
    #     if inst == 'GMOS':
    #         degstep = 10.
    #     elif inst == 'F2':
    #         degstep = 90.

    # Magnitude corrections for conditions
    mmin, mmax = maglimits(l_inst, l_wfs, l_site, iq, cc, sb, verbose=verbose)
    if verbose:
        print('Mag min/max: ', mmin, mmax)
    if mmin == 9999. or mmax == 9999.:
        if verbose:
            print('Problem with magnitude limits.')
        return gstarg, gsra, gsdec, gsmag, l_pa

    # Radius limits
    tmp_rmin, l_rmax = rlimits(l_inst, l_wfs, l_site, verbose=verbose)
    if tmp_rmin == 0.0 or l_rmax == 0.0:
        if verbose:
            print('Problem with radius limits.')
        return gstarg, gsra, gsdec, gsmag, l_pa
    if rmin < 0:
        l_rmin = tmp_rmin * u.arcmin
    else:
        l_rmin = rmin * u.arcmin
    l_rmax = l_rmax * u.arcmin
    if verbose:
        print('Rmin/Rmax:', l_rmin, l_rmax)

    # Image catalog query
    imfile = imdir + '/' + l_target + '_dss.fits'
    if overwrite or not os.path.exists(imfile):
        if os.path.exists(imfile):
            os.remove(imfile)
        gemdssfile(l_ra, l_dec, imfile, 15., 15., site=l_site)

    hdu = pyfits.open(imfile)
    h = hdu[0].header
    wcs = WCS(h)
    cdelt = [h['CD1_1'], h['CD2_2']]
    rot = np.arctan2(-1.*h['CD2_1'], h['CD2_2']) * degrad
    # print(cdelt)
    # print(rot)

    if l_wfs == 'OIWFS':
        # pad [arcsec] tries to account for uncertainties in the patrol area, avoid guide stars
        # too close to the edge.
        # convert to arcmin
        l_pad = pad / 60.
        if 'GMOS' in l_inst:
            # Offsets for GMOS IFU base position
            if iifu > 0:
                xshift = [[0.5, 0.529, 0.471], [-0.5, -0.471, -0.529]]
                dx = xshift[isite][iifu]
            else:
                dx = 0.0
            # Vertices of OIWFS FOV [arcmin]
            x = [0.19 + dx, -3.31 + dx, -3.31 + dx, 0.19 + dx, 0.19 + dx]
            y = [-0.56, -0.56, 3.64, 3.64, -0.56]
            # Vertices with padding
            xpad = [0.19 + dx - l_pad, -3.31 + dx + l_pad, -3.31 + dx + l_pad, 0.19 + dx - l_pad, 0.19 + dx - l_pad]
            ypad = [-0.56 + l_pad, -0.56 + l_pad, 3.64 - l_pad, 3.64 - l_pad, -0.56 + l_pad]
            dpa = 180. * np.arctan((3.31 - dx)/3.64) / np.pi
            # l_rmax = np.sqrt((3.31 - pad / 60.) ** 2 + (3.64 - pad / 60.) ** 2)
        elif l_inst == 'F2':
            # F2
            x, y = f2oifov(port=port, verbose=False)
            xpad, ypad = f2oifov(pad=pad, port=port)
            dpa = 90.
            # l_rmax = l_rmax - pad / 60.

        l_rweight = 0.0

        if l_pamode != 'find':
            rotpa = rotations.Rotation2D(-(l_pa + rot))
            xpr, ypr = rotpa(np.asarray(x) / 60., np.asarray(y) / 60.)
            xpr = xpr/np.cos(tcoo.dec) + tcoo.ra.degree
            # print(xpr)
            ypr += tcoo.dec.degree
            xppr, yppr = rotpa(np.asarray(xpad) / 60., np.asarray(ypad) / 60.)
            xppr = xppr/np.cos(tcoo.dec) + tcoo.ra.degree
            yppr += tcoo.dec.degree

    else:
        # PWFS1/2
        l_rweight = 0.15
        if chopping:
            mmax -= 1.5
            mmin -= 1.5

    if 'xpr' not in locals():
        # Array of angles for making a circle
        ang = np.array(range(101)) * 2. * np.pi / 100.

        #  inner radius
        xpr = l_rmin.to(u.degree).data * np.cos(ang)/np.cos(tcoo.dec) + tcoo.ra.degree
        ypr = l_rmin.to(u.degree).data * np.sin(ang) + tcoo.dec.degree
        # plots, xpr / naxis1, ypr / naxis2, / norm, line = 2
        # outer radius
        xppr = l_rmax.to(u.degree).data * np.cos(ang)/np.cos(tcoo.dec) + tcoo.ra.degree
        yppr = l_rmax.to(u.degree).data * np.sin(ang) + tcoo.dec.degree

    # Query catalog
    if cat == 'UCAC4':
        gsfile = imdir + '/' + l_target + '_ucac4.vot'
        if overwrite or not os.path.exists(gsfile):
            if os.path.exists(gsfile):
                os.remove(gsfile)
            gsres = gemgstable(l_ra, l_dec, gsfile, cat='ucac4', radius=0.12, site='cpo')
        gsq = parse_single_table(gsfile).to_table(use_names_over_ids=True)
        id = gsq['ucac4']
        gscoo = SkyCoord(gsq['raj2000'], gsq['dej2000'], frame='icrs', unit=(u.deg, u.deg))
        if l_inst == 'GNIRS' and l_wfs == 'OIWFS':
            mag = gsq['kmag']
        else:
            mag = gsq['fmag']

    nquery = len(id)
    if nquery < 1:
        if verbose:
            print('No guide stars returned by query')
        return gstarg, gsra, gsdec, gsmag, l_pa
    if verbose:
        print('Number of stars returned by query: ', nquery)

    # Distance from center of field
    rsep = tcoo.separation(gscoo)
    if verbose:
        print('Rsep:', rsep.arcmin.min(), rsep.arcmin.max())

    # PA
    gspa = tcoo.position_angle(gscoo)
    if verbose:
        print('PA min/max: ', gspa.degree.min(), gspa.degree.max())

    ir = np.where(np.logical_and(np.logical_and(np.logical_and(mag > mmin, mag <= mmax), rsep.arcmin > l_rmin.data),
                                 rsep.arcmin <= l_rmax.data))[0]
    ngs = len(ir)
    if verbose:
        print('Number of guide star candidates: ', ngs)

    # Pick guide star
    iis = gspick(gscoo.ra.degree, gscoo.dec.degree, xppr, yppr, mag, mmin, mmax, rsep.degree,
                 l_rmin.to(u.degree), l_rweight)

    # If OIWFS, perhaps adjust PA
    if l_wfs == 'OIWFS':
        if iis != -1 and l_pamode == 'find':
            # This puts the guide star near the center of the FoV
            l_pa = gspa[iis].degree + dpa
        elif l_pamode != 'fixed':
            if iis == -1:
                l_mag = 999.
            else:
                l_mag = mag[iis]
            # Try pa +- 180
            if l_pa > 180.:
                l_pa180 = l_pa - 180.
            else:
                l_pa180 = l_pa + 180.
            rotpa = rotations.Rotation2D(-(l_pa180+rot))
            l_xppr, l_yppr = rotpa(np.asarray(xpad) / 60., np.asarray(ypad) / 60.)
            l_xppr = l_xppr/np.cos(tcoo.dec) + tcoo.ra.degree
            l_yppr += tcoo.dec.degree

            l_iis = gspick(gscoo.ra.degree, gscoo.dec.degree, l_xppr, l_yppr, mag, mmin, mmax, rsep.degree,
                           l_rmin.to(u.degree), l_rweight)

            if l_iis != -1:
                if mag[l_iis] < l_mag:
                    iis = l_iis
                    l_pa = l_pa180

        # Final FoVs for plots
        rotpa = rotations.Rotation2D(-(l_pa + rot))
        xpr, ypr = rotpa(np.asarray(x) / 60., np.asarray(y) / 60.)
        xpr = xpr/np.cos(tcoo.dec) + tcoo.ra.degree
        ypr += tcoo.dec.degree

        xppr, yppr = rotpa(np.asarray(xpad) / 60., np.asarray(ypad) / 60.)
        xppr = xppr/np.cos(tcoo.dec) + tcoo.ra.degree
        yppr += tcoo.dec.degree

    if iis == -1:
        if verbose:
            print('No guide star in FoV.')
    else:
        if type(id[iis]) is bytes:
            gstarg = id[iis].decode('UTF-8')
        else:
            gstarg = id[iis]
        gsra = gscoo.ra[iis].to_string(u.hour, sep=':')
        gsdec = gscoo.dec[iis].to_string(u.degree, sep=':')
        gsmag = mag[iis]

    # Plot
    if display or figout:
        if not display:
            pltuse('Agg')
        fig = plt.figure(figsize=(9,9))
        plt.subplot(projection=wcs)
        plt.imshow(hdu[0].data, origin='lower', cmap='gray_r')
        plt.grid(color='white', ls='solid')
        # Base position
        basepx = wcs.wcs_world2pix([tcoo.ra.value], [tcoo.dec.value], 0)
        plt.scatter(basepx[0], basepx[1], marker='P', color='none', edgecolor='orange', s=60)
        # Guide stars
        if ngs > 0:
            gsir = wcs.wcs_world2pix(gscoo.ra[ir].value, gscoo[ir].dec.value, 0)
            plt.scatter(gsir[0], gsir[1], color='none', edgecolor='green', marker='o', s=60)
        if iis != -1:
            gsiis = wcs.wcs_world2pix(gscoo.ra[iis].value, gscoo[iis].dec.value, 0)
            plt.scatter(gsiis[0], gsiis[1], color='none', edgecolor='blue', marker='s', s=80)
        # WFS FOV
        lstyle = {'OIWFS': {'p': '-', 'pp': '--'},
                  'PWFS2': {'p': '--', 'pp': '-'},
                  'PWFS1': {'p': '--', 'pp': '-'}}
        wfspoly_p = wcs.wcs_world2pix(xpr, ypr, 0)
        wfspoly_pp = wcs.wcs_world2pix(xppr, yppr, 0)
        plt.plot(wfspoly_p[0], wfspoly_p[1], marker='', color='red', linestyle=lstyle[l_wfs]['p'])
        plt.plot(wfspoly_pp[0], wfspoly_pp[1], marker='', color='red', linestyle=lstyle[l_wfs]['pp'])

        plt.xlabel('RA')
        plt.ylabel('Dec')

        if figout:
            if figfile.lower() == 'default':
                l_figfile = imdir + '/' + l_target + '_fov.png'
            else:
                l_figfile = imdir + '/' + figfile
            plt.savefig(l_figfile, dpi=dpi)

        if display:
            plt.show()

    hdu.close()

    return gstarg, gsra, gsdec, gsmag, l_pa
