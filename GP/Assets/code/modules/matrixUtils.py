import numpy as np
import math



### given an OP, it looks for a parent, if it finds one it returns the coordinate
### of the parent after xforms.
def mat_invParent(myOp):
	
	# get reference to the parent component.
	if(len(myOp.inputCOMPs) > 0):
		myOpParent = myOp.inputCOMPs[0]
	else:
		myOpParent = op.geoHolder
		
	# get the parent matrix then translates.
	parent_worldMat = myOpParent.worldTransform
	s, r, t = parent_worldMat.decompose()
	tx,ty,tz = t
	
	# invert the child matrix
	my_worldMat = myOp.worldTransform
	my_worldMat.invert()
	
	# multiply the inverse world matrix by the parent position.
	newPos = my_worldMat * tdu.Position(tx,ty,tz)
	
	returnStr = "%f,%f,%f"%(newPos[0],newPos[1],newPos[2])
	
	return returnStr
	


### given an OP and the soon to be parent, calculate the new xform for the OP 
###  based on the difference in parent matricies.
def neutralize_Parent_Transform(myOp, target):
	
	target = op(target)
	
	# get reference to the parent component.
	if(len(myOp.inputCOMPs) > 0):
		myOpParent = myOp.inputCOMPs[0]
	else:
		myOpParent = op.geoHolder
		
	# get the parent matrix then translates.
	parent_worldMat = myOpParent.worldTransform
	# s, r, t = parent_worldMat.decompose()
	# tx1,ty1,tz1 = t
	
	# get the target matrix then translates.
	target_worldMat = target.worldTransform
	target_worldMat.invert()
	# s, r, t = target_worldMat.decompose()
	# tx2,ty2,tz2 = t
	
	OffsetMat = target_worldMat * parent_worldMat * myOp.localTransform
	s, r, t = OffsetMat.decompose()
	tx3,ty3,tz3 = t
	
	newPos = [t[0],t[1],t[2],r[0],r[1],r[2],s[0],s[1],s[2]]
	
	return newPos


def Calculate_Difference_Matrix(target, parentToBe):
	'''	
	slightly less messy version of neutralize_Parent_Transform() above. Also uses a newer function
	of geo comps the relativeTransform() which is quite handy.
	'''
	# get reference to the current parent component.
	if(len(target.inputCOMPs) > 0):
		currentParent = target.inputCOMPs[0]
	else:
		currentParent = op.geoHolder

	m = parentToBe.relativeTransform(currentParent)
	m *= target.localTransform
	s, r, t = m.decompose()

	return [t[0],t[1],t[2],r[0],r[1],r[2],s[0],s[1],s[2]]
	
	
	
### coordinates that are in local space point, convert to world space 
def LocalSpace_to_WorldSpace(myOp, tx, ty ,tz):

	# get reference to the parent component.
	if(len(myOp.inputCOMPs) > 0):
		myOpParent = myOp.inputCOMPs[0]
	else:
		myOpParent = op.geoHolder
	op_WorldMat = myOp.worldTransform
	# op_WorldMat.invert()
	
	# mult new position against world mat to get corrected coordinate.
	newPos = op_WorldMat * tdu.Position(tx, ty, tz)
	return newPos
	
	
### given a render picked world space point, and a object that needs to receive 
### coordinates that are in local space but appear to be where the world space
### click was, use this to transform a coordinate.
def worldSpace_to_LocalSpace(myOp, tx, ty ,tz):

	# get reference to the parent component.
	if(len(myOp.inputCOMPs) > 0):
		myOpParent = myOp.inputCOMPs[0]
	else:
		myOpParent = op.geoHolder
	op_WorldMat = myOp.worldTransform
	op_WorldMat.invert()
	
	# mult new position against world mat to get corrected coordinate.
	newPos = op_WorldMat * tdu.Position(tx, ty, tz)
	return newPos

##################### ARE THESE EXACTLY THE SAME??? I THINK SO>>

### this function takes an OP, gets it's parent
### retrieves the parent's inverse matrix and 
### uses it to calculate the correct position of
### the child given world space coordinates.
def matCoordFix(myOp, tx, ty ,tz):

	# get reference to the parent component.
	if(len(myOp.inputCOMPs) > 0):
		myOpParent = myOp.inputCOMPs[0]
	else:
		myOpParent = op.geoHolder
		
	# invert the parent matrix
	parent_WorldMat = myOpParent.worldTransform
	parent_WorldMat.invert()
	
	# mult new position against world mat to get corrected coordinate.
	newPos = parent_WorldMat * tdu.Position(tx, ty, tz)
	return newPos
	
def relativeCoords(myOp, tx, ty ,tz):
	'''
	This transforms the given coordinates relative to the op supplied.
	'''
	
	m = myOp.localTransform
	# m.invert()
	
	newPos = m * tdu.Position(tx, ty, tz)
	
	return newPos

### this function simply gets the world space t[xyz] 
### of the supplied geo COMP
def opToWorldSpace(myOp):
	m = myOp.worldTransform
	s, r, t = m.decompose()
	return t
	
	
