"""
Le't try and define a ring with proper twiss parameters and FODO structure
We will then create an insertion for an experiment
This is taken from https://github.com/xsuite/tutorial_lattice_design/
"""
import xtrack as xt
import numpy as np
import matplotlib.pyplot as plt

# Initialize the simulation environment
env = xt.Environment()

# Set up a reference particle with a momentum of 2 GeV/c
env.particle_ref = xt.Particles(p0c=2e9)

# Define the structure of the accelerator arc
# - An arc is composed of several cells and each cell contains bends and other components
n_bends_per_cell = 6    # Number of bending magnets per cell
n_cells_par_arc = 3     # Number of cells per arc section
n_arcs = 3              # Number of arc sections in the ring

# Calculate the total number of bends in the ring
n_bends = n_bends_per_cell * n_cells_par_arc * n_arcs

# Define parameters for components in the arc
env.vars({
    'l.mq': 0.5,                        # Length of the quadrupoles
    'kqf': 0.027,                       # Focusing strength for quadrupole (k1 parameter)
    'kqd': -0.0271,                     # Defocusing strength for quadrupole (k1 parameter)
    'l.mb': 10,                         # Length of the bending magnets
    'l.ms': 0.3,                        # Length of the sextupoles
    'k2sf': 0.001,                      # Focusing strength for sextupoles (k2 parameter)
    'k2sd': -0.001,                     # Defocusing strength for sextupoles (k2 parameter)
    'angle.mb': 2 * np.pi / n_bends,    # Bending angle per bending magnet (full circle divided by total number of bends)
    'k0.mb': 'angle.mb / l.mb',         # Strength of the bending magnet (k0 parameter)
    'k0l.corrector': 0,                 # Default strength for dipole correctors (set to 0 initially)
    'k1sl.corrector': 0,                # Default skew quadrupole corrector strength (set to 0 initially)
    'l.halfcell': 38,                   # Length of half the cell
})

# Define basic magnet components in the environment
env.new('mb', xt.Bend, length='l.mb', k0='k0.mb', h='k0.mb')  # Bending magnet
env.new('mq', xt.Quadrupole, length='l.mq')                   # Generic quadrupole
env.new('ms', xt.Sextupole, length='l.ms')                    # Generic sextupole
env.new('corrector', xt.Multipole, knl=[0], ksl=[0])          # Generic corrector (dipole and skew quadrupole correctors)

# Define arc-specific quadrupoles
env.new('mq.f', 'mq', k1='kqf')  # Focusing quadrupole
env.new('mq.d', 'mq', k1='kqd')  # Defocusing quadrupole

# Define arc-specific sextupoles
env.new('ms.d', 'ms', k2='k2sf')  # Sextupole for dispersion correction
env.new('ms.f', 'ms', k2='k2sd')  # Sextupole for chromaticity correction

# Define the first half of the arc cell
halfcell = env.new_line(components=[
    # Midpoint marker of the half-cell
    env.new('mid', xt.Marker, at='l.halfcell'),
    
    # Bending magnets (placed symmetrically within the half cell)
    env.new('mb.2', 'mb', at='l.halfcell / 2'),
    env.new('mb.1', 'mb', at='-l.mb - 1', from_='mb.2'),  # Position is relative to mb.2
    env.new('mb.3', 'mb', at='l.mb + 1', from_='mb.2'),   # Position is relative to mb.2
    
    # Quadrupoles
    env.place('mq.d', at= '0.5 + l.mq / 2'),                # Defocusing quadrupole
    env.place('mq.f', at='l.halfcell - l.mq / 2 - 0.5'),    # Focusing quadrupole
    
    # Sextupoles (placed close to quadrupoles)
    env.new('ms.d', 'ms', k2='k2sf', at=1.2, from_='mq.d'),  # Sextupole near defocusing quad
    env.new('ms.f', 'ms', k2='k2sd', at=-1.2, from_='mq.f'), # Sextupole near focusing quad
    
    # Dipole correctors (to correct orbit errors)
    env.new('corrector.v', 'corrector', at=0.75, from_='mq.d'),
    env.new('corrector.h', 'corrector', at=-0.75, from_='mq.f')
])

