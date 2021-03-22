#!/usr/bin/env python3

import pandas as pd
import re

#Reading contents from the file
path = 'C:/Users/TapajyotiDeb/Desktop/table_1.txt'
def filecontent(path):
    with open(path, 'r') as file:
        content = file.read()
        lines = content.split('.')
        lines = [x for x in lines if x]
    return lines

lines = filecontent(path)

#Intializing variables for parsing, used later to convert to dataframe
table_name, version_name, type_name, issorted, isduplicate, table_data, value_name = ([] for i in range(7))

for line in lines:
   
    #for table name field
    try:
        tname = re.search('TABLE NAME IS (.*) VERSION', line)
        table_name.append(tname.group(1))
    except AttributeError: 
        print("There is no such attribute. Check the file for correct table name.")
    
    #for version field
    try:
        vname = re.search('VERSION IS (.*)', line)
        version_name.append(vname.group(1))
    except AttributeError: 
        print("There is no such attribute. Check the file for correct version.")
    
    #for type field
    try:
        tyname = re.search('TYPE IS (.*)', line)
        type_name.append(tyname.group(1))
        if tyname.group(1) == 'EDIT VALID':
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
                tbldata = (encodedata.group(1),decodedata.group(1))
                table_data.append(tbldata)            
    except AttributeError: 
        print("There is no such attribute. Check the file for correct type.")
        
    #for sorted/unsorted field
    try:
        sname = re.search('TABLE IS (.*)', line)
        issorted.append(sname.group(1))
    except AttributeError: 
        print("There is no such attribute. Check the file for correct table sorted/unsorted value.")
        
    #for whether duplicate values are allowed or not
    dname = re.search('DUPLICATES ARE (.*)', line)
    if dname == None:
        isduplicate.append("")
    elif dname.group(1) == 'NOT ALLOWED':
        isduplicate.append("NODUP")
    elif dname.group(1) == 'ALLOWED':
        isduplicate.append("DUP")
    
    #for values field
    vname = re.search('VALUES ARE \( (.*) \)', line)
    value_name.append(vname.group(1).replace("' '", "''"))

#Creating Dataframe 
summary = {
           "Table Name": table_name, 
           "Version": version_name, 
           "Type": type_name, 
           "Is_sorted": issorted, 
           "Duplicate": isduplicate, 
           "Datatype": table_data, 
           "Value": value_name
           }

df_summary = pd.DataFrame(summary)
print(df_summary)

#Export to csv file
#df_summary.to_csv("filename.csv")