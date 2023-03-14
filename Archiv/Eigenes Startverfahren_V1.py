#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import math

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

print(tarnr_tarspd)
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


tabelle = pd.DataFrame(
    {'i': np.arange(46), 'n_i': tour_nr_04587['n_i'], 'h_i': tour_nr_04587['h_i'], 'm_i': tour_nr_04587['m_i'],
     't_i': tour_nr_04587['t_i']})
tabelle.sort_values(by=['n_i', 't_i', 'm_i'], ascending=[False, True, False], inplace=True)
tabelle.reset_index(inplace=True, drop=True)
tabelle

# In[12]:


lkwplan = pd.DataFrame({str(reihe_k): ['o', 'o', 'o', 'o', 'o', 'o'] for reihe_k in range(1, 12)})
lkwplan

# In[13]:


anz_pal = max(tabelle['i']) + 1
oben = max(anz_pal - 33, 0)

if anz_pal <= 33:
    for row_a in range(3, 6):
        lkwplan.loc[row_a][:] = 'x'

    if anz_pal <= 30:  # bei weniger als 31 gibt es zwei Möglichkeiten für ganz freie Reihen
        lkwplan_v2 = pd.DataFrame(lkwplan.copy(deep=True))

        for frei in range(0, 11 - math.ceil(anz_pal / 3)):
            lkwplan_v2.iloc[3:, frei] = 'x'

elif anz_pal <= 63:  # auch hier gibt es zwei Möglichkeiten für ganz freie Reihen
    lkwplan_v2 = pd.DataFrame(lkwplan.copy(deep=True))

    for frei in range(0, 11 - math.ceil(oben / 3)):
        lkwplan_v2.iloc[3:, frei] = 'x'

# bei 64 oder mehr mache nichts, weil Restreihe an der Tür ist & alle anderen Reihen voll sind


# dann kann man beide Versionen füllen und wenn HPal kommt, ganze Reihen sperren
# man könnte trotzdem weiter befüllen, aber Strafkosten vergeben, damit ideale Lösung (wenn es eine gibt) besser ist
# oder man bricht dann ab und schaut erst, ob es so möglich wäre


# In[14]:


lkwplan_v2


# In[15]:


# lkwplan.loc[0][:]='x' #ganze Zeilen mit x füllen
# lkwplan['1'][:]='x' #ganze Spalten mit x füllen

# lkwplan


# In[ ]:


# In[16]:


def plan_fuellen(lkwplan, oben):
    col_b = 0
    row_b = 0
    idx = 0

    while idx < anz_pal:

        if oben == 0:
            for row_c in range(3, 6):
                for col_c in range(col_b, 11):
                    if lkwplan.iloc[row_c, col_c] == 'o':
                        lkwplan.iloc[row_c, col_c] = 'x'

        if row_b >= lkwplan.shape[0]:
            row_b = 0
            col_b += 1

        if col_b >= lkwplan.shape[1]:
            print('Keine Zuweisung ab Palette {} (d.h. ab Reihenindex {}) möglich.'.format(tabelle.loc[idx, 'i'], idx))
            break

        if row_b == 0 and tabelle.loc[idx:idx + 6, 'h_i'].sum() >= 1:
            lkwplan.iloc[3:, col_b] = 'x'

        if lkwplan.iloc[row_b, col_b] != 'x':
            lkwplan.iloc[row_b, col_b] = tabelle.loc[idx, 'i']
            idx += 1
            if row_b >= 3:
                oben -= 1

        row_b += 1


# In[17]:


plan_fuellen(lkwplan, oben)
plan_fuellen(lkwplan_v2, oben)

lkwplan

# In[18]:


lkwplan_v2

# In[ ]:


# In[ ]:


# In[19]:


# Annahmen vorab
# benötigte Werte: (hier am Bsp. Zugmaschine MAN + Dry Liner KRONE)
radstand = 7.63
abst_kp_stw = 1.65
m_tractor = 7943
m_trailer = 7890
m_kp_max = 8797.367  # Wert siehe Excel
m_t_max = 18210  # Wert siehe Excel
last_HA_mtractor = 2343.185  # Wert siehe Excel

# tourenabhängige Werte
m_lad = tabelle['m_i'].sum()

# Untergrenze:
lsp_u = radstand * (1 - m_kp_max / m_lad) + abst_kp_stw

# Obergrenze:
lsp_o = min(m_t_max / m_lad * radstand + abst_kp_stw,
            abst_kp_stw + radstand / m_lad * (0.75 * (m_lad + m_trailer) - 0.25 * m_tractor + last_HA_mtractor))

print(f'Untergrenze (in m ab Stirnwand): {lsp_u:.3f} \nObergrenze (in m ab Stirnwand): {lsp_o:.3f}')


# In[20]:


def plan_gewichte_auswertung(tabelle, lkwplan):
    # Indizes von 'tabelle' ändern, damit wir einfacher auf m_i zugreifen können
    tabelle_2 = tabelle.set_index('i', inplace=False, drop=False)  # erzeugt eine Kopie

    # neue Tabelle bzw. Beladungsplan mit Gewichtsangaben erstellen
    lkwplan_gewichte = pd.DataFrame(lkwplan.copy(deep=True))

    for col in range(lkwplan_gewichte.shape[1]):
        for row in range(lkwplan_gewichte.shape[0]):
            if lkwplan_gewichte.iloc[row, col] != 'x' and lkwplan_gewichte.iloc[row, col] != 'o':
                lkwplan_gewichte.iloc[row, col] = tabelle_2.loc[lkwplan_gewichte.iloc[row, col], 'm_i']
            else:
                lkwplan_gewichte.iloc[
                    row, col] = 0  # Alternative hierzu wäre z. B. lkwplan_gewichte.replace('x',0,inplace=True)

    spaltensum_oben = lkwplan_gewichte.loc[3:].sum(axis=0)
    pruefe_ladebalken = 0
    for i in spaltensum_oben:
        if i > 2000:
            pruefe_ladebalken += 1
    if pruefe_ladebalken == 0:
        print('Ladebalkenbelastung zulässig!')
    else:
        print('Ladebalken überlastet')

    spaltensummen = lkwplan_gewichte.sum(axis=0)
    zaehler = 0
    for l in range(0, 11):
        zaehler += (0.6 + 1.2 * l) * spaltensummen[l]
    ladungsschw = zaehler / sum(spaltensummen)

    if lsp_u <= ladungsschw and lsp_o >= ladungsschw:
        print(f'Achslasten eingehalten! \t-> Ladungsschwerpunkt (in m ab Stirnwand): {ladungsschw:.3f}')
    else:
        print(f'Achslasten nicht eingehalten \t-> Ladungsschwerpunkt (in m ab Stirnwand): {ladungsschw:.3f}')

    reihensummen = lkwplan_gewichte.sum(axis=1)

    gew_rechts = reihensummen[0] + reihensummen[3]
    gew_links = reihensummen[2] + reihensummen[5]

    print(f'Gewichtsdifferenz links/rechts:\t {abs(gew_rechts - gew_links):.2f}')


# In[21]:


plan_gewichte_auswertung(tabelle, lkwplan)

# In[22]:


plan_gewichte_auswertung(tabelle, lkwplan_v2)

# In[ ]:


