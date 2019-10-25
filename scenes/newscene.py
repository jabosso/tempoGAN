from manta import *
dim = 3
res = 64
gs =vec3(res, res, res)
s = Solver(name='main', gridSize=gs, dim= dim)
s.timestep = 1.0


flags = s.create(FlagGrid)
#vel = s.create(MACGrid)
#density = s.create(RealGrid)
#pressure = s.create(RealGrid)

#initialize my scene geometry
flags.initDomain() #create an empty box
flags.fillGrid()
phi = s.create(LevelsetGrid)

pp = s.create(BasicParticleSystem)
mesh = s.create(Mesh)

bWidth = 1
flags.initDomain(boundaryWidth=bWidth)

fluidBasin = Box(parent=s, p0=gs * vec3(0, 0, 0), p1=gs * vec3(1.0, 0.1, 1.0))
phi = fluidBasin.computeLevelset()

flags.updateFromLevelset(phi)

sampleLevelsetWithParticles(phi=phi, flags=flags, parts=pp, discretization=2, randomness=0.05)
#this is to show the window with simulation
if 1 and (GUI):
    gui = Gui()
    gui.show()
    
#main loop
for t in range(250):
    mantaMsg('\nFrame %i, simulation time %f' % (s.frame, s.timeTotal))
    
    markFluidCells(parts=pp, flags=flags)
    #pp.advectInGrid(flags=flags, vel=vel, integrationMode=IntRK4, deleteInObstacle=False)    
    #advectSemiLagrange(flags=flags, vel=vel, grid=density, order=2)
    #advectSemiLagrange(flags=flags, vel=vel, grid=vel, order=2)
    #setWallBcs(flags=flags, vel=vel)
    #addBuoyancy(density=density, vel=vel, gravity=vec3(0,-6e-4,0), flags=flags)
    #solvePressure(flags=flags, vel=vel, pressure=pressure)
    #setWallBcs(flags=flags, vel=vel)
    
    if (dim == 3):
        phi.createMesh(mesh)

    s.step()