# What is a .CPK File?
CPK files are a custom file type which appears to have been created by ATLUS, that used to contain multiple files within. It should be noted that these are not the same kind of CPK file as Criware CPK files, which are an entirely different format and only coincidentally use the same file extension.

Typically, the types of files packed into a CPK will be .CIN and .TMX files, indicating they likely serve a similar purpose to .EPL files with a model (2D or 3D) inside (such as the Critical/All-Out-Attack Cut-Ins or any 3D models in Persona 3 Portable's events) in the Persona games from Persona 4 ownwards.

## Anatomy of a CPK
Each file stored in a CPK is preceeded by a header that is 0x100 bytes long. The following table lists the currently understood values of this header.

| Offset | Datatype     | Length (bytes) | Description                          |
| ------ | ------------ | -------------- | ------------------------------------ |
| 0x00   | String       | 0x0E           | Contains the name of the packed file |
| 0x0E   | N/A          | 0xFC           | Currently unknown header data        |
| 0xFC   | Unsigned Int | 0x04           | The size of the packed file in bytes |

The stored file's bytes follow immediately afterward.
## File Byte Alignment
While the file size listed in the header data is accurate for how large the file is, some files need to be padded in order to reach one of multiple different byte alignments. Some files appear to place actual file data in this padding (Such as C04_1204.CPK, which seems to place Single precision floats within this supposed padding,) indicating it serves a purpose beyond just aligning the file correctly. These files are the exception, however, as most files either have null bytes in this extra data, or have repeated bytes with no clear purpose, meaning that the purpose behind the file padding is still unknown as of writing. 

The byte alignments appear to be based on the least significant byte `(0xFF000000 Little-Endian)`, and the known possible hex values for the alignments are as follows:

| Alignments |
| ---------- |
| 0x00       |
| 0x40       |
| 0x80       |
| 0xC0       |

Files that would exceed the highest possible alignment of 0xC0 are padded to the next increment of 0x40, effectively meaning it is padded to the next 0x00 alignment.

## End of CPK file
CPK Files typically end with a "null header," which is a duplicated version of the actual last file's header with the first character of the file name replaced with a null byte (null terminating it early,) and the file size is set to zero. However, this null header is not actually necessary for the game to know when the file has ended, so it is perfectly fine to have CPK files without the null header at the end.

# What is a .CIN File?
CIN files appear to be a custom type of type which includes model data and/or model animation data. Currently, this format is practically undocumented; what little information there is on these files is primarily written here as CIN files are almost always found contained within CPK files, so it is relevant to include.

## Anatomy of a CIN
Currently, little to nothing is known about the data structure or how data is contained within CIN files. What is known is that most CIN files begin with a 0x20 byte long header of some sort, containing multiple unknown values.

The speculated structure of this header is as follows:

| Offset | Datatype | Description |
|--------|----------|-------------|
| 0x00   | String   | Magic Bytes ("CIN"); 4 bytes long, though the 4th byte is a null-termination. |
| 0x04   | Short    | Unknown. Appears to be set to 1 in most CIN files. |
| 0x06   | Short    | Unknown.    |
| 0x08   | Short    | Unknown.    |
| 0x0A   | Signed Short | Unknown. Possibly a position/bounding box coordinate? |
| 0x0C   | Short    | Unknown. Possibly a reserved/null value? |
| 0x0E   | Signed Short | Unknown. Possibly a position/bounding box coordinate? | 
| 0x10   | Short    | Unknown. Possibly a reserved/null value? |
| 0x12   | Signed Short | Unknown. Possibly a position/bounding box coordinate? |
| 0x14   | Short    | Unknown. Possibly a reserved/null value? |
| 0x16   | Signed Short | Unknown. Possibly a position/bounding box coordinate? |
| 0x18   | Short    | Unknown. Possibly a reserved/null value? |
| 0x1A   | Signed Short | Unknown. Possibly a position/bounding box coordinate? |
| 0x1C   | Short    | Unknown. Possibly a reserved/null value? |
| 0x1E   | Signed Short | Unknown. Possibly a position/bounding box coordinate? |

Following this header is the data of the file; it can be assumed this data contains model data (vertices, normals, etc. etc.) and/or animation data (ie keyframes). Typically, a CIN file will end after this data, however, some files do have additional files (typically TMX textures) packed in after the normal CIN data, with the same structuring as a CPK file as listed above.
