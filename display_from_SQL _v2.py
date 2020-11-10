from tkinter import *
from tkinter import messagebox,simpledialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import threading
import time as tt
from datetime import datetime,time,timedelta
from matplotlib.animation import FuncAnimation
import os
import logging
from logging.handlers import TimedRotatingFileHandler
import pyodbc
from sys import exit



#get data every some times?

def update_data(gui_obj):
 
    while True:          
        if gui_obj.stopthread:
            print(f'Break thread for {gui_obj.GOT_num}')
            print('The master (Toplevel) will be garbage collected from now')
            #after this, the Toplevel object will be garbage collected because the 'gui_obj' variable
            # will be deleted after out of scope
            #in this program task will have no referrence because the sub is already garbage collected
            break
        try :
            #to stop the process and kill the master
            gui_obj.df = get_df(gui_obj.select_date,gui_obj.select_end_date,gui_obj.GOT_num,gui_obj.cols)
            gui_obj.str_date = str(gui_obj.df.index.date[0])
            gui_obj.end_date = str(gui_obj.df.index.date[-1])
            gui_obj._time = gui_obj.df.index.strftime('%Y/%m/%d %X')
            gui_obj._data1 = gui_obj.df['昇温室ファン']
            gui_obj._data2 = gui_obj.df['浸炭室ファン']
            gui_obj._data3 = gui_obj.df['降温室ファン']
            gui_obj._data4 = gui_obj.df['昇温室ローラー']
            gui_obj._data5 = gui_obj.df['浸炭室ローラー1']
            gui_obj._data6 = gui_obj.df['浸炭室ローラー2']
            gui_obj._data7 = gui_obj.df['浸炭室ローラー3']
            gui_obj._data8 = gui_obj.df['降温室ローラー']
            gui_obj._data9 = gui_obj.df['油槽エレベータチェン']
            gui_obj.frame_1.label.set(gui_obj.GOT_num + "(" + gui_obj.str_date + ' ~ ' + gui_obj.end_date + ")")
            print(f'Update data for {gui_obj.GOT_num}')
        except Exception as ex:
            logger.error('update_data(' +  gui_obj.GOT_num + f') 99: {ex}')
            
        tt.sleep(15)

#get df from SQL fuction
def get_df(strdate,enddate,GOT_num,cols):
    
    SQL_server = '********'
    SQL_database= '*****'
    
    try: 
        conn = pyodbc.connect('Driver={SQL Server};\
                               Server=' + SQL_server + ';\
                               Database=' + SQL_database + ';\
                               UID=IOT_User;\
                               PWD=sa;') 
        cursor = conn.cursor()
        
        insert_query = '''
                        SELECT *
                        FROM [IOT].[dbo].[**************]
                        where (時間 BETWEEN \'''' + strdate +  '''\' AND \'''' + enddate + '''\') and (GOT_Number = \'''' + GOT_num + '\')'                
               
        cursor.execute(insert_query)
        
        data_tuples = cursor.fetchall()
    
        data_lists = [i for i in map(list, data_tuples)]
        df = pd.DataFrame(data_lists , index = None) 
        
        # we will re turn created df
        if len(df) == 0:
            df = pd.DataFrame([[98]*10], columns = cols)
            df['時間']= datetime(2000,1,1,0,0,0)
            df = df.set_index('時間')
        else:    
            df = df.drop(1,axis=1)
            df.columns = cols
            df = df.set_index('時間')
            
            #other wise it will change the cols atribute of out gui object
            new_cols = cols.copy()
            new_cols.remove('時間')
            for col in new_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    except Exception as ex:
        logger.error(f'get_df(' +  GOT_num + f'): {ex}')
        df = pd.DataFrame([[99]*10], columns = cols)
        df['時間']= datetime(2000,1,1,0,0,0)
        df = df.set_index('時間')
    finally:
        cursor.close()
        conn.close()
    
    return df


