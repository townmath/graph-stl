
import struct, Image, numpy, sys, math
#import matplotlib.pyplot as plt

#'>I'=big endian non-neg int 4 bytes
#'>i'=big endian signed int 4 bytes
#'>d'=big endian double precision float 8 bytes 
#'>f'=big endian single precision float 4 bytes 
#'B'=unsigned char 1 byte (can be formated to hex, chr, etc)

def getWord (index, fileStr):
    x=index
    lenWord=struct.unpack('>I', fileStr[x:x+4])[0] #>I=big endian non-neg int
    #print lenWord
    x+=4
    word=''
    for char in range(lenWord):
        word+=chr(struct.unpack('B', fileStr[x])[0])
        x+=1
    if x%4!=0:
        x+=4-x%4 #new things always start on %4
    return x,word

def getDouble (index, fileStr):
    x=index
    nelems=struct.unpack('>I', fileStr[x:x+4])[0] #>I=big endian non-neg int
    x+=4
    doubleList=[]
    for elem in range(nelems):
        doubleList.append(struct.unpack('>d', fileStr[x:x+8])[0])
        x+=8
    return x, doubleList

def getIntOrFloat (index, fileStr,numType):
    x=index
    nelems=struct.unpack('>I', fileStr[x:x+4])[0] #>I=big endian non-neg int
    x+=4
    numList=[]
    for elem in range(nelems):
        numList.append(struct.unpack(numType, fileStr[x:x+4])[0])
        x+=4
    return x, numList

def getDimList (numberOfDims,fileStr,index):
    x=index #dim list starts after 15
    dimDict={}
    for dim in range (numberOfDims):
        x,word=getWord(x, fileStr)
        #print hex(struct.unpack('B', fileStr[x])[0])
        wordValue=struct.unpack('>I', fileStr[x:x+4])[0]
        dimDict[word]=wordValue
        #print word, '=', wordValue
        x+=4
    return x, dimDict

def getAttList (numberOfAttr,fileStr,index):
    x=index
    allAttDict={}
    for attr in range(numberOfAttr):
        x,word=getWord(x, fileStr)
        attDict={word:0}
        nc_type=struct.unpack('>I', fileStr[x:x+4])[0]
        x+=4
        #print x, nc_type
        if nc_type==2: #word of chars
            x,attValue=getWord(x, fileStr)
            #print word, '=', wordValue
        elif nc_type==6: #double
            x,attValue=getDouble(x, fileStr)
            #print word, '=', doubleList
        elif nc_type==4: #4 signed byte int
            x,attValue=getIntOrFloat(x, fileStr, '>i')
            #print word, '=', intList
        elif nc_type==5: #float
            x,attValue=getIntOrFloat(x, fileStr, '>f')
            #print word, '=', floatList
        else:
            print 'not a word or double, nc_type=', nc_type
            attValue=0
        attDict[word]=attValue
        allAttDict.update(attDict)
    return x, allAttDict

def getVarList (numberOfVar,fileStr,index):
    x=index
    varDict={}
    for var in range(numberOfVar):
        x,word=getWord(x, fileStr)
        nelem=struct.unpack('>I', fileStr[x:x+4])[0]
        x+=4
        dimid=struct.unpack('>I', fileStr[x:x+4])[0]
        x+=4
        #print '--',word, 'nelem=', nelem, 'dimid=', dimid
        if struct.unpack('>I', fileStr[x:x+4])[0]==12: #vatt_list identified=12
            x+=4
            att_list=struct.unpack('>I', fileStr[x:x+4])[0]
            x+=4
            #print 'vatt_list=',att_list
            x,attDict=getAttList(att_list,fileStr,x)
            #print attDict
        else: #vatt is absent
            #print 'no vatt_list'
            attDict={}
            x+=8
        nc_type=struct.unpack('>I', fileStr[x:x+4])[0]
        x+=4
        vsize=struct.unpack('>I', fileStr[x:x+4])[0]
        attDict['vsize']=vsize
        x+=4
        begin=struct.unpack('>I', fileStr[x:x+4])[0]
        attDict['begin']=begin
        x+=4
        if nc_type==6:
            nctype='double'
            attDict['nctype']='>d'
            attDict['ncsize']=8
        elif nc_type==4:
            nctype='signed int'
            attDict['nctype']='>i'
            attDict['ncsize']=4
        elif nc_type==5:
            nctype='float'
            attDict['nctype']='>f'
            attDict['ncsize']=4
        elif nc_type==2:
            nctype='char'
            addDict['nctype']='B'
            attDict['ncsize']=1
        else:
            nctype=str(nc_type)
        varDict[word]=attDict
        #print 'nc_type=',nctype, 'vsize=', vsize, 'begin=', begin
    return x, varDict

