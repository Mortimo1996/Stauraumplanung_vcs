#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import math
import time
from random import randint

# In[2]:


starttime = time.time()

# In[3]:


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

# In[4]:


blkblo_blktnt_blktre_blkk02 = {}
for z in blk_vor:
    if z[14:16] == 'LK':
        # dictionary füllen mit Blockauftragsnr.: [Tournr., Auslieferungsreihenfolge, Kommission/Klima]
        # blkblo_blktnt_blktre_blkk02[z[16:23]]=[z[426:431],z[431:436],z[281:282]]
        # dictionary füllen mit Blockauftragsnr.: [Auslieferungsreihenfolge, Kommission/Klima]
        blkblo_blktnt_blktre_blkk02[z[16:23]] = [z[431:436], z[281:282]]

blkblo_blktnt_blktre_blkk02

# In[5]:


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

# In[6]:


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


# In[7]:


tour_nr_04587 = paletten_je_tour[11]
len(tour_nr_04587['n_i'])

# In[8]:


tourenlaengen = []
for i in range(0, len(paletten_je_tour)):
    tourenlaengen.append(len(paletten_je_tour[i]['n_i']))

tourenlaengen

# In[9]:


h04587 = list(np.zeros(len(tour_nr_04587['n_i'])))
h04587[10] = 1
h04587[11] = 1
tour_nr_04587['h_i'] = h04587


# In[ ]:


# In[10]:


def plan_fuellen(tabelle, lkwplan, anz_pal, oben, option):
    if option == 1:  # "normal", aufsteigend durch Zeilen und Spalten
        col_b = 0
        row_b = 0
        idx_pal = 0

        while idx_pal < anz_pal:

            if oben == 0:
                for row_c in range(3, 6):
                    for col_c in range(col_b, 11):
                        if lkwplan.iloc[row_c, col_c] == 'o':
                            lkwplan.iloc[row_c, col_c] = 'x'

            if row_b >= lkwplan.shape[0]:
                row_b = 0
                col_b += 1

            if col_b >= lkwplan.shape[1]:
                # print('Keine Zuweisung ab Palette {} (d.h. ab Reihenindex {}) möglich.'.format(tabelle.loc[idx_pal,'i'],idx_pal))
                break

            if row_b == 0 and tabelle.loc[idx_pal:idx_pal + 6, 'h_i'].sum() >= 1:
                lkwplan.iloc[3:, col_b] = 'x'

            if lkwplan.iloc[row_b, col_b] != 'x':
                lkwplan.iloc[row_b, col_b] = tabelle.loc[idx_pal, 'i']
                idx_pal += 1
                if row_b >= 3:
                    oben -= 1

            row_b += 1



    elif option == 2:  # nacheinander aufsteigend durch Spalten, aufsteigend untere Zeilen, absteigend obere Zeilen
        col_a = 0
        idx_pal = 0
        rows = [0, 1, 2, 5, 4, 3]
        row_idx = 0

        while idx_pal < anz_pal:

            if oben == 0:
                for row_c in range(3, 6):
                    for col_c in range(col_a, 11):
                        if lkwplan.iloc[row_c, col_c] == 'o':
                            lkwplan.iloc[row_c, col_c] = 'x'

            if row_idx >= lkwplan.shape[0]:  # bzw. >= len(rows)
                row_idx = 0
                col_a += 1

            if col_a >= lkwplan.shape[1]:
                # print('Keine Zuweisung ab Palette {} (d.h. ab Reihenindex {}) möglich.'.format(tabelle.loc[idx_pal,'i'],idx_pal))
                break

            if row_idx == 0 and tabelle.loc[idx_pal:idx_pal + 6, 'h_i'].sum() >= 1:
                lkwplan.iloc[3:, col_a] = 'x'

            if lkwplan.iloc[rows[row_idx], col_a] != 'x':
                lkwplan.iloc[rows[row_idx], col_a] = tabelle.loc[idx_pal, 'i']
                idx_pal += 1
                if rows[row_idx] >= 3:
                    oben -= 1

            row_idx += 1



    elif option == 3:  # nacheinander aufsteigend durch Spalten, dabei zufällige Zeilen
        col_d = 0
        idx_pal = 0
        row_opt = [0, 1, 2, 3, 4, 5]

        while idx_pal < anz_pal:

            if oben == 0:
                for row_c in range(3, 6):
                    for col_c in range(col_d, 11):
                        if lkwplan.iloc[row_c, col_c] == 'o':
                            lkwplan.iloc[row_c, col_c] = 'x'

            if len(row_opt) == 0:
                col_d += 1

                if oben == 2 and anz_pal % 3 == 2:
                    if randint(0, 1) == 0:
                        row_opt = [0, 1, 2, 4, 5]
                    else:
                        row_opt = [0, 1, 2, 3, 4]
                elif oben == 1 and anz_pal % 3 == 1:
                    row_opt = [0, 1, 2, 3, 5]
                else:
                    row_opt = [0, 1, 2, 3, 4, 5]

            if col_d >= lkwplan.shape[1]:
                # print('Keine Zuweisung ab Palette {} (d.h. ab Reihenindex {}) möglich.'.format(tabelle.loc[idx_pal,'i'],idx_pal))
                break

            nr = randint(0, len(row_opt) - 1)  # randint(0,5) zieht eine zufällige Zahl von 0 bis 5 (inkl. 0 und 5)

            if len(row_opt) == 6 and tabelle.loc[idx_pal:idx_pal + 6, 'h_i'].sum() >= 1:
                lkwplan.iloc[3:, col_d] = 'x'

            if lkwplan.iloc[row_opt[nr], col_d] != 'x':
                lkwplan.iloc[row_opt[nr], col_d] = tabelle.loc[idx_pal, 'i']
                idx_pal += 1
                if row_opt[nr] >= 3:
                    oben -= 1

            row_opt.remove(row_opt[nr])


