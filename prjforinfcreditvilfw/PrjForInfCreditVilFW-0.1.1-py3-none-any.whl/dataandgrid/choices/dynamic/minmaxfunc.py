'''
Created on Dec 16, 2017

@author: fan

copied over from Function.py previous JMP codes

import dataandgrid.choices.dynamic.minmaxfunc as minmaxfunc
'''

import logging
import numpy as np
import modelhh.functions.constraints as constraints

logger = logging.getLogger(__name__)


def minmax_KB_Informal_Borrow(d=0.1, Y_minCst=5, Bstart=-1, RB=1.1):
    """
    Does not consider collateral constraint for formal borrowing only

     -- (B_min, K_max)
        --    --
            --        -- upper_slope (b_max_upper)
                --            --
       lower_slope  --              -- (B_max, K_mid)
       (b_min_lower)    --          --  
                            --      --
                                --  --
                                   --- (B_max, K_min)
        
    B_min = borrow_B_min
    B_min = borrow_B_min
    
    Parameters
    ----------
    Bstart: minimal borrowing required
        in multinomial choice logit, every choice is feasible,
        so if a choice is chosen, even if it is optimal to borrow 0 from
        that category, need to pay the category fixed cost and minimal
        borrowing or savings.
    """

    logger.debug('Z0. Prep Variables')
    rB = RB - 1

    logger.debug('Z1. Cash on Hand without Fixed Costs')
    Y_minCst = constraints.get_consumption_constraint(Y_minCst, False)

    logger.debug('A. Normal Case, triangle of choices, B_max > B_min, cash >=0')

    logger.debug('A1. Lower Right Generic')
    B_max = Bstart
    K_min = (-Bstart) / (1 - d)

    logger.debug('A2. Upper Left individual specific based on Y_minCst')
    ratB = (1 + rB) / (d + rB)
    B_min_i = - (Y_minCst) * ratB * (1 - d)
    K_max_i = (Y_minCst) * ratB

    logger.debug('B. Special Case, if B_max < B_min (that implices K_Max > K_min\
                     single point top left in choice set\
                         or\
                     signle point at origin')
    B_max_i = np.maximum(B_max, B_min_i)
    K_min_i = np.minimum(K_max_i, K_min)

    return [[[K_min_i, K_max_i],
             [B_min_i, B_max_i]],
            Y_minCst, RB]


