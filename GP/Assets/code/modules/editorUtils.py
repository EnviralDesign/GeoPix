treeInfoTable = op.sceneOutliner.op('treeInfo_Outliner')
treeOutliner = op.sceneOutliner.op('treeInfo_Outliner')
sceneVars = op.sceneOutliner.op("sceneVars")
zoomNull = op('zoomNull')

SUBMODE = op('SUBMODE')

TDJ = op.TDModules.mod.TDJSON
import json


lastTransformOffset = op.sceneOutliner.op('lastTransformOffset')
toolbar = op.sceneOutliner.op("toolbar")


def newScene():
	mod.tdUtils.deleteAllItems()
	# op.tabArea.SetContext(0)
	debug('update this with new set context switcher, if needed!')

def duplicateSpecial():
	mod.tdUtils.duplicateSelectedItems_withOffset(
		op.Object_Tools.par.Offsetx.eval(),
		op.Object_Tools.par.Offsety.eval(),
		op.Object_Tools.par.Offsetz.eval(),
		op.Object_Tools.par.Offsetrotx.eval(),
		op.Object_Tools.par.Offsetroty.eval(),
		op.Object_Tools.par.Offsetrotz.eval(),
		)

def duplicateMirror():
	symX = int(op.Object_Tools.par.Mirror1.eval())
	symY = int(op.Object_Tools.par.Mirror2.eval())
	symZ = int(op.Object_Tools.par.Mirror3.eval())
	mod.tdUtils.mirrorDuplicateSelectedItems(symZ, symY, symX)
	
	
def homeCamera(reset=False):

	if reset == True:
		
		justOpPaths = [ zoomNull ]
	
	else:
		justOpPaths = []
		if treeInfoTable.col('path') != None and treeInfoTable.col('Selected') != None:
			
			opPath = map(str,treeInfoTable.col('path')[1::])
			Selected = map(int,treeInfoTable.col('Selected')[1::])
			opPathPair = dict(zip(opPath,Selected))
			
			selectedOpPaths = { k:v for k,v in opPathPair.items() if v == 1 }
			justOpPaths = [ op(x) for x in list(selectedOpPaths.keys()) ]
			# print(justOpPaths)
		if len(justOpPaths) == 0:
			justOpPaths = [ zoomNull ]
	
	op.Viewport.mod.vpUtils.HomeCamera(justOpPaths[0])
	
	
def SelectAllItems():
	if SUBMODE['ObjectEditMode'] == 1:
		ObjectSelect_All()
	elif SUBMODE['HullEditMode'] == 1:
		selectAllHulls()
	elif SUBMODE['PixelEditMode'] == 1:
		selectAllPix()
	return
	
def DeselectAllItems():
	if SUBMODE['ObjectEditMode'] == 1:
		ObjectSelect_None()
	elif SUBMODE['HullEditMode'] == 1:
		deselectAllHulls()
	elif SUBMODE['PixelEditMode'] == 1:
		deselectAllPix()
	return
	
def InvertSelectAllItems():
	if SUBMODE['ObjectEditMode'] == 1:
		mod.tdUtils.invertSelectItems()
	elif SUBMODE['HullEditMode'] == 1:
		invertAllHulls()
	elif SUBMODE['PixelEditMode'] == 1:
		invertAllPix()
	return
	
def DeleteSelectedItems():
	'''
	This deletes the current selection, weather it be hulls, pix, of objects (mode dependant)
	'''

	# debug('DELETEING BRO..')
	# '''
	if SUBMODE['ObjectEditMode'] == 1:
		# debug('delete those objects')
		mod.tdUtils.deleteSelectedItems()
	elif SUBMODE['HullEditMode'] == 1:
		# debug('delete those Hulls')
		deleteSelectedHulls()
	elif SUBMODE['PixelEditMode'] == 1:
		# debug('delete those Pix')
		deleteSelectedPix()
	# '''
	
	return
	
def DeleteLastItem():
	'''
	This deletes last Hull or Pix in chain.
	'''
	if SUBMODE['ObjectEditMode'] == 1:
		pass
	elif SUBMODE['HullEditMode'] == 1:
		deleteLastHull()
	elif SUBMODE['PixelEditMode'] == 1:
		deleteLastPix()
	
	return
	
def DeleteAllItems():
	'''
	This deletes last Hull or Pix in chain.
	'''
	if SUBMODE['ObjectEditMode'] == 1:
		mod.tdUtils.deleteAllItems()
	elif SUBMODE['HullEditMode'] == 1:
		deleteAllHulls()
	elif SUBMODE['PixelEditMode'] == 1:
		deleteAllPix()
	
	return
	
def NudgeSelectItemsMinus():
	if SUBMODE['ObjectEditMode'] == 1:
		pass
	elif SUBMODE['HullEditMode'] == 1:
		shiftHullSelMinusOne()
	elif SUBMODE['PixelEditMode'] == 1:
		shiftPixSelMinusOne()
	return
	
def NudgeSelectItemsPlus():
	if SUBMODE['ObjectEditMode'] == 1:
		pass
	elif SUBMODE['HullEditMode'] == 1:
		shiftHullSelPlusOne()
	elif SUBMODE['PixelEditMode'] == 1:
		shiftPixSelPlusOne()
	return
	
def GrowSelectItems():
	if SUBMODE['ObjectEditMode'] == 1:
		pass
	elif SUBMODE['HullEditMode'] == 1:
		growHullSelPlusOne()
	elif SUBMODE['PixelEditMode'] == 1:
		growPixSelPlusOne()
	return
	
