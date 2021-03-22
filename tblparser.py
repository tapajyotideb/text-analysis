#!/usr/bin/env python3

import pandas as pd
import re, ntpath, time, shlex, datetime, warnings, os
import numpy as np
from ast import literal_eval
warnings.filterwarnings("ignore")
try:
    import easygui
except ModuleNotFoundError:
    print("A library is missing, please wait while it gets installed.\n")
    os.system("pip install easygui")
    print("Library installed sucessfully.\n")
    import easygui

timestr = time.strftime("%Y%m%d-%H%M%S")

#Reading contents from the file
path = easygui.fileopenbox(msg=None, title="Select file", default='*', filetypes=None, multiple=False)
outname = ntpath.basename(path).replace(".txt", "")
def filecontent(path):
    #checking for possible unnecessary 8 digit numbers in each line
    with open(path, 'r') as file:
        content = file.readlines()
        for line in content:
            line = line.rstrip()
            a = re.findall(r"\D(0000\d{4})\D", " "+line+" ")
            if a:
                a = "".join(a)
                line = line.replace(a, "").rstrip()
            with open("temp.txt", 'a') as f:
                f.write(line + "\n")

    #splitting the txt based on a delimiter
    with open("temp.txt", 'r') as file:
        content = file.read().rstrip()
        lines = content.split('.')
        lines = [x for x in lines if x]
    os.remove("temp.txt")
    return lines

lines = filecontent(path)

#Removing quotes from the csv file
def file_modify(filename, a=None):
    with open(filename, 'r+') as file:
        content = file.read()
        for ch in ['"','[',']']:
            if ch in content:
                content = content.replace(ch,'')
        if "\n\n" in content:
            content = content.replace("\n\n", "\n")
        if a:
            content = content.replace(",", "")
    with open(filename, 'w') as file:
        file.write(content)

#Checking for duplicate rows in code table
def check_dup(f):
    duplicateRowsDF = f[f.duplicated(['Table Name', '1st'])]
    print("We have " + str(len(duplicateRowsDF)) + " duplicate rows in code generation table. \n")
    print(duplicateRowsDF)

