geoHolder 	= op.sceneOutliner.op("geoHolder")
multiSel 	= op.sceneOutliner.op("null_multiSelect")
postLoadScript = op.sceneOutliner.op("geoHolder").op("postLoadScript")
treeInfo_V3 = op.sceneOutliner.op("null_treeInfo_V3")
sceneVars = op.sceneOutliner.op("sceneVars")





import matrixUtils
import fnmatch
from collections import defaultdict
# import yaml
from copy import copy
import collections
import colorsys
import os
import natsort

TDJ = op.TDModules.mod.TDJSON


ProjectorParamsToGet = [[ 'myName' , 'name'],
						[ 'Name' , 'Name'], 
						[ 'Tx' , 'tx'],
						[ 'Ty' , 'ty'],
						[ 'Tz' , 'tz'],
						[ 'Rx' , 'rx'],
						[ 'Ry' , 'ry'],
						[ 'Rz' , 'rz'],
						[ 'Sx' , 'sx'],
						[ 'Sy' , 'sy'],
						[ 'Sz' , 'sz'],
						[ 'Visible' , 'Visible'],
						[ 'Pscale' , 'Pscale'],
						[ 'Pstyle' , 'style'],
						[ 'Pextend' , 'extend'],
						[ 'Routingr' , 'RoutingR'],
						[ 'Routingg' , 'RoutingG'],
						[ 'Routingb' , 'RoutingB'],
						[ 'Routinga' , 'RoutingA'],
						[ 'Inputpreview' , 'Input'],
						[ 'Masking' , 'Masking'],
						[ 'Maskmode' , 'Maskmode'],
						[ 'Coloroverride' , 'Coloroverride'],
						[ 'Setcolor1' , 'Setcolor1'],
						[ 'Setcolor2' , 'Setcolor2'],
						[ 'Setcolor3' , 'Setcolor3'],
						[ 'Setcolor4' , 'Setcolor4'],
						[ 'Res1' , 'Res1'],
						[ 'Res2' , 'Res2'],
						[ 'Active' , 'Active'],
						[ 'Gamma' , 'Gamma'],
						[ 'Gain' , 'Gain'],
						[ 'Uvfxorigin' , 'Uvfxorigin'],
						[ 'Uvfxshuffle' , 'Uvfxshuffle'],
						[ 'Projectorblendmode' , 'Projectorblendmode'],
						[ 'Projectorlayer' , 'Projectorlayer'],
						]


def outlinerSort(objects=[], strings=False):

	####### NEW SORTING METHOD! WAY FASTTTTTER
	objects = [ x for x in objects if x != None ] 
	# sortedObjects = sorted(objects, key=lambda obj: (os.path.dirname(obj.par.Namepath.eval()), os.path.basename(obj.par.Namepath.eval())))

	if strings == False:
		# sortedObjects = sorted(objects, key=lambda obj: (  -obj.par.Namepath.eval().count(os.path.sep)  , obj.par.Namepath.eval()  )  ) # faster, but doesnt natsort
		natsort_key2 = natsort.natsort_keygen(key=lambda y: y.par.Namepath.eval())
		sortedObjects = sorted( objects , key=natsort_key2 ) # VERY robust, but slower.
		
	else:
		# sortedObjects = sorted(objects, key=lambda p: (-p.count(os.path.sep), p)) # roughly 4 times faster than below, but doesn't handle nat sort.
		sortedObjects = natsort.natsorted(objects) # slower, but super robust and handles ALL kind of shit.

	return sortedObjects


def getObjectsSortedIDByType(myOp):
	'''
	Given a GP editor object type, this function gets the user name, and the objType int, and then retrieves all items in the scene
	of that object type. Then, it will determine the index, of the originally provided object, in that list, by using it's name.
	'''
	Name = myOp.par.Name.eval()
	Objtype = myOp.par.Objtype.eval()
	allOfType = getObjectList( "all" , Objtype )[0]
	allOfTypeSorted = outlinerSort(allOfType)
	allOfTypeSortedNames = [ x.par.Name.eval() for x in allOfTypeSorted ]
	NameIndex = allOfTypeSortedNames.index(Name)

	return NameIndex


def getObjectFromIndexAndType(indexVal, ObjtypeInt):
	'''
	Given an assumed valid outliner sorted index, and an object type int, this function wiill
	return a reference to the OP that matches that index.
	'''
	allOfType = getObjectList( "all" , ObjtypeInt )[0]
	allOfTypeSorted = outlinerSort(allOfType)

	assert indexVal < len(allOfTypeSorted), "index provided cannot be higher than the list length."

	return allOfTypeSorted[indexVal]


### parents all but the last selected item, to the last selected item.
def multiParentToLast():
	if(multiSel.numRows > 0):
		childList = []
		lastSel = op.treeInfo_V2.par.Lastselected.eval()
		for x in range(multiSel.numRows):
			xOP = multiSel[x,0]
			if op(xOP) != lastSel:
				childList += [xOP.val]
		parentObjectFlat(childList, lastSel)
	return [lastSel]

### unparents all selected items. (they will return to root.)
def multiUnParent():
	
	directSelected = getObjectList("directSelected")[0]

	for xOP in directSelected:
		
		if sceneVars.op("null_parentInPlace")[0] == 1:
			myOpParent = geoHolder
			r = matrixUtils.Calculate_Difference_Matrix(xOP, myOpParent)
			xOP.par.Tx = r[0]
			xOP.par.Ty = r[1]
			xOP.par.Tz = r[2]
			xOP.par.Rx = r[3]
			xOP.par.Ry = r[4]
			xOP.par.Rz = r[5]
			xOP.par.Sx = r[6]
			xOP.par.Sy = r[7]
			xOP.par.Sz = r[8]

			if hasattr(xOP.par , 'Uniformscale'):
				xOP.par.Uniformscale = 1.0 # our matrix calculation assumes we're applying all scale through sx/sy/sz. this must be neutralized.
		
		xOP.inputCOMPConnectors[0].disconnect()
	return

