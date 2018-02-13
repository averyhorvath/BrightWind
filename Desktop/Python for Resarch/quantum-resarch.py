import matplotlib.pyplot as plt
import numpy as np
from  more_itertools import unique_everseen
from IPython.display import Markdown, display
from matplotlib.pyplot import rc
import re
import pandas as pd
import collections
import matplotlib as mpl




################## USEFUL FUNCTIONS #########################
def bold(string):
    display(Markdown(string))



'''When finding coverging values, assuring the values are only printed once'''
def unique_everseen(iterable, key=None):
        """List unique elements, preserving order. Remember all elements ever seen."""
        "unique_everseen('AAAABBBCCDAABBB') --> A B C D"
        "unique_everseen('ABBCcAD', str.lower)"
        seen = set()
        seen_add = seen.add
        if key is None:
            for element in filterfalse(seen.__contains__, iterable):
                seen_add(element)
                pass
        else:
            for element in iterable:
                k = key(element)
                if k not in seen:
                    seen_add(k)
                    yield element

plt.style.use("classic")
plt.rcParams['figure.facecolor'] = 'white'

##################################IMPORTING DATA####################################
"Varied N data"
df = pd.read_excel('./research data notepad.xls',skiprows=6)
data = df[['beta_omega','N','bare','<E>/Omg', 'stderr(E)/Omg']]
Energy = df['<E>/Omg']
beta_omega = df['beta_omega']
error = df['stderr(E)/Omg']
N = df['N']
bare = df['bare']


"N = 2 data"
df2 = pd.read_excel('./research two body data.xls')
data2 = df2[['beta_omega','N','bare','<E>/Omg', 'stderr(E)/Omg']]
Energy2 = df2['<E>/Omg']
beta_omega2 = df2['beta_omega']
error2 = df2['stderr(E)/Omg']
bare2 = df2['bare']

"N = 2 vs N = 6 data"
df3 = pd.read_excel('./E2vsE6.xls')
E2_old = df3['# E2/2']
E6_old = df3['# E6/6']


###################################### MANY BODY ##############################################
"""Because the data ranges from N = 2 to N = 20"""
space = np.arange(4,22,2)
bare_space = [0.2, 1, 2, 3, 4, 5, 6]


sort = {}
bare_sort = {}
count = []


"""Sorting N values"""
for N in space:
    sliced = data[data.N==N]
    sort[N] = sliced


"Sorting Bare in same df"
for bare in bare_space:
    sliced = data[data.bare==bare]
    bare_sort[bare] = sliced
    

Emany = []
EmanyErr = []
sort = collections.OrderedDict(sorted(sort.items()))
for key in sort.keys():
    data = sort[key]

    for bare in bare_space:
        sliced = data[data.bare==bare]
        group = sliced.groupby('beta_omega').mean()
    
        
        "Value Energy converges to (Really just Energy value at beta_omega == 2.5)"
        a = group['bare'].values
        b = group['<E>/Omg'].values
        c = group['stderr(E)/Omg'].values
        Emany.append(['bare = ' + str(a[0]),'N = ' + str(key), b[4]])
        EmanyErr.append(c[4])
        
        "Plotting Averaged Energy/Omega for each fixed N and bare value against Beta Omega"
        x = group.index
        y = group['<E>/Omg'].values
        yerr = group['stderr(E)/Omg'].values
        plt.plot(x, y, label=str(bare))
        plt.errorbar(x, y,xerr = 0, yerr = yerr)
        plt.legend(loc='best',prop={'size':6})
        plt.xlabel(r'$\beta$ $\Omega$')
        plt.ylabel('E/$\Omega$')
        plt.title("Energy for N = " + str(key) + " as a Function of Beta Omega")
    plt.show()

############################################ TWO BODY #################################################

two_bare_space = np.arange(0.20, 6.20, 0.20)
two_bare_sort = {}


E2 = []
E2err = []
bareplot = []
for bare in two_bare_space:
    sliced = data2[data2.bare==bare]
    two_bare_sort[bare] = sliced
    group = sliced.groupby('beta_omega').mean()

    "group.index = beta_omega values"
    for element in group.index:
        
        "finding convergence"
        if element == 2.5:
            a = group['bare'].values
            b = group['<E>/Omg'].values
            c = group['stderr(E)/Omg'].values
            bareplot.append(a)
            E2.append(['bare = ' + str(a[0]), b[4]])
            E2err.append(c[4])
   
    "Plotting Averaged Energy/Omega for each fixed N and bare value against Beta Omega"
    x = group.index
    y = group['<E>/Omg'].values
    yerr = group['stderr(E)/Omg'].values
    plt.plot(x, y, label = str(bare))
    plt.legend(loc='upper right',prop={'size':6})
    plt.errorbar(x, y,xerr = 0, yerr = yerr)
    plt.xlabel('beta omega')
    plt.ylabel('Energy/Omega')
    plt.title('Energy vs. Beta Omega with bare fixed for N = 2')
