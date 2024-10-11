# X-Suite starter pack
As described on [x-suite website](https://xsuite.readthedocs.io/en/latest/):
*Xsuite is a collection python packages for the simulation of the beam dynamics in particle accelerators.*

This repo is a collection of examples (mostly copied from the x-suite documentation) developed to practice with this new tool. 

## Table of content
- [Install X-Suite or get a Docker](#install-x-suite) 
- [First working example](#first-working-example)
- [Describe a Line](#describe-a-line)

## Install X-Suite
X-Suite can be easily installed via `pip` but in case you prefer I have a dockerfile you can use.

For more information on Docker usage with Xsuite, visit [this Docker repository](https://github.com/b-vitali/Dockers).

This docker has some minimal tweeking to have a functioning jupyter notebook and other small things.
Most of the requirements for additional tools (MAD-X, Sixtracktools, PyHEADTAIL, ...) are already installed.

## First working example
Let's dive right in. The `basic_example.py` has the minimal functioning parts for a simple simulation
This code simulates the tracking of particles through a simple lattice using the x-suite library (Xtrack, Xobjects).
The purpose is to visualize the evolution in phase space (\( x, px \)) of a particle over multiple turns.

### Code Overview
The code is hevely commented so here I will just outline the steps, which are similar in every simulation
- Generate a *Line*
- Attach a reference particle
- Define on what the simulation will be running (CPU/GPU)
- Compute the *Twiss parameters*
- Simulate the particles for N turns
- Collect and plot the results

### Results
Collecting the tracking information at every turn we can follow the evolution in (\( x, px \))
![Phase Space Evolution](basic_example.png)

## Describe a Line