# In[11]:


def gewichte_bestimmen(tabelle_g, lkwplan_g):  # wird von Funktion "plan_bewertung" aufgerufen
    # Indizes von 'tabelle' ändern, damit wir einfacher auf m_i zugreifen können
    tabelle_2 = tabelle_g.set_index('i', inplace=False, drop=False)  # erzeugt eine Kopie

    # neue Tabelle bzw. Beladungsplan mit Gewichtsangaben erstellen
    lkwplan_gewichte = pd.DataFrame(lkwplan_g.copy(deep=True))

    for col in range(lkwplan_gewichte.shape[1]):
        for row in range(lkwplan_gewichte.shape[0]):
            if lkwplan_gewichte.iloc[row, col] != 'x' and lkwplan_gewichte.iloc[row, col] != 'o':
                lkwplan_gewichte.iloc[row, col] = tabelle_2.loc[lkwplan_gewichte.iloc[row, col], 'm_i']
            else:
                lkwplan_gewichte.iloc[
                    row, col] = 0  # Alternative hierzu wäre z. B. lkwplan_gewichte.replace('x',0,inplace=True)

    spaltensum_oben = lkwplan_gewichte.loc[3:].sum(axis=0)
    spaltensummen = lkwplan_gewichte.sum(axis=0)
    zeilensummen = lkwplan_gewichte.sum(axis=1)

    return zeilensummen, spaltensummen, spaltensum_oben


# In[12]:


