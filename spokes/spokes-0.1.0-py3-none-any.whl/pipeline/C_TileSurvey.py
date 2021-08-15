import random
import numpy
import h5py
import math
import time
from ..utils import logger

def tile_survey(databank_path):

    start_time = time.perf_counter()

    log = logger.get_logger(__name__)


    log.info("=============================")
    log.info("Tiling Survey")
    log.info("=============================\n")


    with h5py.File(databank_path, 'a') as db:
        target_selection_flag = db['/Galaxies/target_selection_flag'][()]
        ra = db['/Galaxies/ra_true'][()]
        dec = db['/Galaxies/dec_true'][()]

        ra_range = db['/SurveyParameters/right_ascension_range'][()]
        dec_range = db['/SurveyParameters/declination_range'][()]
        fov = db['/SurveyParameters/field_of_view'][()]
        shape = db['/SurveyParameters/tile_shape'][()]

        verbose = db['/RuntimeParameters/verbose'][()]

    if 2 in verbose:
        log.setLevel(10)

    log.verbose(f"Imported data from databank at {databank_path}")

    Ngal = len(target_selection_flag)

    log.verbose(f"Number of galaxies imported: {Ngal}")

    min_ra = ra_range[0]
    max_ra = ra_range[1]
    min_dec = dec_range[0]
    max_dec = dec_range[1]

    log.verbose(f"Right ascension range:   [{min_ra} deg, {max_ra} deg]")
    log.verbose(f"Declination range:       [{min_dec} deg, {max_dec} deg]")
    log.verbose(f"Shape:                   {shape}")
    log.verbose(f"Field of view radius:    {fov} deg")
    log.verbose(f"Calculating survey selection flag...")

    survey_selection_flag_ra = (ra > min_ra) * (ra < max_ra)
    survey_selection_flag_dec = (dec > min_dec) * (dec < max_dec)
    survey_selection_flag = survey_selection_flag_ra * survey_selection_flag_dec
    survey_selection_flag = survey_selection_flag * target_selection_flag

    log.verbose(f"Survey selection flag calculated")

    ra_min_tot = numpy.min(ra[survey_selection_flag])
    ra_max_tot = numpy.max(ra[survey_selection_flag])
    dec_min_tot = numpy.min(dec[survey_selection_flag])
    dec_max_tot = numpy.max(dec[survey_selection_flag])

    if shape == "square":
        side_length = math.sqrt(2) * fov

        log.verbose(f"Tile side length: {side_length} deg")

        Ntiles_ra = math.ceil((max_ra - min_ra)/side_length)
        Ntiles_dec = math.ceil((max_dec - min_dec)/side_length)
        Ntiles_total = Ntiles_ra * Ntiles_dec

        log.verbose(f"Total tiles required to cover survey ranges: {Ntiles_total}")
        log.verbose(f"Tiling survey with {Ntiles_total} square tiles")

        tile_centers_ra = numpy.array(list(numpy.arange(start=min_ra+(side_length/2), stop=max_ra+(side_length/2), step=side_length)) * Ntiles_dec)
        tile_centers_dec = numpy.repeat(numpy.arange(start=min_dec+(side_length/2), stop=max_dec+(side_length/2), step=side_length), Ntiles_ra)

        log.verbose(f"Calculated tile centers")

        ra_crop = ra[survey_selection_flag]
        dec_crop = dec[survey_selection_flag]

        log.verbose(f"Calculating galaxy tile IDs...")

        ra_tile_id = ((ra_crop - min_ra)/side_length).astype(int)
        dec_tile_id = ((dec_crop - min_dec)/side_length).astype(int)
        tile_id_galaxy_only = dec_tile_id * Ntiles_ra + ra_tile_id

        log.verbose(f"Galaxy tile IDs calculated")

    if shape == "hexagonal":
        tile_centers_ra = []
        tile_centers_dec = []

        ra_direction = 1

        ra_current = fov * math.sin(60 * (math.pi / 180)) + min_ra
        dec_current = fov * math.cos(60 * (math.pi / 180)) + min_dec

        extends_right = False
        extends_left = True

        log.verbose("Generating hexagonal tile centers...")

        while True:
            tile_centers_ra.append(ra_current)
            tile_centers_dec.append(dec_current)

            temp_ra_current = ra_current + ra_direction * 2 * fov * math.sin(60 * (math.pi / 180))
            inner_edge = temp_ra_current - ra_direction * fov * math.sin(60 * (math.pi / 180))

            if ra_direction == 1:
                if inner_edge > max_ra:
                    dec_current += 1.5 * fov
                    if ra_current < max_ra:
                        ra_current += fov * math.sin(60 * (math.pi / 180))
                        extends_right = True
                    else:
                        ra_current -= fov * math.sin(60 * (math.pi / 180))
                    ra_direction = -1
                else:
                    ra_current = temp_ra_current
            else:
                if inner_edge < min_ra:
                    dec_current += 1.5 * fov
                    if ra_current > min_ra:
                        ra_current -= fov * math.sin(60 * (math.pi / 180))
                    else:
                        ra_current += fov * math.sin(60 * (math.pi / 180))
                    ra_direction = 1
                else:
                    ra_current = temp_ra_current

            if dec_current > (max_dec + fov):
                break

        log.verbose("Hexagonal tile centers generated")

        Ntiles_total = len(tile_centers_ra)

        log.verbose(f"Total tiles required to cover survey ranges: {Ntiles_total}")
        log.verbose(f"Re-ordering tile centers to match tile ID system...")

        tile_centers_ra = numpy.array(tile_centers_ra)
        tile_centers_dec = numpy.array(tile_centers_dec)

        switch = []
        odd = False
        old_dec = tile_centers_dec[0]
        for i in range(Ntiles_total):
            if not tile_centers_dec[i] == old_dec:
                old_dec = tile_centers_dec[i]
                odd = not odd
                if odd == True:
                    switch.append(old_dec)
        for id in switch:
            min_id = min(numpy.where(tile_centers_dec == id)[0])
            max_id = max(numpy.where(tile_centers_dec == id)[0])
            tile_centers_ra = numpy.concatenate((tile_centers_ra[:min_id], tile_centers_ra[max_id:min_id-1:-1], tile_centers_ra[max_id+1:]))

        log.verbose(f"Tiles re-ordered")
        log.verbose(f"Assigning tile IDs to galaxies...")

        ra_crop = ra[survey_selection_flag]
        dec_crop = dec[survey_selection_flag]

        tile_id_galaxy_only = []

        gridHeight = fov + fov * math.cos(60 * (math.pi / 180))
        gridWidth = 2 * fov * math.sin(60 * (math.pi / 180))

        Ntiles_ra = math.ceil((max_ra - min_ra)/(2 * fov *math.sin(60 * (math.pi / 180)))) # first row

        for i in range(len(ra_crop)):
            r = ra_crop[i] - min_ra
            d = dec_crop[i] - min_dec

            row = int(d / gridHeight)
            relY = d % gridHeight

            if row % 2 == 0:
                column = int(r / gridWidth)
                relX = r % gridWidth
            else:
                if extends_left:
                    column = int((r + gridWidth / 2) / gridWidth)
                    relX = (r + gridWidth/2) % gridWidth
                else:
                    column = int((r - gridWidth / 2) / gridWidth)
                    relX = (r - gridWidth/2) % gridWidth

            if relY > fov + relX * (math.tan(30 * (math.pi / 180))): # Left top edge
                if row % 2 == 0:
                    if not extends_left:
                        column -= 1
                else:
                    if extends_left:
                        column -= 1
                row += 1
            elif relY > (2 * fov) - relX * (math.tan(30 * (math.pi / 180))): # Right top edge
                if row % 2 == 0:
                    if extends_left:
                        column += 1
                else:
                    if not extends_left:
                        column += 1
                row += 1

            extend_right = int(extends_right == True)
            extend_left = int(extends_left == True)
            tile_id = int(row * Ntiles_ra + int(row / 2) * (extend_right+extend_left - 1) + column)
            tile_id_galaxy_only.append(tile_id)

        tile_id_galaxy_only = numpy.array(tile_id_galaxy_only)
        log.verbose("Galaxy tile IDs succesfully generated")

    log.verbose("Removing tiles without galaxies assigned to them and generating tile_id_galaxy...")

    disconnected_ids = sorted(list(set(tile_id_galaxy_only)))
    for id in range(len(disconnected_ids)):
        tile_id_galaxy_only[tile_id_galaxy_only == disconnected_ids[id]] = id

    tile_centers_ra = tile_centers_ra[disconnected_ids]
    tile_centers_dec = tile_centers_dec[disconnected_ids]

    Ntiles = len(tile_centers_ra)

    list_tile_ID = numpy.arange(Ntiles)

    tile_id_galaxy = numpy.full(Ngal, -1)
    tile_id_galaxy[survey_selection_flag] = tile_id_galaxy_only

    log.verbose(f"Unnecessary tiles removed and generated tile_id_galaxy")


    with h5py.File(databank_path, 'a') as db:
        # galaxies
    	db['/Galaxies/survey_selection_flag'] = survey_selection_flag
    	db['/Galaxies/tile_id'] = tile_id_galaxy

    	# tiles
    	db['/SurveyTiles/tile_id'] = list_tile_ID
    	db['/SurveyTiles/number_of_tiles'] = Ntiles
    	#db['/SurveyTiles/airmass'] = airmass
    	db['/SurveyTiles/tile_centers_ra'] = tile_centers_ra
    	db['/SurveyTiles/tile_centers_dec'] = tile_centers_dec

    	db['/SurveyTiles/ra_min_tot'] = ra_min_tot
    	db['/SurveyTiles/ra_max_tot'] = ra_max_tot
    	db['/SurveyTiles/dec_min_tot'] = dec_min_tot
    	db['/SurveyTiles/dec_max_tot'] = dec_max_tot

    log.verbose("Data written back to databank")
    log.verbose(f"*********************************")
    log.verbose(f"Tile survey results summary:")

    target_selected = numpy.sum((target_selection_flag == True))
    survey_selected = numpy.sum((survey_selection_flag == True))

    log.verbose(f"Total galaxies:                    {Ngal}")
    log.verbose(f"Selected from target selection:    {target_selected}")
    log.verbose(f"Selected from survey selection:    {survey_selected}")
    log.verbose(f"Number of tiles:                   {Ntiles}")

    end_time = time.perf_counter()
    log.verbose(f"Tiled survey in {end_time - start_time} seconds")
