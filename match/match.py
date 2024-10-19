
#? Import the usual
import xtrack as xt
import matplotlib.pyplot as plt
import numpy as np

def matchplot(tw_before, tw_after, center):
    # Inspect fundamental parameters before tuning
    qx_before = tw_before.qx  # Horizontal tune before
    qy_before = tw_before.qy  # Vertical tune before
    dqx_before = tw_before.dqx  # Horizontal chromaticity before
    dqy_before = tw_before.dqy  # Vertical chromaticity before

    # Inspect fundamental parameters after tuning
    qx_after = tw_after.qx  # Horizontal tune after
    qy_after = tw_after.qy  # Vertical tune after
    dqx_after = tw_after.dqx  # Horizontal chromaticity after
    dqy_after = tw_after.dqy  # Vertical chromaticity after

    #? Create plots for closed orbit, beta functions and dispersion
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

    spbet.set_xlim(center - 1000, center + 1000)

    # Adjust subplot spacing for clarity
    fig1.subplots_adjust(left=.15, right=.92, hspace=.27)
    plt.show()

#? Load a line and build a tracker
line = xt.Line.from_json('match_line.json')
line.build_tracker()

# Initial twiss before tuning
tw_before = line.twiss(method='4d')

#? Match tunes and chromaticities to assigned values
opt = line.match(
    # Matching method used; in this case, a 4-dimensional optimization
    method='4d',  
    vary=[
        # Quadrupole strengths to be varied with steps 1e-8
        xt.VaryList(['kqtf.b1', 'kqtd.b1'], step=1e-8, tag='quad'),
        # Sextupole strengths to be varied with steps 1e-4 within [-0.1, 0.1] 
        xt.VaryList(['ksf.b1', 'ksd.b1'], step=1e-4, limits=[-0.1, 0.1], tag='sext'),  
    ],
    targets=[
        # Target tunes with a tolerance of 1e-6
        xt.TargetSet(qx=62.315, qy=60.325, tol=1e-6, tag='tune'), 
        # Target chromaticities with a tolerance of 0.01 
        xt.TargetSet(dqx=10.0, dqy=12.0, tol=0.01, tag='chrom'),  
    ])

print("How did the match change the knobs?")
# Get knobs values before optimization
knobs_before_match = opt.get_knob_values(iteration=0)
print(knobs_before_match)
# contains: {'kqtf.b1': 0, 'kqtd.b1': 0, 'ksf.b1': 0, 'ksd.b1': 0}

# Get knobs values after optimization
knobs_after_match = opt.get_knob_values()
print(knobs_after_match)
# contains: {'kqtf.b1': 4.27163e-05,  'kqtd.b1': -4.27199e-05,
#            'ksf.b1': 0.0118965, 'ksd.b1': -0.0232137}

# Final twiss after tuning
tw_after = line.twiss(method='4d')

# Make the plot
matchplot(tw_before, tw_after, tw_after['s', 'ip5'])

#? Match a specific position
#? OR with a line.twiss() -> see the README
opt = line.match(
    start='mq.30l8.b1', end='mq.23l8.b1',
    init_at=xt.START, betx=1, bety=1, y=0, py=0, # <-- conditions at start
    vary=xt.VaryList(['acbv30.l8b1', 'acbv28.l8b1', 'acbv26.l8b1', 'acbv24.l8b1'],
                    step=1e-10, limits=[-1e-3, 1e-3]),
    targets = [
        xt.TargetSet(y=3e-3, py=0, at='mb.b28l8.b1'),
        xt.TargetSet(y=0, py=0, at=xt.END)
    ])

opt.tag(tag='matched')
opt.reload(0)
tw_before = line.twiss(method='4d')
opt.reload(tag='matched')
tw = line.twiss(method='4d')

plt.close('all')
fig = plt.figure(1, figsize=(6.4*1.2, 4.8*0.8))
ax = fig.add_subplot(111)
ax.plot(tw.s, tw.y*1000, label='y')

for nn in ['mcbv.30l8.b1', 'mcbv.28l8.b1', 'mcbv.26l8.b1', 'mcbv.24l8.b1']:
    ax.axvline(x=line.get_s_position(nn), color='k', linestyle='--', alpha=0.5)
    ax.text(line.get_s_position(nn), 10, nn, rotation=90,
            horizontalalignment='left', verticalalignment='top')

ax.axvline(x=line.get_s_position('mb.b28l8.b1'), color='r', linestyle='--', alpha=0.5)
ax.text(line.get_s_position('mb.b28l8.b1'), 10, 'mb.b28l8.b1', rotation=90,
        horizontalalignment='left', verticalalignment='top')

ax.axvline(x=line.get_s_position('mq.30l8.b1'), color='g', linestyle='--', alpha=0.5)
ax.axvline(x=line.get_s_position('mq.23l8.b1'), color='g', linestyle='--', alpha=0.5)
ax.text(line.get_s_position('mq.30l8.b1'), 10, 'mq.30l8.b1', rotation=90,
        horizontalalignment='right', verticalalignment='top')
ax.text(line.get_s_position('mq.23l8.b1'), 10, 'mq.23l8.b1', rotation=90,
        horizontalalignment='right', verticalalignment='top')

ax.set_xlim(line.get_s_position('mq.30l8.b1') - 10,
            line.get_s_position('mq.23l8.b1') + 10)
ax.set_xlabel('s [m]')
ax.set_ylabel('y [mm]')
ax.set_ylim(-0.5, 10)
plt.subplots_adjust(bottom=.152, top=.9, left=.1, right=.95)
plt.show()

assert np.isclose(tw['y', 'mb.b28l8.b1'], 3e-3, atol=1e-4)
assert np.isclose(tw['py', 'mb.b28l8.b1'], 0, atol=1e-6)
assert np.isclose(tw['y', 'mq.23l8.b1'], tw_before['y', 'mq.23l8.b1'], atol=1e-6)
assert np.isclose(tw['py', 'mq.23l8.b1'], tw_before['py', 'mq.23l8.b1'], atol=1e-7)
assert np.isclose(tw['y', 'mq.33l8.b1'], tw_before['y', 'mq.33l8.b1'], atol=1e-6)
assert np.isclose(tw['py', 'mq.33l8.b1'], tw_before['py', 'mq.33l8.b1'], atol=1e-7)

