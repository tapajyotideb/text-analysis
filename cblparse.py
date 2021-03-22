#!/usr/bin/env python3

import pandas as pd
import re
import datetime
import time
import easygui

timestr = time.strftime("%Y%m%d-%H%M%S")

#Reading contents from the file
path = easygui.fileopenbox(msg=None, title="Select file", default='*', filetypes=None, multiple=False)
def filecontent(path):
    with open(path, 'r') as file:
        content = file.read().rstrip()
        lines = content.split('.')
        lines = [x for x in lines if x]
    return lines

lines = filecontent(path)

#Removing quotes from the csv file
def file_modify(filename):
    with open(filename, 'r+') as file:
        content = file.read()
        for ch in ['"','[',']']:
            if ch in content:
                content = content.replace(ch,'')
    with open(filename, 'w') as file:
        file.write(content)

#Intializing variables for parsing, used later to convert to dataframe
table_name, version_name, type_name, issorted, isduplicate, table_data, value_name, time_t = ([] for i in range(8))
counter = 0
for line in lines:
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
        vname = re.search('VALUES ARE \( (.*) \)', line)
        value_name.append(vname.group(1).replace("' '", "''"))
    except AttributeError:
        print("There is no such attribute. Check the file for Value field at index " + str(counter))

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
           "Timestamp": time_t, 
           "Value": value_name
           }

df = pd.DataFrame(summary)
df_summary = df.iloc[:,:-2]
print("\n--------------------------------SUMMARY FILE-----------------------------------\n\n")
print(df_summary)
print("\n\n")
#Export to csv file
csv_filename = "summary" + timestr + ".csv"
df_summary.to_csv(csv_filename, header=False, index=False)
csvmodify = file_modify(csv_filename)

####################################################################################
#Function for Code Generation Table
def code_table():
    df_type_code = df[df["Type"]=="CODE"]
    #df_type_code
    columns = ['Table Name', 'Value']
    df_type_code = pd.DataFrame(df_type_code, columns=columns)

    for index, row in df_type_code.iterrows():
        span = 2
        words = row.Value.split(" ")
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
    df_final = df_final[['Table Name', '1st', '2nd']]
    #print(df_final)
    return df_final

df_final = code_table()
#print("\nCODE TABLE GENERATOR\n\n")
#print(df_final)
#print("\n")

#Exporting to a COBOL file
filename = "code_table_generator" + timestr + ".cbl"
df_final.to_csv(filename, header=False, index=False)
csvmodify = file_modify(filename)

#Checking for duplicate rows in code table
duplicateRowsDF = df_final[df_final.duplicated(['Table Name', '1st'])]
print("We have " + str(len(duplicateRowsDF)) + " duplicate rows in code generation table. \n")
print(duplicateRowsDF)

####################################################################################
#Function for Edit Generation Table
def edit_table():
    df_type_edit = df[df["Type"] != "CODE"]
    columns = ['Table Name', 'Type', 'Value', 'Timestamp']
    df_type_edit = pd.DataFrame(df_type_edit, columns=columns)

    for index, row in df_type_edit.iterrows():
        span = 1
        words = row.Value.split(" ")
        row.Value = [",".join(words[i:i+span]) for i in range(0, len(words), span)]

    df_type_edit['Table Name'] = (df_type_edit['Table Name'].map(str) + " " + df_type_edit['Type'].map(str)).replace(' ', '-', regex=True)
    df_type_edit['Table Name'] = "88 " + df_type_edit['Table Name'] + " VALUES"
    df_type_edit.update(df_type_edit[['Value']].applymap('"{}"'.format))
    #print(df_type_edit)
    df_edit_final= df_type_edit['Timestamp'] + " " + df_type_edit['Table Name'] + " " + df_type_edit['Value'] + ".\n"
    return df_edit_final

df_edit_final = edit_table()
#print(df_edit_final)

#Exporting to a COBOL file
filename = "edit_table_generator" + timestr + ".cbl"
df_edit_final.to_csv(filename, header=False, index=False)
csvmodify = file_modify(filename)
