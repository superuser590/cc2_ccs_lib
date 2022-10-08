from ccs import CCSChunk
from brccs import BrCCSFile, CCSTypes
from ccs import *
from utils.PyBinaryReader.binary_reader import *
import json

def read_ccs(file):
    with open(file, 'rb') as f:
        file_bytes = f.read()

    with BinaryReader(file_bytes, Endian.LITTLE, 'cp932') as br:
        ccs_file: BrCCSFile = br.read_struct(BrCCSFile)

    table = ccs_file.StringTable

    ccs: CCSFile = CCSFile()
    ccs.names = table.names
    ccs.paths = table.paths
    ccs.version = ccs_file.Header.version

    for brchunk in ccs_file.Chunks:
        # check if chunk type exists in globals
        if CCSTypes(brchunk.type).name in globals():
            chunk = globals()[CCSTypes(brchunk.type).name](brchunk, table, ccs_file.Chunks)
            chunk.init_data(brchunk.data, table)
            ccs.chunks.append(chunk)
        else:
            ccs.chunks.append(CCSChunk(brchunk, table))
    
    return ccs
