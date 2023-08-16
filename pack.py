import os
import struct
import logger as log
from rcpk import getPaddingAmt
import json

cpkConfig = None

def createPadding(fileSize, file, exDir):
	global cpkConfig
	cFilePadding = getPaddingAmt(fileSize)
	cExData = b''
	if cFilePadding != 0 and os.path.isdir(exDir) and cpkConfig["SkipExtraData"] == False:
		cExPath = os.path.join(exDir, file + '.bin')
		if os.path.getsize(cExPath) == cFilePadding:
			log.verboseLog("Loading extra file data from", cExPath + '!')
			with open(cExPath, "rb") as xDat:
				# in this path, the needed amount of padding matches
				# the extra data file's size, so we use that instead of
				# generating padding to try maintaining higher file accuracy
				cExData = xDat.read(cFilePadding)
		else:
			log.verboseLog("Required padding does not match extra data", cExPath + '\'s file size!\nGenerating padding from scratch!')
			cExData = b'\x00' * cFilePadding
	else:
		log.verboseLog("Generating file padding! Amt:", cFilePadding)
		cExData = b'\x00' * cFilePadding
	return cExData

def packFiles(wDir, whDir, wxDir):
	cpkBytes = None
	cHeader = b''
	global cpkConfig
	fileIter = os.listdir(wDir)
	if cpkConfig["AutomaticImport"] == False:
		log.verboseLog("AutomaticImport set to false! Iterating over manually-defined files from Config.json!")
		fileIter = cpkConfig["Files"]
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
		# copy last file header to append EOF header thing
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

def packCPK(input, outDir):
	# Get output file path; output files in all-caps
	# since the game's files are named in all-caps
	outputFile = None
	if isinstance(outDir, str):
		outputFile = os.path.join(outDir, input[input.rindex(os.sep)+len(os.sep):].upper() + '.CPK')
	else:
		outputFile = os.path.join(input[:input.rindex(os.sep)], input[input.rindex(os.sep)+len(os.sep):].upper() + '.CPK')
	if os.path.isfile(outputFile) and log.args.newonly:
		log.alreadyExist(outputFile)
		return
	# get files and headers folder as
	# vars for easy repeated access
	filesDir = os.path.join(input, "Files")
	headersDir = os.path.join(input, "Headers")
	exDir = os.path.join(input, "ExtraData")
	global cpkConfig
	with open(os.path.join(input, "Config.json"), "r") as jsStream:
		cpkConfig = json.load(jsStream)
	if os.path.isdir(filesDir):
		if os.path.isdir(headersDir):
			print("Packing", input, "into CPK file...")
			# pack files into cpk
			cpkData = packFiles(filesDir, headersDir, exDir)
			# write file data to disk
			with open(outputFile, "wb") as cpkOut:
				cpkOut.write(cpkData)
		else:
			# TODO: Add ability to generate generic header, if that's even a good idea
			print("Warning! Could not locate Headers directory in", headersDir + "! Folder will not be packed into CPK!")
	else:
		print("Error! Could not locate Files directory in", filesDir + "! Folder will not be packed into CPK!")