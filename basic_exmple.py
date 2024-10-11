
#? Import the usual stuff
import numpy as np
import matplotlib.pyplot as plt

#? Import xobjects and xtrack
import xobjects as xo
import xtrack as xt

"""
The first step to perform a tracking simulation consists in creating or importing the lattice
It can be created from a list of elements, like in this example
Even after creation you can change the values like : line['quad_0'].knl[1] = 2.
It is also possible to import a lattice from a MAD-X file (Other example)
"""
#? Generate a simple line
line = xt.Line(
    elements=[xt.Drift(length=2.),
              xt.Multipole(knl=[0, 0.5], ksl=[0,0]),
              xt.Drift(length=1.),
              xt.Multipole(knl=[0, -0.5], ksl=[0,0])],
    element_names=['drift_0', 'quad_0', 'drift_1', 'quad_1'])

#? Attach a reference particle to the line (optional)
line.particle_ref = xt.Particles(p0c=6500e9, #eV
                                 q0=1, mass0=xt.PROTON_MASS_EV)

#? Choose a context
context = xo.ContextCpu()         # For CPU
# context = xo.ContextCupy()      # For CUDA GPUs
# context = xo.ContextPyopencl()  # For OpenCL GPUs

"""
An Xtrack tracker object needs to be associated to the line in order to track 
particles on the chosen computing platform (defined by the context)
This transfers the machine model to the required platform and compiles the required tracking code
"""
#? Transfer lattice on context and compile tracking code
line.build_tracker(_context=context)

#? Compute the Twiss parameters of the lattice
tw = line.twiss(method='4d')
tw.cols['s betx bety'].show()
# prints:
#
# name       s    betx    bety
# drift_0    0 3.02372 6.04743
# quad_0     2 6.04743 3.02372
# drift_1    2 6.04743 3.02372
# quad_1     3 3.02372 6.04743
# _end_point 3 3.02372 6.04743

"""
The particles to be tracked can be allocated on the chosen platform using the build_particles
The coordinates of the particle object are accessible with: particles.x[20]
Reference mass, charge, energy are taken from the reference particle.
"""
#? Build particle object on context
n_part = 200
particles = line.build_particles(
                        x=np.random.uniform(-1e-3, 1e-3, n_part),
                        px=np.random.uniform(-1e-5, 1e-5, n_part),
                        y=np.random.uniform(-2e-3, 2e-3, n_part),
                        py=np.random.uniform(-3e-5, 3e-5, n_part),
                        zeta=np.random.uniform(-1e-2, 1e-2, n_part),
                        delta=np.random.uniform(-1e-4, 1e-4, n_part))

"""
The line object can now be used to track the generated particles 
this can be done over the specified lattice for an arbitrary number of turns
Optionally the particles coordinates can be saved at each turn: turn_by_turn_monitor=True
"""
#? Track the particles
n_turns = 100
line.track(particles, num_turns=n_turns,
              turn_by_turn_monitor=True)

"""
Let's make a (x,px) plot to keep track after each turn
If everything works fine we expect an ellipse
"""
#? Access the turn-by-turn monitoring data
monitor = line.record_last_track

#? Select a specific particle to visualize and extract the data
particle_id = 0
x_data = monitor.x[particle_id]
px_data = monitor.px[particle_id]
turns = np.arange(len(x_data))

#? Create scatter plot with a color gradient based on the turn number
plt.figure(figsize=(10, 6))
sc = plt.scatter(x_data, px_data, c=turns, cmap='viridis', marker='o')
plt.colorbar(sc, label='Turn number')
plt.xlabel('x [m]')
plt.ylabel('px [rad]')
plt.title(f'Phase Space Evolution of Particle {particle_id} (x, px)')
plt.grid(True)
plt.show()