def animate_1_1(i,gui_obj):
    global time_range
    try:
        y_lim1 = 10
        y_lim2 = 20
        gui_obj.frame_1.a1.clear()
        gui_obj.frame_1.a1.set_title('昇温室ファン',fontname="MS Gothic",fontsize=10) 
        gui_obj.frame_1.a1.tick_params(axis='x', labelrotation= 90,labelsize = 7)
        
        tick_index = np.arange(0, len(gui_obj.df), 24)
        text_to_display = [gui_obj.df.index[i].strftime('%Y/%m/%d') for i in tick_index]
        gui_obj.frame_1.a1.set_xticks(tick_index)
        gui_obj.frame_1.a1.set_xticklabels(text_to_display)
        gui_obj.frame_1.a1.set_xlabel('時間',fontname="MS Gothic")
        gui_obj.frame_1.a1.xaxis.set_label_coords(1.02, -0.025)
        gui_obj.frame_1.a1.set_ylim(0,30)
        gui_obj.frame_1.a1.tick_params(axis="y", labelsize=8)
        gui_obj.frame_1.a1.yaxis.grid(True)

        gui_obj.frame_1.a1.plot(gui_obj._time,gui_obj._data1, marker =None, linewidth = 1)
    
        gui_obj.frame_1.a1.fill_between(gui_obj._time, gui_obj._data1, y_lim2,
                     where=(gui_obj._data1 > y_lim2),
                     interpolate=True, color='red', alpha=1)

        gui_obj.frame_1.a1.fill_between(gui_obj._time, gui_obj._data1, y_lim1,
                     where=(np.bitwise_and(gui_obj._data1 > y_lim1 ,gui_obj._data1 <= y_lim2)),
                     interpolate=True, color='yellow', alpha=0.25)
    #    
        gui_obj.frame_1.a1.fill_between(gui_obj._time, gui_obj._data1, y_lim1,
                     where=(gui_obj._data1 <= y_lim1),
                     interpolate=True, color='blue', alpha=0.25)    
    except Exception as ex:
        logger.error(f'animate_1_1( ' +  gui_obj.GOT_num + f'): {ex}')
    
def animate_2_1(i,gui_obj):
    gui_obj.frame_3.a1.clear()
    gui_obj.frame_3.a1.tick_params(axis="y", labelsize=8)
    gui_obj.frame_3.a1.bar('',gui_obj._data1.max(),width = 2,color='#DA532F')
    gui_obj.frame_3.a1.set_yticks([0,21])
    gui_obj.frame_3.a1.text(-0.5, gui_obj._data1.max() + .4, gui_obj._data1.max(), color='black',
                          fontweight='bold', fontsize = 10)
    gui_obj.frame_3.a1.axes.get_xaxis().set_visible(False)   
    gui_obj.frame_2.var_1.set(str(gui_obj._data1.max()))

def animate_2_2(i,gui_obj):
    gui_obj.frame_3.a2.clear()
    gui_obj.frame_3.a2.tick_params(axis="y", labelsize=8)
    gui_obj.frame_3.a2.bar('',gui_obj._data2.max(),width = 2,color='#2952A4')
    gui_obj.frame_3.a2.set_yticks([0,8.5])   
    gui_obj.frame_3.a2.text(-0.5, gui_obj._data2.max() + .25, gui_obj._data2.max(), color='black',
                          fontweight='bold', fontsize = 10)
    gui_obj.frame_3.a2.axes.get_xaxis().set_visible(False) 
    gui_obj.frame_2.var_2.set(str(gui_obj._data2.max()))

def animate_2_3(i,gui_obj):
    gui_obj.frame_3.a3.clear()
    gui_obj.frame_3.a3.tick_params(axis="y", labelsize=8)
    gui_obj.frame_3.a3.bar('',gui_obj._data3.max(),width = 2,color='green')
    gui_obj.frame_3.a3.set_yticks([0,8.5])   
    gui_obj.frame_3.a3.text(-0.5, gui_obj._data3.max() + .25, gui_obj._data3.max(), color='black',
                          fontweight='bold', fontsize = 10)
    gui_obj.frame_3.a3.axes.get_xaxis().set_visible(False) 
    gui_obj.frame_2.var_3.set(str(gui_obj._data3.max()))
    
