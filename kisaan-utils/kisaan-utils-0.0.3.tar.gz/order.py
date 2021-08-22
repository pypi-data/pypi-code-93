
def is_contain_subscription(products):
    for product in products:
        if(product["is_subscription"]==True):
            return True
    return False 

def is_matched_price(cart_products,original_product):
    original_product_id=original_product["product_id"]
    original_variation_id=original_product["product_details"]["details"][0]["variation_id"]

    matched_products=[]
    for cart_product in cart_products:
        if(cart_product["product_id"]==original_product_id and
        cart_product["product_details"]["details"][0]["variation_id"]==original_variation_id):
            matched_products.append(cart_product)
    print("_________")
    print(matched_products)        

    try:
        matched_products_current_price=matched_products[0]["product_details"]["details"][0]["pricing_details"]["current_price"]
    except:
        print("No current price found in matched products")	

    matched_products_unit_price=matched_products[0]["product_details"]["details"][0]["pricing_details"]["unit_price"]
    try:
        original_product_current_price=original_product["product_details"]["details"][0]["pricing_details"]["current_price"]
    except:
        print("No current price found original product")	
    original_product_unit_price=original_product["product_details"]["details"][0]["pricing_details"]["unit_price"]
    

    if(matched_products[0]["type"]!="double_variation"):
        if(matched_products_current_price==original_product_current_price and
        matched_products_unit_price==original_product_unit_price):
            return True
    else:
        if(matched_products_unit_price==original_product_unit_price):
            return True
    return False		