def ShrinkSelectItems():
	if SUBMODE['ObjectEditMode'] == 1:
		pass
	elif SUBMODE['HullEditMode'] == 1:
		growHullSelMinusOne()
	elif SUBMODE['PixelEditMode'] == 1:
		growPixSelMinusOne()
	return
	
def InsertBetweenItems():
	if SUBMODE['ObjectEditMode'] == 1:
		pass
	elif SUBMODE['HullEditMode'] == 1:
		SubdivideTwoHulls()
	elif SUBMODE['PixelEditMode'] == 1:
		SubdivideTwoPix()
	return
	
def AppendItem():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	if lastSelObj != None:
	
		if SUBMODE['ObjectEditMode'] == 1:
			pass
		elif SUBMODE['HullEditMode'] == 1:
			HullComp = lastSelObj.op('hull')
			lastCoord = HullComp.GetAllCoords()[-1]
			HullComp.DeselectAll()
			HullComp.AddCoord( x=lastCoord[0] , y=lastCoord[1] , z=lastCoord[2] , selected=1 , localSpace=True )
			HullComp.WriteCoordsToTable()
		elif SUBMODE['PixelEditMode'] == 1:
			PixComp = lastSelObj.op('pix')
			lastCoord = PixComp.GetAllCoords()[-1]
			PixComp.DeselectAll()
			PixComp.AddPix( x=lastCoord[0] , y=lastCoord[1] , z=lastCoord[2] , selected=1 )
	return
	
	
def selectAllHulls():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	# print(lastSelObj)
	if lastSelObj != None:
		lastSelHullComp = lastSelObj.op('hull')
		if lastSelHullComp != None:
			lastSelHullComp.SelectAll()
			lastSelHullComp.WriteCoordsToTable()
			
			
def deselectAllHulls():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelHullComp = lastSelObj.op('hull')
		if lastSelHullComp != None:
			lastSelHullComp.DeselectAll()
			lastSelHullComp.WriteCoordsToTable()
		
	
	
def invertAllHulls():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelHullComp = lastSelObj.op('hull')
		if lastSelHullComp != None:
			lastSelHullComp.InvertSelectAll()
			lastSelHullComp.WriteCoordsToTable()
		
	
	
def shiftHullSelPlusOne():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelHullComp = lastSelObj.op('hull')
		if lastSelHullComp != None:
			lastSelHullComp.ShiftSelection(1)
			lastSelHullComp.WriteCoordsToTable()
		
	
	
def shiftHullSelMinusOne():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelHullComp = lastSelObj.op('hull')
		if lastSelHullComp != None:
			lastSelHullComp.ShiftSelection(-1)
			lastSelHullComp.WriteCoordsToTable()
		
	
	
def growHullSelPlusOne():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelHullComp = lastSelObj.op('hull')
		if lastSelHullComp != None:
			lastSelHullComp.GrowShrinkSelection(1,1)
			lastSelHullComp.WriteCoordsToTable()
		
	
	
def growHullSelMinusOne():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelHullComp = lastSelObj.op('hull')
		if lastSelHullComp != None:
			lastSelHullComp.GrowShrinkSelection(1,-1)
			lastSelHullComp.WriteCoordsToTable()
		
	
	
def reverseHullDirection___________():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelHullComp = lastSelObj.op('hull')
		if lastSelHullComp != None:
			lastSelHullComp.ReverseAllHulls()
			lastSelHullComp.WriteCoordsToTable()
		
	
	
def deleteAllHulls():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelHullComp = lastSelObj.op('hull')
		if lastSelHullComp != None:
			lastSelHullComp.DeleteAll()
			lastSelHullComp.WriteCoordsToTable()
		
	
	
def deleteLastHull():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelHullComp = lastSelObj.op('hull')
		if lastSelHullComp != None:
			lastSelHullComp.DeleteLastCoordAndSelect()
			lastSelHullComp.WriteCoordsToTable()
		
	
	
def deleteSelectedHulls():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelHullComp = lastSelObj.op('hull')
		if lastSelHullComp != None:
			lastSelHullComp.DeleteSelectedCoords()
			lastSelHullComp.WriteCoordsToTable()
		
	
	
