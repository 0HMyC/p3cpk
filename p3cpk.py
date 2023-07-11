import argparse
import os
import unpack
# import rcpk

parser = argparse.ArgumentParser(description="Extractor/Packer of Persona 3 FES .cpk files.")
operateGroup = parser.add_mutually_exclusive_group(required=True)
operateGroup.add_argument('-i', '--file', metavar='file', help="The CPK file to extract.")
operateGroup.add_argument('-f', '--folder', metavar='folder', help="The folder containing CPK files to extract.")
parser.add_argument('-u', '--unpack', help="Unpack file/files in folder. Redundant when operating on a file.", action='store_true')
parser.add_argument('-p', '--pack', help="Pack folder/folders in folder.", action='store_true')
parser.add_argument('-o', '--output', help="Override the output path for files.")
# parser.add_argument('-q', '--quiet', help="Minimizes messages printed.", action='store_true')
# parser.add_argument('-v', '--verbose', help="Prints extra messages when extracting files. Useful for debugging.", action='store_true')
# parser.add_argument('--overwrite', help="Overwrite existing extracted files.", action='store_true')
# parser.add_argument('--license', help="Prints the license for the script.", action='store_true')
args = parser.parse_args()

def packCPK():
	print("Packing not implemented yet!")

#force unix paths & call functions
if isinstance(args.file, str):
	if not args.file.lower().endswith('.cpk'):
		print('Passed file is not a CPK!')
	else:
		args.file = args.file.replace(os.sep, '/')
		# Tell user they can't pack a packed CPK; there'd be no point lmao
		if args.pack and not args.unpack:
			print("You cannot pack a packed CPK file!")
		else:
			unpack.unpackCPK(args.file, args.output)
elif isinstance(args.folder, str):
	args.folder = args.folder.replace(os.sep, '/')
	if args.unpack:
		unpack.findCPKS(args.folder, args.output)
	else:
		packCPK()
