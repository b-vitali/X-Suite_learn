"""
Accelerators and beam lines have complex control paterns.
We can include these dependencies in the simulation model so that changes in the high-level
parameters are automatically propagated down to the line elements properties.
To see more go to https://github.com/xsuite/xtrack/blob/main/examples/toy_ring/002_expressions.py

NB: When importing a MAD-X model...
the dependency relations from MAD-X deferred expressions are automatically imported!
"""
#? Import the usual stuff
import numpy as np
import matplotlib.pyplot as plt

#? Import the usual x-suite things
import xtrack as xt
import xobjects as xo

#? Import the library to save and load *lines*
import json

#? Auxiliary function just to see the beamline
def plot_beamline(line):
    # Create a new figure and axis
    fig, ax = plt.subplots(figsize=(12, 4))
    
    # Get the table data
    tab = line.get_table()
    positions = tab['s']  # Array of positions
    names = tab['name']   # Array of element names

    # Define a vertical offset for elements
    y_offset = 0.5

    # Loop through the positions and names
    for i in range(len(positions)):
        current_position = positions[i]

        # Determine the length of the element
        if i < len(positions) - 1:
            length = positions[i + 1] - current_position
        else:
            length = 0  # The last element does not have a length

        # Determine the color based on the name
        if 'mqf' in names[i]:
            color = 'green'  # Focusing Quadrupole
        elif 'mqd' in names[i]:
            color = 'red'  # Defocusing Quadrupole
        elif 'mb' in names[i]:
            color = 'orange'  # Bending Magnet
        elif 'ms' in names[i]:
            color = 'magenta'  # Bending Magnet
        elif 'd' in names[i]:
            color = 'blue'  # Drift
        else:
            color = 'black'  # Default color for unknown elements
        
        # Plot the element as a rectangle
        ax.add_patch(plt.Rectangle((current_position, y_offset), length, 0.3, facecolor=color,  edgecolor='black', linewidth=1))

        # Label the element
        ax.text(current_position + length / 2, y_offset + 0.35, names[i], ha='center', va='bottom', fontsize=8, rotation=90)

    # Set plot limits and labels
    if len(positions) > 0:  # Check if positions array is not empty
        ax.set_xlim(0, positions[-1])
    else:
        ax.set_xlim(0, 1)  # Default limit if no positions

    ax.set_ylim(0, 2)
    ax.set_xlabel("Position along the beamline (m)")
    ax.set_yticks([])
    ax.set_title("Beamline Layout")

    # Create a legend
    legend_elements = [
        plt.Line2D([0], [0], color='blue', lw=4, label='Drift'),
        plt.Line2D([0], [0], color='orange', lw=4, label='Bending Magnet'),
        plt.Line2D([0], [0], color='green', lw=4, label='Focusing Quadrupole'),
        plt.Line2D([0], [0], color='red', lw=4, label='Defocusing Quadrupole'),
        plt.Line2D([0], [0], color='magenta', lw=4, label='Sextupole')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    plt.show()

#? Load
with open('line.json', 'r') as fid:
    loaded_dct = json.load(fid)
line = xt.Line.from_dict(loaded_dct)
print("\nLet's see if there is any info in the dictionary:")
print(loaded_dct['my_additional_info'])
line.get_table().show()

lquad = line['mqf.1'].length
print("\nmqf.1 lenght = ", lquad)

# Use the function to plot the line
plot_beamline(line)
plt.show()


#? Let's use some variable to control the beamline
print("===================")
print("==== variables ====")
print("===================")
# For each quadrupole we create a variable controlling its integrated strength.
# Expressions can be associated to any beam element property, using the `element_refs`:
line.vars['k1l.qf.1'] = 0
line.element_refs['mqf.1'].k1 = line.vars['k1l.qf.1'] / lquad
line.vars['k1l.qd.1'] = 0
line.element_refs['mqd.1'].k1 = line.vars['k1l.qd.1'] / lquad
line.vars['k1l.qf.2'] = 0
line.element_refs['mqf.2'].k1 = line.vars['k1l.qf.2'] / lquad
line.vars['k1l.qd.2'] = 0
line.element_refs['mqd.2'].k1 = line.vars['k1l.qd.2'] / lquad

# When a variable is changed, the corresponding element property is automatically updated:
line.vars['k1l.qf.1'] = 0.1
# is 0.333, i.e. 0.1 / lquad
print("\nChanging line.vars['k1l.qf.1'] = 0.1, mqf.1 is updated: ", line['mqf.1'].k1) 

# We can create a variable controlling the integrated strength of the two focusing quadrupoles
line.vars['k1lf'] = 0.1
line.vars['k1l.qf.1'] = line.vars['k1lf']
line.vars['k1l.qf.2'] = line.vars['k1lf']

# and a variable controlling the integrated strength of the two defocusing quadrupoles
line.vars['k1ld'] = -0.7
line.vars['k1l.qd.1'] = line.vars['k1ld']
line.vars['k1l.qd.2'] = line.vars['k1ld']

# Changes on the controlling variable are propagated to the controlled ones 
# and also to the corresponding element properties
line.vars['k1lf'] = 0.2
line.vars['k1l.qf.1']._get_value() # is 0.2
line.vars['k1l.qf.2']._get_value() # is 0.2
# is 0.666, i.e. 0.2 / lquad
print("\n'line.vars['k1lf'] -> k1l.qf.1 -> line['mqf.1'].k1 :", line['mqf.1'].k1) 

# The `_info()` method of a variable provides information on the existing relations
# between the variables. For example:
print("\nline.vars['k1l.qf.1']._info() gives all the relations")
line.vars['k1l.qf.1']._info()
# prints:
##  vars['k1l.qf.1']._get_value()
#   vars['k1l.qf.1'] = 0.2
#
##  vars['k1l.qf.1']._expr
#   vars['k1l.qf.1'] = vars['k1lf']
#
##  vars['k1l.qf.1']._expr._get_dependencies()
#   vars['k1lf'] = 0.2
#
##  vars['k1l.qf.1']._find_dependant_targets()
#   element_refs['mqf.1'].k1


#? Let's use some variable to control the beamline
print("===================")
print("=== expressions ===")
print("===================")
# Expressions can include multiple variables and mathematical operations. 
# For example line.vars['a'] = 3 * line.functions.sqrt(line.vars['k1lf']) + 2 * line.vars['k1ld']

# As seen above, line.vars['varname'] returns a reference object that
# can be used to build further references, or to inspect its properties.
# To get the current value of the variable, one needs to use `._get_value()`
# For quick access to the current value of a variable, one can use the `line.varval` (or `line.vv`)
print("line.varval['k1lf'] = ", line.varval['k1lf'])    # is 0.2
print("line.vv['k1lf'] = ", line.vv['k1lf'])            # is 0.2

# Note an important difference when using `line.vars` or `line.varval` in building
# expressions. For example:
line.vars['a'] = 3.
line.vars['b'] = 2 * line.vars['a']
print("\nline.vars['a'] = 3 and line.vars['b'] = 2 * line.vars['a']")

# In this case the reference to the quantity `line.vars['a']` is stored in the expression, 
# and the value of `line.vars['b']` is updated when `line.vars['a']` changes:
line.vars['a'] = 4.
print("if line.vars['a'] = 4 => line.vars['b'] = ", line.vv['b']) # is 8

print("\nNB: using line.vv['b'] = 2 * line.vv['a'], the changes are not propagated")
# On the contrary, when using `line.varval` or `line.vv` in building expressions,
# the current value of the variable is stored in the expression:
line.vv['a'] = 3.
line.vv['b'] = 2 * line.vv['a']
line.vv['b'] # is 6.
line.vv['a'] = 4.
line.vv['b'] # is still 6.

# The `line.vars.get_table()` returns a table with the value of all the existing variables:
print("\nline.vars.get_table().show() gives all the existing variables")
line.vars.get_table().show()