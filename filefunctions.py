#!/bin/python3

import mmap, csv

def writefile(filename, list):
    with open(filename, "w") as output:
        writer = csv.writer(output, delimiter=' ')
        for val in list:
            writer.writerow(val)


def readfile(filename):
    retVal = list()
    with open(filename, "r") as filename:
        reader = csv.reader(filename, delimiter=' ')
        for row in reader:
            retVal.append(row)
    return retVal

def searchinfile(filename, text):
    line = ""
    with open(filename, 'rb', 0) as file, \
        mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        index = mm.find(text.encode('utf-8'))
        if index != -1:
            mm.seek(index)
            line = mm.readline().decode('utf-8')
        return index, line

def readfileat(filename, start, end, delimiter=""):
    retval = []
    with open(filename, 'rb', 0) as file, \
        mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        mm.seek(start)
        index = start
        while index < end:
            line = mm.readline().decode('utf-8').rstrip().split(" ")
            retval.append(line.split(delimiter))

    return retval

def readfileatuntil(filename, start, endmark, delimiter=""):
    retval = []
    with open(filename, 'rb', 0) as file, \
        mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        mm.seek(start)
        while 1: 
            line = mm.readline().decode('utf-8').rstrip()
            if endmark in line:
                break
            retval.append(line.split(delimiter))

    return retval