def animate_2_4(i,gui_obj):
    gui_obj.frame_3.a4.clear()
    gui_obj.frame_3.a4.tick_params(axis="y", labelsize=8)
    gui_obj.frame_3.a4.bar('',gui_obj._data4.max(),width = 2,color='#F3A925')
    gui_obj.frame_3.a4.set_yticks([0,3.2])   
    gui_obj.frame_3.a4.text(-0.5, gui_obj._data4.max() + .1, gui_obj._data4.max(), color='black',
                          fontweight='bold', fontsize = 10)
    gui_obj.frame_3.a4.axes.get_xaxis().set_visible(False) 
    gui_obj.frame_2.var_4.set(str(gui_obj._data4.max()))
    
def animate_2_5(i,gui_obj):
    gui_obj.frame_3.a5.clear()
    gui_obj.frame_3.a5.tick_params(axis="y", labelsize=8)
    gui_obj.frame_3.a5.bar('',gui_obj._data5.max(),width = 2,color='#B39154')
    gui_obj.frame_3.a5.set_yticks([0,3.2])   
    gui_obj.frame_3.a5.text(-0.5, gui_obj._data5.max() + .1, gui_obj._data5.max(), color='black',
                          fontweight='bold', fontsize = 10)
    gui_obj.frame_3.a5.axes.get_xaxis().set_visible(False) 
    gui_obj.frame_2.var_5.set(str(gui_obj._data5.max()))
    
def animate_2_6(i,gui_obj):
    gui_obj.frame_3.a6.clear()
    gui_obj.frame_3.a6.tick_params(axis="y", labelsize=8)
    gui_obj.frame_3.a6.bar('',gui_obj._data6.max(),width = 2,color='black')
    gui_obj.frame_3.a6.set_yticks([0,3.2])   
    gui_obj.frame_3.a6.text(-0.5, gui_obj._data6.max() + .1, gui_obj._data6.max(), color='black',
                          fontweight='bold', fontsize = 10)
    gui_obj.frame_3.a6.axes.get_xaxis().set_visible(False) 
    gui_obj.frame_2.var_6.set(str(gui_obj._data6.max()))
    
def animate_2_7(i,gui_obj):
    gui_obj.frame_3.a7.clear()
    gui_obj.frame_3.a7.tick_params(axis="y", labelsize=8)
    gui_obj.frame_3.a7.bar('',gui_obj._data7.max(),width = 2,color='#A066DD')
    gui_obj.frame_3.a7.set_yticks([0,3.2])   
    gui_obj.frame_3.a7.text(-0.5, gui_obj._data7.max() + .1, gui_obj._data7.max(), color='black',
                          fontweight='bold', fontsize = 10)
    gui_obj.frame_3.a7.axes.get_xaxis().set_visible(False) 
    gui_obj.frame_2.var_7.set(str(gui_obj._data7.max()))
    
def animate_2_8(i,gui_obj):
    gui_obj.frame_3.a8.clear()
    gui_obj.frame_3.a8.tick_params(axis="y", labelsize=8)
    gui_obj.frame_3.a8.bar('',gui_obj._data8.max(),width = 2,color='#50D0DA')
    gui_obj.frame_3.a8.set_yticks([0,3.2])   
    gui_obj.frame_3.a8.text(-0.5, gui_obj._data8.max() + .1, gui_obj._data8.max(), color='black',
                          fontweight='bold', fontsize = 10)
    gui_obj.frame_3.a8.axes.get_xaxis().set_visible(False) 
    gui_obj.frame_2.var_8.set(str(gui_obj._data8.max()))
    
def animate_2_9(i,gui_obj):
    gui_obj.frame_3.a9.clear()
    gui_obj.frame_3.a9.tick_params(axis="y", labelsize=8)
    gui_obj.frame_3.a9.bar('',gui_obj._data9.max(),width = 2,color='#725727')
    gui_obj.frame_3.a9.set_yticks([0,1.8])   
    gui_obj.frame_3.a9.text(-0.5, gui_obj._data9.max() + .02, gui_obj._data9.max(), color='black',
                          fontweight='bold', fontsize = 10)
    gui_obj.frame_3.a9.axes.get_xaxis().set_visible(False) 
    gui_obj.frame_2.var_9.set(str(gui_obj._data9.max()))   
    
    
