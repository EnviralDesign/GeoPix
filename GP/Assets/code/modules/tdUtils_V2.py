geoHolder 	= op.sceneOutliner.op("geoHolder")
treeInfoOp 	= op.sceneOutliner.op('treeInfo_Outliner')

treeInfoV2Op = op.treeInfo_V2
treeInfoTable = treeInfoV2Op.op('treeInfoTable')
treeXformTable = treeInfoV2Op.op('treeXformTable')

treeInfo	= op.sceneOutliner.op("null_treeInfo")
multiSel 	= op.sceneOutliner.op("null_multiSelect")

sceneVars = op.sceneOutliner.op("sceneVars")

TDJ = op.TDModules.mod.TDJSON
import json
import yaml
import re
import os

# these are op.attr
opAttrs = []
# hiddenPars = ['Objtype', 'Originsnap', 'Selected']

realTimeAttrs = ['Tx','Ty','Tz','Rx','Ry','Rz','Sx','Sy','Sz']
# BufferPars = ['Hullbuffer', 'Pixbuffer']



def Storage_to_Table_FULL_V2():
	'''
	This function takes a tree dictionary, and writes it to a touch designer DAT table style string.
	'''
	
	# removes orphaned, or deleted items from scene Tree dict.
	Prune_Storage()
	
	# define some things.
	SceneTree = geoHolder.Tree
	headerList = []
	nameList = []
	
	# build header and name row/columns.
	for k,v in SceneTree.items():
		nameList += [k]
		for attr in v.keys():
			# if attr not in headerList and attr not in BufferPars:
			if attr not in headerList:
				headerList += [attr]
				
	# build table rows as lists, ordered by header list.
	tableList = []
	for opName in nameList:
		rowList = [opName]
		for item in headerList:
			try:
				rowList += [ str(SceneTree[opName][item]) ]
			except:
				rowList += [ "" ]
		tableList += [rowList]
		
	# insert name into header and header into master list.
	headerList.insert(0,'name')
	tableList.insert(0,headerList)
	
	# concatenate down the x/y table list, into dat table formatted string.
	tableList2 = ['\t'.join(x) for x in tableList]
	tableList3 = '\r\n'.join(tableList2)
	tableList3 += '\r\n'
	
	# '''
	# if dat table has changed since last update, copy the text over.
	if tableList3 != treeInfoTable.text:
		treeInfoTable.text = tableList3
	
	return
	




def Prune_Storage():
	'''
	This function will look at the objects in the scene and the objects in the tree
	and prune out all the objects in the tree that no longer exist.
	'''
	objectsInTree = list(geoHolder.Tree.keys())
	objectsInScene = [x.name for x in geoHolder.findChildren(tags=['ObjectType'])]
	# print(objectsInScene)
	orphansInTree = [x for x in objectsInTree if x not in objectsInScene]
	
	for orphan in orphansInTree:
		try:
			del geoHolder.Tree[orphan]
		except:
			debug("could not delete -%s- from geoHolder.Tree"%(orphan))
	
	# for sceneObj in objectsInScene:
		# if sceneObj not in objectsInTree:
			# geoHolder.Tree[sceneObj] = {}
	
	# print(geoHolder.Tree)
	return
	

	

	
### unused with direct push to dict, and 2 layer deep dict.
def SceneList_PrettyDump(textOp = None, sceneDict = {"test":123}):
	'''
	This function simply takes a dictionary, and pretty prints it
	using the TDJ module to a target text DAT for easy viewing.
	'''
	
	# if textOp provided is not None..
	if textOp:
		# yamlDump = yaml.dump(sceneDict, allow_unicode=True, default_flow_style=False)
		# op(textOp).text = yamlDump
		
		op(textOp).text = TDJ.jsonToText(sceneDict)
		
		
	return
	
	
	
	

	
	
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
	
	
	
	
### simply returns the parent of the given object, if it has one.
### returns none otherwise.
def getObjectsParent(opInQuestion):
	
	s = op(opInQuestion)
	parentOp = None
	
	if s:
		if len(s.inputCOMPConnectors) > 0:
			connections = s.inputCOMPConnectors[0].connections
			if len(connections) > 0:
				parentOp = connections[0].owner
				
	return parentOp
	
	