# Plot the layout (survey) of the half-cell to visualize its structure
halfcell.survey().plot()

# Define the full cell by mirroring the half-cell
cell = env.new_line(components=[
    env.new('start', xt.Marker),  # Start marker
    -halfcell,                    # Mirror the first half of the cell
    halfcell,                     # Add the second half of the cell
    env.new('end', xt.Marker),    # End marker
])

# Plot the layout (survey) of the full cell
cell.survey().plot()

# Compute and plot the optics (Twiss parameters) for the full cell
cell.twiss4d().plot()

# Perform phase advance matching (setting the tunes to specific values)
opt = cell.match(
    solve=False,  # Do not solve immediately; we'll inspect before solving
    method='4d',  # 4D matching method
    vary=xt.VaryList(['kqf', 'kqd'], step=1e-5),  # Vary the strengths of the focusing and defocusing quadrupoles
    targets=xt.TargetSet(
        qx=0.333333,  # Target horizontal tune (fractional part of betatron oscillation)
        qy=0.333333,  # Target vertical tune
    ))

# Print the status of the matching targets before solving
print('Before match:')
opt.target_status()

# Solve the matching problem
opt.solve()

# Print the status of the matching targets after solving
print('After match:')
opt.target_status()

# Print the optimization log/history
print('\nMatch history')
opt.log()

# Plot the updated optics (Twiss parameters) after matching
tw_cell = cell.twiss4d()
tw_cell.plot()

# Plot the horizontal and vertical phase advance (mux and muy)
# These are critical to understand how the lattice affects the particle motion.
tw_cell.plot('mux muy')


# Define parameters for the straight section
# The focusing and defocusing strengths are halved compared to the arc
env.vars({
    'kqf.ss': 0.027 / 2,     # Reduced focusing strength for quadrupole in the straight section
    'kqd.ss': -0.0271 / 2,   # Reduced defocusing strength for quadrupole in the straight section
})

