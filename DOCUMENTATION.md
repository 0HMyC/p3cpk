# CPK Files
CPK files are a custom file type that appears to have been created by ATLUS, which are used to pack multiple files within. It is important to note that they should not be confused with Criware CPK files, which are an entirely different format and only coincidentally use the same file extension.

Typically, the types of files packed into a CPK will be .[CIN](#what-is-a-cin-file) and .TMX files, indicating they likely serve a similar purpose to .EPL files with a model (2D or 3D) inside (such as the Critical/All-Out-Attack Cut-Ins or any 3D models in Persona 3 Portable's events) in the Persona games from Persona 4 ownwards.

## Packed File Header
Each file stored in a CPK is preceeded by a header that is `0x100` bytes long. The following table lists the currently understood values of this header.

| Offset   | Datatype     | Length (bytes)   | Description                          |
| -------- | ------------ | ---------------- | ------------------------------------ |
| `0x00`   | String       | `0x0E`           | Contains the name of the packed file |
| `0x0E`   | N/A          | `0xFC`           | Currently unknown header data        |
| `0xFC`   | Unsigned Int | `0x04`           | The size of the packed file in bytes |

The stored file's bytes follow immediately afterward.
## File Alignment
While the file size listed in the header data is accurate for how large the file is, some files need to be padded in order to reach one of multiple byte alignments. Some files may have actual file data in this padding (Such as C04_1204.CPK, which seems to put single precision floats within these bytes,) indicating the data may serve a purpose beyond just aligning the given file.

These files are the exception, however, as most files either have null bytes `(0x00)` in this extra data, or have the same bytes repeated multiple times, meaning that the purpose behind the file padding is still unknown as of writing. 

The byte alignments appear to be based on the least significant byte `(0xFF000000 Little-Endian)`, and the known possible hex values for the alignments are as follows:

| Alignments   |
| ------------ |
| `0x00`       |
| `0x40`       |
| `0x80`       |
| `0xC0`       |

Files that would exceed the highest possible alignment of `0xC0` are padded to the next alignment of `0x00`.

## End of a CPK file
CPK Files typically end with a "null header," which is a duplicated version of the actual last file's header with the first character of the file name replaced with a null byte (null terminating it early,) and the file size is set to zero. However, this null header is not actually necessary for the game to know when the file has ended, so it is perfectly fine to have CPK files without the null header at the end.

# What is a .CIN File?
CIN files appear to be a custom type of type which includes 2D animation data, seemingly formatted like 2D model information. Currently, this format is practically undocumented; what little information there is on these files is primarily written here as CIN files are almost always found contained within CPK files, so it is relevant to include.

## Anatomy of a CIN
Currently, little to nothing is known about the data structure or how data is contained within CIN files. What is known is that most CIN files begin with a 0x2A byte long header of some sort, containing multiple unknown values.

The assumed structure of this header is as follows:

| Offset | Datatype             | Description |
|--------|----------------------|-------------|
| 0x00   | String               | Magic Bytes ("CIN"); 4 bytes long, though the 4th byte is a null-termination. |
| 0x04   | Unsigned Byte[28]    | Unknown. Some values tend to be consistent between many CIN files. |
| 0x20   | Unsigned Byte[10]    | Unknown. May only be padding, or something else. |

Following this header is the file data, which can define information such as the visible boundaries/bounding box of the animation (unconfirmed), texture mapping (unconfirmed), and the position, scale, and movement of animated objects. All of this data is defined in 18 byte "chunks", of which appear to be contained within groups denoted by a "null" chunk at the start and end, with 5 "data" chunks in between.

These 5 data chunks appear to be made up as essentially defining the four points of a Quad (a mesh with 4 vertices), with the fifth chunk always being a duplicate of the first; the reason for the duplication is not yet understood.

The structure of these individual chunks are as follows:

| Offset  | Datatype       | Description |
|---------|----------------|-------------|
| 0x00    | [Enum\<Unsigned Byte\>](#cin-chunk-id-enum)       | Defines what type of data this chunk creates. Always 0 if chunk denotes group end/start. |
| 0x01    | Byte           | Unknown; possibly refrence to animation object? Seems to be 0xFF or 0xFE is chunk is group end/start. |
| 0x02    | Unsigned Short[4] | Defines amount of Red, Green, Blue or Alpha to multiply image by (255 = 1.0, 0 = 0.0). Only the most significant bytes for each value appear to be used, effectively making the true datatype an Unsigned Byte. |
| 0x0A    | Short          | X coordinate of object vertex. |
| 0x0C    | Short          | Y coordinate of object vertex. |
| 0x0E    | Short          | Unknown. |
| 0x10    | Short          | Unknown. |

### CIN Chunk ID Enum

The following is a table of the enum values used to define the CIN Chunk type (note that the names are made up as a quick explanation, not pulled from any official ATLUS source):

| Value | Name          | Description |
|-------|---------------|-------------|
| 0     | UNK_VISBOUNDS | Unknown; may be used for defining the visible area/bounding box of the animation. |
| 1     | UNK_SEC_01    | Unknown; may be used for texture mapping (UV's.) |
| 2     | CIN_ANIMATION | Used to define mesh/animation data. |