### this function simply gets the INVERSE world space  
### t[xyz] of the supplied geo COMP's PARENT
def opParentLocation(myOp):
	if(len(myOp.inputCOMPs) > 0):
		myOpParent = myOp.inputCOMPs[0]
	else:
		myOpParent = op.geoHolder
	m = myOpParent.worldTransform
	m.invert()
	s, r, t = m.decompose()
	return t

def fixDragForHulls(myOp, tx,ty,tz ):
	
	wMat = myOp.worldTransform
	wMat.invert()
	pos = tdu.Position(tx,ty,tz)
	pos *= wMat
	newCoordX = pos[0]
	newCoordY = pos[1]
	newCoordZ = pos[2]
	
	returnCoord = [ newCoordX , newCoordY , newCoordZ ]
	
	return returnCoord


def opLocation(myOp):
	
	m = myOp.worldTransform
	m.invert()
	s, r, t = m.decompose()
	return t


def fullMatrixTransform(px, py, pz, tx, ty, tz, rx, ry, rz, sx, sy, sz): # plain python version.
	px = np.asarray(px)
	py = np.asarray(py)
	pz = np.asarray(pz)
	tx = np.asarray(tx)
	ty = np.asarray(ty)
	tz = np.asarray(tz)
	rx = np.asarray(rx)
	ry = np.asarray(ry)
	rz = np.asarray(rz)
	sx = np.asarray(sx)
	sy = np.asarray(sy)
	sz = np.asarray(sz)
	
	crx, srx = np.cos(rx*math.pi/180), np.sin(rx*math.pi/180)
	cry, sry = np.cos(ry*math.pi/180), np.sin(ry*math.pi/180)
	crz, srz = np.cos(rz*math.pi/180), np.sin(rz*math.pi/180)
	
	px *= sx
	py *= sy
	pz *= sz
	
	x = (cry * crz) * px + (srx * sry * crz - srz * crx) * py + (crx * sry * crz + srx * srz) * pz + tx
	y = (cry * srz) * px + (srz * srx * sry + crx * crz) * py + (crx * sry * srz - srx * crz) * pz + ty
	z = -sry * px + (srx * cry) * py + (crx * cry) * pz + tz
	
	result = np.column_stack((x, y, z)).tolist()
	return result
	
	
def InverseMatrix(Op):
	op_ = op(Op)
	
	if op_:
		worldMat = op_.worldTransform
		worldMat.invert()
		s, r, t = worldMat.decompose()
		
		r = [t[0], t[1], t[2], r[0], r[1], r[2], s[0], s[1], s[2]]
	else:
		r = None
	
	return r
	
	
