import json
from bson.json_util import dumps
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