def getVar(attDict, fileStr):
    index=attDict['begin']
    ncsize=attDict['ncsize']
    end=attDict['vsize']+index
    valueList=[]
    for x in range(index,end,ncsize):
        valueList.append(struct.unpack(attDict['nctype'], fileStr[x:x+ncsize])[0])
    return valueList

def loadNetCDF (fileName):
    numFile = open(fileName, "rb")
    fileStr=numFile.read()
    numFile.close()
    runningSum=0
    index=0
    #note: struct.unpack('B', fileStr[x]) returns a tuple, index 0 is the only element of the tuple
    for magic in range(3): #print CDF
        print chr(struct.unpack('B', fileStr[magic])[0]),
        index+=1
    print 'verson: ', int(struct.unpack('B', fileStr[index])[0])
    index+=1
    #print 'numrecs=',struct.unpack('>I', fileStr[index:index+4])[0]
    index+=4
    if struct.unpack('>I', fileStr[index:index+4])[0]==10: #10 means dim_list is present, 0 means it isn't
        index+=4
        dim_list=struct.unpack('>I', fileStr[index:index+4])[0]
        index+=4
        #print 'dim_list=',dim_list
        index,dimDict=getDimList(dim_list,fileStr,index)
        print dimDict
    else:
        index+=8 #if no dim_list then absent which is 8 0's
        print 'no dim_list'
    #print struct.unpack('>I', fileStr[index:index+4])[0]
    if struct.unpack('>I', fileStr[index:index+4])[0]==12: #12 means att_list is present, 0 means it isn't
        index+=4
        att_list=struct.unpack('>I', fileStr[index:index+4])[0]
        index+=4
        #print 'att_list=',att_list
        index,attDict=getAttList(att_list,fileStr,index)
        #print attDict
    else:
        index+=8 #if no dim_list then absent which is 8 0's
        print 'no att_list'
    #print struct.unpack('>I', fileStr[index:index+4])[0]
    if struct.unpack('>I', fileStr[index:index+4])[0]==11: #11 means var_list is present, 0 means it isn't
        index+=4
        var_list=struct.unpack('>I', fileStr[index:index+4])[0]
        index+=4
        #print 'var_list=',var_list
        #print index
        index,varDict=getVarList(var_list,fileStr,index)
        for key in varDict:
            print key, varDict[key]
#        print index
    else:
        index+=8 #if no dim_list then absent which is 8 0's
        print 'no var_list'
    #get x range
    longList=getVar(varDict['x_range'], fileStr)
    #get y range
    latList=getVar(varDict['y_range'], fileStr)
    #get z range
    heightDiffList=getVar(varDict['z_range'], fileStr)
    #get dimensions
    dimList=getVar(varDict['dimension'],fileStr)
    #get heights
    varDict['z']['vsize']=dimDict['xysize']*varDict['z']['ncsize']
    heightList=getVar(varDict['z'], fileStr)
    #del varDict['z']
    #for key in varDict:
    #    print key, '=', getVar(varDict[key], fileStr)
    return longList, latList, dimList, heightDiffList, heightList

if __name__ == '__main__':
    #loadData1('halfdome_netcdf3.nc')
    #loadData1('halfdome_97_unmasked.grd')
    #loadData1('halfdome_97_masked.grd')
    loadNetCDF('halfdome_48_unmasked.grd')
    #saveData1('halfdome_48_unmasked.grd',600,800)
    #loadData1('halfdome_48_masked.grd')
    #loadData1('halfdome_24_unmasked.grd')
    #loadData1('halfdome_24_masked.grd')
    #loadData4('lidar_halfdome_slp_1m.tif')
    #loadData4('lidar_halfdome_slp_5m.tif')
    #loadData4('ross_3794_0-6084.tif')
    #print convertLatAndLong(37.73855,37.73855,119.56926,119.499)
    #print convertLatAndLong(37.73855,37.77653,119.499,119.499)
