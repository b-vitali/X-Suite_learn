"""
Let's try to define a ring with proper Twiss parameters and FODO structure.
We will then create an insertion for an experiment.
This script is adapted from the tutorial found at https://github.com/xsuite/tutorial_lattice_design/
"""

#? Import required libraries
import xtrack as xt
import numpy as np
import matplotlib.pyplot as plt

# Initialize the simulation environment
env = xt.Environment()

# Set up a reference particle with a momentum of 2 GeV/c
env.particle_ref = xt.Particles(p0c=2e9)

#? Define the structure of the accelerator arc
# An arc is composed of several cells, and each cell contains bending magnets and other components.
n_bends_per_cell = 6    # Bending magnets per cell
n_cells_par_arc = 3     # Cells per arc section
n_arcs = 3              # Arc sections in the ring

# Calculate the total number of bends in the entire ring
n_bends = n_bends_per_cell * n_cells_par_arc * n_arcs

# Define parameters for components in the arc section
env.vars({
    'l.mq': 0.5,                        # Length of the quadrupoles
    'kqf': 0.027,                       # Focusing strength for the quadrupole (k1 parameter)
    'kqd': -0.0271,                     # Defocusing strength for the quadrupole (k1 parameter)
    'l.mb': 10,                         # Length of the bending magnets
    'l.ms': 0.3,                        # Length of the sextupoles
    'k2sf': 0.001,                      # Focusing strength for sextupoles (k2 parameter)
    'k2sd': -0.001,                     # Defocusing strength for sextupoles (k2 parameter)
    'angle.mb': 2 * np.pi / n_bends,    # Bending angle per bending magnet (full circle divided by total number of bends)
    'k0.mb': 'angle.mb / l.mb',         # Strength of the bending magnet (k0 parameter)
    'k0l.corrector': 0,                 # Default strength for dipole correctors (initially set to 0)
    'k1sl.corrector': 0,                # Default skew quadrupole corrector strength (initially set to 0)
    'l.halfcell': 38,                   # Length of half the cell
})

# Define basic magnet components in the environment
env.new('mb', xt.Bend, length='l.mb', k0='k0.mb', h='k0.mb')  # Bending magnet
env.new('mq', xt.Quadrupole, length='l.mq')                   # Generic quadrupole
env.new('ms', xt.Sextupole, length='l.ms')                    # Generic sextupole
env.new('corrector', xt.Multipole, knl=[0], ksl=[0])          # Generic corrector (dipole and skew quadrupole correctors)

# Define arc-specific quadrupoles with specific focusing/defocusing strengths
env.new('mq.f', 'mq', k1='kqf')  # Focusing quadrupole
env.new('mq.d', 'mq', k1='kqd')  # Defocusing quadrupole

# Define arc-specific sextupoles for correcting chromaticity and dispersion
env.new('ms.d', 'ms', k2='k2sf')  # Sextupole for dispersion correction
env.new('ms.f', 'ms', k2='k2sd')  # Sextupole for chromaticity correction

# Define the first half of the arc cell
halfcell = env.new_line(components=[

    # Midpoint marker of the half-cell
    env.new('mid', xt.Marker, at='l.halfcell'),
    
    # Bending magnets placed symmetrically within the half-cell
    env.new('mb.2', 'mb', at='l.halfcell / 2'),             # Center bending magnet
    env.new('mb.1', 'mb', at='-l.mb - 1', from_='mb.2'),    # Left magnet relative to the center
    env.new('mb.3', 'mb', at='l.mb + 1', from_='mb.2'),     # Right magnet relative to the center
    
    # Positioning the quadrupoles within the half-cell
    env.place('mq.d', at='0.5 + l.mq / 2'),                 # Defocusing quadrupole
    env.place('mq.f', at='l.halfcell - l.mq / 2 - 0.5'),    # Focusing quadrupole
    
    # Sextupoles placed near the quadrupoles to enhance performance
    env.new('ms.d', 'ms', k2='k2sf', at=1.2, from_='mq.d'),  # Sextupole near the defocusing quadrupole
    env.new('ms.f', 'ms', k2='k2sd', at=-1.2, from_='mq.f'), # Sextupole near the focusing quadrupole
    
    # Dipole correctors for orbit error corrections
    env.new('corrector.v', 'corrector', at=0.75, from_='mq.d'),  # Vertical corrector after the defocusing quadrupole
    env.new('corrector.h', 'corrector', at=-0.75, from_='mq.f')  # Horizontal corrector before the focusing quadrupole
])

# Plot the layout of the half-cell to visualize its structure
halfcell.survey().plot()

# Define the full cell by mirroring the half-cell
cell = env.new_line(components=[
    env.new('start', xt.Marker),  # Start marker for the cell
    -halfcell,                    # Mirror the first half of the cell to create the second half
    halfcell,                     # Add the second half of the cell
    env.new('end', xt.Marker),    # End marker for the cell
])

