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
    current_position = 0
    y_offset = 0.5  # Vertical offset for elements

    for name, element in zip(line.element_names, line.elements):
        length = element.length if hasattr(element, 'length') else 0
        
        # Set color based on element type
        if isinstance(element, xt.Drift):
            color = 'blue'
        elif isinstance(element, xt.Quadrupole):
            color = 'green' if element.k1 > 0 else 'red'  # Green for focusing, red for defocusing
        elif isinstance(element, xt.Bend):
            color = 'orange'
        else:
            color = 'black'  # Default color for unknown elements
        
        # Plot the element as a rectangle
        ax.add_patch(plt.Rectangle((current_position, y_offset), length, 0.3, color=color))

        # Label the element
        ax.text(current_position + length / 2, y_offset + 0.35, name, ha='center', va='bottom', fontsize=8)

        # Update the position
        current_position += length

    # Set plot limits and labels
    ax.set_xlim(0, current_position)
    ax.set_ylim(0, 2)
    ax.set_xlabel("Position along the beamline (m)")
    ax.set_yticks([])
    ax.set_title("Beamline Layout")

    # Create a legend
    legend_elements = [
        plt.Line2D([0], [0], color='blue', lw=4, label='Drift'),
        plt.Line2D([0], [0], color='green', lw=4, label='Focusing Quadrupole'),
        plt.Line2D([0], [0], color='red', lw=4, label='Defocusing Quadrupole'),
        plt.Line2D([0], [0], color='orange', lw=4, label='Bend')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    plt.show()

"""
A Line can be defined in different ways:    
    -   It is possible to provide beam line element objects and the corresponding names
        This was the case for the 'basic_example.py'

    -   It can be imported from an existing MAD-X model, via 'xtract.Line.from_madx_sequence()'
        For example importing the MAD-X file taken from:  
        https://github.com/xsuite/xtrack/blob/main/test_data/psb_chicane/psb_fb_lhc.str

        from cpymad.madx import Madx
        mad = Madx()

        # Here the code is passed to MAD-X so it's actually Fortran
        mad.input('''
        call, file = './madx/psb.seq';
        call, file = './madx/psb_fb_lhc.str';

        beam, particle=PROTON, pc=0.5708301551893517;
        use, sequence=psb1;

        select,flag=error,clear;
        select,flag=error,pattern=bi1.bsw1l1.1*;
        ealign, dx=-0.0057;

        select,flag=error,clear;
        select,flag=error,pattern=bi1.bsw1l1.2*;
        select,flag=error,pattern=bi1.bsw1l1.3*;
        select,flag=error,pattern=bi1.bsw1l1.4*;
        ealign, dx=-0.0442;

        twiss;
        ''')

        line = xt.Line.from_madx_sequence(
            sequence=mad.sequence.psb1,
            allow_thick=True,
            enable_align_errors=True,
            deferred_expressions=True,
        )

    -   A line can also be defined through a “sequence”, providing the element s positions 

        elements = {
        'quad': Multipole(length=0.3, knl=[0, +0.50]),
        'bend': Multipole(length=0.5, knl=[np.pi / 12], hxl=[np.pi / 12]),
        }

        sequences = {
            'arc': [Node(1.0, 'quad'), Node(4.0, 'bend', from_='quad')],
        }

        line = Line.from_sequence([
                Node( 0.0, 'arc'),
                Node(10.0, 'arc', name='section2'),
                Node( 3.0, Multipole(knl=[0, 0, 0.1]), from_='section2', name='sext'),
                Node( 3.0, 'quad', name='quad_5', from_='sext'),
            ], length=20,
            elements=elements, sequences=sequences,
            auto_reorder=True, copy_elements=False,
        )
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
Accelerators and beam lines have complex control paterns.
We can include these dependencies in the simulation model so that changes in the high-level
parameters are automatically propagated down to the line elements properties.
To see more go to https://github.com/xsuite/xtrack/blob/main/examples/toy_ring/002_expressions.py

NB: When importing a MAD-X model...
the dependency relations from MAD-X deferred expressions are automatically imported!
"""
# For each quadrupole we create a variable controlling its integrated strength.
# Expressions can be associated to any beam element property, using the `element_refs`
# attribute of the line. For example:
line.vars['k1l.qf.1'] = 0
line.element_refs['mqf.1'].k1 = line.vars['k1l.qf.1'] / lquad
line.vars['k1l.qd.1'] = 0
line.element_refs['mqd.1'].k1 = line.vars['k1l.qd.1'] / lquad
line.vars['k1l.qf.2'] = 0
line.element_refs['mqf.2'].k1 = line.vars['k1l.qf.2'] / lquad
line.vars['k1l.qd.2'] = 0
line.element_refs['mqd.2'].k1 = line.vars['k1l.qd.2'] / lquad

# When a variable is changed, the corresponding element property is automatically
# updated:
line.vars['k1l.qf.1'] = 0.1
line['mqf.1'].k1 # is 0.333, i.e. 0.1 / lquad

# We can create a variable controlling the integrated strength of the two
# focusing quadrupoles
line.vars['k1lf'] = 0.1
line.vars['k1l.qf.1'] = line.vars['k1lf']
line.vars['k1l.qf.2'] = line.vars['k1lf']
# and a variable controlling the integrated strength of the two defocusing quadrupoles
line.vars['k1ld'] = -0.7
line.vars['k1l.qd.1'] = line.vars['k1ld']
line.vars['k1l.qd.2'] = line.vars['k1ld']

# Changes on the controlling variable are propagated to the two controlled ones and
# to the corresponding element properties:
line.vars['k1lf'] = 0.2
line.vars['k1l.qf.1']._get_value() # is 0.2
line.vars['k1l.qf.2']._get_value() # is 0.2
line['mqf.1'].k1 # is 0.666, i.e. 0.2 / lquad
line['mqf.2'].k1 # is 0.666, i.e. 0.2 / lquad

# The `_info()` method of a variable provides information on the existing relations
# between the variables. For example:
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


# Expressions can include multiple variables and mathematical operations. For example
line.vars['a'] = 3 * line.functions.sqrt(line.vars['k1lf']) + 2 * line.vars['k1ld']

# As seen above, line.vars['varname'] returns a reference object that
# can be used to build further references, or to inspect its properties.
# To get the current value of the variable, one needs to use `._get_value()`
# For quick access to the current value of a variable, one can use the `line.varval`
# attribute or its shortcut `line.vv`:
line.varval['k1lf'] # is 0.2
line.vv['k1lf']     # is 0.2
# Note an important difference when using `line.vars` or `line.varval` in building
# expressions. For example:
line.vars['a'] = 3.
line.vars['b'] = 2 * line.vars['a']
# In this case the reference to the quantity `line.vars['a']` is stored in the
# expression, and the value of `line.vars['b']` is updated when `line.vars['a']`
# changes:
line.vars['a'] = 4.
line.vv['b'] # is 8.
# On the contrary, when using `line.varval` or `line.vv` in building expressions,
# the current value of the variable is stored in the expression:
line.vv['a'] = 3.
line.vv['b'] = 2 * line.vv['a']
line.vv['b'] # is 6.
line.vv['a'] = 4.
line.vv['b'] # is still 6.

# The `line.vars.get_table()` method returns a table with the value of all the
# existing variables:
line.vars.get_table()


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

# Use the function to plot the line
plot_beamline(line)