### unparents all selected items. (they will return to root.)
def UnParentProvidedObjects(objList):
	for xOP in objList:
		if sceneVars.op("null_parentInPlace")[0] == 1:
			myOpParent = geoHolder
			# r = matrixUtils.neutralize_Parent_Transform(xOP, myOpParent)
			r = matrixUtils.Calculate_Difference_Matrix(xOP, myOpParent)
			xOP.par.Tx = r[0]
			xOP.par.Ty = r[1]
			xOP.par.Tz = r[2]
			xOP.par.Rx = r[3]
			xOP.par.Ry = r[4]
			xOP.par.Rz = r[5]
			xOP.par.Sx = r[6]
			xOP.par.Sy = r[7]
			xOP.par.Sz = r[8]

			if hasattr(xOP.par , 'Uniformscale'):
				xOP.par.Uniformscale = 1.0 # our matrix calculation assumes we're applying all scale through sx/sy/sz. this must be neutralized.
		
		xOP.inputCOMPConnectors[0].disconnect()
		xOP.cook(force=1)

	return

### parent a list of objects to a single target.
def parentObjectFlat(opsToParent, target):
	target_ = op(target)
	# print(opsToParent,target)
	foundChildren = fetchChildrenRecursively( [ op(y).name for y in opsToParent ] )
	foundChildren = [x.name for x in foundChildren]
	
	# this prevents us from causing cyclical parenting.
	if target.name not in foundChildren:
	
		for x in opsToParent:
			xOP = op(x)
			
			if sceneVars.op("null_parentInPlace")[0] == 1:
				# calculate the difference in offset of the object after parenting
				# and subtract this to keep the object in the same place.
				# r = matrixUtils.neutralize_Parent_Transform(xOP, target_)
				r = matrixUtils.Calculate_Difference_Matrix(xOP, target_)
				xOP.par.Tx = r[0]
				xOP.par.Ty = r[1]
				xOP.par.Tz = r[2]
				xOP.par.Rx = r[3]
				xOP.par.Ry = r[4]
				xOP.par.Rz = r[5]
				xOP.par.Sx = r[6]
				xOP.par.Sy = r[7]
				xOP.par.Sz = r[8]

				if hasattr(xOP.par , 'Uniformscale'):
					xOP.par.Uniformscale = 1.0 # our matrix calculation assumes we're applying all scale through sx/sy/sz. this must be neutralized.
			
			xOP.inputCOMPConnectors[0].disconnect()
			target_.outputCOMPConnectors[0].connect(xOP)

	else:
		op.NOTIFV2.Notify('You cannot parent an object, to a child object within its own hierarchy.')



	return
	
### parent a list of objects to a single target.
def parentObjectFlat_BLIND(opsToParent, target):
	target_ = op(target)
	
	for x in opsToParent:
		xOP = op(x)
		xOP.inputCOMPConnectors[0].disconnect()
		target_.outputCOMPConnectors[0].connect(xOP)
		xOP.cook(force=1)
	target_.cook(force=1)
	
	
	return

	
### supply an array of OP paths to objects that have a custom Select param.
### to allow this function to mark them as selected.
def selectItems(itemArray):
	for x in itemArray:
		thisOp = op(str(x))
		if thisOp == None:
			thisOp = geoHolder.op(str(x))
		assert thisOp != None, 'Something went wrong, please check this out.'
		thisOp.par.Selected = 1
		thisOp.current = 1
		
		ls = op(treeInfo_V3[thisOp.name,'dataPath'])
		if ls != None:
			ls.current  = 1
	op.treeInfo_V2.par.Lastselected = geoHolder.op(itemArray[-1]) if len(itemArray) else ''

	return

	
### supply an array of OP paths to objects that have a custom Select param.
### to allow this function to mark them as selected.
def deselectItems(itemArray):
	for x in itemArray:
		
		thisOp = op(str(x))
		if thisOp == None:
			thisOp = geoHolder.op(str(x))
		assert thisOp != None, 'Something went wrong, please check this out.'
		
		thisOp.par.Selected = 0
	
	sel = op.sceneOutliner.mod.tdUtils.getObjectList( criteria='directSelected' )
	if len(sel[0]) > 0:
		op.treeInfo_V2.par.Lastselected = sel[0][-1]
	else:
		op.treeInfo_V2.par.Lastselected = ''
	return

	
### supply an array of OP paths to objects that have a custom Select param.
### to allow this function to mark them as selected.
def invertSelectItems(itemArray=[]):
	
	if len(itemArray) == 0:
		itemArray = geoHolder.findChildren(type=geometryCOMP, parName='Objtype', maxDepth=1)
		itemArray = [x.path for x in itemArray]
	
	lastSel = None
	
	for x in itemArray:
		
		thisOp = op(str(x))
		if thisOp == None:
			thisOp = geoHolder.op(str(x))
		assert thisOp != None, 'Something went wrong, please check this out.'
		
		thisOp.par.Selected = 1 - thisOp.par.Selected
		if thisOp.par.Selected == 1:
			lastSel = thisOp
		
	if lastSel != None:
		op.treeInfo_V2.par.Lastselected = lastSel
	else:
		op.treeInfo_V2.par.Lastselected = ''
		
	return
	
### deselects all objects.
def deselectAllItems():
	foundResults = geoHolder.findChildren(type=geometryCOMP, parName='Objtype', maxDepth=1)
	for x in foundResults:
		x.par.Selected = 0
	op.treeInfo_V2.par.Lastselected = ''
	return
	
### selects all objects.
def selectAllItems():
	foundResults = geoHolder.findChildren(type=geometryCOMP, parName='Objtype', maxDepth=1)
	lastSel = ''
	for x in foundResults:
		x.par.Selected = 1
		lastSel = x
	op.treeInfo_V2.par.Lastselected = lastSel
	return

def deleteSelectedItems():
	
	mod.tdUtils_V2.killAllRuns()
	disableActivePik()
	
	# get list of allSelected items.
	combinedList = getObjectList("allSelected")[0]
	
	for x in combinedList:
		try:
			x.destroyCustomPars()
		except Exception as e: 
			debug(e)
	
	for x in combinedList:
		try:
			DEL_Run = x.op('DEL/Run')
			if DEL_Run != None:
				DEL_Run.run()
			else:
				debug('no delete script found, moving on.')
			x.destroy()
		except Exception as e: 
			debug(e)
			
	op.treeInfo_V2.par.Lastselected = ''

