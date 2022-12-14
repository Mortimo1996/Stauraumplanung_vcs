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
    tasks = 10 #In unserem Beispiel könnten das die Rechenoperationen sein, welche wir zu der Zeit durchlaufen
    x = 0 #x stellt die Rechenoperation dar, welche gerade ausgeführt wird
    button['state']='disabled'
    while (x < tasks):
        time.sleep(1)
        bar['value'] += 10 #die zehn sind hier ein Beispiel, wenn es 5 Operationen wären bspw 20
        x+=1 #inkrementieren nach jeder ausgeführten Rechenoperation
        percent.set(str((x/tasks)*100)+"%")
        window.update_idletasks()

def quit():
    window.destroy()

window = Tk()
window.title("Stauraumplanung")


### Window size
window.width = 500
window.height = 50

window.eval('tk::PlaceWindow . center')


percent = StringVar()
bar = Progressbar(window,orient=HORIZONTAL,length=400)
bar.pack(pady=10)

percentlabel = Label(window,textvariable=percent).pack()
button = Button(window,text="Download",command=start)
button2 = Button(window,text="Close",command=quit)

button.pack() #evtl pack(pady=10)
button2.pack()

window.mainloop()






########################################################################################################
#Sammlung Lara

#gute Beispiele für mip: https://python-mip.readthedocs.io/en/latest/examples.html
#https://python-mip.readthedocs.io/en/latest/classes.html

from sys import stdout
from mip import Model, xsum, minimize, maximize, BINARY
from itertools import product
import numpy as np


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

#Parameter definieren - P, h und m sind hier für die Tour 04587 aus den Novemberdaten
P=46
Q=max(0,P-33)

I=range(P)
J=range(2)
K=range(11)
L=range(3)

n=np.arange(P)
h=np.zeros(P)
h[10]=1         #hier vereinfacht nur eine Hochpalette angenommen
m=[891.2, 376.04, 376.04, 891.2, 141.032, 600.8, 600.8, 600.8, 376.04, 376.04, 196.392, 153.074, 362.078, 362.078, 376.04, 376.04, 376.04, 376.04, 376.04, 367.472, 323.03, 344.146, 258.46, 156.054, 276.918, 29.059, 113.13, 376.04, 376.04, 335.94, 313.952, 274.056, 189.256, 367.472, 278.1, 106.94, 525.008, 424.568, 377.743, 164.288, 367.472, 213.34, 376.04, 202.532, 378.2, 376.04]

M=100


#Variablen hinzufügen
"""x = [[[[model.add_var('x({},{},{},{})'.format(i,j,k,l), var_type=BINARY)
        for l in range(1,3+1)] for k in range(1,4+1)] for j in range(1,2+1)] for i in range(1,n+1)]

# model.vars['x(5,2,4,3)'] entspricht x[4][1][3][2] - deshalb var-Erstellung nochmal geändert"""

x = [[[[model.add_var('x({},{},{},{})'.format(i,j,k,l), var_type=BINARY)
        for l in L] for k in K] for j in J] for i in I]
# jetzt entspricht model.vars['x(4,1,3,2)'] auch x[4][1][3][2]

GL = model.add_var(name='GL', lb=0, var_type='C')
GR = model.add_var(name='GR', lb=0, var_type='C')


#Nebenbedingungen hinzufügen
#NB jede Pal einen Platz
for i in I:
  model += xsum(x[i][j][k][l] for j in J for k in K for l in L) == 1

#NB jeder Platz max. eine Pal
for j,k,l in product(J,K,L):
  model += xsum(x[i][j][k][l] for i in I) <= 1

#NB Hochpal muss unten stehen
model += xsum(h[i]*x[i][1][k][l] for i in I for k in K for l in L) == 0

#NB Reihe über Hochpal frei
for i,k,l in product(I,K,L):
  model += h[i]*x[i][0][k][l] + h[i]*xsum(x[i_s][1][k][l_s] for l_s in L for i_s in I if i_s != i) <= 1+M*(1-x[i][0][k][l])

#NB Ladebalken Reihe oben max. 2t
for k in K:
  model += xsum(m[i]*x[i][1][k][l] for i in I for l in L) <= 2000

#NB zuerst unten voll
model += xsum(x[i][1][k][l] for i in I for k in K for l in L) == Q

#NB unten nur hinten an der Tür frei
for k,l in product(K[1:],L):
  model += xsum(x[i][0][k-1][l_s] for i in I for l_s in L) >= xsum(x[i][0][k][l] for i in I)*3

#NB oben kein Freiraum vorne, Y
#NB oben kein Freiraum hinten, Y
#NB oben kein Freiraum vorne, W
#NB oben kein Freiraum hinten, W

#NB Restreihe: bei zwei Paletten muss eine in der Mitte stehen
for j,k in product(J,K):
  model += M*xsum(x[i][j][k][1] for i in I) >= xsum(x[i][j][k][l] for i in I for l in L)-1

#NB Restreihe: einzelne Palette darf nicht in der Mitte stehen
for j,k in product(J,K):
  model += 2*(xsum(x[i][j][k][0] for i in I)+xsum(x[i][j][k][2] for i in I)) >= xsum(x[i][j][k][l] for i in I for l in L)

#NB Ladungsschwerpunkt Untergrenze
#NB Ladungsschwerpunkt Obergrenze

#NB Auslieferungsreihenfolge
for i,i_s,j,j_s,k,l,l_s in product(I,I,J,J,K[1:],L,L):
  model += x[i][j][k][l]*n[i] <= x[i_s][j_s][k-1][l_s]*n[i_s] + (1-x[i_s][j_s][k-1][l_s])*M

"""#alternativ (falls Freiräume mittig zugelassen werden):
for i,i_s,j,j_s,k,k_s,l,l_s in product(I,I,J,J,K,K,L,L):
  if k_s<k:
    model += x[i][j][k][l]*n[i] <= x[i_s][j_s][k_s][l_s]*n[i_s] + (1-x[i_s][j_s][k_s][l_s])*M"""

#NB kühl-trocken

#NB zur Vorbereitung der Zielfunktion
model += GL >= xsum(x[i][j][k][0]*m[i] for i in I for j in J for k in K) - xsum(x[i][j][k][2]*m[i] for i in I for j in J for k in K)
model += GR >= xsum(x[i][j][k][2]*m[i] for i in I for j in J for k in K) - xsum(x[i][j][k][0]*m[i] for i in I for j in J for k in K)


#Zielfunktion
model.objective = minimize(GL+GR)


#Zielfunktion vereinfacht: Summe aller x (=P)
#model.objective = maximize(xsum(x[i][j][k][l] for i in I for j in J for k in K for l in L))


#Optimierung mit Abbruchkriterien
model.max_mip_gap_abs = 0.1
#model.max_solutions = 1
status = model.optimize() #max_seconds_same_incumbent=60    max_nodes=25


if model.num_solutions: #nur wenn überhaupt eine Lösung gefunden wurde
    print('\nLösung gefunden, Status:',status)
    #print('Summe über alle x =',xsum(x[i][j][k][l] for i in I for j in J for k in K for l in L).x)
    print('ZFW =',GL.x+GR.x)
    print(model.num_solutions)
    print('\n')

    for i,j,k,l in product(I,J,K,L):
      if x[i][j][k][l].x >= 0.99:
        print('x({},{},{},{})'.format(i,j,k,l))

else:
  print('\n\nnichts gefunden')
  print('Letzter Status:',status,'\n')

