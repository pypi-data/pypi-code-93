import re
from html.parser import HTMLParser
from html.entities import name2codepoint
# cleans strings 
def string_cleaner(rouge_text):
	try:
		return ("".join(rouge_text.strip()).encode('ascii', 'ignore').decode("utf-8")).replace("\\","").replace('"','')
	except:
		return rouge_text
# cleans strings in an array
def string_cleaner_array(rouge_array):
	clean_array=[] 
	for arr in rouge_array:
		temp = ("".join(arr.strip()).encode('ascii', 'ignore').decode("utf-8"))
		clean_array.append(space_tabs_remover(temp))
	return clean_array
# cleans strings in an array
def string_cleaner_array_wine(rouge_array):
	clean_array=[] 
	for arr in rouge_array:
		temp = ("".join(arr.strip()).encode('ascii', 'ignore').decode("utf-8"))
		# temp = space_tabs_remover(temp)
		# temp = space_tabs_remover(temp.replace(',',''))
		if temp:	
			clean_array.append(temp)
	return clean_array
# Remove special characters
def remove_special_char(text):
	try:
		return re.sub(r'\W+',' ',text)
	except:
		return text

# cleans prices to numbers
def price_cleaner(dirty):
	try:
		val=string_cleaner(dirty).replace(' ', '').replace(',','')
		val_lower=val.lower().replace('ksh','').replace('sh','').replace('kes','').replace('s','')
		clean=int(float(val_lower))
		return clean
	except:
		return dirty

#Remove characters forcefull version of price_cleaner
def remove_char(rouge_text):
	try:
		return ''.join(i for i in rouge_text.replace('.00','') if i.isdigit())
	except:
		return rouge_text

# Renoves special characters with .00
def remove_char_special(rouge_text):
	try:
		rouge_text=rouge_text.replace('.00','')
		return ''.join(i for i in rouge_text if i.isdigit())
	except:
		return rouge_text

# cleans html raw html to string
def cleanhtml(raw_html):
	try:
	  cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
	  cleantext = re.sub(cleanr, '', raw_html)
	  #cleantext = space_tabs_remover(string_cleaner(cleantext))
	  if cleantext:
	  	return cleantext
	  else:
	  	return False
	except:
		return False
# replace &nbsp; with space
def nbsp_replacer(text):
	try:
	 return text.replace('\u00a0',' ')
	except:
		return False

# cleans html raw html to string
def cleanhtml_array(raw_html_arr):
	try:
		html_arr = []
		for raw_html in raw_html_arr:  
		  cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
		  cleantext = re.sub(cleanr, '', raw_html)
		  html_arr.append(string_cleaner(cleantext))
		return html_arr
	except:
		return raw_html_arr
def cleanhtml_array2(raw_html_arr):
	try:
		html_arr = []
		for raw_html in raw_html_arr:  
		  cleantext = cleanhtml(raw_html)
		  html_arr.append(string_cleaner(cleantext))
		return html_arr
	except:
		return False

# get ratings
def ratings_extractor(style):
	try:
		ratings=float(style.replace('width:','').replace('%',''))
		ratings=(ratings/100)*5
		return round(ratings,1)
	except:
		return False

#generate specs for the tables
def specs_table_gen(col1,col2):
	try:
		specs = []
		for index,item in enumerate(col2):
			specs.append(space_tabs_remover(string_cleaner(f'{col1[index]} : {item}'))) 
		return specs
	except:
		return False

#remove \t \n \r
def space_tabs_remover(rouge):
	try:
		# replace is specific for shopit
		return re.sub(r'(\\t)|(\\u)|(\\n)|(\\r)|(\')|(\")',' ',repr(rouge)).replace('\\xa0','')
	except:
		return rouge

# extract lists
def extract_list(html_block):
	try:
		return re.findall(r'<li[^>]*>(.*?)</li>',html_block)
	except:
		return []

#----- Generate link2 ---------------------------------#
#normal link
def gen_link2_id(shop,name,link):
	try:
		prod_id = re.findall(r'product_id=([^&]+)',link)[0]
		prod_name = '-'.join(remove_special_char(name).split(' '))
		return f"/{shop}/{prod_name}_{prod_id}"
	except:
		return False
#recieves id instead of link
def gen_link2_id2(shop,name,id_):
	try:
		prod_name = '-'.join(remove_special_char(name).split(' '))
		return f"/{shop}/{prod_name}_{id_}"
	except:
		return False
def gen_link2_normal(shop,link):
	try:
		regx = re.findall(r'.*/(.*$)',link)[0]
		return f'/{shop}/{regx}'
	except:
		return False
#link with back slash
def gen_link2_backslash(shop,link):
	try:
		regx = re.findall(r'.*/([^/].*)/$',link)[0]
		return f'/{shop}/{regx}'
	except:
		return False
#link with html end
def gen_link2_html(shop,link):
	try:
		regx = re.findall(r'.*/(.*)\.html$',link)[0]
		return f'/{shop}/{regx}'
	except:
		return False
#link with from shopify
def gen_link_shopify(shop,link):
	try:
		regx = re.findall(r'.*\/(.*)?\?.+$',link)[0]
		return f'/{shop}/{regx}'
	except:
		return False
# Combine methods
def gen_link2(shop,link):
    try:
        if re.match(r'^.+\.html$',link):
            return gen_link2_html(shop,link)
        elif re.match(r'^.+\/$',link):
            return gen_link2_backslash(shop,link)
        elif re.match(r'^.+[^\/]+\?.+$',link):
            return gen_link_shopify(shop,link)
        else:
            return gen_link2_normal(shop,link)
    except:
        return False
