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
	objTemplate = op.sceneOutliner.op("objectTypes/%s"%(ObjNamePrefix))
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
	
	
def DragObjToEditor(FilePath=None, baseName=None, extension=None):
		'''
		this function facilitates importing of 3d files by dragging them from
		windows explorer to the Editor Viewport
		'''

		movie_types = tdu.fileTypes['movie']
		image_types = tdu.fileTypes['image']
		audio_types = tdu.fileTypes['audio']
		geometry_types = ['obj']

		all_types = movie_types + image_types + audio_types + geometry_types

		# handle early exits
		if FilePath == None:
			msg = 'FilePath cannot be equal to None... skipping'
			op.NOTIFV2.Notify(msg)
			debug(msg)
			return

		if extension not in all_types:
			msg = '%s type not supported... skipping'%( extension )
			op.NOTIFV2.Notify(msg)
			debug(msg)
			return

		op.ViewPortUI.ClickButton( "ObjectMode" )
		nameStr = tdu.legalName(baseName)

		if extension in geometry_types: # if user drags a geometry object into the viewport.
		
			newObj = Object(varName='CreateImportGeo', doInit=False)
			InitRun = newObj.op("INIT/Run")

			uniqueTypeName = mod.strUtils.makeNameUnique(nameStr)
			newPath = tdu.collapsePath(FilePath)
			
			newObj.par.Loadobj = newPath
			newObj.par.Name = uniqueTypeName
			
			msg = 'obj imported as an import geometry object.'
			op.NOTIFV2.Notify(msg)

		if extension in image_types: # if user drags an image into the viewport
		
			newObj = Object(varName='CreatePrimitive', doInit=False)
			InitRun = newObj.op("INIT/Run")

			uniqueTypeName = mod.strUtils.makeNameUnique(nameStr)
			newPath = tdu.collapsePath(FilePath)

			newObj.par.Name = uniqueTypeName
			newObj.par.Primtype = 'Plane'

			quiet = parent.project.op('QUIET')
			n = quiet.create( moviefileinTOP )
			n.par.file = FilePath
			n.par.reloadpulse.pulse()
			n.cook(force=1)
			w = n.width
			h = n.height
			# minDim = max(w,h)
			# maxDim = min(w,h)
			aspect = w/h
			newObj.par.Sx = aspect
			newObj.par.Rx = 90 # face down positive Z
			newObj.par.Uniformtexturescale = 4 # by default the texture scale is not 0-1, so scale by 4 to make it so.
			newObj.par.Basecolorstrengthr = 0
			newObj.par.Basecolorstrengthg = 0
			newObj.par.Basecolorstrengthb = 0
			newObj.par.Emitcolorstrengthr = 1
			newObj.par.Emitcolorstrengthg = 1
			newObj.par.Emitcolorstrengthb = 1
			newObj.par.Emitcolortexture = FilePath

			op.Viewport.par.Enablebloom = False
			n.destroy() # destroy the quiet reference.

			op.PbrPacker.DelayedRepack()
			
			msg = 'Image imported as a textured plane primitive object. Bloom was disabled as well from the Lighting settings. You can re enable this at any time.'
			op.NOTIFV2.Notify(msg)