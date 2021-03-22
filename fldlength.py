import pandas as pd
import glob, os, codecs, csv
import re, ntpath
try:
    import easygui
except ModuleNotFoundError:
    os.system("pip install easygui")
    import easygui

text = easygui.fileopenbox(msg=None, title="Select file", default='*', filetypes='*', multiple=False)
outname = ntpath.basename(text).replace(".txt", "")

def rm_zero_dots(df): #fix rows having 0 as column value
    newRows = []
    last_val_is_zero = False
    tempRow = None
    for row in df.iterrows():
        vals = row[1]
        if vals['column'] == 0:
            if not last_val_is_zero:
                vals['row'] = vals['row'] - 1
                vals['column'] = vals['column'] + vals['length_of_field']
                tempRow = vals
                last_val_is_zero = True
            else:
                tempRow['length_of_field'] = tempRow['length_of_field'] + vals['length_of_field']
        else:
            if tempRow is not None:
                newRows.append(tempRow)
            newRows.append(vals)
            tempRow = None
            last_val_is_zero = False

    if tempRow is not None:
        newRows.append(tempRow)
        
    newData = [[val for val in row] for row in newRows]
    newDf = pd.DataFrame(newData, columns=['map_name', 'row', 'column', 'length_of_field'])
    return newDf

def second_index(pattern):
    i = -1
    for j in range(2):
        i = x.index(pattern, i + 1)
    return i

def sort_with_length(file_name):
    return len(file_name)

def housekeeping(oname):
    extension = 'csv'
    all_filenames = [i for i in glob.glob('table_*.{}'.format(extension))]
    my_files = sorted(all_filenames, key = sort_with_length)
    header_saved = False
    with codecs.open(oname + "_.csv",'w', "UTF-8", 'ignore') as file_out:
        for filename in my_files:
            with codecs.open(filename, 'r', 'UTF-8', 'ignore') as file_in:
                header = next(file_in)
                if not header_saved:
                    file_out.write(header if "\n" == header[-1] else header + "\n")
                    header_saved = True
                for line in file_in:
                    file_out.write(line if "\n" == line[-1] else line + "\n")                
    for f in my_files:
        os.remove(f)

pattern=" " + "*"*132
map_names = []
with open(text,'r') as file:
    content = file.readlines()
    for line in content:
        if "REPORT FOR MAP" in line:
            mname = re.search('0REPORT FOR MAP (.*) VERSION', line)
            map_names.append(mname.group(1).replace(" ", ""))
with open(text,'r') as file:
    content = file.read()
    lines = content.split("0REPORT FOR MAP")
    lines = [x for x in lines if x]

for count in range(len(lines)):
    x = lines[count].split("\n")[3:]
    ind = second_index(pattern)

    nlist = x[1:ind]
    nlist = [a for a in nlist if "(CURSOR)" not in a]

    buf1 = []
    buff_for_df = []
    for items in nlist:
        search_return = re.findall(r"(\.+)", items)   
        if search_return:
            buf1.append(",".join([str(len(i)) for i in search_return]))
            buff_for_df.append([len(i) for i in search_return])

    buf2 = []
    ind = []
    for index, line in enumerate(nlist):
        if '.' in line:
            buf2.append(line)
            ind.append(index+1)

    row2 = []
    subrow = []
    for item1, item2 in zip(buf1,buf2):
        if ',' not in item1:
            row2.append(len(item2.split('.')[0])-1)
        elif ',' in item1:
            temp1 = len(item2.split('.')[0])-1
            subrow.append(temp1)
            temp2 = item1.split(",")
            counter = 0
            for i in range(0, len(temp2)-1):
                counter += int(temp2[i])
                temp1 +=  int(temp2[i]) + len(item2.split('.')[counter])
                subrow.append(temp1)
            row2.append(subrow)
            subrow = []
    df1 = pd.DataFrame(ind, columns=['row1'])
    df2 = pd.DataFrame(zip(row2), columns=['row2'])
    df3 = pd.DataFrame(zip(buff_for_df), columns=['num_of_dots'])
    df4 = pd.concat([df1,df2], axis=1)
    df5 = pd.concat([df1,df3], axis=1)
    new_rows1 = df4.explode('row2')
    new_rows2 = df5.explode('num_of_dots')
    final_df = pd.concat([new_rows1, new_rows2.iloc[:, -1:]], axis=1)
    final_df['map_name'] = map_names[count]
    cols = ['map_name', 'row1', 'row2', 'num_of_dots']
    final_df = final_df[cols]
    final_df.rename(columns = {'row1':'row', 'row2':'column', 'num_of_dots':'length_of_field'}, inplace = True) 
    final_df = rm_zero_dots(final_df)
    final_df['pos'] = list(zip(final_df.row,final_df.column))
    final_df['pos'] = final_df['pos'].astype(str)
    final_df['pos'] = final_df['pos'].str.replace(" ", "")
    filename = "table_" + str(count) + ".csv"
    final_df.to_csv(filename, index=False)

housekeeping(outname)