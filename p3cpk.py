import argparse
import os
import unpack
import pack
import convert
# import rcpk

parser = argparse.ArgumentParser(description="Extractor/Packer of Persona 3 FES .cpk files.")
operateGroup = parser.add_mutually_exclusive_group(required=True)
operateGroup.add_argument('-i', '--file', metavar='file', help="The CPK file to extract.")
operateGroup.add_argument('-f', '--folder', metavar='folder', help="The folder containing CPK files to extract.")
operateGroup.add_argument('-l', '--license', help="Prints the license for the script.", action='store_true')
parser.add_argument('-u', '--unpack', help="Unpack file(s) in folder. Redundant when operating on a file.", action='store_true')
parser.add_argument('-p', '--pack', help="Pack folder to CPK.", action='store_true')
parser.add_argument('-c', '--convert', help="Convert file(s) to PAK format for use with other tools.", action='store_true')
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
if args.license:
	with open("LICENSE", "r") as liscFile:
		print(liscFile.read())

# call functions
if isinstance(args.file, str):
	if not args.file.lower().endswith('.cpk'):
		print('Passed file is not a CPK!')
	else:
		if args.convert:
			convert.convertCPK(args.file, args.output)
		# Tell user they can't pack a packed CPK; there'd be no point lmao
		elif args.pack and not args.unpack:
			print("You cannot pack a packed CPK file!")
		else:
			unpack.unpackCPK(args.file, args.output)
elif isinstance(args.folder, str):
	# TODO: Allow packing CPK files to PAK format?
	if args.unpack and not args.convert:
		unpack.findCPKS(args.folder, args.output, args.recursive)
		print("Unpacked all possible CPK files!")
	elif args.convert and not args.pack:
		convert.findCPKS(args.folder, args.output, args.recursive)
		print("\nConverted all possible CPK files!")
	else:
		pack.findCPKS(args.folder, args.output, args.recursive)
		print("Packed all possible CPK folders!")
