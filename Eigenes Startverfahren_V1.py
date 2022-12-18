#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd

# In[2]:


tar_pfad = 'C:/Users/laras/Documents/Master WiSe 2021/04 Vorlesungen/IT-Studienprojekt/Rohdaten/Testdaten November 2022/Daten vor Stauraumplanung/tar.asc'
tar = open(tar_pfad, 'r')
tar_vor = tar.readlines()
tar.close()

blk_pfad = 'C:/Users/laras/Documents/Master WiSe 2021/04 Vorlesungen/IT-Studienprojekt/Rohdaten/Testdaten November 2022/Daten vor Stauraumplanung/blk.asc'
blk = open(blk_pfad, 'r')
blk_vor = blk.readlines()
blk.close()

pss_pfad = 'C:/Users/laras/Documents/Master WiSe 2021/04 Vorlesungen/IT-Studienprojekt/Rohdaten/Testdaten November 2022/Daten vor Stauraumplanung/pss.asc'
pss = open(pss_pfad, 'r')
pss_vor = pss.readlines()
pss.close()

# In[3]:


blkblo_blktnt_blktre_blkk02 = {}
for z in blk_vor:
    if z[14:16] == 'LK':
        # dictionary füllen mit Blockauftragsnr.: [Tournr., Auslieferungsreihenfolge, Kommission/Klima]
        # blkblo_blktnt_blktre_blkk02[z[16:23]]=[z[426:431],z[431:436],z[281:282]]
        # dictionary füllen mit Blockauftragsnr.: [Auslieferungsreihenfolge, Kommission/Klima]
        blkblo_blktnt_blktre_blkk02[z[16:23]] = [z[431:436], z[281:282]]

blkblo_blktnt_blktre_blkk02

# In[4]:


touren2 = {}
tarnr_tarspd = {}
idx = 0

for z_tar in tar_vor:
    if z_tar[14:16] == 'AR':
        # dict mit TARNR - TARSPD füllen
        # tarnr_tarspd[z_tar[16:23]]=z_tar[53:63]
        # starte Index von TARNR erst bei 18 statt 16, da Nr. in blk nur fünfstellig
        # tarnr_tarspd[z_tar[18:23]]=z_tar[53:63]
        tarnr_tarspd[idx] = [z_tar[18:23], z_tar[53:63]]

    touren2[idx] = {'BLKBLO': [], 'BLKTNT': [], 'BLKTRE': [], 'BLKK02': []}
    for z_blk in blk_vor:
        if z_blk[426:431] == z_tar[18:23]:  # gleiche Tournr.
            touren2[idx]['BLKBLO'].append(z_blk[16:23])
            touren2[idx]['BLKTNT'].append(z_blk[426:431])
            touren2[idx]['BLKTRE'].append(z_blk[431:436])  # könnte man hier auch weglassen
            touren2[idx]['BLKK02'].append(z_blk[281:282])
    idx += 1

# print(tarnr_tarspd)
touren2

# In[5]:


paletten_je_tour = {}
idx = 0

for z_tar in tar_vor:
    paletten_je_tour[idx] = {'n_i': [], 'h_i': [], 'm_i': [], 't_i': []}

    for z_pss in pss_vor:
        # wenn BLKNR zur aktuell bearbeiteten Tour gehört
        if z_pss[25:32] in touren2[idx]['BLKBLO']:
            # hinten 1 falls dictionary blkblo_blktnt_blktre_blkk02 inkl. Tournr.
            # paletten_je_tour[idx]['n_i'].append(int(blkblo_blktnt_blktre_blkk02[z_pss[25:32]][1]))
            paletten_je_tour[idx]['n_i'].append(int(blkblo_blktnt_blktre_blkk02[z_pss[25:32]][0]))

            if int(z_pss[45:55]) > 1050:
                paletten_je_tour[idx]['h_i'].append(1)
            else:
                paletten_je_tour[idx]['h_i'].append(0)

            paletten_je_tour[idx]['m_i'].append(int(z_pss[82:94]) / 1000)

            # hinten 2 falls dictionary blkblo_blktnt_blktre_blkk02 inkl. Tournr.
            # if blkblo_blktnt_blktre_blkk02[z_pss[25:32]][2]=='Y':
            if blkblo_blktnt_blktre_blkk02[z_pss[25:32]][1] == 'Y':
                if int(z_pss[110:111]) != 2:  # wollen nur den originalen Eintrag, wenn dieser nicht 2 ist
                    paletten_je_tour[idx]['t_i'].append(int(z_pss[110:111]))
            else:  # alles andere wird als Trockenware behandelt
                paletten_je_tour[idx]['t_i'].append(0)

    idx += 1

