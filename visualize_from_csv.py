from tkinter import *
from tkinter import ttk 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import threading
import time
from datetime import datetime,time,timedelta
from matplotlib.animation import FuncAnimation
import threading 
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import os
from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler


#Constant values
path = ''    #pls insert your directory that contain the CSV file
NO = 'NO.1'     # to display to user
cols = ['時間','昇温室ファン','浸炭室ファン', '降温室ファン', '昇温室ローラー','浸炭室ローラー1', '浸炭室ローラー2','浸炭室ローラー3', '降温室ローラー', '油槽エレベータチェン']


# set logging 
# insert directory for logging
logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.ERROR)
handler = TimedRotatingFileHandler('',
                                       when="H",
                                       interval=1,
                                       backupCount=10)


s_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(s_format)
logger.addHandler(handler)


#set df
file_path = str(sorted(Path(path).iterdir(), key=os.path.getmtime)[-1])
df = pd.read_csv(file_path,encoding="UTF-8",header=None, skiprows=13)
df.columns = cols
df = df.set_index('時間')

#get data
str_date = str(pd.to_datetime(df.index).date[0]).replace('-','/')
_time = pd.to_datetime(df.index).time       
_data1 = df['昇温室ファン']
_data2 = df['浸炭室ファン']
_data3 = df['降温室ファン']
_data4 = df['昇温室ローラー']
_data5 = df['浸炭室ローラー1']
_data6 = df['浸炭室ローラー2']
_data7 = df['浸炭室ローラー3']
_data8 = df['降温室ローラー']
_data9 = df['油槽エレベータチェン']

time_range = [(datetime(1,1,1) + timedelta(hours=i)).time() for i in range(24)]
patterns = ["*.csv","*.CSV"]                      
ignore_patterns = ""                                                            
ignore_directories = False                                                     
case_sensitive = True
my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)


def on_changed(event):
    global df
    global cols
    global first_modify
    global path
    global file_path
    global str_date
    global _time
    global _data1
    global _data2
    global _data3
    global _data4
    global _data5    
    global _data6
    global _data7
    global _data8    
    global _data9
    
    # we can add error handler because the first modify will cause an error >> df = pd.read_csv(path,encoding="UTF-8",usecols = cols)
    #this time i try another method logic to skip the first modify
    try:
        file_path = str(sorted(Path(path).iterdir(), key=os.path.getmtime)[-1])
        df = pd.read_csv(file_path,encoding="UTF-8",header=None, skiprows=13)
        df.columns = cols
        df = df.set_index('時間')
        
        str_date = str(pd.to_datetime(df.index).date[0]).replace('-','/')
        _time = pd.to_datetime(df.index ).time
        _data1 = df['昇温室ファン']
        _data2 = df['浸炭室ファン']
        _data3 = df['降温室ファン']
        _data4 = df['昇温室ローラー']
        _data5 = df['浸炭室ローラー1']
        _data6 = df['浸炭室ローラー2']
        _data7 = df['浸炭室ローラー3']
        _data8 = df['降温室ローラー']
        _data9 = df['油槽エレベータチェン']
        mygui.frame_1.label.set(NO + "(" + str_date + ")")
    except Exception as ex:
        logger.error(f'on_changed: {ex}')

    
     
my_event_handler.on_modified = on_changed
my_event_handler.on_created = on_changed
my_event_handler.on_deleted = on_changed
#Craete observer 
go_recursively = True
my_observer = Observer()
my_observer.schedule(my_event_handler, path, recursive=go_recursively)
my_observer.start()

#set all front to 6
plt.rcParams.update({'font.size': 6})
Fond = {'fontsize':6}


