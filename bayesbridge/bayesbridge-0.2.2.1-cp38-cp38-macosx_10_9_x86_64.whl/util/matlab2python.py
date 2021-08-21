import sys

def main():
    filename = sys.argv[1] 
    newfilename = "{:s}_converted.py".format(
        filename[:filename.find('.')]
    )
    with open(filename, 'r') as file, open(newfilename, 'w') as newfile:
        for line in file:
            line = convert_basic_syntax(line)
            line = convert_to_numpy_syntax(line)
            line = convert_to_matplotlib_syntax(line)
            newfile.write(line)

def convert_basic_syntax(str):
    # Remove a line if it is a closing of a control statement. 
    if str.lstrip()[:3] == 'end':
        str = ''
        return str

    str = str.replace('%', '#')
    str = str.replace(';', '')
    str = str.replace('...', '\\')
    str = str.replace('~', '_')
    str = str.replace('length(', 'len(')
    
    # Add a colon at the end of control statements. Algorithmically
    # converting a for-loop syntax seems trickly, so not delt here.
    control = ['for', 'if', 'else', 'while']
    wo_lspace = str.lstrip()
    for word in control:
        if wo_lspace[:len(word)] == word:
            str = str.rstrip('\n') + ':' + '\n'
    
    return str

def convert_to_numpy_syntax(str):
    # For the functions with numpy equivalents, simply append 'np.'.
    # 'zeros' and 'ones' need further processing inside the parentheses.
    # Also watch out for the fact that axis indexing starts with 0 in Python.
    expression_list = [
        'zeros', 'ones', 'exp', 'log', 'sqrt', 'abs', 'sign', 'linspace'
    ]
    for expression in expression_list:
        str = str.replace(expression + '(', 'np.' + expression + '(')
        
    str = str.replace('rng(', 'np.random.seed(')
        
    return str

def convert_to_matplotlib_syntax(str):
    # Remove the lines 'hold on' and 'hold off'
    if str.lstrip()[:5] == 'hold ':
        return ''
    
    expression_list = [
        'plot', 'subplot', 'hist', 'refline'
    ]
    for expression in expression_list:
        wo_lspace = str.lstrip()
        # Avoid matching 'plot' within a string 'subplot'.
        if wo_lspace[:len(expression)] == expression:
            str = str.replace(expression + '(', 'plt.' + expression + '(')

    return str

if __name__ == "__main__":
    main()