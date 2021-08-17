#code to query GAIA database for closest object to calculated coordinates

#import packages
import numpy as np
from astropy.coordinates import SkyCoord, ICRS, Galactic, FK4, FK5
import astropy.units as u
from astroquery.gaia import Gaia
from astroquery.mast import Catalogs
from matplotlib import pyplot as plt
import create_err_plot as cep
import write_ds9_file as w9f
#import math
from astropy.table import Table,Column
from itertools import permutations,combinations
from matplotlib import colors

def get_shift(data,theta,catalog_keyword,output_file,ref_system,racenter,deccenter,filename,maskbluID,adcuse):
    #set up arrays and columns to hold results
    rpd = np.pi/180.  #radians per degree
    ra_shifts=[]
    dec_shifts = []
    ra_centers = []
    dec_centers = []
    x_centers = []
    y_centers = []
    catalog_obj_ra = []
    catalog_obj_dec = []
    objects_ra = []
    objects_dec = []
    data.add_column(0.00000000000,name='RA_Center')
    data.add_column(0.00000000000,name='Dec_Center')
    data.add_column(0.00000000000,name='X_Center')
    data.add_column(0.00000000000,name='Y_Center')
    data.add_column(0.00000000000,name='Cat_Obj_RA')
    data.add_column(0.00000000000,name='Cat_Obj_Dec')

    #Step through each slit and calcuate the center of each
    i=0
    k =0
    print('--------------Querying Catalog-------------')
    while i <= len(data)-4:
        #load in the corners for a given slit in both RA,Dec and x,y and calculate the ratio of the sides
        ra1,ra2,ra3,ra4 = data['Calc_RA'][i],data['Calc_RA'][i+1],data['Calc_RA'][i+2],data['Calc_RA'][i+3]
        dec1,dec2,dec3,dec4 = data['Calc_Dec'][i],data['Calc_Dec'][i+1],data['Calc_Dec'][i+2],data['Calc_Dec'][i+3]
        side1 = 3600*np.sqrt(((ra2-ra1)*np.cos(dec1*np.pi/180))**2+(dec1-dec2)**2)
        side2 = 3600*np.sqrt(((ra2-ra3)*np.cos(dec2*np.pi/180))**2+(dec3-dec2)**2)
        ratio = side1/side2
        print(ratio)
        ra_arr=[ra1,ra2,ra3,ra4]
        dec_arr=[dec1,dec2,dec3,dec4]
        ra_avg = (np.max(ra_arr)+np.min(ra_arr))/2.
        dec_avg = (np.max(dec_arr)+np.min(dec_arr))/2.
        xpos = [data['X'][i],data['X'][i+1],data['X'][i+2],data['X'][i+3]]
        ypos = [data['Y'][i],data['Y'][i+1],data['Y'][i+2],data['Y'][i+3]]
        x_avg = (np.max(xpos)+np.min(xpos))/2.
        y_avg = (np.max(ypos)+np.min(ypos))/2.
        data['RA_Center'][i],data['RA_Center'][i+1],data['RA_Center'][i+2],data['RA_Center'][i+3]=ra_avg,ra_avg,ra_avg,ra_avg
        data['Dec_Center'][i],data['Dec_Center'][i+1],data['Dec_Center'][i+2],data['Dec_Center'][i+3]=dec_avg,dec_avg,dec_avg,dec_avg
        data['X_Center'][i],data['X_Center'][i+1],data['X_Center'][i+2],data['X_Center'][i+3]=x_avg,x_avg,x_avg,x_avg
        data['Y_Center'][i],data['Y_Center'][i+1],data['Y_Center'][i+2],data['Y_Center'][i+3]=y_avg,y_avg,y_avg,y_avg

        #decide if current slit is an alignment box based on the ratio of the lengths of the sides of the slits
        if 0.95 < ratio < 1.05:
            k=k+1
            ra_centers.append(ra_avg)
            dec_centers.append(dec_avg)
            x_centers.append(x_avg)
            y_centers.append(y_avg)
            print('ra,dec of box =',ra_avg,dec_avg)

            #call astroquery with the chosen catalog to gather list of objects in and near the alignment boxes

            coord = SkyCoord(ra=ra_avg, dec=dec_avg, unit=(u.deg,u.deg),frame=ref_system)
            if catalog_keyword == 'gaia':
                width = 200*u.arcsec
                height = 200*u.arcsec
                obj = Gaia.query_object_async(coordinate=coord, width=width,height=height)
                mag_cutoff = (obj['phot_g_mean_flux']>18.)
                obj = obj[mag_cutoff]

                objects_ra.append(obj['ra'])
                objects_dec.append(obj['dec'])

                objects_ra.append(obj['ra'])
                objects_dec.append(obj['dec'])

                #find the object with the closest position
                diff = []
                for j in range(len(obj)):
                    diff.append(np.sqrt(((obj['ra'][j]-ra_avg)*np.cos(dec_avg*np.pi/180.))**2+(obj['dec'][j]-dec_avg)**2))
                min_diff = np.argmin(diff)

                #save catalog object to array
                catalog_obj_ra.append(obj[min_diff]['ra'])
                catalog_obj_dec.append(obj[min_diff]['dec'])

                data['Cat_Obj_RA'][i],data['Cat_Obj_RA'][i+1],data['Cat_Obj_RA'][i+2],data['Cat_Obj_RA'][i+3] = obj[min_diff]['ra'],obj[min_diff]['ra'],obj[min_diff]['ra'],obj[min_diff]['ra']
                data['Cat_Obj_Dec'][i],data['Cat_Obj_Dec'][i+1],data['Cat_Obj_Dec'][i+2],data['Cat_Obj_Dec'][i+3] = obj[min_diff]['dec'],obj[min_diff]['dec'],obj[min_diff]['dec'],obj[min_diff]['dec']

                print('GAIA object located at:',obj[min_diff]['ra'],obj[min_diff]['dec'])
                ra_shifts.append((ra_avg-obj['ra'][min_diff])*np.cos(dec_avg*np.pi/180.))
                dec_shifts.append(dec_avg-obj['dec'][min_diff])

            if catalog_keyword == 'panstarrs':
                obj = Catalogs.query_region(coord, radius=15*u.arcsec, catalog='Panstarrs', data_release='dr2')
               # mag_cutoff = (obj['gMeanKronMag']>18.)
                #obj = obj[mag_cutoff]

                objects_ra.append(obj['raMean'])
                objects_dec.append(obj['decMean'])


                #find the object with the closest position
                diff = []
                for j in range(len(obj)):
                    diff.append(np.sqrt(((obj['raMean'][j]-ra_avg)*np.cos(dec_avg*np.pi/180.))**2+(obj['decMean'][j]-dec_avg)**2))
                min_diff = np.argmin(diff)


                #save catalog object to array
                catalog_obj_ra.append(obj[min_diff]['raMean'])
                catalog_obj_dec.append(obj[min_diff]['decMean'])

                data['Cat_Obj_RA'][i],data['Cat_Obj_RA'][i+1],data['Cat_Obj_RA'][i+2],data['Cat_Obj_RA'][i+3] = obj[min_diff]['raMean'],obj[min_diff]['raMean'],obj[min_diff]['raMean'],obj[min_diff]['raMean']
                data['Cat_Obj_Dec'][i],data['Cat_Obj_Dec'][i+1],data['Cat_Obj_Dec'][i+2],data['Cat_Obj_Dec'][i+3] = obj[min_diff]['decMean'],obj[min_diff]['decMean'],obj[min_diff]['decMean'],obj[min_diff]['decMean']

                print('PANSTARRS object located at:',obj[min_diff]['raMean'],obj[min_diff]['decMean'])
                ra_shifts.append((ra_avg-obj['raMean'][min_diff])*np.cos(dec_avg*np.pi/180.))
                dec_shifts.append(dec_avg-obj['decMean'][min_diff])

            if catalog_keyword == 'custom':
                obj = Table.read(filename)
                objects_ra.append(obj['ra'])
                objects_dec.append(obj['dec'])

                #find the object with the closest position
                diff = []
                for j in range(len(obj)):
                    diff.append(np.sqrt(((obj['ra'][j]-ra_avg)*np.cos(dec_avg*np.pi/180.))**2+(obj['dec'][j]-dec_avg)**2))
                min_diff = np.argmin(diff)

                #save catalog object to array
                catalog_obj_ra.append(obj[min_diff]['ra'])
                catalog_obj_dec.append(obj[min_diff]['dec'])

                data['Cat_Obj_RA'][i],data['Cat_Obj_RA'][i+1],data['Cat_Obj_RA'][i+2],data['Cat_Obj_RA'][i+3] = obj[min_diff]['ra'],obj[min_diff]['ra'],obj[min_diff]['ra'],obj[min_diff]['ra']
                data['Cat_Obj_Dec'][i],data['Cat_Obj_Dec'][i+1],data['Cat_Obj_Dec'][i+2],data['Cat_Obj_Dec'][i+3] = obj[min_diff]['dec'],obj[min_diff]['dec'],obj[min_diff]['dec'],obj[min_diff]['dec']

                print('Custom object located at:',obj[min_diff]['ra'],obj[min_diff]['dec'])
                ra_shifts.append((ra_avg-obj['ra'][min_diff])*np.cos(dec_avg*np.pi/180.))
                dec_shifts.append(dec_avg-obj['dec'][min_diff])

            i=i+4
        else:
            i=i+4

    good_ra_shifts=[]
    good_dec_shifts=[]
    removed = 0
    large = 0
    small = 0
    ra_raw_average = np.average(ra_shifts)
    ra_raw_median = np.median(ra_shifts)
    ra_raw_dispersion = np.sqrt(np.sum((ra_shifts-ra_raw_average)**2)/(len(ra_shifts)-1))
    dec_raw_average = np.average(dec_shifts)
    dec_raw_median = np.median(dec_shifts)
    dec_raw_dispersion = np.sqrt(np.sum((dec_shifts-dec_raw_average)**2)/(len(dec_shifts)-1))
    '''
    #test using the median and the dispersion
    for p in range(len(ra_shifts)):
        if ra_raw_median-ra_raw_dispersion < ra_shifts[p] and ra_shifts[p] < ra_raw_median+ra_raw_dispersion and dec_raw_median-dec_raw_dispersion < dec_shifts[p] and dec_shifts[p] < dec_raw_median+dec_raw_dispersion:
            good_ra_shifts.append(ra_shifts[p])
            good_dec_shifts.append(dec_shifts[p])
        else:
            removed = removed+1

    '''
    print(np.min(np.abs(ra_shifts))*3600.,np.max(np.abs(ra_shifts))*3600.)
    if (np.min(np.abs(ra_shifts))*3600 < 1.2 and np.max(np.abs(ra_shifts))*3600 > 5.0) or (np.min(np.abs(dec_shifts))*3600 < 1.2 and np.max(np.abs(dec_shifts))*3600 > 5.0):
        print('Found Outliers...')
        for h in range(len(ra_shifts)):
            if np.abs(ra_shifts[h])*3600 < 1.2 and np.abs(dec_shifts[h])*3600 < 1.2:
                small = small +1
            else:
                large = large+1
        if small >= large:
            for n in range(len(ra_shifts)):
                if np.abs(ra_shifts[n])*3600 > 5. or np.abs(dec_shifts[n])*3600 > 5.0:
                    removed = removed +1
                    n=n+1
                else:
                    good_ra_shifts.append(ra_shifts[n])
                    good_dec_shifts.append(dec_shifts[n])
        if large > small:
            for n in range(len(ra_shifts)):
                if np.abs(ra_shifts[n])*3600 < 5. or np.abs(dec_shifts[n])*3600 < 5.0:
                    removed = removed +1
                    n=n+1
                else:
                    good_ra_shifts.append(ra_shifts[n])
                    good_dec_shifts.append(dec_shifts[n])
    else:
        good_ra_shifts = ra_shifts
        good_dec_shifts = dec_shifts

    print(small,'small shifts')
    print(removed,'elements removed from shift arrays')
    '''
    #calculate the differences in avg shift based on which ones we include
    #remove one value
    l = 2
    total_shifts = []
    total_shifts2 = []
    total_shifts3 = []
    while l <= len(good_ra_shifts)-1:

        raperms = list(combinations(good_ra_shifts,l))
        deccperms = list(combinations(good_dec_shifts,l))
        for g in range(len(raperms)):
            print('l=',l)
            raremLst = np.average(raperms[g])
            decremLst = np.average(deccperms[g])
            if l == 2:
                total_shifts2.append(np.sqrt((raremLst/np.cos(dec_avg*np.pi/180))**2+(decremLst**2))*3600 )
            if l == 3:
                total_shifts3.append(np.sqrt((raremLst/np.cos(dec_avg*np.pi/180))**2+(decremLst**2))*3600 )
            if l > 3:
                total_shifts.append(np.sqrt((raremLst/np.cos(dec_avg*np.pi/180))**2+(decremLst**2))*3600 )

        l = l+1
    print('total shifts2:',total_shifts2)
    print('total shifts3:',total_shifts3)
    print('total shifts4+:',total_shifts)
    dispersion2 = np.sqrt(np.sum((total_shifts2-np.average(total_shifts2))**2)/(len(total_shifts2)-1))
    dispersion3 = np.sqrt(np.sum((total_shifts3-np.average(total_shifts3))**2)/(len(total_shifts3)-1))
    dispersionall = np.sqrt(np.sum((total_shifts-np.average(total_shifts))**2)/(len(total_shifts)-1))
    fig = plt.figure()
    plt.hist([total_shifts2,total_shifts3,total_shifts],bins=10,color=["red", "blue", "purple"],stacked=True,label=['2 Elements','3 Elements','4+ Elements'])
    fig.text(0.15,0.4,'2 Element Avg:'+str(round(np.average(total_shifts2),3))+'$\pm$'+str(round(dispersion2,3)),bbox=dict(facecolor='green', alpha=0.8))
    fig.text(0.15,0.3,'3 Element Avg:'+str(round(np.average(total_shifts3),3))+'$\pm$'+str(round(dispersion3,3)),bbox=dict(facecolor='green', alpha=0.8))
    fig.text(0.15,0.2,'4+ Element Avg:'+str(round(np.average(total_shifts),3))+'$\pm$'+str(round(dispersionall,3)),bbox=dict(facecolor='green', alpha=0.8))
    plt.legend()
    plt.xlabel('Shifts (arcsec)')
    '''
    dec_shift_final = np.average(good_dec_shifts)
    ra_shift_final = np.average(good_ra_shifts)/np.cos(data['Calc_Dec'][0]*np.pi/180)
    final_shifts = np.zeros(len(good_ra_shifts))
    for g in range(len(final_shifts)):
        final_shifts[g] = np.sqrt((good_ra_shifts[g]/np.cos(data['Calc_Dec'][0]*np.pi/180))**2+(good_dec_shifts[g]**2))*3600
    total_shift_final = np.sqrt(ra_shift_final**2+dec_shift_final**2)*3600
    total_shift_dispersion =np.sqrt(np.sum((final_shifts-total_shift_final)**2)/(len(final_shifts)-1))

    badshift = 0
    if total_shift_dispersion >=2.0 or np.isnan(total_shift_final) == True:
        ra_shift_final = np.float64(0.0)
        dec_shift_final = np.float64(0.0)
        badshift = 1
        print('---------No Systematic Shift Found. No Shift Applied---------')
    print('ratio',total_shift_final/total_shift_dispersion)