def getSmallestUnusedDeviceID():
	# print('aasdsd')
	idParNames = [ 'Fdeviceid', 'Deviceid' ]
	allSceneObjects = mod.tdUtils.getObjectList('all')[0]
	
	# bit of a hack that works because all deviceID params end with the same eviceid string.
	# we can use .pars pattern matching and the if statement checks to see if the returned list has more than 0 items.
	allDeviceIDs = [x.pars('*eviceid')[0].eval() for x in allSceneObjects if x.pars('*eviceid')]
	
	# remove dups
	allDeviceIDs = list(set(allDeviceIDs))
	
	# the weird voodoo, gets the smallest positive int NOT in allDeviceIDs
	smallestUnusedID = next(i for i, e in enumerate(sorted(allDeviceIDs) + [ None ], 1) if i != e)
	
	return smallestUnusedID
	
	
def testChannelOverlap(argDict = {}):
	'''
	this will determine if any fixtures in the scene overlap with any other fixtures in the scene.
	it does so by performing a 1d overlap test, where:
	min=masterOffset
	max=min+(numPix * numChans)
	'''
	
	conflictStrings = ''
	
	results = []
	reusltConflicts = []
	
	for k in argDict.keys():
		argumentList = argDict[k]
	
		# for i in range(len(argumentList) - 1):
		for i in range(len(argumentList)):
			for j in range(len(argumentList)):
			
				subConflictsList = []
				
				min1 = argumentList[i][0]
				max1 = argumentList[i][0]+argumentList[i][1]-1
				
				min2 = argumentList[j][0]
				max2 = argumentList[j][0]+argumentList[j][1]-1
				
				strA = argumentList[i][2]
				strB = argumentList[j][2]
				
				# print(min1, max1,':::',  min2, max2)
				
				if i != j:
				
					overlapResult = overlap(min1, max1, min2, max2)
					# print(strA,strB,overlapResult)
					
					if overlapResult == True:
						if strA != strB:
							results += [ overlapResult ]
							reusltConflicts += [ '^'.join(sorted([strA, strB])) ]

	uniqueConflictsOnly = list(set(reusltConflicts))
	# conflictStrings = '|||'.join( ["Error: %s's Address Offsets overlap with %s - This will produce probably undesired mapping behavior"%(x.split('^')[0],x.split('^')[1]) for x in uniqueConflictsOnly] )
	return ["Error: Fixture Overlap [ %s <-> %s ]"%(x.split('^')[0],x.split('^')[1]) for x in uniqueConflictsOnly]
	
	# else:
		# return ''
		

def testFixtureOverlap(fixtures = [] , devices = []):
	
	presentDeviceIDs = sorted(list(set([ x.par.Deviceid.eval() for x in devices ])))
	if len(presentDeviceIDs) == 0:
		presentDeviceIDs = sorted(list(set([x.par.Fdeviceid.eval() for x in fixtures])))
	
	SORTER_DICT = {}
	for each in presentDeviceIDs:
		SORTER_DICT[each] = []
	
	gatheredOffsets = gatherFixtureOffsets()
	
	for k,fixtureDict in gatheredOffsets.items():
		subList = []
		f = op(fixtureDict['path'])
		Fdeviceid = f.par.Fdeviceid.eval()
		Name = f.par.Name.eval()
		AbsStartUni = fixtureDict['StartUni']
		StartChan = fixtureDict['StartChan']
		ChanWidth = fixtureDict['ChanWidth']
		
		offset = (AbsStartUni*512) + StartChan
		
		if Fdeviceid in presentDeviceIDs:
			subList += [ offset , ChanWidth , Name ]
			SORTER_DICT[Fdeviceid] += [subList]
		
	for k in SORTER_DICT.keys():
		SORTER_DICT[k] = [x for x in SORTER_DICT[k] if len(x) > 0]
	overlapResult = testChannelOverlap(SORTER_DICT)
	
	return overlapResult
	
	
	
