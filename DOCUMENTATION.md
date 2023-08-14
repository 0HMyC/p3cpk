# What is a .CPK File?
CPK files are a custom file type which appears to have been created by ATLUS, that used to contain multiple files within. It should be noted that these are not the same kind of CPK file as Criware CPK files, which are an entirely different format and only coincidentally use the same file extension.

Typically, the types of files packed into a CPK will be .CIN and .TMX files, indicating they likely serve a similar purpose to .EPL files with a model (2D or 3D) inside (such as the Critical/All-Out-Attack Cut-Ins or any 3D models in Persona 3 Portable's events) in the Persona games from Persona 4 ownwards.

# Anatomy of a CPK
Each file stored in a CPK is preceeded by a header that is 0x100 bytes long. The following table lists the currently understood values of this header.

| Offset | Datatype     | Length (bytes) | Description                          |
| ------ | ------------ | -------------- | ------------------------------------ |
| 0x00   | String       | 0x0E           | Contains the name of the packed file |
| 0x0E   | N/A          | 0xFC           | Currently unknown header data        |
| 0xFC   | Unsigned Int | 0x04           | The size of the packed file in bytes |

The stored file's bytes follow immediately afterward.
## File Byte Alignment
While the file size listed in the header data is accurate for how large the file is, some files need to be padded in order to reach one of multiple different byte alignments. Some files appear to place actual file data in this padding (Such as C04_1204.CPK, which seems to place Single precision floats within this supposed padding,) indicating it serves a purpose beyond just aligning the file correctly. These files are the exception, however, as most files either have null bytes in this extra data, or have repeated bytes with no clear purpose, meaning that the purpose behind the file padding is still unknown as of writing. 

The byte alignments appear to be based on the least significant byte `(0x000000FF)`, and the known possible hex values for the alignments are as follows:

| Alignments |
| ---------- |
| 0x00       |
| 0x40       |
| 0x80       |
| 0xC0       |

## End of CPK file
CPK Files typically end with a "null header," which is a duplicated version of the actual last file's header with the first character of the file name replaced with a null byte (null terminating it early,) and the file size is set to zero. However, this null header is not actually necessary for the game to know when the file has ended, so it is perfectly fine to have CPK files without the null header at the end.