def minmax_KB_Borrow(DELTA_DEPRE=0.1, Y_minCst=0, Bstart=0, RB=0, Z=None, RZ=None):
    """
    Does not consider collateral constraint for formal borrowing only

     -- (B_min, K_max)
        --    --
            --        -- upper_slope (b_max_upper)
                --            --
       lower_slope  --              -- (B_max, K_mid)
       (b_min_lower)    --          --  
                            --      --
                                --  --
                                   --- (B_max, K_min)
        
    B_min = borrow_B_min
    B_min = borrow_B_min
    
    Parameters
    ----------
    Bstart: minimal borrowing required
        in multinomial choice logit, every choice is feasible,
        so if a choice is chosen, even if it is optimal to borrow 0 from
        that category, need to pay the category fixed cost and minimal
        borrowing or savings.
    """

    logger.debug('\nDELTA_DEPRE=%s\nBstart=%s\nRB=%s\nZ=%s\nRZ=%s',
                 DELTA_DEPRE, Bstart, RB, Z, RZ)
    logger.debug('Y_minCst:\n%s', Y_minCst)

    logger.debug('0. Prep Variables')
    d = DELTA_DEPRE
    rB = RB - 1
    if (Z is not None):
        rZ = RZ - 1

    logger.debug('A. Cash on Hand without Fixed Costs')
    Y_minCst = constraints.get_consumption_constraint(Y_minCst, False)

    logger.debug('B1. Maximum Borrowing (B_min) Feasible Given Cash on Hand and Rates,')
    ratB = (1 + rB) / (d + rB)
    borrow_B_min = - (Y_minCst) * ratB * (1 - d)

    logger.debug('B2. Minimal Borrowing (B_max) required')
    borrow_B_max = Bstart
    # borrow_B_max = -float(abs(Bstart))
    if (Z is not None):
        borrow_B_min += borrow_B_min + (-Z * ratB * ((d + rZ) / (1 + rZ)))

    logger.debug('B3. if B_max < B_min, set B_max = B_min, single dot choice point')
    # if Bstart = -1, but Y_minCst = 0, then max borrow < min borrow
    borrow_B_max = np.maximum(borrow_B_max, borrow_B_min)

    logger.debug('C1. Minimum K (K_min) Feasible Given Cash on Hand and Rates')
    # k_min
    #    = (-Bstart) / (1 - d)
    #        for having enough capital to repay minimal borrowing required
    kapitalnext_min = (-Bstart) / (1 - d)

    logger.debug('C2. Maximum K (K_max) Feasible Given Cash on Hand and Rates')
    kapitalnext_max = (Y_minCst) * ratB
    if (Z is not None):
        try:
            kapitalnext_min += np.maximum((-Z) / (1 - d), 0)
        except:
            'If formula, k*gamma'
            kapitalnext_min += (-Z) / (1 - d)

        kapitalnext_max += -(Z * (rB - rZ)) / ((1 + rZ) * (d + rB))

    logger.debug('B3. Minimal Borrowing (B_max) required')
    # if Bstart = -1, then kapitalnext_min = 1/(1-d), but with Y_minCst = 0, kap_max = 0, so then max < min
    # in this case, even though there is minimal borrowing requirement, not valid because can't pay for it'
    kapitalnext_min = np.minimum(kapitalnext_max, kapitalnext_min)

    'Z<0 means there is minimum borrowing, '
    'If z > 0, has minimum savings, min will be 0'

    if (Z is not None):
        Y_minCst = Y_minCst + (-Z / (1 + rZ))

    #     logger.debug('RB:%s',RB)
    #     logger.debug('cur_minmax:\n%s',
    #                  np.concatenate((kapitalnext_min, kapitalnext_max,
    #                                  borrow_B_min, borrow_B_max,
    #                                  Y_minCst)))

    if (np.isscalar(kapitalnext_min)):
        kapitalnext_min = np.zeros(kapitalnext_max.shape) + kapitalnext_min

    #     The algorithm above for joint formal + informal borrow is incorrect
    #     when Y_minCst = 0. If Y_minCst for this category, no resource, can not borrow_B_max
    #     can not have K. and when borrowing, can not have positive number.

    if (np.isscalar(Y_minCst)):
        if (borrow_B_min > 0):
            kapitalnext_min = 0
            kapitalnext_max = 0
            borrow_B_min = -0
            borrow_B_max = -0
    else:
        borrow_B_min_pos = (borrow_B_min > 0)
        kapitalnext_min[borrow_B_min_pos] = 0
        kapitalnext_max[borrow_B_min_pos] = 0
        borrow_B_min[borrow_B_min_pos] = -0
        borrow_B_max[borrow_B_min_pos] = -0

    return [[[kapitalnext_min, kapitalnext_max],
             [borrow_B_min, borrow_B_max]],
            Y_minCst, RB]


