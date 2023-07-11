import os
import rcpk

def findCPKS(start, outDir):
	for filFol in os.listdir(start):
		cur = os.path.join(start, filFol)
		# Check if we need to search through more folders,
		# or extract a CPK. TODO: better comparision method than .lower()?
		if os.path.isdir(cur):
			findCPKS(cur, outDir)
		elif os.path.isfile(cur) and cur.lower().endswith('.cpk'):
			print("Unpacking", cur)
			unpackCPK(cur, outDir)

def unpackCPK(input, outDir):
	cpkBytes = None
	# Get output folder
	outputFolder = None
	if isinstance(outDir, str):
		outputFolder = os.path.join(outDir, input[input.rindex('/')+1:-4] + '_extracted')
	else:
		outputFolder = os.path.join(input[:input.rindex('/')], input[input.rindex('/')+1:-4] + '_extracted')
	os.makedirs(outputFolder, exist_ok=True) # Make output folder if it doesn't exist
	#Read CPK file to unpack
	with open(input, "rb") as rCPK:
		cpkBytes = rCPK.read(os.path.getsize(input))
	i = 0
	while i < len(cpkBytes):
		cHeader = rcpk.readHeader(cpkBytes[i:i+0x100])
		# if cHeader is ever -1 that means the read failed/
		# we're at the end of the file
		if cHeader == -1:
			break
		cFile = cpkBytes[i+0x100:(i+0x100)+cHeader["FileSize"]]
		i += 0x100 + cHeader["FileSize"]
		#Create output directories that we need
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