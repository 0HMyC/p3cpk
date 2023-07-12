# p3cpk
A Python script that allows for extracting and packing Persona 3's CPK files.

Requires Python 3.3+ (determined using [vermin.](https://github.com/netromdk/vermin))

## Usage
To unpack a single .cpk file:

`python p3cpk.py -i "path\to\file"`

To unpack all .cpk's in a folder:

`python p3cpk.py -f "folder\path" [-u|--unpack]`

To pack a folder into a .cpk file:

`python p3cpk.py -f "folder\path [-p|--pack]"`

You can optionally specify a folder to output extracted or packed files to, like so:

`python p3cpk.py [-i "file"|-f "folder"] [-o|--output] "output\folder"`
