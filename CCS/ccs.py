from brccs import *


class CCSFile:
    def __init__(self):
        self.version = 0
        global ccsf_version  # I need to find a better way to do this
        ccsf_version = self.version
        self.paths = list()
        self.names = list()
        self.chunks: list[CCSChunk] = list()

    def get_chunks_by_type(self, chunk_type: CCSTypes):
        return [chunk for chunk in self.chunks if chunk.type == chunk_type]
    
    def get_chunks_by_name(self, name: str):
        return [chunk for chunk in self.chunks if chunk.name == name]
    

class CCSChunk:
    def __init__(self, chunk: BrChunk, string_table: BrStringTable = None, chunks: list[BrChunk] = None):
        self.name = string_table.names[chunk.index][0]
        self.type = CCSTypes(chunk.type).name
        self.index = chunk.index
        self.data = chunk.data

        self.brchunks = chunks
    

class Clump(CCSChunk):
    def init_data(self, chunk: BrClump, string_table: BrStringTable = None):
        self.bone_count = chunk.bone_count
        self.bone_indices = chunk.bone_indices
        self.bones = list()
        for b, i in zip(chunk.bones, chunk.bone_indices):
            self.bones.append(Bone(b, i, string_table, self.brchunks))


class Bone:
    def __init__(self, bone: BrBone, index, string_table: BrStringTable = None, chunks: list[BrChunk] = None):
        self.name = string_table.names[index][0]
        self.index = index

        parentindex: BrObject = list(filter(lambda x: x.index == index, chunks))[0].data.ParentObjectID
        
        self.parent = string_table.names[parentindex][0]
        self.position = bone.bone_pos
        self.rotation = bone.bone_rot
        self.scale = bone.bone_scale


class Object(CCSChunk):
    def init_data(self, chunk: BrObject, string_table: BrStringTable = None):
        self.ParentObject = string_table.names[chunk.ParentObjectID][0]
        self.Model = string_table.names[chunk.ModelID][0]
        self.Shadow = string_table.names[chunk.ShadowID][0]
        if ccsf_version > 0x120:
            self.unk = chunk.unk


class Color_Palette(CCSChunk):
    def init_data(self, chunk: BrColor_Palette, string_table: BrStringTable = None):
        self.BlitGroup = chunk.BlitGroup
        self.ColorCount = chunk.ColorCount
        self.Palette = chunk.Palette


class Texture(CCSChunk):
    def init_data(self, chunk: BrTexture, string_table: BrStringTable = None):
        self.Clut = string_table.names[chunk.ClutID][0]
        self.BlitGroup = chunk.BlitGroup
        self.TextureFlags = chunk.TextureFlags
        self.TextureType = TextureTypes(chunk.TextureType).name
        self.MipmapsCount = chunk.MipmapsCount
        self.Width = chunk.ActualWidth
        self.Height = chunk.ActualHeight

        self.TextureData = chunk.TextureData


class Model(CCSChunk):
    def init_data(self, chunk: BrModel, string_table: BrStringTable = None):
        self.VertexScale = chunk.VertexScale
        self.ModelType = ModelTypes(chunk.ModelType).name
        self.MeshFlags = chunk.MeshFlags
        self.MeshCount = chunk.MeshCount
        self.SourceFactor = chunk.SourceFactor
        self.DestinationFactor = chunk.DestinationFactor
        self.UnkFlags = chunk.UnkFlags
        self.unk = chunk.unk

        if ccsf_version > 0x110:
            self.OutlineColor = chunk.OutlineColor
            self.OutlineWidth = chunk.OutlineWidth
        
        if self.MeshCount > 0:
            self.meshes = list()
            for mesh in chunk.Meshes:
                if self.ModelType == "Rigid1" or self.ModelType == "Rigid2":
                    self.meshes.append(RigidMesh(mesh, string_table))
        else:
            self.meshes = None


class RigidMesh:
    def __init__(self, mesh: BrRigidMesh, string_table: BrStringTable = None):
        self.Parent = string_table.names[mesh.ParentID][0]
        self.Material = string_table.names[mesh.MatTexID][0]
        self.Vertices = list()
        self.Triangles = list()

        for i in range(mesh.VertexCount):
            self.Vertices.append(Vertex(mesh.VertexPositions[i],
            mesh.VertexNormals[i][0], mesh.VertexColors[i],
            mesh.VertexUVs[i], mesh.VertexNormals[i][1]))
        

class Vertex:
    def __init__(self, position = None, normal = None, color = None, uv = None, triangleflag = None):
        self.Position = (position[0] / 32767, position[1] / 32767, position[2] / 32767)
        self.Normal = (normal[0] / 32767, normal[1] / 32767, normal[2] / 32767)
        self.Color = color
        self.UV = uv
        self.TriangleFlag = triangleflag
        

class MeshFlags(IntFlag):
    Outline = 0x8
    Material = 0x10
    Unk = 0x20