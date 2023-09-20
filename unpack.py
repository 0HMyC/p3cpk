import os
import rcpk
import logger as log
import json

initPath = None

def findCPKS(start, outDir, recursive):
	global initPath # Python plz
	if initPath == None:
		initPath = start
	for filFol in os.listdir(start):
		cur = os.path.join(start, filFol)
		# Check if we need to search more folders, or extract a CPK.
		# Only do so if recursive search argument has been passed.
		if os.path.isdir(cur) and recursive:
			findCPKS(cur, outDir, recursive)
		# TODO: better comparision method than .lower()?
		elif os.path.isfile(cur) and cur.lower().endswith('.cpk'):
			log.compliantLog("\nUnpacking", cur)
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
	if os.path.isfile(path) and log.args.newonly:
		return True
	return False

def unpackCPK(input, outDir):
	cpkBytes = None
	outputFolder = createOutDir(outDir, input) # Get output folder
	rcpk.log.args = log.args                   # set rcpk verbose mode
	with open(input, "rb") as rCPK:            # Read CPK file to unpack
		cpkBytes = rCPK.read(os.path.getsize(input))
	i = 0
	# Create a metadata file to use for packing
	cpkConfig = {
		"NoNullHeader": False,      # if true, include null header at end of file when packing
		"GenerateExtraData": False, # if true, generate file padding instead of loading from file
		"AutomaticImport": True,    # if false, only load manually defined files
		"Files": []                 # list of files in CPK
	}
	while i < len(cpkBytes):
		cHeader = rcpk.readHeader(cpkBytes[i:i+0x100])
		if cHeader == -1: # only -1 on read failure
			break
		cFile = cpkBytes[i+0x100:(i+0x100)+cHeader["FileSize"]]
		# TODO: Sometimes the file "padding" contains extra data... What and why is this? 
		# NOTE: File sizes preceded by 0x00007F4E appear to contain floats at the end, sometimes? Figure that out!!!
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
		cpkConfig["Files"].append(cHeader["FileName"])
		cDirs = os.path.join(cDirs, cHeader["FileName"])
		if not checkExists(cDirs):
			with open(cDirs, "wb") as cFileOut: # Write file bytes
				cFileOut.write(cFile)
		cDirs = os.path.join(outputFolder, "Headers")
		os.makedirs(cDirs, exist_ok=True)
		cDirs = os.path.join(cDirs, cHeader["FileName"] + '.bin')
		if not checkExists(cDirs):
			with open(cDirs, "wb") as headerOut:
				headerOut.write(cHeader["Unknown0"])
		# Only write extra data if there's even any in the file
		if cExData != None:
			cDirs = os.path.join(outputFolder, "ExtraData")
			os.makedirs(cDirs, exist_ok=True)
			cDirs = os.path.join(cDirs, cHeader["FileName"] + '.bin')
			if not checkExists(cDirs):
				with open(cDirs, "wb") as exOut:
					exOut.write(cExData)
	jsPath = os.path.join(outputFolder, "Config.json")
	if os.path.isfile(jsPath) and log.args.newonly:
		log.alreadyExist(jsPath)
		return
	with open(jsPath, "w") as cpkJS:
		json.dump(cpkConfig, cpkJS, indent = 2)