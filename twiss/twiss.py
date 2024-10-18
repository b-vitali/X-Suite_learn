import numpy as np
import xtrack as xt
import matplotlib.pyplot as plt

'''
Off-momentum twiss

Reverse reference frame

Twiss with synchrotron radiation
'''

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
spbet.plot(tw.s, tw.betx*1e-3, label=r'$\beta_x$')
spbet.plot(tw.s, tw.bety*1e-3, label=r'$\beta_y$')
spbet.set_ylabel(r'$\beta_{x,y}$ [km]')
spbet.legend()

# Plot horizontal and vertical closed orbits
spco.plot(tw.s, tw.x*1e6, label=r'$x$')
spco.plot(tw.s, tw.y*1e6, label=r'$y$')
spco.set_ylabel(r'(Closed orbit)$_{x,y}$ [$\mu$m]')
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

spbet.set_xlim(tw['s', 'ip5'] - 1000, tw['s', 'ip5'] + 1000)

# Adjust subplot spacing for clarity
fig1.subplots_adjust(left=.15, right=.92, hspace=.27)
plt.show()

#? What about the *beam size*?
# Transverse normalized emittances
nemitt_x = 2.5e-6
nemitt_y = 2.5e-6

# Longitudinal emittance from energy spread
sigma_pzeta = 2e-4
gemitt_zeta = sigma_pzeta**2 * tw.bets0
# similarly, if the bunch length is known, the emittance can be computed as gemitt_zeta = sigma_zeta**2 / tw.bets0

# Compute beam sizes
beam_sizes = tw.get_beam_covariance(nemitt_x=nemitt_x, nemitt_y=nemitt_y,
                                    gemitt_zeta=gemitt_zeta)

# Inspect beam sizes (table can be accessed similarly to twiss tables)
beam_sizes.rows['ip.?'].show()
# prints
#
# name                       s     sigma_x     sigma_y sigma_zeta    sigma_px ...
# ip3                        0 0.000226516 0.000270642    0.19694 4.35287e-06
# ip4                  3332.28 0.000281326 0.000320321   0.196941 1.30435e-06
# ip5                  6664.57  7.0898e-06 7.08975e-06    0.19694  4.7265e-05
# ip6                  9997.01 0.000314392 0.000248136   0.196939 1.61401e-06
# ip7                  13329.4 0.000205156 0.000223772   0.196939 2.70123e-06
# ip8                  16650.7 2.24199e-05 2.24198e-05   0.196939 1.49465e-05
# ip1                  19994.2 7.08975e-06 7.08979e-06   0.196939 4.72651e-05
# ip2                  23326.6 5.78877e-05 5.78878e-05   0.196939 5.78879e-06

# All covariances are computed including those from linear coupling
beam_sizes.keys()
# is:
#
# ['s', 'name', 'sigma_x', 'sigma_y', 'sigma_zeta', 'sigma_px', 'sigma_py',
# 'sigma_pzeta', 'Sigma', 'Sigma11', 'Sigma12', 'Sigma13', 'Sigma14', 'Sigma15',
# 'Sigma16', 'Sigma21', 'Sigma22', 'Sigma23', 'Sigma24', 'Sigma25', 'Sigma26',
# 'Sigma31', 'Sigma32', 'Sigma33', 'Sigma34', 'Sigma41', 'Sigma42', 'Sigma43',
# 'Sigma44', 'Sigma51', 'Sigma52'])

fig2 = plt.figure(1, figsize=(6.4, 4.8*1.5))
spbet = plt.subplot(3,1,1)
spdisp = plt.subplot(3,1,2, sharex=spbet)
spbsz = plt.subplot(3,1,3, sharex=spbet)

spbet.plot(tw.s, tw.betx*1e-3, label=r'$\beta_x$')
spbet.plot(tw.s, tw.bety*1e-3, label=r'$\beta_y$')
spbet.set_ylabel(r'$\beta_{x,y}$ [km]')
spbet.legend()

spdisp.plot(tw.s, tw.dx, label=r'$D_x$')
spdisp.plot(tw.s, tw.dy, label=r'$D_y$')
spdisp.set_ylabel(r'$D_{x,y}$ [m]')
spdisp.set_xlabel('s [m]')
spdisp.legend()

spbsz.plot(beam_sizes.s, beam_sizes.sigma_x*1e3, label=r'$\sigma_x$')
spbsz.plot(beam_sizes.s, beam_sizes.sigma_y*1e3, label=r'$\sigma_y$')
spbsz.set_ylabel(r'$\sigma_{x,y}$ [mm]')
spbsz.set_xlabel('s [m]')
spbsz.legend()