def overlap(x1, x2, y1, y2):
	# Assumes x1 <= x2 and y1 <= y2; if this assumption is not safe, the code
	# can be changed to have x1 being min(x1, x2) and x2 being max(x1, x2) and
	# similarly for the ys.
	x1 = min(x1,x2)# - 139777
	x2 = max(x1,x2)# - 139777
	y1 = min(y1,y2)# - 139777
	y2 = max(y1,y2)# - 139777
	
	returnTest = x2 >= y1 and y2 >= x1
	# if returnTest:
		# print(x1,x2,y1,y2 , returnTest)
	return x2 >= y1 and y2 >= x1
	
	
def gatherFixtureOffsets( optionalFixtures = None):
	'''
	This function gets all fixtures, and calculates their abs universe and channel offsets.
	it's meant to be used in the channel monitors edit feature.
	'''
	if optionalFixtures == None:
		allFixtureObjects = mod.tdUtils.getObjectList('all', 2)[0] + mod.tdUtils.getObjectList('all', 6)[0] # fixtures and custom fixtures
	else:
		allFixtureObjects = optionalFixtures

	# filter out 0 chan size fixtures.
	allFixtureObjects = [ x for x in allFixtureObjects if x.par.Chansize.eval() > 0 ]
	
	chanSizes = [x.par.Chansize.eval() for x in allFixtureObjects]
	pixSizes = [x.par.Numpix.eval() for x in allFixtureObjects]
	startingChan = [x.par.Channel.eval()-1 for x in allFixtureObjects]
	startingUni = [x.par.Universe.eval()-1 for x in allFixtureObjects]
	DeviceId = [x.par.Fdeviceid.eval() for x in allFixtureObjects]
	PixSplit = [x.par.Pixsplit.eval()*1 for x in allFixtureObjects]
	opPaths = [x.path for x in allFixtureObjects]

	chanSizes2 = [0 for x in allFixtureObjects]
	pixSizes2 = [0 for x in allFixtureObjects]
	
	offsets = {}
	
	for x in range(len(allFixtureObjects)):
		
		chanWidth , uniRound = mod.tdUtils.getFixtureChanWidth( allFixtureObjects[ x ] )

		offsets[x] = {}
		
		chanSize = max(chanSizes2[x] , chanSizes[x])
		pixSize = max(pixSizes2[x] , pixSizes[x])

		if PixSplit[x] == 1:
			xtraChansFromPixSplit = 0
		else:
			xtraChansFromPixSplit = int(chanWidth / uniRound) * (512-uniRound)

		chanWidth += xtraChansFromPixSplit
		
		
		offsets[x]['path'] = opPaths[x]
		offsets[x]['StartUni'] = startingUni[x]
		offsets[x]['StartChan'] = startingChan[x]
		offsets[x]['ChanWidth'] = chanWidth
		offsets[x]['chanSize'] = chanSize
		offsets[x]['PixSplit'] = PixSplit[x]
		
		# pass
	
	return offsets
	
	
