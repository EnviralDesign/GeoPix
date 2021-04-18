import os

TDF = op.TDModules.mod.TDFunctions
TDJ = op.TDModules.mod.TDJSON

# define IO globals.
# IO_BACKEND = op.IOV2
# IO_TEMPLATES = op.IO_templates
# IO_SCENE = parent.IO.par.Scenegeocomp.eval()
# IO_TOOLS = op.IO_logic
# IO_VIEWPORT = op.IOV2.op('Graph')
# IO_NOTIFICATIONS = op.IO_notif_center
# IO_RENDERPICK = op.IOV2.op('Graph').par.Graphrenderpick.eval()

# define EDITOR globals.
# EDITOR_BACKEND = op.sceneOutliner

# define IO misc variables.
# Undeletable_Io_Nodes = op.IOV2.par.Undeletablenodes.eval().split(' ')


'''
NEW way to select IO relative global OPs

parent.IO.IO_BACKEND()
parent.IO.IO_TEMPLATES()
parent.IO.IO_SCENE()
parent.IO.IO_TOOLS()
parent.IO.IO_VIEWPORT()
parent.IO.IO_NOTIFICATIONS()
parent.IO.IO_RENDERPICK()

parent.IO.EDITOR_BACKEND()

parent.IO.Undeletable_Io_Nodes()
'''