def plan_bewertung(tabelle_, lkwplan_):
    bewertung = [0 for i in range(7)]  # erzeugt Liste mit 7 Nullen, 0 bedeutet "alles gut"

    # ---kein idx, da im Startverf.: Restreihe ist "an der Tür"
    # ---kein idx, da in Verbesserung: Restreihe_einzeln am Rand, zwei mittig&Rand
    # ---kein idx, da im Startverf.: oben stehen genau Q Paletten
    # ---kein idx, da Start&Verbesserung berücksichtigen: Auslieferungsreihenfolge

    # R idx0: Anzahl nicht eingeplanter Paletten (0 = am besten)
    # R idx1: alle Hochpaletten haben einen zulässigen Platz (stehen unten & obere Reihe komplett leer)
    # .> +0.01, wenn HPal nicht unten steht; +1, wenn über einer HPal nicht frei ist
    # .> durch diese Werte könnte man hinterher auswerten, was das Problem ist - brauchen wir das?
    # R idx2: kühl-trocken-Trennung auch nach Austausch berücksichtigt
    # .> eigener idx sinnvoll, da dies ggf später vernachlässigt werden darf
    # R idx3: Anz zusätzl benötigter Ladungssicherung durch ganz freie Reihen mittendrin
    # .> ideal wäre NUR vorne oder NUR hinten ganze Reihen frei - 1x Ladungssicherung ist also ideal
    ##### bisher nur oben möglich, falls HP unten -> andere Möglichkeiten ggf. noch ergänzen (?)

    # G idx4: Ladebalkenbelastung eingehalten (max. 2 t pro 3er-Reihe oben)
    # G idx5: Achslastvorgaben einhalten!
    # G idx6: Gewichtsdifferenz

    # --------------------------------------------------------------------------------------
    # für die G-Teile (Gewichte):
    z_sum, sp_sum, sp_sum_oben = gewichte_bestimmen(tabelle_, lkwplan_)

    # G idx4: Ladebalkenbelastung eingehalten (max. 2 t pro 3er-Reihe oben)
    ladebalken_ueberl_col = []
    for col in sp_sum_oben.index:
        if sp_sum_oben[col] > 2000:
            ladebalken_ueberl_col.append(col)
            bewertung[4] = 1

    # G idx5: Achslastvorgaben einhalten!
    zaehler = 0
    for l in range(0, 11):
        zaehler += (0.6 + 1.2 * l) * sp_sum[l]
    ladungsschw = zaehler / sum(sp_sum)

    if lsp_u > ladungsschw or lsp_o < ladungsschw:
        bewertung[5] = 1  # Ladungsschwerpunkt außerhalb des zulässigen Bereichs, Achslasten nicht eingehalten

    # G idx6: Gewichtsdifferenz
    gew_rechts = z_sum[0] + z_sum[3]
    gew_links = z_sum[2] + z_sum[5]

    bewertung[6] = abs(gew_rechts - gew_links)

    # --------------------------------------------------------------------------------------
    # für die R-Teile (räumlich):

    # R idx0: Anzahl nicht eingeplanter Paletten (0 = am besten)
    freieplaetze = 0
    for col_idx in range(lkwplan_.shape[1]):
        for row_idx in range(lkwplan_.shape[0]):
            if type(lkwplan_.iloc[row_idx, col_idx]) == str:
                freieplaetze += 1

    bewertung[0] = freieplaetze - (66 - anz_pal)

    # R idx1: alle Hochpaletten haben einen zulässigen Platz (stehen unten & obere Reihe komplett leer)
    hpaletten = tabelle_[tabelle_['h_i'] > 0].reset_index(inplace=False, drop=True)

    for hpal in range(hpaletten.shape[0]):  # für jede HPal einzeln, daher rowhp und colhp immer nur ein Element

        try:
            rowhp = list(lkwplan_[lkwplan_.isin([hpaletten.loc[hpal, 'i']]).any(axis=1)].index)[0]
            colhp = str(list(lkwplan_.columns[lkwplan_.isin([hpaletten.loc[hpal, 'i']]).any()])[0])
        except:
            bewertung[1] = 100  # 100 als Kennzeichen, dass HPal nicht mehr eingeplant werden konnte
        else:
            if rowhp >= 3:  # falls eine HPal oben steht
                bewertung[1] += 0.01

            # Spaltensumme der Gewichte in Zeilen [3:] sollte == 0 sein (= oben frei)
            if sp_sum_oben[colhp] != 0:
                bewertung[1] += 1

    # R idx2: kühl-trocken-Trennung auch nach Austausch berücksichtigt
    kuehlpaletten = tabelle_[tabelle_['t_i'] > 0].reset_index(inplace=False, drop=True)

    for tpal in range(kuehlpaletten.shape[0]):  # für jede Kühlpalette einzeln

        try:
            col_tpal = int(list(lkwplan_.columns[lkwplan_.isin([kuehlpaletten.loc[tpal, 'i']]).any()])[0])
        except:
            bewertung[2] = 100  # 100 als Kennzeichen, dass Kühlpalette nicht mehr eingeplant werden konnte
        else:
            # alle n in der nächsthöheren Reihe müssen kleiner sein ODER gleich wenn t auch 1 ist
            tabelle_vgl = tabelle_.set_index('i', inplace=False, drop=False)
            if col_tpal <= 10:
                for jedes in lkwplan_.loc[:, str(col_tpal + 1)]:

                    if jedes != 'x' and jedes != 'o':

                        if tabelle_vgl.loc[jedes, 'n_i'] > tabelle_vgl.loc[kuehlpaletten.loc[tpal, 'i'], 'n_i']:
                            bewertung[2] = 2  # das kann eigentlich nicht passieren; abh. von Verb.verf.

                        elif tabelle_vgl.loc[jedes, 'n_i'] == tabelle_vgl.loc[kuehlpaletten.loc[tpal, 'i'], 'n_i']:
                            if tabelle_vgl.loc[jedes, 't_i'] < 1:
                                bewertung[2] = 1

    # R idx3: Anz zusätzl benötigter Ladungssicherung durch ganz freie Reihen mittendrin

    # zähle Typwechsel hoch, wenn man von Paletten auf ganz leere Reihe wechselt oder umgekehrt
    # Typwechsel entspricht damit Anz. benötigter Ladungssicherung
    # rechne zum Schluss -1, da ein Wechsel i. O. (entspricht der Ideallösung)

    # entscheidende Typwechsel nur bei folgender Palettenanzahl möglich:
    if anz_pal <= 27 or (anz_pal >= 34 and anz_pal <= 60):

        # bei mehr als 33 Paletten zählen wir Typwechsel nur oben, ansonsten nur unten
        if anz_pal > 33:
            rows = [3, 4, 5]
        else:
            rows = [0, 1, 2]

        typwechsel = 0
        col_idx = 1
        while col_idx < lkwplan_.shape[1]:

            if (lkwplan_.iloc[rows, col_idx - 1] == 'o').any():
                if col_idx < 10:
                    typwechsel += 1
                break  # Restreihe gefunden

            try:
                (lkwplan_.iloc[rows, col_idx - 1] >= 0).all()
            except:
                if (lkwplan_.iloc[rows, col_idx - 1] == 'x').all():
                    if (lkwplan_.iloc[rows, col_idx] == 'x').all():
                        pass
                    else:
                        typwechsel += 1

                else:  # wenn nicht nur Zahlen oder nicht nur x, dann kann man aufhören, da Restreihe gefunden
                    # braucht kein if (lkwplan_.iloc[3:,col_idx-1]=='o').any() or (lkwplan_.iloc[3:,col_idx-1]=='x').any(): ...
                    if col_idx < 10:
                        typwechsel += 1
                    col_idx = 11
                    break

            else:
                try:
                    (lkwplan_.iloc[rows, col_idx] >= 0).all()
                except:
                    if (lkwplan_.iloc[rows, col_idx] == 'x').all():
                        typwechsel += 1
                    else:
                        if col_idx < 10:
                            typwechsel += 1
                        col_idx = 11
                        break  # Restreihe gefunden

            col_idx += 1

        if typwechsel - 1 == 0 and (lkwplan_.iloc[rows, 0] == 'x').any():
            typwechsel = 1.0001

        bewertung[3] = typwechsel - 1

    return bewertung


