graph-stl
=========

With the 3D graph maker you can enter any function (z in terms of x and y) and it will output a 3-D printable *.stl file. 


Enter your function, domain, range, and decide if you want Autoscale or not.  When you click the Start button it will ask you where you want to save the file and what you want to call it.  Once the program is finished it will put the .stl file where you told it to.  You can then open the 3D printable graph with the OpenStl program (which I did not create, but is free from the internet) to verify that it worked, then go print it!

Enjoy,

Jim Town

Autoscale will make the whole print fit inside of a 10cm envelope (or in math terms a 10cm cube).  Without Autoscale, you will have regulate your own heights (z) to fit your 3D printer, but the base (x and y) will still be less than or equal to 10cm.  

Dependencies:
- numpy
- Image
- tkinter
- math
- sys
- itertools