class IOV2:
	
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		
		self.DraggedItem = None # promoted attribute
		self.SelectedItems = [] # promoted attribute
		TDF.createProperty(self, 'HoveredItem', value=None, dependable=True, readOnly=False)

	def RESET(self):
		op.IO_viewport.Reset()
		nodesToNotDelete = op.IOV2.UNDELETABLE_IO_NODES()
		for each in op.IO_scene.children:
			if each.name not in nodesToNotDelete:
				each.destroy()

		op.IOV2.par.Scenegeocomp = '/software/top/IOV2/IO_ROOT'

		# reset UI
		op.IoGraphUI.RESET()
		return
	
	
	def TriggerActiveMacros(self):
		if parent.IO.IO_VIEWPORT().par.Isgraphroot.eval():
			sel = self.GetSelectedObjects()
			sel = [ each for each in sel if each.par.Objtype == 10 ]

			for each in sel:
				each.Start()
		else:
			parent.IO.IO_SCENE().parent.obj.Start()
	
	
	def StopActiveMacros(self):
		if parent.IO.IO_VIEWPORT().par.Isgraphroot.eval():
			sel = self.GetSelectedObjects()
			sel = [ each for each in sel if each.par.Objtype == 10 ]
			for each in sel:
				each.Stop()
		else:
			parent.IO.IO_SCENE().parent.obj.Stop()
	
	
	def StopAllMacros(self):
		sel = op.IO_scene.findChildren(depth=1)
		sel = [ each for each in sel if each.par.Objtype == 10 ]
		for each in sel:
			each.Stop()


	def GetNamesByType(self,tag=None):
		alreadyExistingName = []
		if tag != None:
			alreadyExisting = parent.IO.IO_BACKEND().GetObjectsByTagPrefix([tag])
			alreadyExistingName = [x.par.Name.eval() for x in alreadyExisting]
		
		return alreadyExistingName
		

	def GetMaxOffsets(self,tag=None):
		alreadyExistingXpos = 0
		if tag != None:
			alreadyExisting = parent.IO.IO_BACKEND().GetObjectsByTagPrefix([tag])
			alreadyExistingName = [x.par.Name.eval() for x in alreadyExisting]
			if len(alreadyExisting):
				alreadyExistingXpos += max([x.par.Tx.val for x in alreadyExisting]) + 100
		
		return alreadyExistingXpos
		
	
	
	def IsFileReal(self, filePath):
		return os.path.isfile(filePath)
	
	
	def GetPathSafely(self, filePath):
		
		filePath = tdu.expandPath(filePath)
		
		if self.IsFileReal(filePath):
			return filePath
		else:
			return ''
	
	
	def GetAllUpstreamNodes_______________________(self, InitialNodeList ):
		##### recursive function! this searches up stream and finds all IO nodes that are eventual inputs
		##### of the given nodes.
		def getUpstreamComps(comp):
			returnList = []
			if len(comp.inputs) > 0:
				for x in comp.inputs:
					returnList += [ x.parent() ]
			return returnList
		
		def recursiveUpstreamSearch(listOfComps = []):
			
			returnlist = []
			if len(listOfComps) > 0:
				for comp in listOfComps:
					returnlist += [ comp ]
					upstreamComps = recursiveUpstreamSearch( getUpstreamComps( comp ) )
					returnlist += upstreamComps 
			return returnlist
		
		allUpstreamNodes = recursiveUpstreamSearch(InitialNodeList)
		allUpstreamNodes = list(set(allUpstreamNodes))
		
		return allUpstreamNodes
		
	
	
	def GetOriginNodesUpstream___________________(self, InitialNodeList ):
		
		allUpstreamNodes = self.GetAllUpstreamNodes(InitialNodeList)
		
		return [ x for x in allUpstreamNodes if len(x.inputs) == 0 ]
	
	
	def CalculateSelectedObjectsBounds(self, optionalOps=[]):
		
		if len(optionalOps) == 0:
			sel = self.GetSelected()
		else:
			sel = optionalOps

		returnDict = {}
		
		returnDict['minx'] = 0
		returnDict['miny'] = 0
		returnDict['maxx'] = 0
		returnDict['maxy'] = 0
		returnDict['maxDim'] = 0
		returnDict['centerx'] = 0
		returnDict['centery'] = 0

		if len(sel) > 0:

			# compute min/max stuff manually using dims of geo comp, and the user TX /TY
			boundsStuff = [ x.op('GEO').computeBounds() for x in sel ]
			wd2 = [ x.size[0]/2 for x in boundsStuff ]
			hd2 = [ x.size[1]/2 for x in boundsStuff ]

			minx = min([ x.par.Tx - wd2[i] for i,x in enumerate(sel) ])
			miny = min([ x.par.Ty - hd2[i] for i,x in enumerate(sel) ])

			maxx = max([ x.par.Tx + wd2[i] for i,x in enumerate(sel) ])
			maxy = max([ x.par.Ty + hd2[i] for i,x in enumerate(sel) ])
			
			maxDim = max( (maxx - minx) , (maxy - miny) )

			# print(maxDim)
			
			centerx = (minx + maxx) / 2
			centery = (miny + maxy) / 2
			
			# returnDict = {}
			
			returnDict['minx'] = minx
			returnDict['miny'] = miny
			returnDict['maxx'] = maxx
			returnDict['maxy'] = maxy
			returnDict['maxDim'] = maxDim
			returnDict['centerx'] = centerx
			returnDict['centery'] = centery

		# print(returnDict)
		
		return returnDict
	
	
	
	def GetAllObjects(self):
		
		f = parent.IO.IO_SCENE().findChildren(type=geometryCOMP, depth=1, maxDepth=1, parName="Objtype")
		
		return f
	
	
	
	def GetSelectedObjects(self):
		
		f = parent.IO.IO_SCENE().findChildren(type=geometryCOMP, depth=1, maxDepth=1, parName="Objtype")
		
		f = [x for x in f if x.par.Selected.eval() == True]
		
		return f
	
	
	
	def GetObjectsByObjtype(self, macroOp=None, typeList=[]):
		macroOp = op(macroOp)
		if macroOp == None:
			f = parent.IO.IO_SCENE().findChildren(type=geometryCOMP, depth=1, maxDepth=1 )
		else:
			f = macroOp.op('GRAPH').findChildren(type=geometryCOMP, depth=1, maxDepth=1 )
		
		f = [x for x in f if x.par.Objtype.eval() in typeList]
		
		return f
	
	def GetObjectsFromIoNames(self, nameList=[]):
		# this gets us objects from a search of the currently active path.
		f = parent.IO.IO_SCENE().findChildren(type=geometryCOMP, maxDepth=1)
		# print(f)
		
		f = [x for x in f if x.par.Name.eval() in nameList]
		
		return f

	
	
	def GetObjectsByBounds(self, min, max):
		
		txMin = min[0]
		tyMin = min[1]
		
		txMax = max[0]
		tyMax = max[1]
		
		f = parent.IO.IO_SCENE().findChildren(type=geometryCOMP, depth=1)
		# f = [ x for x in f if x.par.Objtype not in [5] ] # get rid of macros.
		f = [ x for x in f if x.par.render == True ] # get rid of things that are invisible - not rendering.
		
		filteredItems = []
		
		for item in f:
			mat = item.worldTransform
			s,r,t = mat.decompose()
			tx,ty = t[0],t[1]
			if tx > txMin and tx < txMax and ty > tyMin and ty < tyMax:
				filteredItems += [ item ]
		
		return filteredItems
		
		
		
		
	def Select(self, ops = [None]):
		# gather all objects
		found = parent.IO.IO_SCENE().findChildren(parName="Selected", depth=1)
		
		# deselect all objects.
		for x in found:
			x.par.Selected = 0
			x.selected = 0
		
		# get only real ops
		ops = [ op(x) for x in ops if op(x) ]
		
		for thisOp in ops:
			
			# select the provided object.
			thisOp.par.Selected = 1
			thisOp.selected = 1
		
		
		parent.IO.IO_BACKEND().par.Lastselected = ops[-1] if len(ops) else ''
		
		
		return


		
		
		
		
		
		
	def SelectAdd(self, ops = [None]):
		
		# get only real ops.
		ops = [ op(x) for x in ops if op(x) ]
		
		for thisOp in ops:
				
			# select the provided object.
			thisOp.par.Selected = 1
			thisOp.selected = 1
			parent.IO.IO_BACKEND().par.Lastselected = thisOp
		
			
		return
		
		
		
	def SelectRemove(self, ops = [None]):
		
		# get only real ops.
		ops = [ op(x) for x in ops if op(x) ]
		
		for thisOp in ops:
				
			# select the provided object.
			thisOp.par.Selected = 0
			thisOp.selected = 0
			if parent.IO.IO_BACKEND().par.Lastselected.eval() == thisOp:
				parent.IO.IO_BACKEND().par.Lastselected = ''
		
			
		return

	def DeselectAll(self):
		
		# gather all objects
		found = parent.IO.IO_SCENE().findChildren(parName="Selected", depth=1)
		
		# deselect all objects.
		for x in found:
			x.par.Selected = 0
			x.selected = 0

		parent.IO.IO_BACKEND().par.Lastselected = ''
		
		
		return
		
	
	def Refresh_IO_Connections(self, target=None):
		target = op(target)
		if target == None:
			target = parent.IO.IO_SCENE()
		GatherIOs = target.findChildren(tags=['_GatherIO_'])
		for x in GatherIOs:
			x.run()
			
			
	def Get_Node_Coordinates(self, nodeList = [] , coordinateSpace = "World" ):
		'''
		Given a list of valid TD geomCOMP objects, this function returns a list
		of world x/y coordinates.
		ie. worldCoords = parent.IO.IO_BACKEND().Get_Node_Coordinates([parent.obj] , coordinateSpace="World" )
		'''
		coordList = []
		if coordinateSpace == "World":
			for node in nodeList:
				mat = node.worldTransform
				s,r,t = mat.decompose()
				coordList += [ [t[0],t[1]] ]
			return coordList
		elif coordinateSpace == "Local":
			for node in nodeList:
				mat = node.localTransform
				s,r,t = mat.decompose()
				coordList += [ [t[0],t[1]] ]
			return coordList
		else:
			debug('coordinate space type "%s" not supported'%(coordinateSpace))
			return None
			
		
		
	def Set_Node_Coordinates(self, nodeList = [] , coordList = [] , coordinateSpace = "World" ):
		'''
		Given a list of valid TD geomCOMP objects, this function set's their x/y
		positions in world space.
		ie. worldCoords = parent.IO.IO_BACKEND().Set_Node_Coordinates( nodeList=[parent.obj] , coordList=[] coordinateSpace="World" )
		'''
		if coordinateSpace == "World":
			for i,node in enumerate(nodeList):
				# nodeMat = tdu.Matrix()
				parentMat = node.parent().worldTransform
				parentMat.invert()
				parentMat.translate(coordList[i][0],coordList[i][1],0)
				s,r,t = parentMat.decompose()
				node.par.Tx = t[0]
				# node.par.Ty = t[1]
				# node.nodeCenterX = node.par.Tx * 2
				# node.nodeCenterY = node.par.Ty * 2
				
		elif coordinateSpace == "Local":
			for i,node in enumerate(nodeList):
				node.par.Tx =coordList[i][0]
				node.par.Ty = coordList[i][1]
				# node.nodeCenterX = node.par.Tx * 2
				# node.nodeCenterY = node.par.Ty * 2
				
		else:
			debug('coordinate space type "%s" not supported'%(coordinateSpace))
			return None
		
		
	def DragClipToIO(self, ClipPath=None, baseName=None, extension=None):
		'''
		this function facilitates importing of video clips by dragging them from
		windows explorer to the IO graph
		'''

		if parent.IO.IO_VIEWPORT().par.Isgraphroot:
			op.NOTIFV2.Notify('Content type nodes can only be created from within a Macro. To use these, please create a Macro first, then click -Enter Macro- at the top, and then create your content graph.')

		else:

			if ClipPath != None:

				if extension in tdu.fileTypes['image']+tdu.fileTypes['movie']:
					nameStr = tdu.legalName(baseName)
					
					templateFileInNode = op.IO_TEMPLATES_V3.op("TEX/Load/ExternalFile")

					newlyMadeOp = parent.IO.CreateNode(templateFileInNode.id)
					newlyMadeOp.par.Clip = ClipPath
					newlyMadeOp.par.Clipreload.pulse()

				if extension in tdu.fileTypes['audio']:
					nameStr = tdu.legalName(baseName)
					
					templateFileInNode = op.IO_TEMPLATES_V3.op("AUDIO/Load_/AudioFile")

					newlyMadeOp = parent.IO.CreateNode(templateFileInNode.id)
					newlyMadeOp.par.Clip = ClipPath
					newlyMadeOp.par.Clipreload.pulse()
			
		
		return
		
		
	def UniquifyObjName(self, someOpName):
		uniqueName = None
		if someOpName:
			
			found = parent.IO.IO_SCENE().findChildren(parName="Name", depth=1, maxDepth=1)
			foundNames = [x.par.Name.eval() for x in found]
			# print(someOpName, foundNames)
			# if someOpName in foundNames:
				# if someOpName[-1].isalpha():
					# someOpName[1:-1] + int(float(someOpName[-1]))+1
			uniqueName = mod.globalFuncs.uniquifyString( someOpName, foundNames )
			# someOp.par.Name = uniqueName
		
		return uniqueName
	
	
	def DeleteSelected(self):
		'''
		Delete selected IO objects.
		'''
		
		# gather all objects
		found = parent.IO.IO_SCENE().findChildren(parName="Selected", depth=1, maxDepth=1)
		found = [x for x in found if x.par.Selected.eval() == 1]
		
		
		
		parent.IO.EDITOR_BACKEND().mod.tdUtils_V2.killAllRuns()
		
		GlobalNodeCount = 0
		# '''
		# deselect all objects.
		for x in found:
			if x.name not in parent.IO.UNDELETABLE_IO_NODES():
				if x.parent() == op.IO_scene:
					GlobalNodeCount += 1
				x.destroy()
			else:
				# debug('Not allowed to delete system nodes.')
				op.NOTIFV2.Notify('Not allowed to delete system nodes.')
		
		parent.IO.IO_BACKEND().par.Lastselected = ''

		if GlobalNodeCount > 0:
			# print('Some nodes that were deleted were global nodes, attempting to prune all macro inputs')
			self.MacroInput_PruneInvalidConnections_GLOBAL()
		# '''
		return
		
	
	def StoreSelected(self, usePlaceTarget = False):
		
		if usePlaceTarget == False:
			f = self.GetSelected()
		else:
			f = [ parent.IO.IO_BACKEND().par.Placetarget.eval() ]
		
		f = [ x for x in f if op(x) != None ]
		
		
		self.SelectedItems = f
		
		return
		
		
	def GetSelected(self):
		
		'''
		returns list of selected items.
		'''
		found = parent.IO.IO_SCENE().findChildren(parName="Selected", depth=1)
		found = [x for x in found if x.par.Selected == 1]
		
		# self.SelectedItems = found
		
		return found
		
	
	def TranslateNodes_Init(self):
		self.StoreNodePositions()
		self.StoreSelected()
		
		
		
	def StoreNodePositions(self, usePlaceTarget = False):
		'''
		Stores x/y pos so that we can transform or reset nodes.
		'''


		# macroX = 0
		# macroY = 0
		if usePlaceTarget == False:
			found = self.GetSelected()
		else:
			# graph = parent.IO.IO_VIEWPORT()
			# if graph.par.Isgraphroot.eval() == False:
			# 	macroX = - parent.IO.IO_VIEWPORT().par.Scenegeocomp.eval().parent.obj.par.Tx
			# 	macroY = - parent.IO.IO_VIEWPORT().par.Scenegeocomp.eval().parent.obj.par.Ty
			found = [ parent.IO.IO_BACKEND().par.Placetarget.eval() ]
		
		found = [ x for x in found if op(x) != None ]

		storedItems = {}
		startPos = {"Tx":parent.IO.IO_RENDERPICK()['pik_tx'].eval() , "Ty":parent.IO.IO_RENDERPICK()['pik_ty'].eval() }
		
		for x in found:
			# print(x.par.Tx, x.par.Ty)
			storedItems[x.name] = {'Tx':x.par.Tx.eval(), 'Ty':x.par.Ty.eval()}
		
		# print(startPos)
		# print(storedItems)
		
		parent.IO.IO_VIEWPORT().store('storedItems', storedItems)
		parent.IO.IO_VIEWPORT().store('startPos', startPos)
		
		return
		
		
	def TranslateNodes_Move(self, usePlaceTarget = False):
		'''
		moves selected nodes by the difference the IO_ RENDERPICK coordinates have moved.
		happens based on the stored start positions, so can be called blindly
		until the transform is accepted or cancelled.
		'''

		# macroX = 0
		# macroY = 0
		# if usePlaceTarget == True:
		# 	graph = parent.IO.IO_VIEWPORT()
		# 	if graph.par.Isgraphroot.eval() == False:
		# 		macroX = - parent.IO.IO_VIEWPORT().par.Scenegeocomp.eval().parent.obj.par.Tx
		# 		macroY = - parent.IO.IO_VIEWPORT().par.Scenegeocomp.eval().parent.obj.par.Ty



		currentPikPos = {"Tx":parent.IO.IO_RENDERPICK()['pik_tx'].eval() , "Ty":parent.IO.IO_RENDERPICK()['pik_ty'].eval() }
		
		storedItems = parent.IO.IO_VIEWPORT().fetch('storedItems', {})
		startPos = parent.IO.IO_VIEWPORT().fetch('startPos', currentPikPos)
		
		# found = self.GetSelected()
		found = self.SelectedItems
		for x in found:
			
			if op(x) != None:
				fetchedPos = storedItems[x.name]
				
				x.par.Tx = -(startPos['Tx'] - currentPikPos['Tx']) + fetchedPos['Tx'] 
				x.par.Ty = -(startPos['Ty'] - currentPikPos['Ty']) + fetchedPos['Ty'] 
				
				# x.nodeCenterX = x.par.Tx * 2
				# x.nodeCenterY = x.par.Ty * 2
		
	
	def TranslateNodes_Finish(self):
		'''
		finishes the translate, by doing nothing, just turning off transform mode.
		'''
		
		# found = self.SelectedItems
		# print(found)
		# for x in found:
			# x.nodeX = x.par.Tx
			# x.nodeY = x.par.Ty
		# debug('ending translate...')
		parent.IO.IO_VIEWPORT().par.Translatemode = 0
		parent.IO.IO_TOOLS().par.Mode = 0
		
		
		
	def TranslateNodes_Cancel(self):
		'''
		cancels the translate, by re writing old values saved when the translate initiated.
		'''
		# debug('canceling Translate...')
		# if we're even in translate mode to begin with...
		if parent.IO.IO_VIEWPORT().par.Translatemode:
		
			storedItems = parent.IO.IO_VIEWPORT().fetch('storedItems', {})
			
			# foundw = self.GetSelected()
			found = self.SelectedItems
			for x in found:
				fetchedPos = storedItems[x.name]
				x.par.Tx = fetchedPos['Tx']
				x.par.Ty = fetchedPos['Ty']
				
			parent.IO.IO_VIEWPORT().par.Translatemode = 0
			parent.IO.IO_TOOLS().par.Mode = 0
			
			
			
	def DeleteAllObjects(self, typeIgnore=[]):
		
		# gather all objects
		found = parent.IO.IO_SCENE().findChildren(parName="Selected", depth=1, maxDepth=1)
		parent.IO.EDITOR_BACKEND().mod.tdUtils_V2.killAllRuns()
		
		for x in found:
			if x.name not in parent.IO.UNDELETABLE_IO_NODES():
				x.destroy()
			else:
				# if x.name == "Default_0":
				# 	x.nodeCenterX = -200
				# 	x.nodeCenterY = 0
				# 	x.par.Tx = -100
				# 	x.par.Ty = 0
				# debug('Not allowed to delete system nodes.')
				# op.NOTIFV2.Notify('Not allowed to delete system nodes.')
				pass
		
		parent.IO.IO_BACKEND().par.Lastselected = ''
			
		return
		
		
	def DuplicateSelectedObjects(self):

		sel = self.GetSelected()
		translationDict = {}
		
		if len(sel):
		
			newSel = []
			
			before = set(parent.IO.IO_SCENE().children)
			ui.copyOPs( sel )
			ui.pasteOPs( parent.IO.IO_SCENE() )
			after = set(parent.IO.IO_SCENE().children)
			
			newSel = list(after.difference( before ))
			
			
			for new in newSel:
				new.par.Name = self.UniquifyObjName(new.par.Name.eval())
				
			boundsDict = self.CalculateSelectedObjectsBounds( optionalOps = sel )
			
			xSize = 0 # no value for x size, since we want to offset duplicates DOWN.
			ySize = ((boundsDict['maxy']-boundsDict['miny']) + 10) * -1
			
			# offset duplicated objects to be non overlapping by bounding size.
			for newOp in newSel:
				newOp.par.Tx += xSize
				newOp.par.Ty += ySize
				newOp.nodeX += xSize*2
				newOp.nodeY += ySize*2
			
			for newlyMadeOp in newSel:
				# IoGatherScripts = newlyMadeOp.findChildren(tags=['_GatherIO_'])
				# for x in IoGatherScripts:
					# x.run()
				self.Refresh_IO_Connections(newlyMadeOp)
			
			# update selection.
			parent.IO.IO_BACKEND().par.Lastselected = newSel[-1]
			self.Select(newSel)
			
		return
		
	
	
	def Node_Disconnect(self, connectionsTab, A ):

		A += 1

		a_SOURCE = connectionsTab[A,'Name'].val

		try:
			a_path = op( connectionsTab[A,'path'] ).parent.obj
		except:
			a_path = op( connectionsTab[A,'path'] )

		a_connId = connectionsTab[A,'connectorID']
		a_dir = connectionsTab[A,'direction']
		try:
			if a_dir == "in":
				a_path.inputConnectors[a_connId].disconnect()
			elif a_dir == "out":
				a_path.outputConnectors[a_connId].disconnect()

		except:
			op.NOTIFV2.Notify('Could not disconnect : %s'%(a_path) )


		return


	def Node_Connect(self, connectionsTab, A, B):
		
		A += 1
		B += 1
		
		a_SOURCE = connectionsTab[A,'Name'].val
		
		try:
			a_path = op( connectionsTab[A,'path'] ).parent.obj
		except:
			a_path = op( connectionsTab[A,'path'] )
			
		# print(op( connectionsTab[A,'path'] ))
		
		# inputOpPath = '/'.join(connectionsTab[B,'path'].val.split('/')[0:-1])
		B_DEST = op(connectionsTab[B,'path'].val)
		
		try:
			
			# b_path = op( inputOpPath ).parent.obj
			b_path = op( B_DEST ).parent.obj
		except:
			# b_path = op( inputOpPath )
			b_path = op( B_DEST )
			
		# print(b_path)
			
		a_type = connectionsTab[A,'GP_type']
		b_type = connectionsTab[B,'GP_type']
		
		a_connId = connectionsTab[A,'connectorID']
		b_connId = connectionsTab[B,'connectorID']
		
		a_dir = connectionsTab[A,'direction']
		b_dir = connectionsTab[B,'direction']
		
		canWeConnect = 1
		
		# print(a_path,b_path)
		
		if a_path != None and b_path != None:
			# first check, are we connecting two connectors on the same object?
			# we're not allowed to do this.
			if a_path == b_path:
				canWeConnect = 0
			
			# we also need to make sure we're connecting like operators. chop-chop or top-top
			if a_type != b_type:
				canWeConnect = 0
				op.NOTIFV2.Notify('You can only connect similar inputs and outputs.')

				
			# if user tried to connect output to output or input to input
			if a_dir == b_dir:
				canWeConnect = 0
				op.NOTIFV2.Notify('You can only connect out->in or in<-out')
				
			# connect it!!!
			if canWeConnect == 1:
				if a_dir == "out":
					a_path.outputConnectors[a_connId].connect(b_path.inputConnectors[b_connId])
				elif a_dir == "in":
					b_path.outputConnectors[b_connId].connect(a_path.inputConnectors[a_connId])
				
			# print( ' Connecting! ' if canWeConnect else "can't connect..." )
	
		# disconnect
		elif a_path != None and b_path == None:
			
			if a_dir == "out":
				a_path.outputConnectors[a_connId].disconnect()
			elif a_dir == "in":
				a_path.inputConnectors[a_connId].disconnect()
				
		else:
			pass
		
		return

	#############################################################################################
	########################### begin macro OUTPUT functions ####################################
	#############################################################################################

	def GetParentMacroRefIfExists(self, someOp ):
		return someOp.parent.obj.parent.obj if someOp.parent.obj.parent.obj.name != "IO_ROOT" else None


	def GetOutputsByNameFromMacro(self, macroOp=None, nameList=[] ):
		
		assert macroOp != None, "You must provide a valid macro operator for this function to work."

		# this gets us objects from a search of the currently active path.
		f = parent.IO.IO_SCENE().findChildren(type=geometryCOMP, maxDepth=1, depth=1)
		f = [ x for x in f if x.par.Selected == 1]
		f = [ x for x in f if x.par.Objtype == 10 ] 

		assert len(f) <= 1, "Should not be trying to retrieve output nodes for more than 1 macro at a time... "

		f2 = macroOp.op('GRAPH').findChildren( type=geometryCOMP , depth=1, maxDepth=1, parName="Objtype" )
		f2 = [ x for x in f2 if x.par.Objtype.eval() in [ 14,15,16 ] ]

		f2 = [ x for x in f2 if x.par.Name in nameList ]
		
		return f2



	def GetOutputsIndexDictFromMacro(self, macroOp=None ):
		
		assert macroOp != None, "You must provide a valid macro operator for this function to work."

		f = macroOp.op('GRAPH').findChildren( type=geometryCOMP , depth=1, maxDepth=1, parName="Objtype")
		f = [ x for x in f if x.par.Objtype.eval() in [ 14,15,16 ] ]
		f = reversed(sorted(f, key=lambda node: node.nodeY))

		f2 = { myOp.par.Name.eval():i for i,myOp in enumerate(f)  }
		
		return f2


	def MacroOutput_Connect(self , A , B ):
		'''
		Connects a texture [or audio etc] output of a macro, to an input tile on the right.
		'''

		def getOutputType( index ):
			outputLookupDat = parent.IO.op('sceneData/null_current_macros_Tex_Out_Names')
			lookupDat = op.IO_TEMPLATES_V3.op('null_PIK_LOOKUP')
			Objtype = int(outputLookupDat[index+1,'Objtype'])

			# now find the macro output node type ie.tex,chan,audio
			d = {}
			for i in range(lookupDat.numRows):
				try:
					d[ int(lookupDat[i,'-objtype-']) ] = str(lookupDat[i,'-type-'])
				except:
					pass
			texType = d[Objtype]

			# now find the objtype of the macro output. 60,61,62, etc.
			d = {}
			for i in range(lookupDat.numRows):
				try:
					if int(lookupDat[i,'-objtype-']) >= 60 and int(lookupDat[i,'-objtype-']) < 65:
						d[ lookupDat[i,'-type-'].val ] = str(lookupDat[i,'-objtype-'])
				except:
					pass

			return d[texType]

		def getInputType( index ):
			TileInfo = op.TileManager.GetInfoFromHovered()
			Objtype = TileInfo['Objtype']
			return Objtype

		def getInputInfo( index ):
			TileInfo = op.TileManager.GetInfoFromHovered()
			return TileInfo

		connCompat = op.IO_TEMPLATES_V3.op('null_connectionCompatibility')

		currentRoot = parent.IO.IO_BACKEND().par.Scenegeocomp.eval()
		assert currentRoot != None, 'root object should definitely not be None, check this out..'

		sel = self.GetSelectedObjects()
		assert len(sel) == 1, 'should not even be able to disconnect a macro nodes output when multiple or no nodes are selected, check this out.'

		macroOp = sel[0]
		OutList = macroOp.par.Out.eval()

		assert isinstance( OutList , list ) , 'Outlist is not a list! this should not happen'

		indexLookupDict = self.GetOutputsIndexDictFromMacro( macroOp )
		invertedDict = {v:k for k,v in indexLookupDict.items()}

		OutType = int(getOutputType(A))
		InType = int(getInputType(B))

		allowedTypes = connCompat[ str(InType) ,1].val.split(',')
		allowedTypes = [int(x) for x in allowedTypes if x.isnumeric()]
		# print(OutType, allowedTypes)
		if OutType in allowedTypes:

			# print(OutType,InType, allowedTypes)

			OUT_NAME = invertedDict[A]
			IN_NAME = getInputInfo(B)['Name']

			InOnlyNames = [x['B'] for x in OutList]

			if IN_NAME not in InOnlyNames:
				OutList += [ {"A":OUT_NAME , "B":IN_NAME} ]
				macroOp.par.Out = OutList

			elif IN_NAME in InOnlyNames:
				indexOfInName = InOnlyNames.index(IN_NAME)
				OutList[indexOfInName]["A"] = OUT_NAME
				macroOp.par.Out = OutList

			else:

				debug('wtf? check this out')

		else:
			op.NOTIFV2.Notify('Connection between those types is not compatible.')



	
	def MacroOutput_PruneInvalidConnections( self ):
		'''
		This function will check the currently selected macro, examine it's connections, and determine if any are invalid.
		If any are, they will be removed from the connections list so that it becomes valid again.
		'''

		tilesDat = op.TileManager.op('null_tileNames')


		currentRoot = parent.IO.IO_BACKEND().par.Scenegeocomp.eval()
		assert currentRoot != None, 'root object should definitely not be None, check this out..'

		sel = self.GetSelectedObjects()
		assert len(sel) == 1, 'should not even be able to disconnect a macro nodes output when multiple nodes are selected, check this out.'

		macroOp = sel[0]
		OutList = macroOp.par.Out.eval()
		NewOutList = []
		assert isinstance( OutList , list ), 'variable stored in Out parameter was not a list, this is an error. check this out'

		A_Names = self.GetOutputsByNameFromMacro(macroOp , [x['A'] for x in OutList]  )
		A_Names = [ each.par.Name.eval() for each in A_Names ]
		B_Names = list(map(str,tilesDat.col('Name')[1::]))
		
		for each in OutList:
			if each['A'] in A_Names and each['B'] in B_Names:
				NewOutList += [each]
		
		macroOp.par.Out = NewOutList

		return


	def MacroOutput_UpdateConnectionNames( self , FindName , ReplaceName , ObjNameType , ObjRef ):
		'''
		Given a find and replace string, this function goes through ALL macros, and attempts to find and replace the connection names.
		The is intended to be used when the user changes the name of a projector or a macro out connector, since connections are maintained
		based on user given name, not operator name, this means things can break when the user renames things, common task for cleaning u
		and organizing a file after some work has been done.

		Last argument(ObjNameType) can be the following: [ 'local' , 'global' ,  ]
		'''
		# Isgraphroot = parent.IO.IO_VIEWPORT().par.Isgraphroot.eval()
		# print(op.IO_viewport.par.Isgraphroot.eval())
		# if op.IO_viewport.par.Isgraphroot.eval() == False:
		# import inspect
		# print('asd')
		# print( inspect.stack() )
		
		if FindName not in [None]:

			TileNamesDat = op.TileManager.op('null_tileNames')
			TileNames = list(map(str,TileNamesDat.col('Name')[1::]))

		
			if ObjNameType in ['global']: # if the changed thing is a global thing, like a projector, we need to update all macros.
				allObjects = parent.IO.op('IO_ROOT').findChildren(type=geometryCOMP, maxDepth=1, parName='Objtype')
				allMacros = [ x for x in allObjects if x.par.Objtype.eval() in [10] ] # get all macros

			elif ObjNameType in ['local']: # if the changed thing is a tex out node OF a macro, we only need to update that specific macro.
				allMacros = [ ObjRef.parent.obj ]
			
			for macro in allMacros:
				OutList = macro.par.Out.eval()
				NewOutList = []
				for ConnectionDict in OutList:
					NewOutList += [ 
							{ 
								"A":ConnectionDict['A'].replace(FindName,ReplaceName) if ConnectionDict['A'].endswith(FindName) else ConnectionDict['A'], 
								"B":ConnectionDict['B'].replace(FindName,ReplaceName) if ConnectionDict['B'].endswith(FindName) else ConnectionDict['B']
							} 
						]
				macro.par.Out = NewOutList


		return
	
	def MacroOutput_Disconnect(self, OutputIndex ):
		'''
		Disconnects a macro output from it's target.
		'''
		self.MacroOutput_PruneInvalidConnections()

		currentRoot = parent.IO.IO_BACKEND().par.Scenegeocomp.eval()
		assert currentRoot != None, 'root object should definitely not be None, check this out..'

		sel = self.GetSelectedObjects()
		assert len(sel) == 1, 'should not even be able to disconnect a macro nodes output when multiple nodes are selected, check this out.'
		
		macroOp = sel[0]
		OutList = macroOp.par.Out.eval()
		assert isinstance( OutList , list ), 'variable stored in Out parameter was not a list, this is an error. check this out'

		indexLookupDict = self.GetOutputsIndexDictFromMacro( macroOp )
		invertedDict = {v:k for k,v in indexLookupDict.items()}
		fetchedNameToDelete = invertedDict.get(OutputIndex,':ERR:')

		assert fetchedNameToDelete != ':ERR:', 'Output index did not correspond to any output stored in dict... check this out.'

		NewOutList = [ each for each in OutList if each['A'] != fetchedNameToDelete ]
		macroOp.par.Out = NewOutList
			
		return
	

	def MacroOutput_Reset(self):
		'''
		Connects a texture [or audio etc] output of a macro, to an input tile on the right.
		'''
		currentRoot = parent.IO.IO_BACKEND().par.Scenegeocomp.eval()
		if currentRoot != None:
			sel = self.GetSelectedObjects()
			if len(sel) == 1:
				macroOp = sel[0]
				macroOp.par.Out = []

			else:
				debug('multiple macros selected... this should not happen.')
		else:
			debug('root object should definitely not be None, check this out..')
	
	#############################################################################################
	########################### begin macro INPUT functions #####################################
	#############################################################################################


	def GetInputsByNameFromMacro(self, macroOp=None, nameList=[] ):
		
		assert macroOp != None, "You must provide a valid macro operator for this function to work."

		# this gets us objects from a search of the currently active path.
		f = parent.IO.IO_SCENE().findChildren(type=geometryCOMP, maxDepth=1, depth=1)
		f = [ x for x in f if x.par.Selected == 1] # filter down to selected only
		f = [ x for x in f if x.par.Objtype == 10 ] # filter down to Macros only.

		assert len(f) <= 1, "Should not be trying to retrieve output nodes for more than 1 macro at a time... "

		f2 = macroOp.op('GRAPH').findChildren( type=geometryCOMP , depth=1, maxDepth=1, parName="Objtype" )
		f2 = [ x for x in f2 if x.par.Objtype.eval() in [ 17,18,19 ] ]
		f2 = [ x for x in f2 if x.par.Name in nameList ]
		
		return f2


	def GetInputsIndexDictFromMacro(self, macroOp=None ):
		
		assert macroOp != None, "You must provide a valid macro operator for this function to work."

		f = macroOp.op('GRAPH').findChildren( type=geometryCOMP , depth=1, maxDepth=1, parName="Objtype")
		f = [ x for x in f if x.par.Objtype.eval() in [ 17,18,19 ] ]
		f = reversed(sorted(f, key=lambda node: node.nodeY))
		f2 = { myOp.par.Name.eval():i for i,myOp in enumerate(f)  }
		
		return f2


	def MacroInput_Connect(self , connectionsTab , A , B ):
		'''
		Connects a texture [or audio etc] node to an input of a macro, on it's left.
		'''

		def getInputInfo( index ):
			inputLookupDat = parent.IO.op('sceneData/null_current_macros_Tex_In_Names')
			lookupDat = op.IO_TEMPLATES_V3.op('null_PIK_LOOKUP')
			Objtype = int(inputLookupDat[index+1,'Objtype'])

			# now find the macro output node type ie.tex,chan,audio
			d = {}
			for i in range(lookupDat.numRows):
				try:
					d[ int(lookupDat[i,'-objtype-']) ] = str(lookupDat[i,'-type-'])
				except:
					pass
			texType = d[Objtype]

			# now find the objtype of the macro output. 65,66,67, etc.
			d = {}
			for i in range(lookupDat.numRows):
				try:
					if int(lookupDat[i,'-objtype-']) >= 65 and int(lookupDat[i,'-objtype-']) < 70:
						d[ lookupDat[i,'-type-'].val ] = str(lookupDat[i,'-objtype-'])
				except:
					pass

			returnDict = {}
			returnDict['objtype'] = int(d[texType])
			returnDict['textype'] = texType
			return returnDict

		def getOutputInfo( connectionsTab , index ):

				index += 1
				
				try:
					a_path = op( connectionsTab[index,'path'] ).parent.obj
				except:
					a_path = op( connectionsTab[index,'path'] )

				d = {}
				d['path'] = str(connectionsTab[index,'path'])
				d['source'] = str(connectionsTab[index,'Name'])
				d['type'] = str(connectionsTab[index,'GP_type'])
				d['connId'] = int(connectionsTab[index,'connectorID'])
				d['dir'] = str(connectionsTab[index,'direction'])

				return d


		
		currentRoot = parent.IO.IO_BACKEND().par.Scenegeocomp.eval()
		assert currentRoot != None, 'root object should definitely not be None, check this out..'

		sel = self.GetSelectedObjects()
		assert len(sel) == 1, 'should not even be able to disconnect a macro nodes output when multiple or no nodes are selected, check this out.'

		macroOp = sel[0]
		InList = macroOp.par.In.eval()
		assert isinstance( InList , list ) , 'Outlist is not a list! this should not happen'

		indexLookupDict = self.GetInputsIndexDictFromMacro( macroOp )
		invertedDict = {v:k for k,v in indexLookupDict.items()}
		# print(indexLookupDict)

		OutInfo = getOutputInfo(connectionsTab,A)
		InInfo = getInputInfo(B)

		# print(OutInfo)
		
		out_direction = OutInfo['dir']
		out_textype = OutInfo['type']
		in_textype = InInfo['textype']

		textype_check = out_textype == in_textype
		direction_check = out_direction == "out"

		if textype_check == False:
			op.NOTIFV2.Notify('Connection between those types is not compatible.')

		if direction_check == False:
			op.NOTIFV2.Notify('Can only connect outputs of IO nodes to inputs of Macros.')

		if textype_check and direction_check:

			OUT_NAME = OutInfo["source"] + "/" + str(OutInfo["connId"])
			IN_NAME = invertedDict[B]
			# print(IN_NAME)

			InOnlyNames = [x['B'] for x in InList]

			# print(OUT_NAME)
			# print(IN_NAME)

			if IN_NAME not in InOnlyNames:
				InList += [ {"A":OUT_NAME , "B":IN_NAME} ]
				macroOp.par.In = InList

			elif IN_NAME in InOnlyNames:
				indexOfInName = InOnlyNames.index(IN_NAME)
				InList[indexOfInName]["A"] = OUT_NAME
				macroOp.par.In = InList

			else:
				debug('wtf? check this out')

		else:
			op.NOTIFV2.Notify('Connection between those types is not compatible.')

		
		return


	
	def MacroInput_PruneInvalidConnections( self ):
		'''
		This function will check the currently selected macro, examine it's input connections, and determine if any are invalid.
		If any are, they will be removed from the connections list so that it becomes valid again.
		'''

		rootNodesDat = op.IOV2.op('sceneData/null_IOV2_ROOTNODES')


		currentRoot = parent.IO.IO_BACKEND().par.Scenegeocomp.eval()
		assert currentRoot != None, 'root object should definitely not be None, check this out..'

		sel = self.GetSelectedObjects()
		assert len(sel) == 1, 'should not even be able to disconnect a macro nodes output when multiple nodes are selected, check this out.'

		macroOp = sel[0]
		InList = macroOp.par.In.eval()
		NewInList = []
		assert isinstance( InList , list ), 'variable stored in In parameter was not a list, this is an error. check this out'

		A_Names = list(map(str,rootNodesDat.col('Name')[1::]))

		B_Names = self.GetInputsByNameFromMacro(macroOp , [x['B'] for x in InList]  )
		B_Names = [ each.par.Name.eval() for each in B_Names ]
		
		for each in InList:
			if each['A'].split('/')[0] in A_Names and each['B'] in B_Names:
				NewInList += [each]

		macroOp.par.In = NewInList

		return


	
	def MacroInput_PruneInvalidConnections_GLOBAL( self ):
		'''
		This function will check all macros, examine their input connections, and determine if any are invalid.
		If any are, they will be removed from the connections list so that it becomes valid again.
		'''

		rootNodesDat = op.IOV2.op('sceneData/null_IOV2_ROOTNODES')


		allObjects = parent.IO.op('IO_ROOT').findChildren(type=geometryCOMP, maxDepth=1, parName='Objtype')
		allMacros = [ x for x in allObjects if x.par.Objtype.eval() in [10] ] # get all macros

		for macroOp in allMacros:

			InList = macroOp.par.In.eval()
			NewInList = []
			assert isinstance( InList , list ), 'variable stored in In parameter was not a list, this is an error. check this out'

			A_Names = list(map(str,rootNodesDat.col('Name')[1::]))

			B_Names = self.GetInputsByNameFromMacro(macroOp , [x['B'] for x in InList]  )
			B_Names = [ each.par.Name.eval() for each in B_Names ]
			
			for each in InList:
				if each['A'].split('/')[0] in A_Names and each['B'] in B_Names:
					NewInList += [each]

			macroOp.par.In = NewInList

		return


	def MacroInput_UpdateConnectionNames( self , FindName , ReplaceName , ObjNameType , ObjRef ):
		'''
		Given a find and replace string, this function goes through ALL macros, and attempts to find and replace the connection names.
		The is intended to be used when the user changes the name of a projector or a macro out connector, since connections are maintained
		based on user given name, not operator name, this means things can break when the user renames things, common task for cleaning u
		and organizing a file after some work has been done.

		Last argument(ObjNameType) can be the following: [ 'Projector' , 'TexOut' ,  ]
		'''
		# Isgraphroot = parent.IO.IO_VIEWPORT().par.Isgraphroot.eval()

		# if op.IO_viewport.par.Isgraphroot.eval() == False:
		
		if ObjNameType in ["global"]: # if the changed thing is an ALL, we want to update all macros since outputs can be connected to several macros.
			allObjects = parent.IO.op('IO_ROOT').findChildren(type=geometryCOMP, maxDepth=1, parName='Objtype')
			allMacros = [ x for x in allObjects if x.par.Objtype.eval() in [10] ] # get all macros

		elif ObjNameType in ["local"]: # if the changed thing is a tex out node OF a macro, we only need to update that specific macro.
			allMacros = [ ObjRef.parent.obj ]
		
		# print(FindName,ReplaceName,ObjNameType)

		for macro in allMacros:
			InList = macro.par.In.eval()
			NewInList = []
			for ConnectionDict in InList:
				NewInList += [ 
						{ 
							"A":ConnectionDict['A'].replace(FindName,ReplaceName) , 
							"B":ConnectionDict['B'].replace(FindName,ReplaceName)
						} 
					]
			macro.par.In = NewInList


		return


	def MacroInput_Disconnect(self, OutputIndex ):
		'''
		Disconnects a macro input from it's source.
		'''
		self.MacroInput_PruneInvalidConnections()

		currentRoot = parent.IO.IO_BACKEND().par.Scenegeocomp.eval()
		assert currentRoot != None, 'root object should definitely not be None, check this out..'

		sel = self.GetSelectedObjects()
		assert len(sel) == 1, 'should not even be able to disconnect a macro nodes output when multiple nodes are selected, check this out.'
		
		macroOp = sel[0]
		InList = macroOp.par.In.eval()
		assert isinstance( InList , list ), 'variable stored in In parameter was not a list, this is an error. check this out'

		indexLookupDict = self.GetInputsIndexDictFromMacro( macroOp )
		invertedDict = {v:k for k,v in indexLookupDict.items()}
		fetchedNameToDelete = invertedDict.get(OutputIndex,':ERR:')

		assert fetchedNameToDelete != ':ERR:', 'Input index did not correspond to any output stored in dict... check this out.'
		
		NewInList = [ each for each in InList if each['B'] != fetchedNameToDelete ]
		macroOp.par.In = NewInList
			
		return

	def MacroInput_Reset(self):
		'''
		resets the connection param to default
		'''
		currentRoot = parent.IO.IO_BACKEND().par.Scenegeocomp.eval()
		if currentRoot != None:
			sel = self.GetSelectedObjects()
			if len(sel) == 1:
				macroOp = sel[0]
				macroOp.par.In = []

			else:
				debug('multiple macros selected... this should not happen.')
		else:
			debug('root object should definitely not be None, check this out..')


	
	def UpdateWidgetCaptureNames(self,old,new):

		f = op.IO_scene.findChildren(parName = "clone")
		allWidgetCaptures = [ x for x in f if x.par.clone.eval() == op.IO_TEMPLATES_V3.op('CHAN/Capture_/WidgetCapture') ]

		numChanged = 0

		for widgetCapture in allWidgetCaptures:
			oldString = widgetCapture.par.Widgetselector.eval()
			oldStringSplit = oldString.split('/')
			oldStringSplit[0] = oldStringSplit[0].replace( old , new )
			newString = '/'.join(oldStringSplit)

			print(widgetCapture , old,new)

			widgetCapture.par.Widgetselector = newString

			numChanged += (newString != oldString)*1

		
		if numChanged > 0:
			op.NOTIFV2.Notify('%i Widget Capture node(s) in IO had their Selector names updated.'%(numChanged))

			op.IO_RightBar_V2.par.Regen.pulse()
		return
		
	
	
	def Load_Conns____________________________(self, connsDict=None, translationDict = None, target=None):
		
		assert connsDict != None, 'Please supply a connection DICT.'
		# debug('Loading IO graph Connections from Project Save.')
		
		if op(target) == None:
			t = parent.IO.IO_SCENE()
		else:
			t = op(target)
		
		
		# exectionString = ""
		
		for k,v in connsDict.items():
			
			# try:
				
			if translationDict == None:
				A_name = v['A_name']
				B_name = v['B_name']
			else:
				A_name = translationDict.get( v['A_name'] , v['A_name'] )
				B_name = translationDict.get( v['B_name'] )
				
				
			A_index = v['A_index']
			B_index = v['B_index']
			
			try:
				t.op( A_name ).outputConnectors[ A_index ].connect( t.op( B_name ).inputConnectors[ B_index ] )
			except:
				debug('Could not connect %s:%i to %s:%i, this may be normal during pruning.'%( A_name,A_index,B_name,B_index ) )
		
		
	
		
	def Dict_to_JSON_______________________________(self, myDict=None):
		return TDJ.jsonToText(myDict)
		
		
	def DICT_to_IO_____________________________(self, Dict=None, target=None):
		
		if op(target) == None:
			target = parent.IO.IO_SCENE()
		# define some attribute types as things we want to handle first, and last.
		# everything else can go in the middle.
		firstOrder = [	'_name',
						'_typeID',
						]
		lastOrder = ['_parent']
		
		translationDict = {}
		
		# print(jsonFile)
		# get the actual dict.
		ioDict = Dict
		
		### first pass.
		# we can iterate through our IO dict, we can discard the key, it's just a counter, though we might want it later.
		for k_,v_ in ioDict.items():
			# print(k_)
			if k_ not in ['connections'] :
		
				opName = v_['_name']
				opType = v_['_typeID']
				
				
				
				# find children in IO
				IO_Found = parent.IO.IO_TEMPLATES().findChildren(tags=[opType], depth=1)
				
				# alternatively, find children in the sampler module where our scheme template lies.
				Sampler_Found = parent.IO.EDITOR_BACKEND().op('Sampler').findChildren(tags=[opType], depth=1)
				
				# combine all sources into 1 list. we should only have 1 item in the sum of lists.
				found = IO_Found + Sampler_Found
				
				# print(opType, "-", found)
				
				found = found[0]
				
				newObj = target.copy(found, name=opName)
				
				# if we're loading or importing things that exist by name, track name change TD does so we can still perform post ops..
				translationDict[opName] = newObj.name
				
				for k2,v2 in v_.items():
					
					# now we deal with intermediate, attribute setting.
					if k2[0] != "_":
						foundAttr = getattr( newObj.par, k2, ':PAR-ERR:' )
						if foundAttr != ':PAR-ERR:':
							foundAttr.val = v2
						else:
							debug('Could not set parameter %s, probably due to format change.'%(k2))
							
							
				# try:
					# newObj.nodeCenterX = newObj.par.Tx * 2
					# newObj.nodeCenterY = newObj.par.Ty * 2
					# newObj.nodeWidth = 160
					# newObj.nodeHeight = 130
				# 	pass
				# except:
				# 	debug('-- could not set nodex/y from Tx Ty on this IO node: %s'%(newObj))
					
		
		
		return translationDict
		
		
	def GetIoJson___________________________(self):
		'''
		Creates an undo state of the current state of the IO scene and returns it's json.
		'''
		selectedOnly = False
		ioDict = self.IO_To_Dict(selectedOnly)
		ioJson = self.Dict_to_JSON(ioDict)
		
		# print(ioJson)
		
		return ioJson
	
	
		
	def Save_IO_________________________(self, selectedOnly = False):
		'''
		converts the IO scene into a dict, then to a json and then writes it to disk where user chooses.
		'''
		debug('saving IO graph...')
		IO_VIEWPORT_ = {}
		IO_VIEWPORT_['IO'] = self.IO_To_Dict(selectedOnly)
		IO_VIEWPORT_['IOCONNS'] = self.GatherConnections()
		
		ioJson = self.Dict_to_JSON(IO_VIEWPORT_)
		
		path = parent.IO.EDITOR_BACKEND().mod.tdUtils_V2.LaunchFileBrowser(load=False, start='USER\IO_VIEWPORTS',fileTypes=['GPgraph'],title='Save IO graph AS:')
		if path:
			f = open(path,'w')
			f.write(ioJson)
			f.close()
		
		return
		
		
	def Load_IO_________________________(self, ioDict=None, clearFirst = True):
		# print('attempting to load damnit')
		# parent.IO.IO_BACKEND().Refresh_Folders()
		
		templateArea = parent.IO.IO_TEMPLATES()
		
		# assume the user did not pass in a dict from a master save file somewhere... 
		# we need to handle prompting the user with a file load dialogue.
		if ioDict == None:
			# pass
			
			path = parent.IO.EDITOR_BACKEND().mod.tdUtils_V2.LaunchFileBrowser(load=True, start='USER\IO_VIEWPORTS',fileTypes=['GPgraph'],title='Load IO graph :')
			if path:
				f = open(path,'r')
				fRead = f.read()
				
				# get the actual dict.
				ioDict = TDJ.textToJSON(fRead, showErrors=True)
				
				if clearFirst:
					self.DeleteAllObjects()
				
				before = set(parent.IO.IO_SCENE().children)
				translationDict = self.DICT_to_IO( ioDict.get('IO', {}) )
				after = set(parent.IO.IO_SCENE().children)
				conns = self.Load_Conns( ioDict.get("IOCONNS", {}) , translationDict )
				
				newSel = list(after.difference(before))
				# fix name overlaps.
				for new in newSel:
					new.par.Name = self.UniquifyObjName(new.par.Name.eval())
				
				
				for newlyMadeOp in newSel:
					self.Refresh_IO_Connections(newlyMadeOp)
					# IoGatherScripts = newlyMadeOp.findChildren(tags=['_GatherIO_'])
					# for x in IoGatherScripts:
						# x.run()
				
				# update selection.
				parent.IO.IO_BACKEND().par.Lastselected = newSel[-1]
				self.Select(newSel)
				
		else:
				if clearFirst:
					self.DeleteAllObjects()
				debug('Loading IO from supplied dict...')
				self.DICT_to_IO( ioDict )
				
		# '''
		found = parent.IO.IO_SCENE().findChildren(tags=['_GatherIO_'])
		for x in found:
			x.run(delayFrames=1)
		# '''




	def GetDrivableByName(self,itemName):
		'''
		This function is generically named, because it must also exist in extensions for other areas that must be able to fetch
		an object by it's user given name. The contents of these functions will differ from area to area, but abstract that away.
		This function is mostly used by the UI mapper.
		'''
		
		retVal = None
		macroName = None
		nodeName = None

		# print(itemName)
# 
		if ':' in itemName:

			macroName = itemName.split(':')[0]
			nodeName = itemName.split(':')[1]

			foundMacros = op.IO_scene.findChildren( parName='Name', parValue=macroName, maxDepth=1, depth=1 )
			
			if len(foundMacros) == 1:
				foundNodes = foundMacros[0].op('GRAPH').findChildren( parName='Name', parValue=nodeName, maxDepth=1, depth=1 )
				# debug(foundNodes)
				if len(foundNodes) == 1:
				# assert len(foundNodes) == 1,'did not find exactly one node by this name<%s>, something is wrong, check this out'%(nodeName)
					retVal = foundNodes[0]
		else:
			nodeName = itemName
			# debug('------B-------', nodeName)
			foundNodes = op.IO_scene.findChildren( parName='Name', parValue=nodeName, maxDepth=1, depth=1 )
			# assert len(foundNodes) == 1,'did not find exactly one node by this name<%s>, something is wrong, check this out'%(nodeName)
			if len(foundNodes) == 1:
				retVal = foundNodes[0]


		return retVal
