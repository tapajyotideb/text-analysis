import fileinput
import re, ntpath
import pandas as pd

def replace_all(text, d):
    for i, j in d.items():
        text = text.replace(i, j)
    return text

df = pd.read_excel("C:/Users/TapajyotiDeb/Downloads/***** mapping.xlsx")
path = "C:/Users/TapajyotiDeb/Desktop/NYL-239/******-RP-ENTER - Source code.txt"

with open(path, 'r') as f:
    lines = f.readlines()

for index, line in enumerate(lines):
    if "ELSE" in line:
        match = line.split("ELSE")[0].count(" ")
        if "END" not in (lines[index-1]):
            ind = index
lines.insert(ind, " "*match + "END")

spaces = '    '
indent = 0
output = []
for line in lines:
    line = line.strip()
    if line.startswith('IF '):
        o = (indent * spaces) + line
        indent = indent + 1
        output.append(o)
    elif line.startswith('ELSE'):
        o = (indent * spaces) + line
        indent = indent + 1
        output.append(o)
    elif line.startswith('END'):
        indent = indent - 1
        o = (indent * spaces) + line
        output.append(o)
    else:
        o = (indent * spaces) + line
        output.append(o)

with open(path, "w") as file:
    for o in output:
        file.write(" "*11 + o + "\n")

with open(path, "r") as file:
    content = file.readlines()
    for index, line in enumerate(content):
        if "ELSE" in line:
            if "END" in (content[index-1]):
                content.pop(index-1)
        if  line.strip() == "THEN DO.":
            content.pop(index)
        if line.strip() == "DO.":
            content.pop(index)
content = ''.join(content)
if "DO." in content:
    content = content.replace("DO.", "")
if "END." in content:
    content = content.replace("END.", "END-IF")    
with open(path, "w") as file:
    file.write(content)


#----------------------------------------------------------------------------------------------#

d = { " EQ ": " = ", " NE ": " NOT = ", " GT ": " > ", " GE ": " >= ", " LT ": " < ", " LE ": " <= ", "NEXT": "CONTINUE"}
with fileinput.FileInput(path, inplace=True) as file:
    for line in file:
        line = replace_all(line, d) 
        if ("SUBSTR(" in line) and line.count(',')>1:       
            m = re.search(r'\((.*?)\)',line).group(1)
            comma_index = [x for x, v in enumerate(line) if v == ',']
            if (m.count(',') == 2):
                line = list(line)
                line[comma_index[0]] = '('
                line[comma_index[1]] = ':'
                line = "".join(line)
                line = line.replace("SUBSTR(", "")
        print(line, end='')

with open(path, 'r') as file:
    lines = file.readlines()
    
map_index = []
forfield_index = []
display_index = []

str1 = "MOVE -1                  TO "
str2 = "MOVE "
str21 = "      TO CSSC-MESSAGE\n"
str3 = "MOVE ***NIMD            TO "
str31 = "MOVE ***MFSE            TO "
str32 = "MOVE ***MASK            TO "

for n, l in enumerate(lines): 
    if 'MODIFY MAP TEMP CURSOR AT' in l:
        if '!*' not in lines[n]:
            match = lines[n].split("MODIFY")[0].count(" ")
            map_index.append(n)
            counter = 0
            if '!*' not in lines[n]:
                fldname = re.search("MODIFY MAP TEMP CURSOR AT FIELD (.*)\n", lines[n]).group(1)
                counter += 1
                lines[n] = " "*6 + "*" + " "*(match-6) + lines[n].lstrip()
            continue
    if 'FOR FIELD' in l:
        if '!*' not in lines[n]:
            match = lines[n].split("FOR")[0].count(" ")
            forfield_index.append(n)
            forname = re.search("FOR FIELD " + fldname + "(.*).\n", lines[n]).group(1)
            counter += 1
            lines[n] = " "*6 + "*" + " "*(match-6) + lines[n].lstrip()
        continue
    if 'DISPLAY MSG TEXT' in l:
        if '!*' not in lines[n]:
            match = lines[n].split("DISPLAY")[0].count(" ")
            display_index.append(n)
            if counter > 0:
                for index, item in enumerate(df['Function']):
                    if item in fldname:
                        lines.insert(n+1, " "*match + str1 + df['OLPMF'][index][:-1]+"L\n")
                        break

                dispname = re.search("DISPLAY MSG TEXT (.*).\n", lines[n]).group(1)        
                if dispname:
                    lines.insert(n+2, " "*match + str2 + dispname + str21)
            
            if counter > 1:
                if ("ATTR" in forname) and ("BRIGHT" in forname) and ("UNPROT" not in forname):
                    lines.insert(n+3, " "*match + str3 + df['OLPMF'][index] + "\n")
                elif ("ATTR" in forname) and ("BRIGHT" in forname) and ("UNPROT" in forname):
                    lines.insert(n+3, " "*match + str31 + df['OLPMF'][index] + "\n")                    
                elif ("ATTR" in forname) and ("SKIP" in forname):
                    lines.insert(n+3, " "*match + str32 + df['OLPMF'][index] + "\n")
            lines[n] = " "*6 + "*" + " "*(match-6) + lines[n].lstrip()
                    
lines = "".join(lines)
with open("expected.txt", 'w') as f:
    f.write(lines)        
