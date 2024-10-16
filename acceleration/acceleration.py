import numpy as np
from cpymad.madx import Madx
import xtrack as xt
import matplotlib.pyplot as plt

# Import a line and build a tracker
line = xt.Line.from_json('acceleration_line.json')

# Set the initial kinetic energy (in eV)
e_kin_start_eV = 160e6

# Define reference particle parameters: mass, charge, and total energy
line.particle_ref = xt.Particles(
    mass0=xt.PROTON_MASS_EV,                    # Proton mass in eV
    q0=1.,                                      # Charge state (1 for a proton)
    energy0=xt.PROTON_MASS_EV + e_kin_start_eV  # Total energy (rest mass + kinetic energy)
)

# Build the tracker to simulate the particle dynamics along the line
line.build_tracker()

# User-defined energy ramp: time values [s] and corresponding kinetic energies [GeV]
t_s = np.array([0., 0.0006, 0.0008, 0.001 , 0.0012, 0.0014, 0.0016, 0.0018,
                0.002 , 0.0022, 0.0024, 0.0026, 0.0028, 0.003, 0.01])

E_kin_GeV = np.array([0.16000000,0.16000000,
    0.16000437, 0.16001673, 0.16003748, 0.16006596, 0.16010243, 0.16014637,
    0.16019791, 0.16025666, 0.16032262, 0.16039552, 0.16047524, 0.16056165,
    0.163586])

# Attach the energy program to the line to define how the kinetic energy evolves over time
line.energy_program = xt.EnergyProgram(
    t_s=t_s,                            # Array of time points [s]
    kinetic_energy0=E_kin_GeV * 1e9     # Corresponding kinetic energies [eV]
)

# Plot energy and revolution frequency vs. time
t_plot = np.linspace(0, 10e-3, 20)                                  # Time points for plotting [s]
E_kin_plot = line.energy_program.get_kinetic_energy0_at_t_s(t_plot) # Get kinetic energy values
f_rev_plot = line.energy_program.get_frev_at_t_s(t_plot)            # Get revolution frequency values

plt.close('all')
plt.figure(1, figsize=(6.4 * 1.5, 4.8))
ax1 = plt.subplot(2, 2, 1)
plt.plot(t_plot * 1e3, E_kin_plot * 1e-6)   # Convert time to ms and energy to MeV for plotting
plt.ylabel(r'$E_{kin}$ [MeV]')              # Kinetic energy label
ax2 = plt.subplot(2, 2, 3, sharex=ax1)
plt.plot(t_plot * 1e3, f_rev_plot * 1e-3)   # Convert frequency to kHz for plotting
plt.ylabel(r'$f_{rev}$ [kHz]')              # Revolution frequency label
plt.xlabel('t [ms]')                        # Time label in milliseconds

# Setup the RF cavity frequency to stay on the second harmonic of the revolution frequency
t_rf = np.linspace(0, 3e-3, 100)                    # Time samples for the frequency program (in seconds)
f_rev = line.energy_program.get_frev_at_t_s(t_rf)   # Get revolution frequency for each time sample
h_rf = 2                                            # Harmonic number
f_rf = h_rf * f_rev                                 # Calculate RF frequency as harmonic number times revolution frequency

# Build a piecewise linear function using the time and frequency samples and link it to the RF cavity
line.functions['fun_f_rf'] = xt.FunctionPieceWiseLinear(x=t_rf, y=f_rf)
line.element_refs['br.c02'].frequency = line.functions['fun_f_rf'](
                                                        line.vars['t_turn_s']) # Assign the RF frequency function

# Setup the voltage and phase lag of the RF cavity
line.element_refs['br.c02'].voltage = 3000  # Set the RF cavity voltage [V]
line.element_refs['br.c02'].lag = 0         # Set the phase lag (in degrees, below transition energy)

# When setting the line variable 't_turn_s', the reference energy and the RF frequency are updated automatically
line.vars['t_turn_s'] = 0
line.particle_ref.kinetic_energy0   # Kinetic energy should be 160.00000 MeV
line['br.c02'].frequency            # RF frequency should be 1983931.935 Hz

line.vars['t_turn_s'] = 3e-3
line.particle_ref.kinetic_energy0   # Kinetic energy updates to 160.56165 MeV
line['br.c02'].frequency            # RF frequency updates to 1986669.0559674294 Hz

# Reset to zero for tracking (prepare initial state)
line.vars['t_turn_s'] = 0

# Track a few particles to visualize the longitudinal phase space
p_test = line.build_particles(x_norm=0, zeta=np.linspace(0, line.get_length(), 101))

# Enable time-dependent variables (automatically update variables like 't_turn_s' at each turn)
line.enable_time_dependent_vars = True

# Track particles for 9000 turns and record data, with progress tracking enabled
line.track(p_test, num_turns=9000, turn_by_turn_monitor=True, with_progress=True)
mon = line.record_last_track

# Plot the longitudinal phase space for the last 2000 turns
plt.subplot2grid((2, 2), (0, 1), rowspan=2)
plt.plot(mon.zeta[:, -2000:].T, mon.delta[:, -2000:].T, color='C0')
plt.xlabel(r'$\zeta$ [m]')                              # Longitudinal position label
plt.ylabel('$\delta$')                                  # Relative momentum deviation label
plt.xlim(-40, 30)                                       # Set limits for the zeta axis
plt.ylim(-0.0025, 0.0025)                               # Set limits for the delta axis
plt.title('Last 2000 turns')
plt.subplots_adjust(left=0.08, right=0.95, wspace=0.26) # Adjust subplot spacing
plt.show()


line.survey().plot()
plt.show()  