def animate_1_1(i):
    global time_range
    try:
        y_lim = 21
        mygui.frame_1.a1.clear()
        mygui.frame_1.a1.set_title('昇温室ファン',fontname="MS Gothic",fontsize=10) 
        mygui.frame_1.a1.tick_params(axis='x', labelrotation= 45,labelsize = 7)
        mygui.frame_1.a1.set_xticks(time_range)
        mygui.frame_1.a1.set_xlabel('時間',fontname="MS Gothic")
        mygui.frame_1.a1.xaxis.set_label_coords(1.02, -0.025)
        mygui.frame_1.a1.set_ylim(0,30)
        mygui.frame_1.a1.set_xlim(time(0, 0),time(23, 0))
        mygui.frame_1.a1.tick_params(axis="y", labelsize=8)
        mygui.frame_1.a1.yaxis.grid(True)
    #    mygui.frame_1.a1.plot(_data1,linewidth = 1,label='Pressure')
      
        mygui.frame_1.a1.plot(_time,_data1, marker ='.', linewidth = 1)
    
        mygui.frame_1.a1.fill_between(_time, _data1, y_lim,
                     where=(_data1 > y_lim),
                     interpolate=True, color='red', alpha=0.25)
    #    
        mygui.frame_1.a1.fill_between(_time, _data1, y_lim,
                     where=(_data1 <= y_lim),
                     interpolate=True, color='blue', alpha=0.25)    
    except Exception as ex:
        logger.error(f'animate_1_1: {ex}')
    
def animate_2_1(i):
    mygui.frame_3.a1.clear()
    mygui.frame_3.a1.tick_params(axis="y", labelsize=8)
    mygui.frame_3.a1.bar('',_data1.max(),width = 2,color='#DA532F')
    mygui.frame_3.a1.set_yticks([0,21])
    mygui.frame_3.a1.text(-0.5, _data1.max() + .4, _data1.max(), color='black',
                          fontweight='bold', fontsize = 10)
    mygui.frame_3.a1.axes.get_xaxis().set_visible(False)   
    mygui.frame_2.var_1.set(str(_data1.max()))

def animate_2_2(i):
    mygui.frame_3.a2.clear()
    mygui.frame_3.a2.tick_params(axis="y", labelsize=8)
    mygui.frame_3.a2.bar('',_data2.max(),width = 2,color='#2952A4')
    mygui.frame_3.a2.set_yticks([0,8.5])   
    mygui.frame_3.a2.text(-0.5, _data2.max() + .25, _data2.max(), color='black',
                          fontweight='bold', fontsize = 10)
    mygui.frame_3.a2.axes.get_xaxis().set_visible(False) 
    mygui.frame_2.var_2.set(str(_data2.max()))

def animate_2_3(i):
    mygui.frame_3.a3.clear()
    mygui.frame_3.a3.tick_params(axis="y", labelsize=8)
    mygui.frame_3.a3.bar('',_data3.max(),width = 2,color='green')
    mygui.frame_3.a3.set_yticks([0,8.5])   
    mygui.frame_3.a3.text(-0.5, _data3.max() + .25, _data3.max(), color='black',
                          fontweight='bold', fontsize = 10)
    mygui.frame_3.a3.axes.get_xaxis().set_visible(False) 
    mygui.frame_2.var_3.set(str(_data3.max()))
    
def animate_2_4(i):
    mygui.frame_3.a4.clear()
    mygui.frame_3.a4.tick_params(axis="y", labelsize=8)
    mygui.frame_3.a4.bar('',_data4.max(),width = 2,color='#F3A925')
    mygui.frame_3.a4.set_yticks([0,3.2])   
    mygui.frame_3.a4.text(-0.5, _data4.max() + .1, _data4.max(), color='black',
                          fontweight='bold', fontsize = 10)
    mygui.frame_3.a4.axes.get_xaxis().set_visible(False) 
    mygui.frame_2.var_4.set(str(_data4.max()))
    
def animate_2_5(i):
    mygui.frame_3.a5.clear()
    mygui.frame_3.a5.tick_params(axis="y", labelsize=8)
    mygui.frame_3.a5.bar('',_data5.max(),width = 2,color='#B39154')
    mygui.frame_3.a5.set_yticks([0,3.2])   
    mygui.frame_3.a5.text(-0.5, _data5.max() + .1, _data5.max(), color='black',
                          fontweight='bold', fontsize = 10)
    mygui.frame_3.a5.axes.get_xaxis().set_visible(False) 
    mygui.frame_2.var_5.set(str(_data5.max()))
    
