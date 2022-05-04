# By: Jim Town
# james.ross.town@gmail.com
#

from PIL import Image

from numpy import zeros,array
import numpy as np
import sys
import math
from stl import mesh
from itertools import product

#triangle points must be in counter clockwise order
verbose=False


def isIn(heights,pt):
    i,j=pt
    return i>=0 and j>=0 and i<heights.shape[0] and j<heights.shape[1]

def getStartingPoint(heights,minVal):
    for i in range(heights.shape[0]):
        for j in range(heights.shape[1]):
            #print(heights[i,j])
            if heights[i,j]>minVal:
                #print(i,j)
                return (i,j)
    print("no starting point?")
    return None

def isNeighbor(heights,pt1,pt2):
    i,j=pt1
    otherPts=[(i-1,j),(i,j+1),(i+1,j),(i,j-1),(i-1,j+1),(i+1,j+1),(i+1,j-1),(i-1,j-1)]
    for pt in otherPts:
        if pt==pt2:
            return True
    return False

def hasAzero(heights,pt,minVal):
    i,j=pt
    otherPts=[(i-1,j),(i,j+1),(i+1,j),(i,j-1)]
    for pt in otherPts:
        pi,pj=pt
        if ((isIn(heights,pt) and heights[pi,pj]<=minVal) or
            not isIn(heights,pt)):
            return True
    return False

def getNextPt(heights,pt,oldPoints,minVal,clockwise=True):
    #print(pt,lastPt)
    i,j=pt
    otherPts=[(i-1,j),(i,j+1),(i+1,j),(i,j-1)]
    for newPt in otherPts:
        ni,nj=newPt
        if newPt in oldPoints or not isIn(heights,newPt) or heights[ni,nj]<=minVal:
            continue
        if hasAzero(heights,newPt,minVal):
            return newPt
                #NE       #SE       #SW       #NW
    otherPts=[(i-1,j+1),(i+1,j+1),(i+1,j-1),(i-1,j-1)]
    for newPt in otherPts:
        ni,nj=newPt
        if newPt in oldPoints or not isIn(heights,newPt) or heights[ni,nj]<=minVal:
            continue
        if hasAzero(heights,newPt,minVal):
            return newPt
    #debugging
    #otherPts=[(i-1,j),(i,j+1),(i+1,j),(i,j-1),(i-1,j+1),(i+1,j+1),(i+1,j-1),(i-1,j-1)]
    #print("no next point at:",pt,heights[pt])
    #print("other points: ")
    #for newPt in otherPts:
    #    if isIn(heights,newPt):
    #        print(newPt,heights[newPt],hasAzero(heights,newPt,minVal),newPt in oldPoints)
    #    else:
    #        print(newPt,"not in")
    #print("")
    #end debugging
    return None
    
def getSides(heights,goodPts,minVal):
    startPt=getStartingPoint(heights,minVal)
    nextPt=getNextPt(heights,startPt,[],minVal)
    sides=[startPt,nextPt]
    backInTime=1
    while True:#nextPt is not None: #nextPt!=startPt:#nextPt is not None:#not nextPt==startPt:
        #print(nextPt)
        nextPt=getNextPt(heights,nextPt,sides,minVal)
        if nextPt is None:
            backInTime+=1
            nextPt=sides[-backInTime]
            backInTime+=1
            print(backInTime,nextPt)
        else:
            backInTime=1
        sides.append(nextPt)
        if isNeighbor(heights,startPt,nextPt):
            break
        
    #if isNeighbor(heights,nextPt,startPt):
    #    print("good")
    #else:
    #    print("bad",sides[-2],startPt)
    return sides[:-1]#get rid of None at the end
        
                
