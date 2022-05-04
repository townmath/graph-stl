# By: Jim Town
# james.ross.town@gmail.com
#

from numpy2stl import numpy2stl
from PIL import Image
import tkinter as Tkinter #for compatibility
from numpy import zeros,array
from tkinter.filedialog import asksaveasfilename
import sys
import math

BGCOLOR='#C0D9AF' #light green 
FGCOLOR='#E0EEE0' #slightly lighter green
minScale=1  #if z values are a lot larger than x and y values, scale it
maxDimension=100.0 #makes max dimension 100 = 10cm
maxWidth=10000#140 #10000, #afinia website says it can print a 5.5" cube 140mm
maxDepth=10000#140 #10000, #10000mm=10m user can shrink it with their printer software
maxHeight=10000#140 #10000, #

class Application(Tkinter.Frame):

    class IORedirector(object):
        #A general class for redirecting I/O to this text widget.
        def __init__(self,outputBox):
            self.outputBox = outputBox

    class StdoutRedirector(IORedirector):
        #A class for redirecting stdout to this text widget.
        def write(self,str):
            if not str.isspace():
                self.outputBox.insert(Tkinter.END,str+' ')#,False)
                root.update()
    def checkFunction(self):
        x=float(self.xmax.get()+self.xmin.get())/float(2)
        y=float(self.ymax.get()+self.ymin.get())/float(2)
        try:
            testing=eval(self.function.get())
        except ZeroDivisionError:
            self.output=self.function.get()+' is not defined at ('+str(x)+','+str(y)+'), try a different domain.'
            return False
        except:
            self.output=self.function.get()+' is not a valid function, try again (see examples below).'
            return False
        else:
            return True

    def saveFileLocation(self):
        self.fileLocation=asksaveasfilename(filetypes=[("STL","*.stl")])
        if self.fileLocation:
            STLlist=['.STL','.stl']
            if self.fileLocation[-4:] not in STLlist:
                self.fileLocation+='.stl'
            return True
        else:
            self.output='Please enter a filename when prompted.'
            return False
        
    def makeHeights (self):
        xmin=self.xmin.get()
        xmax=self.xmax.get()
        ymin=self.ymin.get()
        ymax=self.ymax.get()
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
                    heightArray[i][j]=eval(self.function.get())
                except:
                    self.outputBox.delete(1.0,Tkinter.END)
                    self.output=self.function.get()+' is not defined at ('+str(x)+','+str(y)+'), try a different domain.'
                    self.outputBox.insert(Tkinter.END,self.output)
                    return array([])
        if self.autoScale.get():
            self.scaleFactor=maxDimension/(heightArray.max()-heightArray.min())#max(graphWidth,graphHeight)/heightArray.max()
        else:
            self.scaleFactor=minScale
        heightArray*=self.scaleFactor
        return heightArray

    def main(self):
        self.outputBox.delete(1.0,Tkinter.END)
        while self.xmax.get()<=self.xmin.get() or self.ymax.get()<=self.ymin.get() or not self.checkFunction() or not self.saveFileLocation():
            if self.xmax.get()<=self.xmin.get() or self.ymax.get()<=self.ymin.get():
                output='Max must be greater than Min.'
            else:
                output=self.output
            self.outputBox.insert(Tkinter.END,output)
            return
        self.outputBox.insert(Tkinter.END,'Working... ')#This may take a while.')
        root.update()
        #start redirecting stdout:
        sys.stdout = self.StdoutRedirector(self.outputBox)
        heightArray=self.makeHeights()
        # make stl file
        if not heightArray.size:
            return
        else:
            numpy2stl (heightArray, self.fileLocation) 
        self.outputBox.delete(1.0,Tkinter.END)
        self.outputBox.insert(Tkinter.END,'Program is finished.')
        #stop redirecting stdout:
        sys.stdout = sys.__stdout__
        

    def functionInput(self, caption, width=None, **options):
        Tkinter.Label(self.frame, text=caption, bg=BGCOLOR).grid(row=self.row, column=self.column, sticky='es')#, columnspan=1)
        entry = Tkinter.Entry(self.frame, **options)
        self.column+=1
        entry.grid(row=self.row, column=self.column, sticky='wes', columnspan=4)
        entry.insert(Tkinter.END,'x**2+y**2')
        return entry

    def makeSlider(self, caption, default, width=None, **options):
        Tkinter.Label(self.frame, text=caption, bg=BGCOLOR).grid(row=self.row, column=self.column, sticky='w', columnspan=2)
        slider = Tkinter.Scale(self.frame, **options)
        slider.grid(row=self.row+1, column=self.column, sticky='we', columnspan=2)
        self.column+=2
        slider.set(default)
        return slider

    def makeButton(self, **options):
        button = Tkinter.Button(self.frame, **options)
        button.grid(row=4, column=self.column, rowspan=3, padx=23, sticky='w')
        return button

    def makeCheckBox(self):
        self.autoScale = Tkinter.BooleanVar()
        checkBox = Tkinter.Checkbutton(self.frame, text="AutoScale", variable=self.autoScale, 
                                       bg=BGCOLOR, onvalue=True, offvalue=False)
        checkBox.select()
        checkBox.grid(row=6, column=self.column, rowspan=2, padx=20, sticky='w')
    
    def makeScrollBar(self):
        winHeight=min(1060,root.winfo_screenheight()-500)
        scrollbar = Tkinter.Scrollbar(self, orient="vertical")
        scrollbar.pack(side='right',fill='y', expand=False)
        self.canvas= Tkinter.Canvas(self,bd=0, #width=935, height=winHeight,
                               borderwidth=0, background=BGCOLOR,
                               highlightthickness=0,
                               yscrollcommand=scrollbar.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.canvas.yview)

        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        self.frame = Tkinter.Frame(self.canvas, background=BGCOLOR)
        newWindow = self.canvas.create_window(0,0,window=self.frame,anchor='nw')

        def configureFrame(event):
            size=(self.frame.winfo_reqwidth(), self.frame.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)
            if self.frame.winfo_reqwidth() != self.canvas.winfo_width():
                self.canvas.config(width=self.frame.winfo_reqwidth())
        self.frame.bind('<Configure>', configureFrame)
        
        def configureCanvas(event):
            if self.frame.winfo_reqwidth() != self.canvas.winfo_width():
                self.canvas.config(width=self.frame.winfo_width())
        self.canvas.bind('<Configure>', configureCanvas)
        self.pack()

    def shrinkWindow(self, event): #when the window shrinks the scrollbar/canvas shrinks with it
        if root.winfo_height()!=self.canvas.winfo_height():
            self.canvas.config(height=root.winfo_height())        
    
    def insertImage(self,filename,**options):
        theImage=Tkinter.PhotoImage(file="images/"+filename+".gif")
        instructionLabel = Tkinter.Label(self.frame, image=theImage, bg=BGCOLOR, relief=Tkinter.FLAT)
        instructionLabel.photo=theImage
        instructionLabel.grid(**options)

    def __init__(self, master=None):
        frame=Tkinter.Frame.__init__(self, master)
        root.bind('<Configure>', self.shrinkWindow)
        self.makeScrollBar()
        self.width=0
        self.height=0
        self.grid()
        self.scaleFactor=minScale #image size divided by (ie 2 means half): default is 1
        self.column=1
        self.row=3
        #self.insertImage('logo',row=0,column=0,rowspan=10)
        self.xmax=self.makeSlider("x max", 10, from_=-1000, to=1000, length=225, bg=BGCOLOR, resolution=1, orient=Tkinter.HORIZONTAL)
        self.ymax =self.makeSlider("y max", 10, from_=-1000, to=1000, length=225, bg=BGCOLOR, resolution=1, orient=Tkinter.HORIZONTAL)
        self.startButton=self.makeButton(text="Start", width=10,command=self.main)
        self.makeCheckBox()
        self.column=1
        self.row+=2
        self.xmin=self.makeSlider("x min", -10, from_=-1000, to=1000, length=225, bg=BGCOLOR, resolution=1, orient=Tkinter.HORIZONTAL)
        self.ymin =self.makeSlider("y min", -10, from_=-1000, to=1000, length=225, bg=BGCOLOR, resolution=1, orient=Tkinter.HORIZONTAL)
        self.row+=2
        self.column=0
        self.function = self.functionInput("z=",bg=FGCOLOR,width=300)
        self.row+=1