def onClick_status(gui_obj):
    if gui_obj.update_status:
        gui_obj.ani_1_1.event_source.stop()
        gui_obj.ani_2_1.event_source.stop()
        gui_obj.ani_2_2.event_source.stop()
        gui_obj.ani_2_3.event_source.stop()
        gui_obj.ani_2_4.event_source.stop()
        gui_obj.ani_2_5.event_source.stop()
        gui_obj.ani_2_6.event_source.stop()
        gui_obj.ani_2_7.event_source.stop()
        gui_obj.ani_2_8.event_source.stop()
        gui_obj.ani_2_9.event_source.stop()
        gui_obj.update_status = False
        gui_obj.frame_3.status_var.set('Stop') 
    else:
        gui_obj.ani_1_1.event_source.start()
        gui_obj.ani_2_1.event_source.start()
        gui_obj.ani_2_2.event_source.start()
        gui_obj.ani_2_3.event_source.start()
        gui_obj.ani_2_4.event_source.start()
        gui_obj.ani_2_5.event_source.start()
        gui_obj.ani_2_6.event_source.start()
        gui_obj.ani_2_7.event_source.start()
        gui_obj.ani_2_8.event_source.start()
        gui_obj.ani_2_9.event_source.start()
        gui_obj.update_status = True
        gui_obj.frame_3.status_var.set('Start')
        
def onClick_date(gui_obj):
    gui_obj.select_date = gui_obj.frame_3.entry1_var.get()
    gui_obj.select_end_date = gui_obj.frame_3.entry2_var.get()
    
    if gui_obj.select_end_date == '':
        gui_obj.select_end_date = str(datetime.now().date())
        
    try :
        gui_obj.df = get_df(gui_obj.select_date,gui_obj.select_end_date,gui_obj.GOT_num,gui_obj.cols)
        gui_obj.str_date = str(gui_obj.df.index.date[0])
        gui_obj.end_date = str(gui_obj.df.index.date[-1])
        gui_obj._time = gui_obj.df.index.strftime('%Y/%m/%d %X')
        gui_obj._data1 = gui_obj.df['昇温室ファン']
        gui_obj._data2 = gui_obj.df['浸炭室ファン']
        gui_obj._data3 = gui_obj.df['降温室ファン']
        gui_obj._data4 = gui_obj.df['昇温室ローラー']
        gui_obj._data5 = gui_obj.df['浸炭室ローラー1']
        gui_obj._data6 = gui_obj.df['浸炭室ローラー2']
        gui_obj._data7 = gui_obj.df['浸炭室ローラー3']
        gui_obj._data8 = gui_obj.df['降温室ローラー']
        gui_obj._data9 = gui_obj.df['油槽エレベータチェン']
        gui_obj.frame_1.label.set(gui_obj.GOT_num + "(" + gui_obj.str_date + ' ~ ' + gui_obj.end_date + ")")
        print(f'Change date by clicking for {gui_obj.GOT_num}')
    except Exception as ex:
        logger.error('onClick_date(' +  gui_obj.GOT_num + f'): {ex}')
            
def on_closing(sub_gui):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        sub_gui.master.stopthread = True
        # Destroy all widget of toplevel(just widget). but other attributes is still alive
        sub_gui.master.destroy()  

#
        
