import os

geoHolder 	= op.sceneOutliner.op("geoHolder")


# this calculates depth based on COMP vertical wires.
# it only looks up 1 level at a time until no further parents
# are found and reports back how many hops it took.
# This may not be bullet proof...
def flatDepth(targetOp):
	recursionLimit = 20
	hierarchyList = []
	depthFound = 0
	activeOp = targetOp
	hierarchyList += [ activeOp.par.Name.val ]
	while(recursionLimit > 0):
		if( len(activeOp.inputCOMPs) > 0 ):
			activeOp = activeOp.inputCOMPs[0]
			depthFound += 1
			hierarchyList += [ activeOp.par.Name.val ]
		else:
			recursionLimit = 0
		recursionLimit -= 1
	pathStr = "/".join(reversed(hierarchyList))
	# print(depthFound)
	return [depthFound, pathStr]
	
	
def realDepth(targetOp):
	recursionLimit = 20
	hierarchyList = []
	hierarchyNameList = []
	depthFound = 0
	activeOp = targetOp
	hierarchyList += [ activeOp.name ]
	hierarchyNameList += [ activeOp.par.Name.eval() ]
	while(recursionLimit > 0):
		if( len(activeOp.inputCOMPs) > 0 ):
			activeOp = activeOp.inputCOMPs[0]
			depthFound += 1
			hierarchyList += [ activeOp.name ]
			hierarchyNameList += [ activeOp.par.Name.eval() ]
		else:
			recursionLimit = 0
		recursionLimit -= 1
	pathStr = "/".join(reversed(hierarchyList))
	NamePathStr = "/".join(reversed(hierarchyNameList))
	# print(NamePathStr)
	# print(depthFound)
	return [depthFound, pathStr, NamePathStr]
	
# this calculates depth based on COMP vertical wires.
# it only looks up 1 level at a time until no further parents
# are found and reports back how many hops it took.
# This may not be bullet proof...
def flatDepth_v2(targetOp):
	recursionLimit = 20
	hierarchyList = []
	depthFound = 0
	activeOp = targetOp
	hierarchyList += [ activeOp.name ]
	while(recursionLimit > 0):
		if( len(activeOp.inputCOMPs) > 0 ):
			activeOp = activeOp.inputCOMPs[0]
			depthFound += 1
			hierarchyList += [ activeOp.name ]
		else:
			recursionLimit = 0
		recursionLimit -= 1
	pathStr = "/".join(reversed(hierarchyList))
	return [depthFound, pathStr]



def flatDepth_name_v3(targetOp, pathStr=""):
	'''
	This functions builds a hierarchy path, using the operator names.
	It builds a hierarchy based on the COMP wire parenting, not depth parenting.
	'''
	pathStr = targetOp.name + pathStr
	if len(targetOp.inputCOMPs) > 0:
		nextOp = targetOp.inputCOMPs[0]
		pathStr = '/' + pathStr
		return flatDepth_name_v3(nextOp,pathStr)
	else:
		return pathStr


def GetDataBlockInfo_General(targetOp):
	
	returnDict = {}

	# p.par.Highlighted = 

	try:
		flatDepthResult =  flatDepth_name_v3(targetOp) # returns pathstring with real op names
		flatDepthSplit = flatDepthResult.split('/')
		
		returnDict['Parent'] = ''
		returnDict['Path'] = ''
		returnDict['Namepath'] = ''

		# returnDict['Realpath'] = flatDepthResult # real name path
		returnDict['Parent'] = targetOp.inputCOMPs[0].name if len(targetOp.inputCOMPs) > 0 else ''
		# returnDict['Path'] = '/'.join([ op.geoHolder.op(x).par.Name.eval() for x in flatDepthSplit ]) # label name path
		# returnDict['Namepath'] = returnDict['Path'] # real name path
		returnDict['Depth'] = len(flatDepthSplit)-1
		returnDict['Highlighted'] = 0
	except:
		returnDict['Realpath'] = ''
		returnDict['Parent'] = ''
		returnDict['Path'] = ''
		returnDict['Namepath'] = ''
		returnDict['Depth'] = 0
		returnDict['Highlighted'] = 0

	return returnDict
	

def verifyObjPath(objPathStr):
	
	isPath = os.path.isfile(str(objPathStr))
	
	projDirTest = str(objPathStr).startswith('GP://')
	# print(projDirTest)
	
	if max( isPath , projDirTest):
		return [objPathStr, 1]
	
	else:
		return [app.samplesFolder+'/Geo/defgeo.tog', 0]
		