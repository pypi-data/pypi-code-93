import pandas as pd
import numpy as np
from datetime import timedelta
import sys
from sklearn.preprocessing import normalize
import warnings
warnings.filterwarnings("ignore")

sys.path.append("..")
pd.options.display.float_format = '{:.2f}'.format


def filter_data(pd_df, business, date_filter, region_list, order_status_type, order_status):
    """Function to create filters on the orders based on 
    business, date, region, order_status_type and order_status

    Args:
        pd_df(dataframe): Contains orders at transaction level for each customer
        business(list): 'BeerHawk'
        date_filter(date): The date from which data should be considered for clustering
        region_list(list): limit to orders from following region 
        order_status_type: 'Valid'
        order_status(list): ['complete','serviceissueresolved']
    Returns:
        pd_df(dataframe): Filtered data frame for raw_orders and raw_sessions
        
    """
    # Apply filters to sales DF
    print('Total number of Orders')
    print(len(pd_df))

    print('Orders only from {}'.format(business))
    pd_df = pd_df[pd_df['BUSINESS_NAME'] == business]
    print(len(pd_df))

    print('Orders from {} onwards'.format(date_filter))
    pd_df = pd_df[pd_df['ORDER_DATE'] >= date_filter]
    print(len(pd_df))

    print('Orders only from region: {}'.format(region_list))
    pd_df = pd_df[pd_df['REGION'].isin(region_list)]
    print(len(pd_df))

    print('Orders with status type as {}'.format(order_status_type))
    pd_df = pd_df[pd_df['ORDER_STATUS_TYPE'] == order_status_type]
    print(len(pd_df))

    print('Orders with status as {}'.format(order_status))
    pd_df = pd_df[pd_df['ORDER_STATUS'].isin(order_status)]
    print(len(pd_df))

    return pd_df

def create_customer_kpis(pd_df, sales_pd_gb):
    """Function to create customer KPIs (e.g. AOV, AOF etc)

    Args:
        pd_df(dataframe): Combined dataframe for raw_orders and raw_sessions
        sales_pd_gb(dataframe): Grouped sales for each individual customer.
    Returns:
        customer_df(dataframe): KPIs(e.g. AOV, AOF etc) for each individual customer.
        
    """
    # Calculate average unique skus per order
    unique_sku_per_order = pd_df.groupby(['CUSTOMER_SPK', 'ORDER_SPK'])['PRODUCT_SPK'].nunique().reset_index()
    average_unique_skus = unique_sku_per_order.groupby('CUSTOMER_SPK')['PRODUCT_SPK'].mean().reset_index()
    average_unique_skus.rename(columns={'PRODUCT_SPK': 'average_unique_skus_per_order'}, inplace=True)

    # Create customer dataframe
    customer_df = pd.DataFrame()

    # Create unique customer identifier (using hashed email not customer ID given association of multiple customerids to same email)
    customer_df['CUSTOMER_SPK'] = sales_pd_gb['CUSTOMER_SPK']

    # Calculate average order frequency (days)
    customer_df['average_order_frequency'] = ((sales_pd_gb['ORDER_DATE']['max'] - sales_pd_gb['ORDER_DATE']['min']) / timedelta(1)) / \
                                             sales_pd_gb['ORDER_SPK']['nunique']

    # Recencecy
    customer_df['recency'] = pd.to_numeric((sales_pd_gb['ORDER_DATE']['max'].max() - sales_pd_gb['ORDER_DATE']['max']).dt.days, downcast='integer')

    # Calculate total number of orders
    customer_df['total_number_of_orders'] = sales_pd_gb['ORDER_SPK']['nunique'] 

    # # Calculate average number of orders per customer
    # customer_df['average_number_of_orders_per_customer'] = sales_pd_gb['ORDER_SPK']['nunique'] / \
    #                                           ((sales_pd_gb['ORDER_DATE']['max'] - sales_pd_gb['ORDER_DATE']['min']) / timedelta(1))
    # customer_df[customer_df['average_number_of_orders_per_customer'] == np.inf] = 0.001                                             

    # Calculate average order value
    customer_df['average_order_value'] = sales_pd_gb['UNIT_GROSS_REVENUE_LOCAL']['sum'] / \
                                         sales_pd_gb['ORDER_SPK']['nunique']

    # Average items per order
    customer_df['average_items_per_order'] = sales_pd_gb['UNIT_QUANTITY']['sum'] / \
                                             sales_pd_gb['ORDER_SPK']['nunique']

    # Average price per item
    customer_df['average_price_per_item'] = sales_pd_gb['UNIT_GROSS_REVENUE_LOCAL']['sum'] / \
                                            sales_pd_gb['UNIT_QUANTITY']['sum']

    # Merge in average number of unique skus per order
    customer_df = pd.merge(customer_df, average_unique_skus, on='CUSTOMER_SPK', how='left')

    # Average level of discount
    customer_df['average_discount_level'] = abs(sales_pd_gb['UNIT_DISCOUNT_TAX_EXCL_USD']['sum']) /\
                                            (abs(sales_pd_gb['UNIT_DISCOUNT_TAX_EXCL_USD']['sum']) + sales_pd_gb['UNIT_GROSS_REVENUE_LOCAL']['sum'])

    # Specific discount flag percentages
    customer_df['flash_sale_percentage'] = sales_pd_gb['sales_flag']['sum'] / \
                                           sales_pd_gb['line_count']['sum']  # Double check with Rob
    # customer_df['price_promo_percentage']=sales_gb['PRICE_PROMO_FLAG']['sum']/sales_gb['line_count']['sum']
    # customer_df['listed_price_reduction_flag']=sales_gb['listed_price_reduction_flag']['sum']/sales_gb['line_count']['sum']
    # print(customer_df.head())
    return customer_df

