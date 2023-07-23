# What is a .CPK File?
CPK files are a type of file custom-made by ATLUS, which are used to contain multiple files within. It should be noted that these are not the same kind of CPK file as Criware CPK files, which are an entirely different format and only coincidentally use the same file extension.

Typically, the types of files packed into a CPK will be .CIN and .TMX files, indicating they likely serve a similar purpose to .EPL files which contain a 2D animated model (such as the Critical/All-Out-Attack Cut-Ins) in the Persona games from Persona 4 ownwards.

# Anatomy of a CPK
Each file stored in a CPK is preceeded by a header that is 0x100 bytes long. The following table lists the currently understood values of this header.

| Offset | Datatype     | Length (bytes) | Description                          |
| ------ | ------------ | -------------- | ------------------------------------ |
| 0x00   | String       | 0x0E           | Contains the name of the packed file |
| 0x0E   | N/A          | 0xFC           | Currently unknown header data        |
| 0xFC   | Unsigned Int | 0x04           | The size of the packed file in bytes |

The stored file's bytes follow immediately afterward.
## File Byte Alignment
While the file size listed in the header data is accurate for how large the file is, some files need to be padded in order to reach one of multiple different byte alignments. The reasoning for the padding is not yet known or understood.

The byte alignments appear to be based on the least significant byte `(0x000000FF)`, and the possible hex values for the alignments are as follows:

| Alignments |
| ---------- |
| 0x00       |
| 0x40       |
| 0x80       |
| 0xC0       |

## End of CPK file
The end of a CPK file is determined by a "null header," which is a duplicated version of the last file packed into the CPK's header with the main differences being that the file name is null-terminated early, and the file size is set to zero.
