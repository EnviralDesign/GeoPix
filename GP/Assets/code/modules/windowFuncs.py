from __future__ import print_function
import ctypes
from ctypes import wintypes
from collections import namedtuple
import os
import inspect
import json

MONITORS_TD = op('MONITORS_TD')

############## BEGIN DEFINITION OF CTYPES THINGS ##################

user32 = ctypes.WinDLL('user32', use_last_error=True)

def check_zero(result, func, args):    
	if not result:
		err = ctypes.get_last_error()
		if err:
			raise ctypes.WinError(err)
	return args

if not hasattr(wintypes, 'LPDWORD'): # PY2
	wintypes.LPDWORD = ctypes.POINTER(wintypes.DWORD)

WindowInfo = namedtuple('WindowInfo', 'pid title')

WNDENUMPROC = ctypes.WINFUNCTYPE(
	wintypes.BOOL,
	wintypes.HWND,    # _In_ hWnd
	wintypes.LPARAM,) # _In_ lParam

user32.EnumWindows.errcheck = check_zero
user32.EnumWindows.argtypes = (
	WNDENUMPROC,      # _In_ lpEnumFunc
	wintypes.LPARAM,) # _In_ lParam

user32.IsWindowVisible.argtypes = (
	wintypes.HWND,) # _In_ hWnd

user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetWindowThreadProcessId.argtypes = (
  wintypes.HWND,     # _In_      hWnd
  wintypes.LPDWORD,) # _Out_opt_ lpdwProcessId

user32.GetWindowTextLengthW.errcheck = check_zero
user32.GetWindowTextLengthW.argtypes = (
   wintypes.HWND,) # _In_ hWnd

user32.GetWindowTextW.errcheck = check_zero
user32.GetWindowTextW.argtypes = (
	wintypes.HWND,   # _In_  hWnd
	wintypes.LPWSTR, # _Out_ lpString
	ctypes.c_int,)   # _In_  nMaxCount


class get_wnd_rect(ctypes.Structure):
	_fields_ = [('L', ctypes.c_int),
				('T', ctypes.c_int),
				('R', ctypes.c_int),
				('B', ctypes.c_int)]
rect = get_wnd_rect()


class RECT(ctypes.Structure):
	_fields_ = [
		('left', ctypes.c_int),
		('top', ctypes.c_int),
		('right', ctypes.c_int),
		('bottom', ctypes.c_int)
		]
	def dump(self):
		return map(int, (self.left, self.top, self.right, self.bottom))

class MONITORINFO(ctypes.Structure):
	_fields_ = [
		('cbSize', ctypes.c_int),
		('rcMonitor', RECT),
		('rcWork', RECT),
		('dwFlags', ctypes.c_int)
	]

############## END DEFINITION OF CTYPES THINGS ##################


def list_pid_groups():
	'''
	returns a dict of lists, each item of the dict, is a PID group. 
	a pid group, is essentially all the windows that belong to certain process ID (pid)
	'''
	result = []
	result2 = []
	@WNDENUMPROC
	def enum_proc(hWnd, lParam):
		if user32.IsWindowVisible(hWnd):
			pid = wintypes.DWORD()
			tid = user32.GetWindowThreadProcessId(
						hWnd, ctypes.byref(pid))
			length = user32.GetWindowTextLengthW(hWnd) + 1
			title = ctypes.create_unicode_buffer(length)
			user32.GetWindowTextW(hWnd, title, length)
			result.append(WindowInfo(pid.value , title.value))
			result2.append(hWnd)
		return True
	user32.EnumWindows(enum_proc, 0)

	resultDict = {}
	for i in range(len(result)):
		pidList = resultDict.get( result[i][0], [] )
		pidList += [ {'title':result[i][1], 'hWnd':result2[i]} ]
		resultDict[result[i][0]] = pidList
	return resultDict


def get_geopix_pid():
	'''
	returns the pid (windows process ID) of THIS running TouchDesigner instance.
	'''
	return os.getpid()

def get_geopix_pidGroup():
	pid = get_geopix_pid()
	pidGrps = list_pid_groups()
	GeoPixPidGrp = pidGrps.get(pid,[])

	return GeoPixPidGrp

	