# In[ ]:


# In[13]:


# FÜR JEDE TOUR EINZELN:
"""tabelle=pd.DataFrame({'i': np.arange(46), 'n_i': tour_nr_04587['n_i'], 'h_i': tour_nr_04587['h_i'],
                      'm_i': tour_nr_04587['m_i'], 't_i': tour_nr_04587['t_i']})"""

tour_idx = 4
tabelle = pd.DataFrame({'i': np.arange(len(paletten_je_tour[tour_idx]['n_i'])),
                        'n_i': paletten_je_tour[tour_idx]['n_i'],
                        'h_i': paletten_je_tour[tour_idx]['h_i'],
                        'm_i': paletten_je_tour[tour_idx]['m_i'],
                        't_i': paletten_je_tour[tour_idx]['t_i']})

# In[14]:


sum(tabelle['m_i'])

# In[15]:


# Annahmen vorab
# benötigte Werte: (hier am Bsp. Zugmaschine MAN + Dry Liner KRONE)
radstand_trailer = 7.63
radstand_tractor = 3.6
sattelvorm_tractor = 0.575  # Kingpin 575 mm vor Hinterachse
abst_kp_stw_trailer = 1.65
m_tractor = 7943
m_trailer = 7890
massenschw_vorHA_tractor = 2.538
massenschw_zuStw_trailer = 7.249  # Abstand zur Stirnwand (hier leicht gerundet, s. Excel)
m_HA_max_ges = 11500  # gesetzliche Vorgabe
m_t_max_ges = 24000  # gesetzliche Vorgabe