def genereatorFromSelectedHulls():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	assert lastSelObj != None,'This OP is not valid, please check this out.'
		
	lastSelHullComp = lastSelObj.op('hull')
	lastSelPixComp = lastSelObj.op('pix')
	
	# assert lastSelHullComp != None,'there is no hull comp inside of this fixture.. or is it a fixture? check this out'
	# assert lastSelPixComp != None,'there is no pix comp inside of this fixture.. or is it a fixture? check this out'
	
	if lastSelHullComp != None and lastSelPixComp != None:
		
		# get the selected fixture object.
		lastSelObj = mod.tdUtils.getObjectList(criteria="directSelected")[0][0]
		
		totalHullCount = lastSelHullComp.GetTotalNumberOfHulls()
		selectedHullCount = len(lastSelHullComp.GetSelectedCoords())
		
		# print('numHullsselected, ',selectedHullCount)
		
		if selectedHullCount > 0:
			
			# set the viewport to object mode.
			op.ViewPortUI.ClickButton('ObjectMode')
			
			# get the hull indicies string.
			hullIndiciesStr = lastSelHullComp.GetSelectedCoordIndiciesAsString()

			# list comp to ints, make values 1 based (instead of 0 based) then convert back to csv style.
			hullIndiciesStr = ','.join(map(str,[ x+1 for x in map(int,hullIndiciesStr.split(',')) ]))

			totalPixCout = lastSelPixComp.GetTotalNumberOfPix()
			avgCenter = lastSelHullComp.GetAvgCenterOfSelected()
			avgCenter = mod.matrixUtils.LocalSpace_to_WorldSpace(lastSelObj, avgCenter[0], avgCenter[1], avgCenter[2])
			
			# create generator.
			createdGenerator = mod.create.Object("CreateGenerator")
			
			# set the new position of the created generator. 
			createdGenerator.par.Tx = avgCenter[0]
			createdGenerator.par.Ty = avgCenter[1]
			createdGenerator.par.Tz = avgCenter[2]
			
			# set some parameters om the generator based on our selection.
			if totalHullCount == selectedHullCount:
				createdGenerator.par.Hullcoords = '*'
			else:
				createdGenerator.par.Hullcoords = hullIndiciesStr
				
			if selectedHullCount == 1:
				createdGenerator.par.Gentype = 'Grid'
			
			# parent newly created generator to the fixture object.
			mod.tdUtils.parentObjectFlat( [createdGenerator] , lastSelObj )

			# createdGenerator.op('GENERATOR/datexec_on_par_vis_change').run(delayFrames=10)
			createdGenerator.op('INIT/Run').run(delayFrames=1)
			mod.tdUtils.selectItems([createdGenerator])
			
		else:
			op.NOTIFV2.Notify('Please select at least 1 Hull, before you can create a Generator from your Hull Selection.')
	
	else:
		debug('Hull and Comp pix not found, or still loading... probably safe to ignore this.')
		
		
		
def selectAllPix():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelPixComp = lastSelObj.op('pix')
		if lastSelPixComp != None:
			lastSelPixComp.SelectAll()
			lastSelPixComp.WriteCoordsToTable()
		
			

def deselectAllPix():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelPixComp = lastSelObj.op('pix')
		if lastSelPixComp != None:
			lastSelPixComp.DeselectAll()
			lastSelPixComp.WriteCoordsToTable()
		
			

def invertAllPix():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelPixComp = lastSelObj.op('pix')
		if lastSelPixComp != None:
			lastSelPixComp.InvertSelectAll()
			lastSelPixComp.WriteCoordsToTable()
		
			

def shiftPixSelPlusOne():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelPixComp = lastSelObj.op('pix')
		if lastSelPixComp != None:
			lastSelPixComp.ShiftSelection(1)
			lastSelPixComp.WriteCoordsToTable()
		
			

def shiftPixSelMinusOne():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelPixComp = lastSelObj.op('pix')
		if lastSelPixComp != None:
			lastSelPixComp.ShiftSelection(-1)
			lastSelPixComp.WriteCoordsToTable()
		
			

def growPixSelPlusOne():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelPixComp = lastSelObj.op('pix')
		if lastSelPixComp != None:
			lastSelPixComp.GrowShrinkSelection(1,1)
			lastSelPixComp.WriteCoordsToTable()
		
			

def growPixSelMinusOne():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelPixComp = lastSelObj.op('pix')
		if lastSelPixComp != None:
			lastSelPixComp.GrowShrinkSelection(1,-1)
			lastSelPixComp.WriteCoordsToTable()
		
			

def deleteLastPix():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelPixComp = lastSelObj.op('pix')
		if lastSelPixComp != None:
			lastSelPixComp.DeleteLastCoordAndSelect()
			lastSelPixComp.WriteCoordsToTable()
		

def deleteAllPix():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelPixComp = lastSelObj.op('pix')
		if lastSelPixComp != None:
			lastSelPixComp.DeleteAll()
			lastSelPixComp.WriteCoordsToTable()
		

def deleteSelectedPix():
	
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelPixComp = lastSelObj.op('pix')
		if lastSelPixComp != None:
			lastSelPixComp.DeleteSelectedCoords()
			lastSelPixComp.WriteCoordsToTable()
		

def reversePixStrand(lastSelectedOnly=True):
	
	if lastSelectedOnly == True:
		lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
		
		if lastSelObj != None:
			lastSelPixComp = lastSelObj.op('pix')
			if lastSelPixComp != None:
				lastSelPixComp.ReverseAllPix()
				lastSelPixComp.WriteCoordsToTable()
				
	else:
		# lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
		allFixtures = mod.tdUtils.getObjectList('directSelected', 2)[0]
		for fixture in allFixtures:
			
			lastSelPixComp = fixture.op('pix')
			if lastSelPixComp != None:
				lastSelPixComp.ReverseAllPix()
				lastSelPixComp.WriteCoordsToTable()
				

def reverseHullStrand(lastSelectedOnly=True):
	
	if lastSelectedOnly == True:
		lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
		
		if lastSelObj != None:
			lastSelHullComp = lastSelObj.op('hull')
			if lastSelHullComp != None:
				lastSelHullComp.ReverseAllHulls()
				lastSelHullComp.WriteCoordsToTable()
				
	else:
		# lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
		allFixtures = mod.tdUtils.getObjectList('directSelected', 2)[0]
		for fixture in allFixtures:
			
			lastSelHullComp = fixture.op('hull')
			if lastSelHullComp != None:
				lastSelHullComp.ReverseAllHulls()
				lastSelHullComp.WriteCoordsToTable()
				
			
