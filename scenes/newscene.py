from manta import *
from scenes_utils import SessionSaver
import numpy as np
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--save-screen", action="store_true", default=False,
                    help="Save screenshots (default: False)")
parser.add_argument("--save-data", action="store_true", default=False,
                    help="Save uni parts when using the script (default: False)")
parser.add_argument("--show-gui", action="store_true", default=False,
                    help="Show gui (default: False)")
parser.add_argument("--number", type=int, default=1,
                    help="Number of env to run (default: 1)")
parser.add_argument("--res", type=int, default=64,
                    help="Resolution to run (default: 64)")
parser.add_argument("--frames", type=int, default=200,
                    help="Number of frames to run. Infinite=0 (default: 200)")
args = parser.parse_args()

saver_paths = SessionSaver("../tensorflow/2ddata_sim/newscene_sim_1000")
save_screen = args.save_screen
save_for_tempogan = args.save_data
use_gui = args.show_gui

dim = 3
res = args.res
gs = vec3(res, res, res)
# -------------- Create the solver for the scene ----------------------
s = Solver(name='main', gridSize=gs, dim=dim)
s.timestep = 1.0

minParticles = pow(2, int(dim / 2.0))
print(("Min particles: %i" % minParticles))
radiusFactor = 0.8

# how much to reduce target sim size
targetFac = 0.25
target_gs = vec3(targetFac * gs.x, targetFac * gs.y, targetFac * gs.z)
# if dim == 2:
#    target_gs.z = 1  # 2D

if save_for_tempogan:
    arR = np.zeros([int(gs.z), int(gs.y), int(gs.x), 1])
    arV = np.zeros([int(gs.z), int(gs.y), int(gs.x), 3])
    target_arR = np.zeros([int(target_gs.z), int(target_gs.y), int(target_gs.x), 1])
    target_arV = np.zeros([int(target_gs.z), int(target_gs.y), int(target_gs.x), 3])
    print("arR shape")
    print(arR.shape)
    print("arV shape")
    print(arV.shape)
    print("target_arR shape")
    print(target_arR.shape)
    print("target_arV shape")
    print(target_arV.shape)

flags = s.create(FlagGrid)
# ------------------------------------------------------------

# target grid
# ------------------------initialize my scene geometry-------------------
flags.initDomain()  # create an empty box
flags.fillGrid()
phi = s.create(LevelsetGrid)

vel = s.create(MACGrid)
velOld = s.create(MACGrid)
pressure = s.create(RealGrid)
# tmpVec3 = s.create(VecGrid)
tmpVec3 = s.create(Vec3Grid)
tstGrid = s.create(RealGrid)
density = s.create(RealGrid)

pp = s.create(BasicParticleSystem)
pVel = pp.create(PdataVec3)
pTest = pp.create(PdataReal)
mesh = s.create(Mesh)

pindex = s.create(ParticleIndexSystem)
gpi = s.create(IntGrid)

# Bigger grid: normal one
setupFactor = 3.0
mainDt = 0.5
gs_res = vec3(setupFactor * res, setupFactor * res, setupFactor * res)
sm = Solver(name='main', gridSize=gs, dim=dim)
sm.timestep = 1.0
dummy = s.create(MACGrid)
blurden = sm.create(RealGrid)
blurvel = sm.create(MACGrid)
vel_2 = s.create(MACGrid)
flags_2 = s.create(FlagGrid)
density_2 = s.create(RealGrid)
pressure_2 = s.create(RealGrid)
vorticity_2 = s.create(Vec3Grid)  # vorticity
norm_2 = s.create(RealGrid)

bWidth = 1 * setupFactor
flags.initDomain(boundaryWidth=bWidth)
flags.fillGrid()

bWidth = 1
# fluidVel = 0
flags.initDomain(boundaryWidth=bWidth)
# --------------------------------------------------------------------------
fluidDrop = Box(parent=s, p0=gs * vec3(0, 0.1, 0), p1=gs * vec3(0.35, 1, 1))

fluidVel = Box(parent=s, p0=gs * vec3(0.50, 0.70, 0.18), p1=gs * vec3(0.80, 0.9, 0.4))
fluidSetVel = vec3(0, -1, 0)

# --------------------------------------------------------------------------
fluidBasin = Box(parent=s, p0=gs * vec3(0, 0, 0), p1=gs * vec3(1.0, 0.1, 1.0))

