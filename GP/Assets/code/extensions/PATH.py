

class PATH:
	"""
	These functions are sort of like op shortcuts, except provide more custom gatekeeping to how/where these paths come from since some of them
	May change through out runtime, specifically the IO_SCENE, which can point to root, or the internals of a macro, and maybe other stuff later.
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		

	def IO_BACKEND(self):
		return op.IOV2
		
	def IO_TEMPLATES(self):
		return op.IO_TEMPLATES_V3
		
	def IO_SCENE(self):
		return parent.IO.par.Scenegeocomp.eval()
	
	### this needs to be updated!
	def IO_TOOLS(self):
		debug('remove this eventually')
		#return op.IO_logic
		return None
	
	def IO_VIEWPORT(self):
		return op.IOV2.op('Graph')
	
	def IO_NOTIFICATIONS(self):
		return op.IO_notif_center
	
	def IO_RENDERPICK(self):
		return op.IOV2.op('Graph').par.Graphrenderpick.eval()
		
			
	def EDITOR_BACKEND(self):
		return op.sceneOutliner
		
	def IO_TIMING_CHOP(self):
		return op('customData/TIMING')
		
	def IO_STATS_CHOP(self):
		return op('customData/STATS')
		
		
		
	def UNDELETABLE_IO_NODES(self):
		return op.IOV2.par.Undeletablenodes.eval().split(' ')