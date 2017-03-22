import kivy

#Setting the size of the Kivy windows
from kivy.config import Config  
Config.set('graphics','position','custom')
Config.set('graphics','left',80)
Config.set('graphics','top',100)
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '600')

from kivy.app import App

from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.core.window import Window

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox 
from kivy.uix.button import Button 
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.image import AsyncImage

from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

from kivyoav.delayed import delayable  #anim_gif

import os
import shutil

from send2trash import send2trash 

from kivy.lang import Builder

## 
class CustomCheckbox(CheckBox): #cf the .kv file   
	pass
	
class Loading_Image_KV(BoxLayout):#cf the .kv file
	pass
	
## To do list
# pbm with loading the table (which sometimes takes more than 15sec and having an animated gig meanwhile  cf 
# to be able to display the gif : import kivyoav +  @delayable + yield ( cf "anim_gif") +  http://stackoverflow.com/questions/42955019/kivy-returning-animated-gif-and-then-calling-another-def/42956376#42956376
	
	
	
class MyWidget(BoxLayout):

	##1 Global variables for MyWidget
	Filechooser_initial_path =StringProperty(os.path.expanduser('~')+r"\Desktop")
	dico_ref_folder_selected_ck = {}    # keep id of label displaying the folder in the table
	dico_ref_folder_selected_lbl = {}   # keep id of checkbox 
	popup_ref = {}                      # keep id of popup  
	
	# variable for conditions
	root_path=""
	conditions= []
	folder_list= []
	sup_inf= ""   
	unit ="" 
	extensions_list =[]
	

	##2 retrieve data from user
	@delayable  #anim_gif
	def selected(self, *args): 
		#0 filechooser.path, 1 filechooser.selection, 2 Ck_emptyfolder.active, 3 Ck_only_desktop_ini.active, 4 Ck_only_srt_txt.active,  
		#5 Txt_extension.text , 6 self.sup_inf.active  (true = < / false = >) , 7  Txt_size.text,   8 Kb.state, 9  Mb.state,  10 Gb.state

		self.conditions = [] 
		if len(args) == 2:
			for i in args[1]:
				self.conditions.append(i)
			self.conditions= tuple(self.conditions) 
			print("yes")
		else:
			for i in args:
				self.conditions.append(i)
			self.conditions= tuple(self.conditions)
		print("first",self.conditions)
		

		
		#remove the python add widget if there: 
		if len(self.children)>1:
			self.remove_widget(self.children[0])


		#store root variable (need when delete folder)
		self.root_path=self.conditions[0]
		print(self.root_path)
		
		# create extensions list to delete 
		self.extensions_list =[]
		if self.conditions[4]:
			self.extensions_list.extend([".srt", ".txt"])
		if self.conditions[5]:  # if  Txt_extension.text  is not empty then  
			list_of_ext= self.conditions[5].split(",")
			self.extensions_list.extend(list_of_ext)
		
		# prepare variable for size:
		self.sup_inf= ""
		if self.conditions[6]:
			self.sup_inf= "<"
		else:
			self.sup_inf= ">"


		
		self.unit =""
		if  self.conditions[8] == "down":
			self.unit = "Kb"
		elif self.conditions[9] == "down":
			self.unit = "Mb"
		elif self.conditions[10] == "down":
			self.unit = "Gb"


		# create folder list        
		self.folder_list= []
		for each in self.conditions[1]:
			if each == '..\\':
				each = self.root_path
			self.folder_list.append(each)
			
	##3 animated gif
		wait_image= Loading_Image_KV()
		self.add_widget(wait_image) 
		yield 0.01  #anim_gif
		 
		# Clock.schedule_once(lambda x: self.DisplayTable(self), 0)
		
	# def DisplayTable(self, instance):                    
			
	##4Create lists of folders needed for the table
		list_of_directory_to_delete_empty= []
		list_of_directory_to_delete_desktop_ini=[]
		list_of_directory_to_delete_extensions =[]
		list_of_directory_to_delete_size=[]    
		for each in self.folder_list:

			for dir, subdirs, files in os.walk(each):

				if subdirs == [] and files == []: # if no files and no folders 
					if self.conditions[2]:
						list_of_directory_to_delete_empty.append([dir,subdirs,files])
						
						
				elif subdirs == []:               # if contains only 1 file and no folder
					
					if self.conditions[3] and len(files) == 1:
						if files[0].endswith('.ini'):                # check if the file is .ini
							list_of_directory_to_delete_desktop_ini.append([dir,subdirs,files])
							
					if self.extensions_list : 
						contains_other_ext=0
						for file in files:
							if not file.endswith(tuple(self.extensions_list)):  
								contains_other_ext=True
						if contains_other_ext== 0:
							list_of_directory_to_delete_extensions.append([dir,subdirs,files]) 

				if self.conditions[7]:
					size = int(self.conditions[7])
					factor = 0
					if  self.unit == "Kb":
						factor = 10**3
					elif self.unit == "Mb":
						factor = 10**6
					elif self.unit == "Gb":
						factor = 10**9
					threshold = size * factor
					def get_tree_size(dir):

						"""Return total size of files in given path and subdirs."""
						total = 0
						for entry in os.scandir(dir):        # import os needed
							if entry.is_dir(follow_symlinks=False):
								total += get_tree_size(entry.path)
							else:
								total += entry.stat(follow_symlinks=False).st_size
						return total
					size_folder = get_tree_size(dir) 
					if self.sup_inf == "<":    # true = < / false = >
						if size_folder < threshold:
							list_of_directory_to_delete_size.append([dir,subdirs,files, size_folder])
					else:
						if size_folder > threshold:
							list_of_directory_to_delete_size.append([dir,subdirs,files, size_folder])


			
		list_of_directory_to_delete_empty_with_label= ["Empty directories"] + list_of_directory_to_delete_empty
		list_of_directory_to_delete_desktop_ini_with_label=["Folder with only desktop.ini"] +list_of_directory_to_delete_desktop_ini
		list_of_directory_to_delete_extensions_with_label =["Folder with only this extensions : " + str(self.extensions_list)] + list_of_directory_to_delete_extensions
		list_of_directory_to_delete_size_with_label= ["Folders size " + str(self.sup_inf) + " " + str(self.conditions[7]) + " " + str(self.unit)] + list_of_directory_to_delete_size

		lists_to_display = [list_of_directory_to_delete_empty_with_label, list_of_directory_to_delete_desktop_ini_with_label, list_of_directory_to_delete_extensions_with_label, list_of_directory_to_delete_size_with_label ]
		

		

	##5 Display the table 
		
		
		layout_all_list_and_b = GridLayout(cols=1,size_hint_y=0.9 )   
		layout_all_list_for_scroll = GridLayout(cols=1, padding = 20, size_hint_y=None)   
		layout_all_list_for_scroll.bind(minimum_height=layout_all_list_for_scroll.setter('height'))

		index = 0  # create index for key of dico path + checkbox kivy ID

		for list in lists_to_display: 
			title=Label(bold= True,font_size=20, text=list[0],size_hint_y=None, height=40)
			layout_all_list_for_scroll.add_widget(title)
			yield 0.000001 #anim_gif
			for folder in list[1:]: 
				yield 0.000001 #anim_gif
				layout_folder = GridLayout(cols=5, spacing= 15, size_hint_y=None, height=40 )

				path=Label(font_size=15, text=str(folder[0].replace(self.root_path, '...root...')), size_hint_x= None)
				self.dico_ref_folder_selected_lbl[str(index)] = path
				path.bind(texture_size=path.setter('size'))
				path.bind(size_hint_min_x=path.setter('width'))
				scroll_p = ScrollView(size_hint=(None, None), size=((Window.width-400)/5, 30))
				scroll_p.add_widget(path) 

				subfolder_text= str(folder[1])
				if len(subfolder_text)>100:
					subfolder_text= subfolder_text[0:100]+" (...)"
				subfolder=Label(font_size=15, text=subfolder_text, size_hint_x= None)  
				subfolder.bind(texture_size=subfolder.setter('size'))
				subfolder.bind(size_hint_min_x=subfolder.setter('width'))
				scroll_sf = ScrollView(size_hint=(None, None), size=((Window.width-400)/5, 30))
				scroll_sf .add_widget(subfolder)
	
				files_text= str(folder[2])
				if len(files_text)>100:
					files_text= files_text[0:100]+" (...)"
				files=Label(font_size=15, text=files_text,  size_hint_x= None)   
				files.bind(texture_size=files.setter('size'))
				files.bind(size_hint_min_x=files.setter('width'))
				scroll_f = ScrollView(size_hint=(None, None), size=((Window.width-400)/5, 30))
				scroll_f.add_widget(files)


				layout_folder.add_widget(scroll_p)                   
				layout_folder.add_widget(scroll_sf)   
				layout_folder.add_widget(scroll_f)                   
				
				if len(folder) == 4:
					size_bytes= folder[3]
					suffixes = ['B', 'KB', 'MB', 'GB']
					if size_bytes==0:
						size_human = "0 B"
					i = 0
					while size_bytes>=1024 and i < len(suffixes)-1:
						size_bytes /= 1024
						i += 1
					size_human = str(round(size_bytes,2))+" "+str(suffixes[i])

					sizes_label = Label(font_size=15, text=size_human) 
					layout_folder.add_widget(sizes_label)
				checkb= CustomCheckbox()	
	
				self.dico_ref_folder_selected_ck[str(index)] = checkb  # add ref checkbox for later retrieve 
				layout_folder.add_widget(checkb)
				layout_all_list_for_scroll.add_widget(layout_folder)
				index +=1
		
		scroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height*0.80))
		scroll.add_widget(layout_all_list_for_scroll)
		layout_all_list_and_b.add_widget(scroll)
		layout_buttons= BoxLayout(orientation="horizontal", spacing = 20)

		# add button delete select/all
		button_delete = Button(text="Delete", size_hint= (None, None), height= 40, width=60)
		button_delete.bind(on_press=self.confirmation_popup_before_delete)
		button_selectAll=Button(text="Select/Unselect All", size_hint= (None, None), height= 40, width=180)
		button_selectAll.bind(on_press=self.check_all_checkboxes)
		layout_buttons.add_widget(button_delete)
		layout_buttons.add_widget(button_selectAll)
		
		
		layout_all_list_and_b.add_widget(layout_buttons) 
		

		#remove the python add widget if there: 
		if len(self.children)>1:
			self.remove_widget(self.children[0])

		self.add_widget(layout_all_list_and_b)
		
		self.ids["filechooser"]._update_files()
		
		
	def check_all_checkboxes(self, *arg):
		state = True
		for idx, wgt in self.dico_ref_folder_selected_ck.items():
			if wgt.active == False:
					state = False
		if state == False:
			for idx, wgt in self.dico_ref_folder_selected_ck.items():
				wgt.active = True
		else:
			for idx, wgt in self.dico_ref_folder_selected_ck.items():
				wgt.active = False   
	
	def confirmation_popup_before_delete(self, *arg):
		list_folder_to_delete=[]
		for idx, wgt in self.dico_ref_folder_selected_ck.items():
			if wgt.active == True:
				folder_path = self.dico_ref_folder_selected_lbl.get(idx).text
				formated_folder_path = folder_path.replace('...root...', self.root_path)
				list_folder_to_delete.append(formated_folder_path)
		# print("1", list_folder_to_delete)
		list_folder_to_delete_sorted= list(set(list_folder_to_delete))
		list_folder_to_delete_sorted.sort()
		# print("2", list_folder_to_delete_sorted)
		
		
		
		# display in a boxlayout with 1 lable for each folder        
		layout_pop1  = GridLayout (cols=1, size_hint_y=0.9)        
		layout_pop_label  = GridLayout (cols=1, size_hint_y=None) 
		layout_pop_label.bind(minimum_height=layout_pop_label.setter('height'))
		
		for item in list_folder_to_delete_sorted:
			label_pop = Label(text=item, font_size=15, size_hint= (None, None), height= 30)
			label_pop.bind(texture_size=label_pop.setter('size'))
			label_pop.bind(size_hint_min_x=label_pop.setter('width'))
			scroll = ScrollView(size_hint=(None, None), size=(1000, 30))  
			scroll.add_widget(label_pop)
			layout_pop_label.add_widget(scroll)
		scroll2 = ScrollView(size_hint=(1, None), size=(1000, 400))  
		scroll2.add_widget(layout_pop_label)    
		layout_pop1.add_widget(scroll2)

	

		layout_button_pop=BoxLayout (orientation="horizontal")
		button1= Button(text="Delete", size_hint=(None, None), width = 150, height=40, on_press=lambda x: self.deletefolder(list_folder_to_delete_sorted))
		button2=Button(text="Cancel", size_hint=(None, None), width = 150, height=40, on_press=self.closepopup)
		layout_button_pop.add_widget(button1)
		layout_button_pop.add_widget(button2)
		layout_pop1.add_widget(layout_button_pop)
		popup = Popup(content=layout_pop1, auto_dismiss=False, background = 'atlas://data/images/defaulttheme/button_disabled')
		self.popup_ref["popup"] = popup
		popup.open()
	
	def closepopup(self, *arg): 
		self.popup_ref.get("popup").dismiss()
		
	def deletefolder(self, folders):
		for folder in folders:
			if os.path.isdir(folder):
				send2trash(folder)
		self.popup_ref.get("popup").dismiss() 
		# popup2 = Popup(content="Folders deleted", auto_dismiss=True, background = 'atlas://data/images/defaulttheme/button_disabled')
		# popup2.open()
		#update filechooser path
		self.ids["filechooser"]._update_files()
		print("conditions ", self.conditions)
		self.selected(self, self.conditions)
		
		
class MyApp(App):
	
	def build(self):

		Window.clearcolor = (0.863, 0.863, 0.863, 0.9)

		return MyWidget()
		

MyApp().run()