phi = fluidBasin.computeLevelset()
# -----------------
phi.join(fluidDrop.computeLevelset())
# --------------------------------------------------------------------------
obstacle1 = Box(parent=s, p0=gs * vec3(0, 0, 0), p1=gs * vec3(0.4, 0.6, 1.0))
obstacle2 = Box(parent=s, p0=gs * vec3(0.35, 0, 0), p1=gs * vec3(0.4, 1, 0.4))
obstacle3 = Box(parent=s, p0=gs * vec3(0.35, 0, 0.6), p1=gs * vec3(0.4, 1, 1))
obstacle4 = Box(parent=s, p0=gs * vec3(0.35, 0.65, 0), p1=gs * vec3(0.4, 1, 1))
obstacle1.applyToGrid(grid=flags, value=FlagObstacle)
obstacle2.applyToGrid(grid=flags, value=FlagObstacle)
obstacle3.applyToGrid(grid=flags, value=FlagObstacle)
obstacle4.applyToGrid(grid=flags, value=FlagObstacle)

sdfgrad = obstacleGradient(flags)
sdf = obstacleLevelset(flags)
bgr = s.create(Mesh)
sdf.createMesh(bgr)
# ------------------

flags.updateFromLevelset(phi)

sampleLevelsetWithParticles(phi=phi, flags=flags, parts=pp, discretization=2, randomness=0.05)

fluidVel.applyToGrid(grid=vel, value=fluidSetVel)
mapGridToPartsVec3(source=vel, parts=pp, target=pVel)
testInitGridWithPos(tstGrid)
pTest.setConst(0.1)
phi2 = phi

# this is to show the window with simulation
if use_gui:
    gui = Gui()
    gui.setBackgroundMesh(bgr)
    gui.show()
    gui.pause()
# main loop
for t in range((args.frames * 2 + 1) if args.frames > 0 else sys.maxsize):  # 200, 200 + frames * 2):
    mantaMsg('\nFrame %i, simulation time %f' % (s.frame, s.timeTotal))

    pp.advectInGrid(flags=flags, vel=vel, integrationMode=IntRK4, deleteInObstacle=False)
    mapPartsToMAC(vel=vel, flags=flags, velOld=velOld, parts=pp, partVel=pVel, weight=tmpVec3)
    extrapolateMACFromWeight(vel=vel, distance=2, weight=tmpVec3)  # note, tmpVec3 could be free'd now...
    markFluidCells(parts=pp, flags=flags)

    extrapolateLsSimple(phi=phi, distance=4, inside=True)

    gridParticleIndex(parts=pp, flags=flags, indexSys=pindex, index=gpi)
    unionParticleLevelset(pp, pindex, flags, gpi, phi, radiusFactor)
    resetOutflow(flags=flags, parts=pp, index=gpi, indexSys=pindex)

    addGravity(flags=flags, vel=vel, gravity=(0, -0.001, 0))
    setWallBcs(flags=flags, vel=vel)
    solvePressure(flags=flags, vel=vel, pressure=pressure, phi=phi)
    setWallBcs(flags=flags, vel=vel)
    pVel.setSource(vel, isMAC=True)
    pTest.setSource(tstGrid)
    adjustNumber(parts=pp, vel=vel, flags=flags, minParticles=1 * minParticles, maxParticles=2 * minParticles,
                 phi=phi,
                 radiusFactor=radiusFactor)
    extrapolateMACSimple(flags=flags, vel=vel)

    flipVelocityUpdate(vel=vel, velOld=velOld, flags=flags, parts=pp, partVel=pVel, flipRatio=0.97)
    if (dim == 3):
        phi.createMesh(mesh)

    # copy to target
    if save_for_tempogan:
        blurSig = float(1. / targetFac) / 3.544908  # 3.544908 = 2 * sqrt( PI )
        blurRealGrid(density, blurden, blurSig)
        interpolateGrid(target=density_2, source=blurden)

        blurMacGrid(vel, blurvel, blurSig)
        interpolateMACGrid(target=vel_2, source=blurvel)
        vel_2.multConst(vec3(targetFac))

    # if 0 and save_screen:
    #    pp.save(saver_paths.getUniFolder() + ('density_low_%04d.ppm' % t))

    if save_screen and use_gui:
        gui.screenshot(saver_paths.getScreenFolder() + ('newscene_screen_%04d.png' % t))

    # Questo è il codice per salvare preso dagli altri progetti
    if save_for_tempogan and t % 2 == 0:
        simPath = saver_paths.getUniFolder()
        # Taken from sim_3006
        frameNr = t / 2
        framedir = "frame_%04d" % frameNr
        # os.mkdir( outputpath + framedir )
        outputpath = simPath
        computeVorticity(vel=vel, vorticity=tmpVec3, norm=tstGrid)  # vorticity
        tmpVec3.save('%s/vorticity_low_%04d.uni' % (outputpath, frameNr))
        vel.save("%s/velocity_low_%04d.uni" % (outputpath, frameNr))
        density.save("%s/density_low_%04d.uni" % (outputpath, frameNr))
        density_2.save("%s/density_high_%04d.uni" % (outputpath, frameNr))

    s.step()