def animate_2_6(i):
    mygui.frame_3.a6.clear()
    mygui.frame_3.a6.tick_params(axis="y", labelsize=8)
    mygui.frame_3.a6.bar('',_data6.max(),width = 2,color='black')
    mygui.frame_3.a6.set_yticks([0,3.2])   
    mygui.frame_3.a6.text(-0.5, _data6.max() + .1, _data6.max(), color='black',
                          fontweight='bold', fontsize = 10)
    mygui.frame_3.a6.axes.get_xaxis().set_visible(False) 
    mygui.frame_2.var_6.set(str(_data6.max()))
    
def animate_2_7(i):
    mygui.frame_3.a7.clear()
    mygui.frame_3.a7.tick_params(axis="y", labelsize=8)
    mygui.frame_3.a7.bar('',_data7.max(),width = 2,color='#A066DD')
    mygui.frame_3.a7.set_yticks([0,3.2])   
    mygui.frame_3.a7.text(-0.5, _data7.max() + .1, _data7.max(), color='black',
                          fontweight='bold', fontsize = 10)
    mygui.frame_3.a7.axes.get_xaxis().set_visible(False) 
    mygui.frame_2.var_7.set(str(_data7.max()))
    
def animate_2_8(i):
    mygui.frame_3.a8.clear()
    mygui.frame_3.a8.tick_params(axis="y", labelsize=8)
    mygui.frame_3.a8.bar('',_data8.max(),width = 2,color='#50D0DA')
    mygui.frame_3.a8.set_yticks([0,3.2])   
    mygui.frame_3.a8.text(-0.5, _data8.max() + .1, _data8.max(), color='black',
                          fontweight='bold', fontsize = 10)
    mygui.frame_3.a8.axes.get_xaxis().set_visible(False) 
    mygui.frame_2.var_8.set(str(_data8.max()))
    
def animate_2_9(i):
    mygui.frame_3.a9.clear()
    mygui.frame_3.a9.tick_params(axis="y", labelsize=8)
    mygui.frame_3.a9.bar('',_data9.max(),width = 2,color='#725727')
    mygui.frame_3.a9.set_yticks([0,1.8])   
    mygui.frame_3.a9.text(-0.5, _data9.max() + .02, _data9.max(), color='black',
                          fontweight='bold', fontsize = 10)
    mygui.frame_3.a9.axes.get_xaxis().set_visible(False) 
    mygui.frame_2.var_9.set(str(_data9.max()))   
    
update_status = True    
def onClick():
    global update_status
    if update_status:
        mygui.ani_1_1.event_source.stop()
        mygui.ani_2_1.event_source.stop()
        mygui.ani_2_2.event_source.stop()
        mygui.ani_2_3.event_source.stop()
        mygui.ani_2_4.event_source.stop()
        mygui.ani_2_5.event_source.stop()
        mygui.ani_2_6.event_source.stop()
        mygui.ani_2_7.event_source.stop()
        mygui.ani_2_8.event_source.stop()
        mygui.ani_2_9.event_source.stop()
        update_status = False
        mygui.frame_3.status_var.set('Stop') 
    else:
        mygui.ani_1_1.event_source.start()
        mygui.ani_2_1.event_source.start()
        mygui.ani_2_2.event_source.start()
        mygui.ani_2_3.event_source.start()
        mygui.ani_2_4.event_source.start()
        mygui.ani_2_5.event_source.start()
        mygui.ani_2_6.event_source.start()
        mygui.ani_2_7.event_source.start()
        mygui.ani_2_8.event_source.start()
        mygui.ani_2_9.event_source.start()
        update_status = True
        mygui.frame_3.status_var.set('Start')

class Frame1(Frame):
    def __init__(self,parent,*args, **kwargs):
        super().__init__(parent,*args, **kwargs)
        self.label = StringVar()
        self.NO_label = Label(self,textvariable = self.label,font =('MS Gothic',15),anchor=E,
                             bg='White',padx=1)
        self.label.set(NO + "(" + str_date + ")")
        
        self.NO_label.pack(fill=BOTH,expand=True)
        
        self.f1 = Figure(figsize = (7,3), dpi =100,tight_layout=True)
        self.a1 = self.f1.add_subplot(111)
      
        self.canvas1 = FigureCanvasTkAgg(self.f1,self)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().pack(fill = BOTH, expand = True)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas1,self)
        self.toolbar.config(background="white")
        self.toolbar.update()
        self.canvas1._tkcanvas.pack(fill=BOTH,expand=True)
        