def gen_link2_split(shop,link):
	link = re.sub(r'https:\/\/[^\/]+/','',link)
	link = re.sub(r'\/$','',link)
	return f"/{shop}/{'_'.join(link.split('/')[::-1])}"

#------------------------------ End -------------------------#
# Generate link from 3 sub caterories
def gen_link_categories3(shop,link):
	try:
		regx = re.findall(r'\/([^\/]+)\/([^\/]+)\/([^\/]+)\/?$',link)[0]
		return f'/{shop}/{regx[2]}_{regx[1]}_{regx[0]}'
	except:
		return False
# Generate link from 2 sub caterories
def gen_link_categories2(shop,link):
	try:
		regx = re.findall(r'\/([^\/]+)\/([^\/]+)\/?$',link)[0]
		return f'/{shop}/{regx[1]}_{regx[0]}'
	except:
		return False
#link with length 2
def gen_link_length2(shop,link):
	try:
		name = re.findall(r'https\:\/\/[^\/]+\/[^\/]+\/([^\/]+)',link)[0]
		prod_id1 = re.findall(r'https\:\/\/[^\/]+\/[^\/]+\/[^\/]+\/([^\/]+)',link)[0]
		prod_id2 = re.findall(r'https\:\/\/[^\/]+\/[^\/]+\/[^\/]+\/[^\/]+\/([^\/]+)',link)[0]
		return f'/{shop}/{name}_{prod_id1}_{prod_id2}'
	except:
		return False		
#generate link format
def link_format(link):
	try:
		return re.sub('(.+)/(.+$)',r'\1_\2',link)
	except:
		return False
#generate specs for wine (not perfect)
def specs_table_gen_wine(col1,col2):
	try:
		specs = []
		for index,item in enumerate(col1):
			try:
				specs.append(space_tabs_remover(string_cleaner(f'{item} : {col2[index]}'))) 
			except:
				specs.append(space_tabs_remover(string_cleaner(f'{item} : None')))
		return specs
	except:
		return False

# General link creator
def create_link2(base,url):
	return f'{base}{url}' if url else False
# --------------------------------------------------------------- #
#Json extractors
def extract_from_ldjson(ldjson,value):
	if ldjson and value:
		return re.findall(rf'"{value}"[ ]?:[ ]?"([^"]+)",?',ldjson)[0] if re.search(rf'"{value}"[ ]?:[ ]?"([^"]+)",?',ldjson) else False
	else:
		return False
def extract_jsonshell_ldjson(ldjson,value):
	if ldjson and value:
		return re.findall(r'"%s"[ ]?:[ ]?(\{[^\}]+)\},?' %value,ldjson)[0] if re.search(r'"%s"[ ]?:[ ]?\{([^\}]+)\},?' %value,ldjson) else False
	else:
		return False
#-----------------------------------------------------------------#
# Extract description
def extract_description(*args):
	if len(args) == 2:
		try:
			return (args[0].replace(args[1],''))
		except:
			return False
	elif len(args) == 3:
		try:
			return (args[0].replace(args[1],'').replace(args[2],''))
		except:
			return False
	else:
	    return False
# ----------------------------------------------------------------#
# CDN replacer
def replace_with_imagekit(imageurl,baseurl):
	try:
		return imageurl.replace(baseurl,'https://ik.imagekit.io/ywt2p2dpl')
	except:
		return False
#----------------------------Specs generator from table -------#
def table_shaker(table_html_block,types):
	try:
		column1 = cleanhtml_array(table_html_block.css(f'tr {types[0]}:nth-child(1)').getall())
		column2 = cleanhtml_array(table_html_block.css(f'tr {types[1]}:nth-child(2)').getall())
		return specs_table_gen(column1,column2)
	except:
		return False
# ----------------------------- Description format --------------#
class _HTMLToText(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._buf = []
        self.hide_output = False

    def handle_starttag(self, tag, attrs):
        if tag in ('br',) and not self.hide_output:
            self._buf.append('<br/>')
        elif tag in ('h1','h2','h3','h4','h5','b','caption') and not self.hide_output:
        	self._buf.append('<strong>')
        elif tag in ('script', 'style'):
            self.hide_output = True

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self._buf.append(' ')

    def handle_endtag(self, tag):
        if tag in ('p','li','tr') and not self.hide_output:
            self._buf.append('<br/>')
        elif tag in ('h1','h2','h3','h4','h5','b','caption') and not self.hide_output:
        	self._buf.append('</strong><br/>')
        elif tag in ('td','th') and not self.hide_output:
        	self._buf.append(' ')
        elif tag in ('script', 'style'):
            self.hide_output = False

    def handle_data(self, text):
        if text and not self.hide_output:
            self._buf.append(re.sub(r'\s+', ' ', text))

    def handle_entityref(self, name):
        if name in name2codepoint and not self.hide_output:
            c = chr(name2codepoint[name])
            self._buf.append(c)

    def handle_charref(self, name):
        if not self.hide_output:
            n = int(name[1:], 16) if name.startswith('x') else int(name)
            self._buf.append(chr(n))

    def get_text(self):
    	description = [] 
    	for line in [item for item in re.sub(r' +', ' ', ''.join(self._buf)).split('<br/>') if item]:
    		if re.match(r'^<strong>.+</strong>$',line):
    			description.append({'title':string_cleaner(re.sub(r'</?strong>','',line))})
    		else:
    			description.append({'text':string_cleaner(re.sub(r'</?strong>','',line))})
    	return description



def get_description(html):
    """
    Given a piece of HTML, return the plain text it contains.
    This handles entities and char refs, but not javascript and stylesheets.
    """
    parser = _HTMLToText()
    try:
        parser.feed(html)
        parser.close()
    except:  #HTMLParseError: No good replacement?
        pass
    return parser.get_text()
# ------------- End of descrition formater -----------#