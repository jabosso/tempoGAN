from manta import *
dim = 3
res = 64
gs =vec3(res*2, res, res)
#-------------- Create the solver for the scene ----------------------
s = Solver(name='main', gridSize=gs, dim= dim)
s.timestep = 1.0

minParticles = pow(2, dim)
radiusFactor = 0.8

flags = s.create(FlagGrid)
#------------------------------------------------------------

#------------------------initialize my scene geometry-------------------
flags.initDomain() #create an empty box
flags.fillGrid()
phi = s.create(LevelsetGrid)

vel = s.create(MACGrid)
velOld = s.create(MACGrid)
pressure = s.create(RealGrid)
tmpVec3 = s.create(VecGrid)
tstGrid = s.create(RealGrid)
density = s.create(RealGrid)

pp = s.create(BasicParticleSystem)
pVel = pp.create(PdataVec3)
pTest = pp.create(PdataReal)
mesh = s.create(Mesh)

pindex = s.create(ParticleIndexSystem)
gpi = s.create(IntGrid)

bWidth = 1
#fluidVel = 0
flags.initDomain(boundaryWidth=bWidth)
#--------------------------------------------------------------------------
fluidDrop = Box(parent=s, p0=gs * vec3(0, 0.1, 0), p1=gs * vec3(0.35,1, 1))

fluidVel = Box(parent=s, p0=gs * vec3(0.50, 0.70, 0.18), p1=gs * vec3(0.80, 0.9, 0.4))
fluidSetVel = vec3(0, -1, 0)


#--------------------------------------------------------------------------
fluidBasin = Box(parent=s, p0=gs * vec3(0, 0, 0), p1=gs * vec3(1.0, 0.1, 1.0))

phi = fluidBasin.computeLevelset()
#-----------------
phi.join(fluidDrop.computeLevelset())
#--------------------------------------------------------------------------
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
#------------------

flags.updateFromLevelset(phi)

sampleLevelsetWithParticles(phi=phi, flags=flags, parts=pp, discretization=2, randomness=0.05)

fluidVel.applyToGrid(grid=vel, value=fluidSetVel)
mapGridToPartsVec3(source=vel, parts=pp, target=pVel)
testInitGridWithPos(tstGrid)
pTest.setConst(0.1)
phi2 = phi

#this is to show the window with simulation
if 1 and (GUI):
    gui = Gui()
gui.setBackgroundMesh(bgr)
gui.show()
gui.pause()    
#main loop
for t in range(2050):
    mantaMsg('\nFrame %i, simulation time %f' % (s.frame, s.timeTotal))
    
      
    pp.advectInGrid(flags=flags, vel=vel, integrationMode=IntRK4, deleteInObstacle=False)    
    mapPartsToMAC(vel=vel, flags=flags, velOld=velOld, parts=pp, partVel=pVel, weight=tmpVec3)
    extrapolateMACFromWeight(vel=vel, distance=2, weight=tmpVec3)  # note, tmpVec3 could be free'd now...
    markFluidCells(parts=pp, flags=flags)

    extrapolateLsSimple(phi=phi, distance=4, inside=True);

    gridParticleIndex(parts=pp, flags=flags, indexSys=pindex, index=gpi)
    unionParticleLevelset(pp, pindex, flags, gpi, phi, radiusFactor)
    resetOutflow(flags=flags, parts=pp, index=gpi, indexSys=pindex)

    addGravity(flags=flags, vel=vel, gravity=(0, -0.001, 0))
    setWallBcs(flags=flags, vel=vel)
    solvePressure(flags=flags, vel=vel, pressure=pressure, phi=phi)
    setWallBcs(flags=flags, vel=vel)
    pVel.setSource(vel, isMAC=True)
    pTest.setSource(tstGrid);
    adjustNumber(parts=pp, vel=vel, flags=flags, minParticles=1 * minParticles, maxParticles=2 * minParticles,
                phi=phi,
                radiusFactor=radiusFactor)
    extrapolateMACSimple(flags=flags, vel=vel)

    flipVelocityUpdate(vel=vel, velOld=velOld, flags=flags, parts=pp, partVel=pVel, flipRatio=0.97)
    if (dim == 3):
        phi.createMesh(mesh)

    s.step()