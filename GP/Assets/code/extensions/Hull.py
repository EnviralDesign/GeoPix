"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

For more info, see: http://www.derivative.ca/wiki099/index.php?title=Extensions
"""

from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions
import copy
import numpy as np
import yaml
import json
from collections.abc import Sequence
import decimal

t = op("hull_coords")
DATABLOCK = parent.obj.op('DATABLOCK')

class Hull:
	"""
	Hull description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		
		# properties
		TDF.createProperty(self, 'ArcLength', value=0, dependable=True, readOnly=False)
		TDF.createProperty(self, 'NumHulls', value=0, dependable=True, readOnly=False)
		
		# stored items (persistent across saves and re-initialization):
		storedItems = [
			# Only 'name' is required...
			{'name': 'coordList', 'default': {"x":0, "y":0, "z":0, "selected":0}, 'property': True, 'dependable': False},
		]
		self.stored = StorageManager(self, ownerComp, storedItems, locked=False)
		# print("INIT_HULL", self.coordList)
		
	def format_number(self, num):
		
		# handle cases where number is very small, but close to zero.
		if abs(num) < 0.0001:
			num = 0
			
		remainder = num % 1
		if abs(remainder) < 0.0001:
			num = int(num)
		
		num = round(num,6)
		
		return num
	
	def strip_depend(self, obj):
		# this function traverses a dict, removing TD dependability from it so we can work with it natively in json dumps.
		if isinstance(obj, dict):
			return {k: self.strip_depend(v) for k, v in obj.items()}
		elif isinstance(obj, list):
			return [self.strip_depend(elem) for elem in obj]
		elif type(obj).__name__ == 'DependDict':
			return { k:v.getRaw() for k,v in obj.items() }
			return round(obj,2)
		else:
			return obj  # no container, just values (str, int, float)
	
	def format_extreme_floats(self, obj):
		
		# this function traverses a dict, removing TD dependability from it so we can work with it natively in json dumps.
		if isinstance(obj, dict):
			return {k: self.format_extreme_floats(v) for k, v in obj.items()}
		elif isinstance(obj, list):
			return [self.format_extreme_floats(elem) for elem in obj]
		elif isinstance(obj, float):
			return self.format_number( obj )
		else:
			return obj  # no container, just values (str, int, float)
	
	def format_dict_keys_ints(self, obj):
		return { int(k):v for k,v in obj.items() }
	
	def GetHullDict(self, deep=False):
		if deep == False:
			return self.coordList.copy()
		else:
			return copy.deepcopy( self.coordList )
		
		
	def ReplaceHullDict(self, HullDict):
		self.coordList = HullDict
		self.WriteCoordsToTable()
		return
		
	def GetDictAsYaml(self, coordsOnly = False):
		
		returnItem = ''
		
		if coordsOnly == False:
			d = self.GetHullDict()
			returnItem = yaml.dump(d)
			
		elif coordsOnly == True:
			c = self.GetAllCoords()
			c = '\n'.join( [','.join(map(str,[round(y,4) for y in x])) for x in c] )
			returnItem = c
		return returnItem
		
	def GetDictAsJson(self, coordsOnly = False):
		
		returnItem = ''
		
		if coordsOnly == False:
			d = self.GetHullDict()
			d = self.strip_depend(d)
			d = self.format_extreme_floats(d)
			
			returnItem = json.dumps( d , indent=4 )
			
		elif coordsOnly == True:
			c = self.GetAllCoords()
			c = '\n'.join( [','.join(map(str,[round(y,4) for y in x])) for x in c] )
			# print(c)
			returnItem = c
		return returnItem
		
	def LoadJsonAsDict(self, jsonStr = None):
		if jsonStr != None:
			
			d = json.loads(jsonStr)
			d = self.format_dict_keys_ints(d)
			
			self.ReplaceHullDict(d)
			# self.SaveToBuffer()
		
	def LoadYamlAsDict(self, yamlStr = None):
		if yamlStr != None:
			d = yaml.load(yamlStr)
			self.ReplaceHullDict(d)
			# self.SaveToBuffer()
	
	def PushNewCoords(self, tableFormattedStr = None):
		if tableFormattedStr != None:
			# print(tableFormattedStr)
			lines = tableFormattedStr.split('\n')
			lines = [x for x in lines if x != '']# remove blank lines
			data = [ [float(y) for y in x.split(',')] for x in lines]
			
			dictLen = len(self.coordList)
			listLen = len(data)
			
			# if the source coords and dictionary length are the same... simply replace the coord values.
			if listLen == dictLen:
				for i,coord in enumerate(data):
					self.coordList[i]['x'] = coord[0]
					self.coordList[i]['y'] = coord[1]
					self.coordList[i]['z'] = coord[2]
			
			# if user provided more coordinates than there are dict entries..
			elif listLen > dictLen and dictLen > 0:
				for i,coord in enumerate(data):
					if i < dictLen: # as long as we're within range of the dictionary, just set values
						self.coordList[i]['x'] = coord[0]
						self.coordList[i]['y'] = coord[1]
						self.coordList[i]['z'] = coord[2]
					else: # once we've gone beyond the range of the dictionary... deep copy last, and set coords.
						self.coordList[i] = copy.deepcopy( self.coordList[dictLen-1] )
						self.coordList[i]['x'] = coord[0]
						self.coordList[i]['y'] = coord[1]
						self.coordList[i]['z'] = coord[2]
						
			# if user provided more coordinates than there are dict entries.. AND dict as 0 entries.
			elif listLen > dictLen and dictLen == 0:
				for i,coord in enumerate(data):
					# print("i", i, listLen, dictLen)
					# self.AddPixRaw(  x=coord[0] , y=coord[1] , z=coord[2] , xtraChans=['r','g','b'] , xtraMasks=[], selected=0 , i=i  )
					self.AddCoord( x=coord[0] , y=coord[1] , z=coord[2] , u=0 , v=0 , selected=0 , i=i , localSpace=True )
					# self.coordList[i]['coords']['x']['val'] = coord[0]
					# self.coordList[i]['coords']['y']['val'] = coord[1]
					# self.coordList[i]['coords']['z']['val'] = coord[2]
						
			# if user provided more coordinates than there are dict entries..
			elif listLen < dictLen:
				for i,coord in enumerate(data):
					if i < dictLen: # as long as we're within range of the dictionary, just set values
						self.coordList[i]['x'] = coord[0]
						self.coordList[i]['y'] = coord[1]
						self.coordList[i]['z'] = coord[2]
						
				for x in range(listLen,dictLen):# delete the keys that come after.
					del self.coordList[x]
						
			# dump = yaml.dump(self.coordList)
			# print(dump)
			
			# self.SaveToBuffer()
			self.WriteCoordsToTable()
	
	
	def GetTotalNumberOfHulls(self):
		return len( self.coordList )
	
	def GetAllCoords(self):
		coordsList = []
		for k,v in self.coordList.items():
			# print(key,value)
			coordsList += [ [v['x'] , v['y'] , v['z']] ]
		
		return coordsList
	
	def GetAllCoords_WS(self):
		
		worldCoords = []
		parentMat = parent.obj.worldTransform
		offsetPos = tdu.Position(0,0,0)
		for k,v in self.coordList.items():
			offsetPos[0],offsetPos[1],offsetPos[2] = v['x'] , v['y'] , v['z']
			newPos = parentMat * offsetPos
			worldCoords += [ [newPos[0],newPos[1],newPos[2]] ]
		
		return worldCoords
	
	
	def GetAllUvs(self):
		coordsList = []
		for k,v in self.coordList.items():
			# print(key,value)
			coordsList += [ [v['u'] , v['v'] ] ]
		
		return coordsList
		
	
	def PrintCoords(self):
		for key, value in self.coordList.items():
			print(key,value)
		return
		
	def GetAllCoordIndiciesAsString(self):
		indexList = []
		for key, value in self.coordList.items():
			# print(key,value)
			indexList += [str(key)]
		
		if len(indexList) > 0:
			return ( "-".join(indexList) )
		else:
			return None
			
	def ReverseAllHulls(self):
		newDict = {}
		myLen = len(self.coordList)
		for k in self.coordList.keys():
			newDict[ k ] = self.coordList[myLen-1-k]
		self.coordList = newDict
		# self.fixNumbering()
		return
	
	def GetSelectedCoordIndiciesAsString(self):
		# print(self.coordList)
		returnList = []
		
		filteredDict = {k: v for k, v in self.coordList.items() if v["selected"] == 1}
		filteredList = [k for k,v in self.coordList.items() if v["selected"] == 1]
		# for k,v in filteredDict.items():
		for k in filteredList:
			returnList += [ str(k) ]
			
		return ",".join(returnList)
	
	
	def GetSelectedCoords(self):
	
		returnList = []
		
		filteredDict = {k: v for k, v in self.coordList.items() if v["selected"] == 1}
		for k,v in filteredDict.items():
			returnList += [ [ k , v["x"] , v["y"] , v["z"] ] ]
		return returnList
	
	### this returns the specified coordinates from the dictionary.
	def GetSpecifiedCoords(self, coords=[]):
		totalLen = len(self.coordList.items())
		returnList = []
		for i in coords:
			if i >= 0 and i < totalLen:
				returnList += [ [ 	self.coordList[i]["x"] , 
									self.coordList[i]["y"] , 
									self.coordList[i]["z"] ] ]
		return returnList
		
		
	def GetAvgCenterOfSelected(self , WS = False):
		
		xAvg = 0
		yAvg = 0
		zAvg = 0
		
		filteredDict = {k: v for k, v in self.coordList.items() if v["selected"] == 1}
		numSel = len(filteredDict)
		
		if numSel > 0:
			for k,v in filteredDict.items():
			
				xAvg += v["x"]
				yAvg += v["y"]
				zAvg += v["z"]
			
			xAvg /= numSel
			yAvg /= numSel
			zAvg /= numSel
			
			if WS == True:
				pos = parent.obj.worldTransform * tdu.Position( xAvg , yAvg , zAvg )
				xAvg,yAvg,zAvg = pos.x,pos.y,pos.z
			
			return [ xAvg , yAvg , zAvg ]
			
		else:
			return [ 0 , 0 , 0 ]
		
	def GetAvgSizeOfSelected(self):
		
		filteredDict = {k: v for k, v in self.coordList.items() if v["selected"] == 1}
		numSel = len(filteredDict)
		
		if numSel == 0:
			filteredDict = {k: v for k, v in self.coordList.items() if v["selected"] > 0}
			numSel = len(filteredDict)
		
		size = 0
		
		if numSel > 0:
			
			selCoords = []
			for k,v in filteredDict.items():
				selCoords += [ [v["x"] , v["y"] , v["z"]] ]
			
			selCoords_np = np.asarray(selCoords)
			min = np.amin(selCoords_np, axis=0)
			max = np.amax(selCoords_np, axis=0)
			size = max - min
			size = float(np.amax(max))
			
		return size
	
	
	def DeleteLastCoordAndSelect(self):
		lastIndex = len(self.coordList) - 1
		indexesToDelete = [ lastIndex ]

		self.coordList = { k:v for k,v in self.coordList.items() if k not in indexesToDelete }
		
		lastIndex = len(self.coordList) - 1
		if lastIndex >= 0:
			self.coordList[lastIndex]["selected"] = 1

		self.fixNumbering()
		return
		
	def DeleteSelectedCoords(self):

		# NOTE : we were having trouble using the del command to get rid of entries.. not sure why, maybe dependDict?
		# whatever, it was easy to just list comp the items we wanted to delete out of existance.. maybe less efficient?
		# not sure it will matter for this purpose though.
		self.coordList = { k:v for k,v in self.coordList.items() if v["selected"] == 0 }
		self.fixNumbering()
		return
		
	# after deleteing key/value pairs, this generates and returns
	# a new dictionary renumbering the keys indicies.
	def fixNumbering(self):
		newDict = {}
		i = 0
		for key, value in self.coordList.items():
			newDict[i] = value
			i += 1
		self.coordList = newDict
		return
	
	### all manner of selecting and deselecting coordinates.
	def DeleteAll(self):
		self.coordList.clear()
		return	
		
	def Select(self, indexList):
		self.DeselectAll()
		for i in indexList:
			self.coordList[i]["selected"] = 1
		# print(self.coordList)
		return
		
	def SelectLast(self):
		self.DeselectAll()
		# print( self.coordList )
		total = len(self.coordList.items())
		self.coordList[total-1]["selected"] = 1
		return

	def SelectAll(self):
		for key, value in self.coordList.items():
			value["selected"] = 1
		return
		
	def DeselectAll(self):
		for key, value in self.coordList.items():
			value["selected"] = 0
		return
		
	def InvertSelectAll(self):
		for key, value in self.coordList.items():
			value["selected"] = int(1 - value["selected"])
		return
					
	def SelectAdd(self, indexList):
		for i in indexList:
			self.coordList[i]["selected"] = 1
		return
		
	def SelectRemove(self, indexList):
		for i in indexList:
			self.coordList[i]["selected"] = 0
		return
		
	def SelectInvert(self, indexList):
		for i in indexList:
			self.coordList[i]["selected"] = 1 - self.coordList[i]["selected"]
		return
		
	def InsertCoord(self):
		'''
		This function takes two hull indicies and creates a 
		new hull inbetween these two, effectively subdividing that hull segment.
		'''
		
		if len( self.GetSelectedCoords() ) == 2:
		
			selIndicies = self.GetSelectedCoordIndiciesAsString()
			selIndicies = list(map(int,selIndicies.split(',')))
			iA = selIndicies[0]
			iB = selIndicies[1]
			
			if abs(iB - iA) == 1:
				
				cAvg = self.GetAvgCenterOfSelected()
				# print(iA,iB)
				
				for k,v in reversed(list(self.coordList.items())):
					# print(k,v)
					self.coordList[ k + int(k>=iB) ] = v
				
				self.DeselectAll()
				self.AddCoord( x = cAvg[0] , y = cAvg[1] , z = cAvg[2] , selected = 1 , i = iB , localSpace = True )
				
			else:
				op.NOTIFV2.Notify('Your two Hulls need to be sequentially next to each other to perform this operation.')
		
		else:
			
			op.NOTIFV2.Notify('You need to have exactly two Hulls selected to perform this operation.')
			
		self.fixNumbering()
		return
	
	### setting and adding / removing coordinates
	def AddCoord(self, x=0, y=0, z=0, u=0, v=0, selected=0, i=-1, localSpace=False):
		if(i == -1):
			i = len(self.coordList.items())
		
		if localSpace == False:
			# calculate world space to local space.
			newCoord = mod.matrixUtils.worldSpace_to_LocalSpace(parent.obj,x,y,z )
		else:
			newCoord = [x,y,z]
		
		
		self.coordList[i] = {
						"x":newCoord[0], 
						"y":newCoord[1], 
						"z":newCoord[2], 
						"u":u, 
						"v":v, 
						"selected":selected}

		self.fixNumbering()
		return


		
	def Set(self, i=0, key="x", val=0):
		self.coordList[i][key] = val
		return
		
		
	def SetSelected(self, key="x", val=0):
		
		for keyItr, value in self.coordList.items():
			if value["selected"] == 1:
				self.coordList[keyItr][key] = float(val)
			
		return
	
	# goes through all coordinates in storage and collects all the different names of channels in use at least once.
	def generateTableHeader(self):
		headerDict = {}
		counter = 0
		for key, value in self.coordList.items():
			for key2, value2 in value.items():
				if key2 not in headerDict:
					headerDict[key2] = counter
					counter += 1
		return sorted(headerDict.items(), key=lambda x: x[1])
		
	def WriteCoordsToTable(self):
		# print('hhhhh')
		
		# self.PrintCoords()
		
		# first, get ordered header. (note, order is not based on anything in particular.)
		headerDict = self.generateTableHeader()
		
		# build our header sub string.
		headerString = ""
		headerStringList = []
		for orderedItem in headerDict:
			headerStringList += [ orderedItem[0] ]
		
		# build our table string from the data in storage, and also order it by our header.
		tableString = ""
		tableStringList = []
		for key, value in self.coordList.items():
			rowStringList = []
			for orderedItem in headerDict:
				OrderedKey = orderedItem[0]
				OrderedValue = orderedItem[1]
				if OrderedKey in value:
					rowStringList += [ str(value[OrderedKey]) ]
				else:
					rowStringList += [ "-" ] # for now, just fill in the gaps with -'s. this is not permanent.
			tableStringList += [ "\t".join(rowStringList) ]
		headerString = "\t".join(headerStringList)
		tableString = "\n".join(tableStringList)
		fullBodyString = headerString + "\n" + tableString
		
		# write to table.
		t.text = fullBodyString
		
		
		DATABLOCK.par.Numhulls = len(self.coordList)
		hLen = self.ArcLen()
		DATABLOCK.par.Lenhulls = hLen
		DATABLOCK.par.Wirelen = hLen
		# '''
		return

	# shift selection forwards or backwards by provided amount.
	def ShiftSelection(self, shiftAmt = -1):
		
		# get length of coords list, for modulo.
		totalLen = len(self.coordList.items())
		
		# dicts are mutable, so we need a copy that won't change that we can reference.
		originalCopy = copy.deepcopy(self.coordList)
		
		# loop through our "live" coordList and re assign values from copy using modulo and 
		# our shift offset amount.
		for key, value in self.coordList.items():
			self.coordList[(key+shiftAmt)%totalLen]["selected"] = originalCopy[key]["selected"]
		
		return
	
	
	
	# Grows or shrinks the selection by x amount.
	def GrowShrinkSelection(self, GrowAmt = 1, direction = 1):
		
		for x in range(GrowAmt):
			
			# get length of coords list, for modulo.
			maxIndex = len(self.coordList.items()) - 1
			
			
			# if we are growing selection
			if direction == 1:
				# loop through our "live" coordList  and grow RISING edge
				for key, value in self.coordList.items():
					backOne = tdu.clamp(key - direction,0,maxIndex)
					if value["selected"] == 1:
						self.coordList[backOne]["selected"] = 1
				
				# loop through our "live" coordList  and grow FALLING edge
				for x in range(len(self.coordList.items()))[::-1]:
					forwardOne = tdu.clamp(x + direction,0,maxIndex)
					if self.coordList[x]["selected"] == 1:
						self.coordList[forwardOne]["selected"] = 1
			
			
			# if we are shrinking selection
			elif direction == -1:
				# loop through our "live" coordList and shrink RISING edge
				for x in range(len(self.coordList.items()))[::-1]:
					backOne = tdu.clamp(x - direction,0,maxIndex)
					if self.coordList[x]["selected"] == 0:
						self.coordList[backOne]["selected"] = 0
						
				# loop through our "live" coordList  and grow RISING edge
				for key, value in self.coordList.items():
					forwardOne = tdu.clamp(key + direction,0,maxIndex)
					if value["selected"] == 0:
						self.coordList[forwardOne]["selected"] = 0
				

			

		return
		
		
	def GetNumberOfHulls(self):
		
		return list(range(len(self.coordList)))
		
		
	
	def AutoProjectUvs(self, argsDict):
		# get some variables.
		Uvmode 			= argsDict['Uvmode']
		Axis 			= argsDict['Axis']
		Dim1 			= argsDict['Dim1']
		Dim2 			= argsDict['Dim2']
		Pos1 			= argsDict['Pos1']
		Pos2 			= argsDict['Pos2']
		Targetwidth 	= argsDict['Targetwidth']
		Targetheight 	= argsDict['Targetheight']
		Projector 		= argsDict['Projector']
		currentCoords 	= self.GetAllCoords()
		nDim1 = min(Dim1,Targetwidth) / Targetwidth # normlized dimensions.
		nDim2 = min(Dim2,Targetheight) / Targetheight
		nPos1 = Pos1 / Targetwidth # normlized offsets.
		nPos2 = Pos2 / Targetheight
		
		uvs = []
		
		# calculate the Hull world coords.
		worldCoords = []
		parentMat = parent.obj.worldTransform
		offsetPos = tdu.Position(0,0,0)
		for each in currentCoords:
			offsetPos[0] = each[0]
			offsetPos[1] = each[1]
			offsetPos[2] = each[2]
			newPos = parentMat * offsetPos
			worldCoords += [ [newPos[0],newPos[1],newPos[2]] ]
		
		if Uvmode == 'projector':
			f = op.geoHolder.findChildren( type=geometryCOMP , depth=1 )
			f = [x for x in f if x.par.Name.eval() == Projector]
			if len(f) > 0: # if we found a matching projector...
				pObj = f[0]
				if pObj.par.Pstyle.eval() == 'Ortho': # if projectors style == orthographic
					projCoords = []
					orthoWidth = pObj.par.Pscale.eval()
					
					projViewMat = pObj.worldTransform
					projViewMat.invert()
					
					offsetPos = tdu.Position(0,0,0)
					for each in worldCoords:
						offsetPos[0] = each[0]
						offsetPos[1] = each[1]
						offsetPos[2] = each[2]
						newPos = projViewMat * offsetPos
						
						s = orthoWidth/2
						projCoords += [ [ 
							(newPos[0]/s)*.5+.5 , 
							(newPos[1]/s)*.5+.5 , 
							(newPos[2]/s)*.5+.5 
							] ]
					worldCoords = projCoords
					
					# break out the two dims to U and V respectively.
					U = [ x[0] for x in worldCoords ]
					V = [ x[1] for x in worldCoords ]
					
					# zip and convert to list of lists.
					uvs = [ list(x) for x in list(zip(U,V)) ]
					
				else:
					op.NOTIFV2.Notify('Please change projector to orthographic, other styles not supported at this time.')
					
					
		else: # any other auto projection mode.
		
			# remove 1 dimension from the coords list ,depending on what we don't need.
			if Axis == 'x':
				worldCoords = [ [ each[2],each[1] ] for each in worldCoords]
			elif Axis == 'y':
				worldCoords = [ [ each[0],each[2] ] for each in worldCoords]
			elif Axis == 'z':
				worldCoords = [ [ each[0],each[1] ] for each in worldCoords]
			
			# break out the two dims to U and V respectively.
			U = [ x[0] for x in worldCoords ]
			V = [ x[1] for x in worldCoords ]

			# get the current min/max vals.
			U_Min , U_Max = min(U) , max(U)
			V_Min , V_Max = min(V) , max(V)
			
			# normalize to 0-1
			U = [ tdu.remap(x,U_Min,U_Max,0,1) for x in U ]
			V = [ tdu.remap(x,V_Min,V_Max,0,1) for x in V ]
			
			if Uvmode == 'fill':
				pass 
			elif Uvmode == 'fitbest':
				U_Dif = U_Max-U_Min 
				V_Dif = V_Max-V_Min
				maxDif = max( [ U_Dif,V_Dif ] )
				U_Max = U_Min + maxDif
				V_Max = V_Min + maxDif
			
			# remap to fill shape
			U = [ tdu.remap(x,0,1,0,nDim1)+nPos1 for x in U ]
			V = [ tdu.remap(x,0,1,0,nDim2)+nPos2 for x in V ]
			
			# zip and convert to list of lists.
			uvs = [ list(x) for x in list(zip(U,V)) ]
		
		
		if len(uvs) > 0:
			for i,uv in enumerate(uvs):
				self.Set( i=i , key='u' , val=uv[0] )
				self.Set( i=i , key='v' , val=uv[1] )
				
			self.WriteCoordsToTable()
		
		
		
	def GetHullInfo(self):
		
		returnList = []
		
		numHulls = len(self.GetNumberOfHulls())
		returnList += [ ['NumHulls',numHulls] ]
		
		hullArcLen = self.ArcLen()
		# print('get hull info', hullArcLen)
		returnList += [ ['HullLen',hullArcLen] ]
		
		# flatten the data into a single string.
		returnVal = ','.join( [":".join(map(str,x)) for x in returnList] )
		
		return returnVal
		
	
	def GetAllHulls(self):
		allCoords = []
		for k, v in self.coordList.items():
			allCoords += [ [v["x"] , v["y"] , v["z"]] ]
		# print(allCoords)
		return allCoords
		
		
	def ArcLen(self):
		allCoords = self.GetAllHulls()
		if len(allCoords) > 0:
			arcLen = self.calcArcLength(allCoords)
			arcLen = round(arcLen,3)
			return arcLen
		else:
			return 0
		
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
		
		
		
		
		