# Plot the layout of the full cell
cell.survey().plot()

# Compute and plot the optics (Twiss parameters) for the full cell
cell.twiss4d().plot()

# Perform phase advance matching to achieve desired tunes
opt = cell.match(
    solve=False,  # Do not solve immediately; allows for inspection before solving
    method='4d',  # Use the 4D matching method for better accuracy
    vary=xt.VaryList(['kqf', 'kqd'], step=1e-5),  # Vary the strengths of focusing and defocusing quadrupoles
    targets=xt.TargetSet(
        qx=0.333333,  # Target horizontal tune (fractional part of betatron oscillation)
        qy=0.333333,  # Target vertical tune
    ))

# Print the status of the matching targets before attempting to solve
print('Before match:')
opt.target_status()

# Solve the matching problem to achieve the desired optics
opt.solve()

# Print the status of the matching targets after solving
print('After match:')
opt.target_status()

# Print the optimization log/history for debugging and analysis
print('\nMatch history')
opt.log()

# Plot the updated optics (Twiss parameters) after matching to visualize changes
tw_cell = cell.twiss4d()
tw_cell.plot()

# Plot the horizontal and vertical phase advance (mux and muy)
tw_cell.plot('mux muy')


#? Define parameters for the straight section
# The focusing and defocusing strengths are halved compared to the arc
env.vars({
    'kqf.ss': 0.027 / 2,     # Reduced focusing strength for quadrupole in the straight section
    'kqd.ss': -0.0271 / 2,   # Reduced defocusing strength for quadrupole in the straight section
})

# Define a half-cell structure for the straight section
halfcell_ss = env.new_line(components=[
    env.new('mid', xt.Marker, at='l.halfcell'),   # Midpoint marker for the straight section
    
    # Define straight section quadrupoles with adjusted strengths
    env.new('mq.ss.d', 'mq', k1='kqd.ss', at='0.5 + l.mq / 2'),                # Defocusing quadrupole
    env.new('mq.ss.f', 'mq', k1='kqf.ss', at='l.halfcell - l.mq / 2 - 0.5'),   # Focusing quadrupole
    
    # Correctors for the straight section to maintain optimal performance
    env.new('corrector.ss.v', 'corrector', at=0.75, from_='mq.ss.d'),          # Vertical corrector
    env.new('corrector.ss.h', 'corrector', at=-0.75, from_='mq.ss.f')          # Horizontal corrector
])

# Mirror and replicate the half-cell to create the full straight section cell
hcell_left_ss = halfcell_ss.replicate(name='l', mirror=True)  # Left half of the straight section (mirrored)
hcell_right_ss = halfcell_ss.replicate(name='r')              # Right half of the straight section

# Assemble the full straight section cell by combining the mirrored left and right halves
cell_ss = env.new_line(components=[
    env.new('start.ss', xt.Marker),  # Start marker for the straight section
    hcell_left_ss,                   # Left mirrored half-cell
    hcell_right_ss,                  # Right half-cell
    env.new('end.ss', xt.Marker),    # End marker for the straight section
])

# Plot the layout of the straight section cell
cell_ss.survey().plot()

# Match the optics of the straight section to the end of the arc cell
opt = cell_ss.match(
    method='4d',
    vary=xt.VaryList(['kqf.ss', 'kqd.ss'], step=1e-5),
    targets=xt.TargetSet(
        betx=tw_cell.betx[-1], bety=tw_cell.bety[-1], at='start.ss',  # Match beta functions at the start of the straight section
    ))

#? Assemble the full ring structure
arc = 3 * cell  # Create three identical arcs
arc.survey().plot()  # Plot the arcs

straight_section = 2 * cell_ss  # Create two straight sections
straight_section.survey().plot()  # Plot the straight sections

# Combine arcs and straight sections to form the complete ring
ring = 3 * (arc + straight_section)
ring.survey().plot()  # Visualize the entire ring structure

# Inspect optics for the entire ring structure
tw = ring.twiss4d()  # Compute Twiss parameters for the full ring
fig = plt.figure(figsize=(6.4*1.2, 4.8))  # Create a new figure for plotting
ax1 = fig.add_subplot(2, 1, 1)  # Create the first subplot for beta functions
pltbet = tw.plot('betx bety', ax=ax1)  # Plot horizontal and vertical beta functions

ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)  # Create the second subplot for dispersion
pltdx = tw.plot('dx', ax=ax2)  # Plot the horizontal dispersion

# Adjust layout and legend positions for clarity
fig.subplots_adjust(right=.85)
pltbet.move_legend(1.2, 1)  # Move beta function legend
pltdx.move_legend(1.2, 1)  # Move dispersion legend


