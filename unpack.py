import os
import rcpk
import logger as log
import json

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

def checkExists(path):
	if os.path.isfile(path) and logs.args.newonly:
		return True
	return False

def unpackCPK(input, outDir):
	cpkBytes = None
	outputFolder = createOutDir(outDir, input) # Get output folder
	rcpk.log.args = log.args # set rcpk verbose mode
	# Read CPK file to unpack
	with open(input, "rb") as rCPK:
		cpkBytes = rCPK.read(os.path.getsize(input))
	i = 0
	# Create a metadata file to use for packing
	unpackedFiles = []
	cpkConfig = {
		"NoNullHeader": False,
		"SkipExtraData": False,
		"AutomaticImport": True
	}
	while i < len(cpkBytes):
		cHeader = rcpk.readHeader(cpkBytes[i:i+0x100])
		# if cHeader is ever -1 that means the read failed
		if cHeader == -1:
			# if i < len(cpkBytes):
				# log.verboseLog("Null header at end of file!")
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
		if i >= len(cpkBytes):
			log.verboseLog("No null header at end of file!")
			cpkConfig["NoNullHeader"] = True
		cDirs = os.path.join(outputFolder, "Files")
		os.makedirs(cDirs, exist_ok=True)
		unpackedFiles.append(cHeader["FileName"])
		cDirs = os.path.join(cDirs, cHeader["FileName"])
		if checkExists(cDirs):
			continue
		# Write file bytes
		with open(cDirs, "wb") as cFileOut:
			cFileOut.write(cFile)
		cDirs = os.path.join(outputFolder, "Headers")
		os.makedirs(cDirs, exist_ok=True)
		cDirs = os.path.join(cDirs, cHeader["FileName"] + '.bin')
		if checkExists(cDirs):
			continue
		with open(cDirs, "wb") as headerOut:
			headerOut.write(cHeader["Unknown0"])
		# Only write extra data if there's even any in the file
		if cExData != None:
			cDirs = os.path.join(outputFolder, "ExtraData")
			os.makedirs(cDirs, exist_ok=True)
			cDirs = os.path.join(cDirs, cHeader["FileName"] + '.bin')
			if checkExists(cDirs):
				continue
			with open(cDirs, "wb") as exOut:
				exOut.write(cExData)
	cpkConfig["Files"] = unpackedFiles
	jsPath = os.path.join(outputFolder, "Config.json")
	if os.path.isfile(jsPath) and log.args.newonly:
		log.alreadyExist(jsPath)
		return
	with open(jsPath, "w") as cpkJS:
		json.dump(cpkConfig, cpkJS, indent = 2)