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
TDJ = op.TDModules.mod.TDJSON
import copy
import numpy as np
import yaml
import json
from collections.abc import Sequence

pixCoordsTable = op("pix_coords")
pixCoordsChop = op("pix_coords_CHOP")

pixRangesTable = op("pix_ranges")
pixRangesChop = op("pix_ranges_CHOP")

pixChansTable = op("pix_chans")

pixMasksTable = op("pix_masks")
pixMasksChop = op("pix_masks_CHOP")

pixSelectionTable = op("pix_selection")
pixSelectionChop = op("pix_selection_CHOP")


DATABLOCK = parent.obj.op('DATABLOCK')

VpModeChop = op.ViewPortUI.op("null_ViewportModeCHOP")

rangesIgnoreList = ['x', 'y', 'z', 'selected']

class Pix:
	"""
	Pix description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		
		# properties
		TDF.createProperty(self, 'NumPix', value=0, dependable=True, readOnly=False)
		TDF.createProperty(self, 'ArcLength', value=0, dependable=True, readOnly=False)
		
		# '''
		# stored items (persistent across saves and re-initialization):
		storedItems = [
			{'name': 'coordList', 'default': {0:{ 	'coords':{	0:{'x':{'val':0},'y':{'val':0},'z':{'val':0}}
														}, 
													'chans':{	'r':{'min':0, 'max':255},
																'g':{'min':0, 'max':255},
																'b':{'min':0, 'max':255}
														},
													'masks':{	
														}, 
													'selected':0
												}
											},  
									'property': True, 
									'dependable': False}]

		# print( storedItems )

		self.stored = StorageManager(self, ownerComp, storedItems, sync=True, locked=False)
		
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
		# NOTE WE may not need this anymore since we can get the entire structure stripped of dependDict using TD's functions?
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

	
	def GetPixDict(self, deep=False):
		# works well, but currently a bit slow cause deep copy is slow.
		if deep == False:
			return self.coordList.copy()
		else:
			return copy.deepcopy( self.coordList )

	def GetPixDict_V2(self):
		# debug('Has not had coordinate sets properly implemented...')
		# this is an attempt to make a more optimized version of GetPixDict()

		''' structure attempting to copy properly.
		{
		 0:{ 	'coords':{	'x':{'val':0},
							'y':{'val':0},
							'z':{'val':0}
					}, 
				'chans':{	'r':{'min':0, 'max':255},
							'g':{'min':0, 'max':255},
							'b':{'min':0, 'max':255}
					},
				'masks':{	
					}, 
				'selected':0
			}
		}
		'''
		# 4 levels deep, and accounts for non dictionary items at 3rd level.
		d = { k:{ k2:{ k3:{k4:v4 for (k4,v4) in v3.items()} for (k3,v3) in v2.items() } if isinstance(v2,dict) else v2 for (k2,v2) in v.items() } for (k,v) in self.coordList.items() }
		
		# print(d)

		return d
		
		
	def ReplacePixDict(self, PixDict):
		self.coordList = PixDict
		self.WriteCoordsToTable()
		# mod.globalFuncs.TraceFunctionCall()
		
		return
		
	def SlicePixDict(self, start=0, end=-1):
		end = len(d) if end == -1 else end
		self.coordList = {k:v for (k,v) in self.coordList.items() if k in range(start,end)}
		# mod.globalFuncs.TraceFunctionCall()
		return len(self.coordList)
		
	def CoordSetFetch(self , pixIndex , var , coordSetIndex):
		try:
			ret = self.coordList[pixIndex]['coords'][coordSetIndex][var]['val']
			return ret
		except:
			return 0
		
	def CoordSetMaskFetch(self , pixIndex , var , coordSetIndex):
		'''
		returns 1 if the entry was found, 0 if it wasn't.
		'''
		try:
			self.coordList[pixIndex]['coords'][coordSetIndex][var]['val']
			return 1
		except:
			return 0

	def ActiveCoordsetIndex(self):
		return parent.obj.par.Activecoordinateset.eval()-1

		
	def GetDictAsJson(self, coordsOnly = False , coordSetIndex=-1):
		# debug('Has not had coordinate sets properly implemented...')
		
		if coordSetIndex == -1:
			coordSetIndex = self.ActiveCoordsetIndex()


		returnItem = ''
		
		if coordsOnly == False:
			d = self.GetPixDict()
			
			d = self.strip_depend(d)
			d = self.format_extreme_floats(d)
			
			returnItem = json.dumps( d , indent=4 )
			
		elif coordsOnly == True:
			c = self.GetAllCoords(['x','y','z'], coordSetIndex)
			c = '\n'.join( [','.join(map(str,[round(y,4) for y in x])) for x in c] )
			returnItem = c
		return returnItem
		
	def LoadJsonAsDict(self, jsonStr = None):
		if jsonStr != None:
			d = json.loads(jsonStr)
			d = self.format_dict_keys_ints(d)
			self.ReplacePixDict(d)
		
		
	def GetDictAsYaml(self, coordsOnly = False , coordSetIndex=-1):
		# debug('Has not had coordinate sets properly implemented...')
		returnItem = ''
		
		if coordSetIndex == -1:
			coordSetIndex = self.ActiveCoordsetIndex()
		
		if coordsOnly == False:
			d = self.GetPixDict()
			returnItem = yaml.dump(d)
			
		elif coordsOnly == True:
			c = self.GetAllCoords(['x','y','z'], coordSetIndex)
			c = '\n'.join( [','.join(map(str,[round(y,4) for y in x])) for x in c] )
			returnItem = c
		return returnItem
		
	def LoadYamlAsDict(self, yamlStr = None):
		if yamlStr != None:
			d = yaml.load(yamlStr)
			self.ReplacePixDict(d)
			
	def PushNewCoords(self, tableFormattedStr = None, coordSetIndex=-1 ):
		# debug('Has not had coordinate sets properly implemented...')
		
		def PushTry(i,coord):
			try:
				self.coordList[i]['coords'][coordSetIndex]['x']['val'] = coord[0]
				self.coordList[i]['coords'][coordSetIndex]['y']['val'] = coord[1]
				self.coordList[i]['coords'][coordSetIndex]['z']['val'] = coord[2]
			except:
				self.coordList[i]['coords'][coordSetIndex] = { 'x':{'val':coord[0]} , 'y':{'val':coord[1]} , 'z':{'val':coord[2]} }

		if coordSetIndex == -1:
			coordSetIndex = self.ActiveCoordsetIndex()

		if tableFormattedStr != None:
			lines = tableFormattedStr.split('\n')
			data = [ [float(y) for y in x.split(',')] for x in lines]
			
			dictLen = len(self.coordList)
			listLen = len(data)
			
			# if the source coords and dictionary length are the same... simply replace the coord values.
			if listLen == dictLen:
				for i,coord in enumerate(data):
					PushTry(i,coord)
			
			# if user provided more coordinates than there are dict entries.. AND dict as at least 1 entry.
			elif listLen > dictLen and dictLen > 0:
				for i,coord in enumerate(data):
					if i < dictLen: # as long as we're within range of the dictionary, just set values
						PushTry(i,coord)

					else: # once we've gone beyond the range of the dictionary... deep copy last, and set coords.
						self.coordList[i] = copy.deepcopy( self.coordList[dictLen-1] )
						PushTry(i,coord)
			
			
			# if user provided more coordinates than there are dict entries.. AND dict as 0 entries.
			elif listLen > dictLen and dictLen == 0:
				for i,coord in enumerate(data):
					# print("i", i, listLen, dictLen)
					self.AddPixRaw(  x=coord[0] , y=coord[1] , z=coord[2] , xtraChans=['r','g','b'] , xtraMasks=[], selected=0 , i=i  )
					PushTry(i,coord)
						
			# if user provided more coordinates than there are dict entries..
			elif listLen < dictLen:
				for i,coord in enumerate(data):
					if i < dictLen: # as long as we're within range of the dictionary, just set values
						PushTry(i,coord)
						
				for x in range(listLen,dictLen):# delete the keys that come after.
					del self.coordList[x]

			self.WriteCoordsToTable()
		
	def CopyMaskFromPixDict(self, PixDict, extendMode='zero', masks=[], masksMode='max'):
		'''
		extendmode='zero' : pix masks beyond the amount in the source, will all be zero
		extendmode='cycle' : pix masks beyond the amount in the source, will repeat.
		
		masksMode='add' : will combine the current masks with the supplied using a max(src,trg) composite.
		masksMode='sub' : will combine the current masks with the supplied using a max(trg-src,0) composite.
		masksMode='intersect' : will combine the current masks with the supplied using a min(trg,src) composite.
		'''

		tLen = len( PixDict )
		
		i = 0
		for k,v in self.coordList.items():
			
			### extend mode ZERO
			if extendMode == 'zero':
				getAttempt = PixDict.get(k, None)
				
				if getAttempt != None:
					
					if len(masks): # if user provided masks, we should do additive or subtractive.
						for each in masks:
							doesMaskExist = self.coordList[k]['masks'].get(each,None)
							if doesMaskExist != None:
								
								if masksMode == 'add': # do a max operatiopn
									self.coordList[k]['masks'][each]['val'] = max( self.coordList[k]['masks'][each]['val'] , PixDict[i]['masks'][each]['val'] )
								elif masksMode == 'sub': # do a min operation
									# print('sub' )
									self.coordList[k]['masks'][each]['val'] = max( self.coordList[k]['masks'][each]['val'] - PixDict[i]['masks'][each]['val'] , 0 )
									
								elif masksMode == 'intersect': # do a min operation
									self.coordList[k]['masks'][each]['val'] = min( self.coordList[k]['masks'][each]['val'] , PixDict[i]['masks'][each]['val'] )
								
							else:
								self.coordList[k]['masks'][each] = {'val':0}
								self.coordList[k]['masks'][each]['val'] = PixDict[i]['masks'][each]['val']
					else: # otherwise, we're just copying the entire masks chunk blindly.
						self.coordList[k]['masks'] = PixDict[i]['masks']
				else:
					doesMaskExist = self.coordList[k]['masks'].get(each,None)
					if doesMaskExist != None:
						tmpDict = PixDict[tLen-1]['masks']
						for k2,v2 in tmpDict.items():
							tmpDict[k2]['val'] = 0
						self.coordList[k]['masks'] = tmpDict
			
			### extend mode CYCLE
			elif extendMode == 'cycle':
				
				for each in masks:
					doesMaskExist = self.coordList[k]['masks'].get(each,None)
					if doesMaskExist != None:
						if masksMode == 'add': # do a max operatiopn
							self.coordList[k]['masks'][each]['val'] = max( self.coordList[k]['masks'][each]['val'] , PixDict[i%tLen]['masks'][each]['val'] )
						elif masksMode == 'sub': # do a min operation
							self.coordList[k]['masks'][each]['val'] = max( self.coordList[k]['masks'][each]['val'] - PixDict[i%tLen]['masks'][each]['val'] , 0 )
							
						elif masksMode == 'intersect': # do a min operation
							self.coordList[k]['masks'][each]['val'] = min( self.coordList[k]['masks'][each]['val'] , PixDict[i%tLen]['masks'][each]['val'] )
							
		
			
			i += 1
		
		self.WriteCoordsToTable()
		
		
	def ReverseAllPix(self):
		newDict = {}
		myLen = len(self.coordList)
		for k in self.coordList.keys():
			newDict[ k ] = self.coordList[myLen-1-k]
		self.coordList = newDict
		# mod.globalFuncs.TraceFunctionCall()
		return
		
		
	### returns some basic info about the Fixture.
	### List of Chans.
	def GetChanInfo(self):
		
		returnVal = ""
		if len(self.coordList.items()) > 0:
			returnVal = []
		
			ChanList = []
			
			numChans = 0
			firstKey = list(self.coordList.keys())[0]
			for k,v in self.coordList[firstKey]['chans'].items():
				ChanList += [k]
				
			# flatten the data into a single string.
			returnVal = ','.join( sorted(ChanList) )
		
		if returnVal == "":
			returnVal = 'Empty'
		
		return returnVal
		
		
	def ArcLen(self , coordSetIndex=-1 ):
		# debug('Has not had coordinate sets properly implemented...')

		if coordSetIndex == -1:
			coordSetIndex = self.ActiveCoordsetIndex()

		allCoords = self.GetAllCoords(['x','y','z'], coordSetIndex)
		if len(allCoords) == 0:
			allCoords = [[0,0,0]]
		arcLen = self.calcArcLength(allCoords)
		arcLen = round(arcLen,3)
		return arcLen
		
	
	def PrintCoords(self):
		for key, value in self.coordList.items():
			dump = yaml.dump(value)
			print(key)
			print(dump)
			print('')
		return
	
	def DumpCoords(self):
		dump = yaml.dump(self.coordList)
		return dump
		
	def GetTotalNumberOfPix(self):
		return len( self.coordList )
		
	def GetSelectedCoords(self, coordsToProcess=['x','y','z'] , coordSetIndex=-1):
		# debug('Has not had coordinate sets properly implemented...')
		returnList = []
		if coordSetIndex == -1:
			coordSetIndex = self.ActiveCoordsetIndex()
		
		filteredDict = {k: v for k, v in self.coordList.items() if v["selected"] == 1}
		for k,v in filteredDict.items():
			
			thisSet = [k]
			for c in coordsToProcess:
				thisSet += [ self.CoordSetFetch(k,c,coordSetIndex) ]
			returnList += [ thisSet ]
		
		return returnList
		
		
	def GetSelectedIndicies(self):
	
		returnList = []
		
		for k,v in self.coordList.items():
			if v["selected"] == 1:
				returnList += [ k ]
		
		return returnList
		
		
	def GetAllCoords(self, coordsToProcess=['x','y','z'] , coordSetIndex=-1):
		# debug('Has not had coordinate sets properly implemented...')
		returnList = []

		if coordSetIndex == -1:
			coordSetIndex = self.ActiveCoordsetIndex()
		
		filteredDict = {k: v for k, v in self.coordList.items()}
		for k,v in filteredDict.items():
			thisSet = []
			for c in coordsToProcess:

				# thisSet += [ v["coords"][coordSetIndex][c]['val'] ] # OLD
				# item = v["coords"].get( coordSetIndex , {c:{'val':0}} )[c]['val']
				thisSet += [ self.CoordSetFetch(k,c,coordSetIndex) ]
				# thisSet += [ item ]

			returnList += [ thisSet ]
		
		return returnList
		
		
	def GetAvgCenterOfSelected(self, coordsToProcess=['x','y','z'], WS = False, coordSetIndex=-1):
		
		if coordSetIndex == -1:
			coordSetIndex = self.ActiveCoordsetIndex()
		# debug('Has not had coordinate sets properly implemented...')



		# create the dict to hold averages, then fill with for loop.
		avgs = {}
		for c in coordsToProcess:
			avgs[c] = 0
		
		# get just selected pix.
		filteredDict = {k: v for k, v in self.coordList.items() if v["selected"] == 1}
		numSel = len(filteredDict)
		
		# if we at least have 1 pix selected.
		if numSel > 0:
			for k,v in filteredDict.items():
				
				singleSet = []
				for c in coordsToProcess:
					# avgs[c] += v['coords'][c]['val']
					# avgs[c] += v['coords'].get( coordSetIndex , {c:{'val':0}} )[c]['val']
					avgs[c] += self.CoordSetFetch(k,c,coordSetIndex)
			
			returnList = []
			
			for c in coordsToProcess:
				returnList += [avgs[c] / numSel]
			
			if WS == True:
				pos = parent.obj.worldTransform * tdu.Position( returnList[0] , returnList[1] , returnList[2] )
				returnList[0],returnList[1],returnList[2] = pos.x,pos.y,pos.z
				
			return returnList
			
		else:
			return [0 for x in coordsToProcess]
	
	
	def InsertCoord(self):
		'''
		This function takes two pix indicies and creates a 
		new pix inbetween these two, effectively subdividing that pix segment.
		'''

		# debug('Has not had coordinate sets properly implemented...')
		# NOTE: since this is subdividing a set of two Pix, we should just subdivide between all available coordinate sets.
		
		if len( self.GetSelectedCoords() ) == 2:
			
			sel = self.GetSelectedCoords()
			selIndicies = self.GetSelectedIndicies()
			iA = selIndicies[0]
			iB = selIndicies[1]
			
			if abs(iB - iA) == 1:
				
				cAvg = self.GetAvgCenterOfSelected()
				masks = self.GetMaskList()
				
				for k,v in reversed(list(self.coordList.items())):
					self.coordList[ k + int(k>=iB) ] = v
				currentChans = list(self.coordList[ iB ]['chans'].keys())
				currentMasks = list(self.coordList[ iB ]['masks'].keys())
				
				self.DeselectAll()
				
				self.AddPixRaw(  x=cAvg[0] , y=cAvg[1] , z=cAvg[2] , xtraChans=currentChans , xtraMasks=currentMasks, selected=1 , i=iB  )
				
			else:
				op.NOTIFV2.Notify('Your two Pix need to be sequentially next to each other to perform this operation.')
		else:
			
			op.NOTIFV2.Notify('You need to have exactly two Pix selected to perform this operation.')
		
		return
	
	
	def GetAvgSizeOfSelected(self, coordsToProcess=['x','y','z'] , coordSetIndex=-1 ):
		# debug('Has not had coordinate sets properly implemented...')
		# if -1, means we fetch this dynamically.
		if coordSetIndex == -1:
			coordSetIndex = self.ActiveCoordsetIndex()

		filteredDict = {k: v for k, v in self.coordList.items() if v["selected"] == 1}
		numSel = len(filteredDict)
		
		if numSel == 0:
			filteredDict = {k: v for k, v in self.coordList.items() if v["selected"] > 0}
			numSel = len(filteredDict)
		
		size = 0
		
		if numSel > 0:
			
			selCoords = []
			for k,v in filteredDict.items():
			
				thisSet = []
				for c in coordsToProcess:
					thisSet += [ self.CoordSetFetch(k,c,coordSetIndex) ]
					
				selCoords += [ thisSet ]
			
			selCoords_np = np.asarray(selCoords)
			min_ = np.amin(selCoords_np, axis=0)
			max_ = np.amax(selCoords_np, axis=0)
			size = max_ - min_
			size = float(np.amax(max_))
			
		return size
		
		
	def GetCenterOfBounds( self, coordsToProcess=['x','y','z'] , coordSetIndex=-1 ):

		# debug('Has not had coordinate sets properly implemented...')

		# if -1, means we fetch this dynamically.
		if coordSetIndex == -1:
			coordSetIndex = self.ActiveCoordsetIndex()

		selCoords = []
		for k,v in self.coordList.items():
		
			thisSet = []
			for c in coordsToProcess:
				thisSet += [ self.CoordSetFetch(k,c,coordSetIndex) ]
				
			selCoords += [ thisSet ]
		
		selCoords_np = np.asarray(selCoords)
		min_ = np.amin(selCoords_np, axis=0)
		max_ = np.amax(selCoords_np, axis=0)
		avgCenter = (max_ + min_)/2
		
		m = parent.obj.localTransform
		s, r, t = m.decompose()
		PixCenter = [x for i,x in enumerate(avgCenter) ]
		
		returnDict = {}
		
		for i,each in enumerate(PixCenter):
			returnDict[coordsToProcess[i]] = each
		
		return returnDict
		
		
	def CenterPivot(self, coordsToProcess=['x','y','z'] , coordSetIndex=-1 ):
		
		debug('Has not had coordinate sets properly implemented...')

		# if -1, means we fetch this dynamically.
		if coordSetIndex == -1:
			coordSetIndex = self.ActiveCoordsetIndex()

		if self.GetTotalNumberOfPix() > 0:
		
			PixCenter = self.GetCenterOfBounds(coordsToProcess)
			
			PixCenterRel = op.sceneOutliner.mod.matrixUtils.relativeCoords( parent.obj,PixCenter['x'],PixCenter['y'],PixCenter['z'] )
			
			for k,v in self.coordList.items():
				for c in coordsToProcess:
					try:
						self.coordList[k]['coords'][coordSetIndex][c]['val'] = self.CoordSetFetch(k,c,coordSetIndex) - PixCenter[c]
					except:
						self.coordList[k]['coords'][coordSetIndex] = { 'x':{'val':0}, 'y':{'val':0}, 'z':{'val':0} }
						self.coordList[k]['coords'][coordSetIndex][c]['val'] = self.CoordSetFetch(k,c,coordSetIndex) - PixCenter[c]
			
			parent.obj.par.Tx = parent.obj.par.Tx.eval() + PixCenterRel[0]
			parent.obj.par.Ty = parent.obj.par.Ty.eval() + PixCenterRel[1]
			parent.obj.par.Tz = parent.obj.par.Tz.eval() + PixCenterRel[2]
		
			return PixCenter
			
		else:
			return None
	
	### this is poorly named. means delete last PIX and select.
	def DeleteLastCoordAndSelect(self):

		lastIndex = len(self.coordList) - 1
		indexesToDelete = [ lastIndex ]

		self.coordList = { k:v for k,v in self.coordList.items() if k not in indexesToDelete }
		# mod.globalFuncs.TraceFunctionCall()
		lastIndex = len(self.coordList) - 1
		if lastIndex >= 0:
			self.coordList[lastIndex]["selected"] = 1
		
		
		self.ArcLength = self.ArcLen() # assume default coordinate set.
		
		return
		
	def DeleteSelectedCoords(self):

		self.coordList = { k:v for k,v in self.coordList.items() if v["selected"] == 0 }
		# mod.globalFuncs.TraceFunctionCall()
		self.fixNumbering()

		self.ArcLength = self.ArcLen() # assume default coordinate set.
		
		return
		
	def fixNumbering(self):
		'''
		after deleteing key/value pairs, this generates and returns
		a new dictionary renumbering the keys indicies.
		'''
		newDict = {}
		i = 0
		for key, value in self.coordList.items():
			newDict[i] = value
			i += 1
		self.coordList = newDict
		# mod.globalFuncs.TraceFunctionCall()
		
		
		self.ArcLength = self.ArcLen() # assume default coordinate set.
		
		return
	
	def DeleteAll(self):
		'''
		all manner of selecting and deselecting coordinates.
		'''
		# mod.globalFuncs.TraceFunctionCall()
		self.coordList.clear()
		self.ArcLength = self.ArcLen() # assume default coordinate set.
		return	
		
	def Select(self, indexList):
		self.DeselectAll()
		for i in indexList:
			self.coordList[i]["selected"] = 1
		return
		
	def SelectLast(self):
		self.DeselectAll()
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
	
	
	def DeleteChan(self, chanName = None):
		
		# if chan name is provided as anything other than None.
		if chanName != None:
			
			# iterate through all items in coordsList.
			for key, value in self.coordList.items():
				
				# try and retrieve a chan by the provided name.
				# will not fail but return None if none exists by that name.
				foundVal = value['chans'].get(chanName, None)
				
				# if we found a chan, delete it.
				if foundVal != None:
					del self.coordList[key]['chans'][chanName]
								
		
		return
					
					
	def AddChan(self, chanName = None):
		
		# if chan name is provided as anything other than None.
		if chanName != None:
			
			# iterate through all items in coordsList.
			for key, value in self.coordList.items():
				# print(key,value)
				self.coordList[key]['chans'][chanName] = {'min':0, 'max':255}
				
				
		
		return
	
	
	def AddCoord(self, x=0, y=0, z=0, r=1, g=1, b=1, selected=0, i=-1 , coordSetIndex=-1):
		'''
		setting and adding / removing coordinates
		more of a predefined function for adding rgb pixels.
		'''

		# if -1, means we fetch this dynamically.
		if coordSetIndex == -1:
			coordSetIndex = self.ActiveCoordsetIndex()

		# debug('Has not had coordinate sets properly implemented...')

		if(i == -1):
			i = len(self.coordList.items())
		
		# calculate world space to local space.
		newCoord = op.sceneOutliner.mod.matrixUtils.worldSpace_to_LocalSpace(parent.obj,x,y,z )
		
		self.coordList[i] = {	'coords':{},'masks':{},'chans':{},'selected':selected}
		self.coordList[i]['coords'][coordSetIndex] = { 'x':{'val':newCoord[0]} , 'y':{'val':newCoord[1]} , 'z':{'val':newCoord[2]} }
		
		self.ArcLength = self.ArcLen(coordSetIndex)
		
		curChans = set(parent.obj.par.Chanorder.eval().split(','))
		chanInfo = set(self.GetChanInfo().split(','))
		
		allChans = list(chanInfo.union(curChans))
		allChans = [x for x in allChans if x != '']
		
		# if allChans ONLY contains r/g/b names then we can override the order so that it is r-g-b instead of b-g-r
		if len(allChans) == 3 and len(set(['r','g','b']).difference(set(allChans))) == 0:
			allChans = ['r','g','b']
		
		allChans = ','.join(allChans)
		parent.obj.par.Chanorder = allChans
		
		return
		
		
	
	def AddPix(self, x=0, y=0, z=0, xtraChans=[], selected=0, i=-1 , coordSetIndex=-1):
		'''
		setting and adding / removing PIX type coordinates - with variable chans.
		'''

		# if -1, means we fetch this dynamically.
		if coordSetIndex == -1:
			coordSetIndex = self.ActiveCoordsetIndex()

		# debug('Has not had coordinate sets properly implemented...')

		if(i == -1):
			i = len(self.coordList.items())
		
		
		# add the default pix template, we'll iterate through custom chans next.

		self.coordList[i] = {'coords':{},'masks':{},'chans':{},'selected':selected}
		self.coordList[i]['coords'][coordSetIndex] = { 'x':{'val':x} , 'y':{'val':y} , 'z':{'val':z} }

		# iterate through custom chans, and add their default style variables.
		for chan in xtraChans:
			self.coordList[i]['chans'][chan] = {'min':0, 'max':255}
		
		self.ArcLength = self.ArcLen()
		return
		
		
	def AddPixRaw(self, x=0, y=0, z=0, xtraChans=[], xtraMasks=[], selected=0, i=-1, createInWorldSpace=False , coordSetIndex=-1 ):
		'''
		setting and adding / removing PIX type coordinates - with variable chans.
		'''
		# debug('Has not had coordinate sets properly implemented...')


		# if -1, means we fetch this dynamically.
		if coordSetIndex == -1:
			coordSetIndex = self.ActiveCoordsetIndex()

		if(i == -1):
			i = len(self.coordList.items())

			if createInWorldSpace == True:
				newCoord = op.sceneOutliner.mod.matrixUtils.worldSpace_to_LocalSpace(parent.obj,x,y,z )
				x,y,z = newCoord

		if i not in self.coordList.keys():
			self.coordList[i] = {'coords':{},'masks':{},'chans':{},'selected':selected}
		
		self.coordList[i]['coords'][coordSetIndex] = { 'x':{'val':x} , 'y':{'val':y} , 'z':{'val':z} }
			
		# iterate through custom chans, and add their default style variables.
		for chan in xtraChans:
			self.coordList[i]['chans'][chan] = {'min':0, 'max':255}
		
		# iterate through custom masks, and add their default style variables.
		for mask in xtraMasks:
			self.coordList[i]['masks'][mask] = {'val':1}

		return

		
		
	def SetSelectedCoordinates(self, key='x', val=0 , coordSetIndex=-1):
		# debug('Has not had coordinate sets properly implemented...')

		# if -1, means we fetch this dynamically.
		if coordSetIndex == -1:
			coordSetIndex = self.ActiveCoordsetIndex()

		for keyItr, value in self.coordList.items():
				if value["selected"] == 1:
					try:	
						self.coordList[keyItr]['coords'][coordSetIndex][key]['val'] = val
					except:
						self.coordList[keyItr]['coords'][coordSetIndex] = {'x':{'val':0}, 'y':{'val':0}, 'z':{'val':0}}
						self.coordList[keyItr]['coords'][coordSetIndex][key]['val'] = val
					
					


	def Set(self, i=0, key="x", val=0 , coordSetIndex=-1):
		
		# if -1, means we fetch this dynamically.
		if coordSetIndex == -1:
			coordSetIndex = self.ActiveCoordsetIndex()

		if key in ['selected']:
			# if the param is not a dict, we can set it directly.
			if not isinstance(self.coordList[i][key],dict):
				self.coordList[i][key] = val
			
			# if it is a dict, we need to set it's "state" member explicitly.
			else:
				self.coordList[i][key]['state'] = val
		
		elif key in ['x', 'y', 'z']:
			try:
				self.coordList[i]['coords'][coordSetIndex][key]['val'] = val
			except:
				self.coordList[i]['coords'][coordSetIndex] = {'x':{'val':0}, 'y':{'val':0}, 'z':{'val':0}}
		
		else:
			debug('Whoops! this method is no longer suitable for key type: ', key)
		
		
		
		return
		

	def SetRangeSelected(self, key=None, min_=None, max_=None):
		'''
		This function sets the range of a chan. 
		'''
		for keyItr, value in self.coordList.items():
			# if pix selected.
			if value["selected"] == 1:
				
				self.SetRange(keyItr, key, min_, max_)
		
		
		return
		
		
	def NudgeRangeSelected(self, key=None, subKey=None, amt=None):
		'''
		This function nudges one of the components of the range of a chan. 
		'''
		for keyItr, value in self.coordList.items():
			# if pix selected.
			if value["selected"] == 1:
				self.coordList[keyItr]['chans'][key][subKey] = tdu.clamp( value['chans'][key][subKey] + amt , 0 , 255 )
				
		
		return
		
		
	def SetRange(self, i=0, key=None, min_=None, max_=None):
		if key != None:
			if min_ != None:
				self.coordList[i]['chans'][key]['min'] = tdu.clamp( min_ , 0 , 255 )
			if max_ != None:
				self.coordList[i]['chans'][key]['max'] = tdu.clamp( max_ , 0 , 255 )
		
		
		return
		
		
	def DumpStorageToTextDat(self):
		op('dictDump').text = TDJ.jsonToText(self.coordList)
		return


	### will generate a non duplicates list of header names, sorted alphabetically.
	def generateHeader(self, subDictName):
		labels = []
		if len( self.coordList.keys() ):
			if subDictName == 'coords':
				firstCoordSet = min(self.coordList[0][subDictName].keys())
				labels += list(self.coordList[0][subDictName][firstCoordSet].keys())
				labels = sorted(list(set(labels)))
			else:
				labels += list(self.coordList[0][subDictName].keys())
				labels = sorted(list(set(labels)))

		return labels
	
	
	def WriteCoordsToTable(self, mode=['ALL']):
		'''
		This function gathers all the Pix info from the master dictionary,
		and parses it down into data suitable for several dat tables.
		You can provide an alternate mode(s) if you're trying to do more efficient operations
		like update x/y/z coordinates only.
		mode='ALL' (updates everything, this is the default)
		mode='XYZ' (updates coordinates only)
		mode='RANGES' (updates ranges only)
		mode='MASKS' (updates masks only)
		mode='CHANS' (updates chans only)
		mode='SEL' (updates selection only)
		'''

		# debug('Has not had coordinate sets properly implemented...')
		# NOTE: this MAY not need the coordinateSetIndex argument since we likely want to write out whatever we have all the time,
		# when the mode is set to something that includes coordinates.....

		# debug('Writing Coords to Table')

		if len( self.coordList.items() ) > 0:
			
			if len({ 'ALL', 'XYZ' }.intersection( set(mode) )) > 0:

				# gather, build, then write the coords table.
				namesList = self.generateHeader('coords')

				# optional sort
				SORT_ORDER = {"x": 0, "y": 1, "z": 2, "w": 3}
				namesList.sort( key=lambda val: SORT_ORDER[val] )

				# build up 2d list we will write to table DAT.

				coordList0 = [ [ self.CoordSetFetch(k,name,0) for name in namesList ] for k,v in self.coordList.items() ]
				coordList1 = [ [ self.CoordSetFetch(k,name,1) for name in namesList ] for k,v in self.coordList.items() ]
				coordList2 = [ [ self.CoordSetFetch(k,name,2) for name in namesList ] for k,v in self.coordList.items() ]
				coordList3 = [ [ self.CoordSetFetch(k,name,3) for name in namesList ] for k,v in self.coordList.items() ]

				maskList0 = [ self.CoordSetMaskFetch(k,'x',0) for k,v in self.coordList.items() ]
				maskList1 = [ self.CoordSetMaskFetch(k,'x',1) for k,v in self.coordList.items() ]
				maskList2 = [ self.CoordSetMaskFetch(k,'x',2) for k,v in self.coordList.items() ]
				maskList3 = [ self.CoordSetMaskFetch(k,'x',3) for k,v in self.coordList.items() ]

				coordListT = [
					list(map(list, zip(*coordList0))),
					list(map(list, zip(*coordList1))),
					list(map(list, zip(*coordList2))),
					list(map(list, zip(*coordList3))),
				]

				# send data to script CHOP.
				pixCoordsChop.clear()
				pixCoordsChop.numSamples = len(coordList0)

				for j in range(4): # 4 max coord sets for now.
					suffix = str(j)
					for i,each in enumerate(namesList):
						c = pixCoordsChop.appendChan(each+suffix)
						c.vals = coordListT[j][i]

				# write out the utilization masks to W. we'll use these throughout where we need to know if a coord is intentionally 0,0,0 or if it's a null coord.
				c = pixCoordsChop.appendChan('w0')
				c.vals = maskList0
				c = pixCoordsChop.appendChan('w1')
				c.vals = maskList1
				c = pixCoordsChop.appendChan('w2')
				c.vals = maskList2
				c = pixCoordsChop.appendChan('w3')
				c.vals = maskList3

			
			if len({ 'ALL', 'CHANS' }.intersection( set(mode) )) > 0:
				#### leaving this as table dat, since the data requirements are slightly dif.
				# gather, build, then write the chans table.
				chansList = self.generateHeader('chans')
				pixChansTable.text = '\t'.join(chansList)
			

			if len({ 'ALL', 'RANGES' }.intersection( set(mode) )) > 0:
				
				chansList = self.generateHeader('chans')
				rangesNameList = [ [name+'_min',name+'_max'] for name in chansList ]
				rangesNameList = [ y  for x in rangesNameList for y in x ]

				# build up 2d list we will write to table DAT.
				fullList = [ 
								# [ v['chans'][name]['min'] for name in chansList ] +
								# [ v['chans'][name]['max'] for name in chansList ]
								[ v['chans'].get( name , {"max": 255,"min": 0} )['min'] for name in chansList ] +
								[ v['chans'].get( name , {"max": 255,"min": 0} )['max'] for name in chansList ]
									for k,v in self.coordList.items() 
							]
				
				# transpose list.
				fullListT = list(map(list, zip(*fullList)))

				# send data to script CHOP.
				pixRangesChop.clear()
				pixRangesChop.numSamples = len(fullList)
				for i,each in enumerate(rangesNameList):
					c = pixRangesChop.appendChan(each)
					c.vals = fullListT[i]

			
			if len({ 'ALL', 'MASKS' }.intersection( set(mode) )) > 0:

				namesList = self.generateHeader('masks')

				# build up 2d list we will write to table DAT.
				# this is wrong, didn't acomodate situations where the mask was not there.
				# fullList = [ [ v['masks'][name]['val'] for name in namesList ] for k,v in self.coordList.items() ]
				
				fullList = [ [ v['masks'].get(name,{'val':0})['val'] for name in namesList ] for k,v in self.coordList.items() ]


				
				# transpose list.
				fullListT = list(map(list, zip(*fullList)))

				# send data to script CHOP.
				pixMasksChop.clear()
				pixMasksChop.numSamples = len(fullList)
				for i,each in enumerate(namesList):
					c = pixMasksChop.appendChan(each)
					c.vals = fullListT[i]
			

			if len({ 'ALL', 'SEL' }.intersection( set(mode) )) > 0:

				namesList = ['selected']

				# build up 2d list we will write to table DAT.
				fullList = [ [ v[name] for name in namesList ] for k,v in self.coordList.items() ]
				
				# transpose list.
				fullListT = list(map(list, zip(*fullList)))

				# send data to script CHOP.
				pixSelectionChop.clear()
				pixSelectionChop.numSamples = len(fullList)
				for i,each in enumerate(namesList):
					c = pixSelectionChop.appendChan(each)
					c.vals = fullListT[i]
			

			# write some data to the datablock obj about our Pix.
			DATABLOCK.par.Lenpix = self.ArcLen()# assume default coordinate set.

		else:
			recurseScriptDat = op('recurseForceCookScriptChops')
			pixCoordsChop.clear()
			pixRangesChop.clear()
			pixMasksChop.clear()
			pixSelectionChop.clear()
			recurseScriptDat.run( [pixCoordsChop,pixRangesChop,pixMasksChop,pixSelectionChop,pixChansTable] )

		DATABLOCK.par.Clippedgenerators = ''
		op.Viewport.par.Fixturesaredirty = 1

		return 
		
		

	def ShiftSelection(self, shiftAmt = -1):
		'''
		shift selection forwards or backwards by provided amount.
		'''
		# get length of coords list, for modulo.
		totalLen = len(self.coordList.items())
		
		# dicts are mutable, so we need a copy that won't change that we can reference.
		originalCopy = copy.deepcopy(self.coordList)
		
		# loop through our "live" coordList and re assign values from copy using modulo and 
		# our shift offset amount.
		for key, value in self.coordList.items():
			self.coordList[(key+shiftAmt)%totalLen]["selected"] = originalCopy[key]["selected"]
		
		return
	
	
	
	def GrowShrinkSelection(self, GrowAmt = 1, direction = 1):
		'''
		Grows or shrinks the selection by x amount.
		'''
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
		
	def PixToWorldSpace(self, sourceDat, destDat):
		
		parentMat = parent.obj.worldTransform
		offsetPos = tdu.Position(0,0,0)
		
		resultList = []

		for row in sourceDat.rows()[1::]:
			x = float(row[0].val)
			y = float(row[1].val)
			z = float(row[2].val)
			
			offsetPos[0] = x
			offsetPos[1] = y
			offsetPos[2] = z
			
			newPos = parentMat * offsetPos
			
			lineString = "%f\t%f\t%f"%(newPos[0],newPos[1],newPos[2])
			resultList += [ lineString ]
		
		finalStr = "\r\n".join(resultList)
		destDat.text = finalStr
		
		return
		
	def GetPixDictAsWorldSpace(self , optionalWorldSpaceMatrix = None, coordSetIndex=-1):
		'''
		This function returns the entire Pix sub structure as it is, 
		but with the coordinates of each pix in world space.
		'''

		# debug('Has not had coordinate sets properly implemented...')

		# if -1, means we fetch this dynamically.
		if coordSetIndex == -1:
			coordSetIndex = self.ActiveCoordsetIndex()

		# NOTE - this should probably be implemented for all coordinate sets all the time.
		
		if optionalWorldSpaceMatrix == None:
			parentMat = parent.obj.worldTransform
		else:
			parentMat = optionalWorldSpaceMatrix
		
		
		offsetPos = tdu.Position(0,0,0)
		newDict = {}

		for k, v in self.coordList.items():
			offsetPos[0] = self.CoordSetFetch(k,'x',coordSetIndex)
			offsetPos[1] = self.CoordSetFetch(k,'y',coordSetIndex)
			offsetPos[2] = self.CoordSetFetch(k,'z',coordSetIndex)
			
			newPos = parentMat * offsetPos
			
			newDict[k] = copy.deepcopy(v)
			
			try:
				newDict[k]['coords']['x']['val'] = newPos.x
				newDict[k]['coords']['y']['val'] = newPos.y
				newDict[k]['coords']['z']['val'] = newPos.z
			except:
				newDict[k][coordSetIndex] = {'x':{'val':0}, 'y':{'val':0}, 'z':{'val':0}}
				newDict[k]['coords']['x']['val'] = newPos.x
				newDict[k]['coords']['y']['val'] = newPos.y
				newDict[k]['coords']['z']['val'] = newPos.z
			
		return newDict
		
		
	def WorldSpacePixData(self , coordSetIndex=-1):
		'''
		this function returns some useful info about the Pix in this fixture.
		namely, the min and max bounds of the x/y/z dims for use elsewhere.
		NOTE: this returns the world space position.
		'''

		# debug('Has not had coordinate sets properly implemented...')

		# if -1, means we fetch this dynamically.
		if coordSetIndex == -1:
			coordSetIndex = self.ActiveCoordsetIndex()

		parentMat = parent.obj.worldTransform
		offsetPos = tdu.Position(0,0,0)
		
		resultList = []

		for k, v in self.coordList.items():
			
			x = self.CoordSetFetch(k,'x',coordSetIndex)
			y = self.CoordSetFetch(k,'y',coordSetIndex)
			z = self.CoordSetFetch(k,'z',coordSetIndex)
			offsetPos[0] = x
			offsetPos[1] = y
			offsetPos[2] = z
			newPos = parentMat * offsetPos
			resultList += [ list(newPos) ]
		
		
		return resultList
		
	
	
	def DeviceID____________________________(self):
		val = -1
		try:
			val = parent.obj.par.Deviceid.eval()
		except:
			try:
				val = parent.obj.inputCOMPs[0].par.Deviceid.eval()
			except:
				try:
					val = parent.obj.inputCOMPs[0].inputCOMPs[0].par.Deviceid.eval()
				except:
					val = 0

		return val
		
		
		
		
		
	####################### START MASK FUNCTIONS HERE ########################## 
	
	# reset the masks dict inside each Pix to an empty dict.
	# this erases all masks.
	def ResetMasks(self):
		
		
		# iterate through all items in coordsList.
		for key, value in self.coordList.items():
			self.coordList[key]['masks'] = {}
			
		return
		
		
	
	def DeleteMask(self, maskName = None):
		
		# if chan name is provided as anything other than None.
		if maskName != None:
			
			# iterate through all items in coordsList.
			for key, value in self.coordList.items():
				
				# try and retrieve the masks dict. if it's not there, we get None.
				MaskDict = value.get('masks', None)

				
				# if there was a mask dict.
				if MaskDict != None:
					# print(MaskDict)
					# try and retrieve a chan by the provided name.
					# will not fail but return None if none exists by that name.
					foundMask = MaskDict.get(maskName, None)

					# if we found a chan, delete it.
					if foundMask != None:

						del self.coordList[key]['masks'][maskName]
						# pass
						
		return
					
					
	def AddMask(self, maskName = None, maskValue = None):
		
		# if chan name is provided as anything other than None.
		if maskName != None:
			
			maskName2 = tdu.legalName( maskName )
			if maskName2 != maskName:
				op.NOTIFV2.Notify('The name entered was not valid, it was converted to: %s'%(maskName2))
			# iterate through all items in coordsList.
			for key, value in self.coordList.items():
				selected = int(self.coordList[key]['selected'])
				if maskValue == None:
					finalValue = selected
				else:
					finalValue = maskValue
				
				# try and retrieve the masks dict. if it's not there, we get None.
				MaskDict = value.get('masks', None)
				
				# if there was a mask dict.
				if MaskDict != None:
			
					# add the new mask item to the masks dict if it existed already, set mask value to 1.
					self.coordList[key]['masks'][maskName2] = {'val':finalValue}
				
				# if mask dict did not exist, we probably still want to add the mask, we just have a bit more work to do.
				else:
					
					# make masks dict first, then add our mask to it and set to 1.
					self.coordList[key]['masks'] = {}
					self.coordList[key]['masks'][maskName2] = {'val':finalValue}
					

		return
		
	
	def SetMaskOnSelected_________________________________________(self, maskName = None, maskValue=1):
		
		# if chan name is provided as anything other than None.
		if maskName != None:
		
			for k,v in self.coordList.items():
				if v["selected"] == 1:
				
					# try and retrieve the masks dict. if it's not there, we get None.
					MaskDict = v.get('masks', None)
					
					# if there was a mask dict.
					if MaskDict != None:
			
						# add the new mask item to the masks dict if it existed already, set mask value to 1.
						self.coordList[k]['masks'][maskName] = {'val':maskValue}
				else:
					self.coordList[k]['masks'][maskName] = {'val':0}
		return		
	
	def SetMaskOnSelected_V2(self, maskName = None, maskValue=1):
		
		# if chan name is provided as anything other than None.
		if maskName != None:
		
			for k,v in self.coordList.items():

				setMask = v["selected"] == 1 or int(VpModeChop['ObjectEditMode']) == 1

				if setMask:
				
					# try and retrieve the masks dict. if it's not there, we get None.
					MaskDict = v.get('masks', None)
					
					# if there was a mask dict.
					if MaskDict != None:

						MaskDict[maskName] = {'val':maskValue}
			
						# add the new mask item to the masks dict if it existed already, set mask value to 1.
						# self.coordList[k]['masks'][maskName] = {'val':maskValue}
						self.coordList[k]['masks'] = MaskDict
				
				# else:
					# self.coordList[k]['masks'][maskName] = {'val':0}
		return
		
	def SetMaskOnSingle(self, i=0, maskName = None, maskValue=1):
		
		# if chan name is provided as anything other than None.
		if maskName != None:
			self.coordList[i]['masks'][maskName]['val'] = maskValue
		
		return
		
		
	def SetChanOnSingle(self, i=0, chanName = None, chanValue=1):
		
		# if chan name is provided as anything other than None.
		if chanName != None:
			
			self.coordList[i]['chans'][chanName]['min'] = 0
			self.coordList[i]['chans'][chanName]['max'] = int(255 * chanValue)
		
		return
		
	def InvertMaskOnSelected(self, maskName = None):
		
		# if chan name is provided as anything other than None.
		if maskName != None:
		
			for k,v in self.coordList.items():
				if v["selected"] == 1:
				
					# try and retrieve the masks dict. if it's not there, we get None.
					MaskDict = v.get('masks', None)
					
					# if there was a mask dict.
					if MaskDict != None:
			
						# add the new mask item to the masks dict if it existed already, set mask value to 1.
						self.coordList[k]['masks'][maskName]['val'] = 1 - self.coordList[k]['masks'][maskName]['val']
						
	
	def GetMaskList(self):
		result = list(set([mask for maskSet in self.coordList.values() for mask in maskSet['masks'].keys()]))
		return result
		
	def GetChansList(self):
		result = list(set([mask for maskSet in self.coordList.values() for mask in maskSet['chans'].keys()]))
		return result
		
	
	def UpdateFixtureDimsOnDatablock_______________________________(self):
		
		return
		
		
						
	### 
	def calcArcLength(self, coordList ):
		'''
		helper util, calculated the arc length given a set of coordinates.
		NOTE the argument coordList is not the standard dictionary, but rather a list of xyz coords.(I think?)
		'''

		# print( coordList )
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
		
			
	def findByKey____________________(key, dictionary): # pretty fast, not currently in use.
		for k, v in dictionary.items():
			if k == key:
				yield v
			elif isinstance(v, dict):
				for result in findByKey(key, v):
					yield result
					
	def gen_dict_extract(key, var): # a bit faster
		if hasattr(var,'items'):
			for k, v in var.items():
				if k == key:
					yield v
				if isinstance(v, dict):
					for result in gen_dict_extract(key, v):
						yield set(result.keys())