def get_geopix_hWnd( pid ):
	'''
	returns the best match, for the window handle ID, for GeoPix. this should be run when GeoPix first launches
	and there are no other floating windows open.. this in theory means we will gaurantee the right window handle, and 
	if that number doens't change for the duration of GeoPix running, that means we can rely on it for handling windows resizing
	operations and such.
	'''
	pidGrps = list_pid_groups()
	GeoPixPidGrp = pidGrps.get(pid,[])
	assert len(GeoPixPidGrp) > 0, 'GeoPix PID group has length 0, this should not happen...'

	if len(GeoPixPidGrp) > 1:
		matchingPidEntries = [ each for each in GeoPixPidGrp if 'GeoPix' in each['title'] ]
	elif len(GeoPixPidGrp) == 1:
		matchingPidEntries = GeoPixPidGrp
	else:
		matchingPidEntries = []

	assert len(matchingPidEntries) == 1, 'matchingPidEntries should be exactly 1 in length, our filter isnt specific enough.'

	return matchingPidEntries[0]['hWnd']

def get_activeWindow_hWnd():
	'''
	this returns the windows handle ID for the window that's currently in the forground. this USUALLY would be something you just clicked on,
	but it's possible that this would not always return reliable results I think? so use this for things where the last clicked window matters.
	'''
	return ctypes.windll.user32.GetForegroundWindow()



def Window_GetAttributes( hWnd ):
	'''
	given a window handle ID, this function returns the left/right/top/bottom edge in abs pixel coords.
	'''
	# print(hWnd)
	DWMWA_EXTENDED_FRAME_BOUNDS = 9
	ctypes.windll.dwmapi.DwmGetWindowAttribute(
		wintypes.HWND(hWnd),
		wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
		ctypes.byref(rect),
		ctypes.sizeof(rect)
	)
	d = {'L':rect.L,'T':rect.T,'R':rect.R,'B':rect.B,}
	return d

def getMonitorInfoAsJson():
	# return json.dumps( getMonitorInfo(), indent=4 )
	return json.dumps(getMonitorInfo())

	

def getMonitorInfo():
	""" 
	Returns info about the attached monitors, in device order
	"""
	MONITORS_TD.cook(force=1)
	primaryMonitorHeight = [0]
	monitors = []
	CCHDEVICENAME = 32
	def _MonitorEnumProcCallback(hMonitor, hdcMonitor, lprcMonitor, dwData):
		class MONITORINFOEX(ctypes.Structure):
			_fields_ = [("cbSize", ctypes.wintypes.DWORD),
						("rcMonitor", ctypes.wintypes.RECT),
						("rcWork", ctypes.wintypes.RECT),
						("dwFlags", ctypes.wintypes.DWORD),
						("szDevice", ctypes.wintypes.WCHAR*CCHDEVICENAME)]
		lpmi = MONITORINFOEX()
		lpmi.cbSize = ctypes.sizeof(MONITORINFOEX)
		user32.GetMonitorInfoW(hMonitor, ctypes.byref(lpmi))

		if int(lpmi.dwFlags) == 1:
			primaryMonitorHeight.append(lpmi.rcMonitor.bottom - lpmi.rcMonitor.top)
		monitors.append({
			"name": lpmi.szDevice,
			"index": int(MONITORS_TD[str(lpmi.szDevice),'index']),
			"monitorHandle": hMonitor,
			"primary": lpmi.dwFlags,

			"monitorArea_left": lpmi.rcMonitor.left,
			"monitorArea_right": lpmi.rcMonitor.right,
			"monitorArea_bottom": lpmi.rcMonitor.bottom,
			"monitorArea_top": lpmi.rcMonitor.top,
			"monitorArea_width": lpmi.rcMonitor.right-lpmi.rcMonitor.left,
			"monitorArea_height": lpmi.rcMonitor.bottom-lpmi.rcMonitor.top,

			"workArea_left": lpmi.rcWork.left,
			"workArea_right": lpmi.rcWork.right,
			"workArea_bottom": lpmi.rcWork.bottom,
			"workArea_top": lpmi.rcWork.top,
			"workArea_width": lpmi.rcWork.right-lpmi.rcWork.left,
			"workArea_height": lpmi.rcWork.bottom-lpmi.rcWork.top,
			
			})

		return True
	MonitorEnumProc = ctypes.WINFUNCTYPE(
		ctypes.c_bool,
		ctypes.c_ulong,
		ctypes.c_ulong,
		ctypes.POINTER(ctypes.wintypes.RECT),
		ctypes.c_int)
	callback = MonitorEnumProc(_MonitorEnumProcCallback)
	if user32.EnumDisplayMonitors(0, 0, callback, 0) == 0:
		raise WindowsError("Unable to enumerate monitors")

	# primaryMonitorHeight = max(primaryMonitorHeight)
	for mon in monitors:

		# no longer need this since doing in TD
		# mon['monitorArea_bottom'] = primaryMonitorHeight - mon['monitorArea_bottom']
		# mon['monitorArea_top'] = primaryMonitorHeight - mon['monitorArea_top']
		# mon['workArea_bottom'] = primaryMonitorHeight - mon['workArea_bottom']
		# mon['workArea_top'] = primaryMonitorHeight - mon['workArea_top']

		# mon['monitorArea_top'] -= 1
		mon['monitorArea_right'] -= 1
		# mon['workArea_top'] -= 1
		mon['workArea_right'] -= 1

		pass

	return monitors