def ProjectionBoundsFromFixtures_v2(projOp, fixtureList=[], custFixtureList=[], surfaceList=[], buffer=1):
	'''
	this function takes a projector object, and a list of fixture objects, and based on the
	orientation of the projector, returns transformation values that will stretch the projector
	to the bounds of the pix in the provided fixtures.
	'''

	# define the x/y/z buffers. this is basically padding for the projector fit.
	# we're taking away x and y padding, but z we still want so after a fit, the projector
	# is immediately lighting up the stuff it's fit to.
	buffers = [ 0 , 0 , buffer ]

	# dict to return data in.
	_r_ = {
		't':{'x':0,'y':0,'z':0},
		'r':{'x':0,'y':0,'z':0},
		's':{'x':1,'y':1,'z':1}
		}
		
	resultList = []
	# we go through all the fixtures, adding their world space pix coords if they exist.
	for fixture in fixtureList:
		if fixture != None:
			pix = fixture.op('pix')
			if pix != None:
				pixData = pix.WorldSpacePixData()
				resultList += pixData
	
		
	# we go through all the fixtures, adding their world space pix coords if they exist.
	for fixture in custFixtureList:
		if fixture != None:
			CUSTOMFIXTURE = fixture.op('CUSTOMFIXTURE')
			if CUSTOMFIXTURE != None:
				p = fixture.worldTransform * tdu.Position(0)
				resultList += [[p.x,p.y,p.z]]
			
	
	# we go through all the Surfaces, adding their world space hull coords if they exist.
	for surface in surfaceList:
		if surface != None:
			hull = surface.op('hull')
			if hull != None:
				hullData = hull.GetAllCoords_WS()
				resultList += hullData
				
	# convert the coords list to a numpy array.
	npList = np.asarray( resultList )
	
	
	# calculate the min and max of each axis of the pix coords.
	mins = np.amin(npList, axis=0) 
	maxs = np.amax(npList, axis=0)
	
	# the avg center of the world space pix coords.
	avgCenters = (mins + maxs) / 2
	
	# set the center coords to a simple list.
	center = [
		(maxs[0] + mins[0]) / 2,
		(maxs[1] + mins[1]) / 2,
		(maxs[2] + mins[2]) / 2
	]
	
	# subtract the center from the list so we put our pix coords in the center of the world.
	npListCentered = np.subtract( npList , center )
	
	# get the parent of the projector if there is one, and get it's inverse translates.
	projParent = mod.tdUtils.getObjectsParent(projOp)
	if projParent != None:
		projParentInvMat = projParent.worldTransform
		projParentInvMat.invert()
		s_, r_, t_ = projParentInvMat.decompose()
	else:
		t_ = [0,0,0]
	
	
	# next we need to create a rotation only matrix to rotate our points to projector space.
	projMatInv = projOp.worldTransform
	s, r, t = projMatInv.decompose() # decompose matrix, we just need rotate right now.
	projRotMat = tdu.Matrix()# create an identity matrix AKA no xforms applied.
	projRotMat.rotate(r[0], r[1], r[2]) # rotate that fresh matrix by the inverse rotation vals of the projector.
	projRotMat.invert()
	s, r, t = projRotMat.decompose()
	
	# new empty list to store rotated coords.
	pointsInProjSpace = []
	
	# tdu Position object to use to transform points by rotation mat.
	offsetPos = tdu.Position(0,0,0)
	
	# rotate each coordinate in the centered pix coords list.
	for coord in npListCentered:
		offsetPos.x = coord[0]
		offsetPos.y = coord[1]
		offsetPos.z = coord[2]
		offsetPos = projRotMat * offsetPos
		pointsInProjSpace += [[offsetPos.x,offsetPos.y,offsetPos.z]]

	# convert the points list we just created to np array.
	pointsInProjSpaceNp = np.asarray(pointsInProjSpace)
	
	# calculate the min and max of each axis of the pix coords after xform and rotate.
	mins = np.amin(pointsInProjSpaceNp, axis=0) 
	maxs = np.amax(pointsInProjSpaceNp, axis=0)
	
	# store the sizes.
	sizeX = (maxs[0] - mins[0]) + (buffers[0]*2)
	sizeY = (maxs[1] - mins[1]) + (buffers[1]*2)
	sizeZ = (maxs[2] - mins[2]) + (buffers[2]*2)
	
	projPosPreRot = tdu.Position( 0 , 0 , (sizeZ/2) + buffer )
	
	
	# next we need to create a rotation only matrix to rotate our points to projector space.
	projMat = projOp.worldTransform
	s, r, t = projMat.decompose() # decompose matrix, we just need rotate right now.
	projRotMat = tdu.Matrix()# create an identity matrix AKA no xforms applied.
	projRotMat.rotate(r[0], r[1], r[2]) # rotate that fresh matrix by the inverse rotation vals of the projector.
	
	# rotate the coordinate.
	projPosPreRot = projRotMat * projPosPreRot
	
	# offset the projector coordinate by the offset we moved the points to center them.
	projPosPreRot.translate( *center )
	
	# set the rotate values for the projector after fit. (should remain the same as before.)
	_r_['r']['x'] = projOp.par.Rx.eval()
	_r_['r']['y'] = projOp.par.Ry.eval()
	_r_['r']['z'] = projOp.par.Rz.eval()
	
	_r_['t']['x'] = projPosPreRot.x
	_r_['t']['y'] = projPosPreRot.y
	_r_['t']['z'] = projPosPreRot.z
	
	projOp.par.Pscale = projOp.par.Pscale.default
	
	# set the scale values after fit. should be == to projector space pix coords computed size.
	_r_['s']['x'] = sizeX / projOp.par.Pscale.default
	_r_['s']['y'] = sizeY / projOp.par.Pscale.default
	_r_['s']['z'] = sizeZ / projOp.par.Pscale.default
	
	
	return _r_
	
	
def OrthographicProjectionMatrix( orthoWidth=100 , near=0.0001 , far=100 ):
	
	width = 500
	height = 500

	right = orthoWidth/2
	left = right * -1
	top = orthoWidth/2
	bottom = top * -1
	aspect = width / height

	m = [0 for x in range(16)]

	m[0] = 2/(right-left)
	m[1] = 0
	m[2] = 0
	m[3] = 0

	m[4] = 0
	m[5] = 2/(top-bottom)*aspect
	m[6] = 0
	m[7] = 0

	m[8] = 0
	m[9] = 0
	m[10] = -2 / (far-near)
	m[11] = 0

	m[12] = ((right+left) / (right-left)) * -1
	m[13] = ((top+bottom) / (top-bottom)) * -1
	m[14] = ((far+near)   / (far-near))   * -1
	m[15] = 1

	m = tdu.Matrix(m)

	return m
	
	
def OrthographicProjectionMatrix_TD( orthoWidth=100 , near=0.0001 , far=100 ):
	'''
	this is currently broken... not sure if I'm feeding function wrong, or if function is broken..
	'''
	width = 500
	height = 500

	right = orthoWidth/2
	left = right * -1
	top = orthoWidth/2
	bottom = top * -1
	# near
	# far

	m = tdu.Matrix()
	m.projectionFrustum( left , right , bottom , top , near , far )

	return m
	
	
def PerspectiveProjectionMatrix_TD( fovX=45 , near=0.0001 , far=100 ):
	width = 500
	height = 500

	m = tdu.Matrix()
	m.projectionFovX(fovX, width, height, near, far)

	return m