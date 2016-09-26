#!/usr/bin/python


vers = '1.0'
import sys
import warnings
warnings.filterwarnings("ignore", module="matplotlib")

try:
    import matplotlib.pyplot as plt
except ImportError:
    sys.exit('ERROR: matplotlib is not installed ')
try:
    import numpy as np
except ImportError:
    sys.exit('ERROR: numpy is not installed ')
global dfa
dfa = 0


###---------function: read the star file get the header, labels, and data -------------#######
def read_starfile(f):
    alldata = open(f,'r').readlines()
    labelsdic = {}
    data = []
    header = []
    for i in alldata:
        if '#' in i:
            labelsdic[i.split('#')[0]] = int(i.split('#')[1])-1
        if len(i.split()) > 3:
            data.append(i.split())
        if len(i.split()) < 3:
            header.append(i.strip("\n"))
    return(labelsdic,header,data)
#---------------------------------------------------------------------------------------------#

#------------------------------get arguments -----------------------------------------#
class Arg(object):
    _registry = []
    def __init__(self, flag, value, req):
        self._registry.append(self)
        self.flag = flag
        self.value = value
        self.req = req
errmsg = '''USAGE: rln-star-filter.py --i <starfile>
optional flags:
--about     print the license and contact information'''

def make_arg(flag, value, req):
    Argument = Arg(flag, value, req)
    if Argument.req == True:
        if Argument.flag not in sys.argv:
            print(errmsg)
            sys.exit("ERROR: required argument '{0}' is missing".format(Argument.flag))
    if Argument.value == True:
        try:
            test = sys.argv[sys.argv.index(Argument.flag)+1]
        except ValueError:
            if Argument.req == True:
                print(errmsg)
                sys.exit("ERROR: required argument '{0}' is missing".format(Argument.flag))
            elif Argument.req == False:
                return False
        except IndexError:
                print(errmsg)
                sys.exit("ERROR: argument '{0}' requires a value".format(Argument.flag))
        else:
            if Argument.value == True:
                Argument.value = sys.argv[sys.argv.index(Argument.flag)+1]
        
    if Argument.value == False:
        if Argument.flag in sys.argv:
            Argument.value = True
        else:
            Argument.value = False
    return Argument.value
#-----------------------------------------------------------------------------------#


#---- get the stats of the files - make some pretty graphs
def get_stats_make_graphs(alldata,choice,choicename):
    global dfa
    
    vals = []
    for i in alldata:
        try:
            float(i[choice])
        except ValueError:
            sys.exit('ERROR: This coulmn does not contain numerical values\n Example data: {0}'.format(i[choice]))
        vals.append(float(i[choice]))

    valmin = min(vals)
    valmax = max(vals)
    

    #-- make plot
    n, bins, patches = plt.hist(vals, 100, facecolor='green', alpha=0.75)
    plt.xlabel(choicename,fontsize=10)
    plt.ylabel('Particles',fontsize=10)
    plt.tick_params(axis='both', which='major', labelsize=8)

    plt.tight_layout()
    plt.savefig('star-filt_analysis_{0}.png'.format(dfa))
    plt.close()
    dfa +=1 
    return(vals)
    

#------------------------------------------------------------------------

#----make menu--------------------------------------------------------------------
def make_menu():
    global choices
    optno = 1
    print('\n')
    choices = {}
    for i in labels:
        print("{0}) {1}".format(optno,i))
        choices[optno] = i
        optno+=1
#------------------------------------------------------------------------




print("**** Relion Star Filteringv{0} ****".format(vers))
print("2016 | Astbury Centre for Structural Molecular Biology | University of Leeds")
about = make_arg('--about',False,False)
if about != False:
    print ("""2016 Matt Iadanza - University of Leeds - Astbury Centre for Structural Molecular Biology
contact fbsmi@leeds.ac.uk for suggestions/bug reports

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.""")
    sys.exit()

thefile = make_arg('--i',True,True)
(labels,header,data) = read_starfile(thefile)

make_menu()
choice= int(raw_input('Pick the data column to filter on: '))

vals = get_stats_make_graphs(data,labels[choices[choice]],choices[choice])

print('\n** look at the pretty graph in star-filt_analysis_0.png **')
cull = raw_input('do you want to cull the micrographs (y/n)?')
if cull not in ('yes','Y','y','YES','Yes'):
    sys.exit('Finished, Goodbye')
# stats:
min,max,mean,sd=(min(vals),max(vals),np.mean(vals),np.std(vals))
print('\n** {0} statistics**'.format(choices[choice]))
print('min:\t{0}'.format(min))
print ('max:\t{0}'.format(max))
print ('mean:\t{0}'.format(mean))
print ('sd:\t{0}'.format(sd))



print('Enter filter parameters - what do you want to keep')
ll = 0
ul = 100000000000
ul = raw_input('Low pass filter - keep values below this number - leave blank for no filter: ') or 10000000000000 
ll = raw_input('High pass filter - keep values above this number - leave blank for no filter: : ') or 0
ul = float(ul)
ll = float(ll)

fname = thefile.split('.')[0]
output = open('{0}_filt{1}.star'.format(fname,choices[choice].strip()),'w')
for i in header:
    output.write('{0}\n'.format(i))
output.write('\n')
for i in data:
    if float(i[labels[choices[choice]]]) > ll and float(i[labels[choices[choice]]]) < ul:
        output.write('{0}\n'.format("  ".join(i)))
