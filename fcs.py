from mmap import mmap


def readFCS(filename='ptpn22_fifth_pair_I018048R_INTR.fcs'):
	f=open(filename, 'r+b')
	m=mmap(f.fileno(), 0)
	return m


def find(m, text):
	m.seek(0)
	m.seek(m.find(text))
	return m.read(100)
	
#3.0 00 - 05
#m.seek(0)
#print m.read(6)

#ASCII(32) - space characters 06 - 09
#m.seek(6)
#print m.read(4)

#ASCII-encoded offset to first byte of TEXT segment 10 - 17
#m.seek(10)
#print m.read(8)

#ASCII-encoded offset to last byte of TEXT segment 18 - 25

#ASCII-encoded offset to first byte of DATA segment 26 - 33

#ASCII-encoded offset to last byte of DATA segment 34 - 41

#ASCII-encoded offset to first byte of ANALYSIS segment 42 - 49

#ASCII-encoded offset to last byte of ANALYSIS segment 50 - 57

#ASCII-encoded offset to user defined OTHER segments 58 - beginning of next segment

#One example HEADER segment is as follows:

#FCS3.0*********256****1545****1792**202456*******0*******0 


