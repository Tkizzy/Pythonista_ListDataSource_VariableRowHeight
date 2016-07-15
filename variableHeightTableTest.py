data = '''\
QlpoOTFBWSZTWdDR4kUAATTfgFUQUGd/8D/AFYq/757aQAG93S7pOEooajE9TTEAAADQAA
PUGptSZBppAGQAA0AAABiJEANAhg0MQAmhpgASSamRpoU/UjQGgAAAGRoIgsEhgR0UD9/q
OOxZZAHptOJ2CMS0AFGCAMBJiCRSKVMEFgYIOWfz24dgGL8QGXchgCCEO+21Eg0ryeXwqA
tT0UAlaALCLWQSUMEIMZwHOD7p3EkWTISpkaEIgZxNIagMEJMj2NMK5MCkigDM0bFxsmlS
DkihAGSMkPPRfs0kBUjCkZJA5HnQ4vlaGmJkD2za3LjNiSTVElLHypMkM5ZK0QSmFunQFg
gy1Hn5am4OMiJgRaphyZKNuzYRJMvZWM6Aweg2s+CFryXerwqGu9EPskDjrSGJFgmQBBS+
kIO6uSqnyVUeHlVfzCWBrX55Hhh8imBStejI1Rjh91cmcFm02SGewNVK6Qii2ylMEbVBiS
vkUBoyzjXhPEKbBiDXBgSWAPkVMoLdmrkUiYoqtypALJFTNkWYGdWmZRnUWyXUB2L5mlvY
ZKMvkli6GjRwHFvYu5IpwoSGho8SKA==
'''
import bz2
from base64 import b64decode
pyui = bz2.decompress(b64decode(data))

import ui, random, os
from objc_util import *
import sys, objc_util, ctypes
import swizzle
import dialogs

groupIDPath=str(ObjCClass('NSFileManager').defaultManager().containerURLForSecurityApplicationGroupIdentifier_('group.pythonista').path())


class showDetailedEntryView(ui.View):
	def __init__(self,*args,**kwargs):
		print("]]]> showDetailedEntryView INSTANTIATED!!!!")
		
		self.arguments = kwargs
		self.posArgs = args
		
		#self.view = ui.load_view("../../Documents/aaaFiveStarsProduction/destinyListDetailView.pyui")
		#self.view = ui.load_view("/private/var/mobile/Containers/Shared/AppGroup/"+os.path.abspath(__file__)[47:83]+"/Documents/aaaFiveStarsProduction/destinyListDetailView.pyui")
		#self.view = ui.load_view(groupIDPath+"/Documents/aaaFiveStarsProduction/destinyListDetailView.pyui")
		self.view = ui.load_view_str(pyui.decode('utf-8'))
		self.tableView = self.view["tableViewDetail"]
		self.tableView.row_height = 70
		self.view.present('fullscreen')#,hide_title_bar=True)
		self.view.name = 'DetailedView' #'ShowTableView'
		
		#self.data = self.getDataSource()
		
		self.tableView.data_source = self.tableView.delegate = self.getDataSource()
		self.dataList.number_of_lines = 10
		self.tableView.action = self.evenMoreDetailAction
		
		self.heightSetup()
		self.tableView.reload_data()
		self.setup_tableview_swizzle(1)
		
		self.tableView.reload_data()
		#self.loggingLayer = localLogger()
		#self.dataLayer = DataLayer()
		#self.destinationInitiator()
		#self.refreshTableView()		

		
	def getDataSource(self):

		argLength = len(self.arguments)	

		dataSourceList = []
		
		if argLength > 0:
			for each in self.arguments:
				dataString = "{}: {}".format(each,self.arguments[each])
				dataSourceList.append(dataString)
				
			self.dataList = ui.ListDataSource(dataSourceList)
		
		elif len(self.posArgs) > 0:
			if len(self.posArgs) == 1:
				self.posArg = self.posArgs[0]
				print(type(self.posArg))
				if type(self.posArg) == type({"":""}): #if single dict as pos arg
					print("dict!")
					keys = self.posArg.keys()
					for key in keys:
						dataString = "{}: {}".format(key,self.posArg[key])
						dataSourceList.append(dataString)
						
					self.dataList = ui.ListDataSource(dataSourceList)
		
		else:
			self.dataList = ui.ListDataSource([str(argLength),"","...empty."])
		
		self.dataList.action = self.evenMoreDetailAction
		
		return self.dataList
		
	@ui.in_background
	def evenMoreDetailAction(self,sender):
		info = sender.items[sender.selected_row]
		console.alert(info)
		
			
		pass
		
	
	heights = [random.randrange(11,72) for x in range(100)]
	
	def tableview_height_for_section_row(self,tv,section,row):
		#heights=[random.randrange(11,72) for x in range(100)]
		dialogs.hud_alert(str(row))
		
		return self.heights[row]
		
	def heightSetup(self):
		#can i add other tv delegate methods in this way???? ask jonb...
		
		self.dataList.tableview_height_for_section_row = self.tableview_height_for_section_row
		
		
		
	def setup_tableview_swizzle(self,override=False):
		#it doesn't seem to matter whether we set this to our tableview, or to a new tableviewinstance....
		#t=ui.TableView()
		t = self.tableView
		#t = ui.TableView()
		t_o=ObjCInstance(t)
	
		encoding=ObjCInstanceMethod(t_o,'rowHeight').encoding[0:1]+b'@:@@'
		if hasattr(t_o,'tableView_heightForRowAtIndexPath_') and not override:
			return
		swizzle.swizzle(ObjCClass(t_o._get_objc_classname()),
									('tableView:heightForRowAtIndexPath:'),
									self.tableView_heightForRowAtIndexPath_,encoding)
									
	
	
	@on_main_thread
	def tableView_heightForRowAtIndexPath_(self,_self,_sel,tv,path):
		try:
			#import sys, objc_util, ctypes
			# For some reason, tv returns a NSNumber.  But, our tableview is in _self
			tv_o=objc_util.ObjCInstance(_self)
			# get row and section from the path
			indexPath=objc_util.ObjCInstance(path)
			row=indexPath.row()
			section=indexPath.section()
			# get the pyObject.  get as an opaque pointer, then cast to py_object and deref 
			pyo=tv_o.pyObject(restype=ctypes.c_void_p,argtypes=[])
			tv_py=ctypes.cast(pyo.value,ctypes.py_object).value
			# if the delegate has the right method, call it
			if tv_py.delegate and hasattr(tv_py.delegate,'tableview_height_for_section_row'):
				return tv_py.delegate.tableview_height_for_section_row(tv_py,section,row)
			else:
				return tv_py.row_height
		except Exception as e:
			print(e)
			return 44
									
									
	#end class



if __name__=="__main__":
	x = showDetailedEntryView(title1="haha",title2="hehehe",title3 = "Another thing...how will we add all this?",title4="whoa man, how many entries are we even going to do????")