def getTriangles(heights,i,j,minVal,minThickness,verbose=False):
    #0 = left triangle only
    #1 = upper right #upper half of regular
    #2 = opposite right only
    #3 = lower right #lower half of regular

    triangles=[]
    otherPts={'N':(i-1,j),
                 'S':(i+1,j),
                 'E':(i,j+1),
                 'W':(i,j-1),
                 'NE':(i-1,j+1),
                 'NW':(i-1,j-1),
                 'SE':(i+1,j+1),
                 'SW':(i+1,j-1)}
    #check 0 left triangle
    if (isIn(heights,otherPts['W'])  and heights[otherPts['W']]<=minVal and
        isIn(heights,otherPts['SW']) and heights[otherPts['SW']]>minVal and
        isIn(heights,otherPts['S'])  and heights[otherPts['S']]>minVal):
        triTop=[[i,j,heights[i,j]],[i+1,j-1,heights[i+1,j-1]],[i+1,j,heights[i+1,j]]]
        triBot=[[i,j,-minThickness],[i+1,j-1,-minThickness],[i+1,j,-minThickness]]
        triangles.append(triTop)
        triangles.append(triBot)
        if verbose:
            print(",,,,,0")
            print(triTop)
            #print(triBot)
            print(",,,,,0")
            
        
    #check 1 upper right 
    if (isIn(heights,otherPts['E'])  and heights[otherPts['E']]>minVal and
        isIn(heights,otherPts['SE']) and heights[otherPts['SE']]>minVal):
        triTop=[[i,j,heights[i,j]],[i+1,j+1,heights[i+1,j+1]],[i,j+1,heights[i,j+1]]]
        triBot=[[i,j,-minThickness],[i+1,j+1,-minThickness],[i,j+1,-minThickness]]
        triangles.append(triTop)
        triangles.append(triBot)
        if verbose:
            print("_____1")
            print(triTop)
            #print(triBot)
            print("_____1")
             
    #check 2 opposite right
    if (isIn(heights,otherPts['SE'])  and heights[otherPts['SE']]<=minVal and
        isIn(heights,otherPts['S']) and heights[otherPts['S']]>minVal and
        isIn(heights,otherPts['E'])  and heights[otherPts['E']]>minVal):
        triTop=[[i,j,heights[i,j]],[i+1,j,heights[i+1,j]],[i,j+1,heights[i,j+1]]]
        triBot=[[i,j,-minThickness],[i+1,j,-minThickness],[i,j+1,-minThickness]]
        triangles.append(triTop)
        triangles.append(triBot)
        if verbose:
            print(".....2")
            print(triTop)
            #print(triBot)
            print(".....2")

    #check 3 lower right 
    if (isIn(heights,otherPts['S'])  and heights[otherPts['S']]>minVal and
        isIn(heights,otherPts['SE']) and heights[otherPts['SE']]>minVal):
        triTop=[[i,j,heights[i,j]],[i+1,j,heights[i+1,j]],[i+1,j+1,heights[i+1,j+1]]]
        triBot=[[i,j,-minThickness],[i+1,j,-minThickness],[i+1,j+1,-minThickness]]
        triangles.append(triTop)
        triangles.append(triBot)
        if verbose:
            print("-----3")
            print(triTop)
            #print(triBot)
            print("-----3")
    if verbose: print(" ")
    return triangles

