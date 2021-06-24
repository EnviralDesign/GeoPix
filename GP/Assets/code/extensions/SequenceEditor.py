'''
SEQUENCE EDITOR
'''

import copy 
from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions

class Helper:


	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp

		ownerComp.par.w = 1000
		ownerComp.par.h = 500
		op('Data_Entry').par.w = 200

		op('win').par.borders = False

		op('toolbar/SelectMode').Click()
		op('toolbar/Snapping').Set(1)

		op('Viewer/cam').par.Reset.pulse()

		self.StartStopChop = self.ownerComp.op('null_startStop')


	def RESET(self):
		self.__init__(self.ownerComp)
		return


	def RefreshThumbnails(self):
		# refreshes macro thumbnails or whatever else we want to refresh on various other functions.
		if parent.helper.par.Ops.eval() == op.Time:
			op.Time.RefreshSequenceBlockThumbnails()


		
	# def Launch(self, target=None, parName = None, targetChannelName=None):
	def Launch(self, target, label):
		# parent().display

		parent.helper.op('win').par.winoffsety = -(parent.helper.height / 2) + (25/2)
		# parent.helper.par.Label = label
		parent.helper.par.Ops = target
	
		# we did this before cause anim editor could edit more than one source. Sequence for now cannot.
		# this is why Par parameter is disabled in parent.
		# parent.helper.par.Ops = target
		# parent.helper.par.Par = parName
		
		if parent.helper.op('win').isOpen == False:
			parent.helper.op('win').par.winopen.pulse()
		parent.helper.op('win').setForeground()

		self.EnablePicking()

		self.RefreshThumbnails()
	
		return
		
		
	def Close(self):
	
		parent.helper.op('win').par.winclose.pulse()

		op.perform.setForeground()
		
		return

	def Get_Blocks(self):
		targetOp = parent.helper.par.Ops.eval()

		if targetOp != None:
			parName = parent.helper.par.Par.eval()
			if hasattr( targetOp.par , parName ):
				foundPar = getattr( targetOp.par , parName )
				BlocksList = foundPar.eval()
				return BlocksList
			else:
				op.NOTIFV2.Notify('Could not get blocks from object.. something is wrong.')
				return None
			return
		else:
			return []

	def EnablePicking(self):
		f = parent.helper.op('Viewer').findChildren(name='*_blocks', depth=2, maxDepth=2)
		for each in f:
			each.pickable = True


	def DisablePicking(self):
		f = parent.helper.op('Viewer').findChildren(name='*_blocks', depth=2, maxDepth=2)
		for each in f:
			each.pickable = False


	def Set_Blocks(self, blocksList):

		assert isinstance(blocksList,list),'Keylist should be a list of dictionary entries.'

		targetOp = parent.helper.par.Ops.eval()
		parName = parent.helper.par.Par.eval()
		if hasattr( targetOp.par , parName ):
			foundPar = getattr( targetOp.par , parName )
			foundPar.val = blocksList
			return True
		else:
			op.NOTIFV2.Notify('Could not set blocks to object.. something is wrong.')
			return False
		return

	def Get_Selected_Blocks(self, indiciesOnly = False):
		# sel = self.Get_Selected_Blocks( indiciesOnly=True )
		BlocksList = self.Get_Blocks()
		selectedBlocks = [block for block in BlocksList if block['Selected'] == 1 ]
		selectedBlockIndicies = [i for i,block in enumerate(BlocksList) if block['Selected'] == 1 ]
		if indiciesOnly:
			return selectedBlockIndicies
		else:
			return selectedBlocks

	def Delete_Selected_Blocks(self):
		Blocks = self.Get_Blocks()
		sel = self.Get_Selected_Blocks( indiciesOnly=True )

		Blocks2 = [ block for i,block in enumerate(Blocks) if i not in sel ]

		self.Set_Blocks(Blocks2)

		return

	def Append_Block(self, BlockDict, X=None, Y=None):
		'''
		If X and Y are none, mouse position in the viewer will be used. IE for drag and drop.
		'''

		# u = (float(op('Viewer').panel.insideu) * 2) - 1
		# v = (float(op('Viewer').panel.insidev) * 2) - 1
		# w = 0
		# print(u,v,w)

		# '''

		# print(BlockDict)
		RP = op('Viewer/RENDER_PICKER/renderpick')
		RP.cook(force=1)

		if X == None:
			X = int( max( 0 ,  round( float(RP['tx']) ) )  )

		if Y == None:
			Y = int( ( float(RP['ty']) ) )

		# if Path == None:
		# 	Path = BlockDict['BlockPath']

		BlockDict['BlockStart'] = X
		BlockDict['BlockOrder'] = Y
		# BlockDict['BlockPath'] = Path

		self.SelectClear()
		Blocks = self.Get_Blocks()
		Blocks += [ BlockDict ]

		self.Set_Blocks(Blocks)
		# '''


	def Duplicate_Selected_Blocks(self):

		boundsDict = self.CalcBounds()
		width = boundsDict['xMax'] - boundsDict['xMin']

		SelectedBlocks = self.Get_Selected_Blocks( indiciesOnly=False )
		
		for block in SelectedBlocks:
			block['BlockStart'] += width

		self.SelectClear()
		self.Set_Blocks( self.Get_Blocks()+SelectedBlocks )

		self.RefreshThumbnails()

		return





	def get_attribute(self, attributeName):
		BlocksList = self.Get_Blocks()
		selectedBlocks = [ block[attributeName] for i,block in enumerate(BlocksList) ]
		return selectedBlocks


	def getAspect(self, viewerComp):
		W = viewerComp.width
		H = viewerComp.height #  - 25 # 25 is how tall the toolbar is

		if(W > H):
			maxDim = max(W,H)
		elif(W < H):
			maxDim = min(W,H)

		W /= maxDim
		H /= maxDim

		return [W,H]


	def CalcBounds(self):
		
		sel = self.Get_Selected_Blocks( indiciesOnly=True )

		BlockStart = self.get_attribute('BlockStart')
		BlockLength = self.get_attribute('BlockLength')
		BlockOrder = self.get_attribute('BlockOrder')

		 # filter down to selected IF there is any selected.
		if len( BlockStart ) > 0 and len(sel) > 0:
			BlockStart = [ each for i,each in enumerate(BlockStart) if i in sel ]
			BlockLength = [ each for i,each in enumerate(BlockLength) if i in sel ]
			BlockOrder = [ each for i,each in enumerate(BlockOrder) if i in sel ]

		elif len( BlockStart ) > 0 and len(sel) == 0:
			BlockStart = BlockStart
			BlockLength = BlockLength
			BlockOrder = BlockOrder

		elif len( BlockStart ) == 0:
			
			BlockStart = [self.StartStopChop['Timestart'][0]]
			BlockLength =[ self.StartStopChop['Timestop'][0]]
			BlockOrder = [-1,2]

		xVals = BlockStart + [ each[0]+each[1] for each in zip( BlockStart , BlockLength ) ]
		yVals = BlockOrder + [ each+1 for each in BlockOrder ]


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

		# if no items are avail to calc, we just overwrite our min/max with size of timeline graph.
		# if len( sel ) == 0:
		# 	returnDict['xMin'] = float(self.StartStopChop['Timestart'][0] if self.StartStopChop['Timestart'] != None else 0)
		# 	returnDict['xMax'] = float(self.StartStopChop['Timestop'][0] if self.StartStopChop['Timestop'] != None else 1)
		# 	returnDict['yMin'] = 0
		# 	returnDict['yMax'] = 5

		return returnDict


	def HomeGraphCamToBounds(self):
		
		boundsDict = self.CalcBounds()

		aspect = self.getAspect( parent.helper.op('Viewer') )

		cam = parent.helper.op('Viewer').op('cam')
		cam.par.tx = ((boundsDict['xMin'] + boundsDict['xMax']) / 2)
		cam.par.ty = ((boundsDict['yMin'] + boundsDict['yMax']) / 2)

		cam.par.sx = (boundsDict['xMax'] - boundsDict['xMin']) * (1/aspect[0])
		cam.par.sy = (boundsDict['yMax'] - boundsDict['yMin']) * (1/aspect[1])

		boundsAspectX = cam.par.sx.eval()
		boundsAspectY = cam.par.sy.eval()
		maxAspectBound = max(boundsAspectX,boundsAspectY)
		boundsAspectX /= maxAspectBound
		boundsAspectY /= maxAspectBound

		reductionFactor = 10

		paddingX = cam.par.sx / reductionFactor
		paddingY = cam.par.sy / reductionFactor

		cam.par.sx += (paddingX / 1) * (1/aspect[0])
		cam.par.sy += (paddingY / 1) * (1/aspect[1])


		toolBarHeightFractional = 25 / parent().height
		cam.par.ty += paddingY*.1

		self.EnablePicking()

		return


	def TranslateKeys_Init(self):

		sel = self.Get_Selected_Blocks( indiciesOnly=True )
		# debug(sel)

		w = self.get_attribute('BlockLength')
		x = self.get_attribute('BlockStart')
		y = self.get_attribute('BlockOrder')
		f1 = self.get_attribute('FadeIn')
		f2 = self.get_attribute('FadeOut')

		initDict = {}
		for i in sel:
			initDict[i] = {}
			initDict[i]['w'] = w[i]
			initDict[i]['x'] = x[i]
			initDict[i]['y'] = y[i]
			initDict[i]['f1'] = f1[i]
			initDict[i]['f2'] = f2[i]
			initDict[i]['id'] = i

		# print(initDict)

		parent.helper.store('initPos',initDict)



	def TranslateKeys_Move(self, mode):


		CU = parent.helper
		xDist = CU.par.Dragx - CU.par.Startx
		yDist = CU.par.Dragy - CU.par.Starty

		BlocksList = self.Get_Blocks()

		initDict = CU.fetch('initPos',{})
		for k,v in initDict.items():
			
			if mode == 'block':
				w = v['w']
				x = max( int(round(v['x'] + xDist)) , 0 )
				y = int(round(v['y'] + yDist))
				f1 = v['f1']
				f2 = v['f2']

			elif mode == 'block-left':
				maxAllowedX = ( v['x'] + v['w'] - 1)
				x = min(  max( int(round(v['x'] + xDist)) , 0 )  ,  maxAllowedX )
				w = max( v['w'] - max( int(round(xDist)) , -v['x'] ) , 1 )
				y = v['y']
				f1 = v['f1']
				f2 = v['f2']

			elif mode == 'block-right':
				w = max( v['w'] + int(round(xDist)) , 1 )
				x = v['x']
				y = v['y']
				f1 = v['f1']
				f2 = v['f2']

			elif mode == 'block-fadeleft':
				w = v['w']
				x = v['x']
				y = v['y']
				f1 = min(  max( v['f1'] + int(round(xDist)) , 0 )  ,  v['w']-v['f2']-1  )
				f2 = v['f2']

			elif mode == 'block-faderight':
				w = v['w']
				x = v['x']
				y = v['y']
				f1 = v['f1']
				f2 =  min( max( v['f2'] - int(round(xDist)) , 0 ) , (v['w']-v['f1']-1) )


			BlocksList[k]['BlockLength'] = w
			BlocksList[k]['BlockStart'] = x
			BlocksList[k]['BlockOrder'] = y
			BlocksList[k]['FadeIn'] = f1
			BlocksList[k]['FadeOut'] = f2

		self.Set_Blocks(BlocksList)

		return
			


	
	def boundsCheck(self, AABB, aX, aY, bX, bY):
		'''
		uses aabb testing logic.
		'''

		# marquee box left/right/top/bottom.
		mq_L = min(aX,bX)
		mq_R = max(aX,bX)
		mq_B = min(aY,bY)
		mq_T = max(aY,bY)

		# aabb left/right/top/bottom.
		ab_L = AABB[0]
		ab_B = AABB[1]
		ab_R = AABB[2]
		ab_T = AABB[3]

		a = {
			'x':(ab_R+ab_L)/2, 
			'y':(ab_T+ab_B)/2,
			'width':ab_R-ab_L,
			'height':ab_T-ab_B
			}

		b = {
			'x':(mq_R+mq_L)/2, 
			'y':(mq_T+mq_B)/2,
			'width':mq_R-mq_L,
			'height':mq_T-mq_B
			}

		aabb_result = 	(
							abs(a['x'] - b['x']) * 2 < (a['width'] +  b['width'] ) and 
							abs(a['y'] - b['y']) * 2 < (a['height'] + b['height'])
						)

		return aabb_result


	def MarqueeSelect(self, aX, aY, bX, bY):
		'''
		input vals should be world space coords
		'''
		Lengths = self.get_attribute('BlockLength')

		L = self.get_attribute('BlockStart')
		B = self.get_attribute('BlockOrder')
		T = [each+1 for each in B]
		R = [each+Lengths[i] for i,each in enumerate(L)]

		# LB = list(zip(L,B))
		# RB = list(zip(R,B))
		# RT = list(zip(R,T))
		# LT = list(zip(L,T))

		LBRT = list(zip(L,B,R,T))

		newSel = [ i for i,AABB in enumerate(LBRT) if self.boundsCheck(AABB, aX, aY, bX, bY ) ]

		self.Select(newSel)

		self.RefreshThumbnails()
		
		return
		



	def Select(self, blockID=[]):
		
		newSel = list(set(blockID))
		blockList = self.Get_Blocks()

		for i,block in enumerate(blockList):
			block['Selected'] = (i in newSel)*1

		self.Set_Blocks( blockList )

		self.RefreshThumbnails()
		
		return
			


	def SelectAdd(self, blockID=[]):
		
		newSel = list(set(blockID))
		blockList = self.Get_Blocks()

		for i,block in enumerate(blockList):
			block['Selected'] = max( (i in newSel)*1 , block['Selected'] )

		self.Set_Blocks( blockList )

		self.RefreshThumbnails()
		
		return
			


	def SelectRemove(self, blockID=[]):

		newSel = list(set(blockID))
		blockList = self.Get_Blocks()

		for i,block in enumerate(blockList):
			block['Selected'] = min( (i not in newSel)*1 , block['Selected'] )

		self.Set_Blocks( blockList )

		self.RefreshThumbnails()
		
		return
			


	def SelectClear(self):

		blockList = self.Get_Blocks()

		for i,block in enumerate(blockList):
			block['Selected'] = 0

		self.Set_Blocks( blockList )

		self.RefreshThumbnails()
		
		return


	def ResetSelectedBlockToDefaultLength(self):
		blockList = parent.helper.Get_Selected_Blocks()
		
		if len(blockList) == 1:
			SelectedBlockPath = blockList[0]['BlockPath']
			# print(SelectedBlockPath)
			
			templateDat = parent.helper.op('null_templates')
			templateDict = eval(templateDat[SelectedBlockPath,'dict'].val)
			
			BlockLength = int( templateDict['BlockLength'] )
			
			parent.helper.AttribEditor_SET( {'BlockLength':BlockLength} )



	def AttribEditor_GET(self, argDict={}):

		''' Arg dict can look like this - this is looked up in /UberGui/Viewer/Data_Entry/SET_LOOKUP
		{
			"BlockType":"Audio",
			"BlockName":"MyMp3",
			"BlockStart":0,
			"BlockLength":60,
			"Intensity":1,
			"FadeIn":0,
			"FadeOut":0,
			"BlockOrder":0,
			"BlockPath":"D:/Music/Bassnectar_Paracosm.mp3",
			"Selected": False
		}
		'''
		lookupDat = parent.helper.op("Data_Entry/SET_LOOKUP")
		# debug(lookupDat)
		for k,v in argDict.items():
			foundRow = lookupDat.row(k)
			if foundRow != None:
				targetWidget = op(foundRow[1])

				if k in ['BlockStart','BlockLength', 'FadeIn', 'FadeOut']:

					if k in ['BlockStart']:
						extraAddy = 1
					else:
						extraAddy = 0
				# if k in ['BlockStart']:
					if parent.helper.par.Unitoftime.eval() == "frames":
						targetWidget.par.Value0 = int(float(v))+extraAddy # if setting the frame, we want the user to work in 1 based, but backend is 0 based.
					elif parent.helper.par.Unitoftime.eval() == "seconds":
						targetWidget.par.Value0 = op.sceneOutliner.mod.tdUtils.Frames_2_Seconds( int(v)+extraAddy , parent.helper.par.Fps.eval() )
					elif parent.helper.par.Unitoftime.eval() == "beats":
						targetWidget.par.Value0 = op.sceneOutliner.mod.tdUtils.Frames_2_Beats( int(v)+extraAddy , parent.helper.par.Fps.eval(), parent.helper.par.Bpm.eval() )
				else:
					
					# if targetWidget.name == 'BlockType_dropdown':
						# print(targetWidget, v)
					targetWidget.par.Value0 = v

			else:
				debug(k, 'did not exist in lookup dat...')

		return



	def AttribEditor_SET(self, argDict={}):
		
		# these following commands fetch the parameter, from the object currently sourced.
		# lookupDat = parent.helper.op("Data_Entry/SET_LOOKUP")

		# get our Keylist and selection list.
		BlockList = self.Get_Blocks()
		sel = self.Get_Selected_Blocks( indiciesOnly=True )
		lookupDat = parent.helper.op("Data_Entry/SET_LOOKUP")
					

		for selectedKeyIndex in sel:
			for widgetPath,newValue in argDict.items():

				foundCell = lookupDat.findCell(widgetPath)
				blockAttrName = lookupDat[foundCell.row,0].val

				value = copy.copy(newValue)

				# if blockAttrName in ['BlockLength']:
					# debug(value)
				# print(k,value)
			
				if blockAttrName in ['BlockStart','BlockLength', 'FadeIn', 'FadeOut']:
				# if blockAttrName in ['BlockStart']:

					if parent.helper.par.Unitoftime.eval() == "frames":
						value = int(value)
					elif parent.helper.par.Unitoftime.eval() == "seconds":
						value = op.sceneOutliner.mod.tdUtils.Seconds_2_Frames( value , parent.helper.par.Fps.eval() )
					elif parent.helper.par.Unitoftime.eval() == "beats":
						value = op.sceneOutliner.mod.tdUtils.Beats_2_Frames( value , parent.helper.par.Fps.eval() , parent.helper.par.Bpm.eval() )
						
					if blockAttrName in ['BlockStart']:
						value -= 1

					value = max(value,0)

					if blockAttrName in ['BlockLength']:
						value = max(value,1)
				
				elif blockAttrName in ['Intensity']:
					value = tdu.clamp(value,0,1)

				else:
					pass

				# if blockAttrName in ['BlockStart']:
				# 	debug(value)
				BlockList[selectedKeyIndex][blockAttrName] = value

		self.Set_Blocks(BlockList)
		

		return