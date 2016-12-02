import re, shutil

def make_align(dc2file, layers, locations, window_size=40):
    '''
    Sets up alignment marks for NPGS. Give it the DC2 file you'd like to modify,
    specify the layers of alignment marks (in order) and the locations of the
    centers of the alignment marks (in the same order).

    This will convert the dashed lines of the alignment marks to solid and draw
    dashed square windows that are window_size x window_size, centered at the
    alignment mark locations
    '''
    pattern_layer = re.compile("^\s*[0-9]{1,10}\s*[0-9]{1,10}\s*[0-9]{1,10}\s*[0-9]{1,10}\s*[0-9]{1,10}\s*[0-9]{1,10}\s*$") # this is six integers separated by spaces
    pattern_shape = re.compile("^\s*[0-9]{1,10}\s*[0-9]{1,10}\s*[0-9]{1,10}.[0-9]{1,10}\s*[0-9]{1,10}\s*[0-9]{1,10}\s*[0-9]{1,10}\s*[0-9]{1,10}\s*[0-9]{1,10}\s*[0-9]{1,10}\s*[0-9]{1,10}\s*[0-9]{1,10}\s*[0-9]{1,10}\s*[0-9]{1,10}\s*[0-9]{1,10}\s*$")

    ## Backup copy of DC2 file
    shutil.copyfile(dc2file, dc2file.split('.')[0]+'_backup.dc2') # copy in place

    ## Get contents of DC2 file
    with open(dc2file) as f:
        lines = f.readlines()

    if lines[13] != 'SIMPLEX2.VFN\n':
        raise Exception('Need to open in DesignCAD first and save! Then we can edit it!')
     
    ## Find shape headings and change to solid
    for i, line in enumerate(lines):
        for match in re.finditer(pattern_shape, line):
            layer_number = int(lines[i].split()[5]) # 6th number is layer
            if layer_number in layers:
                ## Change alignment marks to solid
                split = lines[i].split()
                split[4] = str(0) #
                lines[i] = ' '.join(split) + '\n'

    ## Find layer headings and insert alignment windows
    for i, line in enumerate(lines):
        for match in re.finditer(pattern_layer, line): # searches for six ints with spaces
            layer_number = int(lines[i].split()[1]) # the layer number is the second number
            if layer_number in layers:
                ## Insert alignment windows
                layer_index = layers.index(layer_number)
                window = make_window(layer_number, locations[layer_index], window_size)
                lines[i+1:i+1] = window # inserts the array of lines

    ## Write changes
    with open(dc2file.split('.')[0]+'_align.dc2', 'w') as f:
        f.write(''.join(lines))

def make_window(layer_number, location, window_size=40):
    '''
    Makes a dashed window in the given layer, at the given location, with the given size.
    This window is the region that will be scanned when searching for alignment marks.
    '''
    w = window_size/2

    s = []
    s.append('1 5 0.2000 0 1 %s 0 1 0 255 255 255 0 1\n' %layer_number) # I don't know what most of these mean. 5 is number of points in the line. %s is the layer number. The 1 directly before the layer number indicates a dashed line. 255 255 255 is RGB (white)
    s.append('%i %i 0\n' %(location[0] - w, location[1] + w)) # These are the four corners of the square
    s.append('%i %i 0\n' %(location[0] + w, location[1] + w))
    s.append('%i %i 0\n' %(location[0] + w, location[1] - w))
    s.append('%i %i 0\n' %(location[0] - w, location[1] - w))
    s.append('%i %i 0\n' %(location[0] - w, location[1] + w)) # line has to reconnect with itself
    return s