def ArrangeFixtureOffsets( optionalFixtures = None, optionalStartingUni=0):
	'''
	This function gets all fixtures, and calculates their abs universe and channel offsets.
	it's meant to be used in the channel monitors edit feature.
	'''
	if optionalFixtures == None:
		allFixtureObjects = mod.tdUtils.getObjectList('all', 2)[0] + mod.tdUtils.getObjectList('all', 6)[0] # fixtures and custom fixtures
	else:
		allFixtureObjects = optionalFixtures
	
	# do a natSort
	allFixtureObjects = mod.tdUtils.outlinerSort(allFixtureObjects)
	opPaths = [x.path for x in allFixtureObjects]
	
	offsets = {}
	currentOffset = optionalStartingUni*512

	# print( allFixtureObjects )
	chanWidth = 0
	uniRound = 512
	
	for x in range(len(allFixtureObjects)):
		targetOp = op(opPaths[x])
		channel,universe = mod.tdUtils.UnStackOffsets(currentOffset,uniRound)
		targetOp.par.Channel = channel+1
		targetOp.par.Universe = universe+1

		chanWidth , uniRound = mod.tdUtils.getFixtureChanWidth( allFixtureObjects[ x ] )
		
		currentOffset += chanWidth
	
	return
	
	
	
def generateBufferLookupTable():
	'''
	When we add fixtures to our scene, the fixture itself holds it's own Pix and coordinate data. However
	this needs to get consolidated into a single texture. If we pre set the texture to something large.. like 1280x1280
	and just fill in the parts we're using.. @ 32 bit the gpu mem gets out of hand fast. so, the solution is to not have a 
	bunch of empty space in our buffer. to do this, we need a way to track what rows actually go to what device/absolute universe.
	
	the purpose of this function is to generate a lookup table of sorts that provides GP with info to track what rows of
	a the buffer texture are actually going where. we need this info because eventually this needs to be sent back
	out of GP into artnet devices and serial devices etc.
	'''
	# get all fixtures
	
	allFixtureObjects = mod.tdUtils.getObjectList('all', 2)[0] + mod.tdUtils.getObjectList('all', 6)[0]
	
	startingUni = [x.par.Universe.eval()-1 for x in allFixtureObjects]
	DeviceId = [x.par.Fdeviceid.eval() for x in allFixtureObjects]
	startingChan = [x.par.Channel.eval()-1 for x in allFixtureObjects]

	# chanSizes2 = [x.op('INSTANCE').par.Chansize.eval() for x in allFixtureObjects]
	# pixSizes2 = [x.op('INSTANCE').par.Numpix.eval() for x in allFixtureObjects]
	chanSizes2 = [0 for x in allFixtureObjects]
	pixSizes2 = [0 for x in allFixtureObjects]
	
	# print(allFixtureObjects)
	
	# empty list to deposite absolute universes into.
	# ConsumedAbsUnis = []
	ConsumedAbsUnis = {}
	
	
	
	# this for loop iterates through all fixtures.
	for x in range(len(allFixtureObjects)):
		
		
		
		chanWidth,uniRound = mod.tdUtils.getFixtureChanWidth( allFixtureObjects[x] )
		uniRound = max(uniRound,1)
		
		sizeInUnis = math.ceil((startingChan[x] + chanWidth ) / uniRound)
		
		# print(allFixtureObjects[x],sizeInUnis)
		
		# use the universe width as a secondary for loop to interate through.
		for y in range(sizeInUnis):
			
			# this function takes net, subnet, and universe and generates an absolute universe number.
			uni = startingUni[x]+y
			
			# max theoretical limitof artnet port addresses is 32,768.
			# so to encode the absUni along with the deviceID we can put the abs Uni after the decimal
			# and make the deviceID the whole integer.
			deviceID = DeviceId[x]
			stackedDecFlt = deviceID + (uni / 100000)
			stackedDecstr = '%f' % (deviceID + (uni / 100000))
			# print(allFixtureObjects[x], startingUni[x]+y,startingSub[x],startingNet[x])
			
			ConsumedAbsUnis[stackedDecFlt] = stackedDecstr
	
	ROWS = []
	# print(ConsumedAbsUnis)
	
	# next we iterate through the sorted absUnis list.
	for x,addressEncoded in enumerate( sorted(ConsumedAbsUnis.keys()) ):
		
		# get the string representation of the encoded address 
		# we use this vs the float so we don't have to deal with floating point precision issues
		encodedStrAddress = ConsumedAbsUnis[addressEncoded]
		
		# split the string by the decimal.
		splitAddress = encodedStrAddress.split('.')
		
		# the device ID is fine as is, but we need to cut off the last 0 for the absolute universe.
		splitAddress[1] = splitAddress[1][0:-1]
		
		# convert the resulting number from both sides of the decimal to an integer.
		device_uni_pair = list(map(int,splitAddress))
		device = device_uni_pair[0]
		absUni = device_uni_pair[1]
		# print(absUni)
		
		# build the string and add to the final list.
		fullOffsetPath = '%i/%i'%( device,absUni )
		ROWS.append( [ x , fullOffsetPath ] )
	
	# inser the header item to the final list for ease of use adding to table dats.
	ROWS.insert(0, [ 'rowIndex(bufferTextureRow)','offsetPath(device/absUni)' ])
	

	return [ ROWS ]
	
	
	
	