class Frame1(Frame):
    def __init__(self,parent,*args, **kwargs):
        super().__init__(parent,*args, **kwargs)
        self.label = StringVar()
        self.NO_label = Label(self,textvariable = self.label,font =('Times 18 bold'),anchor=E,
                             bg='White',padx=1) 
        self.label.set(parent.GOT_num + "(" + parent.str_date + ' ~ ' + parent.end_date + ")")
        
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
        self.var_1.set(str(parent._data1.max()))
        self.var_6 = StringVar()
        self.value_6 = Label(self,textvariable = self.var_6,font =('Times 18 bold'),
                            bg='white')
        self.var_6.set(str(parent._data6.max()))
        # Third row
        self.label_2 = Label(self,text = "浸炭室ファン",font =('MS Gothic',10),
                             fg='#2952A4',bg='white',padx=1)
        self.label_7 = Label(self,text = "浸炭室ローラ３",font =('MS Gothic',10) ,
                             fg='#A066DD',bg='white',padx=1)        
        # Forth row
        self.var_2 = StringVar()
        self.value_2 = Label(self,textvariable = self.var_2,font =('Times 18 bold'),
                            bg='white')
        self.var_2.set(str(parent._data2.max()))
        self.var_7 = StringVar()
        self.value_7 = Label(self,textvariable = self.var_7,font =('Times 18 bold'),
                            bg='white')
        self.var_7.set(str(parent._data7.max()))
        # Fifth row
        self.label_3 = Label(self,text = "降温室ファン",font =('MS Gothic',10),
                             fg='green',bg='white',padx=1)
        self.label_8 = Label(self,text = "降温室ローラ",font =('MS Gothic',10) ,
                             fg='#50D0DA',bg='white',padx=1)     
        # Sixth row
        self.var_3 = StringVar()
        self.value_3 = Label(self,textvariable = self.var_3,font =('Times 18 bold'),
                            bg='white')
        self.var_3.set(str(parent._data3.max()))
        self.var_8 = StringVar()
        self.value_8 = Label(self,textvariable = self.var_8,font =('Times 18 bold'),
                            bg='white')
        self.var_8.set(str(parent._data8.max()))
        # seventh row
        self.label_4 = Label(self,text = "昇温室ローラ",font =('MS Gothic',10),
                             fg='#F3A925',bg='white',padx=1)
        self.label_9 = Label(self,text = "油槽エレベータ",font =('MS Gothic',10) ,
                             fg='#725727',bg='white',padx=1) 
        # eighth row
        self.var_4 = StringVar()
        self.value_4 = Label(self,textvariable = self.var_4,font =('Times 18 bold'),
                            bg='white')
        self.var_4.set(str(parent._data4.max()))
        self.var_9 = StringVar()
        self.value_9 = Label(self,textvariable = self.var_9,font =('Times 18 bold'),
                            bg='white')
        self.var_9.set(str(parent._data9.max())) 
        # 9th row
        self.label_5 = Label(self,text = "昇温室ローラ",font =('MS Gothic',10),
                             fg='#B39154',bg='white',padx=1)  

        #10th row
        self.var_5 = StringVar()
        self.value_5 = Label(self,textvariable = self.var_5,font =('Times 18 bold'),
                            bg='white')
        self.var_5.set(str(parent._data5.max())) 
      

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
        self.canvas1.get_tk_widget().grid(row =0,rowspan=2,column = 0,sticky = 'nswe')      
        
# =============================================================================
#         2
# =============================================================================
        self.f2 = Figure(figsize = (1,1.7), dpi =100,tight_layout=True)
        self.a2 = self.f2.add_subplot(111)       
        
        self.canvas2 = FigureCanvasTkAgg(self.f2,self)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().grid(row =0,rowspan=2,column = 1,sticky = 'nswe')
# =============================================================================
#         3
# =============================================================================
        self.f3 = Figure(figsize = (1,1.7), dpi =100,tight_layout=True)
        self.a3 = self.f3.add_subplot(111)
      
        self.canvas3 = FigureCanvasTkAgg(self.f3,self)
        self.canvas3.draw()
        self.canvas3.get_tk_widget().grid(row =0,rowspan=2,column = 2,sticky = 'nswe')        
# =============================================================================
#         4
# =============================================================================
        self.f4 = Figure(figsize = (1,1.7), dpi =100,tight_layout=True)
        self.a4 = self.f4.add_subplot(111)      
        
        self.canvas4 = FigureCanvasTkAgg(self.f4,self)
        self.canvas4.draw()
        self.canvas4.get_tk_widget().grid(row =0,rowspan=2,column = 3,sticky = 'nswe')         
        
# =============================================================================
#         5
# =============================================================================
        self.f5 = Figure(figsize = (1,1.7), dpi =100,tight_layout=True)
        self.a5 = self.f5.add_subplot(111)

        self.canvas5 = FigureCanvasTkAgg(self.f5,self)
        self.canvas5.draw()
        self.canvas5.get_tk_widget().grid(row =0,rowspan=2,column = 4,sticky = 'nswe') 
        
# =============================================================================
#       6          
# =============================================================================
        self.f6 = Figure(figsize = (1,1.7), dpi =100,tight_layout=True)
        self.a6 = self.f6.add_subplot(111)   
        
        self.canvas6 = FigureCanvasTkAgg(self.f6,self)
        self.canvas6.draw()
        self.canvas6.get_tk_widget().grid(rowspan=3,row=2,column = 0,sticky = 'nse') 
        