def deleteAllItems():
	
	mod.tdUtils_V2.killAllRuns()
	disableActivePik()
	
	# destroy PROTOCOL OP's first. they like to throw a ton of errors on their way out.
	protocolOps = geoHolder.findChildren(name="PROTOCOL")
	for x in protocolOps:
		x.destroy()
	
	
	# get list of all items.
	combinedList = getObjectList("all")[0]
	
	# then we delete all the actual OPS
	for x in combinedList:
		thisOp = x
		try:
			thisOp.destroy()
		except Exception as e: 
			# print(e)
			debug("trying to delete all objects...", e)
	
	op.treeInfo_V2.par.Lastselected = ''
	


def duplicateSelectedItems_withOffset(tx=0, ty=0, tz=0 , rx=0 , ry=0 , rz=0):
	
	newItems = duplicateSelectedItems_V2()
	m = tdu.Matrix()
	m.rotate(rx,ry,rz)
	
	for item in newItems:
		pos = m * tdu.Position(item.par.Tx.eval(), item.par.Ty.eval(), item.par.Tz.eval())
		
		item.par.Tx = pos.x + tx
		item.par.Ty = pos.y + ty
		item.par.Tz = pos.z + tz
		
		item.par.Rx += rx
		item.par.Ry += ry
		item.par.Rz += rz
	
	# if the item is a fixture, attempt to Cook the pix after duplication.
	for item in newItems:
		thesePars = item.pars("Objtype")
		if len(thesePars) == 1:
			if thesePars[0].val == "fixture":
				item.op("pix").Cook_PixToWorldSpace()
				item.op("pix").Cook()
	
	
	return

### this will duplicate the selected items and mirror them on the axis's enabled
### in the tools area.
def mirrorDuplicateSelectedItems(tx=0, ty=0, tz=0)	:
	
	# newItems = duplicateSelectedItems()
	newItems = duplicateSelectedItems_V2()
	newItems2 = getObjectList("directSelected")
	
	for item in newItems2[0]:
		localMat = item.localTransform
		sx = ((1-tx)*2)-1
		sy = ((1-ty)*2)-1
		sz = ((1-tz)*2)-1
		
		item.par.Tx *= sz
		item.par.Ty *= sy
		item.par.Tz *= sx

		if(sy == -1):
			item.par.Rx = 180 - item.par.Rx
		if(sx == -1):
			item.par.Ry = 180 - item.par.Ry
		if(sz == -1):
			item.par.Ry = 180 - item.par.Ry
			
			
	# if the item is a fixture, attempt to Cook the pix after duplication.
	for item in newItems2[0]:
		thesePars = item.pars("Objtype")
		if len(thesePars) == 1:
			if thesePars[0].val == "fixture":
				item.op("pix").Cook_PixToWorldSpace()
				item.op("pix").Cook()
	
	
	return

	
def fetchChildrenRecursively(startingObjects=[], levelsDeep=99):
	'''
	Psuedo recursively fetches all children of given parents, by the supplied number deep.
	default of 99 basically "guarantees" that we'll get all children cause who would have
	a scene going that deep...
	'''
	foundChildren = []
	currentLevel = startingObjects
	for level in range(levelsDeep):
		nextLevel = []
		for object in currentLevel:
			
			found = [ x.name for x in getObjectsChildren(geoHolder.path + "/" + object) ]
			# found = getObjectsChildren(geoHolder.path + "/" + object)
			nextLevel += found
		
		currentLevel = nextLevel
		foundChildren += nextLevel# [ x.name for x in nextLevel ]
	
	foundChildren = [geoHolder.op(x) for x in foundChildren]
	
	return foundChildren
	

def fetchHierarchyVisibility( startingObject , levelsDeep=99 ):
	
	VizState = startingObject.par.Visible.eval()

	levelsDeep = [ 0 , levelsDeep ][VizState]

	for level in range(levelsDeep):
		startingObject = getObjectsParent(startingObject)
		if startingObject == None:
			return VizState
		else:
			if startingObject.par.Visible.eval() == False:
				return False
		pass

	return VizState




# these are recursive functions.
def tree(): return defaultdict(tree)
def dicts(t): return {k: dicts(t[k]) for k in t}
def fetchParentRecursively(treeList=[]):
	if len(treeList) > 0 and len(treeList) < 10:
		foundParent = getObjectsParent(geoHolder.path + "/" + treeList[0])
		if foundParent:
			
			treeList.insert(0,str(foundParent.name))
			return fetchParentRecursively(treeList)
		else:
			return treeList
	else:
		return treeList
def get_keys(d, target):
    for k, v in d.items():
        path.append(k)
        if isinstance(v, dict):
            get_keys(v, target)
        if v == target:
            result.append(copy(path))
        path.pop()
# this is not a recursive function.
def add( t, path ):
	for node in path:
		t = t[node]
		

def pruneIDs():
	found = geoHolder.findChildren(tags=["ObjectType"], maxDepth=1)
	for i, Op in enumerate(found):
		i += 1
		
		if Op.pars("Id"):
			Op.par.Id = i
		
	