paletten_je_tour

# In[ ]:


# In[6]:


tour_nr_04587 = paletten_je_tour[11]
len(tour_nr_04587['n_i'])

# In[7]:


tourenlaengen = []
for i in range(0, len(paletten_je_tour)):
    tourenlaengen.append(len(paletten_je_tour[i]['n_i']))

tourenlaengen

# In[8]:


tour_nr_04587

# In[9]:


h04587 = list(np.zeros(len(tour_nr_04587['n_i'])))
h04587[10] = 1

# In[10]:


tour_nr_04587['h_i'] = h04587
tour_nr_04587

# In[ ]:


# In[11]:


"""
#erste Ansätze für Sortierung der späteren Prioliste - dann aber doch für pandas entschieden

testliste = [5,4,0,6]
print(list(reversed(testliste)))
print(np.argsort(testliste)) #np.argsort findet den Index des niedrigsten Wertes zuerst
print(list(reversed(np.argsort(testliste)))) #so erhält man den Index des höchsten Wertes zuerst
"""

# In[ ]:


# In[12]:


tabelle = pd.DataFrame(
    {'i': np.arange(46), 'n_i': tour_nr_04587['n_i'], 'h_i': tour_nr_04587['h_i'], 'm_i': tour_nr_04587['m_i'],
     't_i': tour_nr_04587['t_i']})
tabelle.sort_values(by=['n_i', 'm_i'], ascending=[False, False], inplace=True)
tabelle.reset_index(inplace=True, drop=True)
tabelle

# In[13]:


tabelle.loc[0]

# In[14]:


lkwplan = pd.DataFrame({str(reihe_k): ['o', 'o', 'o', 'o', 'o', 'o'] for reihe_k in range(1, 12)})
lkwplan

# - Anzahl an Paletten
# - daraus ableiten, ob nur unten oder auch oben zu nutzen ist
# - Anzahl der ganz vollen Reihen und ggf. Restreihe berechnen
#
# - wenn die Summe der h_i (Summe über unteren&oberen Reihen bzw. die jwlg. Kunden, die da einzuordnen sind) für die eindeutigen Reihen entweder nur vorne oder nur hinten größer 0 ist:
#     plane direkt die anderen oberen Reihen als belegbar ein

# In[15]:


"""
Im Folgenden manuell ein erstes Beispiel erstellt. Muss noch in allgemeine Formulierung übertragen werden.
"""

# bei 46 Paletten wissen wir, dass oben 13 stehen
# ergibt 4 volle Reihen und eine Reihe mit einer Palette
# wenn Summe der h_i von den ersten 24 Paletten (unten+oben) >0 ist, sperren wir den Bereich

if tabelle['h_i'].loc[:24].sum() > 0:
    for row_a in range(3, 6):
        for col_a in range(1, 7):
            # lkwplan.at[row_a,str(col_a)]='x'
            lkwplan.loc[row_a, str(col_a)] = 'x'  # hier funktioniert .iloc nicht, dafür bräuchte man int oÄ

    # lkwplan.iloc[[3,4,5],[0,1,2,3,4,5]]='x'      #.loc funktioniert hier nicht - .loc würde 6 Spalten hinzufügen

lkwplan

# In[16]:


"""
#Summen berechnen
tabelle['h_i'].sum()  #ganze Spalte
tabelle['h_i'].loc[:24].sum()   #die ersten 24 Zeilen (0-23) in Spalte h_i
lkwplan_gewichte.iloc[:,6].sum()
lkwplan_gewichte.loc[lkwplan_gewichte['9']<200,'7'].sum()

#Werte überschreiben
lkwplan.loc[0,'2']=33   #alternativ lkwplan.iloc[0,1]
                        #die ganze Spalte überschreiben mit .loc[:,'2']
lkwplan

#...
"""

# In[17]:


lkwplan.shape

# In[18]:


# Zuweisungsalgorithmus anhand der Prioliste

