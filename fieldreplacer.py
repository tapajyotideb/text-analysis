import os, fileinput, time
from glob import glob
import pandas as pd
try:
    import easygui
except ModuleNotFoundError:
    os.system("pip install easygui")
    import easygui

def complete_fldr():
    print("\nChoose the csv file in the prompt(please minimize all windows to find the prompt): ")
    time.sleep(2)
    path = easygui.fileopenbox(msg=None, title="Select csv file", default='*.csv', filetypes='*.csv', multiple=False)
    df = pd.read_csv(path)
    prompt = input("\nDo you want to change fields in a single file or a folder. Reply file/folder:  ")

    def replacer(filename):
        with fileinput.FileInput(filename, inplace=True) as file:
                counter = 0
                for line in file:
                    if "MP00-MAP-MOVES-IN." in line:
                        counter += 1
                    for index, item in enumerate(df['IDMSname']):
                        if (item in line) and counter < 1:
                            if pd.isna(df['CopyName'][index]) == False:
                                line = line.replace(item, df['CopyName'][index])
                            else:
                                pass     
                        elif (item in line) and counter > 0:
                            if pd.isna(df['StructName'][index]) == False:
                                line = line.replace(item, df['StructName'][index])
                            else:
                                pass
                    print(line, end='')

    if prompt.lower() == "file":
        path = easygui.fileopenbox(msg=None, title="Select file", default='*', filetypes=None, multiple=False)
        replacer(path)
    elif prompt.lower() == "folder":
        root_dir = easygui.diropenbox(msg=None, title="Select folder", default='*')
        os.chdir(root_dir)
        for filename in glob('*.cbl'):
            replacer(filename)
    else:
        print("\n Your input is incorrect. Please input either 'file' or 'folder'.\n")