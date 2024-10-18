"""
Let's see what type of functionality a *line* has in x-suite
We will see the different ways of defining a line, how to inspect it, save/load it
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

"""
A Line can be defined in different ways:    
    -   It is possible to provide beam line element objects and the corresponding names

    -   It can be imported from an existing MAD-X model, via 'xtract.Line.from_madx_sequence()'

    -   A line can also be defined through a “sequence”, providing the element s positions 
"""
#? We build a simple ring
# Here we opted to define 'by hand' and not with a MAD-X file
pi = np.pi
lbend = 3
lquad = 0.3
elements = {
    'mqf.1': xt.Quadrupole(length=lquad, k1=0.1),
    'd1.1':  xt.Drift(length=1),
    'mb1.1': xt.Bend(length=lbend, k0=pi / 2 / lbend, h=pi / 2 / lbend),
    'd2.1':  xt.Drift(length=1),

    'mqd.1': xt.Quadrupole(length=lquad, k1=-0.7),
    'd3.1':  xt.Drift(length=1),
    'mb2.1': xt.Bend(length=lbend, k0=pi / 2 / lbend, h=pi / 2 / lbend),
    'd4.1':  xt.Drift(length=1),

    'mqf.2': xt.Quadrupole(length=lquad, k1=0.1),
    'd1.2':  xt.Drift(length=1),
    'mb1.2': xt.Bend(length=lbend, k0=pi / 2 / lbend, h=pi / 2 / lbend),
    'd2.2':  xt.Drift(length=1),

    'mqd.2': xt.Quadrupole(length=lquad, k1=-0.7),
    'd3.2':  xt.Drift(length=1),
    'mb2.2': xt.Bend(length=lbend, k0=pi / 2 / lbend, h=pi / 2 / lbend),
    'd4.2':  xt.Drift(length=1),
}
line = xt.Line(elements=elements, element_names=list(elements.keys()))
line.particle_ref = xt.Particles(p0c=1.2e9, mass0=xt.PROTON_MASS_EV)
line.build_tracker()

# Use the function to plot the line
plot_beamline(line)

"""
Whatever way it was defined, we can inspect the the properties of a line and its elements:
    -   elements names                  line.element_names
    -   all objects                     line.elements
    -   by a specific 'attribute' with  line.attr[...]
        list of all attributes          line.attr.keys()  
    -   an exaustive table              line.get_table()
    -   So much more ... see https://github.com/xsuite/xtrack/blob/main/examples/toy_ring/004_inspect.py
"""
#? Let's inspect the line we created
# Tuple with all element names
line.element_names # is ('mqf.1', 'd1.1', 'mb1.1', 'd2.1', 'mqd.1', ...

# Tuple with all element objects
line.elements # is (Quadrupole(length=0.3, k1=0.1, ...), Drift(length=1), ...

# `line.attr[...]` can be used for efficient extraction of a given attribute for all elements
line.attr['length'] # is (0.3, 1, 3, 1, 0.3, 1, 3, 1, 0.3, 1, 3, 1, 0.3, 1, 3, 1)
line.attr['k1l'] # is ('0.03, 0.0, 0.0, 0.0, -0.21, 0.0, 0.0, 0.0, 0.03, ... )

# The list of all attributes can be found in
line.attr.keys() # is ('length', 'k1', 'k1l', 'k2', 'k2l', 'k3', 'k3l', 'k4', ...

# `line.get_table()` can be used to get a table with information about the line elements
tab = line.get_table()
tab.show()

"""
An Xtrack Line object can be transformed into a dictionary or saved to a json file

The simpler version is the following:
    # Save to json
    line.to_json('line.json')

    # Load from json
    line_2 = xt.Line.from_json('line.json')

But using the dictionary we can save additional information 
See https://github.com/xsuite/xtrack/blob/main/examples/to_json/000_lattice_to_json.py
"""
#? Save
dct = line.to_dict()
dct['my_additional_info'] = 'Some important information about this line I created'
with open('line.json', 'w') as fid:
    json.dump(dct, fid, cls=xo.JEncoder)

#? Load
with open('line.json', 'r') as fid:
    loaded_dct = json.load(fid)
line_2 = xt.Line.from_dict(loaded_dct)
print("\nLet's see if there is any info in the dictionary:")
print(loaded_dct['my_additional_info'])

line_2.get_table().show()

# Define a sextupole
my_sext = xt.Sextupole(length=0.1, k2=0.1)
# Insert copies of the defined sextupole downstream of the quadrupoles
line.discard_tracker() # needed to modify the line structure
line.insert_element('msf.1', my_sext.copy(), at_s=tab['s', 'mqf.1'] + 0.4)
line.insert_element('msd.1', my_sext.copy(), at_s=tab['s', 'mqd.1'] + 0.4)
line.insert_element('msf.2', my_sext.copy(), at_s=tab['s', 'mqf.2'] + 0.4)
line.insert_element('msd.2', my_sext.copy(), at_s=tab['s', 'mqd.2'] + 0.4)

# Define a rectangular aperture
my_aper = xt.LimitRect(min_x=-0.02, max_x=0.02, min_y=-0.01, max_y=0.01)
# Insert the aperture upstream of the first bending magnet
line.insert_element('aper', my_aper, index='mb1.1')

line.get_table().show()

# Use the function to plot the line
plot_beamline(line)


# Slice different elements with different strategies (in case multiple strategies
# apply to the same element, the last one takes precedence)
line.slice_thick_elements(
    slicing_strategies=[
        # Slicing with thin elements
        xt.Strategy(slicing=xt.Teapot(1)),                              # Default applied to all elements
        xt.Strategy(slicing=xt.Uniform(2), element_type=xt.Bend),       # Selection by element type
        xt.Strategy(slicing=xt.Teapot(3), element_type=xt.Quadrupole),  # Selection by element type
        xt.Strategy(slicing=xt.Teapot(4), name='mb1.*'),                # Selection by name pattern
        # Slicing with thick elements
        xt.Strategy(slicing=xt.Uniform(2, mode='thick'), name='mqf.*'), # Selection by name pattern
        # Do not slice (leave untouched)
        xt.Strategy(slicing=None, name='mqd.1') # (7) Selection by name
    ])
line.build_tracker()

plot_beamline(line)