#    if 0.70 < total_shift_final/total_shift_dispersion:
#        ra_shift_final = np.float64(0.0)
#        dec_shift_final = np.float64(0.0)
#        print('---------No Systematic Shift Found. No Shift Applied---------')

    ra_shifted_centers = ra_centers-ra_shift_final
    dec_shifted_centers = dec_centers-dec_shift_final
    print('Final Shift:',str(round(total_shift_final,3))+'+/-'+str(round(total_shift_dispersion,3)))

    #calculate the difference between the shifted centers and the catalog objects
    after_shifts_total = np.zeros(len(ra_centers))
    before_shifts_total = np.zeros(len(ra_centers))
    after_ra_shifts = np.zeros(len(ra_centers))
    before_ra_shifts = ra_shifts
    for g in range(len(after_shifts_total)):
        before_ra_diff = 3600*(ra_centers[g] - catalog_obj_ra[g])*np.cos(data['Calc_Dec'][0]*np.pi/180)
        before_dec_diff = 3600*(dec_centers[g] - catalog_obj_dec[g])
        ra_diff = 3600*(ra_shifted_centers[g] - catalog_obj_ra[g])*np.cos(data['Calc_Dec'][0]*np.pi/180)
        after_ra_shifts[g]=ra_diff
        before_ra_shifts[g] = 3600.*ra_shifts[g]
        dec_diff = 3600*(dec_shifted_centers[g] - catalog_obj_dec[g])
        before_shifts_total[g] = np.sqrt((before_ra_diff)**2+(before_dec_diff)**2)
        after_shifts_total[g] = np.sqrt((ra_diff)**2+(dec_diff)**2)
    print('Before Shifts:',before_shifts_total)
    print('After Shifts:',after_shifts_total)
    print('Before RA Shifts:',before_ra_shifts)
    print('After RA Shifts:',after_ra_shifts)



    data['Calc_RA'] = data['Calc_RA']-ra_shift_final
    data['Calc_Dec'] = data['Calc_Dec']-dec_shift_final
    data['RA_Center'] = data['RA_Center']-ra_shift_final
    data['Dec_Center'] = data['Dec_Center']-dec_shift_final
    '''
    #write out the info I need for the shift plots to a text file
    #create the string to write to the file
    shiftapplied = 'yes'
    if badshift == 1:
        shiftapplied = 'no'
    info = maskbluID +','+ shiftapplied+','+adcuse+','+str(round(total_shift_final,3))+','+str(round(total_shift_dispersion,3))+',"'+str(before_shifts_total)+'","'+str(after_shifts_total)+'","'+str(before_ra_shifts)+'","'+str(after_ra_shifts)+'"\n'
    file1 = open("myfile.csv","a")#append mode
    file1.write(info)
    file1.close()
    '''
    #print(info)

    return(data,x_centers,y_centers,ra_shifted_centers,dec_shifted_centers,catalog_obj_ra,catalog_obj_dec,objects_ra,objects_dec)