class Frame2(Frame):
    def __init__(self,parent,*args, **kwargs):
        super().__init__(parent,*args, **kwargs)
        # First Row
        self.label_1 = Label(self,text = "昇温室ファン",font =('MS Gothic',10),
                             pady =1,fg='#DA532F',bg='white',padx=2)
        self.label_6 = Label(self,text = "浸炭室ローラ２",font =('MS Gothic',10) ,
                             pady =1,fg='black',bg='white',padx=1)
        # Second row
        self.var_1 = StringVar()
        self.value_1 = Label(self,textvariable = self.var_1,font =('Times 18 bold'),
                            bg='white')
        self.var_1.set(str(_data1.max()))
        self.var_6 = StringVar()
        self.value_6 = Label(self,textvariable = self.var_6,font =('Times 18 bold'),
                            bg='white')
        self.var_6.set(str(_data6.max()))
        # Third row
        self.label_2 = Label(self,text = "浸炭室ファン",font =('MS Gothic',10),
                             fg='#2952A4',bg='white',padx=1)
        self.label_7 = Label(self,text = "浸炭室ローラ３",font =('MS Gothic',10) ,
                             fg='#A066DD',bg='white',padx=1)        
        # Forth row
        self.var_2 = StringVar()
        self.value_2 = Label(self,textvariable = self.var_2,font =('Times 18 bold'),
                            bg='white')
        self.var_2.set(str(_data2.max()))
        self.var_7 = StringVar()
        self.value_7 = Label(self,textvariable = self.var_7,font =('Times 18 bold'),
                            bg='white')
        self.var_7.set(str(_data7.max()))
        # Fifth row
        self.label_3 = Label(self,text = "降温室ファン",font =('MS Gothic',10),
                             fg='green',bg='white',padx=1)
        self.label_8 = Label(self,text = "降温室ローラ",font =('MS Gothic',10) ,
                             fg='#50D0DA',bg='white',padx=1)     
        # Sixth row
        self.var_3 = StringVar()
        self.value_3 = Label(self,textvariable = self.var_3,font =('Times 18 bold'),
                            bg='white')
        self.var_3.set(str(_data3.max()))
        self.var_8 = StringVar()
        self.value_8 = Label(self,textvariable = self.var_8,font =('Times 18 bold'),
                            bg='white')
        self.var_8.set(str(_data8.max()))
        # seventh row
        self.label_4 = Label(self,text = "昇温室ローラ",font =('MS Gothic',10),
                             fg='#F3A925',bg='white',padx=1)
        self.label_9 = Label(self,text = "油槽エレベータ",font =('MS Gothic',10) ,
                             fg='#725727',bg='white',padx=1) 
        # eighth row
        self.var_4 = StringVar()
        self.value_4 = Label(self,textvariable = self.var_4,font =('Times 18 bold'),
                            bg='white')
        self.var_4.set(str(_data4.max()))
        self.var_9 = StringVar()
        self.value_9 = Label(self,textvariable = self.var_9,font =('Times 18 bold'),
                            bg='white')
        self.var_9.set(str(_data9.max())) 
        # 9th row
        self.label_5 = Label(self,text = "昇温室ローラ",font =('MS Gothic',10),
                             fg='#B39154',bg='white',padx=1)  

        #10th row
        self.var_5 = StringVar()
        self.value_5 = Label(self,textvariable = self.var_5,font =('Times 18 bold'),
                            bg='white')
        self.var_5.set(str(_data5.max())) 
      

        #grid
        self.label_1 .grid(row =0,column = 0,sticky = 'nswe',padx=1)
        self.label_6 .grid(row =0,column = 1,sticky = 'nswe')
        
        self.value_1 .grid(row =1,column = 0,sticky = 'nswe')
        self.value_6 .grid(row =1,column = 1,sticky = 'nswe')
        
        self.label_2 .grid(row =2,column = 0,sticky = 'nswe')
        self.label_7 .grid(row =2,column = 1,sticky = 'nswe')       
        
        self.value_2 .grid(row =3,column = 0,sticky = 'nswe')
        self.value_7 .grid(row =3,column = 1,sticky = 'nswe')
        
        self.label_3 .grid(row =4,column = 0,sticky = 'nswe')
        self.label_8 .grid(row =4,column = 1,sticky = 'nswe')       
        
        self.value_3 .grid(row =5,column = 0,sticky = 'nswe')
        self.value_8 .grid(row =5,column = 1,sticky = 'nswe')        
        
        self.label_4 .grid(row =6,column = 0,sticky = 'nswe')
        self.label_9 .grid(row =6,column = 1,sticky = 'nswe')        
        
        self.value_4 .grid(row =7,column = 0,sticky = 'nswe')
        self.value_9 .grid(row =7,column = 1,sticky = 'nswe')         
        
        self.label_5 .grid(row =8,column = 0,sticky = 'nswe') 
        
        self.value_5 .grid(row =9,column = 0,sticky = 'nswe')

        
    
        #set the weight to all column and row (have to use for loop later)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

