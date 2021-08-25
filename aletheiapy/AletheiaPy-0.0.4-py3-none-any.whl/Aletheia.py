import requests
import json

class Client:
    def __init__(self, key):
        self.key = key
        self.base = "https://api.aletheiaapi.com/"
        
    def StockData(self, symbol, summary = False, statistics = False):
        url = self.base + f"StockData?key={self.key}&symbol={symbol}"
        if summary: url = url + "&summary=true"
        if statistics: url = url + "&statistics=true"
    
        return json.loads(requests.get(url).text)
    
    def Crypto(self, symbol):
        url = self.base + f"Crypto?key={self.key}&symbol={symbol}"
        
        return json.loads(requests.get(url).text)
    
    def SearchEntities(self, term, top = 0):
        url = self.base + f"SearchEntities?key={self.key}&term={term}"
        if top > 0: url = url + f"&top={top}"
        
        return json.loads(requests.get(url).text)
    
    def GetEntity(self, id):
        url = self.base + f"GetEntity?key={self.key}&id={id}"
        
        return json.loads(requests.get(url).text)
    
    def GetFiling(self, id = "", url = ""):
        call = self.base + f"GetFiling?key={self.key}" # Here we use "call" since "url" is already a parameter.
        if len(id) == 0 and len(url) == 0:
            print("Please specify either the id or url of the filing.")
        elif len(id) > 0: call = call + f"&id={id}"
        else: call = call + f"&url={url}"
        
        return json.loads(requests.get(call).text)
    
    def LatestTransactions(self, issuer = "", owner = "", top = 20, before = None, securitytype = -1, transactiontype = -1, cascade = False):
        url = self.base + f"LatestTransactions?key={self.key}&top={top}"
        if len(issuer) > 0: url = url + f"&issuer={issuer}"
        if len(owner) > 0: url = url + f"&owner={owner}"
        if before != None: url = url + f"&before={before}"
        if securitytype >= 0: url = url + f"&securitytype={securitytype}"
        if transactiontype >= 0: url = url + f"&transactiontype={transactiontype}"
        if cascade: url = url + "&cascade"
    
        return json.loads(requests.get(url).text)
    
    def AffiliatedOwners(self, id):
        url = self.base + f"AffiliatedOwners?key={self.key}&id={id}"
    
        return json.loads(requests.get(url).text)
    
    def CommonFinancials(self, id, period = None, before = None):
        url = self.base + f"CommonFinancials?key={self.key}&id={id}"
        if period != None: url = url + f"&period={period}"
        if before != None: url = url + f"&before={before}"
    
        return json.loads(requests.get(url).text)
    
    def FinancialFactTrend(self, id, label, period = None, after = None, before = None):
        url = self.base + f"FinancialFactTrend?key={self.key}&id={id}&label={label}"
        if period != None: url = url + f"&period={period}"
        if after != None: url = url + f"&after={after}"
        if before != None: url = url + f"&before={before}"
            
        return json.loads(requests.get(url).text)
    
    def SearchEarningsCalls(self, company = None, year = 0, quarter = None, top = 15):
        url = self.base + f"SearchEarningsCalls?key={self.key}&top={top}"
        if company != None: url = url + f"&company={company}"
        if year > 0: url = url + f"&year={year}"
        if quarter != None: url = url + f"&quarter={quarter}"
            
        return json.loads(requests.get(url).text)
    
    def EarningsCall(self, company, year, quarter, begin = None, end = None):
        url = self.base + f"EarningsCall?key={self.key}&company={company}&year={year}&quarter={quarter}"
        if begin != None: url = url + f"&begin={begin}"
        if end != None: url = url + f"&end={end}"
            
        return json.loads(requests.get(url).text)
    
    def EarningsCallHighlights(self, company, year, quarter, category = None):
        url = self.base + f"EarningsCallHighlights?key={self.key}&company={company}&year={year}&quarter={quarter}"
        if category != None: url = url + f"&category={category}"
        
        return json.loads(requests.get(url).text)
    
    def EntityFilings(self, id, filing = None, before = None):
        url = self.base + f"EntityFilings?key={self.key}&id:={id}"
        if filing != None: url = url + f"&filing={filing}"
        if before != None: url = url + f"&before={before}"
        
        return json.loads(requests.get(url).text)
    
    def OpenForm4(self, filingurl):
        url = self.base + f"OpenForm4?key={self.key}&filingurl={filingurl}"
        
        return json.loads(requests.get(url).text)
    
    def OpenCommonFinancials(self, filingurl):
        url = self.base + f"OpenCommonFinancials?key={self.key}&filingurl={filingurl}"
        
        return json.loads(requests.get(url).text) 

    def consumption(self, begin = None, end = None, year = None, month = None): # Doesn't work yet
        url = self.base + f"consumption?key={self.key}"
        if begin != None: url = url + f"begin={begin}"
        if end != None: url = url + f"end={end}"
        if year != None: url = url + f"year={year}"
        if month != None: url = url + f"month={month}"
        
        return requests.get(url).text
    
    def mycalls(self, last = None): # Doesn't work yet
        url = self.base + f"mycalls?key={self.key}"
        if last != None: url = url + f"&last={last}"

        return json.loads(requests.get(url).text)

    def version(self):
        
        return requests.get(self.base + "version").text

    def CountSecEntities(self, onlyco = False):
        url = self.base + "CountSecEntities"
        if onlyco: url = url + "?onlyco=true"
            
        return json.loads(requests.get(url).text)
        
    def CountSecFilings(self):
        
        return requests.get(self.base + "CountSecFilings").text
        
    def CountTransactions(self):
        
        return requests.get(self.base + "CountTransactions").text
    
    def CountFactContexts(self):
        
        return requests.get(self.base + "CountFactContexts").text
    
    def CountFinancialFacts(self, id = ""):
        url = self.base + "CountFinancialFacts"
        if len(id) > 0: url = url + f"?id={id}"
        
        return requests.get(url).text