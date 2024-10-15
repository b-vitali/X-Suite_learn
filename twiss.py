import numpy as np
import matplotlib.pyplot as plt

import xtrack as xt


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

# Build a simple ring
env = xt.Environment()
pi = np.pi
lbend = 3
line = env.new_line(components=[
    # Three dipoles to make a closed orbit bump
    env.new('d0.1',  xt.Drift,  length=0.05),
    env.new('bumper_0',  xt.Bend, length=0.05, k0=0, h=0),
    env.new('d0.2',  xt.Drift, length=0.3),
    env.new('bumper_1',  xt.Bend, length=0.05, k0=0, h=0),
    env.new('d0.3',  xt.Drift, length=0.3),
    env.new('bumper_2',  xt.Bend, length=0.05, k0=0, h=0),
    env.new('d0.4',  xt.Drift, length=0.2),

    # Simple ring with two FODO cells
    env.new('mqf.1', xt.Quadrupole, length=0.3, k1=0.1),
    env.new('d1.1',  xt.Drift, length=1),
    env.new('mb1.1', xt.Bend, length=lbend, k0=pi / 2 / lbend, h=pi / 2 / lbend),
    env.new('d2.1',  xt.Drift, length=1),
    env.new('mqd.1', xt.Quadrupole, length=0.3, k1=-0.7),
    env.new('d3.1',  xt.Drift, length=1),
    env.new('mb2.1', xt.Bend, length=lbend, k0=pi / 2 / lbend, h=pi / 2 / lbend),
    env.new('d3.4',  xt.Drift, length=1),
    env.new('mqf.2', xt.Quadrupole, length=0.3, k1=0.1),
    env.new('d1.2',  xt.Drift, length=1),
    env.new('mb1.2', xt.Bend, length=lbend, k0=pi / 2 / lbend, h=pi / 2 / lbend),
    env.new('d2.2',  xt.Drift, length=1),
    env.new('mqd.2', xt.Quadrupole, length=0.3, k1=-0.7),
    env.new('d3.2',  xt.Drift, length=1),
    env.new('mb2.2', xt.Bend, length=lbend, k0=pi / 2 / lbend, h=pi / 2 / lbend),
])

line.slice_thick_elements(
    slicing_strategies=[
        # Slicing with thin elements
        xt.Strategy(slicing=xt.Teapot(1)), # (1) Default applied to all elements
        xt.Strategy(slicing=xt.Uniform(2), element_type=xt.Bend), # (2) Selection by element type
        xt.Strategy(slicing=xt.Teapot(3), element_type=xt.Quadrupole),  # (4) Selection by element type
        xt.Strategy(slicing=xt.Teapot(4), name='mb1.*'), # (5) Selection by name pattern
        # Slicing with thick elements
        xt.Strategy(slicing=xt.Uniform(2, mode='thick'), name='mqf.*'), # (6) Selection by name pattern
        # Do not slice (leave untouched)
        xt.Strategy(slicing=None, name='mqd.1') # (7) Selection by name
    ])
line.build_tracker()

kin_energy_0 = 50e6 # 50 MeV
line.particle_ref = xt.Particles(energy0=kin_energy_0 + xt.PROTON_MASS_EV, # total energy
                                 mass0=xt.PROTON_MASS_EV)

# Use the function to plot the line
plot_beamline(line)

# Twiss
tw = line.twiss(method='4d')

# Inspect tunes and chromaticities
tw.qx # Horizontal tune
tw.qy # Vertical tune
tw.dqx # Horizontal chromaticity
tw.dqy # Vertical chromaticity

tw.show()

# Plot closed orbit and lattice functions
import matplotlib.pyplot as plt
plt.close('all')

fig1 = plt.figure(1, figsize=(6.4, 4.8*1.5))
spbet = plt.subplot(3,1,1)
spco = plt.subplot(3,1,2, sharex=spbet)
spdisp = plt.subplot(3,1,3, sharex=spbet)

spbet.plot(tw.s, tw.betx)
spbet.plot(tw.s, tw.bety)
spbet.set_ylabel(r'$\beta_{x,y}$ [m]')

spco.plot(tw.s, tw.x)
spco.plot(tw.s, tw.y)
spco.set_ylabel(r'(Closed orbit)$_{x,y}$ [m]')

spdisp.plot(tw.s, tw.dx)
spdisp.plot(tw.s, tw.dy)
spdisp.set_ylabel(r'$D_{x,y}$ [m]')
spdisp.set_xlabel('s [m]')

fig1.suptitle(
    r'$q_x$ = ' f'{tw.qx:.5f}' r' $q_y$ = ' f'{tw.qy:.5f}' '\n'
    r"$Q'_x$ = " f'{tw.dqx:.2f}' r" $Q'_y$ = " f'{tw.dqy:.2f}'
    r' $\gamma_{tr}$ = '  f'{1/np.sqrt(tw.momentum_compaction_factor):.2f}'
)

fig1.subplots_adjust(left=.15, right=.92, hspace=.27)
plt.show()


