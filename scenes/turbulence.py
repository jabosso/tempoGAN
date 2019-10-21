# Turbulence modeling example
# (k-epsilon model)

from manta import *
import argparse

# unused: scale = 0.2

parser = argparse.ArgumentParser()
parser.add_argument("--speed-x", type=float, default=0.5,
                    help="speed on the X axis in R+ (default: 0.5)")
parser.add_argument("--speed-y", type=float, default=0.0,
                    help="speed on the Y axis in R+ (default: 0.0)")
parser.add_argument("--speed-z", type=float, default=0.0,
                    help="speed on the Z axis in R+ (default: 0.0)")
parser.add_argument("--show-pressure", action="store_true", default=False,
                    help="Save uni parts when using the script (default: False)")
parser.add_argument("--scene", type=int, default=0,
                    help="Select one of the scenes in N U [0,3] (default: 0)")
parser.add_argument("--turb-number", type=int, default=500,
                    help="Turbolence number in N+ (default: 500)")
parser.add_argument("--pause-starting", action="store_true", default=False,
                    help="Put in pause before starting the execution (default: False)")
parser.add_argument("--gui", action="store_false", default=True,
                    help="Remove gui visualization (default: True)")
parser.add_argument("--res", type=int, default=64,
                    help="Resolution of demo cube (default: 64)")
args = parser.parse_args()

# solver params
res = 64
gs = vec3(res, res / 2, res / 2)
s = Solver(name='main', gridSize=gs)
s.timestep = 0.5
timings = Timings()

velInflow = vec3(args.speed_x, args.speed_y, args.speed_z)

# prepare grids
flags = s.create(FlagGrid)
pressure = s.create(RealGrid, show=args.show_pressure)
vel = s.create(MACGrid)

k = s.create(RealGrid)
eps = s.create(RealGrid)
prod = s.create(RealGrid)
nuT = s.create(RealGrid)
strain = s.create(RealGrid)
vc = s.create(MACGrid)
temp = s.create(RealGrid)

# noise field
noise = s.create(NoiseField)
noise.timeAnim = 0

# turbulence particles
turb = s.create(TurbulenceParticleSystem, noise=noise)

flags.initDomain()
flags.fillGrid()

scene = args.scene
if scene == 0:
    # obstacle grid, 4 rocks on right, 4 rocks on left
    for i in range(4):
        for j in range(5):
            obs = Sphere(parent=s, center=gs * vec3(0.2, .02 + (i + 1) / 5.0, -.1 + (j + 1) / 5.0), radius=res * 0.035)
            obs.applyToGrid(grid=flags, value=FlagObstacle)
if scene == 1:
    # 4 rocks like stairs
    for i in range(4):
        obs = Sphere(parent=s, center=gs * vec3((i + 1) / 5.0, 0.5 + (i * 0.03), 0.5 + (i % 2 + 1) / 10.0),
                     radius=res * 0.04)
        obs.applyToGrid(grid=flags, value=FlagObstacle)
if scene == 2:
    # obstacle grid, 4 rocks on right, 4 rocks on left
    for i in range(4):
        for j in range(4):
            obs = Box(parent=s, center=gs * vec3(0.2, (i + 1) / 5.0, (j + 1) / 5.0),
                      size=vec3(0.2, 0.2, 0.2) * vec3(0.2, 0.4, 0.1))
            # Box(parent=s, center=gs * vec3(0.05, 0.43, 0.6), size=gs * vec3(0.02, 0.005, 0.07))
            obs.applyToGrid(grid=flags, value=FlagObstacle)
if scene == 3:
    # one big wal obstacle
    obs = Box(parent=s, center=gs * vec3(0.5, 0.5, 0.5), size=gs * vec3(0.08, 0.3, 0.3))
    # Box(parent=s, center=gs * vec3(0.05, 0.43, 0.6), size=gs * vec3(0.02, 0.005, 0.07))
    obs.applyToGrid(grid=flags, value=FlagObstacle)

sdfgrad = obstacleGradient(flags)
sdf = obstacleLevelset(flags)
bgr = s.create(Mesh)
sdf.createMesh(bgr)

# particle inflow
box = Box(parent=s, center=gs * vec3(0.05, 0.43, 0.6), size=gs * vec3(0.02, 0.005, 0.7))

L0 = 0.01
mult = 0.1
intensity = 0.1
nu = 0.1
prodMult = 2.5
enableDiffuse = True

if (args.gui):
    gui = Gui()
    gui.setBackgroundMesh(bgr)
    gui.show()
    if args.pause_starting:
        gui.pause()
    # sliderL0 = gui.addControl(Slider, text='turbulent lengthscale', val=L0, min=0.001, max=0.5)
    sliderMult = gui.addControl(Slider, text='turbulent mult', val=mult, min=0, max=1)
    sliderProd = gui.addControl(Slider, text='production mult', val=prodMult, min=0.1, max=5)
    checkDiff = gui.addControl(Checkbox, text='enable RANS', val=enableDiffuse)

KEpsilonBcs(flags=flags, k=k, eps=eps, intensity=intensity, nu=nu, fillArea=True)

# main loop
for t in range(10000):
    mantaMsg('\nFrame %i, simulation time %f' % (s.frame, s.timeTotal))
    if (args.gui):
        mult = sliderMult.get()
        # unused: K0 = sliderL0.get()
        enableDiffuse = checkDiff.get()
        prodMult = sliderProd.get()

    turb.seed(box, args.turb_number)
    turb.advectInGrid(flags=flags, vel=vel, integrationMode=IntRK4)
    turb.synthesize(flags=flags, octaves=1, k=k, switchLength=5, L0=L0, scale=mult, inflowBias=velInflow)
    turb.projectOutside(sdfgrad)
    turb.deleteInObstacle(flags)

    KEpsilonBcs(flags=flags, k=k, eps=eps, intensity=intensity, nu=nu, fillArea=False)
    advectSemiLagrange(flags=flags, vel=vel, grid=k, order=1)
    advectSemiLagrange(flags=flags, vel=vel, grid=eps, order=1)
    KEpsilonBcs(flags=flags, k=k, eps=eps, intensity=intensity, nu=nu, fillArea=False)
    KEpsilonComputeProduction(vel=vel, k=k, eps=eps, prod=prod, nuT=nuT, strain=strain, pscale=prodMult)
    KEpsilonSources(k=k, eps=eps, prod=prod)

    if enableDiffuse:
        KEpsilonGradientDiffusion(k=k, eps=eps, vel=vel, nuT=nuT, sigmaU=10.0)

    # base solver
    advectSemiLagrange(flags=flags, vel=vel, grid=vel, order=2)
    setWallBcs(flags=flags, vel=vel)
    setInflowBcs(vel=vel, dir='xXyYzZ', value=velInflow)
    solvePressure(flags=flags, vel=vel, pressure=pressure, cgMaxIterFac=0.5)
    setWallBcs(flags=flags, vel=vel)
    setInflowBcs(vel=vel, dir='xXyYzZ', value=velInflow)

    timings.display()
    s.step()