def killAllRuns(ugOnly=True):
	
	# get the list of runs objects.
	currentRuns = runs
	
	# empty list to store the groups of the runs.
	groups = []
	
	flaggedUgPaths = []
	
	# for each run, add it's group name to the list, and kill it.
	for x in currentRuns:
		# print('----RUN:', x.source)
		# check the run group to see if it's a UG layout, add to list if so.
		if str(x.group) not in flaggedUgPaths:
			# debug('=====================', x.group )
			# debug('=====================', parent() )
				
			fallBackObj = op(str(x.group or parent()))
			if fallBackObj != None:
				if '_ug_attr_editor_' in fallBackObj.tags:
					flaggedUgPaths += [str(x.group)]
			else:
				flaggedUgPaths += [str(x.group)]
				
		
		if x.group in flaggedUgPaths:
			groups.append( str(x.group) )
			x.kill()
	
	# remove duplicates from groups list.
	groups = list(set(groups))
	
	# now for each group, cast it (op path) to an op reference.
	# remove from list if the op comes back as None.
	UGsToRefresh = [op(x) for x in groups if op(x) != None]
	
	# for each real op, we can assume it's an UberGui column layout.
	# we no want to refresh it on the next frame.
	for x in UGsToRefresh:
		mod.execUtils.DelayedScript( 'op("%s").par.Reload.pulse()'%(x) , parent() )
		
		
def updateFixtureBuffers():
	
	# print('updating Fixture buffers....')
	debug('updateFixtureBuffers : dont think we need this anymore...')
	
	'''  don't think we need this anymore since we're saving/lading directly to storage dicts.
	for x in op.geoHolder.findChildren(tags=['hull']):
		x.SaveToBuffer()
		
	for x in op.geoHolder.findChildren(tags=['pix']):
		x.SaveToBuffer()
	'''
	return
		
def clearFixtureBuffers():
	
	debug('clearFixtureBuffers : dont think we need this anymore...')

	'''  don't think we need this anymore since we're saving/lading directly to storage dicts.
	# print('clearing Fixture buffers....')
	
	for x in op.geoHolder.findChildren(tags=['hull']):
		x.par.Hullbuffer.expr = {}
		
	for x in op.geoHolder.findChildren(tags=['pix']):
		x.par.Pixbuffer.expr = {}
	'''
	return
		
# mod.tdUtils_V2.clearFixtureBuffers()

