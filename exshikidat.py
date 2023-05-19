import os
import struct
import base64
import bytesfunc
import click
from operator import xor

ContentKey = "XYzdN48qMxzsMgnJSBFQ+JRdkerx5p4JUjJtdHX3UkXEiRdJ6cCDsLMII6DKmS5ZEBQR5LbEhsk+D0TKG1IUXSNb6tweYGl9RmvJZ9nTxeFjPOXjYL3gqN4BU8sBSJ/SDlS2Lhu01kjeXbAFO7WZps9ifOTk67OH6cRDHC6dvkWfwzxNBoORZ0qiVivDuZ+janPzHHAyMkPd6pAtGnGDbaZ+CXNguoT04S5CNT+o8E2+M0HoW4TCU7Azgeu+owhINjzbY9gG4J2ZVQsBT8iirHOw8KJqFKCp0J7hd7TnzdYJwTr7qbYWyHapmnHg9nvRylhFK/IoNi7vn2pJPLy1z84srg=="
def name_from_bytes(bytes):
    return bytes.split(b'\x00')[0].decode('cp932')
def xor_bytes(sequence1,sequence2):
    result = bytearray([0 for i in range(len(sequence1))])
    bytesfunc.xor(sequence1,sequence2,result)
    return result
@click.command()
@click.option('--file', '-f' , 'FILENAME', help="input file path", required=True)
@click.option('--outdir', '-o' , 'OUTPUTDIR', default="extracted", help="directory name for extracted output", required=False)
@click.option('--extract', '-x' , 'EMODE', help="for extract mode. default is view mode", is_flag=False, flag_value="click")
def unpack(FILENAME, OUTPUTDIR, EMODE):
    with open(FILENAME,'rb') as f:
        data = f.read()
        count = xor(struct.unpack("H" , data[:2])[0], 0x8080)
        print('total {0} files!'.format(count))
        name_length = 0x100
        entry = []
        for i in range(count):
            name_offset = 2
            if i:
                name_offset =  2 + ((name_length + 10) * i)
            name = xor_bytes(data[name_offset:name_offset+name_length], 0x80)
            print('found {0} '.format(name_from_bytes(name)))
            if EMODE:
                info_offset = (name_length + 4) + (i * (name_length + 10))
                info = xor_bytes(data[info_offset:info_offset+8], 0x80)
                size = struct.unpack("I" , info[:4])[0]
                offset = struct.unpack("I" , info[-4:])[0]
                key = base64.b64decode(ContentKey)
                encrypted = min(size, len(key))
                header = xor_bytes(data[offset:offset+encrypted], key[:encrypted])
                output_dir = os.path.abspath(OUTPUTDIR)
                if not os.path.exists(output_dir):
                    os.mkdir(output_dir)
                with open(os.path.join(output_dir,name_from_bytes(name)),'wb') as arc:
                    arc.write(header+data[offset+encrypted:offset+size])
        if EMODE:
            print("extract done!")
if __name__ == '__main__':
    unpack()