### this new duplicate duplicates the selection 1 object at a time instead of using derivative's
### copyOPS which in theory is great because it keeps wiring intact, but problems sprung up recently with
### references to OPs being created before they were actually available in the same frame.
### doing the copy one at a time mitigates that.
def duplicateSelectedItems_V2():
	

	# get list of all selected objects.
	combinedList = getObjectList("allSelected")[0]
	directSelected = getObjectList("directSelected")[0]
	
	combinedList = op.sceneOutliner.mod.tdUtils.outlinerSort(combinedList)
	
	# if we have anything selected at all.
	if(len(combinedList) > 0):
		
		# create an empty tree dictionary object and some other things
		# t = tree()
		parentTargets = {}
		TranslationTargets = {}
		
		# recursively build the hierarchy of our selected items.
		for item in combinedList:
			fullTreePath = fetchParentRecursively([ str(item.name) ])
			
			# get parent and add pair to parent targets dict.
			itemParent = getObjectsParent(item.path)
			
			# there's the possibility an OP is in the root of the scene.
			# if that's true , we set parent to NONE.
			try:
				parentTargets[item.name] = itemParent.name
			except:
				parentTargets[item.name] = None
		
		newlyCreatedItems = []
		
		# now we can do our duplications and build the translation dict.
		for item in combinedList:
			
			# first make an actual TD copy of the node.
			newItem = geoHolder.copy(item)
			
			# make the new items custom parm name unique.
			mod.strUtils.makeNameUnique(newItem)
			
			# add our new item to the translation dict after it's been renamed.
			TranslationTargets[item.name] = newItem.name
			newlyCreatedItems += [ newItem ]
		
		# now we can repair our parenting of our new objects by
		# referencing our parenting dict and translation dict together.
		for newItem in newlyCreatedItems:
			
			# get the ORIGINAL name of the op that was duplicated..
			oldOp = [k for k,v in TranslationTargets.items() if v == newItem.name]
			
			# now find the ORIGINAL parent of that op, from above.
			oldParent = parentTargets[oldOp[0]]
			
			try:
				# now we get our NEW objects parent, via the translation dict again.
				newParent = TranslationTargets[oldParent]
			except:
				# if that fails, it likely means that the parent was outside of the initial selection.
				newParent = oldParent
			
			
			# if newParent is nont None...
			if newParent:
				# parent new item to new parent.
				parentObjectFlat_BLIND( [newItem] , op(geoHolder.path + "/" + newParent) )
	
		# deselect the old, and select the new.
		deselectAllItems()
		
		# we duplicated based on prim/secondary selection, but we want to select
		# only the items the user had selected so as to remain constant.
		newItemsToSelect  = []
		for item in directSelected:
			newItemsToSelect += [ op(geoHolder.path + "/" + TranslationTargets[ item.name]) ]
		
		
		# select the new items.
		selectItems(newItemsToSelect)
		deviceIDs = list(set([  int(getattr( x.par , 'Fdeviceid' , -1 ))   for x in newlyCreatedItems]))
		# handle the address offsetting, if we have any fixtures here.

		maxOffsetsDict = getFixturesHighestOffset(deviceIDs, newItemsToSelect)
		if maxOffsetsDict != None:
		
			# let's offset our address offsets to avoid overlap, if our devices are fixtures.
			reverseTranslationTargets = {v: k for k, v in TranslationTargets.items()}
			# print(reverseTranslationTargets)
			
			# build dict of items to offset. use the OFFSET for the key so we can sort it by ascending address offset properly
			offsetOrdered = {}
			for k,v in reverseTranslationTargets.items():
				newOp = op.geoHolder.op(k)
				if newOp.par.Objtype.eval() in [2,6]: # fixtures or custom fixtures
					Channel = newOp.par.Channel.eval() - 1 # make 0 based
					Universe = newOp.par.Universe.eval() - 1 # make 0 based
					OFFSET = StackOffsets(Channel,Universe)
					offsetOrdered[OFFSET] = k
			
			# iterate through a sorted instance of the offset order dict. 
			for OFST in sorted(offsetOrdered):
				newOp = op.geoHolder.op( offsetOrdered[OFST] )
				if newOp.par.Objtype.eval() in [2,6]:
					
					totalNumOfPix = 0
					if newOp.par.Objtype.eval() == 2: # regular fixtures
						totalNumOfPix = newOp.op('pix').GetTotalNumberOfPix()

					if newOp.par.Objtype.eval() == 6: # custom fixtures
						totalNumOfPix = 1 # custom fixture has no concept of Pix, just channels. thus, we always treat them as fixture of 1 pix.

					if totalNumOfPix > 0:
					
						newAddresOffsets = calculateAddressOffsetFromCurrent( newOp, maxOffsetsDict )
						# debug('maxOffsetsDict', maxOffsetsDict)
						newOp.par.Channel = newAddresOffsets['Channel'] # no need to +1 to 1 based, the function above does this for us.
						newOp.par.Universe = newAddresOffsets['Universe'] # no need to +1 to 1 based, the function above does this for us.
					
						maxOffsetsDict['Channel'] = newAddresOffsets['Channel']
						maxOffsetsDict['Universe'] = newAddresOffsets['Universe']
					
					else:
						maxOffsetsDict['Channel'] = newOp.par.Channel.eval() - 1 # make 0 based
						maxOffsetsDict['Universe'] = newOp.par.Universe.eval() - 1 # make 0 based
		
		# house cleaning for node readability!
		geoHolder.op("layout").run()
		
		if len(newlyCreatedItems):
			op.treeInfo_V2.par.Lastselected = newlyCreatedItems[0]
			
		for each in newlyCreatedItems:
			duplicationRunner = each.op('DUP/Run')
			assert duplicationRunner!=None,'Duplicate runner doesnt exist for %s'%(each.path)
			duplicationRunner.run()
		
		op.treeInfo_V2.par.Forcerefresh.pulse()
		
		return newItemsToSelect
	else:
		op.treeInfo_V2.par.Lastselected = ''
		return []
	



def getObjectByNames(Names=[]):
	# given a list of user specified Names (.Name param) this function returns a list of TD objects that have those names.
	# order is not retained.
	selection = geoHolder.findChildren(type=geometryCOMP, tags=['ObjectType'], maxDepth=1)
	selection = [x for x in selection if x.par.Name in Names]

	return selection


def getLayerSortedProjectorsByNames( Names=[] ):
	projectorsDat = op.sceneOutliner.op('null_sceneProjectors_V2')
	allProjectorOps = list(map(op,projectorsDat.col('ProjectorPath')[1::]))
	namedProjectorOps = [ each for each in allProjectorOps if each.par.Name.eval() in Names ]

	return namedProjectorOps

def getLayerSortedProjectorsByIndex( indexVal ):
	'''
	Given an assumed valid outliner sorted index, and an object type int, this function wiill
	return a reference to the OP that matches that index.
	'''
	projectorsDat = op.sceneOutliner.op('null_sceneProjectors_V2')
	allProjectorOps = list(map(op,projectorsDat.col('ProjectorPath')[1::]))

	assert indexVal < len(allProjectorOps), "index provided cannot be higher than the list length."

	return allProjectorOps[indexVal]