def browsing_category(pd_df, medium_list, source_list):
    """Function to create a browsing behaviour dataframe which
    consists of only top mediums and sources.

    Args:
        pd_df(dataframe): Combined dataframe for raw_orders and raw_sessions
        medium_list(list): Limit medium to top categories
        source_list(list): Limit source to top categories
    Returns:
        browsing_behaviour_df(dataframe): Combined dataframe of Source, Medium, Device
        customer_total_page_views_gb(dataframe): Grouped browsing_behaviour_df on individual customers
    """
    browsing_behaviour_df = pd_df[['CUSTOMER_SPK', 'SOURCE', 'MEDIUM', 'DEVICECATEGORY']]
    
    #Limit medium to top categories
    browsing_behaviour_df['MEDIUMCATEGORY']=np.where(browsing_behaviour_df['MEDIUM'].isin(medium_list),browsing_behaviour_df['MEDIUM'],'other')

    #Limit source to top categories
    browsing_behaviour_df['SOURCECATEGORY']=np.where(browsing_behaviour_df['SOURCE'].isin(source_list),browsing_behaviour_df['SOURCE'],'other')

    customer_total_page_views_gb = browsing_behaviour_df.groupby('CUSTOMER_SPK').size().reset_index().sort_values(0, ascending=False)
    customer_total_page_views_gb = customer_total_page_views_gb.rename(columns={0: 'TOTAL_VIEWS'})

    return browsing_behaviour_df, customer_total_page_views_gb

def clean_behaviour_measure(browsing_behaviour_df, customer_total_page_views_gb, browsing_variable):
    """Function to create a browsing behaviour measure for each customers.

    Args:
        browsing_behaviour_df(dataframe): Combined dataframe of Source, Medium, Device
        customer_total_page_views_gb(dataframe): Grouped browsing_behaviour_df on individual customers
        browsing_variable : DEVICECATEGORY, MEDIUMCATEGORY, SOURCECATEGORY
    Returns:
        browsing_measure_gb: Affinity scores of each customer towards different browsing medium
                            (which could be Device, Medium and Sources)
    """

    browsing_measure_gb = browsing_behaviour_df.groupby(['CUSTOMER_SPK', browsing_variable]).size().reset_index()
    browsing_measure_gb = browsing_measure_gb.rename(columns={0: 'PAGEVIEWS'})
    # Merge total page views into gb
    browsing_measure_gb = pd.merge(browsing_measure_gb, customer_total_page_views_gb, on='CUSTOMER_SPK', how='left')

    # Calculate % total page views
    browsing_measure_gb['percentage_total_page_views'] = browsing_measure_gb['PAGEVIEWS'] / browsing_measure_gb[
        'TOTAL_VIEWS']

    # Drop unnecessary columns
    browsing_measure_gb = browsing_measure_gb.drop(['PAGEVIEWS', 'TOTAL_VIEWS'], axis=1)

    # Rename columns (for merge)
    browsing_measure_gb.rename(columns={browsing_variable: 'variable', 'percentage_total_page_views': 'value'}, inplace=True)

    return browsing_measure_gb