def lightFromSelectedPix():
	
	selectedFixture = op.treeInfo_V2.par.Lastselected.eval()
	
	assert selectedFixture != None,'This OP is not valid, please check this out.'
		
	# lastSelHullComp = selectedFixture.op('hull')
	lastSelPixComp = selectedFixture.op('pix')
	
	# assert lastSelHullComp != None,'there is no hull comp inside of this fixture.. or is it a fixture? check this out'
	assert lastSelPixComp != None,'there is no pix comp inside of this fixture.. or is it a fixture? check this out'
	
	# get the selected fixture object.
	# selectedFixture = mod.tdUtils.getObjectList(criteria="directSelected")[0][0]
	
	# get the hull indicies string.
	# pixIndiciesStr = selectedFixture.op("hull").GetSelectedCoordIndiciesAsString()
	# totalPixCout = selectedFixture.op("pix").GetTotalNumberOfPix()
	
	selectedCoords = lastSelPixComp.GetSelectedCoords()
	# print(selectedCoords)
	# '''
	# if we only have 1 pix selected... proceed.
	
	newObjects = []
	
	if len(selectedCoords) <= 32:
		
		for coord in selectedCoords:
			
			# avgCenter = selectedFixture.op("pix").GetAvgCenterOfSelected()
			# avgCenter = coord[0:2]
			# avgCenter = mod.matrixUtils.LocalSpace_to_WorldSpace(selectedFixture, avgCenter[0], avgCenter[1], avgCenter[2])
			avgCenter = mod.matrixUtils.LocalSpace_to_WorldSpace(selectedFixture, coord[1], coord[2], coord[3])
			# print(avgCenter)
			# create light.
			createdLight = mod.create.Object("CreateLight")
			
			# set up the new light to be linked to the pix that was selected.
			createdLight.par.Tx = avgCenter[0]
			createdLight.par.Ty = avgCenter[1]
			createdLight.par.Tz = avgCenter[2]
			# createdLight.par.Rx = -90
			
			createdLight.par.Lightfixturelink = '..'
			createdLight.par.Lightpixlink = coord[0]
			createdLight.par.Lightrchanlink = 'r'
			createdLight.par.Lightgchanlink = 'g'
			createdLight.par.Lightbchanlink = 'b'
			createdLight.par.Lightpchanlink = 'p'
			createdLight.par.Lighttchanlink = 't'
			
			createdLight.par.Lightpminmax1 = 0
			createdLight.par.Lightpminmax2 = -540
			createdLight.par.Lighttminmax1 = 0
			createdLight.par.Lighttminmax2 = 180
			createdLight.par.Name = createdLight.name
			
			createdLight.par.Lightangle = 15
			
			newObjects += [createdLight]
			# set some parameters om the generator based on our selection.
			# createdGenerator.par.Hullcoords = pixIndiciesStr
			
			# no longer need this since start index is calculated dynamically by generator order.
			# createdGenerator.par.Startindex = totalPixCout
			
			# parent newly created generator to the fixture object.
			mod.tdUtils.parentObjectFlat( [createdLight] , selectedFixture )
			
			createdLight.par.Ry = 0
			
			createdLight.par.Pixlinkactive = True
			
		# enter object mode.
		# mod.execUtils.DelayedScript( 'op.tabArea.SetContext(0)' , parent(), 10 )
		debug('update this with new context mode switcher function, if needed!')
		# op.tabArea.SetContext(0)
	
	else:
		# debug("Trying to autocreate lights for more than 32 pix... please do less than 32 at a time for now.")
		op.NOTIFV2.Notify("Trying to autocreate lights for more than 32 pix... please do less than 32 at a time for now.")
	
	if len(newObjects):
		mod.tdUtils.selectItems(newObjects)
		
		
	
def SubdivideTwoHulls():
	'''
	This will take the currently selected fixture, and it's 
	currently selected hulls (must be 2) and add a new hull
	between the two hulls.
	'''
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelHullComp = lastSelObj.op('hull')
		if lastSelHullComp != None:
			lastSelHullComp.InsertCoord()
			lastSelHullComp.WriteCoordsToTable()
		
			
			
def SubdivideTwoPix():
	'''
	This will take the currently selected fixture, and it's 
	currently selected pix (must be 2) and add a new pix
	between the two pix.
	'''
	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	
	if lastSelObj != None:
		lastSelPixComp = lastSelObj.op('pix')
		if lastSelPixComp != None:
			lastSelPixComp.InsertCoord()
			lastSelPixComp.WriteCoordsToTable()
		
			
	
def runDoubleClickScriptOnLastSelected(targetOp=None, leftOrRight='left'):
	'''
	If no OP is provided, the last selected OP will be used.
	'''
	
	if targetOp == None:
		lastSel = op.treeInfo_V2.par.Lastselected.eval()
	else:
		lastSel = targetOp
	if lastSel != None:
		# debug('dbl CLICK FUCK')
		if leftOrRight == 'left':
			dblClkRun = lastSel.op('DOUBLECLICK/Run')
			if dblClkRun != None:
				# dblClkRun.run()
				pass
				
		elif leftOrRight == 'right':
		
			dblClkRun = lastSel.op('DOUBLECLICK/Run_R')
			if dblClkRun != None:
				# dblClkRun.run()
				pass
			
	return
	
	
def OpenStrobeEditor():
	
	controlPathsTable = op.Perform.op("ControlPaths")
	
	stroberRelated = [ x for x in list( map( str , controlPathsTable.col(0)[1::] ) ) if x.startswith('Strober/') ]
	if len(stroberRelated) > 0:
		# print('opening strober editor')
		op.Perform.op("Edit/Widget_Strober/auxUI_window").par.winopen.pulse()
	
	else:
		op.NOTIFV2.Notify('You need to create a Strobe Widget in the Perform Tab before you can access the Strobe Editor')
		op.PERFORM_notif_center.Notify('You need to create a Strobe Widget in the Perform Tab before you can access the Strobe Editor')
		
		
