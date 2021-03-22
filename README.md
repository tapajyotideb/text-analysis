<!-- PROJECT LOGO -->
<br />
<p align="center">
 <!-- <a href="https://github.com/vikkante/idmstools"> -->
      <img src="images/logo.jpg" alt="Logo" width="80" height="80">
  </a>

  <h2 align="center">IDMS Scripts</h2>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li>
	  <a href="#usage">Usage of scripts</a>
	  <ul>
	    <li><a href="#adsa">adsa_parse.py</a></li>
		<li><a href="#adsc">adsc_parse.py</a></li>
        <li><a href="#fldlength">fldlength.py</a></li>
        <li><a href="#mapconverter">mapconverter.py</a></li>
		<li><a href="#tblparser">tblparser.py</a></li>
      </ul>
	</li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

Check if python3 is installed in your system by typing in your terminal. The version should be 3.4+
* python3
  ```sh
  python --version
  ```


### Installation

1. Clone the repo
 
2. Make sure you have all the python libraries installed which are mentioned in the <b>Requirements.txt</b> in the <i>scripts</i> folder after you clone the repo. Use <b><i>pip install "library"</i></b> to install any missing ones.


<!-- USAGE EXAMPLES -->
## Usage

1. <h3 id="adsa">adsa_parse.py</h3>
   This script is used to generate csv files like - <b><i>tasks, global records, functions, responses and valid responses</i></b> from    	ADSA file. These 5 csv files will then be converted into excel sheets onto a single excel(<b>out.xlsx</b>) file.
	<br />
-  Input file:   <br /><br />
   Usage:<br />
   
    ```sh
    python adsa_parse.py
    ```
   You will be prompted to enter the absolute path for the ADSA file. <br /><br />
   <img src="images/adsa.jpg" width="700" height="90">
   <br />
   Once you enter the absolute path, one folder named <i><b>output</b></i> will be created in the directory from where the script is    	running. In that all the 5 csv files will be present.
	The combined excel file <b><i>out.xlsx</i></b> along with a <i><b>adsa_records.cbl & dlgs.txt</b></i> file will be present in   	the directory of the script, not in the output folder. 
   
2. <h3 id="adsc">adsc_parse.py</h3>
   This script is used to generate csv files like - <b><i>dialog map schema, adsc records, processes/modules</i></b> and <b><i>proc    		folder</i></b> containing code for each process from ADSC file. These csv files will then be converted into excel sheets 		onto a single excel(<b>out.xlsx</b>) file.
   <br /><b>N.B.</b> It is necessary to run the adsa_parse script before running adsc_parse script.
   <br /><br />
-  Input file:   <br /><br />
   Usage:<br />
   
    ```sh
    python adsc_parse.py
    ```
    You will be prompted to enter the absolute path for the ADSC file. 
	<br /><br />
   <img src="images/adsc.jpg" width="700" height="90">
   <br />
    Once you enter the absolute path, in a folder named <i><b>output</b></i> present in the directory from where the script is running,   	one file named processes.csv will be created. This file will be converted to an excel sheet in the earlier created
    <b><i>out.xlsx</i></b> along with <i><b>adsc_records.cbl</b></i> file which will be present in the directory of the script, not in   	the output folder. The adsc_records.cbl file will then be merged with adsa_records.cbl file and ultimately we will have a   		combined <b>RECS</b> file.
	One additional MAPS file will also be generated.

3. <h3 id="fldlength">fldlength.py</h3>
   This script is meant for generating the length of fields from MAPI file. The output will consist of map name, row, column, length of      	field and position. This output of this script can be an additional input argument to the mapconverter script if required.</i><br />
   <br />
-  Input file: ...MAPI.txt  <br /><br />   
   ```sh
   python fldlength.py
   ```
   A pop-up screen will apear to select the MAPI file. Please select the appropiate file. The output will be generated in the folder 	   	from where the script is running.
	

4. <h3 id="mapconverter">mapconverter.py</h3>
   This script is meant for generating the BMS macros from decompiled ADSO MAP. The output will consist of .bms and .cbl files. ADSO map             	file should be for only one map at a time. 
   <br /><i>Except for idd-tables option, in rest of the cases, after the macros are generated you will be asked to select a csv for                     	     replacing some fields and then enter file/folder to apply accordingly.</i>
   <br /><br />
-  Input file: ...MAPT.txt  <br /><br />
   Usage: (The arguments in [ ] are optional.) 
   
   ```sh
	mapconverter.py [-h] -i MAP_FILE [-o BMS_FILE] [-f CSV_FILE] [--log-level LOG_LEVEL] [--idd-tables]
   ```
	
   If you want to generate macros - 
   ```sh
   mapconverter.py -i MAP_FILE C:\Users\TD\Desktop\idmstools\data\OLTR\OLTRMAPDE.txt
   ```
   <img src="images/pic2.jpg" width="490" height="250"> &nbsp; <img src="images/csv.jpg" width="370" height="250">
	
   If you simply want to get the list of idd tables, add <b>--idd-tables</b> at the end.
    ```sh
    mapconverter.py -i MAP_FILE C:\Users\TD\Desktop\idmstools\data\OLTR\OLTRMAPDE.txt --idd-tables
    ```
   There may be a scenario where the generated files may contain <b>'??'</b> as field length. In such a case, we need to pass appropiate   	csv file containing field lengths, with <b>-f</b> parameter for length calculation.
    ```sh
    mapconverter.py -i MAP_FILE C:\Users\TD\Desktop\idmstools\data\OLTR\OLTRMAPDE.txt -f C:\Users\TD\Desktop\a.csv
    ```
	
5. <h3 id="tblparser">tblparser.py</h3>
   This script is used to generate .tbl files and .cbl files from IDD tables dataset. The dataset has to be in this format(Check the     	dataset for whitespaces, comment-symbols and remove them.)
	<br />
   Usage:
    ```sh
    python tblparser.py
    ```
   And select the appropiate dataset from the popup. The dataset should not contain '\*+', whitespaces and other items as shown in the    	image below. <b>Some values are intentionally blurred.</b>
	<br /><br />
   <img src="images/idd2.jpg" width="600" height="450">
   

<!-- CONTACT -->
## Contact
For any issues, feel free to contact - <br /><br />
Tapajyoti Deb - tapajyotideb@gmail.com
<hr />