def browsing_pivot(browsing_behaviour_df, customer_total_page_views_gb):
    """Function to create a pivot table showcasing the affinity of customers
        towards each browsing medium (which could be Device, Medium and Sources)

    Args:
        browsing_behaviour_df(dataframe): Combined dataframe of Source, Medium, Device
        customer_total_page_views_gb(dataframe): Grouped browsing_behaviour_df on individual customers
        
    Returns:
        browsing_pivot: Pivot table showing affinity scores of each customer towards different browsing medium
                            (which could be Device, Medium and Sources)
    """

    # Create browsing behaviour outputs
    device_gb = clean_behaviour_measure(browsing_behaviour_df, customer_total_page_views_gb, 'DEVICECATEGORY')
    medium_gb = clean_behaviour_measure(browsing_behaviour_df, customer_total_page_views_gb, 'MEDIUMCATEGORY')
    source_gb = clean_behaviour_measure(browsing_behaviour_df, customer_total_page_views_gb, 'SOURCECATEGORY')

    # Create browsing data input
    behaviour_concat = pd.concat([device_gb, medium_gb, source_gb])
    behaviour_concat.fillna(0, inplace=True)
    browsing_pivot = pd.pivot_table(behaviour_concat, index='CUSTOMER_SPK', columns='variable', values='value', aggfunc=np.sum).reset_index().fillna(0)
    # print(browsing_pivot.head(2))

    return browsing_pivot

def algo_data(customer_df, browsing_pivot):
    """Function to create input filed to be used by clustering algorithms.

    Args:
        customer_df(dataframe): KPIs(e.g. AOV, AOF etc) for each individual customer.
        browsing_pivot(dataframe): Pivot table showing affinity scores of each customer 
                                    towards different browsing medium
                                    (which could be Device, Medium and Sources)
        
    Returns:
        input_df(dataframe): Combined input data to be fed to the clustering algo
        data_scaled(dataframe): Input data scaled and normalized
    """
    # Identify customers that are within all the measures
    customer_list = list(customer_df['CUSTOMER_SPK'].unique())
    browsing_list = list(browsing_pivot.CUSTOMER_SPK.unique())
    final_customer_list = set(customer_list).intersection(browsing_list)

    # Merge customer, product and browsing into one df
    input_df = pd.merge(customer_df, browsing_pivot, on='CUSTOMER_SPK')
    # Limit data to customers with transaction, browsing + product data
    input_df = input_df[input_df['CUSTOMER_SPK'].isin(final_customer_list)]
    input_df = input_df[(input_df['average_order_value'] > 0) & (input_df['average_order_frequency'] > 0)]

    total_cols = list(input_df.columns)
    total_cols.remove('CUSTOMER_SPK')
    data = input_df[total_cols]
    data_scaled = normalize(data)
    data_scaled = pd.DataFrame(data_scaled, columns=data.columns)
    # print(input_df.head())
    # print(data_scaled.head())
    return input_df, data_scaled

def generate_cluster_inputs(initial_cluster_df):
    """Function to create output from clustering ready to be used by PBI reports.

    Args:
        initial_cluster_df(dataframe): Clustering results generated from Agglomerative clustering
        
    Returns:
        individual_cluster_gb(dataframe): Clustering results to be used by PBI reports 
        
    """
    individual_cluster_gb = initial_cluster_df.groupby('Cluster').agg(['mean','std'])
    individual_cluster_gb = individual_cluster_gb.reset_index(drop=True)
    individual_cluster_gb.columns = individual_cluster_gb.columns.map('-'.join).str.strip('-')
    individual_cluster_gb['CUSTOMER_SPK'] = initial_cluster_df.groupby('Cluster').agg({'CUSTOMER_SPK':pd.Series.nunique}).reset_index(drop=True)

    return individual_cluster_gb