def RecalcHullsAndPix():
	# recalc fixtures
	found = mod.tdUtils_V2.getObjectList('all', 2)[0]
	for x in found:
		x.op('hull').WriteCoordsToTable()
		x.op('pix').WriteCoordsToTable()
	
	# recalc wires
	found = mod.tdUtils_V2.getObjectList('all', 4)[0]
	for x in found:
		x.op('hull').WriteCoordsToTable()
	
	
	
def EnableDisableAllDevices(state=True):
	# recalc fixtures
	found = mod.tdUtils_V2.getObjectList('all', 3)[0]
	for x in found:
		x.par.Active = state
	
	
def FixureWizardCreate_______________________(chans='r,g,b', relPos=[0,0,0] , objName = 'Un-named' , deviceID = 1, linkageDict={}):
	### not currently in use
	# mod.execUtils.DelayedScript( 'op.tabArea.SetContext(0)' , parent(), 10 )
	debug('update this with new context mode switcher, if needed!')
	
	highestOffset = mod.tdUtils.getFixturesHighestOffset( [deviceID] )
	
	try:
		Chansize = highestOffset['Object'].par.Chansize.eval()
	except:
		Chansize = 0
	
	createdFixture = mod.create.Object("CreateFixture", doInit=False)
	createdFixture.par.Chanorder = chans
	lastSelPixComp = createdFixture.op('pix')
	if(lastSelPixComp):
		lastSelPixComp.AddPixRaw( relPos[0] , relPos[1] , relPos[2] , xtraChans=chans.split(',') )
		lastSelPixComp.SelectLast()
		lastSelPixComp.WriteCoordsToTable()
	
	createdFixture.par.Pixscale = 32
	
	createdFixture.par.Name = objName
	mod.strUtils.makeNameUnique(createdFixture)
	
	createdFixture.par.Fdeviceid = deviceID
	
	if highestOffset != None:
		# nextOffset = mod.tdUtils.calculateAddressOffsetFromCurrent( createdFixture, highestOffset )
		nextOffset = mod.tdUtils.calculateAddressOffsetFromLast( createdFixture, highestOffset )
	else:
		nextOffset = {'Net':1, 'Subnet':1, 'Universe':1, 'Channel':1}
		
	createdFixture.par.Net = nextOffset['Net']
	createdFixture.par.Subnet = nextOffset['Subnet']
	createdFixture.par.Universe = nextOffset['Universe']
	createdFixture.par.Channel = nextOffset['Channel']
	
	# '''
	if len(linkageDict):
	
		createdLight = mod.create.Object("CreateLight")
		
		# set up the new light to be linked to the pix that was selected.
		createdLight.par.Tx = createdFixture.par.Tx.eval() + relPos[0]
		createdLight.par.Ty = createdFixture.par.Ty.eval() + relPos[1]
		createdLight.par.Tz = createdFixture.par.Tz.eval() + relPos[2]
		# createdLight.par.Rx = -90
		
		# createdLight.par.Lightfixturelink = createdFixture.par.Name # we used to use this to set a name directly, but now we opt for the parent shortcut syntax.
		createdLight.par.Lightfixturelink = '..'
		createdLight.par.Lightpixlink = 0
		
		for k,v in linkageDict.items():
			# print(k,v)
			foundPar = getattr( createdLight.par , k , ':ERR:' )
			if foundPar != ':ERR:':
				foundPar.val = v
		
		# these hardcoded settings set things up for movers that are 540 degrees of pan and 240 degrees of tilt.
		createdLight.par.Lightpminmax1 = 0
		createdLight.par.Lightpminmax2 = -540
		createdLight.par.Lighttminmax1 = 0
		createdLight.par.Lighttminmax2 = 180
		createdLight.par.Name = createdFixture.par.Name + '_LightViz'
		createdLight.par.Lightangle = 15
		
		mod.tdUtils.parentObjectFlat( [createdLight] , createdFixture )
		createdLight.par.Ry = 0
		createdLight.par.Pixlinkactive = True
		
	# '''
	
	# enter object mode.
	# mod.execUtils.DelayedScript( 'op.tabArea.SetContext(0)' , parent(), 10 )
	debug('update this with new set context function! if needed')
	
	
def FitProjectorToFixtures( projectors=[], fixtures=[] ):
	
	# print(projectors)
	# print(fixtures)

	for i,p in enumerate(projectors):
		
		
		realFixtures = [op(x) for x in fixtures if op(x) != None]
		realFixtures = [x for x in realFixtures if x.par.Objtype.eval() == 2]

		if len(realFixtures):
			
			numPixInEach = [ n.op('pix').GetTotalNumberOfPix() for n in realFixtures if n.op('pix') ]
			pixSum = sum(numPixInEach)
			
			if pixSum > 0:
				
				r = mod.matrixUtils.ProjectionBoundsFromFixtures_v2(p,realFixtures)
				
				p.par.Tx = r['t']['x']
				p.par.Ty = r['t']['y']
				p.par.Tz = r['t']['z']

				p.par.Rx = r['r']['x']
				p.par.Ry = r['r']['y']
				p.par.Rz = r['r']['z']

				p.par.Sx = r['s']['x']
				p.par.Sy = r['s']['y']
				p.par.Sz = r['s']['z']
				


def ObjectSelect_All():
	'''
	Selects all the objects in the scene, also updates last selected.
	'''
	mod.tdUtils.selectAllItems()
	return

