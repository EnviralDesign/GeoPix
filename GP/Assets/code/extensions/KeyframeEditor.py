'''
ANIMATION EDITOR
'''

import copy 
from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions

class Helper:


	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp

		self.StartStopChop = self.ownerComp.op('null_startStop')

		ownerComp.par.w = 1000
		ownerComp.par.h = 500
		op('Data_Entry').par.w = 200
		op('win').par.borders = False
		# parent.helper.op('curveEditor/geo_dots').pickable  = True

		f = parent.helper.op('curveEditor').findChildren(name='geo_dots', depth=2, maxDepth=2)
		for each in f:
			each.pickable = False


	def RESET(self):

		self.__init__(self.ownerComp)

		return


		
	def Launch(self, target=None, parName = None, targetChannelName=None):
		# parent().display

		parent.helper.op('win').par.winoffsety = -(parent.helper.height / 2) + (25/2)
	
		#parent.UberGui.fetch('Widget').resetDestParsToDefault()
		parent.helper.par.Ops = target
		parent.helper.par.Par = parName
		# print('s')
		# self.LoadRampIntoUi()
		
		if parent.helper.op('win').isOpen == False:
			parent.helper.op('win').par.winopen.pulse()

		self.EnableKeyPicking()

		parent.helper.op('win').setForeground()

		self.SelectChannelInGui(targetChannelName)
	
		return

	def SelectChannelInGui(self, targetChannelName):

		allChanNames = self.GetAllChanNames()
		if targetChannelName in allChanNames:
			parent.helper.par.Activechannels = [ allChanNames.index(targetChannelName) ]
		else:
			parent.helper.par.Activechannels = []
		
		
	def Close(self):
	
		parent.helper.op('win').par.winclose.pulse()

		op.perform.setForeground()
		
		return


	def get_keys(self):

		targetOp = parent.helper.par.Ops.eval()
		parName = parent.helper.par.Par.eval()
		if hasattr( targetOp.par , parName ):
			foundPar = getattr( targetOp.par , parName )
			KeysList = foundPar.eval()
			return KeysList
		else:
			op.NOTIFV2.Notify('Could not get keys from object.. please close and reload the Animation Editor.')
			return None
		return

	def Get_Keys(self):

		return self.get_keys()


	def get_unDeletableChans(self):

		targetOp = parent.helper.par.Ops.eval()
		parName = 'Permchans'
		if hasattr( targetOp.par , parName ):
			foundPar = getattr( targetOp.par , parName )
			chansList = foundPar.eval().split(' ')
			return chansList
		else:
			# op.NOTIFV2.Notify('Could not get per from object.. please close and reload the Animation Editor.')
			return []
		return


	def get_activeChans(self):
		return parent.helper.par.Activechannels.eval()

	def ActiveChans(self):
		return self.get_activeChans()

	def ActiveChanNames(self):
		activeChanIndicies = self.get_activeChans()
		activeChanNames = self.ChanIndiciesToNames(activeChanIndicies)
		return activeChanNames

	def ChanIndiciesToNames(self, chanList):
		keys = self.get_keys()
		orderedChanNames = self.GetAllChanNames()

		retVal = []

		for each in chanList:
			# if each in orderedChanNames:
			if each < len(orderedChanNames):
				retVal += [ orderedChanNames[each] ]
		return retVal

	def GetAllChanNames(self):
		retVal = []
		for each in self.get_attribute('id'):
			if each not in retVal:
				retVal += [ each ]

		return retVal


	def set_keys(self, keysList):

		assert isinstance(keysList,list),'Keylist should be a list of dictionary entries.'

		targetOp = parent.helper.par.Ops.eval()
		parName = parent.helper.par.Par.eval()
		if hasattr( targetOp.par , parName ):
			foundPar = getattr( targetOp.par , parName )
			foundPar.val = keysList
			return True
		else:
			op.NOTIFV2.Notify('Could not set keys to object.. please close and reload the Animation Editor.')
			return False
		return


	def Get_chans(self):

		# assert isinstance(chansDict,dict),'Chandict should be a dictionary of entries.'

		targetOp = parent.helper.par.Ops.eval()
		parName = 'Chans'
		if hasattr( targetOp.par , parName ):
			foundPar = getattr( targetOp.par , parName )
			return foundPar.eval()
		else:
			op.NOTIFV2.Notify('Could not get chans from object.. please close and reload the Animation Editor.')
			return None
		return


	def Set_chans(self, chansDict):

		assert isinstance(chansDict,dict),'Chandict should be a dictionary of entries.'
		# print(chansDict)
		targetOp = parent.helper.par.Ops.eval()
		parName = 'Chans'
		if hasattr( targetOp.par , parName ):
			foundPar = getattr( targetOp.par , parName )
			foundPar.val = chansDict
			return True
		else:
			op.NOTIFV2.Notify('Could not set chans to object.. please close and reload the Animation Editor.')
			return False
		return

	def isKeyActive(self, keyid):
		ActiveChansDat = parent.helper.op('ACTIVE_CHANNELS')
		return ActiveChansDat[keyid,'id'] != None

	def isKeyInChannel(self, keyid, chanIndex):
		ActiveChansDat = parent.helper.op('ACTIVE_CHANNELS')
		keyidInt = int(ActiveChansDat[keyid,'id']) if ActiveChansDat[keyid,'id'] != None else -1
		return keyidInt-1 == chanIndex

	def getFirstKeyIndexOfEachChan(self):
		keys = self.get_keys()

		minX = {}
		minIndex = {}
		for i,key in enumerate(keys):
			v = minX.get(key['id'],9999999)
			if key['x'] < v:
				minX[key['id']] = key['x']
				minIndex[key['id']] = i

		return minIndex

	# def get_activeKeys(self):
	# 	KeysList = self.get_keys()
	# 	selectedKeys = [key for i,key in enumerate(KeysList) if self.isKeyActive(key['id']) ]
	# 	return selectedKeys

	def get_selection(self):

		KeysList = self.get_keys()
		selectedKeys = [i for i,key in enumerate(KeysList) if key['selected'] == 1 and self.isKeyActive(key['id']) ]
		return selectedKeys

	def get_attribute(self, attributeName):
		KeysList = self.get_keys()
		# selectedKeys = [key[attributeName] for i,key in enumerate(KeysList) if key['selected'] == 1 and self.isKeyActive(key['id']) ]
		selectedKeys = [ key[attributeName] for i,key in enumerate(KeysList) ]
		return selectedKeys

	def Selection(self):
		return self.get_selection()


	def getAspect(self, viewerComp):
		W = viewerComp.width
		H = viewerComp.height - 25 # 25 is how tall the toolbar is

		if(W > H):
			maxDim = max(W,H)
		elif(W < H):
			maxDim = min(W,H)

		W /= maxDim
		H /= maxDim


	# // if X aspect is bigger than Y aspect, use max(), otherwise use min()
	# if( WH.x > WH.y ){ WH /= max(WH.x , WH.y); }
	# if( WH.x <= WH.y ){ WH /= min(WH.x , WH.y); }

		return [W,H]


	def CalcBoundsFromId_______________________(self, id=1):
		keysTable = parent.helper.op('curveEditor/keys')
		idCol = keysTable[ 0 , 'id' ].col
		xCol = keysTable[ 0 , 'x' ].col
		yCol = keysTable[ 0 , 'y' ].col

		xVals = []
		yVals = []
		for row in keysTable.rows()[1::]:
			if int(row[idCol]) == id:
				xVals += [ float(row[xCol]) ]
				yVals += [ float(row[yCol]) ]

		xMin = min(xVals or [0,1])
		xMax = max(xVals or [0,1])
		yMin = min(yVals or [0,1])
		yMax = max(yVals or [0,1])

		returnDict = {
			"xMin":xMin,
			"xMax":xMax,
			"yMin":yMin,
			"yMax":yMax,
		}

		if keysTable.numRows > 1:
			returnDict['xMin'] = float(self.StartStopChop['Timestart'][0])
			returnDict['xMax'] = float(self.StartStopChop['Timestop'][0])
			returnDict['yMin'] = 0
			returnDict['yMax'] = 1

		return returnDict

	def CalcBoundsFromId(self, ids=[]):
		keysTable = parent.helper.op('curveEditor/keys')
		idCol = keysTable[ 0 , 'id' ].col
		selectedCol = keysTable[ 0 , 'selected' ].col
		xCol = keysTable[ 0 , 'x' ].col
		yCol = keysTable[ 0 , 'y' ].col

		# first, establish the default vals.
		returnDict = {
			'xMin' : float(self.StartStopChop['Timestart'][0]),
			'xMax' : float(self.StartStopChop['Timestop'][0]),
			'yMin' : 0,
			'yMax' : 1
		}

		# if keysTable.numRows > 1: # if there are any keys at all.

		selected = list(map(int,keysTable.col('selected')[1::]))
		if sum(selected) < 2:  # if no keys were selected, or only one was selected, use them all.
			selected = [ 1 for x in selected ]

		if len(ids) == 0: # if user did not provide any ids, just use them all.
			ids = list(map(int,keysTable.col('id')[1::]))
			ids = [ x-1 for x in ids ]

		if keysTable.numRows > 1:
			xVals = []
			yVals = []
			for i,row in enumerate(keysTable.rows()[1::]):
				if int(row[idCol])-1 in ids and selected[i] == 1:
					
					xVals += [ float(row[xCol]) ]
					yVals += [ float(row[yCol]) ]

			# xMin = min(xVals)
			# xMax = max(xVals)
			# yMin = min(yVals)
			# yMax = max(yVals)

			xMin = min(xVals or [0,1])
			xMax = max(xVals or [0,1])
			yMin = min(yVals or [0,1])
			yMax = max(yVals or [0,1])


			# if the user has two keyframes set to 0 on Y, then 
			# homing will skew the vertical very far and require a ton of
			# vertical zooming out.. which is annoying. this is trying to smartly
			# see that the user has two or more 0Y keyframes and to just normalize
			# to 0-1 unless there is a slight difference, which we then assume is intentional.
			tooFlatTreshold = 0.001
			if yMax-yMin < tooFlatTreshold:
				yMax = 1.0
				yMin = 0.0

			tooNarrowTreshold = 0.01
			if xMax-xMin < tooNarrowTreshold:
				xMax = float(self.StartStopChop['Timestop'][0])
				xMin = float(self.StartStopChop['Timestart'][0])

			returnDict = {
				"xMin":xMin,
				"xMax":xMax,
				"yMin":yMin,
				"yMax":yMax,
			}

		return returnDict


	def HomeGraphCamToBounds(self):
		
		activeChans = self.ActiveChans()
		boundsDict = self.CalcBoundsFromId(activeChans)
		aspect = self.getAspect( parent.helper.op('curveEditor') )

		cam = parent.helper.op('curveEditor').op('cam')
		cam.par.tx = ((boundsDict['xMin'] + boundsDict['xMax']) / 2)
		cam.par.ty = ((boundsDict['yMin'] + boundsDict['yMax']) / 2)

		cam.par.sx = (boundsDict['xMax'] - boundsDict['xMin']) * (1/aspect[0])
		cam.par.sy = (boundsDict['yMax'] - boundsDict['yMin']) * (1/aspect[1])

		# print(aspect[1])

		boundsAspectX = cam.par.sx.eval()
		boundsAspectY = cam.par.sy.eval()
		maxAspectBound = max(boundsAspectX,boundsAspectY)
		boundsAspectX = boundsAspectX / maxAspectBound if maxAspectBound != 0 else 1
		boundsAspectY = boundsAspectY / maxAspectBound if maxAspectBound != 0 else 1

		reductionFactor = 10

		paddingX = cam.par.sx / reductionFactor
		paddingY = cam.par.sy / reductionFactor

		cam.par.sx += (paddingX / 1) * (1/aspect[0])
		cam.par.sy += (paddingY / 1) * (1/aspect[1])


		toolBarHeightFractional = 25 / parent().height
		cam.par.ty += paddingY*.1

		self.EnableKeyPicking()

		return


	def TranslateKeys_Init(self):

		sel = self.get_selection()
		keysDat = parent.helper.op('curveEditor/keys')

		x = self.get_attribute('x')
		y = self.get_attribute('y')
		id_ = self.get_attribute('id')

		initDict = {}
		for i in sel:
			initDict[i] = {}
			initDict[i]['x'] = x[i]
			initDict[i]['y'] = y[i]
			initDict[i]['id'] = id_[i]

		# print(initDict)

		parent.helper.store('initPos',initDict)

	def GetNextAvailableSlot( self , desiredKeyIndex , occupiedSlots , searchStep ):
		'''
		Given an initial index, and a list of indicies that are "occupied", this function
		will search via increments of searchStep, for a slot that is not already occupied.
		'''
		BailIters = 100
		BailCounter = 0
		while( BailCounter < BailIters ):
			
			if desiredKeyIndex not in occupiedSlots:
				break
			else:
				desiredKeyIndex += searchStep

			BailCounter += 1

		return desiredKeyIndex



	def TranslateKeys_Move(self):
		# debug('do translate')

		CU = parent.helper
		xDist = CU.par.Dragx - CU.par.Startx
		yDist = CU.par.Dragy - CU.par.Starty

		KeysList = self.get_keys()
		SEL = self.get_selection()
		stickyKeys = self.getFirstKeyIndexOfEachChan()

		for i,each in enumerate(KeysList):
			KeysList[i]["PRE_ID"] = i

		initDict = CU.fetch('initPos',{})
		for k,v in initDict.items():
			
			currentlyOccupiedFrames = [ key['x'] for i,key in enumerate(KeysList) if i not in SEL ]

			x = int(round(v['x'] + xDist))
			if x not in currentlyOccupiedFrames:
				
				if k == stickyKeys[v['id']]: # IF user isn't trying to move first key.
					KeysList[k]['x'] = 0

				else:
					KeysList[k]['x'] = max( x , 0 )
			
			KeysList[k]['y'] = v['y'] + yDist


		# sort the KeyList, this is only needed if the user entered a frame number 
		# in for a key, that placed it at a new index in the keylist.
		KeysList = sorted( KeysList, key=lambda x: x['x'] )

		# if the user reordered the keys by entering a frame number that triggered that, we need to also
		# update the selection list to reflect those changes. We do this by translating from the first selection order
		# which was recorded as "PRE_ID", and keeping the index we found it at now.
		newSelectionList = sorted([ i for i,each in enumerate(KeysList) if each['PRE_ID'] in SEL ])
		
		# now for the fun part, since we are moving keys, and we are sorting them in real time,
		# if at any point the key order changes, we also need to update the KEYS of the init dict. Not the vals though.
		# for this, we need to build a translation dict, to get from OLDKEY -> NEWKEY
		translationDict = { each:newSelectionList[i] for i,each in enumerate(SEL) }
		# print(initDict)
		# we comprehension our way through the old init dict, and update with the new key, while keeping the value.
		initDict = { translationDict[k]:v for k,v in initDict.items() }
		parent.helper.store('initPos',initDict)

		# now that we have sorted the key list, and retrieved our new selection list ,we can remove the PRE_ID
		# from all sub dicts in the list.
		KeysList = [ { k:v for k,v in each.items() if k not in ["PRE_ID"]} for each in KeysList ]

		# store some things back.
		self.Select(newSelectionList)
		self.set_keys(KeysList)

		return
			


	def boundsCheck(self, keyX, keyY, aX, aY, bX, bY):


		bools = [
		keyX >= min(aX,bX),
		keyX <= max(aX,bX),
		keyY >= min(aY,bY),
		keyY <= max(aY,bY)
		]

		return min(bools)

	def MarqueeSelect(self, aX, aY, bX, bY):
		'''
		input vals should be world space coords
		'''
		# these following commands fetch the parameter, from the object currently sourced.
		lookupDat = parent.helper.op("Data_Entry/SET_LOOKUP")
		targetOp = parent.helper.par.Ops.eval()
		targetPar = parent.helper.par.Par.eval()
		assert targetOp != None, 'targetOp cannot be None'
		foundPar = getattr(targetOp.par , targetPar , ":ERR:")
		assert targetOp != None, 'targetOp"s foundPar cannot be None'

		# get our Keylist and selection list.
		KeyList = foundPar.eval()

		newSel = [ i for i,key in enumerate(KeyList) if self.boundsCheck(key['x'], key['y'], aX, aY, bX, bY ) ]

		self.Select(newSel)
		
		return
		
			

	def Channel_Select(self, chanID):
		newSel = list(set(chanID))
		parent.helper.par.Activechannels = newSel
		return
		
			

	def Channel_SelectAdd(self, chanID):
		
		Activechannels = parent.helper.par.Activechannels.eval()
		newSel = list(set(chanID))
		parent.helper.par.Activechannels = list(set(newSel).union( set(Activechannels) ))

		return


	def Channel_SelectRemove(self, chanID):
		
		Activechannels = parent.helper.par.Activechannels.eval()
		newSel = list(set(chanID))
		parent.helper.par.Activechannels = list(set(Activechannels).difference( set(newSel) ))
		
		return


	def Channel_SelectToggle(self, chanID):
		
		Activechannels = parent.helper.par.Activechannels.eval()
		newSel = list(set(chanID))

		itemsToDelete = []
		for each in Activechannels:
			if each in newSel:
				itemsToDelete += [ each ]

		itemsToAdd = []
		for each in newSel:
			if each not in Activechannels:
				itemsToAdd += [ each ]

		Activechannels = [ x for x in Activechannels if x not in itemsToDelete ] # delete stuff
		Activechannels = Activechannels + itemsToAdd # add stuff
		Activechannels = sorted(list(set(Activechannels)))
		parent.helper.par.Activechannels = Activechannels
		
		return


	def Channel_SelectClear(self):
		
		parent.helper.par.Activechannels = []
		
		return


	def Select(self, keyID=[]):
		
		newSel = list(set(keyID))
		keyList = self.get_keys()

		for i,key in enumerate(keyList):

			if self.isKeyActive(key['id']):
				key['selected'] = (i in newSel)*1

		self.set_keys( keyList )
		
		return
			


	def SelectAdd(self, keyID=[]):
		
		newSel = list(set(keyID))
		keyList = self.get_keys()

		for i,key in enumerate(keyList):
			if self.isKeyActive(key['id']):
				key['selected'] = max( (i in newSel)*1 , key['selected'] )

		self.set_keys( keyList )
		
		return
			


	def SelectRemove(self, keyID=[]):

		newSel = list(set(keyID))
		keyList = self.get_keys()

		for i,key in enumerate(keyList):
			if self.isKeyActive(key['id']):
				key['selected'] = min( (i not in newSel)*1 , key['selected'] )

		self.set_keys( keyList )
		
		return
			


	def SelectClear(self):

		# newSel = list(set(keyID))
		keyList = self.get_keys()

		for i,key in enumerate(keyList):
			if self.isKeyActive(key['id']):
				key['selected'] = 0

		self.set_keys( keyList )
		
		return


	def EnableKeyPicking(self):
		# parent.helper.op('curveEditor/geo_dots').pickable  = True
		f = parent.helper.op('curveEditor').findChildren(name='geo_dots', depth=2, maxDepth=2)
		for each in f:
			each.pickable = True


	def DisableKeyPicking(self):
		# parent.helper.op('curveEditor/geo_dots').pickable  = False
		f = parent.helper.op('curveEditor').findChildren(name='geo_dots', depth=2, maxDepth=2)
		for each in f:
			each.pickable = False



	def AttribEditor_GET(self, argDict={}):

		''' Arg dict can look like this - this is looked up in /UberGui/CurveEditor/Data_Entry/SET_LOOKUP
			{"x":0,
			"y":1,
			"inslope":0,
			"inaccel":0,
			"expression":'cubic()',
			"outslope":0,
			"outaccel":0}
		'''
		lookupDat = parent.helper.op("Data_Entry/SET_LOOKUP")
		# debug(argDict)-
		for k,v in argDict.items():
			foundRow = lookupDat.row(k)
			if foundRow != None:
				targetWidget = op(foundRow[1])
				if k == "x":
					if parent.helper.par.Unitoftime.eval() == "frames":
						targetWidget.par.Value0 = int(v)+1 # if setting the frame, we want the user to work in 1 based, but backend is 0 based.
					elif parent.helper.par.Unitoftime.eval() == "seconds":
						targetWidget.par.Value0 = op.sceneOutliner.mod.tdUtils.Frames_2_Seconds( int(v)+1 , parent.helper.par.Fps.eval() )
					elif parent.helper.par.Unitoftime.eval() == "beats":
						targetWidget.par.Value0 = op.sceneOutliner.mod.tdUtils.Frames_2_Beats( int(v)+1 , parent.helper.par.Fps.eval(), parent.helper.par.Bpm.eval() )
				else:
					# print(v)
					targetWidget.par.Value0 = v

			else:
				debug(k, 'did not exist in lookup dat...')

		return



	def AttribEditor_SET(self, argDict={}):
		
		# these following commands fetch the parameter, from the object currently sourced.
		lookupDat = parent.helper.op("Data_Entry/SET_LOOKUP")

		# get our Keylist and selection list.
		KeyList = self.get_keys()
		ChansDict = self.Get_chans()
		sel = self.get_selection()

		ActiveChanIndicies = self.ActiveChans()
		ActiveChanNames = self.ChanIndiciesToNames(ActiveChanIndicies)
		# print(ActiveChanIndicies)

		# insert our temporary PRE_ID value. we will use this to track our selection Id's after 
		# we update params.
		for i,each in enumerate(KeyList):
			KeyList[i]["PRE_ID"] = i
		
		# iterate through each argument pair that the user provided to this function via the argDict.
		for k,v in argDict.items():
			
			# K is == full path of the widget, that sent this value. we try to find that widgets path in the lookup dat.
			foundRow = lookupDat.findCell(k)
			
			# if we found a cell (which we should), we can proceed.
			if foundRow != None:
				
				# doing a reverse lookup, get the attribute name, via the widget path.
				attribute = lookupDat[foundRow.row,0].val

				### IF we are setting a channel parameter.
				if attribute in ['extendleft', 'extendright', 'defaultvalue']:
					
					value = copy.copy(v)
					
					for chanName in ActiveChanNames:
						chanDict = ChansDict.get(chanName,{})
						chanDict[attribute] = value
						ChansDict[chanName] = chanDict

				
				### IF we are setting a key parameter.
				else:
					for selectedKeyIndex in sel:
						value = copy.copy(v)
						# if the user tried to set the first key's frame, just force it to 0.
						if selectedKeyIndex == 0 and attribute == 'x':
							KeyList[selectedKeyIndex][attribute] = 0
						elif attribute == 'x' and selectedKeyIndex != 0:
							
							if parent.helper.par.Unitoftime.eval() == "frames":
								KeyList[selectedKeyIndex][attribute] = value-1 # minus 1 cause X is displayed as 1, entered as 1, but backend it is 0.
							elif parent.helper.par.Unitoftime.eval() == "seconds":
								value = op.sceneOutliner.mod.tdUtils.Seconds_2_Frames( value , parent.helper.par.Fps.eval() )
								KeyList[selectedKeyIndex][attribute] = value - 1
							elif parent.helper.par.Unitoftime.eval() == "beats":
								value = op.sceneOutliner.mod.tdUtils.Beats_2_Frames( value , parent.helper.par.Fps.eval() , parent.helper.par.Bpm.eval() )
								KeyList[selectedKeyIndex][attribute] = value - 1
						
						else:
							KeyList[selectedKeyIndex][attribute] = value

			else:
				debug(k, 'did not exist in any cell in lookup dat...')

		self.Set_chans( ChansDict )

		# sort the KeyList, this is only needed if the user entered a frame number 
		# in for a key, that placed it at a new index in the keylist.
		KeyList = sorted( KeyList, key=lambda x: x['x'] )

		# if the user reordered the keys by entering a frame number that triggered that, we need to also
		# update the selection list to reflect those changes. We do this by translating from the first selection order
		# which was recorded as "PRE_ID", and keeping the index we found it at now.
		newSelectionList = sorted([ i for i,each in enumerate(KeyList) if each['PRE_ID'] in sel ])

		# now that we have sorted the key list, and retrieved our new selection list ,we can remove the PRE_ID
		# from all sub dicts in the list.
		KeyList = [ { k:v for k,v in each.items() if k not in ["PRE_ID"]} for each in KeyList ]

		# set the modified keys list back to the parameter.
		self.Select(newSelectionList)
		self.set_keys(KeyList)
		

		return



	def InsertKey(self):


		CU = parent.helper
		xDist = CU.par.Startx.eval()
		yDist = CU.par.Starty.eval()

		KeysList = self.get_keys()
		ActiveChansList = self.get_activeChans()
		newSelection = []

		for chanIndex in ActiveChansList:

			LeftSideindicies = [ i for i,key in enumerate(KeysList) if key['x'] <= xDist and self.isKeyInChannel(key['id'],chanIndex) ]

			if len(LeftSideindicies) == 0:
				LeftSideindicies = [0]

			newKey = { k:v for k,v in KeysList[LeftSideindicies[-1]].items() }

			newKey['x'] = max( int(round(xDist)) , 1 )
			if len(ActiveChansList) == 1:
				newKey['y'] = yDist
			else:
				pass

			KeysList.append( newKey )



			# insert our temporary PRE_ID value. we will use this to track our selection Id's after 
			# we update params.
			for i,each in enumerate(KeysList):
				KeysList[i]["PRE_ID"] = i

			lastPreID = KeysList[-1]['PRE_ID']

			# sort the KeysList, this is only needed if the user entered a frame number 
			# in for a key, that placed it at a new index in the keylist.
			KeysList = sorted( KeysList, key=lambda x: x['x'] )

			# if the user reordered the keys by entering a frame number that triggered that, we need to also
			# update the selection list to reflect those changes. We do this by translating from the first selection order
			# which was recorded as "PRE_ID", and keeping the index we found it at now.
			# newSelectionList = sorted([ i for i,each in enumerate(KeysList) if each['PRE_ID'] in [lastPreID] ])
			newSelection += sorted([ i for i,each in enumerate(KeysList) if each['PRE_ID'] in [lastPreID] ])

			# now that we have sorted the key list, and retrieved our new selection list ,we can remove the PRE_ID
			# from all sub dicts in the list.
			KeysList = [ { k:v for k,v in each.items() if k not in ["PRE_ID"]} for each in KeysList ]
		# print(newSelection)
		# store some things back.
		self.set_keys(KeysList)
		self.Select(newSelection)
		

		return


	def DeleteChannel(self, chanName):

		permChans = self.get_unDeletableChans()

		KeysList = self.get_keys()
		ChansList = self.Get_chans()

		# go ahead and reset the Selected channels to nothing, so we don't run into problems later.
		parent.helper.par.Activechannels = []
		parent.helper.par.Selection = []

		if chanName not in permChans:
			
			KeysList = [ each for each in KeysList if each['id'] != chanName ]
			ChansList = { k:v for k,v in ChansList.items() if k != chanName }


			pass
		else:
			debug('cant delete that chan!')

		self.set_keys(KeysList)
		self.Set_chans(ChansList)

		return



	def DeleteKeys(self, keysToDelete):
		
		assert isinstance(keysToDelete,list), 'keysToDelete must be a list of integers.'

		CU = parent.helper
		KeysList = self.get_keys()
		sel = self.get_selection()

		ActiveKeyIndicies = sorted([ i for i,key in enumerate(KeysList) if self.isKeyActive(key['id']) ])

		if len(ActiveKeyIndicies) == 0:
			return # early exit if no active key indicies.

		keysToNotDelete = list(set([ActiveKeyIndicies[0]]).union(set([0])))

		# filter out 0 from key list, user is not allowed to delete the first key.
		keysToDelete = [ each for each in keysToDelete if each not in keysToNotDelete ]

		# insert our temporary PRE_ID value. we will use this to track our selection Id's after 
		# we update params.
		for i,each in enumerate(KeysList):
			KeysList[i]["PRE_ID"] = i

		# filter out - aka - delete the keys the user provided through the keysToDelete argument.
		KeysList = [ key for key in KeysList if key['PRE_ID'] not in keysToDelete ]

		# if the user reordered the keys by entering a frame number that triggered that, we need to also
		# update the selection list to reflect those changes. We do this by translating from the first selection order
		# which was recorded as "PRE_ID", and keeping the index we found it at now.
		newSelectionList = sorted([ i for i,each in enumerate(KeysList) if each['PRE_ID'] in sel ])

		# now that we have sorted the key list, and retrieved our new selection list ,we can remove the PRE_ID
		# from all sub dicts in the list.
		KeysList = [ { k:v for k,v in each.items() if k not in ["PRE_ID"]} for each in KeysList ]

		# store some things back.
		
		self.set_keys(KeysList)
		self.Select(newSelectionList)

		return



	def SetValueTo(self, val):

		# get our Keylist and selection list.
		KeyList = self.get_keys()
		sel = self.get_selection()

		for selectedKeyIndex in sel:
			KeyList[selectedKeyIndex]['y'] = val
		
		# set the modified keys list back to the parameter.
		self.set_keys(KeyList)

		return



	def SetValueLowest(self):

		# get our Keylist and selection list.
		KeyList = self.get_keys()
		sel = self.get_selection()

		if len(sel) > 0:
			val = min([ key['y'] for i,key in enumerate(KeyList) if i in sel ])

			for selectedKeyIndex in sel:
				KeyList[selectedKeyIndex]['y'] = val
			
			# set the modified keys list back to the parameter.
			self.set_keys(KeyList)

		return



	def SetValueHighest(self):

		# get our Keylist and selection list.
		KeyList = self.get_keys()
		sel = self.get_selection()

		if len(sel) > 0:
			val = max([ key['y'] for i,key in enumerate(KeyList) if i in sel ])

			for selectedKeyIndex in sel:
				KeyList[selectedKeyIndex]['y'] = val
			
			# set the modified keys list back to the parameter.
			self.set_keys(KeyList)

		return