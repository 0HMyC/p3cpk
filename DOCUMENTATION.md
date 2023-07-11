# What is a .CPK File?
CPK files are a filetype most likely custom-made by ATLUS, which are used to contain multiple files inside.

Typically, the types of files packed into a CPK are CIN and TMX files, indicating they serve a similar purpose
to EPL's containing a 2D Model in more modern Persona titles, such as Persona 3 Portable.

# Anatomy of a CPK
Files in a CPK have their data preceeded by an internal header that is 0x100 bytes long. The following table is
the currently known parts of the header.

| Offset | Datatype | Length (bytes) | Description |
| ------ | -------- | -------------- | ----------- |
| 0x0    | String   | 0x10           | Contains the name of the packed file |
| 0xFC   | Unsigned Int | 0x4        | The size of the packed file in bytes |

The bytes of the packed file follow immediately afterward.
## File Byte Alignment
While the file size listed in the header data is generally accurate, some files need to be padded in order to reach
one of multiple byte alignments. The reasoning for the padding is not yet known or understood.

The byte alignments appear to be based on the rightmost byte, and are as follows:

| Alignments |
| ---------- |
| 0x0        |
| 0x40 |
| 0x80 |
| 0xC0 |

## End of CPK file
The end of a CPK file appears to be determined by whether or not the first byte of the file name is a null byte.
As such, it seems that these "end-of-file" headers wind up being duplicated from the actual last file, with the
name being null terminated at the first-character.
