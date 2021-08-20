import os,sys
import ctypes

import py3toolbox.text_tools as text_tools

if os.name=='nt' and sys.getwindowsversion().major == 10:
  kernel32 = ctypes.windll.kernel32
  kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

PATTERN = {
  "BRIGHT"      : "1",
  "UNDERLINE"   : "4",
  "DIM"         : "2",

  "WHITE"       : "97",  
  "BLACK"       : "30",
  "RED"         : "31",
  "GREEN"       : "32",
  "BLUE"        : "34",
  "YELLOW"      : "33",
  "MAGENTA"     : "35",
  "CYAN"        : "36",
  
  "LGRAY"       : "37",
  "DGRAY"       : "90",
  "LRED"        : "91",
  "LGREEN"      : "92",
  "LYELLOW"     : "93",
  "LBLUE"       : "94",
  "LMAGENTA"    : "95",
  "LCYAN"       : "96",

  "WHITE_BG"    : "107",  
  "BLACK_BG"    : "40",
  "RED_BG"      : "41",
  "GREEN_BG"    : "42",
  "YELLOW_BG"   : "43",
  "BLUE_BG"     : "44",
  "MAGENTA_BG"  : "45",
  "CYAN_BG"     : "46",

  "LGRAY_BG"    : "47",
  "DGRAY_BG"    : "100",
  "LRED_BG"     : "101",
  "LGREEN_BG"   : "102",
  "LYELLOW_BG"  : "103",
  "LBLUE_BG"    : "104",
  "LMAGENTA_BG" : "105",
  "LCYAN_BG"    : "106",
  
  "DEFAULT"     : 0

}



def cls():
  os.system('cls' if os.name=='nt' else 'clear')


