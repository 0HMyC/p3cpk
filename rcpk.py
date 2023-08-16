import struct
import logger as log

def unpack(fmt, bytes):
	return struct.unpack(fmt, bytes)[0]

def readFileName(bytes):
	cStr = ""
	for i in range(len(bytes)):
		if bytes[i] != 0:
			cStr += chr(bytes[i])
		else:
			log.verboseLog("String null terminated early at", i, "| Final String:", cStr)
			break
	return cStr

def getPaddingAmt(inpSize):
	extraOffset = inpSize & 0xFF
	# if this is true, the file is properly aligned, and we don't have anything to do
	if extraOffset == 0 or extraOffset == 0x40 or extraOffset == 0x80 or extraOffset == 0xC0:
		return 0
	else:
		shiftedSize = (inpSize >> 8) << 8 #remove rightmost byte
		if extraOffset < 0x40:
			extraOffset = (0x40+shiftedSize) - inpSize
		elif extraOffset < 0x80:
			extraOffset = (0x80+shiftedSize) - inpSize
		elif extraOffset < 0xC0:
			extraOffset = (0xC0+shiftedSize) - inpSize
		else: # always runs if above 0xC0
			extraOffset = (0x100+shiftedSize) - inpSize
	return extraOffset

def readHeader(header):
	fileHeader = {}
	# load header data into dict
	fileHeader["FileName"] = readFileName(header[:14])
	if fileHeader["FileName"] == "":
		log.verboseLog("File name started with null termination! Not reading file!\n")
		return -1
	log.verboseLog("Unpacking file", fileHeader["FileName"], "from CPK...")
	fileHeader["Unknown0"] = header[14:0xFC]
	fileHeader["FileSize"] = unpack('<I', header[0xFC:0x100])
	# Get offset to skip over file padding
	fileHeader["FilePadding"] = getPaddingAmt(fileHeader["FileSize"])
	return fileHeader