def getObjectList(criteria, myType=None):

	op.sceneOutliner.LogMessage( message="getObjectList" , severity=1 )
	if(criteria == "all"):
		
		selection = geoHolder.findChildren(type=geometryCOMP, tags=['ObjectType'], maxDepth=1)
		
		if myType == None:
			finalSelection = selection
		else:
			ofType = geoHolder.findChildren(type=geometryCOMP, tags=['ObjectType'], key = lambda x: x.par.Objtype == myType, maxDepth=1)
			finalSelection = list(set(selection).intersection(set(ofType)))
	
	elif(criteria == "directSelected"):
		
		selection = geoHolder.findChildren(type=geometryCOMP, tags=['ObjectType'], key = lambda x: x.par.Selected == 1, maxDepth=1)
		
		if myType == None:
			finalSelection = selection
		else:
			ofType = geoHolder.findChildren(type=geometryCOMP, tags=['ObjectType'], key = lambda x: x.par.Objtype == myType, maxDepth=1)
			finalSelection = list(set(selection).intersection(set(ofType)))
		
	elif(criteria == "secondarySelected"):
	
		selection = geoHolder.findChildren(type=geometryCOMP, tags=['ObjectType'], key = lambda x: x.par.Highlighted == 1, maxDepth=1)
		
		if myType == None:
			finalSelection = selection
		else:
			ofType = geoHolder.findChildren(type=geometryCOMP, tags=['ObjectType'], key = lambda x: x.par.Objtype == myType, maxDepth=1)
			finalSelection = list(set(selection).intersection(set(ofType)))
		
	elif(criteria == "allSelected"):
		# get both direct and indirect selected items.
		directlySelected = geoHolder.findChildren(type=geometryCOMP, tags=['ObjectType'], key = lambda x: x.par.Selected == 1, maxDepth=1)
		indirectSelected = geoHolder.findChildren(type=geometryCOMP, tags=['ObjectType'], key = lambda x: x.par.Highlighted == 1, maxDepth=1)
		
		# combine list and make unique.
		combinedList = directlySelected + indirectSelected
		finalSelection = list(set(combinedList))
		
		if myType == None:
			finalSelection = finalSelection
		else:
			ofType = geoHolder.findChildren(type=geometryCOMP, tags=['ObjectType'], key = lambda x: x.par.Objtype == myType, maxDepth=1)
			finalSelection = list(set(finalSelection).intersection(set(ofType)))
	
	
	# make array of pretty names so we can check this instead of UUIDs for human readability.
	nameList = []
	for x in finalSelection:
		nameList += [ x.par.Name.eval() ]

	
	return [ finalSelection , nameList ]
	

def getObjectsParent(opInQuestion):
	
	s = op(opInQuestion)
	parentOp = None
	
	if s:
		if len(s.inputCOMPConnectors) > 0:
			connections = s.inputCOMPConnectors[0].connections
			if len(connections) > 0:
				parentOp = connections[0].owner
				
	return parentOp
	
	
def getObjectsChildren(opInQuestion):
	
	s = op(opInQuestion)
	childrenOps = []
	
	if s:
		if len(s.outputCOMPConnectors) > 0:
			connections = s.outputCOMPConnectors[0].connections
			if len(connections) > 0:
				childrenOps += [x.owner for x in connections]
				
	return childrenOps


def doesObjectHaveChildren(opInQuestion):
	
	s = op(opInQuestion)
	return 1 if len(s.outputCOMPs) > 0 else 0



def saveScene(rootPath = geoHolder.path , selectionOnly = False , byType = None):
	
	
	# get the root path, from the argument. by default it is geoholder.
	TD_Path = op(rootPath)
	
	if selectionOnly:
		foundObjects = getObjectList("allSelected", myType=byType)[0]
	else:
		foundObjects = getObjectList("all", myType=byType)[0]
	
	# define some empty stuff.
	masterText = ""
	parentTargets = {}
	
	for s in foundObjects:
	
		##### First, we generate our header info for THIS object. 
		headerDict = {}
		
		# Get the typeID
		tagList = list(s.tags)
		pattern = 'typeID:*'
		matching = fnmatch.filter(tagList, pattern)
		headerDict["typeID"] = matching[0]
		
		# get the object name.
		headerDict["myName"] = s.name
		
		# get the objects parent, if it has one.
		# NOTE, need to add check to only add parent IF the parent is in the pool of objects being saved.
		parentObj = getObjectsParent(s)
		if parentObj:
			parentTargets[s.name] = parentObj.name
		else:
			parentTargets[s.name] = None
		
		# convert the json dict to text for saving.
		headerAttrs = TDJ.jsonToText(headerDict)
		
		masterText += headerAttrs # append the header attrs JSON text.
		masterText += '\n~\n' # append the header / body split delimiter.
	
		##### Second, we generate all the custom param attributes, and convert it to JSON text.
		# let's get all custom pages, then sort through them and keep just the ones we want params from.
		allCustomPages = s.customPages
		saveableCustomPages = []
		for page in allCustomPages:
			if page.name.isupper() or page.name == "Special":
				saveableCustomPages += [page]
		
		
		# go through all custom pages we kept, and add each custom par to a dict with it's val.
		allParamsToSave = collections.OrderedDict()
		newDict = {}
		for page in saveableCustomPages:
			for custPar in page.pars:
				
				dictRow = { "val":custPar.val }
				newDict[custPar.name] = dictRow
		

		# convert the json dict to text for saving and append to master text.
		masterText += TDJ.jsonToText(newDict)
		masterText += '\n~~~\n' # append object split delimiter
	
	#### append another object splitter delimiter. this marks the end of objects.
	masterText += '~~~\n'
	
	### add the parent targets next.
	# add the parent targets dict to the masterText, last...
	masterText += TDJ.jsonToText(parentTargets)
	
	
	### add the IO scene objects next.
	
	

	return masterText
	
	
	
	
	
	