# TODO:
# Hochpaletten dürfen nur unten stehen
# wenn wir eine Hochpalette platzieren, müssen wir die gesamte Reihe darüber sperren -> 'x'
# Kühlware muss vor Trockenware ausladbar sein

idx = 0
for col_b in range(lkwplan.shape[1]):
    for row_b in range(lkwplan.shape[0]):

        if idx > 45:
            break

        if lkwplan.iloc[row_b, col_b] != 'x':
            lkwplan.iloc[row_b, col_b] = tabelle.loc[idx, 'i']
            idx += 1

if idx < 46:
    print('Keine Zuweisung ab Palette {} (d.h. ab Reihenindex {}) möglich.'.format(tabelle.loc[idx, 'i'], idx))

lkwplan

# In[19]:


"""
tabelle_2=tabelle.set_index('i',inplace=False,drop=False)
tabelle_2.iloc[:3] #iloc[:3] gibt die ersten drei Zeilen aus; loc[:3] hingegen alle Zeilen bis einschl. Index 3
"""

# In[20]:


# Indizes von 'tabelle' ändern, damit wir einfacher auf m_i zugreifen können
tabelle_2 = tabelle.set_index('i', inplace=False, drop=False)

# neue Tabelle bzw. Beladungsplan mit Gewichtsangaben erstellen
lkwplan_gewichte = pd.DataFrame(lkwplan.copy(deep=True))

for col in range(lkwplan_gewichte.shape[1]):
    for row in range(lkwplan_gewichte.shape[0]):
        if lkwplan_gewichte.iloc[row, col] != 'x' and lkwplan_gewichte.iloc[row, col] != 'o':
            lkwplan_gewichte.iloc[row, col] = tabelle_2.loc[lkwplan_gewichte.iloc[row, col], 'm_i']
        else:
            lkwplan_gewichte.iloc[
                row, col] = 0  # Alternative hierzu wäre z. B. lkwplan_gewichte.replace('x',0,inplace=True)

lkwplan_gewichte

# In[21]:


spaltensummen = lkwplan_gewichte.sum(axis=0)
spaltensummen

# In[22]:


print(tabelle['m_i'].sum(), '<->', sum(spaltensummen))

# In[23]:


zaehler = 0
for l in range(0, 11):
    zaehler += (0.6 + 1.2 * l) * spaltensummen[l]
ladungsschw = zaehler / sum(spaltensummen)
print(f'Ladungsschwerpunkt (in m ab Stirnwand): {ladungsschw:.3f}')

# In[24]:


# erlaubter Ladungsschwerpunkt:

# benötigte Werte: (hier am Bsp. Zugmaschine MAN + Dry Liner KRONE)
radstand = 7.63
abst_kp_stw = 1.65
m_tractor = 7943
m_trailer = 7890
m_lad = sum(spaltensummen)
m_kp_max = 8797.367  # Wert siehe Excel
m_t_max = 18210  # Wert siehe Excel
last_HA_mtractor = 2343.185  # Wert siehe Excel

# Untergrenze:
lsp_u = radstand * (1 - m_kp_max / m_lad) + abst_kp_stw

# Obergrenze:
lsp_o = min(m_t_max / m_lad * radstand + abst_kp_stw,
            abst_kp_stw + radstand / m_lad * (0.75 * (m_lad + m_trailer) - 0.25 * m_tractor + last_HA_mtractor))

print(f'Untergrenze (in m ab Stirnwand): {lsp_u:.3f} \nObergrenze (in m ab Stirnwand): {lsp_o:.3f}')
print(f'Tatsächlicher Ladungsschwerpunkt (in m ab Stirnwand): {ladungsschw:.3f}')

if lsp_u <= ladungsschw and lsp_o >= ladungsschw:
    print('Achslasten eingehalten, Ergebnis passt!')
else:
    print('Achslasten nicht eingehalten')

# In[25]:


reihensummen = lkwplan_gewichte.sum(axis=1)
reihensummen

# In[26]:


gew_rechts = reihensummen[0] + reihensummen[3]
gew_links = reihensummen[2] + reihensummen[5]

print(f'Gewicht rechts:\t {gew_rechts:.2f} \nGewicht links:\t {gew_links:.2f} \nDifferenz:\t {abs(gew_rechts - gew_links):.2f}')

