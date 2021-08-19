#!/usr/bin/env python

from __future__ import print_function
import subprocess
from astropy.coordinates import SkyCoord
import astropy.units as u


def gemdssfile(ra, dec, outfile, xsiz, ysiz, site='cpo'):
    """Runs a search of the Gemini DSS server and downloads a FITS image of the field
       Bryan Miller
       ra : sexigesimal string
       dec: sexigesimal string
       outfile: name of output file, with path if needed
       xsize: horizontal size of image [arcmin]
       ysize: vertical size of image [arcmin]
       """

    l_ra = str(ra)
    l_dec = str(dec)
    l_outfile = str(outfile)
    l_xsiz = str(xsiz)
    l_ysiz = str(ysiz)
    l_site = str(site).lower()
    if 'n' or 'mko' in l_site:
        l_site = 'mko'
    if 's' or 'cpo' in l_site:
        l_site = 'cpo'

    status = 0

    if l_site == 'cpo' or l_site == 'mko':
        url = 'http://'+l_site+'catalog.gemini.edu/cgi-bin/dss_search?'
        url += 'ra=' + l_ra + '&dec=' + l_dec + '&mime-type=application/x-fits'
        url += '&x=' + l_xsiz + '&y=' + l_ysiz

        p = subprocess.Popen(["curl", "-k", "-s", "-o", l_outfile, url],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if err.decode() != '':
            print(err.decode())
            status = 1

    else:
        print('Site must be "cpo" or "mko" or include a "S" or "N".')
        status = 1

    return status


def gemgstable(ra, dec, outfile, cat='ucac4', radius=0.12, site='gs'):
    """Runs a search of Gemini-hosted catalog servers and downloads a VOTable-formated file
       Bryan Miller
       2018-05-27
       ra : sexigesimal string [J2000]
       dec: sexigesimal string [J2000]
       outfile: name of output file, with path if needed
       radius: search radius in degrees
       site: What server to use, can be 'gs', 'gn', 'cpo', 'mko', or include a 'N' or 'S'
       """

    coord = SkyCoord(ra + ' ' + dec, frame='icrs', unit=(u.hr, u.deg))
    l_ra = str(coord.ra.to_value('deg'))
    l_dec = str(coord.dec.to_value('deg'))
    l_outfile = str(outfile)
    l_cat = str(cat)
    l_sr = str(radius)
    l_site = str(site).lower()
    if 'n' or "mko" in l_site:
        l_site = 'gn'
    if 's' or "cpo" in l_site:
        l_site = 'gs'
    status = 0

    if l_site == 'gs' or l_site == 'gn':
        url = 'http://' + l_site + 'catalog.gemini.edu/cgi-bin/conesearch.py?'
        url += 'CATALOG=' + l_cat
        url += '&RA=' + l_ra + '&DEC=' + l_dec
        url += '&SR=' + l_sr

        p = subprocess.Popen(["curl", "-k", "-s", "-o", l_outfile, url],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if err.decode() != '':
            print(err.decode())
            status = 1

    else:
        print('Site must be "cpo" or "mko", or include a "S" or "N".')
        status = 1

    return status