fig2.suptitle(
    r'$q_x$ = ' f'{tw.qx:.5f}' r' $q_y$ = ' f'{tw.qy:.5f}' '\n'
    r"$Q'_x$ = " f'{tw.dqx:.2f}' r" $Q'_y$ = " f'{tw.dqy:.2f}'
    r' $\gamma_{tr}$ = ' f'{1/np.sqrt(tw.momentum_compaction_factor):.2f}'
)

spbet.set_xlim(tw['s', 'ip5'] - 1000, tw['s', 'ip5'] + 1000)

fig2.subplots_adjust(left=.15, right=.92, hspace=.27)
plt.show()

#? Particle physical coordinates <-> normalized coordinates?
# Generate some particles with known normalized coordinates
particles = line.build_particles(
    nemitt_x=2.5e-6, nemitt_y=1e-6,
    x_norm=[-1, 0, 0.5], y_norm=[0.3, -0.2, 0.2],
    px_norm=[0.1, 0.2, 0.3], py_norm=[0.5, 0.6, 0.8],
    zeta=[0, 0.1, -0.1], delta=[1e-4, 0., -1e-4])

# Inspect physical coordinates
tab = particles.get_table()
tab.show()

# Use twiss to compute normalized coordinates
norm_coord = tw.get_normalized_coordinates(particles, nemitt_x=2.5e-6, nemitt_y=1e-6)

# Inspect normalized coordinates
norm_coord.show()

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

#? Initial conditions
# Let's turn RF ON again
line = xt.Line.from_json('twiss_line.json')
line.particle_ref = xt.Particles(mass0=xt.PROTON_MASS_EV, q0=1, energy0=7e12)
line.vars['vrf400'] = 16
line.build_tracker()

# Periodic twiss
tw_p = line.twiss()

# Twiss over a range with user-defined initial conditions (at start)
tw1 = line.twiss(start='ip5', end='mb.c24r5.b1',
                betx=0.15, bety=0.15, py=1e-6)


# Twiss over a range with user-defined initial conditions at end
tw2 = line.twiss(start='ip5', end='mb.c24r5.b1', init_at=xt.END,
                alfx=3.50482, betx=131.189, alfy=-0.677173, bety=40.7318,
                dx=1.22515, dpx=-0.0169647)

# Twiss over a range with user-defined initial conditions at arbitrary location
tw3 = line.twiss(start='ip5', end='mb.c24r5.b1', init_at='mb.c14r5.b1',
                 alfx=-0.437695, betx=31.8512, alfy=-6.73282, bety=450.454,
                 dx=1.22606, dpx=-0.0169647)

# Initial conditions can also be taken from an existing twiss table
tw4 = line.twiss(start='ip5', end='mb.c24r5.b1', init_at='mb.c14r5.b1',
                 init=tw_p)

# More explicitly, a `TwissInit` object can be extracted from the twiss table and used as initial conditions
tw_init = tw_p.get_twiss_init('mb.c14r5.b1',)
tw5 = line.twiss(start='ip5', end='mb.c24r5.b1', init=tw_init)

# Choose the twiss to plot
tw = tw5

import matplotlib.pyplot as plt
plt.close('all')

fig1 = plt.figure(1, figsize=(6.4, 4.8*1.5))
spbet = plt.subplot(3,1,1)
spco = plt.subplot(3,1,2, sharex=spbet)
spdisp = plt.subplot(3,1,3, sharex=spbet)

spbet.plot(tw.s, tw.betx*1e-3, label=r'$\beta_x$')
spbet.plot(tw.s, tw.bety*1e-3, label=r'$\beta_y$')
spbet.set_ylabel(r'$\beta_{x,y}$ [km]')
spbet.legend()

spco.plot(tw.s, tw.x*1e6, label=r'$x$')
spco.plot(tw.s, tw.y*1e6, label=r'$y$')
spco.set_ylabel(r'(Closed orbit)$_{x,y}$ [$\mu$m]')
spco.legend()

spdisp.plot(tw.s, tw.dx, label=r'$D_x$')
spdisp.plot(tw.s, tw.dy, label=r'$D_y$')
spdisp.set_ylabel(r'$D_{x,y}$ [m]')
spdisp.set_xlabel('s [m]')
spdisp.legend()

for nn in ['ip5', 'mb.c14r5.b1', 'mb.c24r5.b1']:
    for ax in [spbet, spco, spdisp]:
        ax.axvline(tw_p['s', nn], color='k', ls='--', alpha=.5)
    spbet.text(tw_p['s', nn], 22, nn, rotation=90,
        horizontalalignment='right', verticalalignment='top', alpha=.5)

fig1.subplots_adjust(left=.15, right=.92, hspace=.27)

# Display the plot
plt.show()
