#
# Very simple apic without level set
# and without any particle resampling
#
from manta import *
import argparse
from scenes_utils import SessionSaver

parser = argparse.ArgumentParser()
parser.add_argument("--box-altitude-top", type=float, default=0.72,
                    help="Height of the box in [0,1] (default: 0.72)")
parser.add_argument("--box-width", type=float, default=0.3,
                    help="Dimestion of the box [0,1] (default: 0.3)")
parser.add_argument("--box-height", type=float, default=0.2,
                    help="Dimestion of the box [0,1] (default: 0.2)")
parser.add_argument("--gravity-x", type=float, default=0.0,
                    help="Gravity on the X axis in R+ (default: 0.0)")
parser.add_argument("--gravity-y", type=float, default=0.002,
                    help="Gravity on the Z axis in R+. real gravity is negative (default: 0.002)")
parser.add_argument("--gravity-z", type=float, default=0.0,
                    help="Gravity on the X axis in R+ (default: 0.0)")
parser.add_argument("--particle-number", type=int, default=6,
                    help="Particles number in N+ (default: 6)")
parser.add_argument("--pause-starting", action="store_true", default=False,
                    help="Put in pause before starting the execution (default: False)")
parser.add_argument("--gui", action="store_false", default=True,
                    help="Remove gui visualization (default: True)")
parser.add_argument("--res", type=int, default=64,
                    help="Resolution of demo cube (default: 64)")
parser.add_argument("--save-parts", action="store_true", default=False,
                    help="Save uni parts when using the script (default: False)")
parser.add_argument("--save-each", type=int, default=1,
                    help="Numbers of frame to skip before saving in N+ / {0} (default: 1)")
args = parser.parse_args()

saver_paths = SessionSaver("apic01_simple")

# solver params
dim = 2
particleNumber = args.particle_number  # remember to use more particles in 2d, it can support it
res = args.res
gs = vec3(res, res, res)

if (dim == 2):
    gs.z = 1

s = Solver(name='main', gridSize=gs, dim=dim)
s.timestep = 0.5

# prepare grids and particles
flags = s.create(FlagGrid)
vel = s.create(MACGrid)
velOld = s.create(MACGrid)
pressure = s.create(RealGrid)
tmpVec3 = s.create(VecGrid)
pp = s.create(BasicParticleSystem)
# add velocity data to particles
pVel = pp.create(PdataVec3)
# apic part
mass = s.create(MACGrid)
pCx = pp.create(PdataVec3)
pCy = pp.create(PdataVec3)
pCz = pp.create(PdataVec3)

# scene setup
flags.initDomain(boundaryWidth=0)
# enable one of the following
w = args.box_width
h = args.box_height
# fluidbox = Box(parent=s, p0=gs * vec3(0, 0, 0), p1=gs * vec3(0.4, 0.6, 1))  # breaking dam
fluidbox = Box(parent=s, p0=gs * vec3(.5 - w / 2.0, args.box_altitude_top - h, .5 - w / 2.0),
               p1=gs * vec3(.5 + w / 2.0, args.box_altitude_top, .5 + w / 2.0))  # centered falling block
phiInit = fluidbox.computeLevelset()
flags.updateFromLevelset(phiInit)
# phiInit is not needed from now on!

# note, there's no resamplig here, so we need _LOTS_ of particles...
sampleFlagsWithParticles(flags=flags, parts=pp, discretization=particleNumber, randomness=0.2)


if (args.gui):
    gui = Gui()
    gui.show()
    if args.pause_starting:
        gui.pause()

# main loop
for t in range(2500):
    mantaMsg('\nFrame %i, simulation time %f' % (s.frame, s.timeTotal))

    # APIC
    pp.advectInGrid(flags=flags, vel=vel, integrationMode=IntRK4, deleteInObstacle=False)
    apicMapPartsToMAC(flags=flags, vel=vel, parts=pp, partVel=pVel, cpx=pCx, cpy=pCy, cpz=pCz, mass=mass)
    extrapolateMACFromWeight(vel=vel, distance=2, weight=tmpVec3)
    markFluidCells(parts=pp, flags=flags)

    addGravity(flags=flags, vel=vel, gravity=(args.gravity_x, -args.gravity_y, args.gravity_z))

    # pressure solve
    setWallBcs(flags=flags, vel=vel)
    solvePressure(flags=flags, vel=vel, pressure=pressure)
    setWallBcs(flags=flags, vel=vel)

    # we dont have any levelset, ie no extrapolation, so make sure the velocities are valid
    extrapolateMACSimple(flags=flags, vel=vel)

    # APIC velocity update
    apicMapMACGridToParts(partVel=pVel, cpx=pCx, cpy=pCy, cpz=pCz, parts=pp, vel=vel, flags=flags)

    # generate data for flip03_gen.py surface generation scene
    if args.save_parts and t % args.save_each == 0:
        pp.save(saver_paths.getUniFolder() + ('apicscreen_%04d.uni' % t))

    if args.save_parts and t % args.save_each == 0 and args.gui:
        gui.screenshot(saver_paths.getScreenFolder() + ('apic01_%04d.png' % t))
    s.step()