def ObjectSelect_None():
	'''
	Selects all the objects in the scene, also updates last selected.
	'''
	mod.tdUtils.deselectAllItems()
	return

def ObjectSelect_Up():
	'''
	Selects all parents of selected objects if they exist.
	'''
	directSelected = mod.tdUtils.getObjectList("directSelected")[0]
	parents = [ mod.tdUtils.getObjectsParent(x) for x in directSelected ]
	parents = [x for x in parents if x != None]
	parents = list(set(parents))
	# print(parents)
	
	if len(parents): # if there was at least 1 item in the result.
		
		for each in directSelected: # deselect previous.
			each.par.Selected = 0
		
		for each in parents: # select new.
			each.par.Selected = 1
		
		op.treeInfo_V2.par.Lastselected = parents[-1]
		
	else:
		op.NOTIFV2.Notify('No parent objects to select.')
	
	return
	
	
def ObjectSelect_Down():
	'''
	Selects all children of selected objects.
	'''
	directSelected = mod.tdUtils.getObjectList("directSelected")[0]
	children = [ mod.tdUtils.getObjectsChildren(x) for x in directSelected ]
	children = [x for subset in children for x in subset]
	children = list(set(children))
	
	if len(children): # if there was at least 1 item in the result.
		
		for each in directSelected: # deselect previous.
			each.par.Selected = 0
		
		for each in children: # select new.
			each.par.Selected = 1
			# pass
		
		op.treeInfo_V2.par.Lastselected = children[-1]
		
	else:
		op.NOTIFV2.Notify('No children objects to select.')
	
	return
	
def MergeSelectedFixtures():
	
	debug("MergeSelectedFixtures() is currently broken, and needs to be fixed.")
	return

	lastSelObj = op.treeInfo_V2.par.Lastselected.eval()
	directSelected = mod.tdUtils.getObjectList("directSelected")[0]
	sortedSelected = mod.tdUtils.outlinerSort(directSelected)
	
	
	if len(sortedSelected) == 0:
		op.NOTIFV2.Notify('Please select two or more Fixture objects, or a single Fixture with instances to merge.')
	
	elif lastSelObj == None:
		op.NOTIFV2.Notify('Please de-select all, and reselect Fixtures again using shift to select multiple.')
	
	else:
		
		if len(sortedSelected) <= 1:
			
			if len(sortedSelected) == 1:
				fixtureOp = sortedSelected[0]
				
				fixtureDataOp = op.Gather.op( "TYPE_2/" + fixtureOp.name )
				INST_XYZ = fixtureDataOp.op('INST_XYZ')
				INST_ATTRS = fixtureDataOp.op('INST_ATTRS')
				fixtureWorldMat = fixtureDataOp.worldTransform
				
				allNames = [ x.name for x in INST_ATTRS.chans() ]
				chanNames = [ x for x in allNames if x.startswith( '___' ) and x.endswith( '___' ) ]
				maskNames = [ x for x in allNames if x.startswith( '::' ) and x.endswith( '::' ) ]
				
				masterDict = {}
				
				for i,point in enumerate(INST_XYZ.points):
					worldPos = fixtureWorldMat * tdu.Position( point.x , point.y , point.z )
					
					masterDict[i] = {}
					masterDict[i]['coords'] = {}
					masterDict[i]['coords']['x'] = {'val': worldPos.x}
					masterDict[i]['coords']['y'] = {'val': worldPos.y}
					masterDict[i]['coords']['z'] = {'val': worldPos.z}
					
					masterDict[i]['chans'] = {}
					for chan in chanNames:
						chan = chan.replace('_','')
						min = chan + '_min'
						max = chan + '_max'
						masterDict[i]['chans'][chan] = { 'min':INST_ATTRS[min][i] , 'max':INST_ATTRS[max][i] }
					
					masterDict[i]['masks'] = {}
					for mask in chanNames:
						maskName = mask.replace(':','')
						masterDict[i]['masks'][maskName] = { 'val':INST_ATTRS[mask][i] }
						
					masterDict[i]['selected'] = INST_ATTRS['selected'][i]
						
				
				createdFixture = mod.create.Object("CreateFixture", doInit=False)
				
				createdFixture.op('pix').ReplacePixDict(masterDict)
				
				createdFixture.par.Name = 'CombinedFixture'
				mod.strUtils.makeNameUnique(createdFixture)
				
				createdFixture.par.Pixscale = lastSelObj.par.Pixscale
				createdFixture.par.Chanorder = lastSelObj.par.Chanorder
				createdFixture.par.Fdeviceid = lastSelObj.par.Fdeviceid
				
				createdFixture.par.Net = lastSelObj.par.Net
				createdFixture.par.Subnet = lastSelObj.par.Subnet
				createdFixture.par.Universe = lastSelObj.par.Universe
				createdFixture.par.Channel = lastSelObj.par.Channel
			
			if len(sortedSelected) == 0:
				op.NOTIFV2.Notify('Please select two or more Fixture objects, or a single Fixture with instances to merge.')
		
		else:
		
			illegalTypes = [x for x in sortedSelected if x.par.Objtype.eval() != 2]
			# print(sortedSelected)
			if len(illegalTypes) > 0: # if user has anything other than fixtures selected...
				op.NOTIFV2.Notify('Can only merge Fixture object types. Make sure all selected objects are Fixtures.')
			else:
				
				masterDict = {}
				counter = 0
				
				for each in sortedSelected:
					# print(each.op('pix'))
					pixDictWorld = each.op('pix').GetPixDictAsWorldSpace()
					
					for k,v in pixDictWorld.items():
						# print(k,v)
						masterDict[counter] = v
						counter += 1
				
				# for k,v in masterDict.items():
					# print(k,v)
				
				# print(masterDict)
			
				createdFixture = mod.create.Object("CreateFixture", doInit=False)
				
				createdFixture.op('pix').ReplacePixDict(masterDict)
				
				createdFixture.par.Name = 'CombinedFixture'
				mod.strUtils.makeNameUnique(createdFixture)
				
				createdFixture.par.Pixscale = lastSelObj.par.Pixscale
				createdFixture.par.Chanorder = lastSelObj.par.Chanorder
				createdFixture.par.Fdeviceid = lastSelObj.par.Fdeviceid
				
				createdFixture.par.Net = lastSelObj.par.Net
				createdFixture.par.Subnet = lastSelObj.par.Subnet
				createdFixture.par.Universe = lastSelObj.par.Universe
				createdFixture.par.Channel = lastSelObj.par.Channel
	
	return
	
