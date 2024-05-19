
import pygsheets
import pandas as pd
#https://medium.com/game-of-data/play-with-google-spreadsheets-with-python-301dd4ee36eb

gc = pygsheets.authorize(service_file="D:\linebot\prime-victory-423614-n1-693ab773933f.json")
sht = gc.open_by_url(
'https://docs.google.com/spreadsheets/d/1f3bU44K7SQCFSV6TX48V4dNqQiyWIQA7-kWsIy9xmc0/edit#gid=0'
)
#wks_list = sht.worksheets()
wks = sht[0]

#A1 = wks.cell('A1')
#print(A1.value)
#titles_list=wks.get_values(start='A1', end='D1')[0]
#if titles_list==['']*len(titles_list):
#    wks.update_values('A1', [['購入時間', '食物名稱', '數量', '單位']])
#print(wks.get_values(start='A1', end='D1'))
#print(type(wks.get_all_records()))
#print(wks.get_named_ranges('食物名稱'))
#df = pd.DataFrame(wks.get_all_records())
#wks.get_as_df()

#wks.set_dataframe(df, 'A1') #從欄位 A1 開始
 
# Update即時
#wks.update_value((1,5), "test_A2")
def login_sheet():
    gc = pygsheets.authorize(service_file="D:\linebot\prime-victory-423614-n1-693ab773933f.json")
    sht = gc.open_by_url(
    'https://docs.google.com/spreadsheets/d/1f3bU44K7SQCFSV6TX48V4dNqQiyWIQA7-kWsIy9xmc0/edit#gid=0'
    )
    wks = sht[0]
    return wks

def check_column_title(wks):
    titles_list=wks.get_values(start='A1', end='D1')[0]
    if titles_list==['']*len(titles_list):
        wks.update_values('A1', [['購入時間', '食物名稱', '數量', '單位']])
        titles_list=wks.get_values(start='A1', end='D1')[0]
    return titles_list

def get_names_and_units(wks,titles_list):
    row_data_dict_in_list=wks.get_all_records()
    dates_list,names_list,units_list,storage_list=list(),list(),list(),list()
    for index, row_data_dict in enumerate(row_data_dict_in_list):
        dates_list.append(row_data_dict[titles_list[0]])
        names_list.append(row_data_dict[titles_list[1]])
        storage_list.append(row_data_dict[titles_list[2]])
        units_list.append(row_data_dict[titles_list[3]])
    return dates_list,names_list,storage_list,units_list

def update_all_name_and_count_and_unit(wks,titles_list,new_data):
    row_data_dict_in_list=wks.get_all_records()
    food_time,food_name,food_count,food_unit=new_data
    name_and_unit_pair_list=list()
    names_list,units_list,stroge_list=list(),list(),list()
    for index, row_data_dict in enumerate(row_data_dict_in_list):
        names_list.append(row_data_dict[titles_list[1]])
        stroge_list.append(row_data_dict[titles_list[2]])
        units_list.append(row_data_dict[titles_list[3]])
    mode='write'
    write_into_row_index=0
    for name,unit in zip(names_list,units_list):
        write_into_row_index=write_into_row_index+1
        if name==food_name and unit==food_unit:
            mode='update'
            break
    print(mode,write_into_row_index)
    if mode =='write':
        write_into_row_index=len(row_data_dict_in_list)
        wks.update_values((write_into_row_index+2,1), [[food_time, food_name, food_count,food_unit]])
    elif mode=='update':
        current_stroge=float(stroge_list[write_into_row_index-1])
        if current_stroge+float(food_count)<=0:
            if write_into_row_index!=len(row_data_dict_in_list):
                wks.update_values_batch([(write_into_row_index+1,1), (len(row_data_dict_in_list)+1,1)], [[[row_data_dict_in_list[-1][titles_list[0]], row_data_dict_in_list[-1][titles_list[1]], row_data_dict_in_list[-1][titles_list[2]], row_data_dict_in_list[-1][titles_list[3]]]], [['', '', '', '']]])       
            else:
                wks.update_values((write_into_row_index+1,1), [['', '', '', '']])       
        else:
            wks.update_values((write_into_row_index+1,1), [[food_time, food_name, current_stroge+float(food_count)]])
    row_data_dict_in_list=wks.get_all_records()
    print('row_data_dict_in_list',row_data_dict_in_list)
    '''
    for index, row_data_dict in row_data_dict_in_list:
        if food_name==row_data_dict[titles_list[1]] and food_unit==row_data_dict[titles_list[3]]:
            current_stroge=float(row_data_dict[titles_list[2]])
            if current_stroge-food_count<=0:
                wks.update_values_batch([(index+2,1), (len(row_data_dict_in_list)+2,1)], [[[row_data_dict_in_list[-1][titles_list[0]], row_data_dict_in_list[-1][titles_list[1]], row_data_dict_in_list[-1][titles_list[2]], row_data_dict_in_list[-1][titles_list[3]]]], [['', '', '', '']]])       
            else:
                wks.update_values((index+2,1), [[row_data_dict_in_list[-1][titles_list[0]], row_data_dict[titles_list[1]], current_stroge, row_data_dict[titles_list[3]]]])
            break
    '''
'''
worksheet=login_sheet()
titles=check_column_title(worksheet)
print(titles)
#names,units=get_names_and_units(worksheet,titles)
#print(names,units)'''