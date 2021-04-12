import os
import tdUtils as pof

geoHolder 				= op.sceneOutliner.op("geoHolder")
multiSel 				= op.sceneOutliner.op("null_multiSelect")

geo_template 			= op.sceneOutliner.op("objectTypes/geo_template")
grp_template 			= op.sceneOutliner.op("objectTypes/grp_template")
primitive_template 		= op.sceneOutliner.op("objectTypes/primitive_template")
fixture_template 		= op.sceneOutliner.op("objectTypes/fixture_template")
device_template 		= op.sceneOutliner.op("objectTypes/device_template")
light_template 			= op.sceneOutliner.op("objectTypes/light_template")
signalChain_template	= op.sceneOutliner.op("objectTypes/signalChain_template")
postLoadScript		 	= op.sceneOutliner.op("geoHolder").op("postLoadScript")


def Object(varName = "Item", doInit=True, argStr='CREATE'):
	
	newObject = None
	
	selectedItems = []
	for item in multiSel.rows():
		selectedItems += [ op(item[0]) ]
	
	ObjNamePrefix = varName.replace("Create", "") + "_template"
	ObjNameLabel = varName.replace("Create", "") + "1"
	# print(ObjNamePrefix)
	objTemplate = op.sceneOutliner.op("objectTypes/%s"%(ObjNamePrefix))
	# '''
	newObject = geoHolder.copy(objTemplate, name=ObjNameLabel)
	
	init_uniqueName(newObject, ObjNameLabel)
	init_select(newObject)
	
	init_cleanup(newObject)
	
	InitRun = newObject.op("INIT/Run")
	
	# check to make sure the object still exists. some items can self delete if criteria are not met, such as the import geo option.
	if newObject and InitRun and doInit:
		# print('op("CREATE", "' + InitRun.path + '").run(%s) \n'%( str( [x.path for x in selectedItems] ) ))
		postLoadScript.text = ""
		# postLoadScript.text += 'op("' + InitRun.path + '").run("CREATE", %s) \n'%( str( [x.path for x in selectedItems] ) )
		
		postLoadScript.text += 'if op("%s") != None: \n'%( InitRun.path )
		addLine = '	op("%s").run("%s", %s) \n'%( InitRun.path , argStr , str([x.path for x in selectedItems]) )
		postLoadScript.text += addLine
		postLoadScript.text += 'op.geoHolder.UPDATE_ALL_DATABLOCKS() \n'
		
		postLoadScript.run(delayFrames = 0)
	else:
		# newObject = None
		pass
		
	op.treeInfo_V2.par.Forcerefresh.pulse()
	return newObject
	
	# return

	
	
	######## helper functions  ########
	
def init_uniqueName(someOp, typeName = "Item1"):

	uniqueTypeName = mod.strUtils.makeNameUnique(typeName)
	someOp.par.Name = uniqueTypeName # set the custom par name
	
	return
	
def init_select(someOp):
	mod.tdUtils.deselectAllItems()
	mod.tdUtils.selectItems([someOp])
	# someOp.par.Selected = 1
	return
	
def init_uuid(someOp):
	# generate unique UUID
	op(someOp.path + "/UUID/genUUID").run()
	# set the actual node name to the UUID string prepended with underscore.
	op(someOp.path).name = "_" + op(someOp.path).par.Uuid
	return
	
def init_epoch(someOp):
	op(someOp.path + "/EPOCH/genEPOCH").run()
	return
	
def init_cleanup(someOp):

	# set some flags.
	someOp.render = 1
	someOp.display = 1
	someOp.pickable = 1
	someOp.par.Visible = 1
	
	# do some initialization stuff.
	geoHolder.op("layout").run()
	
	return
	
	
def DragObjToEditor(ClipPath=None, baseName=None, extension=None):
		'''
		this function facilitates importing of 3d files by dragging them from
		windows explorer to the Editor Viewport
		'''
		if ClipPath != None:
			
			op.ViewPortUI.ClickButton( "ObjectMode" )

			# print(ClipPath, baseName)
			# ClipPath.split()
			nameStr = tdu.legalName(baseName)
			
			newObj = Object(varName='CreateImportGeo', doInit=False)
			InitRun = newObj.op("INIT/Run")
			
			postLoadScript.text = ""
			postLoadScript.text += 'op("' + InitRun.path + '").run("LOAD") \n'
			postLoadScript.text += 'op.geoHolder.UPDATE_ALL_DATABLOCKS() \n'
			postLoadScript.run(delayFrames=1)
			
			# uniqueName = init_uniqueName(newObj, nameStr)
			uniqueTypeName = mod.strUtils.makeNameUnique(nameStr)
			
			# print('Importing GEO...', uniqueTypeName)
			newPath = tdu.collapsePath(ClipPath)
			
			newObj.par.Loadobj = newPath
			newObj.par.Name = uniqueTypeName