def loadScene(rootPath = geoHolder.path, masterText = "", templatePath = op.objectTypes.path):
	
	MEEEEE = ''
	
	# get the root path, from the argument. by default it is geoholder.
	TD_Path = op(rootPath)
	templatePath = op(templatePath)

	# split based on the split by master delimiter
	jsonSplit = masterText.split("\n~~~\n~~~\n")
	
	# assign both header and attribute section to vars for easy reading.
	p1_str = jsonSplit[0]
	p2_str = jsonSplit[-1]
	
	# get our parenting json structure.
	json_parenting = TDJ.textToJSON(p2_str, showErrors=True)
	
	LoadedObjects = []
	objTranslation = {}
	
	perObjectSplit = p1_str.split("\n~~~\n")
	for objectStr in perObjectSplit:
		
		# split by object header[0], and object attrs (body)[1]
		objectList = objectStr.split('\n~\n')
		
		json_header = TDJ.textToJSON(objectList[0], showErrors=True)
		json_body = TDJ.textToJSON(objectList[1], showErrors=True)
		
		#############################################
		### get and set a couple object level params.
		typeID = json_header["typeID"] # this tells us what template we copy for this object.
		myName = json_header["myName"] # this is the literal name of the touch designer OP.
		
		# scan our scene for object template types. we should only find 1.
		foundTemplateObjs = templatePath.findChildren(tags=[typeID], maxDepth=1)
		if len(foundTemplateObjs) != 1:
			debug("found more than 1 template object with the same typeID, maybe a problem.")
		template = foundTemplateObjs[0]
		
		# copy our template into our scene.
		copiedObj = TD_Path.copy(template, name=template.name.split('_')[0] + '1')
		# print(copiedObj, copiedObj.name)
		#############################################
		### Now let's get our custom params sorted out.
		parsList = []
		for k, v in json_body.items():
			parsList += [ k ]
		
		# now let's use that list of names to get a list of actual PARAM objects.
		# uses the splat operator to expand a list of strings into separate arguments.
		paramObjList = copiedObj.pars( *parsList )
		
		# now we can safely iterate through the returned param objects and apply values from our save data.
		for paramObj in paramObjList:
			paramItems = json_body[paramObj.name]
			
			# lets assign some vars to easy readable vars.
			val = paramItems["val"]

			# set the var and the expression.. we don't know which we're using yet.
			paramObj.val = val
			
			# if we have a python param, we need to set the expression.
			if paramObj.isPython:
				paramObj.expr = val
		
		#### Now lets find out if we already have an object, by the same name and UUID.
		foundSimilarChildren = TD_Path.findChildren(name=myName)
		
		
		
		# if we do have an op with that name already, run the UUID script, to rename uuid par and name.
		myName2 = myName
		if len( foundSimilarChildren ) > 0:
			myName2 = copiedObj.name
			
		# add the original, and the new name, to the translation table. the new name does not necessarily
		# have to be different from the original.
		objTranslation[myName] = myName2
		
		#### Now let's do some initialization stuff to our objects.
		copiedObj.render = 1
		copiedObj.display = 1
		copiedObj.pickable = 1
		copiedObj.name = myName2
		
		copiedObj.par.Selected = 0
		# put our newly copied object reference into our loadedObjects list.
		LoadedObjects += [ copiedObj ]
		

	#### Handle parenting of objects if they should be parented.
	for k, v in json_parenting.items():
		
		# if the keys exist in the translation dict, update them, otherwise keep the same..
		# this is used to resolve different name issues.
		if k in objTranslation:
			k = objTranslation[k]
		if v in objTranslation:
			v = objTranslation[v]
		
		target = TD_Path.op( k )
		parent = TD_Path.op( v )
		
		# make sure that the target and parent target both exist ,
		# and that the parent target is one of the newly loaded objects.
		if target and parent and (parent in LoadedObjects):
			parentObjectFlat_BLIND( [target] , parent )
	
	#### build our initialization script as a text, and add it to the delayed init text DAT
	postLoadScript.text = ""
	for item in LoadedObjects:
		# print('loadObjects', item)
		InitRun = item.op("INIT/Run")
		ProtocolInit = item.op("PROTOCOL/EnableDisablePars")
		
		# as long as we're not dealing with import  geo type..
		if 'typeID:21' not in item.tags:
			postLoadScript.text += 'op("' + InitRun.path + '").run() \n'
			
		# if we ARE dealing with a device TYPE:
		# this will update the parameter's enable/disable flags so that we see only the active protocol type's parms.
		if 'typeID:60' in item.tags:
			postLoadScript.text += 'op("' + ProtocolInit.path + '").run() \n'
		
		postLoadScript.text += 'op("' + item.path + '").cook(force=1, recurse=1) \n'
	
	
	# postLoadScript.text += '\n' # we could add some post load editor function here.
	
	
	# now run the damned post load script.
	postLoadScript.run(delayFrames = 10)
	
	# relayout geoholder, for readability!
	geoHolder.op("layout").run(delayFrames = 20)
	
	# print('Mee', MEEEEE.val)
	
	return LoadedObjects
	
	
	
def extract_scheme_from_scene():
	'''
	returns an ordered dictionary representing the current scheme
	'''
	
	# allTags = self.GetAllObjectTags()
	masterDict = {}
	
	projectorTable = op.sceneOutliner.op('null_sceneProjectors')
	
	if projectorTable.numRows > 0:
		firstRow = list(map(str,projectorTable.row(0)))
		ActiveCol = firstRow.index('Active')
		
		for i,x in enumerate(projectorTable.rows()[1::]):
			
			if x[ActiveCol] == 1:
				
				masterDict[i] = {}
				for j,item in enumerate(firstRow):
					masterDict[i][item] = str(x[j])
			
	
	return masterDict




