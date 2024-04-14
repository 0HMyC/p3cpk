import os
import struct
import logger as log
from rcpk import getPaddingAmt
import json

cpkConfig = None

# search through folder to find
# unpacked CPK's to pack
def findCPKS(start, out, recursive):
	mirrorOut = out # init var
	for filfol in os.listdir(start):
		cur = os.path.join(start, filfol)
		if os.path.isdir(cur):
			# always skip past unpacked CPK data folders;
			# there should never be CPK's to pack in there
			if (cur == "ExtraData") or (cur == "Files") or (cur == "Headers"):
				continue
			if os.path.isfile(os.path.join(cur, "Config.json")):
				configFile = loadConfigJson(cur)
				# unlikely most files named "Config.json" that aren't ours
				# would have this key in it
				if "NoNullHeader" in configFile:
					os.makedirs(mirrorOut, exist_ok=True) # only create dirs when we will write files
					packCPK(cur, mirrorOut, loadedConfig=configFile)
			else:
				mirrorOut = os.path.join(out, filfol) # only add searched folders
				# If script is run with recursive argument,
				# Search through folders
				if recursive:
					findCPKS(cur, mirrorOut, recursive)
				else:
					return

def getPaddingBytes(cnt):
	log.verboseLog('Generating file padding! Amt:', cnt)
	return b'\x00' * cnt

def createPadding(fileSize, file, exDir):
	global cpkConfig
	cFilePadding = getPaddingAmt(fileSize)
	cExData = b''
	if cFilePadding != 0 and os.path.isdir(exDir) and cpkConfig["GenerateExtraData"] == False:
		cExPath = os.path.join(exDir, file + '.bin')
		if os.path.getsize(cExPath) == cFilePadding:
			log.verboseLog("Loading extra file data from", cExPath + '!')
			with open(cExPath, "rb") as xDat:
				# in this path, the needed amount of padding matches
				# the extra data file's size, so we use that instead of
				# generating padding to maintain high file accuracy
				cExData = xDat.read(cFilePadding)
		else:
			log.verboseLog("Required padding does not match extra data", cExPath + '\'s file size!')
			cExData = getPaddingBytes(cFilePadding)
	else:
		cExData = getPaddingBytes(cFilePadding)
	return cExData

def packFiles(wDir, whDir, wxDir):
	cpkBytes = None
	cHeader = b''
	global cpkConfig
	if cpkConfig["AutomaticImport"] == False:
		log.verboseLog("AutomaticImport set to false! Iterating over manually-defined files from Config.json!")
	fileIter = os.listdir(wDir) if cpkConfig["AutomaticImport"] else cpkConfig["Files"]
	for fil in fileIter:
		print("Packing", fil, "into CPK...")
		if not os.path.isfile(os.path.join(whDir, fil + '.bin')):
			print("Can't locate header file for", fil + "! Skipping file!")
			continue
		if len(fil) > 14:
			log.verboseLog("Warning: The file name is longer than 14 characters!\nThis may or may not cause problems with the packed CPK!")
		if cpkBytes == None:
			# assumes file names can only be 14 characters long
			cpkBytes = struct.pack('>14s', fil.encode())
		else:
			cpkBytes += struct.pack('>14s', fil.encode())
		cFile = os.path.join(wDir, fil)
		with open(os.path.join(whDir, fil + '.bin'), "rb") as cHed:
			# File headers will always be 0xEE bytes long
			# if we have one that isn't... too bad!
			cpkBytes += cHed.read(0xEE)
		# append actual file size to header (as LE)
		cFileSize = os.path.getsize(cFile)
		cpkBytes += struct.pack('<I', cFileSize)
		# copy last file header to append EOF null header
		# when NoNullHeader is set to false in the cpk config
		if cpkConfig["NoNullHeader"] != True:
			cHeader = b'\x00' + cpkBytes[-0xFF:-4] + b'\x00\x00\x00\x00'
		else:
			log.verboseLog("NoNullHeader is true! Not creating null header for end of file!")
		# append file bytes to cpk bytes
		with open(cFile, "rb") as cFil:
			cpkBytes += cFil.read(cFileSize)
		# Pad file as needed
		cpkBytes += createPadding(cFileSize, fil, wxDir)
		# end of loop, start over with new file
	cpkBytes += cHeader
	return cpkBytes
	
def loadConfigJson(basePath):
	jsData = None
	with open(os.path.join(basePath, "Config.json"), "r") as jsStream:
		jsData = json.load(jsStream)
	return jsData

def fixConfig(cfg):
	if not "NoNullHeader" in cfg:
		cfg["NoNullHeader"] = False
		log.verboseLog("Config.json missing NoNullHeader key! Using default value! (False)")
	if not "GenerateExtraData" in cfg:
		cfg["GenerateExtraData"] = False
		log.verboseLog("Config.json missing GenerateExtraData key! Using default value! (False)")
	if not "AutomaticImport" in cfg:
		cfg["AutomaticImport"] = True
		log.verboseLog("Config.json missing AutomaticImport key! Using default value! (True)")
	if not "Files" in cfg:
		cfg["Files"] = []
		cfg["AutomaticImport"] = True
		log.verboseLog("Config.json missing Files key! Using empty array and Forcing AutomaticImport!")
	return cfg

def packCPK(input, outDir, loadedConfig=None):
	# Get output file path; output files in all-caps
	# since loose CPK's in P3F are all-caps
	outputFile = None
	if isinstance(outDir, str):
		outputFile = os.path.join(outDir, input[input.rindex(os.sep)+len(os.sep):].upper() + '.CPK')
	else:
		outputFile = os.path.join(input[:input.rindex(os.sep)], input[input.rindex(os.sep)+len(os.sep):].upper() + '.CPK')
	if os.path.isfile(outputFile) and log.args.newonly:
		log.alreadyExist(outputFile)
		return
	# get files and headers folder as vars for repeated access
	filesDir = os.path.join(input, "Files")
	headersDir = os.path.join(input, "Headers")
	exDir = os.path.join(input, "ExtraData")
	global cpkConfig
	if loadedConfig == None:
		cpkConfig = loadConfigJson(input)
	else:
		cpkConfig = loadedConfig
	if os.path.isdir(filesDir):
		if os.path.isdir(headersDir):
			print("\nPacking", input, "into CPK file...")
			cpkConfig = fixConfig(cpkConfig)
			# pack files into cpk
			cpkData = packFiles(filesDir, headersDir, exDir)
			# write file data to disk
			with open(outputFile, "wb") as cpkOut:
				cpkOut.write(cpkData)
		else:
			# TODO: Add ability to generate generic header, if that's even a good idea
			print("\nWarning! Could not locate Headers directory in", headersDir + "! Folder won't be packed into CPK!")
	else:
		print("\nError! Could not locate Files directory in", filesDir + "! Folder can't be packed into CPK!")