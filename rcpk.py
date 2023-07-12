import struct

logVerbose = False

def verboseLog(*inp):
	if logVerbose:
		print(*inp)

def unpack(fmt, bytes):
	return struct.unpack(fmt, bytes)[0]

def readFileName(bytes):
	cStr = ""
	for i in range(len(bytes)):
		if bytes[i] != 0:
			cStr += chr(bytes[i])
		else:
			verboseLog("String null termination at", i, cStr)
			break
	return cStr

def correctFileSize(inpSize):
	extraOffset = inpSize & 0xFF
	#if this is true, the file is properly aligned, and we don't have anything to do
	if extraOffset == 0 or extraOffset == 0x40 or extraOffset == 0x80 or extraOffset == 0xC0:
		return inpSize
	else:
		shiftedSize = (inpSize >> 8) << 8 #remove rightmost byte
		if extraOffset > 0xC0:
			extraOffset = (0x100 + shiftedSize) - inpSize
		elif extraOffset > 0xA0:
			if extraOffset < 0xC0:
				extraOffset = (0xC0 + shiftedSize) - inpSize
		else:
			if extraOffset > 0x40:
				extraOffset = (0x80 + shiftedSize) - inpSize if extraOffset < 0x80 else (0xC0 + shiftedSize) - inpSize
			else:
				extraOffset = (0x40 + shiftedSize) - inpSize
	return inpSize + extraOffset

def readHeader(header):
	fileHeader = {
		"FileName": None,
		"Unknown0": None,
		"FileSize": None
		}
	# load header data into dict
	fileHeader["FileName"] = readFileName(header[:14])
	if fileHeader["FileName"] == "":
		verboseLog("File name started with null termination! Not reading file!")
		return -1
	fileHeader["Unknown0"] = header[14:0xFC]
	fileHeader["FileSize"] = correctFileSize(unpack('<I', header[0xFC:0x100]))
	return fileHeader