def jsonStr_to_Scheme(jsonStr = None):
	'''
	This function takes a file save string, formatted like how the 
	save/export features of geopix exports... with custom delimiters.
	then it takes out the info it needs, and converts the data to
	a list of lists, suitable for easily adding to a tableDAT later.
	
	NOTE> this function expects the save file to have been of ONLY projectors
	this might change in the future, but a scheme is a nickname for a collections
	of projector parameters.
	'''
	# ProjectorParamsToGet
	
	# this is a table that converts style name to int.
	uvStyle = op.sceneOutliner.op('base_collectProjectors/uvStyle')
	
	# this is a table that converts style name to int.
	camStyle = op.sceneOutliner.op('base_collectProjectors/camStyle')
	
	if jsonStr != None:
		
		# make an empty dict to hold our info.
		schemeDict = collections.OrderedDict()
		
		schemeList = []
		schemeList += [ [x[1] for x in ProjectorParamsToGet] ]
		
		# split the load file by the attr/parenting delimiter.
		jsonStr = jsonStr.split("\n~~~\n~~~\n")[0]
		
		# split the remaining string into object chunks
		perObjectSplit = jsonStr.split("\n~~~\n")
		for objectStr in perObjectSplit:
		
			# split by object header[0], and object attrs (body)[1]
			objectList = objectStr.split('\n~\n')
			
			# get dicts of header and body. we only need name from header.
			json_header = TDJ.textToJSON(objectList[0], showErrors=True)
			json_body = TDJ.textToJSON(objectList[1], showErrors=True)
			
			# get the name of the OP.
			schemeDict[ProjectorParamsToGet[0][1]] = json_header[ProjectorParamsToGet[0][0]]
			
			schemeSubList = []
			# add the name first, since it's in a different dict.
			schemeSubList += [ json_header[ProjectorParamsToGet[0][0]] ]
			
			for paramPair in ProjectorParamsToGet[1::]:
				rawVal = json_body[paramPair[0]]['val'] 
				finalVal = rawVal
				
				# convert cam style
				if paramPair[0] == 'Pstyle':
					finalVal = camStyle[rawVal,1]
				
				# convert uv style.
				if paramPair[0] == 'Pextend':
					finalVal = uvStyle[rawVal,1]
				
				if finalVal == "":
					finalVal = None
				# add the val to the scheme sublist, aka row of table.
				schemeSubList += [ finalVal ]
				# pass
			
			# add that whole row to the table list.
			schemeList += [ schemeSubList ]
			
	return schemeList
	
	
	
def PerformDict_to_DelimStr(performDict = None):
	'''
	This function takes a Perform Dict, and converts it into a string
	with two dif delimiters for rows and cols. easy to parse into a table
	later with nodes.
	'''
	returnList = []
	for k,v in performDict.items():
		
		returnList += [ list(map(str,[k,v])) ]
	
	returnList = '|'.join( [ ':'.join(x) for x in returnList ] )
		
	return returnList
	
	
def Dict_to_Scheme(schemeDict = None):
	'''
	This function takes a scheme dict, and converts it to a list of lists
	suitable for injecting into a tableDAT
	'''
	
	schemeList = []
	schemeList += [ [x[1] for x in ProjectorParamsToGet] ]
	
	# this is a table that converts style name to int.
	uvStyle = op.sceneOutliner.op('base_collectProjectors/uvStyle')
	
	# this is a table that converts style name to int.
	camStyle = op.sceneOutliner.op('base_collectProjectors/camStyle')
	
	if schemeDict != None:
	
		for k,v in schemeDict.items():
			schemeSubList = []
			
			# schemeSubList += [ v['_name'] ]
			schemeSubList += [ v['name'] ]
		
			for paramPair in ProjectorParamsToGet[1::]:
				# print(v, paramPair)
				rawVal = v[paramPair[1]]
				finalVal = rawVal
				# print(rawVal,finalVal)
				
				# convert cam style
				if paramPair[1] == 'Pstyle':
					finalVal = str(camStyle[rawVal,1])
				
				# convert uv style.
				if paramPair[1] == 'Pextend':
					finalVal = str(uvStyle[rawVal,1])
				
				# convert uv style.
				if paramPair[1] == 'Projectorlayer':
					finalVal = int(rawVal)
				
				if finalVal == "":
					# finalVal = None
					finalVal = ''
					
				# add the val to the scheme sublist, aka row of table.
				schemeSubList += [ finalVal ]
			
			# add that whole row to the table list.
			schemeList += [ schemeSubList ]
	
	tableStr = '|'.join( [':'.join( map(str,row) ) for row in schemeList] )
	
	return tableStr
	
	
	
def StackOffsets(Channel,Universe , uniRound=510 ):
	
	Channel2 = Channel
	Universe2 = Universe * uniRound
	
	OFFSET = Channel2 + Universe2
	
	return OFFSET
	
	
	
def UnStackOffsets( OFFSET , uniRound=510  ):
	
	Universe2 = int(OFFSET / uniRound)
	Channel2 = (int(OFFSET) % uniRound)
	
	return [Channel2, Universe2]
	
	
	
def UnStackAbsUni_To_NetSubnetUni( OFFSET  ):
	
	Universe2 = int(OFFSET) % 16
	Subnet2 = (int(OFFSET/16)) % 16
	Net2 = (int(OFFSET/16/16))
	
	return [Universe2, Subnet2, Net2]
			
	
def getFixturesHighestOffset(targetDeviceIDs = [-1], opsToIgnore=[] ):
	'''
	UPDATE: actually now we just get highest values across fixtures with matching deviceID
	'''
	allFixtures = getObjectList('all', 2)[0]
	allCustomFixtures = getObjectList('all', 6)[0]
	allTypesOfFixtures = list(set(allFixtures+allCustomFixtures).difference(set(opsToIgnore)))
	
	allFixtures = [x for x in allTypesOfFixtures if x.par.Fdeviceid.eval() in targetDeviceIDs]

	if len(allFixtures):
		
		offsetDict = {}
		for x in allFixtures:
			
			Channel = x.par.Channel.eval() - 1 # make 0 based
			Universe = x.par.Universe.eval() - 1 # make 0 based
			
			
			OFFSET = StackOffsets(Channel,Universe)
			
			offsetDict[OFFSET] = {	'Channel':Channel,
									'Universe':Universe,
									'Object':x
									}
		
		highestOffset = sorted(offsetDict)[-1]

		
		returnDict = {}
		returnDict['Channel'] = offsetDict[highestOffset]['Channel'] + 1 # make 1 based again
		returnDict['Universe'] = offsetDict[highestOffset]['Universe'] + 1 # make 1 based again
		returnDict['Object'] = offsetDict[highestOffset]['Object']
		
		return returnDict
		
	else:
		return None

