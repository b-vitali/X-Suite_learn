import numpy as np
import xtrack as xt
import matplotlib.pyplot as plt

#? How to generate and access the line.twiss() info
# Load a beamline from a JSON file and set up the reference particle
line = xt.Line.from_json('twiss_line.json')
line.particle_ref = xt.Particles(mass0=xt.PROTON_MASS_EV, q0=1, energy0=7e12)  # Define the reference particle as a proton with 7 TeV energy

# Set the RF voltage variable 'vrf400' to 16 MV
line.vars['vrf400'] = 16

# Build the tracker for the beamline
line.build_tracker()

# Compute Twiss parameters (optical functions of the beamline)
tw = line.twiss()

## The full information is shown via
# tw.show()

# Inspect fundamental parameters
tw.qx  # Horizontal tune
tw.qy  # Vertical tune
tw.dqx # Horizontal chromaticity
tw.dqy # Vertical chromaticity

# Create plots for closed orbit, beta functions, and dispersion
plt.close('all')  # Close any existing plots

fig1 = plt.figure(1, figsize=(6.4, 4.8*1.5))  # Create a figure with increased height for better visibility
spbet = plt.subplot(3,1,1)  # Subplot for beta functions
spco = plt.subplot(3,1,2, sharex=spbet)  # Subplot for the closed orbit, sharing the x-axis with the beta functions
spdisp = plt.subplot(3,1,3, sharex=spbet)  # Subplot for dispersion functions, also sharing the x-axis

# Plot horizontal and vertical beta functions
spbet.plot(tw.s, tw.betx, label=r'$\beta_x$')
spbet.plot(tw.s, tw.bety, label=r'$\beta_y$')
spbet.set_ylabel(r'$\beta_{x,y}$ [m]')
spbet.legend()

# Plot horizontal and vertical closed orbits
spco.plot(tw.s, tw.x, label=r'$x$')
spco.plot(tw.s, tw.y, label=r'$y$')
spco.set_ylabel(r'(Closed orbit)$_{x,y}$ [m]')
spco.legend()

# Plot horizontal and vertical dispersions
spdisp.plot(tw.s, tw.dx, label=r'$D_x$')
spdisp.plot(tw.s, tw.dy, label=r'$D_y$')
spdisp.set_ylabel(r'$D_{x,y}$ [m]')
spdisp.set_xlabel('s [m]')
spdisp.legend()

# Set the overall figure title to include key optical parameters: tunes, chromaticities, and gamma transition
fig1.suptitle(
    r'$q_x$ = ' f'{tw.qx:.5f}' r' $q_y$ = ' f'{tw.qy:.5f}' '\n'
    r"$Q'_x$ = " f'{tw.dqx:.2f}' r" $Q'_y$ = " f'{tw.dqy:.2f}'
    r' $\gamma_{tr}$ = ' f'{1/np.sqrt(tw.momentum_compaction_factor):.2f}'
)

# Adjust subplot spacing for clarity
fig1.subplots_adjust(left=.15, right=.92, hspace=.27)

#? What if there is no RF?
# Let's turn the RF off
tab = line.get_table()
tab_cav = tab.rows[tab.element_type == 'Cavity']
for nn in tab_cav.name:
    line[nn].voltage = 0

# For this configuration, `line.twiss()` gives an error because the longitudinal motion is not stable.
# In this case, the '4d' method of `line.twiss()` can be used to compute the twiss parameters.
tw = line.twiss(method='4d')

# tw.show()

#?

# Display the plot
plt.show()