# =============================================================================
#         7
# =============================================================================
        self.f7 = Figure(figsize = (1,1.7), dpi =100,tight_layout=True)
        self.a7 = self.f7.add_subplot(111)

        self.canvas7 = FigureCanvasTkAgg(self.f7,self)
        self.canvas7.draw()
        self.canvas7.get_tk_widget().grid(rowspan=3,row=2,column = 1,sticky = 'nswe')       
        
# =============================================================================
#         8
# =============================================================================   
        self.f8 = Figure(figsize = (1,1.7), dpi =100,tight_layout=True)
        self.a8 = self.f8.add_subplot(111)
          
        self.canvas8 = FigureCanvasTkAgg(self.f8,self)
        self.canvas8.draw()
        self.canvas8.get_tk_widget().grid(rowspan=3,row=2,column = 2,sticky = 'nswe')      
        
# =============================================================================
#         9
# =============================================================================
        self.f9 = Figure(figsize = (1,1.7), dpi =100,tight_layout=True)
        self.a9 = self.f9.add_subplot(111)

        self.canvas9 = FigureCanvasTkAgg(self.f9,self)
        self.canvas9.draw()
        self.canvas9.get_tk_widget().grid(rowspan=3,row=2,column = 3,sticky = 'nswe')   
 

# =============================================================================
# Create sub frame to contins all buttons
# =============================================================================
#        self.subframe = Frame(self)
#        self.subframe.grid(row =1,columnspan = 2,column = 4,sticky = 'nwes')
  
# =============================================================================
#         status label status
# =============================================================================
        self.status_var = StringVar()
        self.status_label = Label(self,textvariable = self.status_var,font =('Times 10 bold'),
                            bg='white')
        self.status_var.set('Start')
        self.status_label.grid(row =0,column = 6,sticky = 's')
                         
# =============================================================================
#        botton status       
# =============================================================================
        self.botton = Button(self,text = "Change Update", command = lambda : onClick_status(parent))
        self.botton.grid(row =1,column = 6,sticky = 'n')
    

# =============================================================================
# entry1 
# =============================================================================
        self.entry1_var = StringVar()
        self.entry1 = Entry(self, textvariable = self.entry1_var,relief = 'sunken', bd = 2,font =('Times 14 bold'))
        self.entry1_var.set(parent.select_date)
        self.entry1.grid(row =2,column = 6,sticky = 's')
    
# =============================================================================
# entry2
# =============================================================================
        self.entry2_var = StringVar()
        self.entry2 = Entry(self, textvariable = self.entry2_var,relief = 'sunken', bd = 2,font =('Times 14 bold'))
        self.entry2_var.set(parent.select_end_date)
        self.entry2.grid(row =3,column = 6)
        
# =============================================================================
#        botton date      
# =============================================================================
        self.botton = Button(self,text = "Change date", command = lambda : onClick_date(parent))
        self.botton.grid(row =4,column = 6,sticky = 'n')        
   
        #this one is no need because we set the GUI grid already & our Frame is sticky to those GUI's grid 
        #& our widget are sticky to those Frame's grid
#        self.grid_columnconfigure(0, weight=1)
#        self.grid_columnconfigure(1, weight=1)       

    
class GUI(Tk):
    #actually **kwargs only is enought because there is not 
    def __init__(self):   #*args, **kwargs
        super().__init__()
        self.frame = Frame(self)
        self.frame.pack()
        self.title('Display_app')
        self.window_width = 250
        self.window_height = 75
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.x_cor = int((self.screen_width/2)-(self.window_width/2))
        self.y_cor = int((self.screen_height/2)-(self.window_width/2))
        
        self.geometry('{}x{}+{}+{}'.format(self.window_width,self.window_height,self.x_cor,self.y_cor)) 
        
        self.botton_No1 = Button(self.frame,text = "No.1", width = 10, command = lambda : self.create_Top(str((datetime.now() - timedelta(91)).date()),str(datetime.now().date()),'No.1',cols))
        self.botton_No2 = Button(self.frame,text = "No.2", width = 10, command = lambda : self.create_Top(str((datetime.now() - timedelta(91)).date()),str(datetime.now().date()),'No.2',cols))
        self.botton_NoX = Button(self.frame,text = "No.X", width = 10, command = lambda : self.create_Top(str((datetime.now() - timedelta(91)).date()),str(datetime.now().date()),None,cols))