def Window_GetCanvasBounds( monitors ):
	'''
	similar to the monitor DAT's bounds toggle. this reports the bounds and size of the entire windows
	display canvas, canvas meaning the bounding box space of all monitors. 
	To use this, supply the result of monitor_areas() as an argument.
	'''
	monitorWidths = []
	monitorHeights = []
	# monitors = monitor_areas()

	left = min([ each['monitorArea_left'] for each in monitors ])
	right = max([ each['monitorArea_right'] for each in monitors ])
	top = max([ each['monitorArea_top'] for each in monitors ])
	bottom = min([ each['monitorArea_bottom'] for each in monitors ])

	width = right - left + 1
	height = top - bottom + 1

	return {'left':left,'right':right,'bottom':bottom,'top':top, 'width':width, 'height':height}


def Window_Minimize():
	'''
	Minimizes the window from wherever it is, to the taskbar.
	'''
	hWnd = op.software.par.Geopixhwnd.eval()
	minimizeID = 6
	ctypes.windll.user32.ShowWindow(hWnd, minimizeID)



def remap_vertical_component_to_td_style(monitorInfoDict):

	max1 = max([ mon['monitorArea_bottom'] for mon in monitorInfoDict ])
	min1 = min([ mon['monitorArea_top'] for mon in monitorInfoDict ])
	min2 = max1 - min1
	max2 = 0
	# print(min1,max1,min2,max2)

	for mon in monitorInfoDict:
		mon['monitorArea_bottom'] = int(tdu.remap( mon['monitorArea_bottom'] , min1 , max1 , min2 , max2 ))
		mon['monitorArea_top'] = int(tdu.remap( mon['monitorArea_top'] , min1 , max1 , min2 , max2 ))
		mon['workArea_bottom'] = int(tdu.remap( mon['workArea_bottom'] , min1 , max1 , min2 , max2 ))
		mon['workArea_top'] = int(tdu.remap( mon['workArea_top'] , min1 , max1 , min2 , max2 ))

	return monitorInfoDict



def remap_value_to_ctypes_style(monitorInfoDict,value):


	T = [ mon['monitorArea_top'] for mon in monitorInfoDict ]
	B = [ mon['monitorArea_bottom'] for mon in monitorInfoDict ]
	# print(T,B)

	min1 = 0
	max1 = max(B) - min(T)

	min2 = max(B)
	max2 = min(T)
	

	# debug(value,'-1',min1,max1,min2,max2)
	
	value = int(tdu.remap( value , min1 , max1 , min2 , max2 ))

	return value


def Window_Set_FullScreen(monitorID):
	'''
	"Maximizes" the main application window to take up the entire work area of the monitor provided by ID

	NOTE: there is currently a bug with setting a window COMP to full screen
	on non primary monitors, when there are different working resolutions between
	monitors. this function employs a hack, to force the window to not truly be fullscreen
	by setting the height to 1 less than the height of the monitor.
	'''

	monitors = getMonitorInfo()
	monitors = remap_vertical_component_to_td_style(monitors)

	# primaryMonitor = [ mon for mon in monitors if mon['primary'] == 1 ][0]
	# primaryMonitorMaxHeight = primaryMonitor['monitorArea_height'] - 1

	monitor = [ mon for mon in monitors if mon['index'] == monitorID ][0]

	L = monitor['workArea_left']
	R = monitor['workArea_right']
	T = monitor['workArea_top'] # reverse cause windows 0,0 is top left
	B = monitor['workArea_bottom'] # reverse cause windows 0,0 is top left

	W = monitor['workArea_width']
	H = monitor['workArea_height'] - 1 # the minus 1 is needed here, to work around some glitches when things go full screen on non uniform monitor arrays.
	# H = monitor['workArea_height']
	X = L
	Y = T


	monitors = getMonitorInfo()
	Y = remap_value_to_ctypes_style(monitors,Y)

	hWnd = op.software.par.Geopixhwnd.eval()

	ctypes.windll.user32.MoveWindow(
		hWnd, 
		X, 
		Y, 
		W, 
		H, 
		True
	)


