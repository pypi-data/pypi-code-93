import datetime
import json
import pymongo
# import dns.resolver
from pymongo import MongoClient
from pymongo import collection
from pymongo import ASCENDING,DESCENDING
from bson.json_util import dumps
from pymongo.common import CONNECT_TIMEOUT, RETRY_WRITES

# get cart data with price and delivery cahrges

def get_cart_data(uuid):
	cart_data=calculate_price_and_delivery_charges(uuid)
	return cart_data

# Mongodb authentication

def mongodb_auth():
    uri="mongodb+srv://adityasingh98:adityasingh98@kisaan.kwm8f.mongodb.net/kisaan_corp?retryWrites=true&w=majority"
    client=MongoClient(uri,ConnectTimeoutMS=1000,retryWrites=True)
    return client

# ************************* Calculate prices with unit conversion *******************************

def calculate_price(unit,unit_price,weight):
    unit=str(unit)
    unit_price=str(unit_price)
    weight=str(weight)

    if(len(unit.split(" "))==2):
        custom_unit_value,unit=unit.split(" ")
    else:
        custom_unit_value="1"

    weight_value,weight_unit=weight.split(" ")
    weight_unit_standard={"kg":1,"gm":1000,"liter":1,"ml":1000,"dozen":1,"piece":12}
    if(weight_unit_standard[unit]<weight_unit_standard[weight_unit]):
        price=eval(weight_value)*eval(unit_price)/(weight_unit_standard[unit]/eval(custom_unit_value))
        return price
    elif(weight_unit_standard[unit]==weight_unit_standard[weight_unit]):
        price=eval(weight_value)*eval(unit_price)/eval(custom_unit_value)
        return price
    elif(weight_unit_standard[unit]>weight_unit_standard[weight_unit]):
        return eval(weight_value)*eval(unit_price)*(weight_unit_standard[unit]/eval(custom_unit_value))


# **************************check subscription frequency *************************************************


def check_subscription_frequency(subscription_frequency,recurring_delivery_charges):
    for sub_num in range(len(recurring_delivery_charges)):
        if subscription_frequency in recurring_delivery_charges[sub_num].values():
            return {"status":True,"subscription_data":recurring_delivery_charges[sub_num]}
        else:
            return {"status":False,"subscription_data":recurring_delivery_charges[sub_num]}
    return {"status":False,"subscription_data":{}}



# ************************* Calculate delivery charges ***************************************************
def calculate_delivery_charges(cluster_id,pricing_details,client):
    cluster=client.kisaan_webapp_prod.delivery_charge
    pipeline=[
        {"$match":{"cluster_id":cluster_id}}
    ]
    aggregation=cluster.aggregate(pipeline)
    delivery_charge=dumps(aggregation,indent=2).replace("\n","")
    delivery_charge=json.loads(delivery_charge)

    delivery_charge=delivery_charge[0]
    # print(delivery_charge)
    delivery_charge=delivery_charge["delivery_charges"]
    try:
        for i in range(len(pricing_details["recurring_delivery_charges"])):
            print(pricing_details["recurring_delivery_charges"][i])
            for j in range(len(delivery_charge)):
                print(delivery_charge[j])
                recurring_amount=pricing_details["recurring_delivery_charges"][i]["recurring_amount"]
                if(delivery_charge[j]["condition"]=="exclusive-inclusive"):
                    if(recurring_amount>delivery_charge[j]["min_value"] and recurring_amount<=delivery_charge[j]["max_value"]):
                        pricing_details["recurring_delivery_charges"][i]["delivery_charge"]=delivery_charge[j]["delivery_charge"]
                elif(delivery_charge[j]["condition"]=="greater-than"):
                    if(recurring_amount>delivery_charge[j]["value"]):
                        pricing_details["recurring_delivery_charges"][i]["delivery_charge"]=0
    except:
        print("no recurrinng order")

    total_amount=pricing_details["total_amount"]
    for k in range(len(delivery_charge)):
        if(delivery_charge[k]["condition"]=="exclusive-inclusive"):
            if(total_amount>delivery_charge[k]["min_value"] and total_amount<=delivery_charge[k]["max_value"]):
                pricing_details["today_delivery_charges"]=delivery_charge[k]["delivery_charge"]
        elif(delivery_charge[k]["condition"]=="greater-than"):
            if(total_amount>delivery_charge[k]["value"]):
                pricing_details["today_delivery_charges"]=delivery_charge[k]["delivery_charge"]
    
    discount=0
    # print(pricing_details)
    today_delivery_charges=pricing_details["today_delivery_charges"]
    total_payable_amount=total_amount+today_delivery_charges-discount
    pricing_details["discount"]=discount
    pricing_details["total_payable_amount"]=total_payable_amount
    return pricing_details
        