#        self.botton_NoX = Button(self,text = "No.X", command = lambda s=self: s.create_Top(str((datetime.now() - timedelta(91)).date()),str(datetime.now().date()),None,cols))
        self.botton_No1.pack()
        self.botton_No2.pack()
        self.botton_NoX.pack()
        
    #create another window which is called top level
    def create_Top(self,select_date,select_end_date,GOT_num,cols):
#        new = Toplevel(self) !!!! dont put the Toplevel here because it will be used for simpledialog.askstring 
#        this will create another window problem
        if GOT_num == None:
            invalid_num = True
            while invalid_num:
                num = simpledialog.askstring("Input number","Which GOT number do you want to display?")   
                if num == None:
                    return
                try:
                    assert int(num)
                    invalid_num = False
                except:
                    messagebox.showinfo(title=None, message='Please input a number only')  
                    invalid_num = True
                    
            GOT_num = 'No.' + num
            new = Toplevel(self)
            Sub_GUI(new,select_date,select_end_date,GOT_num,cols)
        else:
            new = Toplevel(self)
            Sub_GUI(new,select_date,select_end_date,GOT_num,cols) 


class Sub_GUI():
    #actually **kwargs only is enought because there is not 
    def __init__(self,master,select_date,select_end_date,GOT_num,cols): # take string
        
        #Actually we can use both ex. self.cols = cols or self.master.cols
        #but we will have to pass self.master to our Frame and that Frmae will use the values(GOT,_data1,bla bla)
        #if we dont set self.master.GOT_num slike this (dont use self.master), we will meet problem
        # >> master does no have atribute GOT_num
        #master is the top level
        self.master = master
        self.master.select_date = select_date
        self.master.select_end_date = select_end_date
        self.master.GOT_num = GOT_num
        self.GOT_num = GOT_num
        self.master.cols = cols
        self.master.update_status = True

        self.master.df = get_df(self.master.select_date,self.master.select_date,self.master.GOT_num,self.master.cols)
        self.master.str_date = str(self.master.df.index.date[0])
        self.master.end_date = str(self.master.df.index.date[-1])
        self.master._time = self.master.df.index.strftime('%Y/%m/%d %X')
        self.master._data1 = self.master.df['昇温室ファン']
        self.master._data2 = self.master.df['浸炭室ファン']
        self.master._data3 = self.master.df['降温室ファン']
        self.master._data4 = self.master.df['昇温室ローラー']
        self.master._data5 = self.master.df['浸炭室ローラー1']
        self.master._data6 = self.master.df['浸炭室ローラー2']
        self.master._data7 = self.master.df['浸炭室ローラー3']
        self.master._data8 = self.master.df['降温室ローラー']
        self.master._data9 = self.master.df['油槽エレベータチェン']

        self.master.title('GOT Graph')
        
        self.window_width = 1200
        self.window_height = 680
        
  
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        
    
        self.x_cor = int((self.screen_width/2)-(self.window_width/2))
        self.y_cor = int((self.screen_height/2) - (self.window_height/2))
        
        self.master.geometry('{}x{}+{}+{}'.format(self.window_width,self.window_height,self.x_cor,self.y_cor-35))
        #self.configure(bg='#334456')
        
 
        self.master.frame_1 = Frame1(self.master,bd =1,relief = RAISED,bg='white')
        self.master.frame_2 = Frame2(self.master,bd =1,relief = RAISED,bg='white')
        self.master.frame_3 = Frame3(self.master,bd =1,relief = RAISED,bg='white')

        
        self.master.frame_1.grid(row=0,columnspan = 2,sticky='nsew')
        self.master.frame_2.grid(row =1,column = 0,sticky='nsew')
        self.master.frame_3.grid(row =1,column = 1,sticky='nsew')
   
        #set weight to all column and row
        
