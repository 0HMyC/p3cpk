import os
import rcpk
import logger as log

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
		elif os.path.isfile(cur) and cur.lower().endswith('.cpk'):
			log.compliantLog("Converting", cur)
			convertCPK(cur, outDir)

def convertCPK(input, outDir):
	cpkBytes = None
	pakBytes = b''
	rcpk.log.args = log.args
	with open(input, "rb") as cpkStream:
		cpkBytes = cpkStream.read(os.path.getsize(input))
	i = 0
	while i < len(cpkBytes):
		cFileName = ''
		# Account for padding headers which are usually duplicates of the previous header
		# that null terminate on the first character
		if cpkBytes[i] != 0:
			cFileName = rcpk.readFileName(cpkBytes[i:i+0xFC])
		else:
			cFileName = rcpk.readFileName(cpkBytes[i+1:i+0xFC])
		pakNullBytes = b'\x00'*(0xFC - len(cFileName))
		pakBytes += cpkBytes[i:i+len(cFileName)] + pakNullBytes + cpkBytes[i+0xFC:i+0x100]
		cFileSize = rcpk.unpack('<I', cpkBytes[i+0xFC:i+0x100])
		cFileSize += rcpk.getPaddingAmt(cFileSize)
		pakBytes += cpkBytes[i+0x100:i+0x100+cFileSize]
		i += 0x100 + cFileSize
		log.verboseLog(cFileName, cFileSize - 0x100, len(pakBytes))
	outputFolder = ''
	if isinstance(outDir, str):
		# Create mirrored output directory
		if isinstance(initPath, str):
			outputFolder = os.path.join(outDir, input[len(initPath)+len(os.sep):input.rindex(os.sep)])
		else:
			outputFolder = outDir
		log.verboseLog(outputFolder)
	else:
		# Store output PAK in input directory
		outputFolder = input[:input.rindex(os.sep)]
	os.makedirs(outputFolder, exist_ok=True) # Make output folder if it doesn't exist
	outputPath = os.path.join(outputFolder, input[input.rindex(os.sep)+len(os.sep):-4] + '.pac')
	if os.path.isfile(outputPath) and log.args.newonly:
		log.alreadyExist(outputPath)
		return
	with open(outputPath, "wb") as pakStream:
		pakStream.write(pakBytes)
	log.verboseLog("Converted " + input + " to PAK!")