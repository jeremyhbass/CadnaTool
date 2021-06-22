"""
V2 Modifications:
- check vertices for each box/building and ensure no redundancy (i.e. only 4 vertices)
- add additional source 0.5 m away from each wall of box/building
- 

"""
#  Setup import modules
import os
import tkinter as tk               # GUI creation
from tkinter import filedialog     # Windows dialogs
import tkinter.messagebox          # Windows message box

# Input variables
G_DEBUG = True
# G_DEBUG = False

## Define key functions

# Allow user to select file to process
def getFile(userMessage, userDir, userFileType, allowMultiple=False, debug = True):
    root = tk.Tk()      # Set the Tkinter root
    root.withdraw()     # this stops a small window popping up

    # This line opens the file open dialog
    full_path = tk.filedialog.askopenfilename(parent=root, title= userMessage, defaultextension = userFileType,
                                              initialdir = userDir, multiple=allowMultiple,
                                              filetypes=[('DXF files','*.dxf'),('Text files','*.txt'), ('All files','*.*')])
    # If allowMultiple is true response is a tuple, otherwise a string
    
    if full_path: # full-path contains at least one filename
        if allowMultiple:
            totalFiles    = len(full_path)
            pathName      = []
            fileName      = []
            fileExtension = []
            for file in range(totalFiles):
                dummy, dummyX = os.path.split(full_path[file]); pathName.append(dummy)
                dummy, dummyX = os.path.splitext(dummyX);       fileName.append(dummy)
                fileExtension.append(dummyX[1:])
        else:
            totalFiles = 1
            pathName, fileName       = os.path.split(full_path)
            fileName, fileExtension  = os.path.splitext(fileName)
            fileExtension            = fileExtension[1:]
    else:         # full_path doesn't contain any filenames because user pressed cancel
        totalFiles = 0
        pathName      = None
        fileName      = None
        fileExtension = None

    if debug: # Prints out list of selected files, for debugging purposes
        print(totalFiles)
        print(pathName)
        print(fileName)
        print(fileExtension)
        if totalFiles > 1:
            for fItem in range(totalFiles):
                print('File: %d' % fItem, end = '')
                print('%s' %      pathName[fItem], end = '')
                print('/%s' %      fileName[fItem], end = '')
                print('.%s' % fileExtension[fItem])
    
    # Return key information to main programme
    return totalFiles, pathName, fileName, fileExtension

def messageBox(boxType, title, message):
    top = tk.Tk()
    top.withdraw()
    if boxType.lower() == 'error':
        tkinter.messagebox.showerror(title, message)
    elif boxType.lower() == 'warning':
        tkinter.messagebox.showwarning(title, message)
    elif boxType.lower() == 'information':
        tkinter.messagebox.showinfo(title, message)
    else:                                  # Now hide it
        print('Message box type unknown')
    top.destroy()
    return

## Begin main programme
# Get name and folder of input text file
NO_OF_FILES, DIRECTORY_NAME, FILE_NAME, FILE_EXTN = getFile('Select data file...', r'C:/Users/', 'dxf', False, G_DEBUG)

