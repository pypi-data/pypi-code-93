from cygnsslib import find_land_prod_sample_id_from_excel

if __name__ == '__main__':
    xls_in = 'SLV_Z4_thawed_2019.xlsx'
    find_land_prod_sample_id_from_excel(xls_in, xls_out=None, start_col=1, out_sheet_suffix='', timestamp_col=0)
    xls_in = 'SLV_Z1_thawed_2019.xlsx'
    find_land_prod_sample_id_from_excel(xls_in, xls_out=None, st_row=4, start_col=1, out_sheet_suffix='', timestamp_col=0)