def minmax_KB_Save(DELTA_DEPRE=0.1, Y_minCst=0, Bstart=0, RB=0, Z=None, RZ=None):
    """
    Parameters
    ----------
    Bstart: minimal Savings required
        in multinomial choice logit, every choice is feasible,
        so if a choice is chosen, even if it is optimal to borrow 0 from
        that category, need to pay the category fixed cost and minimal
        borrowing or savings.    
    """

    assume_informal_lending_full_repay_always = True

    d = DELTA_DEPRE
    Y_minCst = constraints.get_consumption_constraint(Y_minCst, False)

    rB = RB - 1
    if (Z is not None):
        rZ = RZ - 1

    # Savings min and max determined first, save_B_min < save_B_max
    save_B_min = Bstart
    save_B_max = (Y_minCst) * (1 + rB)
    if (Z is not None):

        # Y_minCst: coh minus fixed costs
        # Y_minCst - Z / (1 + rZ):
        #     coh minus fixed costs + how much was borrowed from formal sources to add to coh
        # Y_minCst - Z / (1 + rZ) + Z/(1 - d):  
        #     coh minus fixed costs + how much was borrowed from formal sources to add to coh
        #     + minimal commitment towards k to enable repayment in b next period.
        if (assume_informal_lending_full_repay_always is True):
            # Assuming that informal lending will be fully repaid and can cover formal loans
            save_B_max = (Y_minCst - Z / (1 + rZ)) * (1 + rB)
        else:
            # considering that need to have physical capital for formal loan repayment
            save_B_max = (Y_minCst - Z / (1 + rZ) + Z / (1 - d)) * (1 + rB)

    save_B_min = np.minimum(save_B_max, save_B_min)

    # Kapital
    kapitalnext_min = 0
    kapitalnext_max = Y_minCst - save_B_min / (1 + rB)
    if (Z is not None):

        if (assume_informal_lending_full_repay_always is True):
            pass
        else:
            # have to have physical capital for loan repayment
            kapitalnext_min = (-Z) / (1 - d)

        kapitalnext_max = (Y_minCst - Z / (1 + rZ)) - save_B_min / (1 + rB)

    """
    The slope  of the savings triangle should be the savings rate or rather 1/（1+rB)
    
    see the below equation, the problem is with Z/(1-d), when we add to min capital
    level Z/(1-d) that is pushing the whole triangle up, B_max save need to go up as well. 
            
    [Y_minCst -  Bstart / (1 + rB)]
    /
    [(Y_minCst) * (1 + rB)] - Bstart 
        
        
    [Y_minCst - Z/(1 + rZ) - save_B_min/(1 + rB) + (Z)/(1 - d)] 
    /
    [(Y_minCst - Z/(1 + rZ)) * (1 + rB) - Bstart] 
    """

    if (Z is not None):
        Y_minCst = Y_minCst + (-Z / (1 + rZ))

    if (np.isscalar(kapitalnext_min)):
        kapitalnext_min = np.zeros(kapitalnext_max.shape) + kapitalnext_min

    return [[[kapitalnext_min, kapitalnext_max],
             [save_B_min, save_B_max]],
            Y_minCst, RB]


def minmax_KB_save_fbis_a(K_min_br, Y_minCst, RB):
    """
    Solve for alpha + beta*x = y and y = lambda, find x
    
    Parameters
    ----------
    K_min_br: array
        lambda = K_min_br,     
    Y_minCst: array
        alpha = Y_minCst
    RB: scalar
        beta = -1/RB, RB is informal borrowing rate    
    """

    save_B_max_wthKminbr = (K_min_br - Y_minCst) / (-1 / RB)

    return save_B_max_wthKminbr