#Intializing variables for parsing, used later to convert to dataframe
table_name, version_name, type_name, issorted, isduplicate, table_data, value_name, time_t, search_type = ([] for i in range(9))
counter = 0
print("\n--------------------------------WARNINGS/ERRORS------------------------------------\n\n")
for line in lines:
    if '*+' in line: #removing comment symbols
        line.replace('*+', "  ")
    #for table name field
    try:
        tname = re.search('TABLE NAME IS (.*) VERSION', line)
        table_name.append(tname.group(1))
    except AttributeError: 
        print("There is no such attribute. Check the file for correct table name at index " + str(counter))
        table_name.append("NaN")
    
    #for version field
    try:
        vname = re.search('VERSION IS (.*)', line)
        version_name.append("Version " + vname.group(1))
    except AttributeError: 
        print("There is no such attribute. Check the file for correct version at index " + str(counter))
        version_name.append("NaN")
    
    #for type field
    try:
        tyname = re.search('TYPE IS (.*)', line)
        if tyname.group(1) in ['EDIT VALID', 'EDIT INVALID', 'CODE']:        
            type_name.append(tyname.group(1))
        else:
            print("There is no such attribute. Check the file for correct type at index " + str(counter))
            type_name.append("NaN")
        if tyname.group(1) in ['EDIT VALID', 'EDIT INVALID']:
            #for alphanumeric field incase of EDIT VALID
            tbldata = re.search('TABLE DATA IS (.*)', line)
            if tbldata == None:
                table_data.append("")
            else:
                table_data.append(tbldata.group(1))
        elif tyname.group(1) == 'CODE':
            encodedata = re.search('ENCODE DATA IS (.*)', line)
            decodedata = re.search('DECODE DATA IS (.*)', line)
            if encodedata and decodedata == None:
                table_data.append("")
            else:
                tbldata = ",".join((encodedata.group(1),decodedata.group(1)))
                table_data.append(tbldata)   
        else:
            print("There is no such attribute. Check the file for correct datatype at index " + str(counter))
            table_data.append("NaN")                        
    except AttributeError: 
        print("There is no such attribute. Check the file for correct type & datatype at index " + str(counter))
        type_name.append("NaN")
        table_data.append("NaN")            
        
    #for sorted/unsorted field
    try:
        sname = re.search('TABLE IS (.*)', line)
        if sname.group(1) in ['SORTED', 'UNSORTED']:
            issorted.append(sname.group(1))
        else:
            print("There is no such attribute. Check the file for correct table sorted/unsorted value at index " + str(counter))
            issorted.append("NaN")
    except AttributeError: 
        print("There is no such attribute. Check the file for correct table sorted/unsorted value at index " + str(counter))
        issorted.append("NaN")        

    #for whether duplicate values are allowed or not
    try:
        dname = re.search('DUPLICATES ARE (.*)', line)
        if dname == None:
            isduplicate.append("")
        elif dname.group(1) == 'NOT ALLOWED':
            isduplicate.append("NODUP")
        elif dname.group(1) == 'ALLOWED':
            isduplicate.append("DUP")
    except AttributeError:
        print("There is no such attribute. Check the file for duplicate field at index " + str(counter))
    
    #for values field
    try:
        vname = re.search('VALUES ARE \( (.*) \)', line, flags=re.DOTALL)
        temp1 = vname.group(1).replace("' '", "''")
        temp2 = ' '.join(map(str.strip, temp1.split("\n")))
        value_name.append(temp2)
    except AttributeError:
        print("There is no such attribute. Check the file for Value field at index " + str(counter))

   #for searchtype field
    try:
        temp = re.search('SEARCH IS (.*)', line)
        if "BINARY" in temp.group(1):
            search_type.append("BIN")
        elif "LINEAR" in temp.group(1):
            search_type.append("LIN")
    except AttributeError:
        print("There is no such attribute. Check the file for Value field at index " + str(counter))
        search_type.append("NaN")

    #for timestamp
    try:
        time_t.append("      * Table generated at " + str(datetime.datetime.now()) + "\n\t   ")
    except AttributeError: 
        print("There is no such attribute. Check the code for correct code syntax or OS for time.")

    counter += 1

#Creating Dataframe 
summary = {
           "Table Name": table_name, 
           "Version": version_name, 
           "Type": type_name, 
           "Is_sorted": issorted, 
           "Duplicate": isduplicate, 
           "Datatype": table_data,
           "Searchtype": search_type,
           "Timestamp": time_t, 
           "Value": value_name
           }

df = pd.DataFrame(summary)
df['Datatype'] = df['Datatype'].str.replace('ALPHANUMERIC','X')
df['Datatype'] = df['Datatype'].str.replace('NUMERIC','9')
df["Is_sorted"].replace({"SORTED": "Y", "UNSORTED": "N"}, inplace=True)
df_summary = df.iloc[:,:-2]
print("\n--------------------------------SUMMARY FILE-----------------------------------\n\n")
print(df_summary)
print("\n\n")
#Export to csv file
csv_filename = outname + "_summary" + ".csv"
df_summary.to_csv(csv_filename, header=False, index=False)
csvmodify = file_modify(csv_filename)

