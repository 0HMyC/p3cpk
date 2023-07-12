# What is a .CPK File?
CPK files are a type of file custom-made by ATLUS, which are used to contain multiple files inside. It should be noted that these are not the same as Criware CPK files, which are a different format entirely and only coincidentally use the same file extension.

Typically, the types of files packed into a CPK are CIN and TMX files, indicating they serve a similar purpose
to EPL's which contain a 2D Model in Persona games from Persona 4 onward.

# Anatomy of a CPK
Files in a CPK have their data preceeded by an internal header that is 0x100 bytes long. The following table is
the currently known parts of the header.

| Offset | Datatype     | Length (bytes) | Description                          |
| ------ | ------------ | -------------- | ------------------------------------ |
| 0x00   | String       | 0x0E           | Contains the name of the packed file |
| 0x0E   | N/A          | 0xFC           | Currently unknown header data        |
| 0xFC   | Unsigned Int | 0x04           | The size of the packed file in bytes |

The bytes of the packed file follow immediately afterward.
## File Byte Alignment
While the file size listed in the header data is accurate for how large the file is, some files need to be padded in order to reach one of multiple different byte alignments. The reasoning for the padding is not yet known or understood.

The byte alignments appear to be based on the rightmost byte `(0x000000FF)`, and are as follows:

| Alignments |
| ---------- |
| 0x00       |
| 0x40       |
| 0x80       |
| 0xC0       |

## End of CPK file
The end of a CPK file is determined by a "null header," which is a duplicated version of the last file packed into the CPK's header with the main differences being that the file name is null-terminated early, and the file size is set to zero.
