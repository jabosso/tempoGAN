#
# Simple flip with level set and basic resampling
# 
from manta import *
import argparse
from scenes_utils import SessionSaver

parser = argparse.ArgumentParser()
parser.add_argument("--ball-speed", type=float, default=1,
                    help="speed of the ball beign dropped in R+ (default: 1)")
parser.add_argument("--ball-radius", type=float, default=0.1,
                    help="radius of the ball beign dropped in [0,1] (default: 0.1)")
parser.add_argument("--save-parts", action="store_true", default=False,
                    help="Save uni parts when using the script (default: False)")
parser.add_argument("--pause-starting", action="store_true", default=False,
                    help="Put in pause before starting the execution (default: False)")
parser.add_argument("--res", type=int, default=64,
                    help="Resolution of demo cube (default: 64)")
parser.add_argument("--partic-rad", type=float, default=2.0,
                    help="Size of a particle in R+ (default: 2.0)")
args = parser.parse_args()

saver_paths = SessionSaver("saved_chair/")
GUI = True
# solver params
dim = 3
res = args.res
gs = vec3(res, res, res)
if (dim == 2):
    gs.z = 1
s = Solver(name='main', gridSize=gs, dim=dim)
s.timestep = 0.8
minParticles = pow(2, dim)

# save particles for separate surface generation pass? --> args.save_parts

# size of particles 
radiusFactor = args.partic_rad

# prepare grids and particles
flags = s.create(FlagGrid)
phi = s.create(LevelsetGrid)
phiObs = s.create(LevelsetGrid)

vel = s.create(MACGrid)
velOld = s.create(MACGrid)
pressure = s.create(RealGrid)
tmpVec3 = s.create(VecGrid)
tstGrid = s.create(RealGrid)

pp = s.create(BasicParticleSystem)
pVel = pp.create(PdataVec3)
# test real value, not necessary for simulation
pTest = pp.create(PdataReal)
mesh = s.create(Mesh)

# acceleration data for particle nbs
pindex = s.create(ParticleIndexSystem)
gpi = s.create(IntGrid)

# scene setup, 0=breaking dam, 1=drop into pool
setup = 1
bWidth = 1
flags.initDomain()  # boundaryWidth=bWidth)  # , phiWalls=phiObs)
# flags.fillGrid()
fluidVel = 0
fluidSetVel = 0

if setup == 0:
    # breaking dam
    fluidbox = Box(parent=s, p0=gs * vec3(0, 0, 0), p1=gs * vec3(0.4, 0.6, 1.0))  # breaking dam
    # fluidbox = Box( parent=s, p0=gs*vec3(0.4,0.72,0.4), p1=gs*vec3(0.6,0.92,0.6)) # centered falling block
    phi = fluidbox.computeLevelset()
