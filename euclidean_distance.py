#
# *************************************************************
#
# $Source: $
# $Revision: $                                                                 
# $State: $                                                                     
# $Date: $                                                      
# $Author: $  
#
# $Log: $
#
#
# *************************************************************
import sys
from math import sqrt




def euclidean_distance(p, p2): return sqrt(sum(map(lambda x,x2: (x-x2)**2, p, p2)))


points=[tuple(map(float,l.split(','))) for l in sys.stdin.xreadlines()]
n=0
for p1 in points:
    n+=1
    for p2 in points[n:]:
        print euclidean_distance(p1,p2)

