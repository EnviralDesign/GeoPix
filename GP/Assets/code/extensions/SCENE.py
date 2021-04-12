"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""

from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions

nodeSizeX = 100
nodeBufferX = 10
TD_Coord_Multiplier = 2

class SCENE:
	"""
	SCENE description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp



	def EnterSelectedMacro(self):
		'''
		parent.IO.IO_BACKEND().EnterSelectedMacro()
		'''
		sel = parent.IO.IO_BACKEND().GetSelected()
		if len(sel) == 1:
			sel[0].par.Entermacro.pulse()
		

		return

	def ExitCurrentMacro(self):
		'''
		parent.IO.IO_BACKEND().EnterSelectedMacro()
		'''
		macroWereExiting = parent.IO.par.Scenegeocomp.eval()
		macroWereExiting.parent.obj.op('PREVIEW/connectItUp').run()
		parent.IO.par.Scenegeocomp = parent.IO.par.Scenegeocomp.default
		op.IOV2.par.Lastselected = ''
		

		return



	def CreateNode(self, nodeID, inRoot=False):

		srcOp = op(nodeID)
		
		assert srcOp != None , 'Node %s could not be created..., this should not happen'%(str(nodeID))

		if inRoot == True:
			newlyMadeOp = op.IO_scene.copy(srcOp) # make in root no matter where user is,
		else:
			newlyMadeOp = parent.IO.IO_SCENE().copy(srcOp) # make in active container.

		newName = parent.IO.IO_BACKEND().UniquifyObjName( newlyMadeOp.par.Name.eval() )
		newlyMadeOp.par.Name = newName

		parent.IO.IO_BACKEND().Select( [newlyMadeOp] )
		
		parent.IO.par.Context = "node-place"
		parent.IO.par.Mousebutton = "hover"
		parent.IO.par.Placetarget = newlyMadeOp
		
		parent.IO.IO_BACKEND().Refresh_IO_Connections(newlyMadeOp)

		if newlyMadeOp.par.Objtype == 10:
			# debug('just created macro')
			newlyMadeOp.op('PREVIEW/cache_active_when_selected').par.replacespulse.pulse()

		op.IoGraphUI.CloseCreateDialogue()

		return newlyMadeOp




	def CopySelectedNodes(self):

		sel = parent.IO.IO_BACKEND().GetSelectedObjects()
		parent.IO.par.Copiednodes = ' '.join([ str(x.id) for x in sel ])
		parent.IO.par.Copyorcut = False # copy mode
		return




	def CutSelectedNodes(self):

		sel = parent.IO.IO_BACKEND().GetSelectedObjects()
		parent.IO.par.Copiednodes = ' '.join([ str(x.id) for x in sel ])
		parent.IO.par.Copyorcut = True # cut mode
		return




	def PasteNodes(self):

		Copyorcut = parent.IO.par.Copyorcut.eval()

		sel = parent.IO.par.Copiednodes.eval()
		sel = [ op(int(x)) for x in sel.split(' ') ]
		sel = [ x for x in sel if x != None ]


		Isgraphroot = parent.IO.IO_VIEWPORT().par.Isgraphroot.eval()
		# ['AllowedInMacro','AllowedInRoot','AllowedEverywhere']
		boolStruct = [ [True,False,True],[False,True,True] ][Isgraphroot]
		localityFilteredSel = [ each for each in sel if boolStruct[each.par.Locality.menuIndex] == True ]

		if len(localityFilteredSel) != len(sel):
			op.NOTIFV2.Notify('Some of the cut/copied nodes could not be pasted here due to their locality resitrictions and were omitted.')

		# newSel = parent.IO.IO_SCENE().copyOPs(sel)
		newSel = parent.IO.IO_SCENE().copyOPs(localityFilteredSel)

		if Copyorcut == True: # if user CUT, and not COPY
			for each in sel:
				each.destroy()
		
		for new in newSel:
			new.par.Name = parent.IO.IO_BACKEND().UniquifyObjName(new.par.Name.eval())

		boundsDict = parent.IO.IO_BACKEND().CalculateSelectedObjectsBounds( )
		xSize = ((boundsDict['maxx']-boundsDict['minx']) + 100) * 0
		ySize = ((boundsDict['maxy']-boundsDict['miny']) + 100) * -1
		
		# offset duplicated objects to be non overlapping by bounding size.
		for newOp in newSel:
			newOp.par.Tx += xSize
			newOp.par.Ty += ySize
			newOp.nodeX = newOp.par.Tx*2
			newOp.nodeY = newOp.par.Ty*2
		
		for newlyMadeOp in newSel:
			parent.IO.IO_BACKEND().Refresh_IO_Connections(newlyMadeOp)
		
		# update selection.
		parent.IO.IO_BACKEND().par.Lastselected = newSel[-1]
		parent.IO.IO_BACKEND().Select(newSel)
		

		return
			
			
			