# If a file was slected, then process it
if NO_OF_FILES == 1:
    fileName = FILE_NAME + '.' + FILE_EXTN
    if G_DEBUG:
        print('Input filename: {}'.format(fileName))
    
    # Open text file (100ms LAeq data)
    print("Scanning DXF data for objects...")

    # Read input DXF file into list
    with open(file=os.path.join(DIRECTORY_NAME, fileName), mode='rt', newline = None) as f:
        dxf_data = f.readlines()
    f.close()

    # Determine number of items of data in file (2 lines per items)
    items = int(len(dxf_data)/2)

    # Covert into a sequence of tuples containing key value and key name
    dxf_lines = []
    for item in range(items):
        value = dxf_data[2 * item][0:-1]
        key   = dxf_data[(2 * item) + 1][0:-1]
        dxf_line = (key, value)
        dxf_lines.append(dxf_line)
        if G_DEBUG:
            print(item, dxf_line[0], dxf_line[1])

    # Identify number of objects within file
    total_objects = 0
    object_location = []
    for item in range(items):
        if dxf_lines[item][0] == 'POLYLINE':
            object_location.append(item)
            total_objects += 1

    # identify total number of vertices within file
    total_vertices = 0
    for item in range(items):
        if dxf_lines[item][0] == 'VERTEX':
            total_vertices += 1

    # Output key information
    print('Input lines:   {:8d}\tInput Items:   {:8d}'.format(len(dxf_data), items))
    print('No of objects: {:8d}\tNo of vertices:{:8d}'.format(total_objects, total_vertices))
    for i in range(total_objects):
        print('Object {:d} starts at item {:d}'.format(i,object_location[i]))

    # Cycle through object blocks (POLYLINE) and identify all vertices
    x_source = []
    y_source = []
    for i in range(total_objects):
        vertex_count = 0
        vertex_x_sum = 0
        vertex_y_sum = 0
        if i + 1 == total_objects:
            last_item = items
        else:
            last_item = object_location[i + 1]
        if G_DEBUG:
            print(i,object_location[i], last_item)
        for item in range(object_location[i], last_item):
    
            # identify total number of vertices within file
            if dxf_lines[item][0] == 'VERTEX':
                vertex_count += 1
                vertex_x_sum += float(dxf_lines[item+2][0])
                vertex_y_sum += float(dxf_lines[item+3][0])
                if G_DEBUG:
                    print(i, item, vertex_count, vertex_x_sum, vertex_y_sum)

        if vertex_count > 0:
            if vertex_count > 4:
                # Do something to ensure that there are no redundant points, i.e. only 4 points
                pass
            # Add central point
            x_source.append(vertex_x_sum/vertex_count)
            y_source.append(vertex_y_sum/vertex_count)
            # Add points for each pair of vertices
            for side in range(vertex_count):
                x_source.append(vertex_x_sum/vertex_count)
                y_source.append(vertex_y_sum/vertex_count)

#         # else:
#         #     x_source.append(0)
#         #     y_source.append(0)
        # if G_DEBUG:
        #     print(i, vertex_count, x_source[i], y_source[i])

    for i in range(len(x_source)):
        print(i, x_source[i], y_source[i])

#     # Create output source file suitabe for import to Cadna/A
#     fileItems = fileName.rsplit('.')
#     fileName = fileItems[0] + '_source.' + fileItems[1]
#     with open(os.path.join(DIRECTORY_NAME,fileName), 'w') as f:
#         # Write DXF header
#         f.write('{:3d}\n'.format(0))
#         f.write('SECTION\n')
#         f.write('{:3d}\n'.format(2))
#         f.write('ENTITIES\n')

#         # Write individual source locations
#         for i in range(total_objects):
#             f.write('{:3d}\n'.format(0))
#             f.write('POINT\n')
#             f.write('{:3d}\n'.format(8))
#             f.write('QU_{:d}\n'.format(i))
#             f.write('{:3d}\n'.format(10))
#             f.write('{:.2f}\n'.format(x_source[i]))
#             f.write('{:3d}\n'.format(20))
#             f.write('{:.2f}\n'.format(y_source[i]))
#             f.write('{:3d}\n'.format(30))
#             f.write('1.60\n')

#         # Write DXF footer
#         f.write('{:3d}\n'.format(0))
#         f.write('ENDSEC\n')
#         f.write('{:3d}\n'.format(0))
#         f.write('EOF\n')

#     f.close()
#     print('DXF Source data: {}'.format(os.path.join(DIRECTORY_NAME,fileName)))
#     messageBox("Information","Information","DXF processing complete!")
# else:
#     messageBox("Information","Warning!","No DXF selected!")