#gute Beispiele für mip: https://python-mip.readthedocs.io/en/latest/examples.html
#https://python-mip.readthedocs.io/en/latest/classes.html


from mip import Model, xsum, minimize, maximize, BINARY
from itertools import product
import numpy as np
import time

starttime = time.time()


model = Model()

#Parameter definieren - P, h und m sind hier für die Tour 04587 aus den Novemberdaten
P=46
Q=max(0,P-33)

I=range(P)
J=range(2)
K=range(11)
L=range(3)

n=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3, 3]
h=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
m=[376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 376.04, 324.832, 503.96, 38.516, 114.142, 139.466]

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
#model.max_mip_gap_abs = 0.1
#model.max_solutions = 1
status = model.optimize(max_nodes=10000) #max_seconds_same_incumbent=60


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


print(f'Verfahrensdauer: {time.time() - starttime}')