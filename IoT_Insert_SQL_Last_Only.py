import pandas as pd
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import logging
from logging.handlers import TimedRotatingFileHandler
import pyodbc

SQL_server = '******'
SQL_database= '****'
path = '***********'  # path of csv file
cols = ['時間','昇温室ファン','浸炭室ファン', '降温室ファン', '昇温室ローラー','浸炭室ローラー1', '浸炭室ローラー2','浸炭室ローラー3', '降温室ローラー', '油槽エレベータチェン']

# set logging 
logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.ERROR)
#insert log file diratory
handler = TimedRotatingFileHandler('************',
                                       when="H",
                                       interval=1,
                                       backupCount=10)
s_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(s_format)
logger.addHandler(handler)


def insertdataFrameIntoTable(df,NO):
    value_list1 = []
    value_list2 = []
    
    for i in range(len(df)):
        data = df.iloc[i]
        values1 = (data.name,NO,data.name,NO)
        values2 = (data['昇温室ファン'],data['浸炭室ファン'],data['降温室ファン'],   
                   data['昇温室ローラー'], data['浸炭室ローラー1'], data['浸炭室ローラー2'],   
                   data['浸炭室ローラー3'],data['降温室ローラー'],data['油槽エレベータチェン'],
                   data.name,NO)
        
        value_list1.append(values1)
        value_list2.append(values2)
    try:
        
        conn = pyodbc.connect('Driver={SQL Server};\
                               Server=' + SQL_server + ';\
                               Database=' + SQL_database + ';\
                               UID=IOT_User;\
                               PWD=sa;') 
        cursor = conn.cursor()
        
        insert_query = '''
                    INSERT INTO [IOT].[dbo].[********]
                      (時間, GOT_Number)
                    SELECT ? ,?
                    WHERE NOT EXISTS(SELECT 時間,GOT_Number
                                        FROM [IOT].[dbo].[********]
                                       WHERE 時間 = ? AND
                    				   GOT_Number = ?)
               '''
               
        cursor.executemany(insert_query,value_list1)   
        conn.commit()       
        
        insert_query = '''
                    UPDATE [IOT].[dbo].[**********]
                           SET 昇温室ファン = ? ,浸炭室ファン = ?,
                           降温室ファン = ? ,昇温室ローラー= ?,
                           浸炭室ローラー1 = ?,浸炭室ローラー2 = ?,
                           浸炭室ローラー3 = ?,降温室ローラー = ?,
                           油槽エレベータチェン = ?
                    WHERE 時間 = ? AND GOT_Number = ?;
               '''
        cursor.executemany(insert_query,value_list2)   
        conn.commit() 
    
        print("Record inserted successfully")

    except Exception as ex:
        print("Failed to insert into SQL table {}".format(ex))
        logger.error(f'insertdataFrameIntoTable: {ex}')

    finally:
            cursor.close()
            conn.close()
            print("MySQL connection is closed")

def on_changed(event):
    try:
        for directory_number in os.listdir(path):
            if directory_number[0:3] == 'No.':
                directory_path = os.path.join(path,directory_number)
                
                file_path = str(sorted(Path(directory_path).iterdir(), key=os.path.getmtime)[-1])
                    
                df = pd.read_csv(file_path,header=None, skiprows=13)
                df.columns = cols
                df = df.set_index('時間')        

                insertdataFrameIntoTable(df,directory_number)
    except Exception as ex:
        logger.error(f'on_changed: {ex}')
    
    finally:
        print('\nStill watching file changes to update SQL')
    

def main():
    #set watch dog
    patterns = ["*.csv","*.CSV"]                      
    ignore_patterns = ""                                                            
    ignore_directories = False                                                     
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    
    my_event_handler.on_modified = on_changed
    my_event_handler.on_created = on_changed
    my_event_handler.on_deleted = on_changed
    
    #Craete observer 
    go_recursively = True
    
    my_observer = Observer()
    #the observer will watch all CSV files in the path even in anotthe sub directory
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)
    my_observer.start()
   
    
if __name__ == '__main__':
    print('start insert data')
    main()
    input()
    exit()

      
    
    
    
    
    
    