#        self.area = self.areaSlider("Area (sq km)",50,from_=1, to=100000, length=600, bg=BGCOLOR, resolution=1, orient=Tkinter.HORIZONTAL) 
        #self.vertExag=self.makeSlider("Vertical Exaggeration", 1, from_=.1, to=10, length=150, bg=BGCOLOR, resolution=.1, orient=Tkinter.HORIZONTAL)
        self.outputBox = Tkinter.Text(self.frame, bg=BGCOLOR, height= 1, fg='black', font=("Helvetica", 10), relief=Tkinter.FLAT, yscrollcommand='TRUE')#fg='black', relief=Tkinter.SUNKEN, 
        self.outputBox.grid(row=self.row, column=1, columnspan=5, sticky='ew')
        self.row+=1
        self.insertImage('examples',row=self.row,column=0,rowspan=5,columnspan=5, sticky='w', padx=10)
        self.row+=4
        self.httpBox = Tkinter.Text(self.frame, bg=BGCOLOR, height= 1, fg='black', font=("Helvetica", 14), relief=Tkinter.FLAT, yscrollcommand='TRUE')#fg='black', relief=Tkinter.SUNKEN, 
        self.httpBox.grid(row=self.row, column=4, columnspan=4, rowspan=1, sticky='s', pady=6, padx=8)
        self.httpBox.insert(Tkinter.END,'http://docs.python.org/2/library/math.html')

root = Tkinter.Tk()
root.title("3-D graph to *.stl by Jim Town")
root.configure(background=BGCOLOR)
winHeight=min(420,root.winfo_screenheight()-100)
root.geometry('605x'+str(winHeight)+'+10+10')
app = Application(master=root)
app.mainloop()