def LoadProjectorsFromScheme(scheme=None):
	
	projTab = scheme.op('null_projectors')
	# for x in projTab.rows():
		# print(x)
	assert projTab!=None,'This projector table is not valid... something is wrong'
	debug('p.Object_Tools.par.Toolmode = 0 no longer a valid command... fix!')
	#op.Object_Tools.par.Toolmode = 0
	
	allProjectorObjects = mod.tdUtils.getObjectList('all', 9)[0]
	for x in allProjectorObjects:
		x.destroy()
	
	delayedExecStr = '''
projTab = op('%s')
for i in range(1,projTab.numRows):
	
	obj = mod.create.Object( 'CreateProjector' )
	
	# print(projTab.row(i))
	
	obj.par.Name = projTab[ i , 'Name' ]
	
	obj.par.Tx = projTab[ i , 'tx' ]
	obj.par.Ty = projTab[ i , 'ty' ]
	obj.par.Tz = projTab[ i , 'tz' ]
	obj.par.Rx = projTab[ i , 'rx' ]
	obj.par.Ry = projTab[ i , 'ry' ]
	obj.par.Rz = projTab[ i , 'rz' ]
	obj.par.Sx = projTab[ i , 'sx' ]
	obj.par.Sy = projTab[ i , 'sy' ]
	obj.par.Sz = projTab[ i , 'sz' ]
	
	obj.par.Pscale = projTab[ i , 'Pscale' ]
	obj.par.Visible = projTab[ i , 'Visible' ]
	obj.par.Pstyle = projTab[ i , 'style' ]
	obj.par.Pextend = projTab[ i , 'extend' ]
	
	obj.par.Routingr = projTab[ i , 'RoutingR' ] if projTab[ i , 'RoutingR' ] != 'None' else ''
	obj.par.Routingg = projTab[ i , 'RoutingG' ] if projTab[ i , 'RoutingG' ] != 'None' else ''
	obj.par.Routingb = projTab[ i , 'RoutingB' ] if projTab[ i , 'RoutingB' ] != 'None' else ''
	obj.par.Routinga = projTab[ i , 'RoutingA' ] if projTab[ i , 'RoutingA' ] != 'None' else ''
	obj.par.Inputpreview = projTab[ i , 'Input' ]
	
	obj.par.Masking = projTab[ i , 'Masking' ] if projTab[ i , 'Masking' ] != 'None' else ''
	obj.par.Maskmode = projTab[ i , 'Maskmode' ]
	
	obj.par.Coloroverride = int(projTab[ i , 'Coloroverride' ])
	obj.par.Setcolor1 = projTab[ i , 'Setcolor1' ]
	obj.par.Setcolor2 = projTab[ i , 'Setcolor2' ]
	obj.par.Setcolor3 = projTab[ i , 'Setcolor3' ]
	obj.par.Setcolor4 = projTab[ i , 'Setcolor4' ]
	
	obj.par.Res1 = projTab[ i , 'Res1' ]
	obj.par.Res2 = projTab[ i , 'Res2' ]
	
	obj.par.Projectoractive = projTab[ i , 'Active' ]
	obj.par.Gamma = projTab[ i , 'Gamma' ]
	obj.par.Gain = projTab[ i , 'Gain' ]
	
	obj.par.Uvfxorigin = projTab[ i , 'Uvfxorigin' ]
	obj.par.Uvfxshuffle = projTab[ i , 'Uvfxshuffle' ]
	
	obj.par.Projectorblendmode = projTab[ i , 'Projectorblendmode' ]
	obj.par.Projectorlayer = projTab[ i , 'Projectorlayer' ]
		
		
	'''%(projTab.path)
	
	# print(delayedExecStr)
		
	mod.execUtils.DelayedScript(delayedExecStr , parent(), 1)
	
		
	
	
def LoadIoFromScheme(scheme=None):
	
	Iodict = scheme.par.Iodict.eval()
	assert Iodict!=None,'This Iodict is not valid... something is wrong'
	debug('p.Object_Tools.par.Toolmode = 0 no longer a valid command... fix!')
	# op.Object_Tools.par.Toolmode = 0
	
	
	op.IO_scene.DeleteAllObjects(typeIgnore=['scheme/'])
	iojson = op.IO_scene.Dict_to_JSON( myDict=Iodict )
	op.IO_scene.DICT_to_IO( Iodict )
	
	op.IO_scene.Load_Conns( connsDict=Iodict.get('connections',{}) )
	
	op.IO_scene.Load_PixFrameCaches(  )
	
	
