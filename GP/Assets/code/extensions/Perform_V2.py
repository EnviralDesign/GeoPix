"""
PERFORM Ext
"""

class ext:
	"""
	ext description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self.CanvasRoot = op('Layout/Canvas_Wrapper')
		self.MacroChooser = self.ownerComp.op('Macro_Chooser')

		self.MacroChooser.par.display = False
		self.MacroChooser.par.Targetmacrowidget = ''

	def RESET(self):
		# debug('reset Perform V2')

		canvasesToDelete = self.GetCanvasByIds( list(range(1,99)) )
		for c in canvasesToDelete:
			c.destroy()

		widgetsInDefaultCanvas = self.GetChildrenWidgetsOfCanvas([0])

		for widget in widgetsInDefaultCanvas:
			widget.destroy()

		defaultCanvas = self.GetCanvasById(0)
		defaultCanvas.op('base_generate_bg/cache1').par.activepulse.pulse()
		defaultCanvas.par.Divisions1 = 17
		defaultCanvas.par.Divisions2 = 9

		self.MacroChooser.par.display = False
		self.MacroChooser.par.Targetmacrowidget = ''


		op.PerformUI.RESET()
		
		return

	def MakeWidgetNameUnique(self, widget ):

		d = {'prev':widget.par.Name.eval()}
		Name_Uniquify_script = widget.op('UNIQUIFY_NAME/Name_Uniquify')
		if Name_Uniquify_script != None:
			Name_Uniquify_script.run( widget.par.Name.eval() )
		
		d = {'new':widget.par.Name.eval()}
		return d

	def RefreshWidgetExtension(self, widget, parlist ):
		ExtensionRefreshScript = widget.op('EXTENSION_REFRESHER/ExtensionRefreshScript')
		if ExtensionRefreshScript != None:
			ExtensionRefreshScript.run( [ p.name for p in parlist ] )
		else:
			debug('no extension refresh script found!')

		return

	def GetCurrentCanvas(self):
		canvasRoot = self.CanvasRoot
		activeCanvasID = parent.Perform.par.Activecanvas.eval()
		return canvasRoot.op('Canvas%i'%(activeCanvasID))

	def GetCurrentCanvasID(self):
		canvasRoot = self.CanvasRoot
		activeCanvasID = parent.Perform.par.Activecanvas.eval()
		return activeCanvasID

	def GetCanvasById(self, ID):
		canvasRoot = self.CanvasRoot
		return canvasRoot.op('Canvas%i'%(ID))

	def GetCanvasByIds(self, IDs):
		canvasRoot = self.CanvasRoot
		return [ canvasRoot.op('Canvas%i'%(ID)) for ID in IDs if canvasRoot.op('Canvas%i'%(ID)) != None ]

	def GetAllCanvases(self):
		canvasRoot = self.CanvasRoot
		canvases = canvasRoot.findChildren(name="Canvas[0-99]")
		return canvases



	def GetChildrenWidgetsOfCanvas(self,ID=[]):
		'''
		leaving a blank ID arg list, will query widgets from all available canvases.
		'''

		if len(ID) > 0:
			canvases = [ self.GetCanvasById(x) for x in ID ]
		else:
			canvases = self.GetAllCanvases()

		widgets = [ canvas.findChildren(parName='Objtype', maxDepth=1, depth=1) for canvas in canvases ]
		widgets = [widget for widgetList in widgets for widget in widgetList] # unravel nested list into 1d list
		
		return widgets

	def GetChildrenWidgetsOfCurrentCanvas(self):
		currentCanvasID = self.GetCurrentCanvasID()
		widgets = self.GetChildrenWidgetsOfCanvas([currentCanvasID])
		return widgets

	def GetSelectedWidgets(self):

		sel = [ parent.Perform.par.Selectedwidget.eval() ]

		allWidgetsInCanvas = self.GetChildrenWidgetsOfCurrentCanvas()
		selectedWidgetsInCanvas = [ each for each in allWidgetsInCanvas if each in sel ]
		return selectedWidgetsInCanvas

	def GetAllWidgets(self):

		allCanvases = self.GetAllCanvases()
		canvasIDs = [ x.digits for x in allCanvases ]
		allWidgets = self.GetChildrenWidgetsOfCanvas(canvasIDs)

		return allWidgets

	def GetDrivableByName(self,widgetName):
		'''
		This function is generically named, because it must also exist in extensions for other areas that must be able to fetch
		an object by it's user given name. The contents of these functions will differ from area to area, but abstract that away.
		This function is mostly used by the UI mapper.
		'''
		allWidgets = self.GetChildrenWidgetsOfCanvas()

		matchingWidgets = [ each for each in allWidgets if each.par.Name.eval() == widgetName ]
		# matchingWidgets = [ each for each in allWidgets if widgetName in each.Knobs().keys() ]
		if len(matchingWidgets) == 1:
			return matchingWidgets[0]
		else:
			return None



	def GetBoundsOfWidgets(self, widgets=[]):

			if len(widgets) > 0:
				xMin = min([ each.par.Position1.eval() for each in widgets ])
				xMax = max([ each.par.Position1.eval()+each.par.Size1.eval() for each in widgets ])
				xDif = xMax - xMin

				yMin = min([ each.par.Position2.eval() for each in widgets ])
				yMax = max([ each.par.Position2.eval()+each.par.Size2.eval() for each in widgets ])
				yDif = yMax - yMin
			else:
				xMin=0
				xMax=0
				xDif = xMax - xMin
				yMin=0
				yMax=0
				yDif = yMax - yMin


			d = {}
			d['xMin'] = xMin
			d['xMax'] = xMax
			d['yMin'] = yMin
			d['yMax'] = yMax
			d['xDif'] = xDif
			d['yDif'] = yDif

			return d



	def CreateWidget(self, opId):
		templateWidget = op(opId)
		targetCanvas = self.GetCurrentCanvas()

		previousWidgets = self.GetSelectedWidgets()
		canvasWidgets = self.GetChildrenWidgetsOfCurrentCanvas()
		matchingCanvasWidgets = [ x for x in canvasWidgets if x.par.Objtype.eval() == op(opId).par.Objtype.eval() ]

		# detect and disallow creation of more than one system widget on a canvas.
		Types = [ x.par.Objtype.eval() for x in matchingCanvasWidgets ]
		AnySystemWidgets = max([ x >= 50 for x in Types ]) if len(Types) > 0 else False
		if AnySystemWidgets:
			op.NOTIFV2.Notify('Selection contains System Widgets. You cannot duplicate more than one of these per Canvas. Please adjust selection and try again.')
			return

		bounds = self.GetBoundsOfWidgets(previousWidgets)

		assert targetCanvas != None, 'Canvas index %i does not exist.. should not happen!'%(activeCanvasID)
		assert templateWidget != None, 'Template widget does not exist, this shouldnt happen'
		
		newWidget = targetCanvas.copy(templateWidget)


		if bounds['xDif'] <= bounds['yDif']:
			newWidget.par.Position1 = bounds['xMax']
			newWidget.par.Position2 = bounds['yMin']
		else:
			newWidget.par.Position1 = bounds['xMin']
			newWidget.par.Position2 = bounds['yMax']

		self.ownerComp.par.Selectedwidget = newWidget

		self.MakeWidgetNameUnique(newWidget)

		op.PerformUI.CloseCreateDialogue()


		return

	def DeleteSelectedWidget(self, widget=None):

		targetCanvas = self.GetCurrentCanvas()
		if widget == None:
			currentlySelectedWidget = self.ownerComp.par.Selectedwidget.eval()
			if currentlySelectedWidget != None and currentlySelectedWidget in targetCanvas.children:
				currentlySelectedWidget.destroy()
			else:
				op.NOTIFV2.Notify('No valid Widget selected in this Canvas to delete.')

		return

	def DeleteAllWidgetsInCurrentCanvas(self):
		widgets = self.GetChildrenWidgetsOfCanvas([self.GetCurrentCanvasID()])
		for widget in widgets:
			widget.destroy()

		return

	def ConstrainWidgets(self):
		canvas = self.GetCurrentCanvas()

		gridSizeX = canvas.width / canvas.par.Divisions1.eval()
		gridSizeY = canvas.height / canvas.par.Divisions2.eval()
		for widget in canvas.findChildren(depth=1,maxDepth=1,parName="Objtype"):
			
			freeX = widget.par.Position1.eval()+widget.par.Size1.eval()
			counterCorrectX = canvas.par.Divisions1.eval()-freeX
			widget.par.Position1 += min( counterCorrectX , 0 )
			widget.par.Position1 = max( widget.par.Position1 , 0 )
			
			freeY = widget.par.Position2.eval()+widget.par.Size2.eval()
			counterCorrectY = canvas.par.Divisions2.eval()-freeY
			widget.par.Position2 += min( counterCorrectY , 0 )
			widget.par.Position2 = max( widget.par.Position2 , 0 )

			maxAllowedSizeX = canvas.par.Divisions1.eval() - widget.par.Position1.eval()
			maxAllowedSizeY = canvas.par.Divisions2.eval() - widget.par.Position2.eval()

			widget.par.Size1 = min( widget.par.Size1 , maxAllowedSizeX )
			widget.par.Size2 = min( widget.par.Size2 , maxAllowedSizeY )


	def DuplicateSelectedWidgets(self):

		widgets = self.GetSelectedWidgets()

		Types = [ x.par.Objtype.eval() for x in widgets ]
		AnySystemWidgets = max([ x >= 50 for x in Types ])
		if AnySystemWidgets:
			op.NOTIFV2.Notify('Selection contains System Widgets. You cannot duplicate more than one of these per Canvas. Please adjust selection and try again.')
			return

		if len(widgets) > 0:
			canvas = widgets[0].parent.canvas
			bounds = self.GetBoundsOfWidgets(widgets)
			newWidgets = canvas.copyOPs(widgets)

			for each in newWidgets:
				if bounds['xDif'] <= bounds['yDif']:
					each.par.Position1 += bounds['xDif']
				else:
					each.par.Position2 += bounds['yDif']

				self.MakeWidgetNameUnique(each)

			self.ownerComp.par.Selectedwidget = newWidgets[-1]
		return



	def LaunchMacroChooser(self, MacroWidgetRef):
		'''
		Launches the helper UI for choosing/assigning a Macro in IO to a Macro Widget in the Perform tab.
		'''
		if op(MacroWidgetRef) == None:
			debug('Macro Widget Reference cannot be None..')
			return

		self.MacroChooser.par.display = True
		self.MacroChooser.par.Targetmacrowidget = MacroWidgetRef


	def UpdateAllGroupAssignments( self ):
		'''
		Brute force update of all Group's member assignments. This will only be called
		when things are being edited in Edit Mode, or if a Macro name changes, etc.
		During perform, this will never be called, so it can be a bit heavy handed.
		'''
		allWidgets = self.GetAllWidgets()

		MacroWidgets = [ x for x in allWidgets if x.par.Objtype.eval() in [11] ]
		for each in MacroWidgets:
			each.ClearGroup()
			each.RefreshKnobs()


		GroupWidgets = [ x for x in allWidgets if x.par.Objtype.eval() in [12] ]

		for each in GroupWidgets:
			each.AssignMembers()

		return


	def MacroWidget_Translate(self, oldName, newName):
		'''
		Will look through all macro widgets, and translate any names from old, if it matches
		to new. This is called from the IO tab, when a Macro's name changes. this normally breaks lots
		of connections, but this function takes care of fixing it in the Perform tab.
		'''
		if oldName == None or newName == None:
			return

		allWidgets = self.GetAllWidgets()
		WidgetMacros = [ x for x in allWidgets if x.par.Objtype.eval() in [11] ]

		for each in WidgetMacros:
			if each.par.Macroname.eval() == oldName:
				each.par.Macroname = newName
				each.par.Name = newName

		self.UpdateAllGroupAssignments()

		return




	def AddSelectedWidgetToIo______________(self):
		'''
		currently disabled, cause we do not know which sub channel should be captured when created this way.
		'''
		sel = self.GetSelectedWidgets()
		if len(sel) == 1:
			Name = sel[0].par.Name.eval()

			widgetCaptureTemplate = op.IO_TEMPLATES_V3.op('CHAN/Capture_/WidgetCapture')
			assert widgetCaptureTemplate != None, "WidgetCapture node must not be None"
			
			newIoNode = op.IOV2.CreateNode(widgetCaptureTemplate.id, inRoot=True)

			newIoNode.par.Widgetselector = Name

			op.IOV2.par.Context = ''
			op.IOV2.par.Contextend = ''
			op.IOV2.par.Mousebutton = ''
			op.IOV2.par.Placetarget = ''


		return