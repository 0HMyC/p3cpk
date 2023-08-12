import os
import rcpk
import logger as log

initPath = None

def findCPKS(start, outDir):
	global initPath # Python plz
	if initPath == None:
		initPath = start
	for filFol in os.listdir(start):
		cur = os.path.join(start, filFol)
		# Check if we need to search through more folders,
		# or extract a CPK. TODO: better comparision method than .lower()?
		if os.path.isdir(cur):
			findCPKS(cur, outDir)
		elif os.path.isfile(cur) and cur.lower().endswith('.cpk'):
			log.compliantLog("Unpacking", cur)
			unpackCPK(cur, outDir)

def createOutDir(desOut, inFile):
	outFol = None
	if isinstance(desOut, str):
		# Mirror input directory structure on output;
		# nicer to navigate + prevents potential file overwrite issues
		if isinstance(initPath, str):
			mirrorDir = inFile[len(initPath)+len(os.sep):inFile.rindex(os.sep)]
			outFol = os.path.join(desOut, mirrorDir, inFile[inFile.rindex(os.sep)+len(os.sep):-4] + '_extracted')
			log.verboseLog("Mirrored Output Directory:", outFol)
		else:
			outFol = os.path.join(desOut, inFile[inFile.rindex(os.sep)+len(os.sep):-4] + '_extracted')
	else:
		outFol = os.path.join(inFile[:inFile.rindex(os.sep)], inFile[inFile.rindex(os.sep)+len(os.sep):-4] + '_extracted')
	os.makedirs(outFol, exist_ok=True) # Make output folder if it doesn't exist
	return outFol

def unpackCPK(input, outDir):
	cpkBytes = None
	outputFolder = createOutDir(outDir, input) # Get output folder
	rcpk.log.args = log.args # set rcpk verbose mode
	# Read CPK file to unpack
	with open(input, "rb") as rCPK:
		cpkBytes = rCPK.read(os.path.getsize(input))
	i = 0
	while i < len(cpkBytes):
		cHeader = rcpk.readHeader(cpkBytes[i:i+0x100])
		# if cHeader is ever -1 that means the read failed,
		# or we're at the end of the file
		if cHeader == -1:
			break
		cFile = cpkBytes[i+0x100:(i+0x100)+cHeader["FileSize"]]
		# Sometimes the file "padding" contains extra data...
		# TODO: What and why is this? NOTE: File sizes preceded by 0x00007F4E
		# Appear to contain floats at the end, sometimes? Figure that out!!!
		# Create output directories that we need
		cExData = None
		if cHeader["FilePadding"] >= 1:
			cExData = cpkBytes[i+0x100+cHeader["FileSize"]:i+0x100+cHeader["FileSize"]+cHeader["FilePadding"]]
		# Shift file index to next file's header
		i += 0x100 + cHeader["FileSize"] + cHeader["FilePadding"]
		cDirs = os.path.join(outputFolder, "Files")
		os.makedirs(cDirs, exist_ok=True)
		cDirs = os.path.join(outputFolder, "Headers")
		os.makedirs(cDirs, exist_ok=True)
		# TODO: re-implement no file overwrite option?
		# Write file bytes
		with open(os.path.join(outputFolder, "Files", cHeader["FileName"]), "wb") as cFileOut:
			cFileOut.write(cFile)
		with open(os.path.join(outputFolder, "Headers", cHeader["FileName"] + '.bin'), "wb") as headerOut:
			headerOut.write(cHeader["Unknown0"])
		# Only write extra data if there's even any in the file
		if cExData != None:
			cDirs = os.path.join(outputFolder, "ExtraData")
			os.makedirs(cDirs, exist_ok=True)
			with open(os.path.join(outputFolder, "ExtraData", cHeader["FileName"] + '.bin'), "wb") as exOut:
				exOut.write(cExData)