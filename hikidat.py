import os
import struct
import base64
import bytesfunc
import click
from operator import xor

ContentKey = "XYzdN48qMxzsMgnJSBFQ+JRdkerx5p4JUjJtdHX3UkXEiRdJ6cCDsLMII6DKmS5ZEBQR5LbEhsk+D0TKG1IUXSNb6tweYGl9RmvJZ9nTxeFjPOXjYL3gqN4BU8sBSJ/SDlS2Lhu01kjeXbAFO7WZps9ifOTk67OH6cRDHC6dvkWfwzxNBoORZ0qiVivDuZ+janPzHHAyMkPd6pAtGnGDbaZ+CXNguoT04S5CNT+o8E2+M0HoW4TCU7Azgeu+owhINjzbY9gG4J2ZVQsBT8iirHOw8KJqFKCp0J7hd7TnzdYJwTr7qbYWyHapmnHg9nvRylhFK/IoNi7vn2pJPLy1z84srg=="
def name_from_bytes(b):
    return b.split(b'\x00')[0].decode('cp932')
def xor_bytes(sequence1,sequence2):
    result = bytearray([0]*len(sequence1))
    bytesfunc.xor(sequence1,sequence2,result)
    return result
def fill_bytes(b):
    return b + bytes([0x80]*(0x102-len(b)))
def unpack(filename,dir,umode, key=base64.b64decode(ContentKey)):
    with open(filename,'rb') as f:
        data = f.read()
        count = xor(struct.unpack("H" , data[:2])[0], 0x8080)
        print('total {0} files!'.format(count))
        name_length = 0x100
        for i in range(count):
            name_offset = 2
            if i:
                name_offset =  2 + ((name_length + 10) * i)
            name = xor_bytes(data[name_offset:name_offset+name_length], 0x80)
            print('found {0} '.format(name_from_bytes(name)))
            if umode:
                info_offset = (name_length + 4) + (i * (name_length + 10))
                info = xor_bytes(data[info_offset:info_offset+8], 0x80)
                size = struct.unpack("I" , info[:4])[0]
                offset = struct.unpack("I" , info[-4:])[0]
                encrypted = min(size, len(key))
                header = xor_bytes(data[offset:offset+encrypted], key[:encrypted])
                if dir == 'default':
                    output_dir = os.path.abspath('unpacked')
                else:
                    output_dir = os.path.abspath(dir)
                if not os.path.exists(output_dir):
                    os.mkdir(output_dir)
                with open(os.path.join(output_dir,name_from_bytes(name)),'wb') as entry:
                    entry_data = header
                    if size > len(key):
                        entry_data += data[offset+encrypted:offset+size]
                    entry.write(entry_data)
        if umode:
            print("unpack done!")
def pack(dir, filename, key=base64.b64decode(ContentKey)):
    curr_dir = os.path.abspath(dir)
    if filename == 'default':
        filename = curr_dir.split(os.sep)[-1] + '.dat'
    print(curr_dir)
    files = [os.path.join(curr_dir, f) for f in os.listdir(curr_dir) if os.path.isfile(os.path.join(curr_dir, f))]
    print('{0} files will be packed!'.format(len(files)))
    with open(filename,'ab') as f:
        count = xor_bytes(struct.pack("H" , len(files)), struct.pack("H", 0x8080))
        f.write(count)
        data = bytes()
        curr_offset = 2 + (0x10A * len(files))
        for i in range(len(files)):
            entry_name = xor_bytes(bytes(files[i].split(os.sep)[-1], 'cp932'), 0x80)
            f.write(fill_bytes(entry_name))
            entry_size = os.path.getsize(files[i])
            f.write(xor_bytes(struct.pack("I" , entry_size), 0x80))
            entry_offset = struct.pack("I" , curr_offset)
            curr_offset += entry_size
            f.write(xor_bytes(entry_offset, 0x80))
            encrypted = min(entry_size, len(key))
            with open(files[i],'rb') as entry:
                file_data = entry.read()
                header = xor_bytes(file_data[:encrypted], key[:encrypted])
                entry_data = header
                if entry_size > len(key):
                    entry_data += file_data[encrypted:]
                data +=entry_data
        f.write(data)
    print("packing done!")
@click.command()
@click.option('--unpack', '-u' , 'UMODE', help="for unpack mode. default is view mode", is_flag=False, flag_value="click")
@click.option('--pack', '-p' , 'PMODE', help="for pack mode", is_flag=False, flag_value="click")
@click.option('--file', '-f' , 'FILE', default="default", help="file path to unpack/pack")
@click.option('--directory', '-d' , 'DIR', default="default", help="directory path to unpack/pack", required=False)
def main(FILE, DIR, UMODE, PMODE):
    if (FILE == DIR == 'default') or (DIR == 'default' and PMODE):
        print("missing parameter!")
        return None
    if not PMODE:    
        unpack(FILE, DIR, UMODE)
    else:
        pack(DIR,FILE)
    
if __name__ == '__main__':
    main()

