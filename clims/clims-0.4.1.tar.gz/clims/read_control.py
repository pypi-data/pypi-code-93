def read_control():
    control = {'species':{}}
    output = {}
    bands = []
    with open('control.in','r') as f:
        lines = f.readlines()
    # Just read twice: first keywords, second species
    for line in lines:
        words = line.split()
        if len(words) == 0 or words[0].startswith('#'):
            pass
        elif words[0] == 'output':
            if words[1] == 'band' or words[1] == 'band_mulliken':
                bands += [' '.join(words[2:]).split('#')[0].split()]
                if words[1] == 'band_mulliken':
                    output['is_band_mulliken'] = True
            else: 
                output[words[1]] = ' '.join(words[2:]).split('#')[0].split()
        elif words[0] == 'species':
            break
        else:
            control[words[0]] = ' '.join(words[1:]).split('#')[0]
    if len(bands) > 0:
        output['bands'] = bands
    control['output'] = output

    for line in lines:
        words = line.split()
        current_species = ''
        if len(words) == 0 or words[0].startswith('#'):
            pass
        elif words[0] == 'species':
            control['species'][words[1]] = {}
        elif current_species:
            # Parse species defaults
            pass
            
    return control