def Window_Set_Windowed(monitorID):
	'''
	Sets the primary window to a windowed subset of the provided monitorID.
	It also fits the window to one of several common widescreen formats, such as 1080P, or 1280, etc.
	'''

	monitors = getMonitorInfo()
	monitors = remap_vertical_component_to_td_style(monitors)


	# monitor = [ mon for mon in monitors if mon['primary'] == 1 ][0]
	monitor = [ mon for mon in monitors if mon['index'] == monitorID ][0]

	L = monitor['workArea_left']
	R = monitor['workArea_right']
	T = monitor['workArea_top'] # reverse cause Windows considers 0,0 top left of monitor
	B = monitor['workArea_bottom'] # reverse cause Windows considers 0,0 top left of monitor

	W = monitor['workArea_width']
	H = monitor['workArea_height']
	X = L
	Y = T
	# Y = 0

	monitors = getMonitorInfo()
	Y = remap_value_to_ctypes_style(monitors,Y)

	ratio = 0.9
	H2 = H * ratio

	resolutions = [
		[720,480],
		[1280,720],
		[1920,1080],
	]

	i = sum( [ 1 for y in resolutions if H2 >= y[1] ] ) - 1
	chosenRes = resolutions[i]

	W2 = chosenRes[0]
	H2 = chosenRes[1]

	X2 = int(X) + int(round((W - W2) / 2))
	Y2 = int(Y) + int(round((H - H2) / 2))

	hWnd = op.software.par.Geopixhwnd.eval()

	ctypes.windll.user32.MoveWindow(
		hWnd, 
		X2, 
		Y2,
		W2, 
		H2-1, 
		True
	)


def Set_Window_From_Bounds(L,R,B,T):
	'''
	attempts to set the window's position and size from L/R/B/T bounds.
	'''

	W = R-L
	H = T-B
	X = L
	Y = T

	monitors = getMonitorInfo()
	Y = remap_value_to_ctypes_style(monitors,Y)

	hWnd = op.software.par.Geopixhwnd.eval()

	ctypes.windll.user32.MoveWindow(
		hWnd, 
		X, 
		Y,
		W, 
		H, 
		True
	)

	


def Window_Set_Spanned(monitorIDs):
	'''
	Sets the primary window to entirely cover the specified list of monitors by index.
	'''

	assert isinstance(monitorIDs,list), 'monitorIDs must be a list'
	assert len(monitorIDs) > 0, 'monitorIDs must be a list with length greater than 0'

	# monitors = monitor_areas()
	monitors = getMonitorInfo()
	monitors = remap_vertical_component_to_td_style(monitors)

	primaryMonitor = [ mon for mon in monitors if mon['primary'] == 1 ][0]
	primaryMonitorMaxHeight = primaryMonitor['monitorArea_height'] - 1

	# targetedMonitors = {k:v for k,v in monitors.items() if k in monitorIDs}
	targetedMonitors = [ mon for mon in monitors if mon['index'] in monitorIDs]

	L,R,T,B = [],[],[],[]
	for monitor in targetedMonitors:

		# monArea = monitor['monitorArea']

		L += [ monitor['monitorArea_left'] ]
		R += [ monitor['monitorArea_right'] ]
		T += [ primaryMonitorMaxHeight - monitor['monitorArea_top'] ] # reverse cause windows 0,0 is top left
		B += [ primaryMonitorMaxHeight - monitor['monitorArea_bottom'] ] # reverse cause windows 0,0 is top left

	W = max( R ) - min( L ) + 1
	H = max( B ) - min( T ) + 1
	X = min( L )
	Y = min( T )

	hWnd = op.software.par.Geopixhwnd.eval()

	ctypes.windll.user32.MoveWindow(
		hWnd, 
		X, 
		Y, 
		W, 
		H, 
		True
	)

def Window_Move_TitleBarToCursor():

	pidGroupsA = mod.windowFuncs.get_geopix_pidGroup()

	op('Delayed_TitleBarToCursor').run(pidGroupsA, delayFrames=1)


	return
