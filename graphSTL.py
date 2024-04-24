import numpy2stl as numpy2stl
from PIL import Image
from numpy import zeros,array
import sys
import math

BGCOLOR='#C0D9AF' #light green
FGCOLOR='#E0EEE0' #slightly lighter green
minScale=1  #if z values are a lot larger than x and y values, scale it
maxDimension=200.0 #makes max dimension 100 = 10cm
bottom=True #true prints a bottom
minThickPct=.03 #percent of total height to put at bottom
maxWidth=100#140 #10000, #afinia website says it can print a 5.5" cube 140mm
maxDepth=100#140 #10000, #10000mm=10m user can shrink it with their printer software
maxHeight=100#140 #10000, #
#export DISPLAY=:0.0

def makeHeights(xmin,xmax,ymin,ymax,function,autoScale,maxDimension):
    graphWidth=xmax-xmin
    graphHeight=ymax-ymin
    countBy=float(max(graphWidth,graphHeight))/maxDimension
    arrayWidth=int(graphWidth/countBy)+1
    arrayHeight=int(graphHeight/countBy)+1
    heightArray=zeros((arrayWidth,arrayHeight))
    for i in range(arrayWidth):
        for j in range(arrayHeight):
            x=i*countBy+xmin
            y=-j*countBy+ymax
            try:
                val=eval(function)
                if isinstance(val,complex):
                    heightArray[i][j]=0
                else:
                    heightArray[i][j]=val/countBy
            except:
                self.output+=self.function+' is not defined at ('+str(x)+','+str(y)+'), try a different domain.'
                return array([]),1
    if autoScale:
        scaleFactor=maxDimension/(heightArray.max()-heightArray.min())#max(graphWidth,graphHeight)/heightArray.max()
    else:
        scaleFactor=minScale
    return heightArray,scaleFactor

def checkFunction(xmax,xmin,ymax,ymin,function):
    x=float(xmax+xmin)/float(2)
    y=float(ymax+ymin)/float(2)
    try:
        testing=eval(function)
    except ZeroDivisionError:
        output=function+' is not defined at ('+str(x)+','+str(y)+'), try a different domain.'
        return False,output
    except:
        output=function+' is not a valid function, try again (see examples below).'
        return False,output
    else:
        return True,""
    
#for testing or non gui use       
class threeDgraph ():

    def checkFunction(self):
        isGood,self.output=checkFunction(self.xmax,self.xmin,
                                         self.ymax,self.ymin,
                                         self.function)
        return isGood

    def saveFileLocation(self):
        self.fileLocation=asksaveasfilename(filetypes=[("STL","*.stl")])
        if self.fileLocation:
            STLlist=['.STL','.stl']
            if self.fileLocation[-4:] not in STLlist:
                self.fileLocation+='.stl'
            return True
        else:
            self.output+='Please enter a filename when prompted.'
            return False

    def makeHeights (self):
        print("Calculating z values...")
        return makeHeights(self.xmin,self.xmax,self.ymin,self.ymax,self.function,
                           self.autoScale,maxDimension)

    def createSTL(self):
        self.checkFunction()
        print (self.output)
        heightArray,self.scaleFactor=self.makeHeights()
        # make stl file
        if not heightArray.size:
            return
        else:
            #self.output+=' 123 '
            self.f=numpy2stl.numpy2stl (heightArray, self.fileLocation,
                       scale=self.scaleFactor,
                       mask_val=1,#0,#1,
                       #max_width=maxWidth,
                       #max_depth=maxDepth,
                       #max_height=maxHeight,
                       #min_thickness_percent=minThickPct, #helps reduce waste at bottom
                       #solid=bottom #True means it will make a bottom
                                        )
            #self.output+=' 456 '



    def __init__(self, expression, xmin=-10,xmax=10,ymin=-10,ymax=10):
        self.width=0
        self.height=0
        self.autoScale=False#
        self.scaleFactor=minScale #image size divided by (ie 2 means half): default is 1
        self.xmin=xmin
        self.xmax=xmax
        self.ymin=ymin
        self.ymax=ymax
        self.function=expression
        self.output='  '
        self.fileLocation='3dgraph.stl'
        self.createSTL()
        print (self.output)



if __name__=="__main__":
    #graph=threeDgraph('x**2+y**2')
    #torus (donut) test (top half)
    #R=5 #outer R
    #r=3 #inner R
    #graph=threeDgraph("(3**2-((x**2+y**2)**.5-5)**2)**.5")#=z
    #testing hemisphere
    threeDgraph("(5**2-(x**2+y**2))**.5")



#numpy2stl(heightArray, "filename.stl",
#          scale=0.05, maximum height
#          mask_val=5., not quite sure, seems to add holes
#          max_width=235., #width of your 3-D printer surface in mm
#          max_depth=140., #depth of your 3-D printer surface in mm
#          max_height=150.,#height of your 3-D printer surface in mm
#          min_thickness_percent = .005, helps reduce waste at bottom
#          solid=True) True means it will make a bottom