class Frame3(Frame):
    def __init__(self,parent,*args, **kwargs):
        super().__init__(parent,*args, **kwargs)
    
# =============================================================================
#        1    
# =============================================================================
        self.f1 = Figure(figsize = (1,1.7), dpi =100,tight_layout=True)
        self.a1 = self.f1.add_subplot(111)  
        
        self.canvas1 = FigureCanvasTkAgg(self.f1,self)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().grid(row =0,column = 0,sticky = 'nswe')      
        
# =============================================================================
#         2
# =============================================================================
        self.f2 = Figure(figsize = (1,1.7), dpi =100,tight_layout=True)
        self.a2 = self.f2.add_subplot(111)       
        
        self.canvas2 = FigureCanvasTkAgg(self.f2,self)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().grid(row =0,column = 1,sticky = 'nswe')
# =============================================================================
#         3
# =============================================================================
        self.f3 = Figure(figsize = (1,1.7), dpi =100,tight_layout=True)
        self.a3 = self.f3.add_subplot(111)
      
        self.canvas3 = FigureCanvasTkAgg(self.f3,self)
        self.canvas3.draw()
        self.canvas3.get_tk_widget().grid(row =0,column = 2,sticky = 'nswe')        
# =============================================================================
#         4
# =============================================================================
        self.f4 = Figure(figsize = (1,1.7), dpi =100,tight_layout=True)
        self.a4 = self.f4.add_subplot(111)      
        
        self.canvas4 = FigureCanvasTkAgg(self.f4,self)
        self.canvas4.draw()
        self.canvas4.get_tk_widget().grid(row =0,column = 3,sticky = 'nswe')         
        
# =============================================================================
#         5
# =============================================================================
        self.f5 = Figure(figsize = (1,1.7), dpi =100,tight_layout=True)
        self.a5 = self.f5.add_subplot(111)

        self.canvas5 = FigureCanvasTkAgg(self.f5,self)
        self.canvas5.draw()
        self.canvas5.get_tk_widget().grid(row =0,column = 4,sticky = 'nswe') 
        
# =============================================================================
#       6          
# =============================================================================
        self.f6 = Figure(figsize = (1,1.7), dpi =100,tight_layout=True)
        self.a6 = self.f6.add_subplot(111)   
        
        self.canvas6 = FigureCanvasTkAgg(self.f6,self)
        self.canvas6.draw()
        self.canvas6.get_tk_widget().grid(row =1,column = 0,sticky = 'nse') 
        
# =============================================================================
#         7
# =============================================================================
        self.f7 = Figure(figsize = (1,1.7), dpi =100,tight_layout=True)
        self.a7 = self.f7.add_subplot(111)

        self.canvas7 = FigureCanvasTkAgg(self.f7,self)
        self.canvas7.draw()
        self.canvas7.get_tk_widget().grid(row =1,column = 1,sticky = 'nswe')       
        