####################################################################################
#Function for Code Generation Table
def code_table():
    df_type_code_orig = df[df["Type"]=="CODE"]
    #df_type_code
    columns = ['Table Name', 'Value']
    df_type_code = pd.DataFrame(df_type_code_orig, columns=columns)

    for index, row in df_type_code.iterrows():
        span = 2
        words = shlex.split(row.Value, posix = False)
        row.Value = [",".join(words[i:i+span]) for i in range(0, len(words), span)]
    
    df_type_code['Index'] = df_type_code.index
    df_temp = (pd.DataFrame({'Table Name': list(df_type_code['Table Name']),
                    'Value': list(df_type_code['Value']),
                       'Index': list(df_type_code['Index'])})
      .set_index(['Index', 'Table Name']))

    temp = df_temp.explode('Value')
    temp.reset_index(inplace=True, level=1)
    df_new = temp[['Table Name', 'Value']]

    df_final = pd.concat([df_new, df_new['Value'].str.split(',', expand=True)], axis=1)
    df_final = df_final.drop(df_final.columns[[1]], axis=1)
    df_final.columns = ['Table Name', '1st', '2nd']
    df_final.reset_index(inplace=True)
    df_final['type'] = 'C'
    df_final['blank'] = ''
    df_final['zero'] = '0'
    columns = ['Table Name', 'type', '1st', 'zero', 'Table Name', 'type', '2nd', 'blank']
    df_final = df_final[columns]

    temp1 = df_type_code_orig["Searchtype"] + "," + df_type_code_orig['Is_sorted'] + "," + df_type_code_orig['Datatype'] + ","
    temp1 = pd.DataFrame(temp1, columns=['one'])
    temp2 = df_type_code['Value'].to_frame()

    temp = pd.concat([temp1, temp2], axis=1, ignore_index=True)
    temp.columns = ['one', 'two']

    df2 = temp.explode('two')
    df_final2 = pd.concat([df2, df2['two'].str.split(',', expand=True)], axis=1)
    df_final2 = df_final2.drop(df_final2.columns[[1]], axis=1)
    df_final2.columns = ['Name', '1st', '2nd']
    df_final2.reset_index(inplace=True)
    df_final2 = df_final2[['Name']]
    result = pd.concat([df_final, df_final2], axis=1)
    
    result_f1 = result.iloc[:, :3]
    result_f11 = result_f1[['Table Name', 'type', '1st']].apply(lambda x: ''.join(x), axis=1).to_frame()
    result_f2 = result.iloc[:,3:7]
    result_f22 = result_f2[['zero', 'Table Name', 'type', '2nd']].apply(lambda x: ''.join(x), axis=1).to_frame()
    result_f3 = result.iloc[:,-1:]

    final_result = pd.concat([result_f11,result_f22,result_f3], axis=1) 
    final_result.columns = ['col1', 'col2', 'col3']
    for i, col in enumerate(final_result.columns):
        final_result.iloc[:, i] = final_result.iloc[:, i].str.replace("'", '')
    final_result["col1"]= final_result["col1"].str.pad(43, side ='right', fillchar =' ')
    final_result["col2"]= final_result["col2"].str.pad(74, side ='right', fillchar =' ') 
    return result

#print("\nCODE TABLE GENERATOR\n\n")
#print(df_final)
#print("\n")

