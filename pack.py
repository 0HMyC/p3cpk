import os
import struct

def packFiles(wDir, whDir):
	cpkBytes = None
	cHeader = None
	for fil in os.listdir(wDir):
		print("Packing", fil, "into CPK...")
		if not os.path.isfile(os.path.join(whDir, fil + '.bin')):
			print("Can't locate header file for", fil + "! Skipping file!")
			continue
		if cpkBytes == None:
			#assumes file names can only be 14 characters long
			cpkBytes = struct.pack('>14s', fil.encode())
		else:
			cpkBytes += struct.pack('>14s', fil.encode())
		cFile = os.path.join(wDir, fil)
		with open(os.path.join(whDir, fil + '.bin'), "rb") as cHed:
			#File headers will always be 0xEE bytes long
			#if we have one that isn't... too bad!
			cpkBytes += cHed.read(0xEE)
		#append actual file size to header (as LE)
		cFileSize = os.path.getsize(cFile)
		cpkBytes += struct.pack('<I', cFileSize)
		#copy last file header to append EOF header thing
		cHeader = b'\x00' + cpkBytes[-0xFF:-4] + b'\x00\x00\x00\x00'
		#append file bytes to cpk bytes
		with open(cFile, "rb") as cFil:
			cpkBytes += cFil.read(cFileSize)
		#end of loop, start over with new file
	cpkBytes += cHeader
	return cpkBytes

def packCPK(input, outDir):
	# Get output folder
	outputFolder = None
	# os.makedirs(outDir, exist_ok=True) # Make output folder if it doesn't exist
	if isinstance(outDir, str):
		outputFolder = os.path.join(outDir, input[input.rindex('/')+1:] + '.cpk')
	else:
		outputFolder = os.path.join(input[:input.rindex('/')], input[input.rindex('/')+1:] + '.cpk')
	#get files and headers folder as vars
	#for easy repeated access
	filesDir = os.path.join(input, "Files")
	headersDir = os.path.join(input, "Headers")
	if os.path.isdir(filesDir):
		if os.path.isdir(headersDir):
			print("Packing", input, "into CPK file...")
			#pack files into cpk
			cpkData = packFiles(filesDir, headersDir)
			#write file data to disk
			with open(outputFolder, "wb") as cpkOut:
				cpkOut.write(cpkData)
		else:
			#TODO: Add ability to generate generic header, if that's even a good idea
			print("Warning! Could not locate Headers directory in", headersDir + "! Folder will not be packed into CPK!")
	else:
		print("Error! Could not locate Files directory in", filesDir + "! Folder will not be packed into CPK!")
		return