def SelectSystemNodes(nodeName=''):
	
	if nodeName == '':
		op.ATRIB_V6.Clear()
	
	elif nodeName == 'EditorCam':
		selOp = op.Viewport.op('cam')
		op.ViewPortUI.ClickButton( "ObjectMode" )
		mod.tdUtils.deselectAllItems()
		op.treeInfo_V2.par.Lastselected = selOp
		
		mod.execUtils.DelayedScript( 'op.ATRIB_V6.Launch(op("%s"),[op("%s")])'%( selOp.path , selOp.path ) , parent() )
		
	
	elif nodeName == 'EditorVolumetrics':
		selOp = op.Viewport
		op.ViewPortUI.ClickButton( "ObjectMode" )
		mod.tdUtils.deselectAllItems()
		op.treeInfo_V2.par.Lastselected = selOp
		
		mod.execUtils.DelayedScript( 'op.ATRIB_V6.Launch(op("%s"),[op("%s")])'%( selOp.path , selOp.path ) , parent() )
		
	
def Projectors_WidthFromAspect():
	directSelected = mod.tdUtils.getObjectList("directSelected")[0]
	selectedProjectors = [x for x in directSelected if x.par.Objtype == 9]
	for each in selectedProjectors:
		each.par.Fitaspectx.pulse()
		
	
def Projectors_HeightFromAspect():
	directSelected = mod.tdUtils.getObjectList("directSelected")[0]
	selectedProjectors = [x for x in directSelected if x.par.Objtype == 9]
	for each in selectedProjectors:
		each.par.Fitaspecty.pulse()
		
	
def Projectors_FitToScene():
	directSelected = mod.tdUtils.getObjectList("directSelected")[0]
	selectedProjectors = [x for x in directSelected if x.par.Objtype == 9]
	for each in selectedProjectors:
		each.par.Fitscene.pulse()
		
	
def Projectors_FitToSelection():
	directSelected = mod.tdUtils.getObjectList("directSelected")[0]
	selectedProjectors = [x for x in directSelected if x.par.Objtype == 9]
	AllListsPassLengthTest = len(selectedProjectors) > 0
	
	if AllListsPassLengthTest == False:
		op.NOTIFV2.Notify('Your current selection is invalid, please include one or more Projector(s) in your selection.')
		
	for each in selectedProjectors:
		each.par.Fitselection.pulse()
		
	
def Generators_ForceRegen():
	directSelected = mod.tdUtils.getObjectList("directSelected")[0]
	selectedGenerators = [x for x in directSelected if x.par.Objtype == 7]
	
	AllListsPassLengthTest = len(selectedGenerators) > 0
	
	if AllListsPassLengthTest == False:
		op.NOTIFV2.Notify('Your current selection is invalid, please include one or more Generators(s) in your selection.')
		
	for each in selectedGenerators:
		each.par.Regen.pulse()
		
	
def Generators_RotateIDs():
	directSelected = mod.tdUtils.getObjectList("directSelected")[0]
	selectedGenerators = [x for x in directSelected if x.par.Objtype == 7]
	
	AllListsPassLengthTest = len(selectedGenerators) > 0
	
	if AllListsPassLengthTest == False:
		op.NOTIFV2.Notify('Your current selection is invalid, please include one or more Generators(s) in your selection.')
		
	for each in selectedGenerators:
		each.par.Rotateids.pulse()
		
	
def SelectionSet_SelectSet():
	directSelected = mod.tdUtils.getObjectList("directSelected")[0]
	selectedSets = [x for x in directSelected if x.par.Objtype == 10]
	
	AllListsPassLengthTest = len(selectedSets) > 0
	
	if AllListsPassLengthTest == False:
		op.NOTIFV2.Notify('Your current selection is invalid, please include one or more Selection Set(s) in your selection.')
		
	for each in selectedSets:
		each.par.Selectset.pulse()


def ParentSelectedToLast():

	sel = mod.tdUtils.multiParentToLast()
	mod.tdUtils.deselectAllItems()
	mod.tdUtils.selectItems( sel )


	
def RefreshAllFixtures():
	f = op.geoHolder.findChildren(name='forceUpdateWriteCoordsToTable')
	for each in f:
		each.run()
	
	
def GenBlockFixtures_______________(fixtureList = []):
	'''
	If any of the supplied fixtures have generators in place, we set genblock to True. 
	If no generators were found, then we do not need to set gen block.
	'''
	
	for each in fixtureList:
		each = op(each)
		if each != None:
			children = mod.tdUtils.getObjectsChildren(each)
			c = [x for x in children if x.par.Objtype == 7]
			if len(c) > 0:
				try:
					each.par.Genblock = True
				except:
					debug('Could not set Genblock to True, prob doesnt exist, this shouldnt happen, look into it!')


