'''
Created on 29 Apr 2021

@author: jacklok
'''
from trexlib.utils.string_util import is_empty, is_not_empty
from datetime import datetime
import logging

logger = logging.getLogger('helper')


def update_reward_summary_with_new_reward(existing_reward_summary, reward_details):
    reward_summary              = existing_reward_summary
    reward_format               = reward_details.get('reward_format')
    reward_amount               = reward_details.get('reward_amount')
    used_reward_amount          = reward_details.get('used_reward_amount')
    latest_expiry_date          = datetime.strptime(reward_details.get('expiry_date'), '%d-%m-%Y').date()
    
    
    existing_latest_expiry_date = None
    new_latest_expiry_date      = latest_expiry_date
    
    if is_empty(reward_summary):
        reward_balance = reward_amount - used_reward_amount
        reward_summary = {
                            reward_format:{
                                            'latest_expiry_date'    : new_latest_expiry_date.strftime('%d-%m-%Y'),
                                            'amount'                : reward_amount
                                            }
                                        
                            }
    else:
        reward_summary_by_reward_format = reward_summary.get(reward_format)
        
        if reward_summary_by_reward_format is None:
            reward_summary_by_reward_format = {
                                                'amount': 0,
                                                }
            new_latest_expiry_date = latest_expiry_date
        else:
        
            existing_latest_expiry_date = reward_summary_by_reward_format.get('latest_expiry_date')
            existing_latest_expiry_date = latest_expiry_date
            
            if latest_expiry_date > existing_latest_expiry_date:  
                new_latest_expiry_date = existing_latest_expiry_date
                
                
        
        reward_summary_by_reward_format['latest_expiry_date']   = new_latest_expiry_date.strftime('%d-%m-%Y')
        
        reward_balance = reward_amount - used_reward_amount
        
        reward_summary_by_reward_format['amount']               = reward_summary_by_reward_format['amount'] + reward_balance
        
        reward_summary[reward_format] = reward_summary_by_reward_format
        
    return reward_summary

def update_reward_summary_with_reverted_reward(existing_reward_summary, reward_details):
    reward_summary              = existing_reward_summary
    reward_format               = reward_details.get('reward_format')
    reward_amount               = reward_details.get('reward_amount')
    
    logger.debug('update_reward_summary_with_reverted_reward: reward_format=%s', reward_format)
    logger.debug('update_reward_summary_with_reverted_reward: reward_amount=%s', reward_amount)
    
    existing_latest_expiry_date = None
    
    if is_not_empty(reward_summary):
        reward_summary_by_reward_format = reward_summary.get(reward_format)
        
        logger.debug('update_reward_summary_with_reverted_reward: reward_summary_by_reward_format=%s', reward_summary_by_reward_format)
        if reward_summary_by_reward_format:
            existing_latest_expiry_date = reward_summary_by_reward_format.get('latest_expiry_date')
            existing_latest_expiry_date = datetime.strptime(existing_latest_expiry_date, '%d-%m-%Y').date()
            
            final_reward_amount                         = reward_summary_by_reward_format['amount'] - reward_amount
            reward_summary_by_reward_format['amount']   = final_reward_amount
            reward_summary[reward_format]               = reward_summary_by_reward_format
            
            if final_reward_amount==0:
                del reward_summary[reward_format]
        
    return reward_summary

def update_customer_entiteld_voucher_summary_with_new_voucher(customer_entitled_voucher_summary, voucher_key, voucher_label, voucher_image_url, redeem_info_list):
    voucher_summary     = customer_entitled_voucher_summary.get(voucher_key)
    if voucher_summary:
        customer_entitled_voucher_summary[voucher_key]['redeem_info_list'].extend(redeem_info_list)  
    else:
        voucher_summary = {
                            'label'             : voucher_label,
                            'image_url'         : voucher_image_url,
                            'redeem_info_list'  : redeem_info_list 
                            
                            }
        customer_entitled_voucher_summary[voucher_key] = voucher_summary

    return customer_entitled_voucher_summary

'''
customer entitled_voucher_summary format is
{
    voucher_key : 
                label : xxxxxx,
                image_url : xxxxxxxx,
                redeem_info_list :    [
                                        {
                                            redeem_code: xxxxxxxxxx,
                                            effective_date : xxxxxxxx,
                                            expiry_date : xxxxxxxx
                                        }
                                    ]

}

'''
def update_customer_entiteld_voucher_summary_after_reverted(customer_entitled_voucher_summary, reverted_customer_voucher):
    if customer_entitled_voucher_summary:
        voucher_key                             = reverted_customer_voucher.entitled_voucher_key
        redeem_code_of_reverting_voucher        = reverted_customer_voucher.redeem_code
        
        redeem_info_list = customer_entitled_voucher_summary.get(voucher_key)
        
        if redeem_info_list:
            new_redeem_info_list = []
            for redeem_info in redeem_info_list:
                if redeem_info.get('redeem_code')!=redeem_code_of_reverting_voucher:
                    new_redeem_info_list.append(redeem_info)
            
            if len(new_redeem_info_list) ==0:
                del customer_entitled_voucher_summary[voucher_key]
            else:
                customer_entitled_voucher_summary[voucher_key] = redeem_info_list
    return customer_entitled_voucher_summary
    
    
def update_customer_entiteld_voucher_summary_after_redeemed(entitled_voucher_summary, redeemed_entitled_voucher):
    if entitled_voucher_summary:
        voucher_key = redeemed_entitled_voucher.entitled_voucher.urlsafe().decode('utf-8')
        voucher_count = entitled_voucher_summary.get(voucher_key)
        if voucher_count:
            entitled_voucher_summary[voucher_key] = voucher_count - 1    

    return entitled_voucher_summary
      