####################################################################################
#Function for Edit Generation Table
def edit_table():
    df_type_edit_orig = df[df["Type"] != "CODE"]
    columns = ['Table Name', 'Type', 'Value', 'Timestamp']
    df_type_edit = pd.DataFrame(df_type_edit_orig, columns=columns)

    for index, row in df_type_edit.iterrows():
        span = 1
        words = row.Value.split(" ")
        row.Value = [",".join(words[i:i+span]) for i in range(0, len(words), span)]

    df_type_edit['Table_Name'] = (df_type_edit['Table Name'].map(str) + " " + df_type_edit['Type'].map(str)).replace(' ', '-', regex=True)
    df_type_edit['Table_Name'] = "88 " + df_type_edit['Table_Name'] + " VALUES"
    df_type_edit['new_row'] = "01 " + df_type_edit['Table Name'] + "-WORK PIC X(??).\n\t   "
    df_type_edit.update(df_type_edit[['Value']].applymap('"{}"'.format))
    df_type_edit.reset_index(inplace=True)
    #print(df_type_edit)

    df_type_edit['Type2'] = 'E'
    #conditions = [df['Type'] == 'EDIT VALID', df['Type'] == 'EDIT INVALID']
    #outputs = ['VA', 'IN']
    #df_type_edit['other'] = np.select(conditions, outputs)
    aa = df_type_edit[['Table Name', 'Type', 'Type2', 'Value']]
    def label(row):
        if row['Type'] == "EDIT VALID" :
            return 'VAL'
        elif row['Type'] == "EDIT INVALID":
            return 'INV'
        else:
            return "ERROR"
    aa['label'] = aa.apply (lambda row: label(row), axis=1)
    aa['Value'] = aa['Value'].str.replace(r"[\"]", '').apply(literal_eval)
    
    df_temp = aa['Table Name'] + "," + aa['Type2'] + ","
    df_final = pd.concat([df_temp, aa['Value']], axis=1)
    df_final.columns = ['name', 'val']
    #df_final['val'] = df_final['val'].str.pad(34, side ='right', fillchar =' ')

    qq = df_final.explode('val')
    qq['blank'] = '0'
    qq['blank'] = qq['blank'].str.pad(71, side ='right', fillchar =' ')
    qq['val'] = qq['val'].str.pad(34, side ='right', fillchar =' ')
    qq = qq['name'] + qq['val'] + "," + qq['blank'] + ",,,"
    qq.reset_index(inplace=True, drop=True)
    qq.to_frame()

    temp1 = "   " + df_type_edit_orig['Is_sorted'] + "," + df_type_edit_orig['Datatype'] + " " 
    temp1.reset_index(inplace=True, drop=True)
    temp1 = aa['label'] + "," + temp1
    temp1.reset_index(inplace=True, drop=True)

    temp = df_final['val'].to_frame()
    temp = pd.concat([temp1, temp], axis=1, ignore_index=True)
    temp.columns = ['Name', 'two']

    df2 = temp.explode('two')
    df_final2 = pd.concat([df2, df2['two'].str.split(',', expand=True)], axis=1)
    df_final2 = df_final2.drop(df_final2.columns[[1]], axis=1)
    df_final2.columns = ['Name', '2nd']
    df_final2.reset_index(inplace=True)
    df_final2 = df_final2[['Name']]
    result = pd.concat([qq, df_final2], axis=1)
    result = result.rename(columns = {0:'col1'})

    """temp_list = []
    def prepend(list, str): 
        str = "\t\t" + str + '{0},,\n'
        list = [str.format(i) for i in list] 
        list = ''.join(list)
        return(list) 
    for item1, item2 in zip(df_final['name'],df_final['value']):
        temp_list.append(prepend(item2, item1))"""
        
    df_edit_final= df_type_edit['Timestamp'] + " " + df_type_edit['new_row'] + " " + df_type_edit['Table_Name'] + " " + df_type_edit['Value'] + ".\n\n"
    return (df_edit_final, result)

vals =  df_summary.Type.unique()

if len(vals) == 1 and "CODE" in vals:
    df_final = code_table()
    #Exporting to a COBOL file
    filename = outname + "_code_" + timestr + ".tbl"
    df_final.to_csv(filename, header=False, index=False)
    file_modify(filename,1)
    check_dup(df_final)

elif "CODE" not in vals:
    df_edit_final = edit_table()
    #Exporting to a COBOL file
    filename = outname + "_" + timestr + ".cbl"
    df_edit_final[0].to_csv(filename, header=False, index=False)
    file_modify(filename)
    filename = outname + "_edit_" + timestr + ".tbl"
    df_edit_final[1].to_csv(filename, header=False, index=False)
    file_modify(filename,1)

else:
    df_edit_final = edit_table()
    #Exporting to a COBOL file
    filename = outname + "_" + timestr + ".cbl"
    df_edit_final[0].to_csv(filename, header=False, index=False)
    file_modify(filename,1)
    filename = outname + "_edit_" + timestr + ".tbl"
    df_edit_final[1].to_csv(filename, header=False, index=False)
    file_modify(filename,1)

    df_final = code_table()
    #Exporting to a COBOL file
    filename = outname + "_code_" + timestr + ".tbl"
    df_final.to_csv(filename, header=False, index=False)
    file_modify(filename,1)
    check_dup(df_final)