def ExitPrompt():

	prompterDict = {}
	prompterDict['label'] = 'Save changes before closing?'
	prompterDict['options'] = {
								"Save":"op.SAVE_LOAD.Launch(mode='saveproject', quitAfterSave=True)",
								"Don't Save":"project.quit(force=True)",
								"Cancel":"parent.helper.Close()",
								}

	op.Prompter.Launch( prompterDict )
	op.SplashScreen.par.display = False
	return 


def NewPrompt():

	prompterDict = {}
	prompterDict['label'] = 'Create new file, are you sure?'
	prompterDict['options'] = {
								"New File":"op.STARTUP_SCRIPTS.op('makeVanilla').run( [ 'Fullscreen' ] ); parent.helper.Close()",
								"Cancel":"parent.helper.Close()",
								}

	op.Prompter.Launch( prompterDict )
	op.SplashScreen.par.display = False
	return 


def EditFixturePrompt():

	prompterDict = {}
	prompterDict['label'] = 'Fixture edit mode?'
	prompterDict['options'] = {
								"Hulls":"op.ViewPortUI.ClickButton('HullMode')\nparent.helper.Close()",
								"Pix":"op.ViewPortUI.ClickButton('PixMode')\nparent.helper.Close()",
								}

	op.Prompter.Launch( prompterDict )

	return 


def ExitSubModePrompt():

	prompterDict = {}
	prompterDict['label'] = 'Exit edit mode?'
	prompterDict['options'] = {
								"Yes":"op.ViewPortUI.ClickButton('ObjectMode')\nparent.helper.Close()",
								}

	op.Prompter.Launch( prompterDict )

	return 




def EditSurfacePrompt():

	prompterDict = {}
	prompterDict['label'] = 'Surface edit mode?'
	prompterDict['options'] = {
								"Hulls":"op.ViewPortUI.ClickButton('HullMode')\nparent.helper.Close()",
								}

	op.Prompter.Launch( prompterDict )

	return 


def ExportDmxOutputModule():

	dmxBufferPath = ui.chooseFile(load=True, fileTypes=tdu.fileTypes['movie'], title='Choose the DMX buffer video from disk...')
	if dmxBufferPath == None:
		debug('dmxBufferPath was None, operation was cancelled.. doing nothing.')
		return


	toxPath = ui.chooseFile(load=False, fileTypes=['tox'], title='Save DMX Output Module as...')
	if toxPath == None:
		debug('toxPath was None, operation was cancelled.. doing nothing.')
		return

	outputModule = op.OUTPUT_MODULE

	ExportOutputModule = outputModule.parent().copy( outputModule, name='OUTPUT_MODULE_1' )

	ExportOutputModule.nodeX += 1000
	ExportOutputModule.par.opshortcut = ''
	ExportOutputModule.par.extension1 = ''
	f = ExportOutputModule.findChildren( tags=['EXPORT_DELETE'])
	for each in f:
		try:
			each.destroy()
		except:
			pass

	f = ExportOutputModule.findChildren(depth=1, tags=['OUT_DEVICE'])
	for each in f:
		if each.par.Active == False:
			each.destroy()
		else:
			protocol = each.par.Protocol.eval()
			f2 = each.findChildren(depth=1, tags=['PROTOCOLS'])
			for item in f2:
				if item.name != protocol:
					item.destroy()

	ExportOutputModule.op('base_convert_to_chops_and_rename/in_outputsCompressed').outputConnectors[0].connect(
		ExportOutputModule.op('base_convert_to_chops_and_rename/null_output')
		)

	nodeWidth = int(ExportOutputModule.op('select_fixture_buffer').nodeWidth)
	nodeHeight = int(ExportOutputModule.op('select_fixture_buffer').nodeHeight)
	nodeX = int(ExportOutputModule.op('select_fixture_buffer').nodeX)
	nodeY = int(ExportOutputModule.op('select_fixture_buffer').nodeY)
	ExportOutputModule.op('select_fixture_buffer').destroy()

	evalDAT = ExportOutputModule.create(evaluateDAT)
	evalDAT.viewer = True
	evalDAT.nodeX = nodeX - 150
	evalDAT.nodeY = nodeY
	evalDAT.name = 'VFS_PATH'
	evalDAT.par.expr = "parent.OUTPUT_MODULE.vfs.find(pattern='*')"


	vfsFile = ExportOutputModule.vfs.addFile(dmxBufferPath)
	virtPath = vfsFile.virtualPath

	top = ExportOutputModule.create(moviefileinTOP)
	top.nodeWidth = nodeWidth
	top.nodeHeight = nodeHeight
	top.nodeX = nodeX
	top.nodeY = nodeY
	top.name = "DMX_BUFFER_VIDEO"
	top.par.file.expr = f'op("{evalDAT.name}")[0,0]'

	top.outputConnectors[0].connect(ExportOutputModule.op('base_convert_to_chops_and_rename').inputConnectors[0])
	ExportOutputModule.op('select_bofferLookupTable').lock = True

	# ExportOutputModule.op('DELAYED_EXPORT').run(toxPath, delayFrames=30)
	# ExportOutputModule.op('DELAYED_DESTROY').run(toxPath, delayFrames=60)
	ExportOutputModule.save( toxPath )
	ExportOutputModule.destroy()

	return