#        self.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=1)

        creat_animate(self.master)  # pass master because we will use its attibutes
        
        self.master.stopthread = False
        
        self.task = threading.Thread(target=update_data, args=(self.master,))
        #this task will be kills if the main program finish (daemon)
        self.task.daemon = True
        self.task.start()

        self.master.protocol("WM_DELETE_WINDOW", lambda : on_closing(self))
        
    def __del__(self):  
        #actualy the self has no refernce. but please note that we assgen self(Sub_GUI) to on_closing function.
        # the closing fuction will still be holdr Toplevel.protocol. After the widgets are destroyed, protocal finish its process.
        # after the window close, self has no referrence anymore because on_closing out of scope and is not hole anymore
        # the self now has 0 referrence so it will be destroy. 
        # please note the Toplevel object(master) is still there because it is assign to update_data fuctions which is still running
        # 
        print(f'Destroyed Sub_GUI of {self.GOT_num}')

def creat_animate(gui_obj):
    #can use lambda also
    gui_obj.ani_1_1 = FuncAnimation(gui_obj.frame_1.f1, lambda i : animate_1_1(i,gui_obj), interval = 3000 )
    gui_obj.ani_2_1 = FuncAnimation(gui_obj.frame_3.f1, lambda i : animate_2_1(i,gui_obj), interval = 3000 )
    gui_obj.ani_2_2 = FuncAnimation(gui_obj.frame_3.f2, lambda i : animate_2_2(i,gui_obj), interval = 3000 )
    gui_obj.ani_2_3 = FuncAnimation(gui_obj.frame_3.f3, lambda i : animate_2_3(i,gui_obj), interval = 3000 )
    gui_obj.ani_2_4 = FuncAnimation(gui_obj.frame_3.f4, lambda i : animate_2_4(i,gui_obj), interval = 3000 )
    gui_obj.ani_2_5 = FuncAnimation(gui_obj.frame_3.f5, lambda i : animate_2_5(i,gui_obj), interval = 3000 )
    gui_obj.ani_2_6 = FuncAnimation(gui_obj.frame_3.f6, lambda i : animate_2_6(i,gui_obj), interval = 3000 )
    gui_obj.ani_2_7 = FuncAnimation(gui_obj.frame_3.f7, lambda i : animate_2_7(i,gui_obj), interval = 3000 )
    gui_obj.ani_2_8 = FuncAnimation(gui_obj.frame_3.f8, lambda i : animate_2_8(i,gui_obj), interval = 3000 )
    gui_obj.ani_2_9 = FuncAnimation(gui_obj.frame_3.f9, lambda i : animate_2_9(i,gui_obj), interval = 3000 )
    #old version
    #gui_obj.ani_2_9 = FuncAnimation(gui_obj.frame_3.f9, animate_2_9, interval = 3000 )


if __name__ == '__main__':
    ################### Setting
#    GOT_num = ['No.1','No.2']
#    select_date = ['2020-03-18','2020-03-18']
#    select_end_date = [str(datetime.now().date()),str(datetime.now().date())]
#    get 12 weeks before
#    select_date = [str((datetime.now() - timedelta(91)).date()),str((datetime.now() - timedelta(91)).date())]
#   myvar = easygui.enterbox("What, is your favorite color?")
#    GOT_num = ['No.1']
#    select_date = ['2020-03-18']
#    select_end_date = [str(datetime.now().date())]
    cols = ['時間','昇温室ファン','浸炭室ファン', '降温室ファン', '昇温室ローラー','浸炭室ローラー1', '浸炭室ローラー2','浸炭室ローラー3', '降温室ローラー', '油槽エレベータチェン']
    
    
    # set logging 
    if not os.path.exists('logging'):
        os.makedirs('logging')
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.ERROR)
    handler = TimedRotatingFileHandler('logging\\logging_GOT_SQL.log',
                                           when="H",
                                           interval=1,
                                           backupCount=10)
    
    s_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(s_format)
    logger.addHandler(handler)
    
    #set all front to 6
    plt.rcParams.update({'font.size': 6})
    Fond = {'fontsize':6} 
    
    ####################################
    try :
        mygui = GUI()
        mygui.mainloop()
    except Exception as ex:
        logger.error(f'main: {ex}')
        print(ex)
    exit()
    ####################################
