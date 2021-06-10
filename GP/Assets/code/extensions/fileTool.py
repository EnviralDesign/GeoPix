"""
SAVE LOAD V3
"""

import json
import os
import ctypes

class ext:
	"""
	ext description 
	"""
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp
		
		# set default dimensions
		self.ownerComp.par.w = 1200
		self.ownerComp.par.h = 700

		# generate abs paths to some relative folders.
		DefaultUserSavePath = tdu.expandPath( 'LIBRARY/PROJECTS' )
		DefaultUserPrefabPath = tdu.expandPath( 'LIBRARY/PREFABS' )
		DefaultFileFolderPath = tdu.expandPath( 'LIBRARY' )

		# setup some properties/attributes.
		self.DefaultUserSavePath = DefaultUserSavePath
		self.DefaultUserPrefabPath = DefaultUserPrefabPath
		self.fileSysDat = op('Body/center/null_file_sys')
		self.BackQue = []
		self.ForwardQue = []
		self.targetOperators = []
		self.parameterName = ''
		self.exitAfterSave = False

		# reset some internal UI.
		self.ownerComp.op('Body/leftBar').par.w = 200
		self.ownerComp.op('Body/center/secondaryBar').par.w = 200
		self.ownerComp.op('Body/leftBar/container_Volumes').par.h = 165
		self.ownerComp.op('Body/leftBar/container_System_Folders').par.h = 215

		# reset all custom parmaeters to their defaults.
		for p in ownerComp.customPars:
			p.val = p.default

		# set some initial File Tool Paths for various contexts.
		# NOTE: This must happen after parameters are reset to defaults.
		self.ownerComp.par.Savepath = DefaultUserSavePath
		self.ownerComp.par.Loadpath = DefaultUserSavePath
		self.ownerComp.par.Importpath = DefaultUserPrefabPath
		self.ownerComp.par.Filepath = DefaultFileFolderPath
		self.ownerComp.par.Folderpath = DefaultFileFolderPath

		# reset the filter string field to blank.
		self.ownerComp.op('Body/top/field/string_Realtime')[0,0] = ''

		f = self.ownerComp.op('Body/center/secondaryBar').findChildren( name='item[1-99]', depth=1 )
		for each in f:
			each.par.Value0 = True


	def RESET(self):
		'''
		Reset the tool by reinitializing it.
		'''
		self.__init__(self.ownerComp)
		return


	def Close(self):
		'''
		attempt to close the window comp.
		'''
		self.ownerComp.op('window').par.winclose.pulse()
		self.targetOperators = []
		self.parameterName = ''
		self.ownerComp.par.Extension = ''
		return


	def Launch(self, mode, targetOperators=[], parameterName='', extension='', startingPath='', quitAfterSave=False):
		'''
		attempt to launch the window comp.
		valid modes:
		saveproject
		loadproject
		importproject
		choosefile
		choosefolder

		ie
		op.SAVE_LOAD.Launch(mode='saveproject')
		'''

		self.ownerComp.par.Extension = extension
		self.exitAfterSave = quitAfterSave

		if mode in ['choosefile','choosefolder']:
			assert len(targetOperators) > 0 and len(parameterName) > 0,'To launch file chooser or folder chooser must provide target operators and parameter name.'
			self.targetOperators = targetOperators
			self.parameterName = parameterName

			if mode == 'choosefile':
				self.ownerComp.par.Allfiles = True
				self.ownerComp.par.Folders = True
				self.ownerComp.par.Imagefiles = True
				self.ownerComp.par.Moviefiles = True
				self.ownerComp.par.Audiofiles = True
				self.ownerComp.par.Geopixfiles = True
			elif mode == 'choosefolder':
				self.ownerComp.par.Allfiles = False
				self.ownerComp.par.Folders = True
				self.ownerComp.par.Imagefiles = False
				self.ownerComp.par.Moviefiles = False
				self.ownerComp.par.Audiofiles = False
				self.ownerComp.par.Geopixfiles = False
		else:
			self.targetOperators = []
			self.parameterName = ''
			self.ownerComp.par.Allfiles = False
			self.ownerComp.par.Folders = True
			self.ownerComp.par.Imagefiles = False
			self.ownerComp.par.Moviefiles = False
			self.ownerComp.par.Audiofiles = False
			self.ownerComp.par.Geopixfiles = True

		self.ownerComp.par.Mode = mode

		if self.fileSysDat.numRows > 1:
			firstNameItem = self.fileSysDat[1,'name'].val
			self.ownerComp.par.Filename = firstNameItem

		startingPathInfo = tdu.PathInfo( startingPath )
		if startingPathInfo.isDir:
			absPath = startingPathInfo.absPath
			pathPar = self.get_current_path_param()
			pathPar.val = absPath
		elif startingPathInfo.isFile:
			absPath = startingPathInfo.dir
			pathInfo2 = tdu.PathInfo( absPath )
			if pathInfo2.exists:
				absPath2 = pathInfo2.absPath
				pathPar = self.get_current_path_param()
				pathPar.val = absPath


		self.ownerComp.op('window').par.winopen.pulse()
		return


	#########################################################################
	############### HELPER FUNCTIONS - meant to be called internally only ###
	#########################################################################


	def get_base_names_from_current_dir(self):
		'''
		a helper function that returns a list of base names, with out suffix from the folder dat.
		not meant to be called directly.
		'''
		return list(map(str,self.fileSysDat.col('basename')[1::]))


	def get_current_path_param(self):
		'''
		Helper function to get the correct parameter based on what mode the tool is in.
		This is not meant to be called directly.
		'''
		attrLookup = {
		'saveproject':'Savepath',
		'loadproject':'Loadpath',
		'importproject':'Importpath',
		'choosefile':'Filepath',
		'choosefolder':'Folderpath',
		}

		FileToolMode = self.ownerComp.par.Mode.eval()
		ParName = attrLookup[FileToolMode]
		retrievedPar = getattr( self.ownerComp.par , ParName )
		return retrievedPar


	def set_name_field(self, val):
		'''
		Helper function to get the field COMP for the name/folder entry at bottom.
		'''
		self.ownerComp.op('Body/bot/fieldString_FileFolderName').par.Value0 = val
		return


	def store_directory_to_back_que(self, pathStr):
		'''
		Simple wrapper function to store a directory string to the back que.
		'''
		self.BackQue.append( pathStr )
		return


	def store_directory_to_forward_que(self, pathStr):
		'''
		Simple wrapper function to store a directory string to the forward que.
		'''
		self.ForwardQue.append( pathStr )
		return


	def clear_forward_que(self):
		'''
		Clears the forward que
		'''
		self.ForwardQue = []
		return


	def clear_back_que(self):
		'''
		Clears the back que
		'''
		self.ForwardQue = []
		return


	def is_string_integer(self, testStr):
		try: 
			int(testStr)
			return True
		except ValueError:
			return False


	#########################################################################
	############### PUBLIC FUNCTIONS - can be called from anywhere ##########
	#########################################################################

	def Reset_ExitAfterSave(self):
		'''
		convenience wrapper function for resetting the exit after flag to False.
		'''
		self.exitAfterSave == False
		return

	def GetDiskVolumes(self):
		'''
		returns the disk volumes available.
		NOTE: This only works for windows at present, as it makes the assumption a drive starts with an uppercase letter.
		TODO: support OSX in the future.
		'''
		dl = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
		drives = ['%s:/' % d for d in dl if os.path.exists('%s:' % d)]
		return drives


	def GetUserSystemFolders(self):
		'''
		returns a list of valid/existing user folders like Desktop, Documents, etc.
		NOTE: This only works for windows at present.
		TODO: support OSX in the future.
		'''

		suffixsOfInterest = [
			'\\Desktop',
			'\\Documents',
			'\\Downloads',
			'\\Favorites',
			'\\Music',
			'\\Videos',
		]

		ignoreIfContains = [
			'\\Users\\Public\\',
		]

		SHGFP_TYPE_CURRENT = 0   # Get current, not default value
		directories = list(range(256))
		validDirectories = []

		# iterate through a large chunk of potential user folders, and filter them down using the above lists.
		for suffix in suffixsOfInterest:
			for CSIDL_PERSONAL in directories:
				buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
				ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
				if buf.value.endswith( suffix ) and len([ e for e in ignoreIfContains if e in buf.value ]) == 0 and buf.value not in validDirectories:
					validDirectories.append( buf.value )

		GeoPixPaths = [
			self.DefaultUserSavePath.replace('/','\\'),
			self.DefaultUserPrefabPath.replace('/','\\'),
		]
		return GeoPixPaths+validDirectories


	def ViewCurrentDirectoryInExplorer(self):
		'''
		opens the currently viewed directory in the file tool, in windows explorer.
		parent.masterParent.ViewCurrentDirectoryInExplorer() to use.
		'''
		pathParam = self.get_current_path_param()
		pathStr = pathParam.eval()

		PathInfo = tdu.PathInfo( pathStr )
		if PathInfo.exists == True:
			absPath = PathInfo.absPath
			ui.viewFile(absPath)
		return


	def BookmarkCurrentDirectory(self):
		'''
		this function gets the current directory in the path field, and then fetches
		the file_tool_bookmarks from disk using the global helper function called Load_Pref.
		if that function returns None, it means the user had no stored bookmarks, so we begin with an empty list.
		The path is added to that list if it is not already present, then that list is stored back to disk.
		'''
		pathParam = self.get_current_path_param()
		pathStr = pathParam.eval()
		PathInfo = tdu.PathInfo(pathStr)
		pathStr = PathInfo.absPath.replace('\\','/')

		if PathInfo.exists == True:
			
			file_tool_bookmarks = mod.globalFuncs.Load_Pref('file_tool_bookmarks')
			if file_tool_bookmarks == None:
				file_tool_bookmarks = []

			if pathStr not in file_tool_bookmarks:
				file_tool_bookmarks.append( pathStr )

			mod.globalFuncs.Save_Pref('file_tool_bookmarks',file_tool_bookmarks)
		return


	def UnbookmarkGivenDirectory( self , directoryStr ):
		'''
		this function fetches the bookmarks from disk, removes the item from the list
		if it exists, and stores that list back to disk. Meant to be the opposite
		function to the one above "BookmarkCurrentDirectory"
		'''
		directoryStr = directoryStr.replace('\\','/')

		file_tool_bookmarks = mod.globalFuncs.Load_Pref( "file_tool_bookmarks" )

		if file_tool_bookmarks == None:
			file_tool_bookmarks = []
		file_tool_bookmarks = [ x for x in file_tool_bookmarks if x != directoryStr ]
		mod.globalFuncs.Save_Pref( 'file_tool_bookmarks' , file_tool_bookmarks )
		return


	def SetPath(self, pathString, storeToQue=True):
		'''
		pathString can be either to a file or a folder.
		TODO: if to a folder, we simply go to that folder. If to a file,
		TODO: we go to the containing folder and highlight the file using lister magics.
		TODO: setup file double clicking functionality.
		''' 

		retrievedPar = self.get_current_path_param()

		# newPath = pathString if appendToCurrent == False else retrievedPar.eval() + '/' + pathString
		newPath = pathString
		newPathInfo = tdu.PathInfo( newPath )

		if newPathInfo.exists == True:
			if newPathInfo.isDir == True:
				self.set_name_field('')
				newPath = newPath.replace('\\','/')

				# handle updating the undo que if True.
				if storeToQue == True:
					self.store_directory_to_back_que( retrievedPar.eval() )
					self.clear_forward_que()

				setattr( retrievedPar , 'val' , newPath )

			else:
				# op.NOTIFV2.Notify('Cannot enter a file, however we should create a hook here to do context base file actions like save, load, etc...')
				pass
		else:
			op.NOTIFV2.Notify('Something went wrong.. that file or folder is invalid. try refreshing the list.')
		return


	def SetNameField(self, nameStr):
		'''
		Sets the name field to the given name string.
		'''
		# op('Body/bot/fieldString_FileFolderName').par.Value0 = nameStr
		self.ownerComp.par.Filename = nameStr
		return


	def IncrementNameField(self, step=1):
		'''
		This function handles incrementing and decrementing the file name, that is in the name field of the UI.
		It's intended to be called from the Plus/Minus icon buttons to the right of the field, but can be called from anywhere.
		A few logical if /elif blocks catch various states of strings, such as one with no number or one with a number already etc.
		if detected value between the last two dots is not a valid integer, then a new version integer gets inserted just before
		the extension.

		If no extension is present, this function will tell us that is the case, and not do anything. This is the first if block.
		'''
		# currentName = op('Body/bot/fieldString_FileFolderName').par.Value0.eval()
		currentName = self.ownerComp.par.Filename.eval()
		dotCount = currentName.count('.')

		if dotCount == 0:
			debug('trying to increment a file with no extension... is this right?')
		
		elif dotCount == 1:
			newNumber = step
			if newNumber > 0:
				currentName = currentName.replace('.','.%i.'%(newNumber))
			else:
				pass
		
		elif dotCount == 2:
			splitName = currentName.split('.')
			if self.is_string_integer( splitName[1] ):
				newNumber = int(splitName[1]) + step
				if newNumber > 0:
					splitName[1] = str(newNumber)
					currentName = '.'.join( splitName )
				else:
					currentName = splitName[0]+'.'+splitName[2]
			else:
				fromStr = '.%s'%( splitName[-1] )
				toStr = '.%i.%s'%( step,splitName[-1] )
				currentName = currentName.replace(fromStr,toStr)
		
		elif dotCount > 2:
			splitName = currentName.split('.')
			if self.is_string_integer( splitName[-2] ):
				newNumber = int(splitName[-2]) + step
				if newNumber > 0:
					splitName[-2] = str(newNumber)
					currentName = '.'.join( splitName )
			else:
				fromStr = '.%s'%( splitName[-1] )
				toStr = '.%i.%s'%( step,splitName[-1] )
				currentName = currentName.replace(fromStr,toStr)


		# op('Body/bot/fieldString_FileFolderName').par.Value0 = currentName
		self.ownerComp.par.Filename = currentName

		return


	def UpDirectory(self):
		'''
		Takes the user up 1 single directory within the mode context that is active (ie load, save, import etc)
		'''
		retrievedPar = self.get_current_path_param()
		absPath = retrievedPar.eval()
		newPathInfo = tdu.PathInfo( absPath )

		if newPathInfo.exists:
			self.SetPath( newPathInfo.dir )
		else:
			op.NOTIFV2.Notify('Something went wrong.. <%s> is not a valid path...'%(absPath))
		return


	def RefreshDirectory(self):
		'''
		forces the folder DAT and then the lister to refresh their contents.
		'''
		op('Body/center/folder_file_sys').par.refreshpulse.pulse()
		op('Body/center/list').par.Refresh.pulse()
		return


	def ForwardDirectory(self):
		'''
		this function is called by the UI forward button and whatever else needs it.
		It essentially looks to the redo que, and attempts to get the latest directory in the list.
		if it succeeds (list was not empty) it sets the current path to that, and appends it to the back que.
		''' 
		retrievedPar = self.get_current_path_param()

		try:
			lastDir = self.ForwardQue.pop()
			self.SetPath(lastDir, storeToQue=False)
			self.BackQue.append(lastDir)
		except IndexError as e:
			# debug('End of forward que.')
			pass
		return


	def BackDirectory(self):
		'''
		this function is called by the UI back button and whatever else needs it.
		It essentially looks to the undo que, and attempts to get the latest directory in the list.
		if it succeeds (list was not empty) it sets the current path to that, and appends it to the forward que.

		one small edge case to note, the if statement "if len(self.ForwardQue) == 0:" is designed to capture
		the current directory IF the user is "current" meaning if they are navigating around the file system
		they are "current" and whatever the current directory is, should be logged IF they begin pressing back.

		It relies on the forward que being empty as determination if the user is current or not.
		''' 
		retrievedPar = self.get_current_path_param()

		try:
			buff = []
			if len(self.ForwardQue) == 0:
				buff.append( retrievedPar.eval() )

			lastDir = self.BackQue.pop()
			buff.append( lastDir )
			self.ForwardQue.extend(buff)

			self.SetPath(lastDir, storeToQue=False)
			
		except IndexError as e:
			# debug('End of back que.')
			pass
		return


	def NewDirectoryPrompt(self):
		'''
		Sets the New Folder Dialogue parameter on the masterParent to True, making a container referencing
		it visible. That container contains a simple UI for creating a new folder, and clicking on Create
		will call another function here called "NewDirectory()"
		'''
		self.ownerComp.par.Newfolderdialogue = True
		return

	
	def NewDirectory(self, nameStr):
		'''
		attempts to create an new directory at the current directory, and tries to use the provided name.
		If the name already exists, a similar numbered folder will be created.
		'''
		existingItems = self.get_base_names_from_current_dir()
		newNameStr = mod.globalFuncs.uniquifyString( nameStr , existingItems )

		retrievedPar = self.get_current_path_param()
		pathStr = retrievedPar.eval()

		fullPath = os.path.join( pathStr , newNameStr ).replace('/','\\')
		os.mkdir(fullPath)

		self.RefreshDirectory()

		self.ownerComp.par.Newfolderdialogue = False
		return


	####################################################################################################
	############### MASTER FUNCTIONS - these are the primary driving functions of this module ##########
	####################################################################################################


	def SAVE(self):
		'''
		Wrapper for entire system wide save command
		'''

		if op('null_mode')['ObjectEditMode'] == 0:
			MsgStr = 'You are not in Object Mode. Please leave Hull or Pix mode, and try again.'
			op.NOTIFV2.Notify(MsgStr)
			return

		retrievedPar = self.get_current_path_param()
		fullSavePath = os.path.join(retrievedPar.eval(), self.ownerComp.par.Filename.eval() )
		fullSavePath = fullSavePath.replace('\\','/')
		PathInfo = tdu.PathInfo( fullSavePath )

		# early exit if the path provided is not valid and tell the user to try again.
		if tdu.PathInfo( PathInfo.dir ).exists == False or PathInfo.ext != '.gp':
			MsgStr = '%s is not a valid gp file, please refresh and enter a valid file name like FileName.gp'%(fullSavePath.replace('\\','/'))
			op.NOTIFV2.Notify(MsgStr)
			return

		# td operators that have .Save() extension functions.
		save_load_dat = op('null_saveload_items')
		
		# for now, just a place to visualize the save data.
		save_load = op('save_load')
		
		# save dict.
		SAVE_DATA = {}

		# for saveOperator in save_load_dat.rows():
		for i in range(1,save_load_dat.numRows):

			root_op = eval(save_load_dat[ i , 'root_op' ].val)
			include_self = save_load_dat[ i , 'include_self' ].val
			find_children_expression = save_load_dat[ i , 'find_children_expression' ].val
			find_children_expression_secondary = save_load_dat[ i , 'find_children_expression_secondary' ].val
			sub_operators = save_load_dat[ i , 'sub_operators' ].val
			extra_page_names = save_load_dat[ i , 'extra_page_names' ].val
			ignore_defaults = save_load_dat[ i , 'ignore_defaults' ].val
			extra_parameter_attributes = save_load_dat[ i , 'extra_parameter_attributes' ].val
			panel_values = save_load_dat[ i , 'panel_values' ].val

			# only attempt to load if the target module has save/load capabilities..
			# if it doesn't we don't want to halt the entire process, just proceed as possible and notify.
			if hasattr( root_op , 'SaveLoad_GET' ):

				# call GET the save data.
				op_save_data = root_op.SaveLoad_GET( 
					root_op , 
					include_self , 
					find_children_expression , 
					sub_operators , 
					extra_page_names , 
					extra_parameter_attributes , 
					ignore_defaults , 
					find_children_expression_secondary ,
					panel_values )

				# put the objects save data into the master dict.
				SAVE_DATA.update( op_save_data )

			else:
				debug( root_op, ' has no save Save/Load extension attached.. please fix.' )


		# dump the save data to table.
		save_load.text = json.dumps(SAVE_DATA, indent=4, sort_keys=True)


		save_load.save( fullSavePath )
		self.RefreshDirectory()

		op.software.par.Lastsavepath = fullSavePath

		self.Close()

		if self.exitAfterSave == True:
			project.quit(force=True)

		return

	def LOAD_FROM_PROJECTS(self, projectName):

		fullPath = os.path.join( project.folder ,  'LIBRARY/PROJECTS' ).replace('\\','/')
		fullPathInfo = tdu.PathInfo( fullPath )
		if not fullPathInfo.exists:
			MsgStr = fullPath + ' does not exist in the filesystem.. cannot load sample project.'
			op.NOTIFV2.Notify(MsgStr)

		fullFilePathInfo = tdu.PathInfo( fullPath+'/'+projectName+'_' )
		if not fullFilePathInfo.exists:
			MsgStr = projectName + ' does not exist in the LIBRARY/PROJECTS directory,.. cannot load project.'
			op.NOTIFV2.Notify(MsgStr)


		self.ownerComp.par.Loadpath = fullPathInfo.absPath
		self.ownerComp.par.Filename = projectName

		self.LOAD()


		return

	def LOAD(self, resetFirst=True ):

		'''
		Wrapper for entire system wide load command
		'''

		# debug('Begin Loading')

		if op('null_mode')['ObjectEditMode'] == 0:
			MsgStr = 'You are not in Object Mode. Please leave Hull or Pix mode, and try again.'
			op.NOTIFV2.Notify(MsgStr)
			return

		retrievedPar = self.get_current_path_param()
		fullLoadPath = os.path.join(retrievedPar.eval(), self.ownerComp.par.Filename.eval() )
		PathInfo = tdu.PathInfo( fullLoadPath )

		
		# early exit if the path provided is not valid and tell the user to try again.
		if PathInfo.exists == False or PathInfo.isDir or PathInfo.ext != '.gp':
			MsgStr = '%s is not a valid gp file, please refresh and choose one from the list first.'%(fullLoadPath.replace('\\','/'))
			op.NOTIFV2.Notify(MsgStr)
			return

		# wipe everything first if this is a load operation.
		if resetFirst == True:
			op.software.mod.GeoPix.RESET_GEOPIX( ignoreList=['Fullscreen','SAVE_LOAD'] )
			isImport = False
		else:
			isImport = True

		# td operators that have .Load() extension functions.
		save_load_dat = op('null_saveload_items')

		with open(fullLoadPath) as f:
			LOAD_DATA = json.load(f)

		# for saveOperator in save_load_dat.rows():
		for i in range(1,save_load_dat.numRows):

			# get a reference to the actual operator.
			root_op = eval(save_load_dat[ i , 'root_op' ].val)

			# get a reference to the actual operator.
			exact_match = eval(save_load_dat[ i , 'exact_match' ].val)

			if exact_match == 'expr':
				found_children = eval(save_load_dat[ i , 'find_children_expression' ].val)
			else:
				found_children = []
			
			# only attempt to load if the target module has save/load capabilities..
			# if it doesn't we don't want to halt the entire process, just proceed as possible and notify.
			if hasattr( root_op , 'SaveLoad_GET' ):

				# call SET the save data.
				op_save_data = root_op.SaveLoad_SET(LOAD_DATA , exact_match , isImport=isImport , foundChildren=found_children )

			else:
				debug( root_op, ' has no save Save/Load extension attached.. please fix.' )
		
		# update the last save path with the file just loaded.
		op.software.par.Lastsavepath = fullLoadPath.replace('\\','/')


		# handle pbr repacking after load:
		op.PbrPacker.DelayedRepack()

		# handle play/pause initializing.
		playbuttonKey = "/software/top/Time/rightPlayBarButtons/UberGui_GfxButton_Play/Gui/label"
		if playbuttonKey in LOAD_DATA.keys():
			PlayButtonState = bool(LOAD_DATA[playbuttonKey]['.panel.state'])
			if PlayButtonState == True:
				op.IOV2.StopAllMacros()
				op.Time.op('delayed_play').run(delayFrames=100)
			elif PlayButtonState == False:
				op.Time.op('delayed_pause').run(delayFrames=100)

		# handle updating group assignments in perform, after load.
		op.PerformV2.UpdateAllGroupAssignments()

		op.SamplerV2.op('Build_Fixture_Params_Buffer').cook(force=True, recurse=True)

		self.Close()

		# debug('End Loading')

		return



	def IMPORT(self):

		'''
		Wrapper for entire system wide import command.
		import is basically like load, but it doesn't delete things first.
		'''

		self.LOAD( resetFirst=False )


	def SET(self):

		CurrentMode = self.ownerComp.par.Mode.eval()
		targetOperators = self.targetOperators
		parameterName = self.parameterName
		Extension = self.ownerComp.par.Extension

		retrievedPar = self.get_current_path_param()
		fullLoadPath = os.path.join(retrievedPar.eval(), self.ownerComp.par.Filename.eval() )

		# print( fullLoadPath )
		PathInfo = tdu.PathInfo( fullLoadPath )

		EarlyExitTests = [
			PathInfo.exists == False,
			PathInfo.isDir if CurrentMode == 'choosefile' else PathInfo.isFile,
		]

		testResult = min( EarlyExitTests )

		# early exit if the path provided is not valid and tell the user to try again.
		if testResult == True:
			MsgStr = '%s is not a valid selection, please refresh and choose one from the list first.'%( fullLoadPath.replace('\\','/'))
			op.NOTIFV2.Notify(MsgStr)
			return

		if Extension != '':
			if not fullLoadPath.endswith( '.'+Extension ):
				MsgStr = '%s does not have the correct file extension. It should be < .%s > for this file type.'%( fullLoadPath.replace('\\','/') , Extension )
				op.NOTIFV2.Notify(MsgStr)
				return

		targetOperators = [ op(x) for x in targetOperators if op(x) != None ]
		targetOperators = [ x for x in targetOperators if hasattr( x.par , parameterName ) ]

		for each in targetOperators:
			p = getattr( each.par , parameterName )
			p.val = tdu.collapsePath( fullLoadPath ).replace('\\','/')

		self.Close()

		return