# Define a half-cell structure for the straight section
halfcell_ss = env.new_line(components=[
    env.new('mid', xt.Marker, at='l.halfcell'),   # Midpoint marker for the straight section
    
    # Straight section quadrupoles
    env.new('mq.ss.d', 'mq', k1='kqd.ss', at='0.5 + l.mq / 2'),                # Defocusing quadrupole
    env.new('mq.ss.f', 'mq', k1='kqf.ss', at='l.halfcell - l.mq / 2 - 0.5'),   # Focusing quadrupole
    
    # Correctors for the straight section
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
# This provides a visual representation of the straight section layout, showing the components' placement.
cell_ss.survey().plot()

# March to the same betas as the edge of the arc cell
opt = cell_ss.match(
    method='4d',
    vary=xt.VaryList(['kqf.ss', 'kqd.ss'], step=1e-5),
    targets=xt.TargetSet(
        betx=tw_cell.betx[-1], bety=tw_cell.bety[-1], at='start.ss',
    ))


# Assemble a ring
arc = 3 * cell
arc.survey().plot()

straight_section = 2*cell_ss
straight_section.survey().plot()


ring = 3 * (arc + straight_section)
ring.survey().plot()


# # # Inspect optics

# # In[20]:


# tw = ring.twiss4d()
# fig = plt.figure(figsize=(6.4*1.2, 4.8))
# ax1 = fig.add_subplot(2, 1, 1)
# pltbet = tw.plot('betx bety', ax=ax1)

# ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)
# pltdx = tw.plot('dx', ax=ax2)

# fig.subplots_adjust(right=.85)
# pltbet.move_legend(1.2,1)
# pltdx.move_legend(1.2,1)


# # ## Build and insertion

# # We want 40 m of free space with round betas to install an experiment

# # In[21]:


# env.vars({
#     'k1.q1': 0.025,
#     'k1.q2': -0.025,
#     'k1.q3': 0.025,
#     'k1.q4': -0.02,
#     'k1.q5': 0.025,
# })
# env.new('mq.1', 'mq', k1='k1.q1')

# half_insertion = env.new_line(components=[

#     # Start-end markers
#     env.new('ip', xt.Marker),
#     env.new('e.insertion', xt.Marker, at=76), # Same insertion length as initial straight

#     # Quads
#     env.new('mq.1', 'mq', k1='k1.q1', at = 20),
#     env.new('mq.2', 'mq', k1='k1.q2', at = 25),
#     env.new('mq.3', 'mq', k1='k1.q3', at=37),
#     env.new('mq.4', 'mq', k1='k1.q4', at=55),
#     env.new('mq.5', 'mq', k1='k1.q5', at=73),

#     # Dipole correctors (will use h and v on the same corrector)
#     env.new('corrector.ss.1', 'corrector', at=0.75, from_='mq.1'),
#     env.new('corrector.ss.2', 'corrector', at=-0.75, from_='mq.2'),
#     env.new('corrector.ss.3', 'corrector', at=0.75, from_='mq.3'),
#     env.new('corrector.ss.4', 'corrector', at=-0.75, from_='mq.4'),
#     env.new('corrector.ss.5', 'corrector', at=0.75, from_='mq.5'),

# ])


# # In[22]:


# # Match the optics of the insertion
# tw_arc = arc.twiss4d()

# opt = half_insertion.match(
#     solve=False,
#     betx=tw_arc.betx[0], bety=tw_arc.bety[0],
#     alfx=tw_arc.alfx[0], alfy=tw_arc.alfy[0],
#     init_at='e.insertion',
#     start='ip', end='e.insertion',
#     vary=xt.VaryList(['k1.q1', 'k1.q2', 'k1.q3', 'k1.q4', 'k1.q5'], step=1e-5),
#     targets=[
#         xt.TargetSet(alfx=0, alfy=0, at='ip'),
#         xt.Target(lambda tw: tw['betx', 'ip'] - tw['bety', 'ip'], 0),
#         xt.Target(lambda tw: tw.betx.max(), xt.LessThan(400)),
#         xt.Target(lambda tw: tw.bety.max(), xt.LessThan(400)),
#         xt.Target(lambda tw: tw.betx.min(), xt.GreaterThan(2)),
#         xt.Target(lambda tw: tw.bety.min(), xt.GreaterThan(2)),
#     ]
# )
# opt.step(40)
# opt.solve()


# # In[23]:


# insertion = -half_insertion + half_insertion

# insertion.twiss4d().plot()


# # ## Build a ring wih the insertion

# # In[24]:


# ring_2 = 2 * (arc + straight_section) + arc + insertion


# # In[25]:


# ring_2.survey().plot()


# # In[26]:


# tw = ring_2.twiss4d()
# fig = plt.figure(figsize=(6.4*1.2, 4.8))
# ax1 = fig.add_subplot(2, 1, 1)
# pltbet = tw.plot('betx bety', ax=ax1)

# ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)
# pltdx = tw.plot('dx', ax=ax2)

# fig.subplots_adjust(right=.85)
# pltbet.move_legend(1.2,1)
# pltdx.move_legend(1.2,1)


# # In[27]:


# # Make a shallow copy a and slice to get optics every 0.5 m
# ring_2_sliced = ring_2.select()
# ring_2_sliced.replace_all_repeated_elements(mode='replica')


# # In[28]:


# ring_2_sliced.get_table().show()
# plt.show()


# # In[30]:


# ring_2_sliced.cut_at_s(np.arange(0, ring_2.get_length(), 0.5))


# # In[31]:


# tw = ring_2_sliced.twiss4d()
# fig = plt.figure(figsize=(6.4*1.2, 4.8))
# ax1 = fig.add_subplot(2, 1, 1)
# pltbet = tw.plot('betx bety', ax=ax1)

# ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)
# pltdx = tw.plot('dx', ax=ax2)

# fig.subplots_adjust(right=.85)
# pltbet.move_legend(1.2,1)
# pltdx.move_legend(1.2,1)


# # In[32]:


# 1/np.sqrt(tw.momentum_compaction_factor)


# # In[33]:


# tw.qx


# # In[ ]:





##############


plt.show()