def calculate_price_and_delivery_charges(uuid):
    start_timing=datetime.datetime.now()
    client=mongodb_auth()
    cluster=client.kisaan_webapp_prod.cart
    pipeline=[
        {"$match":{"uuid":uuid,"is_cart_active":True,
        "expired":False}},
        {"$project":{"price_details":0}}
    ]

    aggregation=cluster.aggregate(pipeline)
    cart=dumps(aggregation,indent=2).replace("\n","")
    cart=json.loads(cart)
    print(len(cart))

    cart_data=cart[0]
    print(cart_data)
    try:
        cart_data.pop("price_details")
    except:
        print("price_details not in dict")
    print(type(cart_data))
    products=cart_data["products"]
    cluster_id=cart_data["cluster_id"]
    cart_data["product_count"]=len(products)
    total_amount=0
    one_time_amount=0

    pricing_details={"recurring_delivery_charges":[]}
    for i in range(len(products)):
        print(products[i])
        if(products[i]["is_subscription"]==False):
            if(products[i]["type"]=="simple"):
                print("simple")
                item_count=products[i]["item_count"]
                price=products[i]["product_details"]["details"][0]["pricing_details"]["current_price"]
                current_amount=int(item_count)*price
                print("-------------------------------------------------------")
                print(current_amount)
                print(type(current_amount))
                
                print(one_time_amount)
                print(type(one_time_amount))
                
                one_time_amount=one_time_amount+current_amount
                total_amount=total_amount+current_amount
            elif(products[i]["type"]=="simple_variation"):
                print("simple variation")
                item_count=products[i]["item_count"]
                price=products[i]["product_details"]["details"][0]["pricing_details"]["current_price"]
                current_amount=item_count*price
                print(current_amount)
                one_time_amount=one_time_amount+current_amount
                total_amount=total_amount+current_amount
                # print(one_time_amount)
                # print(total_amount)
            elif(products[i]["type"]=="double_variation"):
                print("double variation")
                item_count=products[i]["item_count"]
                unit_price=products[i]["product_details"]["details"][0]["pricing_details"]["unit_price"]
                unit=products[i]["product_details"]["details"][0]["pricing_details"]["unit"]
                option=products[i]["product_details"]["details"][0]["attribute"]["option"]
                # print(calculate_price(unit=unit,unit_price=unit_price,weight=option))
                current_amount=item_count*calculate_price(unit=unit,unit_price=unit_price,weight=option)
                print(current_amount)
                one_time_amount=one_time_amount+current_amount
                total_amount=total_amount+current_amount
                # print(one_time_amount)
                # print(total_amount)
                

        else:
            if(products[i]["type"]=="simple"):
                subscription_frequency=products[i]["subscription_frequency"]
                item_count=products[i]["item_count"]
                price=products[i]["product_details"]["details"][0]["pricing_details"]["current_price"]
                product_price=item_count*price
                total_amount=total_amount+product_price
                subscription_availability=check_subscription_frequency(subscription_frequency,pricing_details["recurring_delivery_charges"])
                # print(subscription_availability)
                if subscription_availability["status"]==False:
                    pricing_details["recurring_delivery_charges"].append(
                        {
                            "subscription_frequency":subscription_frequency,
                            "recurring_amount":product_price
                        }
                    )
                else:
                    pricing_details["recurring_delivery_charges"].remove(subscription_availability["subscription_data"])
                    subscription_availability["subscription_data"]["recurring_amount"]=subscription_availability["recurring_amount"]+product_price
                    pricing_details["recurring_delivery_charges"].append(subscription_availability["subscription_data"])
                
            elif(products[i]["type"]=="simple_variation"):
                subscription_frequency=products[i]["subscription_frequency"]
                item_count=products[i]["item_count"]
                price=products[i]["product_details"]["details"][0]["pricing_details"]["current_price"]
                product_price=item_count*price
                total_amount=total_amount+product_price
                subscription_availability=check_subscription_frequency(subscription_frequency,pricing_details["recurring_delivery_charges"])
                if subscription_availability["status"]==False:
                    pricing_details["recurring_delivery_charges"].append(
                        {
                            "subscription_frequency":subscription_frequency,
                            "recurring_amount":product_price
                        }
                    )
                else:
                    pricing_details["recurring_delivery_charges"].remove(subscription_availability["subscription_data"])
                    subscription_availability["subscription_data"]["recurring_amount"]=subscription_availability["recurring_amount"]+product_price
                    pricing_details["recurring_delivery_charges"].append(subscription_availability["subscription_data"])
            elif(products[i]["type"]=="double_variation"):
                subscription_frequency=products[i]["subscription_frequency"]
                item_count=products[i]["item_count"]
                unit_price=products[i]["product_details"]["details"][0]["pricing_details"]["unit_price"]
                unit=products[i]["product_details"]["details"][0]["pricing_details"]["unit"]
                option=products[i]["product_details"]["details"][0]["attribute"]["option"]
                # print("-----------------------")
                print(calculate_price(unit=unit,unit_price=unit_price,weight=option))
                one_time_amount=one_time_amount+item_count*calculate_price(unit=unit,unit_price=unit_price,weight=option)
                total_amount=total_amount+product_price
                subscription_availability=check_subscription_frequency(subscription_frequency,pricing_details["recurring_delivery_charges"])
                if subscription_availability["status"]==False:
                    pricing_details["recurring_delivery_charges"].append(
                        {
                            "subscription_frequency":subscription_frequency,
                            "recurring_amount":product_price
                        }
                    )
                else:
                    pricing_details["recurring_delivery_charges"].remove(subscription_availability["subscription_data"])
                    subscription_availability["subscription_data"]["recurring_amount"]=subscription_availability["recurring_amount"]+product_price
                    pricing_details["recurring_delivery_charges"].append(subscription_availability["subscription_data"])

    # print(total_amount)
    # print(one_time_amount)

    pricing_details["total_amount"]=total_amount
    pricing_details["one_time_amount"]=one_time_amount
    if(len(pricing_details["recurring_delivery_charges"])==0):
        pricing_details.pop("recurring_delivery_charges")

    pricing_details=calculate_delivery_charges(cluster_id=cluster_id,pricing_details=pricing_details,client=client)
    price_addition_result=cluster.update({"uuid":uuid,"is_cart_active":True,
        "expired":False},{"$set":{"price_details":pricing_details,"product_count":cart_data["product_count"]}})
    print(price_addition_result)
    cart_data["price_details"]=pricing_details
    # print(cart_data)
    end_timing=datetime.datetime.now()
    print(f"total time taking to finish a program{end_timing-start_timing}")
    return cart_data