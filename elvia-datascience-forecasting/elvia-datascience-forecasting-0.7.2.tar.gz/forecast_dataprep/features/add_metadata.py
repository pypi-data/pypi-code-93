# create dictionary of old and new names of substations and then map them to create new column
def add_metadata(row, df_metadata):
    """
    This function takes Azure energy consumption metadata that will apply to the energy consumption dataframe
    by using pandas apply function for cleaning transformer names.

    # Parameters
    --------------
    row           : Refering to the each row of a serie in energy consumtion pandas dataframe
    df_metadata   : Weekly average cumsumtion AZURE DATASET

    # Returns
    --------------
    Has multiple returns that are the cleaned transformer names
    """

    df_trafo_metadata = df_metadata.copy()
    # lists of valid and invalid substations
    list_invalid_t = []
    list_t = []
    cnt = 0
    
    if (row != None) and (not row.startswith('T')) and (
            not row.startswith('Q')
    ):  # all placed in Innlandet and 'NS22LHUN' doesnot have any electricity measurement
        if row.startswith('ENS12160S'):
            new_name = row[:8]
            cnt += 1
            list_t.append(new_name)
            return new_name
        elif row.split(
                'T')[0] not in df_trafo_metadata['Driftsmerking'].values:
            new_name = row.split('T')[0]
            list_invalid_t.append(new_name)
        else:
            new_name = row.split('T')[0]
            cnt += 1
            list_t.append(new_name)
            return new_name

    if row.startswith(
            'Q'):  # we have just one starting with Q, placed in Innlandet
        new_name = row[:4]
        cnt += 1
        list_t.append(new_name)
        return new_name

    # All kommunes start with T, are placed either in Oslo or in Viken
    if (row != None) and (row.startswith('T')):
        name = row.split('-')[0][1:]

        if (len(name) != 5) and (name.endswith('gml')) and (
                name[:len(name) - 3]
                in df_trafo_metadata['Driftsmerking'].values):
            new_name = name[:len(name) - 3]  # removing 'gml'
            cnt += 1
            list_t.append(new_name)
            return new_name

        elif (len(name) != 5) and (name.endswith('gml')) and (
                not name[:len(name) - 3]
                in df_trafo_metadata['Driftsmerking'].values):
            #print('its length is not 5 and it Ends with gml but not in Metadata', name)
            list_invalid_t.append(name)

        elif (len(name) != 5) and (not name.endswith('gml')) and (
                name in df_trafo_metadata['Driftsmerking'].values
        ):  # add to invalid list
            new_name = name
            cnt += 1
            list_t.append(new_name)
            return new_name

        elif (len(name) != 5) and (not name.endswith('gml')) and (
                name not in df_trafo_metadata['Driftsmerking'].values):
            # print('its length is not 5 and it DOESNOT End with gml but not in Metadata', name)
            new_name = name
            list_invalid_t.append(new_name)

            # ADD here metadata dataframe and write here again
        elif (len(name) == 5) and (not name.endswith('gml')) and (
                name in df_trafo_metadata['Driftsmerking'].values):
            new_name = name  # 56 of them are not placed in substation_metadata. Their names are in "not_in_trafo_metadat.json" file
            cnt += 1
            list_t.append(new_name)
            return new_name

        elif (len(name) == 5) and (name.endswith('gml')) and (
                name in df_trafo_metadata['Driftsmerking'].values):
            new_name = name  # 56 of them are not placed in substation_metadata. Their names are in "not_in_trafo_metadat.json" file
            cnt += 1
            list_t.append(new_name)
            return new_name

        elif (len(name) == 5) and (not name.endswith('gml')) and (
                name not in df_trafo_metadata['Driftsmerking'].values):
            # print('length is 5 without gml but not in Metadata', name)
            new_name = name
            list_invalid_t.append(new_name)

        elif (len(name) == 5) and (name.endswith('gml')) and (
                name not in df_trafo_metadata['Driftsmerking'].values):
            # print('length is 5 with gml but not in Metadata', name)
            new_name = name
            list_invalid_t.append(new_name)
