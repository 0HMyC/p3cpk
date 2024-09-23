# CPK Files
CPK files are a custom file type that appears to have been created by ATLUS, which are used to pack multiple files within. It is important to note that they should not be confused with Criware CPK files, which are an entirely different format and only coincidentally use the same file extension.

Typically, the types of files packed into a CPK will be .[CIN](#what-is-a-cin-file) and .TMX files, as they serve a similar purpose to [EPL](https://amicitia.miraheze.org/wiki/EPL) files which contain a model (2D or 3D) inside (such as the Critical/All-Out-Attack cutins or any 3D models in Persona 3 Portable's events) in the Persona games from Persona 4 ownwards.

It should be noted that the formatting of CPK files is actually identical to ATLUS's [PAK](https://amicitia.miraheze.org/wiki/PAC) format, with only extremely minor differences that only result in tools built with PAK files in mind not being able to open CPK files as-is. As such, the following technical documentation largely applies to that format as well.

## Packed File Header
Each file stored in a CPK is preceeded by a header that is `0x100` bytes long. The following table lists the currently understood values of this header.

| Offset   | Datatype     | Length (bytes)   | Description                          |
| -------- | ------------ | ---------------- | ------------------------------------ |
| `0x00`   | String       | `0xFC`           | Contains the name of the packed file. Most CPKs will only use the first 0xE bytes of this region, filling the rest with random garbage data. |
| `0xFC`   | Unsigned Int | `0x04`           | The size of the packed file in bytes. |

The stored files bytes follow immediately afterward.
## File Alignment
While the file size listed in the header data is accurate for how large the file is, some files need to be padded in order to reach one of multiple byte alignments. Typically, this is the result of poor packing (such as a CIN file that was manually extracted from another CPK being packed into a different CPK as-is) causing a mismatch between the actual size of a file and the data stored in the file, or the size of the file falling just short or ahead of an expected alignment.

In both cases, extra data (typically null byte `0x00` padding) will have been added to the file in order to force the data in the CPK to align correctly. All data is aligned to increments of `0x40`.

## End of a CPK file
CPK Files typically end with a "null header," which is a duplicated version of the actual last file's header with the first character of the file name replaced with a null byte (null terminating it early,) and the file size is set to zero. However, this null header is not actually necessary for the game to know when the file has ended, so it is technically possible to use CPK files with no null header; however, this likely comes with a risk of the game crashing depending on where the CPK is loaded into memory and if any data is stored immediately after it.

# What is a .CIN File?
CIN files appear to be a custom type of type which includes 2D animation data, formatted essentially as 2D model information. There is little public documentation on this format outside of 010 Editor template files such as the ones created by [myself](https://github.com/0HMyC/010-Editor-Templates/blob/main/p3_cin.bt) and [Pioziomgames](https://github.com/Pioziomgames/010-Editor-Templates/blob/master/p3f_cin.bt), as well as whatever has been documented here.

Given that CIN files are basically always found contained within CPK files, it's relevant to include documentation on that format here.

## Anatomy of a CIN
Data in a CIN file is formatted in this order: the header (which includes information affecting how the animation works/looks) and a list of "Objects" which contain all frame/mesh data.

The structure of the header is as follows:

| Offset | Datatype             | Description |
|--------|----------------------|-------------|
| 0x00   | String               | Magic Bytes ("CIN"); 4 bytes long due to null termination. Not present in certain old/unused files. |
| 0x04   | Unsigned Short       | Unknown. Not present in certain old/unused files. |
| 0x06   | Unsigned Short       | Frame to pause animation on until the cutin has been "released." |
| 0x08   | Unsigned Short       | Total number of animation objects within the file. |
| 0x0A   | Unsigned Byte[22]    | Appears to be a list of colours to force/apply to animation objects. Exact formatting/order is not known. |

Following this header are the animation objects, which are essentially just a list of frames containing "chunks" that can define rendered shapes, texture masks (formatted much like shapes), and textured triangles. The number of chunks listed per-frame depends on the type of chunk and the complexity of the animation. Textured triangles, for example, tend to be made up of 5 chunks (possibly to be rendered in [TRIANGLE_STRIP](https://www.khronos.org/opengl/wiki/Primitive#Triangle_primitives) like fashion?), while shapes can be made of up to and possibly more than 21.

For the game to know when the end of a frame or animation objects data is, an "Ending Chunk" is appended to the end of a frame's chunks and the end of an object's frames respectively. For more details, see below.

The structure of these individual chunks are as follows:

| Offset  | Datatype       | Description |
|---------|----------------|-------------|
| 0x00    | [Enum\<Unsigned Byte\>](#cin-chunk-id-enum) | Defines what type of data this chunk creates. Always 0 if an ending chunk. |
| 0x01    | Byte           | Unknown, appears to define the "property" of data the chunk is setting; `CIN_MASK` and `CIN_SHAPE` chunks may set this to 1 to denote an exact starting/ending coordinate for a line, while otherwise being set to 2 for lines built in-between. Always -256 if a frame ending chunk. Always -512 if a object ending chunk. |
| 0x02    | Unsigned Short[4] | Defines amount of Red, Green, Blue or Alpha to multiply vertice by (255 == 1.0, 0 == 0.0). Only the most significant bytes for each value appear to be used, effectively limiting the data to being Unsigned Bytes (`0-255`). |
| 0x0A    | Short          | Starting X coordinate of vertice. |
| 0x0C    | Short          | Starting Y coordinate of vertice. |
| 0x0E    | Short          | Ending X coordinate of vertice. Used when drawing shapes or masks, as those are constructed as lines. |
| 0x10    | Short          | Ending Y coording of vertice. Used when drawing shapes or masks, as those are constructed as lines. |

### CIN Chunk ID Enum

The following is a table of the enum values used to define the CIN Chunk type (note that the names are made up as a quick explanation, not pulled from any official ATLUS source):

| Value | Name          | Description |
|-------|---------------|-------------|
| 0     | CIN_MASK      | Used to define the visible area of textured objects. Constructed as lines. |
| 1     | CIN_SHAPE     | Used to define area of a shape (typically flat coloured). Constructed as lines. |
| 2     | CIN_TEXTURE   | Used to define triangles of textured object. |