plt.show()

           
#####################    Energy of Many Body vs. Energy of Two Body    ########################

mylist = []
mylist2 = []
x = []
y = []
bareplot = []
Nplot = []
Xerr = []
Yerr = []
 
for j in range(len(Emany)):
    
    for i in range(len(E2)):
        
        "if bare2 == bare_many"
        if E2[i][0] == Emany[j][0]:
           
            "My list = [bare, Energy Two body, N value for Many body]"
            mylist.append([E2[i][0], E2[i][1], Emany[j][1], E2err[i]])
            mylist2.append([Emany[j][2], EmanyErr[j]])
        
            "deleting repeats and separating E2 value, bare, and N"
            for value in mylist:
                if value[0] not in bareplot:
                    bareplot.append(value[0])
                if value[1] not in x:
                    x.append(value[1])
                if value[2] not in Nplot:
                    Nplot.append(value[2])
                if value[3] not in Xerr:
                    Xerr.append(value[3])
            "Doing same thing for Y-axis"
            for value in mylist2:
                if value[0] not in y:
                    y.append(value[0])
                if value[1] not in Yerr:
                    Yerr.append(value[1])
                    
"Making x and y same dimension"                   
x = [x]
y = [y[i:i+len(x[0])] for i in range(0, len(y),len(x[0]))]

"Manually make N array because Nplot is N values but strings"
N = np.array([4, 6, 8, 10, 12, 14, 16, 18, 20])

    
"dividing Energy of many body by N value"
y = [y[i][:] / N[i] for i in range(len(N))]
Yerr = [Yerr[i] / N[i] for i in range(len(N))]

color = ['r', 'deepskyblue', 'firebrick', 'g', 'b', 'yellowgreen', 'slateblue', 'm','k']


E_final = []
for i in range(len(N)):
    "Plotting New Data"
    plt.plot(x[0][:], y[i][:], marker='o', linestyle='-', color = color[i], label = "N = " + str(N[i]), zorder = 1)
    plt.errorbar(x[0][:], y[i][:], xerr = Xerr, yerr = Yerr[i], marker='o', linestyle='-', color = color[i])
    plt.xlabel(r'$\frac{E_{GS}}{\omega}{^{_{(N = 2)}}}$', fontsize = 35)
    plt.ylabel(r'$\frac{E_{GS}}{\omega  N}$', fontsize = 35)
    E_final.append(y[i][len(x) - 1])


Accepted = [6.0, 10.0, 16.0, 22.0, 28.0, 36.0, 44.0, 52.0, 60.0]
PercentErr = []
PercentErr2 = []
for i in range(len(Accepted)):
    PercentErr.append((E_final[i]*N[i] - Accepted[i])/(Accepted[i])*100)

for i in range(len(Accepted)):
    PercentErr2.append((E_final[i] - Accepted[i]/N[i])/(Accepted[i]/N[i])*100)
table = {'N': [4, 6, 8, 10, 12, 14, 16, 18, 20], 'Energy': E_final[:]*N[:], 'Accepted Energy Values': Accepted[:], 'Percent Error': PercentErr[:]}
table2 = {'N': [4, 6, 8, 10, 12, 14, 16, 18, 20], 'Energy/N': E_final[:], 'Accepted Energy/N Values': Accepted[:]/N[:], 'Percent Error': PercentErr2[:]}

t = pd.DataFrame(table, columns = ['N', 'Energy', 'Accepted Energy Values', 'Percent Error'])
t2 = pd.DataFrame(table2, columns = ['N', 'Energy/N', 'Accepted Energy/N Values', 'Percent Error'])
print(t)
print()
print(t2)

two = np.full((1, len(Accepted)), 2.0, dtype = float)

"Plotting old data on same plot"
plt.plot(E2_old*2, E6_old, marker = 'x', linestyle = '', color = 'darkblue', label = "Previous N = 6 Data", zorder = 2)
plt.plot(two[0], Accepted/N, marker = 'P', markersize = 8, linestyle = '', color = 'springgreen', label = 'Non-Interacting Values', zorder = 3)
plt.legend(loc = 'best', prop = {'size': 10}, frameon = False)
plt.xlim(-0.5, 2.25)
plt.ylim(0, 3.5)
mpl.rc("figure", facecolor = "white")
mpl.rcParams['xtick.labelsize'] = 18
mpl.rcParams['ytick.labelsize'] = 18 

fig_size = plt.rcParams["figure.figsize"]
 
print ("Current size:", fig_size)
 
fig_size[0] = 12
fig_size[1] = 8
plt.rcParams["figure.figsize"] = fig_size
plt.tight_layout()
plt.savefig('ManyBodyVsTwoBody.png', dpi = 300)
plt.show()    


