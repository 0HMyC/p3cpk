import argparse
import os
import unpack
import pack
# import rcpk

parser = argparse.ArgumentParser(description="Extractor/Packer of Persona 3 FES .cpk files.")
operateGroup = parser.add_mutually_exclusive_group(required=True)
operateGroup.add_argument('-i', '--file', metavar='file', help="The CPK file to extract.")
operateGroup.add_argument('-f', '--folder', metavar='folder', help="The folder containing CPK files to extract.")
operateGroup.add_argument('-l', '--license', help="Prints the license for the script.", action='store_true')
parser.add_argument('-u', '--unpack', help="Unpack file/files in folder. Redundant when operating on a file.", action='store_true')
parser.add_argument('-p', '--pack', help="Pack folder to CPK.", action='store_true')
parser.add_argument('-o', '--output', help="Override the output path for files.")
parser.add_argument('-v', '--verbose', help="Prints extra messages when extracting files. Useful for debugging.", action='store_true')
parser.add_argument('-q', '--quiet', help="Supresses some messages from being printed. Useful if you want fewer messages in the console.", action='store_true')
parser.add_argument('-n', '--newonly', help="Only allows new files to be written; Prevents overwriting already extracted files.", action='store_true')
parser.add_argument('-r', '--recursive', help="If passing a folder to script, enables recursive search for folders contained within for CPK's to pack/unpack.", action='store_true')
args = parser.parse_args()

# set verbose logging mode
unpack.log.args = args
pack.log.args = args

# print script license
# TODO: just load this from the license file man,
# the saved file reads aren't worth needing to double-check
# that this is up-to-date
if args.license:
	print("""MIT License

Copyright (c) 2023 0HMyC aka moddaman aka SomeSchmuckPGR

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""")

# call functions
if isinstance(args.file, str):
	if not args.file.lower().endswith('.cpk'):
		print('Passed file is not a CPK!')
	else:
		# Tell user they can't pack a packed CPK; there'd be no point lmao
		if args.pack and not args.unpack:
			print("You cannot pack a packed CPK file!")
		else:
			unpack.unpackCPK(args.file, args.output)
elif isinstance(args.folder, str):
	if args.unpack:
		unpack.findCPKS(args.folder, args.output, args.recursive)
		print("Unpacked all possible CPK files!")
	else:
		pack.findCPKS(args.folder, args.output, args.recursive)
		print("Packed all possible CPK folders!")