# =============================================================================
#         8
# =============================================================================   
        self.f8 = Figure(figsize = (1,1.7), dpi =100,tight_layout=True)
        self.a8 = self.f8.add_subplot(111)
          
        self.canvas8 = FigureCanvasTkAgg(self.f8,self)
        self.canvas8.draw()
        self.canvas8.get_tk_widget().grid(row =1,column = 2,sticky = 'nswe')      
        
# =============================================================================
#         9
# =============================================================================
        self.f9 = Figure(figsize = (1,1.7), dpi =100,tight_layout=True)
        self.a9 = self.f9.add_subplot(111)

        self.canvas9 = FigureCanvasTkAgg(self.f9,self)
        self.canvas9.draw()
        self.canvas9.get_tk_widget().grid(row =1,column = 3,sticky = 'nswe')   
        
# =============================================================================
#        botton       
# =============================================================================
        self.botton = Button(self,text = "Change Update", command = onClick)
        self.botton.grid(row =1,column = 4,sticky = 'e')
    
        
# =============================================================================
#         status label
# =============================================================================
        self.status_var = StringVar()
        self.status_label = Label(self,textvariable = self.status_var,font =('Times 10 bold'),
                            bg='white')
        self.status_var.set('Start')
        self.status_label.grid(row =1,column = 5,sticky = 'w')
        
        #this one is no need because we set the GUI grid already & our Frame is sticky to those GUI's grid 
        #& our widget are sticky to those Frame's grid
#        self.grid_columnconfigure(0, weight=1)
#        self.grid_columnconfigure(1, weight=1)       
        
class GUI(Tk):
    #actually **kwargs only is enought because there is not 
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('GOT Graph')
        self.window_width = 1200
        self.window_height = 680
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.x_cor = int((self.screen_width/2)-(self.window_width/2))
        self.y_cor = int((self.screen_height/2) - (self.window_height/2))
        self.geometry('{}x{}+{}+{}'.format(self.window_width,self.window_height,self.x_cor,self.y_cor-35))
        #self.configure(bg='#334456')
        self.frame_1 = Frame1(self,bd =1,relief = RAISED,bg='white')
        self.frame_2 = Frame2(self,bd =1,relief = RAISED,bg='white')
        self.frame_3 = Frame3(self,bd =1,relief = RAISED,bg='white')
        
        self.frame_1.grid(row=0,columnspan = 2,sticky='nsew')
        self.frame_2.grid(row =1,column = 0,sticky='nsew')
        self.frame_3.grid(row =1,column = 1,sticky='nsew')
   
        #set weight to all column and row
#        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        
def creat_animate(mygui):
    #can use lambda also
    mygui.ani_1_1 = FuncAnimation(mygui.frame_1.f1, lambda i : animate_1_1(i), interval = 3000 )
    mygui.ani_2_1 = FuncAnimation(mygui.frame_3.f1, animate_2_1, interval = 3000 )
    mygui.ani_2_2 = FuncAnimation(mygui.frame_3.f2, animate_2_2, interval = 3000 )
    mygui.ani_2_3 = FuncAnimation(mygui.frame_3.f3, animate_2_3, interval = 3000 )
    mygui.ani_2_4 = FuncAnimation(mygui.frame_3.f4, animate_2_4, interval = 3000 )
    mygui.ani_2_5 = FuncAnimation(mygui.frame_3.f5, animate_2_5, interval = 3000 )
    mygui.ani_2_6 = FuncAnimation(mygui.frame_3.f6, animate_2_6, interval = 3000 )
    mygui.ani_2_7 = FuncAnimation(mygui.frame_3.f7, animate_2_7, interval = 3000 )
    mygui.ani_2_8 = FuncAnimation(mygui.frame_3.f8, animate_2_8, interval = 3000 )
    mygui.ani_2_9 = FuncAnimation(mygui.frame_3.f9, animate_2_9, interval = 3000 )


just_start = True   
try :
    mygui = GUI()
    #we can out all of animate instances here also but ithink every time the gui is updated. it will create new 
    #anamate object
    if just_start:
        creat_animate(mygui)
        just_start = False
except Exception as ex:
    print(ex)
mygui.mainloop() 


my_observer.stop()        
my_observer.join()

#exit()
