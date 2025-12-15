import sys
from new_reader import reader


def iterboxes(r):
    """
    iterboxes iterate boxes,
    r is an open file handle.
    """
    while r:
        idx = r.tell()
        eight_bites = r.read(8)
        if not eight_bites:
            sys.exit()
        header =BoxHeader(idx,eight_bites)
        print(f'\nHeader {vars(header)}')
        if header.name in boxes:
            box = boxes[header.name](header)
        else:
            box =Box(header)
        box.decode(r)


def b2i(bites):
    """
    b2i big endian bytes to int
    """
    total=0
    for bite in bites: total = total<<8|bite
    return total
    # return sum([ (b << (idx<<3)) for idx, b in enumerate(reversed(bites))])

class BoxHeader:
     def __init__(self,idx,bites):
        self.idx = idx
        self.bites = bites
        self.size = b2i(bites[:4])
        self.name = bites[4:]


class Box:
    def __init__(self,header):
        self.idx= header.idx
        self.size = header.size
        self.name = header.name
        self.payload_size= header.size - 8
        self.pay = None
        print(f"{self.name} size: {self.size}  @{self.idx}")

    def decode(self,r):
        self.pay = r.read(self.payload_size)
        nopay=self.__dict__
        nopay.pop('pay')
        print(nopay)

        
class Ftyp(Box):
    def __init__(self,header):
        super().__init__(header)
        self.major_brand = None
        self.minor_version = None
        self.compatible_brands=[]

    def decode(self,r):
        self.pay = r.read(self.payload_size)
        pay = self.pay
        self.major_brand = pay[:4]
        self.minor_version = b2i(pay[4:8])
        pay = pay[8:]
        self.compatible_brands=[pay[i:i+4] for i in range(0,len(pay),4)]
        print(self.__dict__)


class Moov(Box):
    def __init__(self,header):
        super().__init__(header)    

    def decode(self,r):
        psize = self.payload_size
        while psize > 7:
            iterboxes(r)
 
            
class Mdat(Box):
    def __init__(self,header):
        super().__init__(header)
        self.data=None

    def decode(self,r):
        self.data = r.read(self.payload_size)


class Mvhd(Box):
    def __init__(self,header):
        super().__init__(header)
        self.version=0
        self.creation_time=None
        self.modification_time=None
        self.timescale=None
        self.duration=None
        self.rate = None
        self.volume= None
        self.next_track_id=None

    def decode(self,r):
        idx = r.tell()
        self.version=b2i(r.read(4))
        if self.version == 0:
            self.creation_time = b2i(r.read(4))
            self.modification_time = b2i(r.read(4))
            self.timescale = b2i(r.read(4))
            self.duration = b2i(r.read(4))
        else:
            self.creation_time = b2i(r.read(8))
            self.modification_time = b2i(r.read(8))
            self.timescale = b2i(r.read(4))
            self.duration = b2i(r.read(8))            
        self.rate =  b2i(r.read(2))
        r.read(1)
        self.volume =  b2i(r.read(2))
        reserved = b2i(r.read(1))
        r.seek(idx+self.size-12)
        self.next_track_id=b2i(r.read(4))
        r.seek(idx+self.size)
        print(self.__dict__)
               
"""const unsigned int(32)[2] reserved = 0;
template int(32)[9] matrix =
{ 0x00010000,0,0,0,0x00010000,0,0,0,0x40000000 };
// Unity matrix
bit(32)[6] pre_defined = 0;
unsigned int(32) next_track_ID;
"""

class Mdia(Box):
    
    def decode(self,r):
        self.pay = r.read(self.payload_size)


class Tkhd(Box):
    def __init__(self,header):
        super().__init__(header)
        self.version=0
        self.creation_time=None
        self.modification_time=None
        self.track_id=None
        self.duration=None
        self.rate = None
        self.volume= None
        self.layer = None
        self.alternate_group= None
        self.matrix = None
        self.width = None
        self.height= None

    def decode(self,r):
        idx = r.tell()
        self.flags=b2i(r.read(4))
        #self.version=b2i(r.read(4))
        if self.version == 0:
            self.creation_time = b2i(r.read(4))
            self.modification_time = b2i(r.read(4))
            self.track_id = b2i(r.read(4))
            reserved = b2i(r.read(4)) 
            self.duration = b2i(r.read(4))
        else:
            self.creation_time = b2i(r.read(8))
            self.modification_time = b2i(r.read(8))
            self.track_id = b2i(r.read(4))
            reserved = b2i(r.read(4))
            self.duration = b2i(r.read(8))            
        self.rate =  b2i(r.read(4))
        self.volume =  b2i(r.read(2))
        reserved = b2i(r.read(2))
        self.layer = b2i(r.read(2))
        self.alternate_group=b2i(r.read(2))
        self.volume = b2i(r.read(2))
        reserved = b2i(r.read(2))
        self.matrix  = b2i(r.read(4))
        self.width = b2i(r.read(4))
        self.height= b2i(r.read(4))
        r.seek(idx+self.payload_size)
        print(self.__dict__)


        
boxes = {
    b"ftyp": Ftyp,
    b"moov":Moov,
    b"mdat":Mdat,
    b'mvhd':Mvhd,
    b'mdia':Mdia,
    b'tkhd':Tkhd,
    }


if __name__ == '__main__':
    with  reader(sys.argv[1]) as r:
        iterboxes(r)