last_kp_durch_m_trailer = (1 - (massenschw_zuStw_trailer - abst_kp_stw_trailer) / radstand_trailer) * m_trailer
last_t_durch_m_trailer = (massenschw_zuStw_trailer - abst_kp_stw_trailer) / radstand_trailer * m_trailer
last_HA_durch_m_tractor = (1 - massenschw_vorHA_tractor / radstand_tractor) * m_tractor
m_kp_max_vor_m_trailer = (m_HA_max_ges - last_HA_durch_m_tractor) / (1 - sattelvorm_tractor / radstand_tractor)

m_kp_max = m_kp_max_vor_m_trailer - last_kp_durch_m_trailer
m_t_max = m_t_max_ges - last_t_durch_m_trailer

# tourenabhängige Werte
m_lad = tabelle['m_i'].sum()

# Untergrenze:
lsp_u = radstand_trailer * (1 - m_kp_max / m_lad) + abst_kp_stw_trailer

# Obergrenze:    -> Annahme: mindestens 25% des aktuellen Gesamtgewichts auf HA der Zugmaschine
anteil_mKP_HA = 1 - sattelvorm_tractor / radstand_tractor  # KP-Last zu ...% auf der HA der Zugmaschine:
lsp_o = min(m_t_max / m_lad * radstand_trailer + abst_kp_stw_trailer, abst_kp_stw_trailer + radstand_trailer / m_lad * (
            0.7025 * (m_lad + m_trailer) - 0.2975 * m_tractor + 1 / anteil_mKP_HA * last_HA_durch_m_tractor))

print(f'Untergrenze (in m ab Stirnwand): {lsp_u:.3f} \nObergrenze (in m ab Stirnwand): {lsp_o:.3f}')

# In[16]:


lkwplan = pd.DataFrame({str(reihe_k): ['o' for o in range(6)] for reihe_k in range(1, 12)})
lkwplan

# In[17]:


varianten = {'A': {'by': ['n_i', 't_i', 'm_i'],
                   'ascending': [False, True, False]},
             'B': {'by': ['n_i', 't_i', 'm_i'],
                   'ascending': [False, True, True]},
             'C': {'by': ['n_i', 't_i', 'h_i'],
                   'ascending': [False, True, False]},
             'D': {'by': ['n_i', 't_i', 'h_i'],
                   'ascending': [False, True, True]}}

plaene = []

# In[18]:


anz_pal = max(tabelle['i']) + 1  # da Tabelle nullbasiert
oben = max(anz_pal - 33, 0)