#? Build and insert an experimental setup into the accelerator
# We aim to create 40 meters of free space with round beta functions for the insertion

# Define strength values for quadrupoles used in the insertion
env.vars({
    'k1.q1': 0.025, 
    'k1.q2': -0.025,
    'k1.q3': 0.025, 
    'k1.q4': -0.02, 
    'k1.q5': 0.025, 
})

# Create a half insertion with specified components
half_insertion = env.new_line(components=[
    # Start and end markers for the insertion
    env.new('ip', xt.Marker),                             # Insertion point marker
    env.new('e.insertion', xt.Marker, at=76),            # End marker for the insertion

    # Adding quadrupoles at specified positions within the insertion
    env.new('mq.1', 'mq', k1='k1.q1', at=20),
    env.new('mq.2', 'mq', k1='k1.q2', at=25),
    env.new('mq.3', 'mq', k1='k1.q3', at=37),
    env.new('mq.4', 'mq', k1='k1.q4', at=55),
    env.new('mq.5', 'mq', k1='k1.q5', at=73),

    # Adding dipole correctors for orbit correction (both horizontal and vertical)
    env.new('corrector.ss.1', 'corrector', at=0.75, from_='mq.1'), 
    env.new('corrector.ss.2', 'corrector', at=-0.75, from_='mq.2'),
    env.new('corrector.ss.3', 'corrector', at=0.75, from_='mq.3'), 
    env.new('corrector.ss.4', 'corrector', at=-0.75, from_='mq.4'),
    env.new('corrector.ss.5', 'corrector', at=0.75, from_='mq.5'), 
])

# Match the optics of the insertion to ensure compatibility with surrounding components
tw_arc = arc.twiss4d()  # Retrieve Twiss parameters from the arc

# Set up the matching process with specific targets and conditions
opt = half_insertion.match(
    solve=False,  # Do not solve immediately; allows for inspection before solving
    betx=tw_arc.betx[0],  # Target beta function in x at the start of the insertion
    bety=tw_arc.bety[0],  # Target beta function in y at the start of the insertion
    alfx=tw_arc.alfx[0],  # Target alpha function in x at the start
    alfy=tw_arc.alfy[0],  # Target alpha function in y at the start
    init_at='e.insertion', # Initialize matching at the end of the insertion
    start='ip', end='e.insertion',  # Define start and end for the matching
    vary=xt.VaryList(['k1.q1', 'k1.q2', 'k1.q3', 'k1.q4', 'k1.q5'], step=1e-5),  # Parameters to vary during matching
    targets=[  # Conditions to satisfy during matching
        xt.TargetSet(alfx=0, alfy=0, at='ip'),  # Match alpha functions to 0 at the insertion point
        xt.Target(lambda tw: tw['betx', 'ip'] - tw['bety', 'ip'], 0),  # Match beta functions to be equal at 'ip'
        xt.Target(lambda tw: tw.betx.max(), xt.LessThan(400)),  # Ensure max beta in x is less than 400
        xt.Target(lambda tw: tw.bety.max(), xt.LessThan(400)),  # Ensure max beta in y is less than 400
        xt.Target(lambda tw: tw.betx.min(), xt.GreaterThan(2)),  # Ensure min beta in x is greater than 2
        xt.Target(lambda tw: tw.bety.min(), xt.GreaterThan(2)),  # Ensure min beta in y is greater than 2
    ]
)

# Execute a step in the optimization process with a specified distance
opt.step(40)  # Perform a step of size 40 in the matching process
opt.solve()  # Solve the matching problem

# Construct the insertion by mirroring the half insertion
insertion = -half_insertion + half_insertion  # Combine halves to create the full insertion

# Plot the Twiss parameters for the insertion to visualize its optics
insertion.twiss4d().plot()

#? Build the complete ring with the newly created insertion
ring_2 = 2 * (arc + straight_section) + arc + insertion

# Visualize the entire ring structure
ring_2.survey().plot()

# Calculate and retrieve the Twiss parameters for the complete ring
tw = ring_2.twiss4d()
fig = plt.figure(figsize=(6.4*1.2, 4.8))  # Create a new figure for plotting

# Plot the beta functions for the ring
ax1 = fig.add_subplot(2, 1, 1)  # First subplot for beta functions
pltbet = tw.plot('betx bety', ax=ax1)  # Plot horizontal and vertical beta functions

# Plot the horizontal dispersion
ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)  # Second subplot for dispersion, sharing x-axis with the first
pltdx = tw.plot('dx', ax=ax2)  # Plot horizontal dispersion

# Adjust layout to improve clarity of the plots
fig.subplots_adjust(right=.85)  # Adjust subplot spacing
pltbet.move_legend(1.2, 1)  # Move the legend for beta functions
pltdx.move_legend(1.2, 1)  # Move the legend for dispersion

# Display the plots
plt.show()  