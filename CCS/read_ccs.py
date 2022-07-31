from utils import *
from enum import Enum

#from binary_reader import *

file = r""

with open(file, 'rb') as f:
    file_bytes = f.read()

ccsf_versions = {'VER1': 0x110, 'VER2': 0X120, 'VER3': 0X125}

#dict of data types found in ccs files
data_types = {0x0001: 'Header',
              0x0002: 'Path',
              0x0003: 'Null',
              0x0005: 'Stream',
              0x0100: 'Object',
              0x0200: 'Material',
              0x0300: 'Texture',
              0x0400: 'Color Palette',
              0x0500: 'Camera',
              0x0600: 'Light',
              0x0700: 'Animation',
              0x0800: 'Model',
              0x0900: 'Clump',
              0x0A00: 'External?',
              0x0B00: 'HitModel',
              0x0C00: 'Bounding Box',
              0x0D00: 'Particle',
              0x0E00: 'Effect',
              0x1000: 'Blit Group',
              0x1100: 'FrameBuffer Page',
              0x1200: 'FrameBuffer Rect',
              0x1300: 'Dummy(Position)',
              0x1400: 'Dummy(Position & Rotation)',
              0x1700: 'Layer',
              0x1800: 'Shadow',
              0x1900: 'Morpher',
              0x2000: 'Object 2',
              0x2200: 'PCM Audio',
              0x2400: 'Binary Blob',
              0xFF01: 'EOF'
              }

class data_types_enum(Enum):
    Header                  = 0x0001
    StringTable             = 0x0002
    Null                    = 0x0003
    Stream                  = 0x0005
    Object                  = 0x0100
    Material                = 0x0200
    Texture                 = 0x0300
    Color_Palette           = 0x0400
    Camera                  = 0x0500
    Light                   = 0x0600
    Animation               = 0x0700
    Model                   = 0x0800
    Clump                   = 0x0900
    External                = 0x0a00
    HitModel                = 0x0b00
    Bounding_Box            = 0x0c00
    Particle                = 0x0d00
    Effect                  = 0x0e00
    Blit_Group              = 0x1000
    FrameBuffer_Page        = 0x1100
    FrameBuffer_Rect        = 0x1200
    Dummy_Position          = 0x1300
    Dummy_Position_Rotation = 0x1400
    Layer                   = 0x1700
    Shadow                  = 0x1800
    Morpher                 = 0x1900
    Object2                 = 0x2000
    PCM_Audio               = 0x2200
    Binary_Blob             = 0x2400
    EOF                     = 0xff01

class CCSFile(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.Header = br.read_struct(Header)
        self.StringTable = br.read_struct(StringTable)
        self.Setup = br.read_struct(Setup)

        #self.data_sections: [] = list()

class Header(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.ccs_type = br.read_uint32() & 0xFFFF
        assert self.ccs_type == data_types_enum.Header.value
        self.size = br.read_uint32() * 4
        self.magic = br.read_str(4)
        print(self.magic)
        self.filename = br.read_str(32)
        print(self.filename)
        self.version = br.read_uint32()
        print(self.version)
        if self.version > ccsf_versions.get('VER1') and self.version < ccsf_versions.get('VER2'):
            print('version 1')
        elif self.version > ccsf_versions.get('VER2') and self.version < ccsf_versions.get('VER3'):
            print('version 2')
        else:
            print('version 3')
        self.unk = br.read_uint32(3)
        print(f'unknown values {self.unk}')

class StringTable(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.ccs_type = br.read_uint32() & 0xFFFF
        assert self.ccs_type == data_types_enum.StringTable.value
        self.size = br.read_uint32() * 4
        self.paths_count = br.read_uint32()
        self.names_count = br.read_uint32()

        self.paths = [br.read_str(32)[1:] for i in range(self.paths_count)]

        for path in self.paths:
            print(path)
        
        self.names = [(br.read_str(30), self.paths[br.read_uint16()]) for i in range(self.names_count)]

        for name in self.names:
            print(name[0], name[1])

class Setup(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.ccs_type = br.read_uint32() & 0xFFFF
        assert self.ccs_type == data_types_enum.Null.value
        self.size = br.read_uint32() * 4

class Clump(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.ccs_type = br.read_uint32() & 0xFFFF
        self.size = br.read_uint32() * 4
        self.index = br.read_int32()
        self.bones_count = br.read_uint32()
        self.bones_indices = [br.read_uint32() for i in range(bones_count)]
        for bone in self.bones_indices:
            self.bone_loc = br.read_uint32(3)
            self.bone_rot = br.read_float(3)


with BinaryReader(file_bytes, Endian.LITTLE, 'cp932') as br:
    ccs_file: CCSFile = br.read_struct(CCSFile)
    #print(data_types_enum(ccs_file.StringTable.ccs_type).name)