elif setup == 1:
    # falling drop
    fluidBasin = Box(parent=s, p0=gs * vec3(0, 0, 0), p1=gs * vec3(1.0, 0.05, 1.0))  # basin
    dropCenter = vec3(0.68, 0.85, 0.25)
    dropRadius = args.ball_radius
    # fluidDrop = Sphere(parent=s, center=gs * dropCenter, radius=res * dropRadius)
    # fluidVel = Sphere(parent=s, center=gs * dropCenter, radius=res * (dropRadius + 0.05))
    w = args.ball_radius
    fluidDrop = Box(parent=s, p0=gs * vec3(0.50, 0.70, 0.18), p1=gs * vec3(0.80, 0.9, 0.4))
    fluidVel = Box(parent=s, p0=gs * vec3(0.50, 0.70, 0.18), p1=gs * vec3(0.80, 0.9, 0.4))
    fluidSetVel = vec3(0, -args.ball_speed, 0)
    phi = fluidBasin.computeLevelset()
    phi.join(fluidDrop.computeLevelset())
    obstacle_parts = []
    th = 0.05
    h = 0.2
    base = 0.7
    st_z = 0.1
    depth = .4
    st_th = .025
    obstacle_parts.append(Box(parent=s, p0=gs * vec3((0.4 + 0.9) / 2.0 - st_th, 0, (st_z + depth) / 2.0 - st_th),
                              p1=gs * vec3((0.4 + 0.9) / 2.0 + st_th, base - th, (st_z + depth) / 2.0 + st_th)))
    obstacle_parts.append(Box(parent=s, p0=gs * vec3(0.4, base - th, st_z), p1=gs * vec3(0.9, base, st_z + depth)))
    obstacle_parts.append(Box(parent=s, p0=gs * vec3(0.9 - th, base, st_z), p1=gs * vec3(0.9, base + h, st_z + depth)))
    obstacle_parts.append(Box(parent=s, p0=gs * vec3(0.4, base, st_z), p1=gs * vec3(0.4 + th, base + h, st_z + depth)))
    obstacle_parts.append(Box(parent=s, p0=gs * vec3(0.4, base, st_z), p1=gs * vec3(0.9, base + h, st_z + th)))

    # obstacle_parts.append(Box(parent=s, p0=gs * vec3(0.4, 0.2, 0.2), p1=gs * vec3(0.7, 0.4, 0.8)))
    # obstacle_parts.append(Box(parent=s, p0=gs * vec3(0.4, 0.2, 0.2), p1=gs * vec3(0.7, 0.4, 0.8)))
    for part in obstacle_parts:
        part.applyToGrid(grid=flags, value=FlagObstacle)

    # obstacle2 = Sphere(parent=s, center=gs * vec3(0.66, 0.3, 0.5), radius=res * 0.2
    # phiObs.join(obstacle2.computeLevelset())

    """
    flags.updateFromLevelset(phi)
    # also sets boundary flags for phiObs
    fractions = s.create(MACGrid)
    updateFractions(flags=flags, phiObs=phiObs, fractions=fractions, boundaryWidth=bWidth)
    setObstacleFlags(flags=flags, phiObs=phiObs, fractions=fractions)
    # phiObs.subtract(phiObs)"""

    # sdfgrad = obstacleGradient(flags)
    sdf = obstacleLevelset(flags)
    bgr = s.create(Mesh)
    sdf.createMesh(bgr)

    # obsbox = Box( parent=s, p0=gs*vec3(0.4,0.2,0), p1=gs*vec3(0.7,0.4,1))
    # obsbox = Box( parent=s, p0=gs*vec3(0.3,0.2,0), p1=gs*vec3(0.7,0.6,1))
    # phi.join( obsbox.computeLevelset() )
    flags.updateFromLevelset(phi)
    # setOpenBound(flags,bWidth,'xX',FlagOutflow|FlagEmpty)
    sampleLevelsetWithParticles(phi=phi, flags=flags, parts=pp, discretization=2, randomness=0.05)

    if fluidVel != 0:
        # set initial velocity
        fluidVel.applyToGrid(grid=vel, value=fluidSetVel)
    mapGridToPartsVec3(source=vel, parts=pp, target=pVel)

    # testing the real channel while resampling - original particles
    # will have a value of 0.1, new particle will get a value from the tstGrid
    testInitGridWithPos(tstGrid)
    pTest.setConst(0.1)

    # save reference any grid, to automatically determine grid size
    if args.save_parts:
        pressure.save('ref_flipParts_0000.uni')

    if 1 and (GUI):
        gui = Gui()
    gui.setBackgroundMesh(bgr)
    gui.show()
    if args.pause_starting:
        gui.pause()

    # main loop
    for t in range(400):
        mantaMsg('\nFrame %i, simulation time %f' % (s.frame, s.timeTotal))

        # FLIP
        pp.advectInGrid(flags=flags, vel=vel, integrationMode=IntRK4, deleteInObstacle=False)

        # make sure we have velocities throught liquid region
        mapPartsToMAC(vel=vel, flags=flags, velOld=velOld, parts=pp, partVel=pVel, weight=tmpVec3)
        extrapolateMACFromWeight(vel=vel, distance=2, weight=tmpVec3)  # note, tmpVec3 could be free'd now...
        markFluidCells(parts=pp, flags=flags)

        # create approximate surface level set, resample particles
        gridParticleIndex(parts=pp, flags=flags, indexSys=pindex, index=gpi)
        unionParticleLevelset(pp, pindex, flags, gpi, phi, radiusFactor)
        resetOutflow(flags=flags, parts=pp, index=gpi, indexSys=pindex)
        # extend levelset somewhat, needed by particle resampling in adjustNumber
        extrapolateLsSimple(phi=phi, distance=4, inside=True);

        # forces & pressure solve
        addGravity(flags=flags, vel=vel, gravity=(0, -0.001, 0))
        setWallBcs(flags=flags, vel=vel)
        solvePressure(flags=flags, vel=vel, pressure=pressure, phi=phi)
        setWallBcs(flags=flags, vel=vel)

        # set source grids for resampling, used in adjustNumber!
        pVel.setSource(vel, isMAC=True)
        pTest.setSource(tstGrid)
        adjustNumber(parts=pp, vel=vel, flags=flags, minParticles=1 * minParticles, maxParticles=2 * minParticles,
                     phi=phi,
                     radiusFactor=radiusFactor)

        # make sure we have proper velocities
        extrapolateMACSimple(flags=flags, vel=vel)

        flipVelocityUpdate(vel=vel, velOld=velOld, flags=flags, parts=pp, partVel=pVel, flipRatio=0.97)

        if (dim == 3):
            phi.createMesh(mesh)

        # s.printMemInfo()
        s.step()

        # generate data for flip03_gen.py surface generation scene
        if args.save_parts:
            pass#pp.save((saver_paths.getUniFolder() + 'flipParts_%04d.uni') % t)

        if args.save_parts and GUI:
            gui.screenshot((saver_paths.getScreenFolder() + 'flip_screen_02_%04d.png') % t)
