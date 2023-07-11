import argparse
import os
import struct

parser = argparse.ArgumentParser(description="Pack P3FES cpk file from folder.")
parser.add_argument('inputFolder', metavar='folder', help="The folder files to pack into a non-Criware CPK.")
parser.add_argument('-q', '--quiet', help="Minimizes messages printed.", action='store_true')
parser.add_argument('-v', '--verbose', help="Prints extra messages when packing files. Useful for debugging.", action='store_true')
parser.add_argument('-o', '--output', help="Override the output path for packed files. WIP.")
parser.add_argument('--overwrite', help="Overwrite existing packed files.", action='store_true')
parser.add_argument('-c', '--allcaps', help="Outputs file name in all caps.", action='store_true')
parser.add_argument('-l', '--lowercase', help="Outputs file name in all lowercase.", action='store_true')
parser.add_argument('--license', help="Prints the license for the script.", action='store_true')
args = parser.parse_args()

def compliantPrint(*inp):
	if not args.quiet:
		print(*inp)

def verboseLog(*inputs):
	if args.verbose:
		print(*inputs)

if args.license:
	print("""
Copyright © 2023 moddaman AKA SomeSchmuckPGR

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
""")

if isinstance(args.inputFolder, str):
	#ensure unix file pathing for best os compatibility
	if args.lowercase:
		args.inputFolder = args.inputFolder.replace(os.sep, '/').lower()
	else:
		args.inputFolder = args.inputFolder.replace(os.sep, '/')
	compliantPrint('Packing', args.inputFolder[args.inputFolder.rindex('1')+1:], 'into cpk...')
	outPath = args.inputFolder[args.inputFolder.rindex('/')+1:] + '_packed.cpk'
	#remove .cpk ending from folder name if present to make the output a little nicer reading
	if args.inputFolder.lower().endswith('.cpk'):
		outPath = args.inputFolder[:-4] + '_packed.cpk'
	if args.output:
		outPath = os.path.join(args.output, outPath)
	else:
		outPath = os.path.join(args.inputFolder, outPath)
	verboseLog('Outputting file to', outPath.upper() if args.allcaps else outPath)
	headerData = b'' #ensure this is declared; just in case of super weird issue
	if os.path.isfile(os.path.join(args.inputFolder, 'base_header')):
		with open(os.path.join(args.inputFolder, 'base_header'), "rb") as headerFile:
			headerData = headerFile.read(0xEC)
	else:
		print('!!!- Warning! No base_header file in', args.inputFolder + '! A blank header that most likely won\'t work will be generated in it\'s place! -!!!')
		headerData = b'\x00' * 0xEC
	cpkBytes = b''
	addedFirstFile = False
	lastFile = None
	for file in os.listdir(args.inputFolder):
		if file != 'base_header':
			filePath = os.path.join(args.inputFolder, file)
			if os.path.isfile(filePath):
				verboseLog('isFile:', file, 'nameLen:', len(file))
				#we only have space for, at most, 16 characters (if that) as part of the header;
				#we need to truncate file names down to fit
				if len(file) > 0x10:
					print('Warning! File', file, 'has a name longer than 16 characters!\nFilename will be shortened!')
					fileExt = file[file.rindex('.'):]
					#TODO: account for weirdness like 0xE long string in DATA.CVM\CUTIN\SHAPE\C40_1B01.CPK
					file = file[:(0xF - len(fileExt))] + fileExt
					verboseLog('File renamed to:', file)
				#get size of file to pack; used for header and reading the file
				fileSize = os.path.getsize(filePath)
				nAsBytes = struct.pack('>16s', file.encode())
				cpkBytes += nAsBytes + headerData
				cpkBytes += struct.pack('<I', fileSize)
				lastFile = file #when we exit the loop, this will be the name of the last file we packed
				with open(filePath, "rb") as ldFile:
					cpkBytes += ldFile.read(fileSize)
				if not addedFirstFile:
					#check if we need to pad after first file, and then pad if we do
					fileSizeLower = fileSize & 0xFF
					verboseLog('fileSizeLower', hex(fileSizeLower))
					shiftedFileSize = (fileSize >> 8) << 8 #chop off 'lowest' byte; will use for padding amounts later
					#pad amount checks; determined by lowest byte (ie 0x0000_00FF)
					if fileSizeLower != 0 or fileSizeLower != 0x80 or fileSizeLower != 0xC0:
						if fileSizeLower > 0xC0:
							fileSizeLower = (0x100 + shiftedFileSize) - fileSize
						elif fileSizeLower > 0xA0:
							if fileSizeLower < 0xC0:
								fileSizeLower = (0xC0 + shiftedFileSize) - fileSize
						else:
							if fileSizeLower > 0x40: #i'm not entirely sure that this is the correct value but it works
								fileSizeLower = 0x80 + shiftedFileSize if fileSizeLower < 0x80 else 0xC0 + shiftedFileSize
								fileSizeLower = fileSizeLower - fileSize
							else:
								fileSizeLower = (0x40 + shiftedFileSize) - fileSize
						cpkBytes += b'\x00' * fileSizeLower
					addedFirstFile = True
	#Add final null file; is this necessary? Idk lmao
	cpkBytes += b'\x00' + struct.pack('>15s', lastFile[1:].encode()) + headerData + struct.pack('<I', 0)
	compliantPrint('Packing complete!\nAttempting to write CPK...')
	if args.allcaps:
		outPath = outPath.upper()
	elif args.lowercase:
		outPath = outPath.lower()
	if os.path.isfile(outPath) and not args.overwrite:
		compliantPrint(outPath, 'already exists! Will not write file...')
	else:
		with open(outPath, "wb") as cpkOut:
			cpkOut.write(cpkBytes)
		compliantPrint('Finished writing', outPath.upper() + '!')