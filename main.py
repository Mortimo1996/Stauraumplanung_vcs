# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from tqdm import tqdm
import time
import progressbar
from tkinter import *
from tkinter import ttk
import time
import threading
from tkinter.ttk import *
import tkinter
import timeit

#https://www.youtube.com/watch?v=0WRMYdOwHYE
def start():
    buttonlock = False
    tasks = 10  # In unserem Beispiel könnten das die Rechenoperationen sein, welche wir zu der Zeit durchlaufen
    x = 0  # x stellt die Rechenoperation dar, welche gerade ausgeführt wird
    if buttonlock == False:
        while (x < tasks):
            time.sleep(1)
            bar['value'] += 10 # die zehn sind hier ein Beispiel, wenn es 5 Operationen wären bspw 20
            x += 1  # inkrementieren nach jeder ausgeführten Rechenoperation
            percent.set(str((x / tasks) * 100) + "%")
            button.configure(state=DISABLED)
            window.update()



def quit():
    window.destroy()


window = Tk()
window.title("Stauraumplanung")


### Window size
window.width = 500
window.height = 50

window.eval('tk::PlaceWindow . center')


percent = StringVar()
bar = Progressbar(window, orient=HORIZONTAL, length=400)
bar.pack(pady=10)

percentlabel = Label(window, textvariable=percent).pack()
button = Button(window, text="Download", command=start).pack(pady=10)
button2 = Button(window,text="Close",command=quit).pack()

window.mainloop()






########################################################################################################
#Sammlung Lara

#gute Bsp. für mip: https://python-mip.readthedocs.io/en/latest/examples.html

from sys import stdout
from mip import Model, xsum, minimize, maximize, BINARY
from itertools import product


#______________________________________________________________________________________________________
#### Schach-Beispiel ####
# number of queens
n = 40

queens = Model()

x = [[queens.add_var('x({},{})'.format(i, j), var_type=BINARY)
      for j in range(n)] for i in range(n)]

# one per row
for i in range(n):
    queens += xsum(x[i][j] for j in range(n)) == 1, 'row({})'.format(i)

# one per column
for j in range(n):
    queens += xsum(x[i][j] for i in range(n)) == 1, 'col({})'.format(j)

# diagonal \
for p, k in enumerate(range(2 - n, n - 2 + 1)):
    queens += xsum(x[i][i - k] for i in range(n)
                   if 0 <= i - k < n) <= 1, 'diag1({})'.format(p)

# diagonal /
for p, k in enumerate(range(3, n + n)):
    queens += xsum(x[i][k - i] for i in range(n)
                   if 0 <= k - i < n) <= 1, 'diag2({})'.format(p)

queens.optimize()

if queens.num_solutions:
    stdout.write('\n')
    for i, v in enumerate(queens.vars):
        stdout.write('O ' if v.x >= 0.99 else '. ')
        if i % n == n-1:
            stdout.write('\n')


"""#Abfragen zum Testen im Notebook
queens.vars[17].x
queens.vars[40*40-1] #letzte Zahl innerhalb der range bei n=40
queens.vars[7*40+1].x
queens.vars[3*40-1].x

queens.vars[7*40+1]
queens.vars['x(7,1)']

print(queens.vars['x(7,1)'],'\t',queens.vars['x(7,1)'].x)
print(queens.vars[7*40+1],'\t',queens.vars[7*40+1].x)"""

#______________________________________________________________________________________________________



#### Unser Projekt ####
model = Model()
n=5
"""x = [[[[model.add_var('x({},{},{},{})'.format(i,j,k,l), var_type=BINARY)
        for l in range(1,3+1)] for k in range(1,4+1)] for j in range(1,2+1)] for i in range(1,n+1)]

# model.vars['x(5,2,4,3)'] entspricht x[4][1][3][2] - deshalb var-Erstellung nochmal geändert"""

I=range(n)
J=range(2)
K=range(4)
L=range(3)

x = [[[[model.add_var('x({},{},{},{})'.format(i,j,k,l), var_type=BINARY)
        for l in L] for k in K] for j in J] for i in I]

# jetzt entspricht model.vars['x(4,1,3,2)'] auch x[4][1][3][2]

#Zielfunktion: hier vereinfacht erstmal die Summe
model.objective = maximize(xsum(x[i][j][k][l] for i in I for j in J for k in K for l in L))

#NB jede Pal einen Platz
for i in I:
  model += xsum(x[i][j][k][l] for j in J for k in K for l in L) == 1

#NB jeder Platz max. eine Pal
for j,k,l in product(J,K,L):
  model += xsum(x[i][j][k][l] for i in I) <= 1


#optimize
model.optimize()

if model.num_solutions: #nur wenn überhaupt eine Lösung gefunden wurde
    print('Lösung gefunden')
    #for i,j,k,l in product(I,J,K,L):
      #print(x[i][j][k][l].x)

    print('Summe über alle x =',xsum(x[i][j][k][l] for i in I for j in J for k in K for l in L).x)

