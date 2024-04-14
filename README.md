# p3cpk
A Python script that allows for extracting and packing Persona 3's CPK files.

Requires Python 3.3+ (determined using [vermin.](https://github.com/netromdk/vermin))

## Usage
To unpack a single .CPK file:

`python p3cpk.py -i "path\to\file"`

To unpack all .CPK files in a folder:

`python p3cpk.py -f "folder\path" [-u|--unpack]`

To pack a folder into a .CPK file:

`python p3cpk.py -f "folder\path [-p|--pack]"`

You can optionally specify a folder to output extracted or packed files to, like so:

`python p3cpk.py [-i "file"|-f "folder"] [-u|-p] [-o|--output] "output\folder"`

Other available arguments can be seen by running the script with only the help argument:

`python p3cpk.py -h`

## Config.json
When unpacking CPK files, the script will create a Config.json in the folder of the unpacked CPK. This file contains some settings which determines how exactly the script will re-pack that CPK. The settings are as follows:

|Setting Name   |Data Type   |Description|
|---------------|------------|-----------|
|NoNullHeader   |Bool        |Determines whether or not a "null header" should be appended to the end of the CPK. For information on null headers, see [DOCUMENTATION.MD](https://github.com/0HMyC/p3cpk/blob/main/DOCUMENTATION.md).|
|SkipExtraData  |Bool        |Determines whether to load file padding/extra data from the files in the "(CPKName)\ExtraData" directory or to generate the needed file padding.|
|AutomaticImport|Bool        |Determines whether or not the script should pack all files contained within "(CPKName)\Files" or if it should only packed manually defined files.|
|Files          |String Array|A list of all files contained within the CPK; when AutomaticImport is set to false, this list is used to manually define which files in "(CPKName)\Files" will be packed into a CPK.| 
