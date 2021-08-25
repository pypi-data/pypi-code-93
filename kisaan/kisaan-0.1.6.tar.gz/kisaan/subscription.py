# *********************** Find unique subscription frequency in products *********************

def find_different_frequency(products):
    frequency=[]
    for product in products:
        frequency.append(product["subscription_frequency"])
    frequency=list(set(frequency))
    return frequency

# ************************* filter specific frequency type products ***************************

async def find_specific_frequency_products(products,frequency):
    filtered_products=[]
    for product in products:
        if(product["subscription_frequency"]==frequency):
            filtered_products.append(product)
    return filtered_products     

# **************************check subscription frequency *************************************************
"""
This Function check if specific frequency prices is present or not in recurring delivery charges
if already present then update the recurring amount
otherwise add new subscription amount and subscription frequency
"""
async def check_subscription_frequency(subscription_frequency,recurring_delivery_charges):
    for sub_num in range(len(recurring_delivery_charges)):
        if subscription_frequency in recurring_delivery_charges[sub_num].values():
            return {"status":True,"subscription_data":recurring_delivery_charges[sub_num]}
        else:
            return {"status":False,"subscription_data":recurring_delivery_charges[sub_num]}
    return {"status":False,"subscription_data":{}}    