def render256(text, align=None, width=None):
  # regexp : (\[\%(\w+)\|FG(\d+)\|BG(\d+)\|(L|R|\<|\>)\|(\d+)\:(.*?)\%\])
  # sample : [%B|FG233|BG123|L|22:test_color%] and dfgdfg [%B|FG233|BG123|L|22:another test_color%] dfgdfg
  
  render_text = ""
  
  start_flag = '\033['
  end_flag = '\033[0m'
  
  
  ATTR  = ''
  FG    = start_flag + '<ATTR>38;5;<FG>m'
  BG    = start_flag + '48;5;<BG>m'
  
  render_groups = text_tools.re_findall(r'(\[\%(\w+)\|FG(\d+)\|BG(\d+)\|(L|R|M|C|\<|\>)\|(\d+)\:(.*?)\%\])', text)
  
  for render_section in render_groups:
    src_text, attr,  fg_color, bg_color, align, width, raw_text = (render_section[0],render_section[1],render_section[2],render_section[3],render_section[4],render_section[5],render_section[6])
    width = int(width)
    
    
    ATTR  = ''
    if 'B' in attr : ATTR += PATTERN['BRIGHT'] + ';' 
    if 'U' in attr : attr += PATTERN['UNDERLINE'] + ';' 
    if 'D' in attr : attr += PATTERN['DIM'] + ';' 
    
    if align == 'L' : align = '<'
    if align == 'R' : align = '>'
    if align == 'C' or align == 'M' : 
      raw_text = ' ' * ((width - len(raw_text)) // 2) + raw_text + ' ' * (width -  ((width - len(raw_text)) // 2) - len(raw_text) )
    else:
      format_str = '{0:' + align + str(width) + '}'
      raw_text = format_str.format(raw_text)
      
    render_text = FG.replace('<ATTR>',ATTR).replace('<FG>',str(fg_color)) + BG.replace('<BG>',str(bg_color)) + raw_text + end_flag
    
    
    # if not windows 10
    if os.name=='nt' and sys.getwindowsversion().major != 10 :
      render_text = raw_text
      

    text = text.replace(src_text, render_text)

    
  
  return (text)

def render256_demo():
  start_flag = '\033['
  end_flag = '\033[0m '
  FG = start_flag + '38;5;<FG>m'
  BG = start_flag + '48;5;<BG>m'
  count = 0
  render_text = ''
  for bg in range (0,256):
    for fg in range (0,256) :
      count +=1
      text =  BG.replace('<BG>',str(bg)) +  FG.replace('<FG>',str(fg)) + 'bg' + str(bg).rjust(3, '0') + 'fg' + str(fg).rjust(3, '0') + end_flag
      render_text += text 
      if count % 16 == 0:
        print (render_text)
        render_text = ''
    print ('')

  return ""

  
def render(text, align=None, width=None):
  render_groups = text_tools.re_findall(r'(\[\%([\w+\|?]+)\:([^\:\|\%]+)\%\]?)', text)
  render_text   = text
  for render_section in render_groups:
    src_text, render_patterns,raw_text = (render_section[0],text_tools.re_findall(r'(\w+)',render_section[1]),render_section[2])
    term_pattern = '\033['
    for p in render_patterns:
      if p not in PATTERN.keys() : raise ValueError( 'Pattern: [' + p + '] not defined!')
      term_pattern += PATTERN[p] + ';'

    
    # if not windows 10
    if os.name=='nt' and sys.getwindowsversion().major != 10 :
      term_pattern = raw_text
    
    # if windows 10 or *nix
    else:
      term_pattern = term_pattern[:-1] + 'm' + raw_text + '\033[0m'
    
    if (align is not None) and (width is not None):
      if align == '>' or align == 'R' :
        term_pattern = ' ' * (width - len(raw_text)) + term_pattern
      if align == '<' or align == 'L' :
        term_pattern = term_pattern + ' ' * (width - len(raw_text)) 
        
    render_text = render_text.replace(src_text,term_pattern)
  return (render_text)
  

  
  
def pause(txt=None) :
  press_keys_info = "Confirm and press [%LGREEN_BG|BLACK:[Enter]%] to continue ... or [%LRED_BG|BLACK:[Ctrl-C]%] to exit ...\n\n"
  if txt is None : txt = "\n\n---> " 
  pause_txt = txt + press_keys_info
  input(render(pause_txt))


def keep_print(text):
  print (text, sep=' ', end='', flush=True)    
  
def get_progress_bar(current, total, scale=50):
  percent = int(current/total*100+0.5)
  if percent <0   : percent = 0
  if percent >100 : percent = 100
  arrow_pos =  int(percent * scale /100 ) 
  if arrow_pos <=1 : 
    progress_bar = '[%LYELLOW:>%]' * arrow_pos + '[%LRED:.%]' * (scale - arrow_pos)
  else:
    if percent < 100 :
      progress_bar = '[%LGREEN:=%]' * (arrow_pos -1) + '[%LYELLOW:>%]' + '[%LRED:.%]' * (scale - arrow_pos)
    else:
      progress_bar = '[%LGREEN:=%]' * scale
  progress_bar = '    [{0}] {1:<5} {2:<12} \r'.format(progress_bar, str(percent) + '%', str(current) + '/' + str(total))
  return render(progress_bar)

def format_str(fmt, *args) :
  return (fmt.format(*args))   

if __name__ == "__main__":
  #'{1} {0}'.format('one', 'two')  
  print(format_str('{1} {0}', 'One', 'Tow'))
  keep_print (get_progress_bar(10,23))
  exit(1)
  _step   =  render('[%LGREEN|DGRAY_BG:12345%] and another [%LGREEN|GREEN_BG:   abcdefgh    %] -',align='<'  ,width=20)
  print (_step)
  _step   =  render('and another [%LGREEN|GREEN_BG:   abcdefgh    %] =',align='<'  ,width=20)
  print (_step)
  
  for i in range (16,21) :
    m = "\033[38;5;" + str(i) + "m#\033[0m"
    print (m)
  #print (render256('[%B|FG184~189|BG46~51|L|22:test_color%] and dfgdfg [%B|FG233|BG123|L|22:another test_color%] dfgdfg'))
  print (render256('[%B|FG014|BG246|L|22:test_color%] and dfgdfg [%U|FG233|BG123|L|22:another test_color%] dfgdfg'))
  print(render256('[%B|FG087|BG235|L|' + str(12) + ':1222222%]'))
  print (render256('[%B|FG087|BG235|C|20:Workers%]'))
  print (render256_demo())
  pass  