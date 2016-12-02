MAG_SCALE = 300000 # = (actual field of view (um)) * (magnification); from Pg.sys

def setup_run_file(runfile, align_layers, expose_layers, mag=900, dose=320, config_param=None, current=None):
    '''
    This function assumes that a runfile has been generated with two entities.
    The first entity must be "alignment" and the second must be "pattern".
    "align_layers" is a list of layer numbers where alignment marks can be found.
    "expose_layers" is a list of layer numbers you want to expose
    "mag" is magnification. Set this somewhat lower than MaxMag (allows for rotation correction) 900 is good for 200x200 um alignment marks
    "dose" is the exposure area dose (µC/cm^2) 320 is default for PMMA bilayer
    "config_param" is the configuration parameter. At CNF, this controls the SEM aperture size (important!). Can be set at the tool
    "current" is the measured beam current (pA) - this can always be set directly at the Nabity and the dwell time will update correctly

    Some customization for CNF's Nabity:
    MAG_SCALE (global variable) defined as 300000
    Square exposure grid
    Line spacing set to minimum recommended by Nabity for the finest features
    '''
    ## Initialize some stuff
    layer_number = None
    alignment_layer = True
    assert type(mag) is int
    assert type(config_param) in (int, type(None))

    ## Get contents of runfile
    with open(runfile) as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        split = line.split()

        if split[0] == 'lev': # indicates a new layer
            layer_number = int(split[1]) # layer number is second thing on the line

            ## Set layer settings
            if alignment_layer:
                if layer_number in align_layers:
                    split[2] = 'w' # window
                else:
                    split[2] = 's' # skip
            else:
                if layer_number in expose_layers:
                    split[2] = 'c' # continuous
                else:
                    split[2] = 's' # skip

            # split[3] # this is the origin; leave at 0,0
            # split[4] # no clue what this is
            split[5] = str(mag) # magnification

            ## Set minimum line spacing (needs to be set in Angstrom)
            line_spacing = MAG_SCALE * 10000 / mag / 2**16 * 4 # 10000 converts um to Angstrom, divide by mag to get field of view, then divide by 16 bits on the DAC, then multiply by 4 based on Nabity's suggestion
            if alignment_layer:
                line_spacing *= 10 # Alignment doesn't need super super fine spacing, and NPGS will complain if there are too many exposure points in the grid. If this is for some reason still too small, can always edit the runfile manually.
            split[6] = str(line_spacing)
            split[7] = split[6] # this is what Nabity calls "line spacing" - make it the same as center-to-center fo square exposure grid

            if config_param is not None:
                split[8] = str(config_param) # configuration parameter
            if current is not None:
                split[9] = str(current)
            else:
                current = float(split[9]) # for doing the dwell time calculation below

        elif split[0] == 'col': # indicates a color
            # split[1] # just the corresponding number
            # split[2], split[3], split[4] # RGB values for the color

            ## Going out of order here because dwell time requires calculation from dose
            if not alignment_layer:
                split[6] = str(dose)
                split[7] = str(0) # 0 denotes area dose, 1 is line dose
            else:
                pass # not sure if this actually matters for an alignment layer; it doesn't show up in the runfile

            if alignment_layer:
                split[5] = str(100) # dwell counts, 100 is typically good for alignment
            else:
                split[5] = str(dose * line_spacing ** 2 / current / 100) # Formula from p 107 of NPGS Manual, 100 is for unit conversion; Since lines are read in order, line_spacing will be correct for the current layer

        elif split[0] == '*':
            alignment_layer = False # We have now reached the pattern layer

        lines[i] = ' '.join(split) + '\n' # recreate the line with spaces

    ## Write changes
    with open(runfile.split('.')[0]+'_edited.RF6', 'w', newline='\r\n') as f:
        f.writelines(lines)
