"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

For more info, see: http://www.derivative.ca/wiki099/index.php?title=Extensions
"""

import numpy as np
# from TDStoreTools import StorageManager
# TDF = op.TDModules.mod.TDFunctions

DATABLOCK = parent.obj.op('DATABLOCK')

class Generator:
	"""
	Generator description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
	
	def WildCardToIndicies(self):
		
		indexArray = parent.obj.op("hull").GetAllCoordIndiciesAsString()
		# print("WildCardToIndicies", indexArray)
		return indexArray
	
	def Cook(self):
		# '''
		parentObj = parent.obj
		# debug('Generator cooking')
		# mod.globalFuncs.TraceFunctionCall()
		
		hullOp = parent.obj.op("hull")
		pixOp = parent.obj.op("pix")
		
		# if we have at least 1 hull.
		if len(hullOp.GetNumberOfHulls()) > 0:
			
			# get all output comps
			connections = parentObj.outputCOMPs
			
			# filter down the output comps to just generators.
			connections = [x for x in connections if 'typeID:50' in x.tags]

			if len(connections) == 0:
				return
			
			# group generators into "buckets" according to their targeted coordinate set.
			gennyBuckets = {}
			for genny in connections:
				coordSet = int( genny.par.Coordinateset.eval() )-1
				bucket = gennyBuckets.get( coordSet, [] )
				bucket.append( genny )
				gennyBuckets[coordSet] = bucket

			# outliner sort gennys of each bucket.
			for k,v in gennyBuckets.items():
				gennyBuckets[k] = op.sceneOutliner.mod.tdUtils.outlinerSort(v)

			# sum up total number of coords to be generated for each bucket.
			bucketSums = [ sum([ int(genny.op('GENERATOR/null_numPix')[0]) for genny in bucket ]) for bucket in gennyBuckets.values() ]

			# if genblock is on... halt operations, do nothing.
			if parentObj.par.Genblock == True:
				op.NOTIFV2.Notify(parentObj.par.Name + ' has custom user data, Please click "Regen" in any of its generators to force regenerate.')
				return

			elif len( set(bucketSums) ) > 1:
				op.NOTIFV2.Notify(parentObj.par.Name + ' has generators associated with it that are producing inconsistent numbers of coordinates across different coordinate sets. Some unintended clipping or extending will occur.')
				if parentObj.par.Coordsetmismatch.eval() == False:
					parentObj.par.Coordsetmismatch = True
				return

			elif op.EDITOR_SETTINGS.par.Enablecoordinatesets.eval() == False and len( gennyBuckets.get(0,[]) ) == 0:
				op.NOTIFV2.Notify(parentObj.par.Name + ' has no generators associated with it that are producing coordinates on Set 1, and Coordinate Sets are disabled in Settings. Your Generators will not generate Pix properly unless Set1 is used, or Coordinate Sets are enabled in Preferences.')
				return
			
			# if genblock was off, we have no custom data and we can just recalculate our data.
			else:
				# print('sdfgx')
				if parentObj.par.Coordsetmismatch.eval() == True:
					parentObj.par.Coordsetmismatch = False
				# start off by wiping all our pix, so we can re generate them.
				pixOp.DeleteAll()

				# iterate through connections of each bucket.
				for coordSetIndex,connections in gennyBuckets.items():

					if len(connections) > 0:
						
						# define some things.
						pixOffsetCounter = 0
						clampedGenerators = []
						gchans = ''
						
						# for each sorted generator that is a child of this Fixture.
						for x in connections:
							childOp = x
							if childOp.par.Objtype == 7: # 7 is the code for generator type
								
								generatorText = childOp.op("GENERATOR/__gen__").text
								Genfixturemask = childOp.par.Genfixturemask.eval() # generates a full mask across the generated data.
								
								#################### uncomment this to bring back generator fixture mask names.. we turned this off 
								#################### so that we could generate masks more easily through the mask wizard.
								fixtureMaskNames = []
								
								
								if generatorText not in ["", " "]:
								
									genArgs = generatorText.split(",")
									
									genType = genArgs[0]
									genMode = genArgs[1]
									
									xCount = int(float(genArgs[2]))
									yCount = int(float(genArgs[3]))
									
									xPitch = float(float(genArgs[4]))
									yPitch = float(float(genArgs[5]))	
									
									zigZag = int(float(genArgs[8]))
									
									# stuff related to Helix.
									diam1 = float(genArgs[9])
									diam2 = float(genArgs[10])
									revs = float(genArgs[11])
									coordSet = int(genArgs[12])-1
									
									# general stuffs.
									coordsStr = genArgs[13]
									xtraChans = genArgs[14].split("-")
									
									Cutoff = int(genArgs[15])
									# print(xtraChans)
									
									if coordsStr == "*":
										coordsStr = self.WildCardToIndicies()
									
									# wildcardtoindicies returns None if there are no hull points.
									if coordsStr != None:
										coordsStr = coordsStr.split("-")
										
										coords = []
										for c in coordsStr:
											coords += [ int(float(c)) ]
										
										
										
										genResult =	self.Generate(	genType=genType, genMode=genMode, 
														xCount=xCount, yCount=yCount, 
														xPitch=xPitch, yPitch=yPitch, 
														indexOffset=pixOffsetCounter,
														zigZag=zigZag, coords=coords,
														chans=xtraChans, diam1=diam1,
														diam2=diam2, revs=revs, Cutoff=Cutoff,
														genMasks=fixtureMaskNames,
														coordSet=coordSet,
													)
										pixOffsetCounter += genResult['numPix']
										x.par.Numpixfromgen = genResult['numPix']
										
										if genResult['isClamped']:
											clampedGenerators += [childOp.par.Name.eval()]
									# debug('assigning ChanOrder from Gchans', childOp.par.Gchans.eval())
									gchans = childOp.par.Gchans
							
							# debug('pixOffs', parent.obj.par.Pixfillamount.eval(), pixOffsetCounter)
							if parent.obj.par.Pixfill.eval() == True:
								self.Dummy_Fill(cutoff=parent.obj.par.Pixfillamount.eval(), indexOffset=pixOffsetCounter, coordSet=coordSet)
							
							parentObj.par.Chanorder = gchans
							pixOp.WriteCoordsToTable()
							
							
							
							# hullOp = parent.obj.op("hull")
							pixOp.cook(force=1)
							hullOp.cook(force=1)
							hullOp.ArcLength = hullOp.ArcLen()
							hullOp.NumHulls = len(hullOp.GetNumberOfHulls())
							pixOp.NumPix = pixOp.GetTotalNumberOfPix()
							
							pixOp.ArcLength = pixOp.ArcLen()
							
							if len(clampedGenerators):
								DATABLOCK.par.Clippedgenerators = ','.join(clampedGenerators)
							else:
								DATABLOCK.par.Clippedgenerators = ''
								
						# '''
	
	# genType: the operation type, strip, grid, etc
	#1 xCount: count of pix on X
	#2 yCount: count of pix on Y
	#3 xPitch: spacing between pix on X
	#4 yPitch: spacing between pix on Y
	#7 indexOffset: starting index for the pix generation.
	#8 coords: the hull coords that will be interpreted and used to generate the pix.
	def Generate(self, genType="", genMode="", xCount=0, yCount=0, xPitch=0, yPitch=0, indexOffset=0, zigZag=0, coords=[], chans=[], diam1=0, diam2=0, revs=0, Cutoff=100, genMasks=[], coordSet=0):
		
		isClamped = False
		
		xPitch = max(xPitch,1)
		yPitch = max(yPitch,1)
		
		numLeds = 0
		
		### if we're generating a strip by count...
		if genType == "Strip" and genMode == "Count":
			
			returnData = self.Strip_Count(xCount=xCount, indexOffset=indexOffset, coords=coords, chans=chans, cutoff=Cutoff, genMasks=genMasks, coordSet=coordSet)
			numLeds = xCount
			
			isClamped = returnData['isClamped']
		

		
		### if we're generating a strip by pitch...
		elif genType == "Strip" and genMode == "Pitch":
			
			hullOp = parent.obj.op("hull")
			hullCoords = hullOp.GetSpecifiedCoords( coords )
			arcLen = self.calcArcLength(hullCoords)
			numLeds = max( int(arcLen / xPitch) , 2 ) # limit to 2 minimum so that strip_count doesn't error.
			
			if numLeds >= len(coords):
				returnData = self.Strip_Count(xCount=numLeds, indexOffset=indexOffset, coords=coords, chans=chans, cutoff=Cutoff, genMasks=genMasks, coordSet=coordSet)
				isClamped = returnData['isClamped']
				numLeds = returnData['numPix']
				# flag this as clamped
				# if numLeds >= Cutoff:
					# isClamped = True
			
			else:
				# debug("Currently, you need to specify more PIX than you have HULL's")
				op.NOTIFV2.Notify("You need to specify more PIX than you have HULL's")
		
		
		
		### if we're generating a grid
		elif genType == "Grid" and genMode in ['Count','Pitch']:
			
			### if we're generating a static grid.
			if len(coords) == 1:
				returnData = self.Grid1(xCount=xCount, yCount=yCount, xPitch=xPitch, yPitch=yPitch, zigZag=zigZag, indexOffset=indexOffset, axis=2, coords=coords, chans=chans, cutoff=Cutoff, genMasks=genMasks, coordSet=coordSet)
				isClamped = returnData['isClamped']
				# numLeds = xCount * yCount
				numLeds = returnData['numPix']
			
			### if we're generating a dynamic grid.
			elif len(coords) == 4:
				returnData = self.Grid4(xCount=xCount, yCount=yCount, zigZag=zigZag, indexOffset=indexOffset, axis=2, coords=coords, chans=chans, cutoff=Cutoff, genMasks=genMasks, coordSet=coordSet)
				isClamped = returnData['isClamped']
				# numLeds = xCount * yCount
				numLeds = returnData['numPix']
			else:
				# debug("Provide either 1 or 4 hulls for Grid generators to work.")
				op.NOTIFV2.Notify('Provide either 1 or 4 hulls for Grid generators to work.')
		
		
		
		### if we're generating a helix
		elif genType == "Helix" and genMode in ['Count','Pitch']:
			### if we're generating a 2 point helix aka dynamic helix.
			if len(coords) == 2:
				# we don't need to limit when the user var is the actual limit...
				returnData = self.Helix2(xCount=xCount, xPitch=xPitch, diam1=diam1, diam2=diam2, revs=revs, coords=coords, chans=chans, genMode=genMode, indexOffset=indexOffset, cutoff=Cutoff, genMasks=genMasks, coordSet=coordSet)
				isClamped = returnData['isClamped']
				# numLeds = xCount
				numLeds = returnData['numPix']
			
			else:
				# debug("Provide exactly 2 hulls for a Helix generator to work.")
				op.NOTIFV2.Notify('Provide exactly 2 hulls for a Helix generator to work.')
				
				
		### if we're generating a grid
		elif genType == "Cube" and genMode in ['Count','Pitch']:
			
			### if we're generating a static cube.
			if len(coords) == 1:
				xtraCounter = 0
				runningTotal = 0
				for x in range(xCount):
					if runningTotal > Cutoff:
						isClamped = True
						break
						
					addyOffset = (x * xPitch) - (((xCount-1)*xPitch)/2)
					returnData = self.Grid1(xCount=xCount, yCount=yCount, xPitch=xPitch, yPitch=yPitch, zigZag=zigZag, indexOffset=indexOffset+xtraCounter, axis=2, coords=coords, chans=chans, xtraOffset=addyOffset, cutoff=Cutoff, genMasks=genMasks, coordSet=coordSet)
					isClamped = returnData['isClamped']
					numLedsThisItr = returnData['numPix']
					xtraCounter += numLedsThisItr
					runningTotal += numLedsThisItr
				numLeds = runningTotal

				
			else:
				# debug("Provide exactly 1 hull for Cube generators to work.")
				op.NOTIFV2.Notify('Provide exactly 1 hull for Cube generators to work.')
				
		
		# update the dat table now that we're done doing stuff to the data.
		# pixOp = parent.obj.op("pix")
		# print('ccc', isClamped)
		return {'numPix':numLeds , 'isClamped':isClamped}
		
		
	###################	  START ACTUAL GENERATION FUNCTIONS	  ###########################
	def Dummy_Fill(self, cutoff=100, indexOffset=0, coordSet=0):
		
		
		pixOp = parent.obj.op("pix")
		CurrentNumPix = pixOp.GetTotalNumberOfPix()
		NumLeft = cutoff - CurrentNumPix
		
		lastCoord = pixOp.GetAllCoords()[-1]
		
		if NumLeft > 0:
			# debug('filling...')
			chans = list(set([] + pixOp.GetChansList()))
			masks = list(set([] + pixOp.GetMaskList())) 
			count = indexOffset
			for i in range(NumLeft):
				pixOp.AddPixRaw(
					x = lastCoord[0], 
					y = lastCoord[1],
					z = lastCoord[2],
					# ["r", "g", "b"],
					xtraChans = chans,
					xtraMasks = masks,
					selected = 0,
					i = count,
					coordSetIndex=coordSet
				)
				count+= 1
				
		elif NumLeft < 0:
			# debug('clipping...')
			pixOp.SlicePixDict(0,cutoff)
			pass
		
		else:
			pass
		
		return
		
	### generates a strip based off of a pix count.
	def Strip_Count(self, xCount=10, indexOffset=0, coords=[], chans=[], cutoff=100 , genMasks=[], coordSet=0):
		# print(genMasks)
		isClamped = False
		
		if len(coords) >= 2 and xCount > 2:
		
			hullOp = parent.obj.op("hull")
			pixOp = parent.obj.op("pix")
			
			hullCoords = hullOp.GetSpecifiedCoords( coords )
		
			# s = (xCount,3)
			s = ( max( xCount , len(hullCoords) ) ,3)
			data = np.zeros(s)
			counter = 0
			
			# print('hullCoords len is:', len(hullCoords))
			# print('data len is:', len(data))
			for hullCoord in hullCoords:
				data[counter][0] = hullCoord[0]
				data[counter][1] = hullCoord[1]
				data[counter][2] = hullCoord[2]
				counter += 1
			
			arcLen = self.calcArcLength(hullCoords)
			
			x,y,z = data.T
			xd = np.diff(x)
			yd = np.diff(y)
			zd = np.diff(z)
			
			dist = np.sqrt(xd**2+yd**2+zd**2)
			u = np.cumsum(dist)
			u = np.hstack([[0],u])
			t = np.linspace(0,arcLen,int(xCount)) * 1.
			xn = np.interp(t, u, x)
			yn = np.interp(t, u, y)
			zn = np.interp(t, u, z)

			combined = np.vstack((xn, yn, zn)).T
			
			# convert to normal python list
			combined = combined.tolist()
			
			if len( combined ) > cutoff:
				combined = combined[0:cutoff]
				isClamped = True
			
			chans = list(set(chans + pixOp.GetChansList()))
			masks = list(set(genMasks + pixOp.GetMaskList())) 
			count = indexOffset
			for coord in combined:
				pixOp.AddPixRaw(
					x = coord[0], 
					y = coord[1],
					z = coord[2],
					# ["r", "g", "b"],
					xtraChans = chans,
					xtraMasks = masks,
					selected = 0,
					i = count,
					coordSetIndex=coordSet
				)
				count+= 1
		
		returnDict = {}
		returnDict['isClamped'] = isClamped
		returnDict['numPix'] = len(combined)
			
		return returnDict
		
	def Grid1(self, xCount=10, yCount=10, xPitch=3.333, yPitch=3.333, indexOffset=0, zigZag=0, axis=2, coords=[], chans=[], xtraOffset=0, cutoff=100, genMasks=[], coordSet=0):
		
		isClamped = False
		
		if len(coords) == 1:
		
			hullOp = parent.obj.op("hull")
			pixOp = parent.obj.op("pix")
			
			hullCoords = hullOp.GetSpecifiedCoords( coords )
			oX, oY, oZ = hullCoords[0][0] , hullCoords[0][1] , hullCoords[0][2]
		
			dimX , dimY  = ((xCount-1) * xPitch)/2 , ((yCount-1) * yPitch)/2
			
			# generate grid using numpy magic.
			nx , ny = ( xCount , yCount )
			x = np.linspace( 0 , ((xCount-1)*xPitch) , nx )
			y = np.linspace( 0 , ((yCount-1)*yPitch) , ny )
			xv , yv = np.meshgrid( x , y )
			
			# center grid on x and y.
			xv -= dimX
			yv -= dimY
			
			zv = abs(xv * 0)
			
			if(zigZag == 1):
				flipMe = 0
				for x in range( len(xv) ):
					if(flipMe == 0):
						flipMe = 1
					elif(flipMe == 1):
						xv[x] = xv[x][::-1]
						flipMe = 0
			
			# turn into 1 dimensional arrays of coordinates.
			xv = np.ravel(xv)
			yv = np.ravel(yv)
			zv = np.ravel(zv)
			
			if(axis == 2):
				yv *= -1 # flip it on y so first led is top left.
			elif(axis == 1):
				yv *= +1
			elif(axis == 0):
				yv *= -1
				
			xv = xv.tolist()
			yv = yv.tolist()
			zv = zv.tolist()
				
			finalCoordinates = []
			for x in range(len(xv)):
				if(axis == 2):
					finalCoordinates += [ [ xv[x]+oX , yv[x]+oY , zv[x]+oZ ] ]
				elif(axis == 1):
					finalCoordinates += [ [ xv[x]+oX , zv[x]+oY , yv[x]+oZ ] ]
				elif(axis == 0):
					finalCoordinates += [ [ zv[x]+oX , yv[x]+oY , xv[x]+oZ ] ]
			
			if len( finalCoordinates ) > cutoff:
				finalCoordinates = finalCoordinates[0:cutoff]
				isClamped = True
			
			
			chans = list(set(chans + pixOp.GetChansList()))
			masks = list(set(genMasks + pixOp.GetMaskList())) 
			count = indexOffset
			for coord in finalCoordinates:
				pixOp.AddPixRaw(
					x = coord[0], 
					y = coord[1],
					z = coord[2] + xtraOffset,
					xtraChans = chans,
					xtraMasks = masks,
					selected = 0,
					i = count,
					coordSetIndex=coordSet
				)
				count+= 1
		
		returnDict = {}
		returnDict['isClamped'] = isClamped
		returnDict['numPix'] = len(finalCoordinates)
			
		return returnDict
		
	def Grid4(self, xCount=10, yCount=10, indexOffset=0, zigZag=0, axis=2, coords=[], chans=[], cutoff=100, genMasks=[], coordSet=0):
		
		isClamped = False
		
		if len(coords) == 4:
		
			hullOp = parent.obj.op("hull")
			pixOp = parent.obj.op("pix")
			
			hullCoords_ = hullOp.GetSpecifiedCoords( coords )
			
			hullCoords = [[],[],[],[]]
			hullCoords[0] = hullCoords_[3]
			hullCoords[1] = hullCoords_[0]
			hullCoords[2] = hullCoords_[1]
			hullCoords[3] = hullCoords_[2]
			
			# generate grid using numpy magic.
			nx , ny = ( xCount , yCount )
			x = np.linspace( 0 , ((xCount)/xCount) , nx )
			y = np.linspace( 0 , ((yCount)/yCount) , ny )
			xv , yv = np.meshgrid( x , y )
			
			# center grid on x and y.
			xv -= .5
			yv -= .5
			zv = abs(xv * 0)
			
			if(zigZag == 1):
				flipMe = 0
				for x in range( len(xv) ):
					if(flipMe == 0):
						flipMe = 1
					elif(flipMe == 1):
						xv[x] = xv[x][::-1]
						flipMe = 0
			
			# turn into 1 dimensional arrays of coordinates.
			xv = np.ravel(xv)
			yv = np.ravel(yv)
			zv = np.ravel(zv)
			
			if(axis == 2):
				yv *= -1 # flip it on y so first led is top left.
				
			finalCoordinates = []
			for x in range(len(xv)):
				if(axis == 2):
					
					yNrm = tdu.remap(yv[x],-.5,.5,0,1)
					x_bot = self.interp_1d( hullCoords[0][0] , hullCoords[1][0] , yNrm )
					x_top = self.interp_1d( hullCoords[3][0] , hullCoords[2][0] , yNrm )
					xv_ = tdu.remap( xv[x] , -.5 , .5 , x_bot , x_top )
					
					xNrm = tdu.remap(xv[x],-.5,.5,0,1)
					yvA = self.interp_1d( hullCoords[0][1] , hullCoords[3][1] , xNrm )
					yvB = self.interp_1d( hullCoords[1][1] , hullCoords[2][1] , xNrm )
					yv_ = tdu.remap( yv[x] , -.5 , .5 , yvA , yvB )
					
					zvA = self.interp_1d( hullCoords[0][2] , hullCoords[3][2] , xNrm )
					zvB = self.interp_1d( hullCoords[1][2] , hullCoords[2][2] , xNrm )
					zv_ = tdu.remap( yv[x] , -.5 , .5 , zvA , zvB )
					
					finalCoordinates += [ [ xv_ , yv_, zv_ ] ]
			
			if len( finalCoordinates ) > cutoff:
				finalCoordinates = finalCoordinates[0:cutoff]
				isClamped = True
			
			chans = list(set(chans + pixOp.GetChansList()))
			masks = list(set(genMasks + pixOp.GetMaskList())) 
			count = indexOffset
			for coord in finalCoordinates:
				pixOp.AddPixRaw(
					x = coord[0], 
					y = coord[1],
					z = coord[2],
					xtraChans = chans,
					xtraMasks = masks,
					selected = 0,
					i = count,
					coordSetIndex=coordSet
				)
				count+= 1
		
		returnDict = {}
		returnDict['isClamped'] = isClamped
		returnDict['numPix'] = len(finalCoordinates)
		return returnDict
		
		
	def Helix2(self, xCount=30, xPitch=3.333, indexOffset=0, diam1=50, diam2=50, revs=2, coords=[], chans=[], genMode='Count', cutoff=100, genMasks=[], coordSet=0):
		
		isClamped = False
		
		if len(coords) == 2:
			
			hullOp = parent.obj.op("hull")
			pixOp = parent.obj.op("pix")
			
			hullCoords = hullOp.GetSpecifiedCoords( coords )
			dist = self.dist3d(hullCoords[0][0] , hullCoords[1][0] , hullCoords[0][1] , hullCoords[1][1] , hullCoords[0][2] , hullCoords[1][2] )
			
			# Plot a helix along the x-axis
			diamScale = np.linspace(diam1, diam2, num=xCount)
			theta_max = np.linspace( 0, ((revs) * (np.pi*2)) , num=xCount )
			maxY = np.linspace(0, dist, xCount)
			px = np.sin(theta_max) * diamScale
			py = maxY
			pz = np.cos(theta_max) * diamScale
			
			v2 = [0,0,0]
			v2[0] = hullCoords[1][0] - hullCoords[0][0]
			v2[1] = hullCoords[1][1] - hullCoords[0][1]
			v2[2] = hullCoords[1][2] - hullCoords[0][2]
			angleDiff = self.vectDif_2_eulerRot( [0,1,0] , v2 )
			
			tx,ty,tz =  np.full( xCount,hullCoords[0][0] , dtype=float) , np.full(xCount,hullCoords[0][1] , dtype=float) , np.full(xCount,hullCoords[0][2] , dtype=float )
			rx = np.full(xCount,angleDiff[0] , dtype=float)
			ry = np.full(xCount,angleDiff[1] , dtype=float)
			rz = np.full(xCount,angleDiff[2] , dtype=float)
			sx, sy, sz = np.full(xCount,1 , dtype=float) , np.full(xCount,1 , dtype=float) , np.full(xCount,1 , dtype=float)
			
			h1_x = hullCoords[0][0]
			h1_y = hullCoords[0][1]
			h1_z = hullCoords[0][2]
			
			h2_x = hullCoords[1][0]
			h2_y = hullCoords[1][1]
			h2_z = hullCoords[1][2]
			
			# if hull 0 is directly above hull 1 the helix generator gets flipped on Y. this corrects for it
			if h1_x == h2_x and h1_z == h2_z and h1_y > h2_y:
				rx *= 0
			
			finalCoordinates = self.transform(px,py,pz,tx,ty,tz,rx,ry,rz,sx,sy,sz)
			arcLen_ = self.calcArcLength(finalCoordinates)
			
			### generate a 2 point helix by count.
			if genMode == 'Count':
				finalCoordinates = self.resampleCoords(finalCoordinates, xCount)
			
			### generate a 2 point helix by pitch.
			elif genMode == 'Pitch':
				xCount = int((arcLen_ / xPitch))
				finalCoordinates = self.resampleCoords(finalCoordinates, xCount)
				
			
			# convert to normal python list
			finalCoordinates = finalCoordinates.tolist()
			
			if len( finalCoordinates ) > cutoff:
				finalCoordinates = finalCoordinates[0:cutoff]
				isClamped = True
			
			
			chans = list(set(chans + pixOp.GetChansList()))
			masks = list(set(genMasks + pixOp.GetMaskList())) 
			count = indexOffset
			for coord in finalCoordinates:
				pixOp.AddPixRaw(
					x = coord[0], 
					y = coord[1],
					z = coord[2],
					xtraChans = chans,
					xtraMasks = masks,
					selected = 0,
					i = count,
					coordSetIndex=coordSet
				)
				count+= 1
			
		returnDict = {}
		returnDict['isClamped'] = isClamped
		returnDict['numPix'] = len(finalCoordinates)
			
		return returnDict
	
	
	
	
	
	
	def resampleCoords(self, coords=[], xCount=30):
		arcLen = self.calcArcLength(coords)
		
		x,y,z = coords.T
		xd = np.diff(x)
		yd = np.diff(y)
		zd = np.diff(z)
		
		dist = np.sqrt(xd**2+yd**2+zd**2)
		u = np.cumsum(dist)
		u = np.hstack([[0],u])
		t = np.linspace(0,arcLen,int(xCount)) * 1.
		xn = np.interp(t, u, x)
		yn = np.interp(t, u, y)
		zn = np.interp(t, u, z)

		combined = np.vstack((xn, yn, zn)).T
		
		return combined
	
	def vectDif_2_eulerRot(self, vector_orig, vector_fin):
		"""Calculate the rotation matrix required to rotate from one vector to another.

		For the rotation of one vector to another, there are an infinit series of rotation matrices
		possible.  Due to axially symmetry, the rotation axis can be any vector lying in the symmetry
		plane between the two vectors.	Hence the axis-angle convention will be used to construct the
		matrix with the rotation axis defined as the cross product of the two vectors.	The rotation
		angle is the arccosine of the dot product of the two unit vectors.

		Given a unit vector parallel to the rotation axis, w = [x, y, z] and the rotation angle a,
		the rotation matrix R is::

				  |	 1 + (1-cos(a))*(x*x-1)	  -z*sin(a)+(1-cos(a))*x*y	 y*sin(a)+(1-cos(a))*x*z |
			R  =  |	 z*sin(a)+(1-cos(a))*x*y   1 + (1-cos(a))*(y*y-1)	-x*sin(a)+(1-cos(a))*y*z |
				  | -y*sin(a)+(1-cos(a))*x*z   x*sin(a)+(1-cos(a))*y*z	 1 + (1-cos(a))*(z*z-1)	 |


		@param R:			The 3x3 rotation matrix to update.
		@type R:			3x3 numpy array
		@param vector_orig: The unrotated vector defined in the reference frame.
		@type vector_orig:	numpy array, len 3
		@param vector_fin:	The rotated vector defined in the reference frame.
		@type vector_fin:	numpy array, len 3
		"""
		
		R = np.matrix([[1., 0, 0], [0, 1., 0], [0, 0, 1.]])
		
		# Convert the vectors to unit vectors.
		vector_orig = vector_orig / np.linalg.norm(vector_orig)
		vector_fin = vector_fin / np.linalg.norm(vector_fin)

		# The rotation axis (normalised).
		axis = np.cross(vector_orig, vector_fin)
		axis_len = np.linalg.norm(axis)
		if axis_len != 0.0:
			axis = axis / axis_len

		# Alias the axis coordinates.
		x = axis[0]
		y = axis[1]
		z = axis[2]

		# The rotation angle.
		angle = math.acos(np.dot(vector_orig, vector_fin))

		# Trig functions (only need to do this maths once!).
		ca = math.cos(angle)
		sa = math.sin(angle)

		# Calculate the rotation matrix elements.
		R[0,0] = 1.0 + (1.0 - ca)*(x**2 - 1.0)
		R[0,1] = -z*sa + (1.0 - ca)*x*y
		R[0,2] = y*sa + (1.0 - ca)*x*z
		R[1,0] = z*sa+(1.0 - ca)*x*y
		R[1,1] = 1.0 + (1.0 - ca)*(y**2 - 1.0)
		R[1,2] = -x*sa+(1.0 - ca)*y*z
		R[2,0] = -y*sa+(1.0 - ca)*x*z
		R[2,1] = x*sa+(1.0 - ca)*y*z
		R[2,2] = 1.0 + (1.0 - ca)*(z**2 - 1.0)
		
		sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])
		
		singular = sy < 1e-6
	 
		if	not singular :
			x = math.atan2(R[2,1] , R[2,2])
			y = math.atan2(-R[2,0], sy)
			z = math.atan2(R[1,0], R[0,0])
		else :
			x = math.atan2(-R[1,2], R[1,1])
			y = math.atan2(-R[2,0], sy)
			z = 0
	 
		return np.rad2deg( np.array([x, y, z]) )
	
	### helper util, calculated the arc length given a set of coordinates.
	def calcArcLength(self, coordList ):
		coordList2 = np.asarray(coordList)
		# print(coordList2)
		x,y,z = coordList2.T
		xd =np.diff(x)
		yd = np.diff(y)
		zd = np.diff(z)
		
		dist = np.sqrt(xd**2+yd**2+zd**2)
		u = np.cumsum(dist)
		u = np.hstack([[0],u])
		return u[-1]

	
	def dist3d(self, x1, x2, y1, y2, z1, z2):
		x_ = ((x2-x1) * (x2-x1))
		y_ = ((y2-y1) * (y2-y1))
		z_ = ((z2-z1) * (z2-z1))
		result = math.sqrt(x_ + y_ + z_)
		return result
	
	### x = normalized value from 0-1
	def interp_1d(self, x1, x2, x):
		r = (x1 * (1-x)) + (x2 * x)
		# print(r)
		return r
		
		
	def transform(self, px, py, pz, tx, ty, tz, rx, ry, rz, sx, sy, sz): # numpy array math version.
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
		
		result = np.column_stack((x, y, z))
		return result