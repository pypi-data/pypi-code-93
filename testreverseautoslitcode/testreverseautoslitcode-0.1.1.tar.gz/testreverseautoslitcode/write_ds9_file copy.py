#function for creating the ds9 region files

#read in packages
#import fileinput
import sys
import numpy as np
#import pandas as pd
from astropy.coordinates import SkyCoord, ICRS, Galactic, FK4, FK5
from astropy.table import Table,Column
from astropy.io import ascii,fits
from astropy.time import Time
from regions import DS9Parser, write_ds9
import astropy.units as u


def create_ds9_file(data,ra_centers,dec_centers,theta,catalog_object_ra,catalog_object_dec,output_file):
#create a region file associated with the coordinates given in the data file
    str_data = Table()
    ra_str = Column(data['RA_Center'], name='RA_Center', dtype=str)
    dec_str = Column(data['Dec_Center'], name='Dec_Center', dtype=str)
    str_data.add_column(ra_str)
    str_data.add_column(dec_str)
    pa = str(theta)

#calculate the height and width (or grab them from the data?)
    width1 = str(np.abs(np.max(data['X'][0:4])-np.min(data['X'][0:4]))/3600)
    height1 = str(np.abs(np.max(data['Y'][0:4])-np.min(data['Y'][0:4]))/3600)

    reg_string ='icrs\nbox('+str_data['RA_Center'][0]+','+str_data['Dec_Center'][0]+','+width1+','+height1+','+pa+') # color=red'
    parser= DS9Parser(reg_string)
    regs = parser.shapes.to_regions()
    reg_list = regs
    i=4
    while i in range(1,int(len(str_data))):#-4):
        width = str(np.abs(np.max(data['X'][i:i+4])-np.min(data['X'][i:i+4]))/(0.7253 *0.99857*3600))
        height = str(np.abs(np.max(data['Y'][i:i+4])-np.min(data['Y'][i:i+4]))/(0.7253 *0.99857*3600))
        reg_string='icrs\nbox('+str_data['RA_Center'][i]+','+str_data['Dec_Center'][i]+','+width+','+height+','+pa+') # color=red'
        parser= DS9Parser(reg_string)
        regs = parser.shapes.to_regions()
        reg_list = reg_list + regs
        i = i+4

#write out boxes to the reg_string

    '''
    #to draw boxes based on having the positions of the corners

    reg_string ='icrs\npolygon('+str_data['Calc_RA'][0]+','+str_data['Calc_Dec'][0]+','+str_data['Calc_RA'][1]+','+str_data['Calc_Dec'][1]+','+str_data['Calc_RA'][2]+','+str_data['Calc_Dec'][2]+','+str_data['Calc_RA'][3]+','+str_data['Calc_Dec'][3]+') # color=blue'
    parser= DS9Parser(reg_string)
    regs = parser.shapes.to_regions()
    reg_list = regs
    i=4
    while i in range(1,int(len(str_data))-4):
        reg_string='icrs\npolygon('+str_data['Calc_RA'][i]+','+str_data['Calc_Dec'][i]+','+str_data['Calc_RA'][i+1]+','+str_data['Calc_Dec'][i+1]+','+str_data['Calc_RA'][i+2]+','+str_data['Calc_Dec'][i+2]+','+str_data['Calc_RA'][i+3]+','+str_data['Calc_Dec'][i+3]+') # color=blue'
        parser= DS9Parser(reg_string)
        regs = parser.shapes.to_regions()
        reg_list = reg_list + regs
        i = i+4

    #draw the vectors from the catalog objects to the box centers
    reg_string2 ='icrs\nline('+str(ra_centers[0])+','+str(dec_centers[0])+','+str(catalog_object_ra[0])+','+str(catalog_object_dec[0])+') # line=0 0 color=blue'
    parser2= DS9Parser(reg_string2)
    regs2 = parser2.shapes.to_regions()
    reg_list2 = regs2
    print('LEN RA CENTERS IS:' ,len(ra_centers))
    for i in range(1,len(ra_centers)):
        reg_string2='icrs\nline('+str(ra_centers[i])+','+str(dec_centers[i])+','+str(catalog_object_ra[i])+','+str(catalog_object_dec[i])+') # line=0 0 color=blue'
        parser2= DS9Parser(reg_string2)
        regs2 = parser2.shapes.to_regions()
        reg_list2 = reg_list2 + regs2
    '''

    #combine the two sections so the slits and vectors are both included
    reg_list = reg_list #+ reg_list2

    reg_filename = output_file+'.reg'#data_output_name+'.reg'#data_input_name[:period_index]+'.reg'
    write_ds9(reg_list, reg_filename,radunit='deg')