def numpy2stlIslands(heights,fileName="test.stl",minVal=0,minThickness=1):#trying to make islands
    #print(len(np.where(heights>0)[0]))
    #print(len(np.where(heights>0)[1]))
    #print(heights.max())
    goodPts=np.where(heights>minVal)
    #print(minVal)
    sidePts=getSides(heights,goodPts,minVal)
    topTris=2*len(goodPts[0])
    botTris=2*len(goodPts[0])
    sideTris=2*len(sidePts)
    shape=mesh.Mesh(np.zeros(topTris+sideTris+botTris, dtype=mesh.Mesh.dtype))
    #print(len(goodPts[0]),len(sidePts))
    #find an edge point
    triCnt=0
    for i in range(heights.shape[0]):
        for j in range(heights.shape[1]):
            if heights[i,j]>minVal:
                triangles=getTriangles(heights,i,j,minVal,minThickness,verbose)
                for triangle in triangles:
                    #print(triangle,triCnt)
                    shape.vectors[triCnt]=triangle
                    triCnt+=1
    for s,side in enumerate(sidePts):
        if s==len(sidePts)-1:
            nextS=sidePts[0]
        else:
            nextS=sidePts[s+1]
        i,j=side
        nextI,nextJ=nextS
        tri1=[[i,j,-minThickness],[nextI,nextJ,heights[nextI,nextJ]],[i,j,heights[i,j]]]
        tri2=[[i,j,-minThickness],[nextI,nextJ,-minThickness],[nextI,nextJ,heights[nextI,nextJ]]]
        shape.vectors[triCnt]=tri1
        shape.vectors[triCnt+1]=tri2
        triCnt+=2
    #print(triCnt)
    shape.save(fileName)
    

def numpy2stlRectangles(heights,fileName="test.stl",minThickness=1):#rectangular (for now...)
    topTris=2*heights.shape[0]*heights.shape[1]
    lSideTris=2*heights.shape[0]
    rSideTris=2*heights.shape[1]
    bottomTris=2
    shape = mesh.Mesh(np.zeros(topTris+lSideTris+rSideTris+bottomTris, dtype=mesh.Mesh.dtype))
    triCnt=0
    #top
    for i in range(heights.shape[0]-1):
        for j in range(heights.shape[1]-1):
            tri1=[[i,j,heights[i,j]],[i+1,j,heights[i+1,j]],[i+1,j+1,heights[i+1,j+1]]]
            tri2=[[i,j,heights[i,j]],[i+1,j+1,heights[i+1,j+1]],[i,j+1,heights[i,j+1]]]
            shape.vectors[triCnt] = tri1
            shape.vectors[triCnt+1] = tri2
            triCnt+=2
                          
    #side1 j=0 and side3 j=shape[1]-1
    for i in range(heights.shape[0]-1):
        for j in [0,heights.shape[1]-1]:
            tri1=[[i,j,-minThickness],[i,j,heights[i,j]],[i+1,j,heights[i+1,j]]]
            tri2=[[i,j,-minThickness],[i+1,j,heights[i+1,j]],[i+1,j,-minThickness]]
            shape.vectors[triCnt]=tri1
            shape.vectors[triCnt+1]=tri2
            triCnt+=2
    #side2 i=0 and side4 i=shape[0]-1
    for j in range(heights.shape[1]-1):
        for i in [0,heights.shape[0]-1]:
            tri1=[[i,j,-minThickness],[i,j,heights[i,j]],[i,j+1,heights[i,j+1]]]
            tri2=[[i,j,-minThickness],[i,j+1,heights[i,j+1]],[i,j+1,-minThickness]]
            shape.vectors[triCnt]=tri1
            shape.vectors[triCnt+1]=tri2
            triCnt+=2
    #bottom
    tri1=[[0,0,-minThickness],
          [0,heights.shape[1]-1,-minThickness],
          [heights.shape[0]-1,heights.shape[1]-1,-minThickness]]
    tri2=[[0,0,-minThickness],
          [heights.shape[0]-1,0,-minThickness],
          [heights.shape[0]-1,heights.shape[1]-1,-minThickness]]
    shape.vectors[triCnt]=tri1
    shape.vectors[triCnt+1]=tri2
    
    shape.save(fileName)

def numpy2stl(heights,
              fileName="test.stl",
              mask_val=0,
              min_thickness=1,
              isIsland=True, #cuts off bottom to make islands
              ):
    #heights*=scale
    if isIsland:
        numpy2stlIslands(heights,fileName,mask_val,min_thickness)
    else:
        numpy2stlRectangles(heights,fileName,min_thickness)

if __name__=="__main__":
    imageArr=np.load("test.npy")
    numpy2stl(imageArr,mask_val=-.1,min_thickness=5)
        
