def DelayedScript(execStr = '', OpSrc = None, frameDelay=1):
	
	if execStr and OpSrc:
		# print('doin it')
		newTextOp = OpSrc.create(textDAT, 'RUN_DELAYED_%i'%(frameDelay))
		execStr += '\n' + 'me.destroy()'
		newTextOp.text = execStr
		newTextOp.run(delayFrames = frameDelay)
		
		return True
	else:
		debug('Not executing delayed script, not all arguments were valid.')
		return False