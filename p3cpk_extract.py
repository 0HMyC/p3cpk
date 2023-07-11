import argparse
import os
# import struct

parser = argparse.ArgumentParser(description="Extractor for Persona 3 FES .cpk files.")
operateGroup = parser.add_mutually_exclusive_group(required=True)
operateGroup.add_argument('-i', '--file', metavar='file', help="The non-Criware CPK file to extract.")
operateGroup.add_argument('-f', '--folder', metavar='folder', help="The folder containing non-Criware CPK files to extract.")
parser.add_argument('-q', '--quiet', help="Minimizes messages printed.", action='store_true')
parser.add_argument('-v', '--verbose', help="Prints extra messages when extracting files. Useful for debugging.", action='store_true')
parser.add_argument('-o', '--output', help="Override the output path for extracted files. WIP.")
parser.add_argument('-r', '--recursive', help="Search folders recursively when passing a folder into the script.", action='store_true')
parser.add_argument('--overwrite', help="Overwrite existing extracted files.", action='store_true')
parser.add_argument('--license', help="Prints the license for the script.", action='store_true')
args = parser.parse_args()

def compliantPrint(*inp):
	if not args.quiet:
		print(*inp)

def verboseLog(*inputs):
	if args.verbose:
		print(*inputs)

def searchForCPK(inputDir):
	verboseLog('Searching', inputDir, 'for cpk files...')
	for fifo in os.listdir(inputDir):
		cFifo = os.path.join(inputDir, fifo)
		if os.path.isdir(cFifo) and args.recursive:
			searchForCPK(cFifo)
		elif os.path.isfile(cFifo) and fifo.lower().endswith('.cpk'):
			extractCPK(cFifo.replace(os.sep, '/').lower())

def extractCPK(inputFile):
	print('==Unpacking', inputFile[inputFile.rindex('/')+1:] + '...==')
	alignType = inputFile[inputFile.rindex('_')+1:-7]
	verboseLog('\nalignType=' + alignType + '\n')
	outPath = os.path.join(inputFile[:inputFile.rindex('/')], inputFile[inputFile.rindex('/') + 1:-4] + '_extracted.cpk')
	if isinstance(args.output, str):
		outPath = os.path.join(args.output, '_extracted.cpk')
	os.makedirs(outPath, exist_ok=True)
	inpFile = open(inputFile, "rb")
	def readLittle(bytes):
		return int.from_bytes(inpFile.read(bytes), byteorder='little')
	inpFile.seek(0, os.SEEK_END)
	totalBytes = inpFile.tell()
	inpFile.seek(0)
	pastFirstFile = False
	# cpkBytes = inpFile.read(totalBytes) #read file into memory; cuts down on file reads
	# inpFile.close()
	# cIndex = 0
	while True:
		if inpFile.tell() >= totalBytes:
			verboseLog('\nDEB: Reached end of file! Stopping to prevent error...\n')
			break
		#get file name
		verboseLog(hex(inpFile.tell()))
		# cFile = inpFile.read(0x10).rstrip(b'\x00').decode('utf-8')
		cFile = inpFile.read(0x10)
		if cFile[0] == 0x0:
			verboseLog('Warning! cFile is null terminated from start! Skipping...')
			inpFile.seek(0xF0, 1)
			continue
		cFile = cFile.split(b'\x00')[0].decode('utf-8') #convert to file name
		verboseLog('\nSkipping unknown header(?) data!\n')
		headerBase = bytearray(inpFile.read(0xEC))
		if not pastFirstFile:
			if args.overwrite or not os.path.isfile(os.path.join(outPath, 'base_header')):
				verboseLog('Writing base_header file...')
				with open(os.path.join(outPath, 'base_header'), "wb") as headOut: #aight imma-
					headOut.write(headerBase)
		cFileSize = readLittle(4) #get file's size in bytes
		#skip extraction if file already exists
		# warn user about error
		if cFileSize == 0:
			verboseLog('Warning!', cFile, 'is 0 bytes long! Skipping to prevent possible python error!')
			# inpFile.seek(4, 1)
			continue
		compliantPrint('=Extracting ' + cFile + '!=')
		cExtraOffset = 0
		if not pastFirstFile:
			cExtraOffset = cFileSize & 0xFF
			cShiftedSize = (cFileSize >> 8) << 8
			verboseLog("Lowest Byte:", hex(cExtraOffset))
			if cExtraOffset == 0 or cExtraOffset == 0x80 or cExtraOffset == 0xC0:
				cExtraOffset = 0
			else:
				if cExtraOffset > 0xC0:
					cExtraOffset = (0x100 + cShiftedSize) - cFileSize
					# cExtraOffset = cExtraOffset - cFileSize
				elif cExtraOffset > 0xA0:
					# cExtraOffset -= 0xA0
					if cExtraOffset < 0xC0:
						cExtraOffset = (0xC0 + cShiftedSize) - cFileSize
						# cExtraOffset = cExtraOffset - cFileSize
				else:
					if cExtraOffset > 0x40: #TODO: is this correct?
						cExtraOffset = (0x80 + cShiftedSize) - cFileSize if cExtraOffset < 0x80 else (0xC0 + cShiftedSize) - cFileSize
					else:
						cExtraOffset = (0x40 + cShiftedSize) - cFileSize
					# cExtraOffset = cExtraOffset - cFileSize
		verboseLog(cFile, 'size is:', hex(cFileSize), 'extra offset is:', hex(cExtraOffset))
		verboseLog('Current address in file:', hex(inpFile.tell()))
		pastFirstFile = True #TODO: could this cause problems if the first file is 0 byte?
		#read data from cpk and write file
		if os.path.isfile(os.path.join(outPath, cFile)) and not args.overwrite:
			verboseLog(cFile, 'already extracted! Will not write file...')
			inpFile.seek(cFileSize + cExtraOffset, 1)
			continue
		cFileData = inpFile.read(cFileSize)
		with open(os.path.join(outPath, cFile), "wb") as cFileOut:
			cFileOut.write(cFileData)
		inpFile.seek(cExtraOffset, 1)
	compliantPrint('==Finished unpacking', inputFile[inputFile.rindex('/')+1:] + '!==')
	# inpFile.close()
	
if args.license:
	print("""
Copyright © 2023 moddaman AKA SomeSchmuckPGR

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
""")

if isinstance(args.folder, str):
	print('Looking for .cpk files in', args.folder + '!')
	searchForCPK(args.folder)
	print('Search complete!')

elif isinstance(args.file, str):
	args.file = args.file.replace(os.sep, '/').lower()
	if args.file.endswith('.cpk'):
		extractCPK(args.file)