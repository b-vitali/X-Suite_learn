import xtrack as xt
import matplotlib.pyplot as plt
import numpy as np

# Load a line and build a tracker
line = xt.Line.from_json('match_line.json')
line.build_tracker()

# Initial twiss before tuning
tw_before = line.twiss(method='4d')

# Inspect fundamental parameters before tuning
qx_before = tw_before.qx  # Horizontal tune before
qy_before = tw_before.qy  # Vertical tune before
dqx_before = tw_before.dqx  # Horizontal chromaticity before
dqy_before = tw_before.dqy  # Vertical chromaticity before

# Match tunes and chromaticities to assigned values
opt = line.match(
    method='4d', # <- passed to twiss
    vary=[
        xt.VaryList(['kqtf.b1', 'kqtd.b1'], step=1e-8, tag='quad'),
        xt.VaryList(['ksf.b1', 'ksd.b1'], step=1e-4, limits=[-0.1, 0.1], tag='sext'),
    ],
    targets = [
        xt.TargetSet(qx=62.315, qy=60.325, tol=1e-6, tag='tune'),
        xt.TargetSet(dqx=10.0, dqy=12.0, tol=0.01, tag='chrom'),
    ])

# Final twiss after tuning
tw_after = line.twiss(method='4d')

# Inspect fundamental parameters after tuning
qx_after = tw_after.qx  # Horizontal tune after
qy_after = tw_after.qy  # Vertical tune after
dqx_after = tw_after.dqx  # Horizontal chromaticity after
dqy_after = tw_after.dqy  # Vertical chromaticity after

# Create plots for closed orbit, beta functions, dispersion, and differences
plt.close('all')  # Close any existing plots

fig1 = plt.figure(1, figsize=(6.4, 4.8*1.5))  # Create a figure with increased height for better visibility
spbet = plt.subplot(3, 1, 1)  # Subplot for beta functions
spco = plt.subplot(3, 1, 2, sharex=spbet)  # Subplot for the closed orbit, sharing the x-axis with the beta functions
spdisp = plt.subplot(3, 1, 3, sharex=spbet)  # Subplot for dispersion functions, also sharing the x-axis

# Plot horizontal and vertical beta functions
spbet.plot(tw_after.s, tw_after.betx * 1e-3, label=r'$\beta_x$ (after)')
spbet.plot(tw_after.s, tw_after.bety * 1e-3, label=r'$\beta_y$ (after)')
spbet.set_ylabel(r'$\beta_{x,y}$ [km]')
spbet.legend()

# Plot horizontal and vertical closed orbits (before and after)
spco.plot(tw_before.s, tw_before.x, label=r'$x$ (before)', linestyle='-')
spco.plot(tw_before.s, tw_before.y, label=r'$y$ (before)', linestyle='-')
spco.plot(tw_after.s, tw_after.x, label=r'$x$ (after)', linestyle='-')
spco.plot(tw_after.s, tw_after.y, label=r'$y$ (after)', linestyle='-')
spco.set_ylabel(r'(Closed orbit)$_{x,y}$ [m]')
spco.legend()

# Plot horizontal and vertical dispersions
spdisp.plot(tw_after.s, tw_after.dx, label=r'$D_x$ (after)')
spdisp.plot(tw_after.s, tw_after.dy, label=r'$D_y$ (after)')
spdisp.set_ylabel(r'$D_{x,y}$ [m]')
spdisp.set_xlabel('s [m]')
spdisp.legend()


# Set the overall figure title to include key optical parameters before and after tuning
fig1.suptitle(
    r'Before Tuning: $q_x$ = ' + f'{qx_before:.3f}, $q_y$ = ' + f'{qy_before:.3f}' + '\n' +
    r'After Tuning: $q_x$ = ' + f'{qx_after:.3f}, $q_y$ = ' + f'{qy_after:.3f}' + '\n' +
    r'$Q_x$: ' + f'{dqx_before:.3f} -> {dqx_after:.3f}; $Q_y$: ' + f'{dqy_before:.3f} -> {dqy_after:.3f}'
)

spbet.set_xlim(tw_after['s', 'ip5'] - 1000, tw_after['s', 'ip5'] + 1000)

# Adjust subplot spacing for clarity
fig1.subplots_adjust(left=.15, right=.92, hspace=.27)
plt.show()