for var in varianten:
    # zu verbessern: 'x'-Sperrung & wissen, ob 1 oder 2 Pläne pro Variante muss man nicht für jede Variante wieder prüfen
    # nur von anz_pal abhängig; vorher definieren spart ggf. Rechenaufwand
    tabelle.sort_values(by=varianten[var]['by'], ascending=varianten[var]['ascending'], inplace=True)
    tabelle.reset_index(inplace=True, drop=True)

    for planoption in range(1, 4):

        plaene.append([pd.DataFrame(lkwplan.copy(deep=True)), None])

        zweioptionen = False
        if anz_pal <= 33:
            plaene[-1][0].iloc[3:, :] = 'x'

            if anz_pal <= 30:  # bei weniger als 31 gibt es zwei Möglichkeiten für ganz freie Reihen
                plaene.append([pd.DataFrame(plaene[-1][0].copy(deep=True)), None])
                zweioptionen = True

                for frei in range(0, 11 - math.ceil(anz_pal / 3)):
                    plaene[-1][0].iloc[3:, frei] = 'x'  # hier ist -1 dann der neu hinzugefügte

        elif anz_pal <= 63:  # auch hier gibt es zwei Möglichkeiten für ganz freie Reihen
            plaene.append([pd.DataFrame(plaene[-1][0].copy(deep=True)), None])
            zweioptionen = True

            for frei in range(0, 11 - math.ceil(oben / 3)):
                plaene[-1][0].iloc[3:, frei] = 'x'  # hier ist -1 dann der neu hinzugefügte

        # bei 64 oder mehr mache nichts, weil Restreihe an der Tür ist & alle anderen Reihen voll sind

        # dann kann man beide Versionen füllen und falls HPal kommt, ganze Reihen sperren
        # trotzdem weiter befüllen, aber Strafkosten vergeben, damit ideale Lösung (wenn es eine gibt) besser ist

        plan_fuellen(tabelle, plaene[-1][0], anz_pal, oben, planoption)
        plaene[-1][1] = plan_bewertung(tabelle, plaene[-1][0])

        if zweioptionen:
            plan_fuellen(tabelle, plaene[-2][0], anz_pal, oben, planoption)
            plaene[-2][1] = plan_bewertung(tabelle, plaene[-2][0])

# In[19]:


plaene_zweitewahl = []

# Duplikate entfernen
pl1 = 0
while pl1 < len(plaene):
    pl2 = pl1 + 1
    while pl2 < len(plaene):
        if (plaene[pl1][0] == plaene[pl2][0]).all().all():
            plaene.pop(pl2)
        else:
            pl2 += 1
    pl1 += 1

# Pläne in Erst- und Zweitwahl aufteilen
pl = 0
while pl < len(plaene):
    if sum(plaene[pl][1][0:6]) > 0.0001:
        plaene_zweitewahl.append(plaene.pop(pl))
    else:
        pl += 1


# In[20]:


def sort_erstewahl_a(e):
    return e[1][3]


def sort_erstewahl_b(e):
    return sum(e[1])


plaene.sort(key=sort_erstewahl_a)
plaene.sort(key=sort_erstewahl_b)

plaene


# In[21]:


# R idx0: Anzahl nicht eingeplanter Paletten (0 = am besten)
# R idx1: alle Hochpaletten haben einen zulässigen Platz (stehen unten & obere Reihe komplett leer)
# .> +0.01, wenn HPal nicht unten steht; +1, wenn über einer HPal nicht frei ist
# .> durch diese Werte könnte man hinterher auswerten, was das Problem ist - brauchen wir das?
# R idx2: kühl-trocken-Trennung auch nach Austausch berücksichtigt
# .> eigener idx sinnvoll, da dies ggf später vernachlässigt werden darf
# R idx3: Anz zusätzl benötigter Ladungssicherung durch ganz freie Reihen mittendrin
# .> ideal wäre NUR vorne oder NUR hinten ganze Reihen frei - 1x Ladungssicherung ist also ideal
##### bisher nur oben möglich, falls HP unten -> andere Möglichkeiten ggf. noch ergänzen (?)

# G idx4: Ladebalkenbelastung eingehalten (max. 2 t pro 3er-Reihe oben)
# G idx5: Achslastvorgaben einhalten!
# G idx6: Gewichtsdifferenz


# In[22]:


def sort_zweitewahl(e):
    return sum(e[1])


plaene_zweitewahl.sort(key=sort_zweitewahl)

# In[23]:


plaene_zweitewahl

# In[ ]:


# In[24]:


# TODO:
# Verbesserungsverfahren zunächst nur für plaene (falls Einträge enthalten)
# wenn das schon zu sehr gutem Ergebnis führt (Vorgaben ausstehend): aufhören
# ansonsten auch noch mit plaene_zweitewahl beschäftigen


# In[25]:


if len(plaene) > 0:
    print(f'Beste gefundene Lösung:\n\n{plaene[0][0]}\n\nGewichtsdifferenz:{plaene[0][1][-1]: .2f} kg')
else:
    print('Noch keine optimale Lösung gefunden.')

# In[26]:


print(f'bisherige Dauer:{time.time() - starttime: .3f} s')