def getFixtureChanWidth(someFixture=None):
	
	if someFixture != None:
		
		Pixsplit = getattr( someFixture.par , "Pixsplit" , False ) 
		
		NumChans = max( someFixture.par.Chansize.eval() , 0 )
		NumPix = max( someFixture.par.Numpix.eval() , 0 )
		Chan_Size = NumPix * NumChans
		
		Chan_Size_With_Splits = Chan_Size
		FixtureUniWidth = 512
		Routetablewidth = 512
		
		uniWidth = Routetablewidth
		
		if Pixsplit == 1:
			FixtureUniWidth = int(uniWidth)
		else:
			if NumChans > 0:
				FixtureUniWidth = int(uniWidth / NumChans) * NumChans
			else:
				FixtureUniWidth = 0
			
		
		if Pixsplit == 1 and NumChans > 0:
			SplitWidth = uniWidth - FixtureUniWidth
			Channel = int(someFixture.par.Channel.eval())-1 # make 0 based
			numberOfSplits = int((Chan_Size+(Channel)) / FixtureUniWidth)
			totalChannelsSplit = SplitWidth * numberOfSplits
			Chan_Size_With_Splits = Chan_Size + totalChannelsSplit
		
		return [ Chan_Size_With_Splits , FixtureUniWidth ]
		
	else:
		
		return [ 0 , 0 ]
	
def calculateAddressOffsetFromCurrent(someOp = None, offsetsDict = None):
	
	
	returnDict = None
	
	if someOp != None:
		if someOp.par.Objtype.eval() in [2,6]:
			
			if someOp.par.Objtype.eval() == 2:
				someOp.op('pix').WriteCoordsToTable()
				someOp.op('hull').WriteCoordsToTable()
			
			prevOp = offsetsDict.get('Object', None)
			
			
			if prevOp == None:
				ChanWidthInfo = getFixtureChanWidth(someOp)
				WIDTH = ChanWidthInfo[0]
				uniRounding = ChanWidthInfo[1]
			else:
				ChanWidthInfo = getFixtureChanWidth(prevOp)
				WIDTH = ChanWidthInfo[0]
				uniRounding = ChanWidthInfo[1]
			
			if offsetsDict == None:
			
				Channel = someOp.par.Channel.eval() - 1 # make 0 based
				Universe = someOp.par.Universe.eval() - 1 # make 0 based
				
			else:
			
				Channel = offsetsDict['Channel'] - 1 # make 0 based
				Universe = offsetsDict['Universe'] - 1 # make 0 based


			
			OFFSET = StackOffsets(Channel,Universe , uniRounding )
			
			OFFSET2 = OFFSET + WIDTH
			
			newOffsets = UnStackOffsets(OFFSET2 , uniRounding )
			
			Channel2 = newOffsets[0] + 1 # make 1 based again
			Universe2 = newOffsets[1] + 1 # make 1 based again
			
			returnDict = {}
			returnDict['Channel'] = Channel2
			returnDict['Universe'] = Universe2
	
	return returnDict
	
	
def calculateAddressOffsetFromLast(someOp = None, offsetsDict = None):
	
	returnVal = None
	if someOp != None:
		if someOp.par.Objtype.eval() == 2:
		
			someOp.op('pix').WriteCoordsToTable()
			someOp.op('hull').WriteCoordsToTable()
			
			ChanWidthInfo = getFixtureChanWidth(someOp)
			WIDTH = ChanWidthInfo[0]
			uniRounding = ChanWidthInfo[1]
			
			
			if offsetsDict == None:
			
				Channel = someOp.par.Channel.eval() - 1 # make 0 based
				Universe = someOp.par.Universe.eval() - 1 # make 0 based
				
			else:
			
				Channel = offsetsDict['Channel'] - 1 # make 0 based
				Universe = offsetsDict['Universe'] - 1 # make 0 based
			
			OFFSET = StackOffsets(Channel,Universe , uniRounding)
			
			OFFSET2 = OFFSET + WIDTH
			
			newOffsets = UnStackOffsets(OFFSET2 , uniRounding)
			
			Channel2 = newOffsets[0] # make 1 based again
			Universe2 = newOffsets[1] # make 1 based again
			
			returnDict = {}
			returnDict['Channel'] = Channel2
			returnDict['Universe'] = Universe2
			
	return returnDict



def hsv_to_rgb(h,s,v):
	rgb = colorsys.hsv_to_rgb(h, s, v)
	return ' '.join(list(map(str,rgb)))
	
def disableActivePik():
	op.activePikTranslate.par.Target = ''
	op.activePikTranslate.par.Enabled = 0
	

def Seconds_2_Frames( seconds , fps , bpm=None ):
	# first argument should be the variable one.
	return int(seconds * fps)
	

def Frames_2_Seconds( frames , fps , bpm=None ):
	# first argument should be the variable one.
	return frames / fps


def Beats_2_Frames( beats , fps , bpm ):
	# first argument should be the variable one.
	secInMin = 60
	return int( ( ( fps * secInMin ) / bpm ) * beats )


def Frames_2_Beats( frames , fps , bpm ):
	# first argument should be the variable one.
	secInMin = 60
	return ( frames * bpm ) / ( fps * secInMin )


def Seconds_2_Beats( seconds , fps , bpm ):
	frames = Seconds_2_Frames( seconds , fps )
	beats = Frames_2_Beats( frames , fps , bpm )
	return beats


def Beats_2_Seconds( beats , fps , bpm ):
	frames = Beats_2_Frames( beats , fps , bpm )
	seconds = Frames_2_Seconds( frames , fps )
	return seconds

	
def Time_Convert(oldUnit, newUnit, timeValue, fps, bpm ):

	if oldUnit != newUnit:
		functionName = oldUnit.title()+"_2_"+newUnit.title()
		functionToCall = getattr(mod.tdUtils, functionName)
		newTime = functionToCall( timeValue , fps , bpm )
		return newTime

	else: # if same unit is provided, do nothing, just return the timeValue.
		return timeValue
		
	