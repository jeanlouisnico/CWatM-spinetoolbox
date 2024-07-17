import os
import sys

inifile = sys.argv[1]
''' other arguments are optional and should be treated as such'''
if len(sys.argv) > 1:
    for idx, arg in enumerate(sys.argv):
        if idx ==1:
            continue
        arg[idx-1] = arg
# Can be deleted after debugging
if __name__ == '__main__':
    for idx, arg in enumerate(sys.argv):
       print("arg #{} is {}".format(idx, arg))
    print(len(sys.argv))

