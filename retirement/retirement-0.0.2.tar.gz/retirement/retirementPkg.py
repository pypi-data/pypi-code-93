# Variable input class
#TODO imports to init.py?

class retirement():
 
    def var_input():
        import pandas as pd
        import numpy as np
        import time
        from time import sleep
        
        variables = []
        variable_names = []
    
        #time to retirement
        years_to_retire = int(input('\nFictitious Steve is planning to retire in how many years? '))
    
        #amount needed at retirement
        how_much_needed_at_retirement = float(input('How much per year does Fictitious Steve need at retirement? [Annually; In thousands of $; After taxes.]'))
    
        #current retirement savings
        starting_principle = float(input('How much did Fictitious Steve have saved for retirement right now? [In thousands of $]'))
        
        #income after retirment
        how_much_ss_at_retirement = float(input('How much Social Security benefits per year will Fictitious Steve receive at retirement? [In thousands/year] '))
        how_much_other_passive_income = float(input('How much will Fictitious Steve have in other income per year in retirement? [e.g. Pension, Rental Income, etc; In thousands of $] '))
    
        #return on retirement savings
        rate_of_return = float(input('What is the annualized percent return (rate of return) on the retirement saving before retiring? '))

        #life expectance after retirement
        yrs_to_death = input('How long does Fictitious Steve need retirement income? [press enter if you want 20 yrs.]')
        if yrs_to_death:
            yrs_to_death = float(yrs_to_death) + float(years_to_retire)
        else:
            yrs_to_death = float(20) + float(years_to_retire)
            print('The time Fictitious Steve needs retirement income is for ', yrs_to_death - float(years_to_retire), 'years.')
    
        #contribution to retirement savings before retiring    
        additional_principle = float(input('How much will Fictitious Steve be adding to the retirement savings per year before retiring? '))

        #inflation rate
        inflation = input('What is the inflation rate per year? [press enter if you want 3%.]')
        if inflation:
            inflation = float(inflation)
        else:
            inflation = float(3)
            print('Based on your input the inflation rate is', inflation, '%.')

        #tax rate
        tax_rate = input('Based on what Fictitious Steve needs, what will be the tax rate? [press enter if you want to assume 25% for both state and federal taxes.]')
        if tax_rate:
            tax_rate = float(tax_rate)
        else:
            tax_rate = float(25)
            print('Based on your input the overall income tax rate is', tax_rate, '%.')
            
        final_principle = float(0)
    
        variables = [years_to_retire, how_much_needed_at_retirement, starting_principle,
                 how_much_ss_at_retirement, how_much_other_passive_income, rate_of_return,
                 yrs_to_death, additional_principle, inflation, tax_rate, final_principle]
    
        variable_names = ['years_to_retire', 'how_much_needed_at_retirement', 'starting_principle',
                 'how_much_ss_at_retirement', 'how_much_other_passive_income', 'rate_of_return',
                 'yrs_to_death', 'additional_principle', 'inflation', 'tax_rate', 
                 'final_principle']
        ''' 
        legend 
        variables[0] = years_to_retire 
        variables[1] = how_much_needed_at_retirement
        variables[2] = starting_principle
        variables[3] = how_much_ss_at_retirement
        variables[4] = how_much_other_passive_income
        variables[5] = rate_of_return 
        variables[6] = yrs_to_death
        variables[7] = additional_principle
        variables[8] = inflation
        variables[9] = tax_rate
        variables[10] = final_principle
        '''
        df = pd.DataFrame(columns= ['years_to_retire', 'how_much_needed_at_retirement', 'starting_principle',
                 'how_much_ss_at_retirement', 'how_much_other_passive_income', 'rate_of_return',
                 'yrs_to_death', 'additional_principle', 'inflation', 'tax_rate', 
                 'final_principle']) #creates the df using variable_names list
    
        return variables, variable_names, df

    #determines the amount of gain over entirement retirement period (retirement to death)
    def impact_years_compounding(variables, df):
        yr = 1
        starting_principle = variables[2]
        while yr <= variables[6]: #calculates compounding across multiple years
            if yr > variables[0] :#ends additional contribution to retirement at the start of retirement    
                additional_principle = 0
            else:
                additional_principle = variables[7]
          
            if yr < variables[0]: #years_to_retire: starts retirement debit at the start of retirement
                #variables[0] = when retirement starts
                debit = 0
                taxes = 0
                inflat = 0
            else:
                debit = (1 + (variables[9]/100) + (variables[8]/100)*((yr + 1) - variables[0])) * (-variables[1]) 
                #how_much_needed_at_retirement
                # variables[9] are taxes; variables[1] is amount needed at retirement; variables[8] is inflation
                taxes = variables[9]
                inflat = variables[8]
            
            years_to_retire = variables[0] - yr
            if years_to_retire < 0:
                years_to_retire = 'Retired'
        
            years_left = variables[6] - yr
        
        
            #defines gain through monthly compounding while taking into account additional principle
                
            if yr > variables[0]:
                soc_security = variables[3]
                passive_retirement_income = variables[4]
            else: 
                soc_security = 0
                passive_retirement_income = 0
            mpr = variables[5]/1200 # APR divided by 12 to get monthly interest rate
            #print('mpr = ', mpr)
            month = 1    
            new_principle = starting_principle
            #print('new_principle = ', new_principle, '\n')
            while month < 13:
                gain_from_interest_on_principle = new_principle * mpr
                #print('gain_from_interest_on_principle =', gain_from_interest_on_principle)
                new_principle = new_principle + gain_from_interest_on_principle + additional_principle/12 + debit/12 + soc_security/12 + passive_retirement_income/12
                month += 1
                new_principle = float(new_principle)
            
            final_principle = new_principle 
            apr = variables[5]
        
            df = df.append({'years_to_retire': years_to_retire, 
                        'how_much_needed_at_retirement' : debit, 
                        'starting_principle': variables[2],
                        'how_much_ss_at_retirement': soc_security, #variables[3] 
                        'how_much_other_passive_income': passive_retirement_income, #variables[4], 
                        'investment_apr': variables[5],
                        'yrs_to_death': years_left, 
                        'additional_principle': additional_principle, 
                        'inflation': inflat, 
                        'tax_rate': taxes, 
                        'final_principle': final_principle}, ignore_index = True)                           
        
            starting_principle = final_principle
        
            yr += 1
        
        return df
    
    
    # summarizes the data
    def summary(df):
        
        import sys
        import time
        from time import sleep
    
        #prints out a typewriter effect
        #https://stackoverflow.com/questions/19911346/create-a-typewriter-effect-animation-for-strings-in-python
        print()
        lines = ['The Big question ... Will the retirement savings last long enough in this game?????']

        for line in lines:          # for each line of text (or each message)
            for c in line:          # for each character in each line
                print(c, end='')    # print a single character, and keep the cursor there.
                sys.stdout.flush()  # flush the buffer
                sleep(0.1)          # wait a little to make the effect look good.
            print('')               # line break (optional, could also be part of the message)
    
        time.sleep(2)
    
        i = 0
        while i < len(df):
            print('year', i+1 , 'Retirement Savings: $', int(df.iloc[i,10] * 1000)) #print out the year ending
        
            time.sleep(1)
        
            if i == df.iloc[0,0] - 1: #defines the point when retirment starts
                #print(i, df.iloc[0,0])
                print('Congratulations, retirement has started! Fictitious Steve will start drawing from his retirement savings!!!')
            
            if df.iloc[i,10] < 0: #defines the point when the retirement savings crosses into the negative
                under_water = i - df.iloc[0,0] 
                print("\nOhhhhh Noooooo .... Fictitious Steve's retirement savings ran out at between the", under_water , 'th and', under_water + 1 , 'th year of retirement!')
                time.sleep(2)
                print('\nBUMMERS ... BUT ... since Fictitous Steve is an easy going guy and ... this is only a game, go back and change some of the conditions to see if you can make his retirement savings make it a bit farther!')
                break    
            #else:
                #i = len(df) - 1
                #print('Looking Good!')
                #print('In the end your retirement accound will be worth', df.iloc[i,10])
            
            i += 1
    
        if i == len(df):
            print('\nYOU WON!!!! Fictitious Steve thanks you! The retirement savings lasted his entire retirement!!!!')