def minmax_KB_save_fbis_b(K_vec, Y_minCst, RB):
    """
    Solve for b: k = alpha + beta*b
    
    Given K vector, what is the upper slope current K's corresponding B?
    
    Parameters
    ----------
    K_vec: array
        K_vec = k     
    Y_minCst: array
        alpha = Y_minCst
    RB: scalar
        beta = -1/RB, RB is informal borrowing rate        
    """

    borr_B_max_upper = (K_vec - Y_minCst) / (-1 / RB)

    return borr_B_max_upper

    """
    
    Situation 1:
        zero coh
        
        Borrow 10 dollar today
        tomorrow pay back 10(R) required
            
        if you use that money to invest in K, is that OK?
        not really, because K next period is only worth (1-d)K
        
        so you would owe 10R, and only have (1-d)10 if K == B
        
        so you would never borrow B to finance to finance K fully like this, not possible    
    
    Situation 2:
        supppose not every dollar of K' needs to be borrowed, you have some 
        income this period, some cash, non-zero cash from before. Could borrowing
        help?
        
        If you can not borrow, you invest whatever you think is optimal into K.
        any amount if ok for K, as long as you still have positive consumption. 
        so given you COH this period, the minimal K is 0 and the maximal K is spent
        bascially nearly every dollar on K.
        
        then now introduce savings. Savings is easy, if you want to do something
        other than K, you can plow some of your cash into savings as well, easy. 
        
        
        Now borrowing, if you borrow 1 dollar today, that changes the minimal K
        you need to save up, the 
        
            let's say coh: 10
            k min to max were: 0 to 10
            if you borrow $0.5, suppose R=2.0, massive 100 percent interest:
                k min = 1, need to have at least k=1 tomorrow to pay for 50 cents debt?
                    actually that is not even enough, because there is depreciation tomorrow, 
                        hence  0.5(1.0+1.0) = k(1-d), how much k is needed?
                            in other word if B=-1 (principle), how much k is needed
                                -B*(R)=K(1-d) 
                                -B * [(R)/(1-d)]
                what about k max ?
                k max is also now higher, you can have K_max = 10.5
                    would you do this?
                        you would, if capital is highly productive, and you normally invest 10.5
                        but this period you lacked some cash. 
                        
                    the ability to borrow in this world, would likely not impact
                    k 
                    
                    The key thing here, is that there are two different lines
                    one slope is for as borrowing increases, how much min k
                    is needed, this slope increases at a rate of:
                        For each B unit of principle, need to have this much K at least:                    
                            [(R)/(1-d)] > 1
                    the other slope is the slope is the top part of the slope, that
                        is as borrowing, increases, given each level of borrowing, what is:
                            for each B unit of principle acquired, have B unit of additional K' for investment.
                                the slope is 1. 
                                
                                so the question is, what is the peak point a the top left. 
                                
                                we start always at the 0,0 center point, at which point
                                we are consuming all cash on hand today. 
                                
                                ignoring the issues with fixed costs for a second:
                                
                                for borrowing:
                                
                                    the lower right = [0,   0]
                                    the upper right = [0, coh]
                                    
                                suppose there is no bound on how much could be borrowed:
                                    we have two lines, solve for where they intersect:
                                        
                                        top line:
                                            Y = coh - X
                                        bottom line:
                                            Y = 0 - ((R)/(1-d))*X                                            
                                        this is too simple, just says, they intersect if:
                                            coh - X_max = 0 - ((R)/(1-d))*X_max
                                            coh = X_max - ((R)/(1-d))*X_max
                                            coh = X_max * (1-((R)/(1-d)))
                                            
                                            coh*(1/(1-((R)/(1-d)))) = X_max
                                            
                                            this means Y_max = coh - coh*(1/(1-((R)/(1-d))))
                                            Y_max = coh*(1- (1/(1-((R)/(1-d))))) 
                                            
                                        
                                    the upper left = []
                                    the upper left = []
                                
                        Think about how this works, so we have two assets:
                            1. one risky, one risk free, 
                            2. you are reducing the holding of the risk-free asset (when you borrow)
                                increasing the risky asset,
                            3. how much are you willing to do this?
                                especially given the particular constraint structure. 
                                
                                
                        
        
        
        would you be able to borrow? to help smooth consumption?
        is it better to borrow to smooth consumption, or is it better to use up
        your K?
    
    
    """

    """
    The B here includes principle and interest
    
    Several things to consider:
        inside Y_minCst = fixed cost
        Bstart = minimal borrowing/saving
        collateral constraint
            : limiting borrowing to be below Bstart required possibly
    
    Y_minCst = [Y+(1-d)*K+B] - fixed cost
    
    Assume we have enough cash on hand today and k today so that
    we can support Bstar and fixed costs.  
    
    upper_right:
        maximum k' at maximum b'
            - maximum b' is the least amount we have to borrow
                = Bstart
            - max k' at max b' 
                = (Y_minCst - Bstart)
                given coh, take away fixed cost of this activity, and add
                minimal borrowing required for this category, all of these go
                to k'
            
    lower_right:
        minimal k' at maximum b'
            - to borrow this amount b', some k' next period is required for
                guaranteeing repayment
                = Bstart/(1-d)
            - if formal+informal borrow, minimal k' required needs to cover
                both formal as well as informal borrowing
                    - informal borrowing still is Bstart
                    - formal borrowing could either be Full or just to cover
                        minimal formal borrowing. 
            
    upper_left:
        maximum k' at minimal b'
            - minimal b' is the most that can be borrowed
                = find the tip of the triangle. 
                    with associated k' and b' values
            - 
                
    upper_right:
    """