def LaunchFileBrowser( load=True , start=None , fileTypes=None , title='Load...'  ):
	'''
	path = op.sceneOutliner.mod.tdUtils_V2.LaunchFileBrowser(load=True, start='USER\PROJECTS',fileTypes=['txt'],title='Load PROJECT:')
	'''
	
	knownPathSuffixes = [
		'USER/PROJECTS',
		'USER/PREFABS',
		'USER/GRAPHS',
		'ErrorLog.txt',
		'TECH_Map.jpg',
		'EXAMPLES/3d models',
		'UV_Snapshot.png',
	]
	
	dynamicPathSuffixes = [
		'GP_ScreenCapture_',
	]
	
	# if there is a matching project directory in the user's set project folder, we'll use that instead.
	expandedPath = tdu.expandPath(start)
	endsWithTest = [x for x in knownPathSuffixes if expandedPath.endswith(x) == True]
	MatchingProjectPathSuffix = None
	if len(endsWithTest) > 0:
		MatchingProjectPathSuffix = endsWithTest[0]
		
	# if there is a partial matching dynamic name being saved, we'll convert that path.
	endsWithTest = [ x for x in dynamicPathSuffixes if expandedPath.find(x) != -1 ]
	MatchingDynPathSuffix = None
	if len(endsWithTest) > 0:
		MatchingDynPathSuffix = endsWithTest[0]
	path = None
	
	
	GP_Path = project.paths.get('GP', None)
	if GP_Path != None:
		isPathReal = os.path.exists(GP_Path)
	else:
		isPathReal = False
	
	
	if GP_Path == None:
		path = ui.chooseFile(load=load, start=start,fileTypes=fileTypes,title=title)
	else:
		if isPathReal == True:
			
			if MatchingProjectPathSuffix != None:
				GP_Path = GP_Path + '/' + MatchingProjectPathSuffix
			
			if MatchingDynPathSuffix != None:
				GP_Path = GP_Path + '/' + start.replace('\\', '/').split('/')[-1]
			
			path = ui.chooseFile(load=load, start=GP_Path,fileTypes=fileTypes,title=title)
			
	return path
	
	
	
def LaunchFolderBrowser( start=None , title='Choose Folder...'  ):
	'''
	path = op.sceneOutliner.mod.tdUtils_V2.LaunchFolderBrowser( start='USER\PROJECTS' , title='Choose Folder:' )
	'''
	
	knownPathSuffixes = [
		'USER/PROJECTS',
		'USER/PREFABS',
		'USER/GRAPHS',
		'EXAMPLES/3d models',
	]
	
	# if there is a matching project directory in the user's set project folder, we'll use that instead.
	expandedPath = tdu.expandPath(start)
	endsWithTest = [x for x in knownPathSuffixes if expandedPath.endswith(x) == True]
	MatchingProjectPathSuffix = None
	if len(endsWithTest) > 0:
		MatchingProjectPathSuffix = endsWithTest[0]
	
	
	GP_Path = project.paths.get('GP', None)
	if GP_Path != None:
		isPathReal = os.path.exists(GP_Path)
	else:
		isPathReal = False
	
	useProjectRoot = False
	if MatchingProjectPathSuffix != None:
		if GP_Path != None:
			useProjectRoot =  True
	
	# print(useProjectRoot)
	# if GP_Path == None or MatchingProjectPathSuffix != None:
	if useProjectRoot == False:
		path = ui.chooseFolder( start=start , title=title)
	else:
		if isPathReal == True:
			
			if MatchingProjectPathSuffix != None:
				GP_Path = GP_Path + '/' + MatchingProjectPathSuffix
			
			path = ui.chooseFolder( start=GP_Path , title=title )
			
	return path
	