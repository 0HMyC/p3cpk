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
