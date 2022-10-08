from enum import Enum, IntFlag
from utils.PyBinaryReader.binary_reader import *


class CCSFVersions(Enum):
    VER1 = 0x110
    VER2 = 0x120
    VER3 = 0x125


class CCSTypes(Enum):
    Header = 0x0001
    StringTable = 0x0002
    Null = 0x0003
    Stream = 0x0005
    Object = 0x0100
    Material = 0x0200
    Texture = 0x0300
    Color_Palette = 0x0400
    Camera = 0x0500
    Light = 0x0600
    Animation = 0x0700
    Model = 0x0800
    Clump = 0x0900
    External = 0x0a00
    HitModel = 0x0b00
    Bounding_Box = 0x0c00
    Particle = 0x0d00
    Effect = 0x0e00
    Blit_Group = 0x1000
    FrameBuffer_Page = 0x1100
    FrameBuffer_Rect = 0x1200
    Dummy_Position = 0x1300
    Dummy_Position_Rotation = 0x1400
    Layer = 0x1700
    Shadow = 0x1800
    Morpher = 0x1900
    Object2 = 0x2000
    PCM_Audio = 0x2200
    Binary_Blob = 0x2400
    EOF = 0xff01


class BrCCSFile(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.Header = br.read_struct(BrHeader)
        self.StringTable = br.read_struct(BrStringTable)
        self.Setup = br.read_struct(BrSetup)
        self.Chunks = list()
        while True:
            chunk = br.read_struct(BrChunk)
            if chunk.type == CCSTypes.EOF.value:
                break
            self.Chunks.append(chunk)


class BrHeader(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.ccs_type = br.read_uint32() & 0xFFFF
        assert self.ccs_type == CCSTypes.Header.value
        self.size = br.read_uint32() * 4
        self.magic = br.read_str(4)
        print(self.magic)
        self.filename = br.read_str(32)
        print(self.filename)
        self.version = br.read_uint32()
        global ccsf_version
        ccsf_version = self.version

        '''if ccsf_version < CCSFVersions.VER1.value:
            self.version_string = "CCSF Version 1"
        elif ccsf_version > CCSFVersions.VER2.value:
            self.version_string = "CCSF Version 2"
        elif ccsf_version > CCSFVersions.VER3.value:
            self.version_string = "CCSF Version 3"
        else:
            self.version_string = "Unknown CCSF Version"
'''


        self.unk = br.read_uint32(3)
        print(f'unknown values {self.unk}')


class BrStringTable(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.ccs_type = br.read_uint32() & 0xFFFF
        assert self.ccs_type == CCSTypes.StringTable.value
        self.size = br.read_uint32() * 4
        self.paths_count = br.read_uint32()
        self.names_count = br.read_uint32()

        self.paths = [br.read_str(32)[1:] for i in range(self.paths_count)]

        self.names = [(br.read_str(30), self.paths[br.read_uint16()])
                      for i in range(self.names_count)]


class BrSetup(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.ccs_type = br.read_uint32() & 0xFFFF
        assert self.ccs_type == CCSTypes.Null.value
        self.size = br.read_uint32() * 4


class BrChunk(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.type = br.read_uint32() & 0xFFFF
        #print(f'Position = {br.pos()}')
        #print(f'chunk type = {CCSTypes(self.type).name}')

        global chunk_size

        self.size = br.read_uint32()

        chunk_size = (self.size * 4)

        self.index = br.read_int32()

        print(f'position = {br.pos()}')
        if f'Br{CCSTypes(self.type).name}' in globals():
            chunktype = f'Br{CCSTypes(self.type).name}'
            self.data = br.read_struct(globals()[chunktype])

        else:
            print(CCSTypes(self.type).name)
            self.data = br.read_bytes((self.size * 4) - 4)


class BrClump(BrChunk):
    def __br_read__(self, br: BinaryReader):
        self.bone_count = br.read_uint32()
        self.bone_indices = [br.read_uint32()
                              for i in range(self.bone_count)]
        self.bones = [br.read_struct(BrBone) for i in range(self.bone_count)]


class BrBone(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.bone_pos = br.read_float(3)
        self.bone_rot = br.read_float(3)
        self.bone_scale = br.read_float(3)


class BrObject(BrChunk):
    def __br_read__(self, br: BinaryReader):
        self.ParentObjectID = br.read_uint32()
        #print(self.ParentObjectID)
        self.ModelID = br.read_uint32()
        #print(self.ModelID)
        self.ShadowID = br.read_uint32()
        #print(self.ShadowID)
        if ccsf_version > 0x120:
            self.unk = br.read_uint32()


class BrColor_Palette(BrChunk):
    def __br_read__(self, br: BinaryReader):
        self.BlitGroup = br.read_uint32()
        br.seek(8, 1)

        self.ColorCount = br.read_uint32()
        self.Palette = list()
        for i in range(self.ColorCount):
            B = br.read_uint8()
            G = br.read_uint8()
            R = br.read_uint8()
            A = br.read_uint8()

            self.Palette.append((B, G, R, min(255, A * 2)))

class BrTexture(BrChunk):
    def __br_read__(self, br: BinaryReader):
        self.ClutID = br.read_uint32()
       # print(f'ClutID = {self.ClutID}')
        self.BlitGroup = br.read_uint32()
        #print(f'BlitGroup = {self.BlitGroup}')
        self.TextureFlags = br.read_uint8()
        #print(f'TextureFlags = {self.TextureFlags}')
        self.TextureType = br.read_uint8()
        #print(f'TextureType = {self.TextureType}')
        self.MipmapsCount = br.read_uint8()
        #print(f'MipmapsCount = {self.MipmapsCount}')
        self.unk1 = br.read_uint8()
        #print(f'unk1 = {self.unk1}')
        self.Width = br.read_uint8()
        #print(f'Width = {self.Width}')
        self.Height = br.read_uint8()
        #print(f'Height = {self.Height}')
        self.unk2 = br.read_uint16()
        #print(f'unk2 = {self.unk2}')
        if ccsf_version < 0x120:
            self.ActualWidth = 1 << self.Width
            self.ActualHeight = 1 << self.Height
            self.unk3 = br.read_uint32()
        elif self.Width == 0xff or self.Height == 0xff:
            self.ActualWidth = br.read_uint16()
            self.ActualHeight = br.read_uint16()
            self.unk3 = br.read_uint16()
        elif self.TextureType == 0x87 or self.TextureType == 0x89:
            br.seek(0x10, 1)
            self.ActualHeight = br.read_uint16()
            self.ActualWidth = br.read_uint16()
            br.seek(0x14, 1)
        else:
            self.ActualWidth = 1 << self.Width
            self.ActualHeight = 1 <<self.Height
            self.unk4 = br.read_uint32()

        self.TextureDataSize = br.read_uint32()
        #print(f'TextureDataSize = {self.TextureDataSize}')

        if self.TextureType == 0x87 or self.TextureType == 0x89:
            br.seek(0xC, 1)
            self.TextureName = br.read_str(16)
            #print(f'TextureName = {self.TextureName}')
            self.TextureData = br.read_bytes(self.TextureDataSize - 0x40)
        else:
            self.TextureData = br.read_bytes(self.TextureDataSize << 2)

        #print(f'TextureData length = {len(self.TextureData)}')


class TextureTypes(Enum):
    RGBA32 = 0
    Indexed8 = 0x13
    Indexed4 = 0x14
    DXT1 = 0x87
    DXT5 = 0x89


class ModelTypes(IntFlag):
    Rigid1 = 0x0
    Rigid2   = 0x1
    Deformable = 0x4
    ShadowMesh = 0x8


class BrRigidMesh(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.ParentID = br.read_uint32()
        self.MatTexID = br.read_uint32()
        self.VertexCount = br.read_uint32()
        self.VertexPositions = [br.read_int16(3) for i in range(self.VertexCount)]

        if br.pos() % 4 == 2:
            br.read_uint16()

        self.VertexNormals = [(br.read_uint8(3), br.read_uint8()) for i in range(self.VertexCount)]
        self.VertexColors = [br.read_uint8(4) for i in range(self.VertexCount)]
        
        if ccsf_version > 0x125:
            self.VertexUVs = [br.read_uint32(2) for i in range(self.VertexCount)]
        else:
            self.VertexUVs = [br.read_uint16(2) for i in range(self.VertexCount)]
        

class BrShadowMesh(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.VertexCount = br.read_uint32()
        self.TriangleVerticesCount = br.read_uint32()
        self.VertexPositions = list()
        self.Triangles = list()

        for i in range(self.VertexCount):
            self.VertexPositions.append(br.read_int16(3))
        
        for i in range((self.TriangleVerticesCount // 3)):
            self.Triangles.append(br.read_int32(3))


class BrModel(BrChunk):
    def __br_read__(self, br: BinaryReader):
        self.VertexScale = br.read_float()
        self.ModelType = br.read_uint8()
        self.MeshFlags = br.read_uint8()
        self.MeshCount = br.read_uint16()
        self.SourceFactor = br.read_uint8()
        self.DestinationFactor = br.read_uint8()
        self.UnkFlags = br.read_uint16()
        self.unk = br.read_uint32()

        if ccsf_version > 0x110:
            self.OutlineColor = br.read_uint8(4)
            self.OutlineWidth = br.read_float()

        self.Meshes = list()

        if self.MeshCount > 0:
            if self.ModelType < ModelTypes.Deformable:
                for i in range(self.MeshCount):
                    rigidmesh = br.read_struct(BrRigidMesh)
                    self.Meshes.append(rigidmesh)
            
            elif self.ModelType == ModelTypes.Deformable:
                count = chunk_size - (0x3c * self.MeshCount)
                br.read_bytes(count)

            elif self.ModelType == ModelTypes.ShadowMesh:
                br.read_struct(BrShadowMesh)
            
            elif self.ModelType == ModelTypes.Dummy:
                print('Dummy model')


class BrVertex(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.posX = br.read_int16()
        self.posY = br.read_int16()
        self.posZ = br.read_int16()
