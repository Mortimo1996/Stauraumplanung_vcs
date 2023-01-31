#!/usr/bin/env python
# coding: utf-8

# In[1]:


# offene Punkte:
# bisher nur Reihensperrungen oben möglich, wenn HP unten -> andere Möglichkeiten zur Achslastverbesserung noch ergänzen
# Verbesserungsverfahren: durch zufällige Tausche könnten ggf. mehr Paletten in den LKW passen

# ...


# In[ ]:


# In[2]:


import numpy as np
import pandas as pd
import math
import time
from random import randint

# In[3]:


starttime = time.time()

# In[4]:


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

# In[5]:


blkblo_blktnt_blktre_blkk02 = {}
for z in blk_vor:
    if z[14:16] == 'LK':
        # dictionary füllen mit Blockauftragsnr.: [Tournr., Auslieferungsreihenfolge, Kommission/Klima]
        # blkblo_blktnt_blktre_blkk02[z[16:23]]=[z[426:431],z[431:436],z[281:282]]
        # dictionary füllen mit Blockauftragsnr.: [Auslieferungsreihenfolge, Kommission/Klima]
        blkblo_blktnt_blktre_blkk02[z[16:23]] = [z[431:436], z[281:282]]

# blkblo_blktnt_blktre_blkk02


# In[40]:


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
# touren2


# In[7]:


paletten_je_tour = {}
idx = 0

for z_tar in tar_vor:
    paletten_je_tour[idx] = {'n_i': [], 'h_i': [], 'm_i': [], 't_i': [], 'zeile': []}
    zzz = 0
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

            paletten_je_tour[idx]['zeile'].append(zzz)

        zzz += 1
    idx += 1

# paletten_je_tour


# In[ ]:


# In[8]:


"""
______________________________________________________________________________

bis hier war nur Vorarbeit zum Einlesen der Daten (-> überarbeitet Maarten)
als Nächstes folgen die Funktionsdefinitionen
______________________________________________________________________________
"""


# In[ ]:


# In[9]:


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
            restr = False

            if oben == 0:
                for row_c in range(3, 6):
                    for col_c in range(col_d, 11):
                        if lkwplan.iloc[row_c, col_c] == 'o':
                            lkwplan.iloc[row_c, col_c] = 'x'

            if len(row_opt) == 0:
                col_d += 1

                if oben == 2 and anz_pal % 3 == 2:  # Optionen für Restreihe
                    restr = True
                    if randint(0, 1) == 0:
                        row_opt = [0, 1, 2, 4, 5]
                    else:
                        row_opt = [0, 1, 2, 3, 4]
                elif oben == 1 and anz_pal % 3 == 1:  # Optionen für Restreihe
                    restr = True
                    row_opt = [0, 1, 2, 3, 5]
                else:  # alle anderen außer der Restreihe
                    row_opt = [0, 1, 2, 3, 4, 5]

            if col_d >= lkwplan.shape[1]:
                # print('Keine Zuweisung ab Palette {} (d.h. ab Reihenindex {}) möglich.'.format(tabelle.loc[idx_pal,'i'],idx_pal))
                break

            nr = randint(0, len(row_opt) - 1)  # randint(0,5) zieht eine zufällige Zahl von 0 bis 5 (inkl. 0 und 5)

            if (len(row_opt) == 6 or restr) and tabelle.loc[idx_pal:idx_pal + 6, 'h_i'].sum() >= 1:
                lkwplan.iloc[3:, col_d] = 'x'

            if lkwplan.iloc[row_opt[nr], col_d] != 'x':
                lkwplan.iloc[row_opt[nr], col_d] = tabelle.loc[idx_pal, 'i']
                idx_pal += 1
                if row_opt[nr] >= 3:
                    oben -= 1

            row_opt.remove(row_opt[nr])


# In[10]:


def gewichtsplan(tabelle_g,
                 lkwplan_g):  # wird von Funktion "gewichte_bestimmen" aufgerufen & später nochmal bei Verbesserung

    # Indizes von 'tabelle' ändern, damit wir einfacher auf m_i zugreifen können
    tabelle_2 = tabelle_g.set_index('i', inplace=False, drop=False)  # erzeugt eine Kopie

    # neue Tabelle bzw. Beladungsplan mit Gewichtsangaben erstellen
    lkwplan_gew = pd.DataFrame(lkwplan_g.copy(deep=True))

    for col in range(0, lkwplan_gew.shape[1]):
        for row in range(0, lkwplan_gew.shape[0]):
            if type(lkwplan_gew.iloc[row, col]) != str:
                lkwplan_gew.iloc[row, col] = tabelle_2.loc[lkwplan_g.iloc[row, col], 'm_i']
            else:
                lkwplan_gew.iloc[
                    row, col] = 0  # Alternative hierzu wäre z. B. lkwplan_gewichte.replace('x',0,inplace=True)

    return lkwplan_gew


def gewichte_bestimmen(tabelle_gb, lkwplan_gb):  # wird von Funktion "plan_bewertung" aufgerufen

    lkwplan_gewichte = gewichtsplan(tabelle_gb, lkwplan_gb)

    spaltensum_oben = lkwplan_gewichte.loc[3:].sum(axis=0)
    spaltensummen = lkwplan_gewichte.sum(axis=0)
    zeilensummen = lkwplan_gewichte.sum(axis=1)

    return zeilensummen, spaltensummen, spaltensum_oben


# In[11]:


def plan_bewertung(tabelle_, lkwplan_):
    bewertung = [0 for i in range(7)]  # erzeugt Liste mit 7 Nullen, 0 bedeutet "alles gut"

    # ---kein idx, da im Startverf.: Restreihe ist "an der Tür"
    # ---kein idx, da in Verbesserung: Restreihe_einzeln am Rand, zwei mittig&Rand
    # ---kein idx, da im Startverf.: oben stehen genau Q Paletten
    # ---kein idx, da Start&Verbesserung berücksichtigen: Auslieferungsreihenfolge

    # R idx0: Anzahl nicht eingeplanter Paletten (0 = am besten)
    # R idx1: alle Hochpaletten haben einen zulässigen Platz (stehen unten & obere Reihe komplett leer)
    # +0.01, wenn HPal nicht mehr eingeplant werden konnte
    # +1, wenn über einer HPal nicht frei ist oder HPal selbst nicht unten steht
    # R idx2: kühl-trocken-Trennung auch nach Austausch berücksichtigt
    # eigener idx sinnvoll, da dies ggf später vernachlässigt werden darf
    # +0.01, wenn Palette nicht mehr eingeplant werden konnte
    # +1 für jede t=1 Palette, wenn Regel nicht eingehalten wurde
    # R idx3: Anz zusätzl benötigter Ladungssicherung durch ganz freie Reihen mittendrin
    # ideal wäre NUR vorne oder NUR hinten ganze Reihen frei - 1x Ladungssicherung ist also ideal
    # für NUR vorne ganze Reihen frei trotzdem noch +0.0001 ergänzt, da dann NUR hinten noch bevorzugt werden kann
    ##### bisher nur Sperrungen oben möglich, wenn HP unten -> andere Möglichkeiten ggf. zur Achslastverbesserung noch ergänzen

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
            bewertung[4] += 1

    # G idx5: Achslastvorgaben einhalten!
    zaehler = 0
    for l in range(0, 11):
        zaehler += (0.6 + 1.2 * l) * sp_sum[l]
    ladungsschw = zaehler / sum(sp_sum)

    if lsp_u > ladungsschw or lsp_o < ladungsschw:
        bewertung[5] = 10  # Ladungsschwerpunkt außerhalb des zulässigen Bereichs, Achslasten nicht eingehalten

    # G idx6: Gewichtsdifferenz
    """gew_rechts=z_sum[0]+z_sum[3]
    gew_links=z_sum[2]+z_sum[5]
    bewertung[6]=abs(gew_rechts-gew_links)  """

    # Gewichtsdifferenz NEU: in %
    # gew_rechts=z_sum[0]+z_sum[3]
    gew_mitte = z_sum[1] + z_sum[4]
    gew_links = z_sum[2] + z_sum[5]

    prozent_links = (gew_links + gew_mitte / 2) / sum(z_sum) * 100
    bewertung[6] = abs(50 - prozent_links) * 2

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
            bewertung[1] += 0.01  # als Kennzeichen, dass HPal nicht mehr eingeplant werden konnte
        else:
            if rowhp >= 3:  # falls eine HPal oben steht
                bewertung[1] += 1

            elif sp_sum_oben[colhp] != 0:
                # Spaltensumme der Gewichte in Zeilen [3:] sollte == 0 sein (= oben frei)
                # wäre auch immer verletzt, wenn HPal selbst oben steht
                # ...dafür rechnen wir aber bereits +1, deshalb hier elif: greift nur, wenn HPal unten steht
                bewertung[1] += 1

    # R idx2: kühl-trocken-Trennung auch nach Austausch berücksichtigt
    kuehlpaletten = tabelle_[tabelle_['t_i'] > 0].reset_index(inplace=False, drop=True)

    for tpal in range(kuehlpaletten.shape[0]):  # für jede Kühlpalette einzeln

        try:
            col_tpal = int(list(lkwplan_.columns[lkwplan_.isin([kuehlpaletten.loc[tpal, 'i']]).any()])[0])
        except:
            bewertung[2] += 0.01  # als Kennzeichen, dass Kühlpalette nicht mehr eingeplant werden konnte
        else:
            # alle n in der nächsthöheren Reihe müssen kleiner sein ODER gleich wenn t auch 1 ist
            tabelle_vgl = tabelle_.set_index('i', inplace=False, drop=False)
            if col_tpal <= 10:
                for jedes in lkwplan_.loc[:, str(col_tpal + 1)]:

                    if jedes != 'x' and jedes != 'o':

                        if tabelle_vgl.loc[jedes, 'n_i'] > tabelle_vgl.loc[kuehlpaletten.loc[tpal, 'i'], 'n_i']:
                            bewertung[2] += 1

                        elif tabelle_vgl.loc[jedes, 'n_i'] == tabelle_vgl.loc[kuehlpaletten.loc[tpal, 'i'], 'n_i']:
                            if tabelle_vgl.loc[jedes, 't_i'] < 1:
                                bewertung[2] += 1

    # R idx3: Anz zusätzl benötigter Ladungssicherung durch ganz freie Reihen mittendrin

    # zähle Typwechsel hoch, wenn man von Paletten auf ganz leere Reihe wechselt oder umgekehrt
    # Typwechsel entspricht damit Anz. benötigter Ladungssicherung
    # rechne zum Schluss -1, da ein Wechsel i. O. (entspricht der Ideallösung)

    # entscheidende Typwechsel nur bei folgender Palettenanzahl möglich:
    if anz_pal - bewertung[0] <= 27 or (anz_pal - bewertung[0] >= 34 and anz_pal - bewertung[0] <= 60):

        # bei mehr als 33 Paletten zählen wir Typwechsel nur oben, ansonsten nur unten
        if anz_pal - bewertung[0] > 33:
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


# In[12]:


def sort_erstewahl_a(e):
    return e[1][3]  # sortiert Pläne mit freien Reihen an der Stirnwand weiter nach hinten


def sort_erstewahl_b(e):
    return e[1][-1]  # Gewichtsdifferenz


def plaene_erstewahl_sort(plaene_liste):
    plaene_liste.sort(key=sort_erstewahl_a)
    plaene_liste.sort(key=sort_erstewahl_b)
    return plaene_liste


# In[13]:


def sort_zweitewahl_a(e):
    return e[1][-1]  # Gewichtsdifferenz


def sort_zweitewahl_b(e):
    return e[1][4]  # Ladebalkenverletzung nach vorne holen, damit diese bei Summe in c weiter oben stehen


def sort_zweitewahl_c(e):
    return sum(e[1][:6])  # Summe der anderen Bewertungsindizes exkl. Gewichtsdifferenz


def plaene_zweitewahl_sort(plaene_liste):
    plaene_liste.sort(key=sort_zweitewahl_a)
    plaene_liste.sort(reverse=True, key=sort_zweitewahl_b)
    plaene_liste.sort(key=sort_zweitewahl_c)
    return plaene_liste


# In[14]:


def sort_3_a(e):
    return e[1][-1]  # Gewichtsdifferenz


def sort_3_b(e):
    return e[1][0]  # Anz. übriger Paletten


def sort_3_c(e):
    return sum(e[1][1:6])  # Summe der anderen Bewertungsindizes exkl. Gewichtsdifferenz


def plaene_pal_ueber_sort(plaene_liste):
    plaene_liste.sort(key=sort_3_a)
    plaene_liste.sort(key=sort_3_b)
    plaene_liste.sort(key=sort_3_c)
    return plaene_liste


# In[15]:


def gewichte_optimieren(tabelle_, lkwplan_, bewertung_):
    opt_gewicht = bewertung_[-1]
    plan_gewichte = gewichtsplan(tabelle_, lkwplan_)

    z_sum = plan_gewichte.sum(axis=1)
    if z_sum[0] + z_sum[3] > z_sum[2] + z_sum[5]:  # if rechts>links
        w = 1
    else:
        w = -1

    # Tauschpotentiale berechnen: je höher der Wert, desto "besser" (kann ggf. zu viel sein)
    plan_tauschpotential = pd.DataFrame({str(reihe_k): [0 for o in range(6)] for reihe_k in range(1, 12)})
    # in plan_tauschpotential berechne in Zeile...
    # 0 - Differenz 0 u 1
    # 1 - Differenz 0 u 2
    # 2 - Differenz 1 u 2
    # 3 - Differenz 3 u 4
    # 4 - Differenz 3 u 5
    # 5 - Differenz 4 u 5

    if anz_pal > 33:
        rows_rest = [3, 4, 5]
        rows_total = [0, 1, 2, 3, 4, 5]
    else:
        rows_rest = [0, 1, 2]
        rows_total = [0, 1, 2]

    for col in range(0, plan_tauschpotential.shape[1]):
        if (plan_tauschpotential.iloc[rows_rest, col] == 0).all():
            rows_potential = [r for r in rows_total if r not in rows_rest]
        else:
            if (plan_tauschpotential.iloc[rows_rest, col] == 0).any():
                rows_potential = rows_total
                if anz_pal % 3 == 1:  # dann 0 und 2 bzw. 3 und 5 sperren (abhängig von Ebene der Restreihe)
                    del rows_potential[-3]
                    del rows_potential[-1]
                elif anz_pal % 3 == 2:
                    if (plan_tauschpotential.iloc[rows_rest[1:], col] == 0).any():
                        del rows_potential[-1]
                    else:
                        del rows_potential[-3]

        for row in rows_potential:
            if row == 0 or row == 3:
                plan_tauschpotential.iloc[row, col] = (plan_gewichte.iloc[row, col] - plan_gewichte.iloc[
                    row + 1, col]) * w
            elif row == 1 or row == 4:
                plan_tauschpotential.iloc[row, col] = (plan_gewichte.iloc[row - 1, col] - plan_gewichte.iloc[
                    row + 1, col]) * w
            elif row == 2 or row == 5:
                plan_tauschpotential.iloc[row, col] = (plan_gewichte.iloc[row - 1, col] - plan_gewichte.iloc[
                    row, col]) * w

    tester = plan_tauschpotential

    diff = bewertung_[-1] / 100 * sum(tabelle['m_i'])
    best_value = 0
    best_row = None
    best_col_str = None

    # finde die Reihe mit dem Wert am nächsten zur aktuellen Gewichtsdifferenz (um möglichst optimal wegzutauschen)
    for col in tester.columns:
        v1 = pd.DataFrame(tester.loc[(tester[col] - diff).abs().argsort()[:1]].copy(deep=True))
        if v1.loc[v1.index[0], col] != 0 and abs(diff - v1.loc[v1.index[0], col]) < abs(diff - best_value):
            best_row = v1.index[0]
            best_col_str = col
            best_value = v1.loc[v1.index[0], col]

    # print(tester,'\n\n')

    if best_row != None and best_col_str != None:
        # print(tester.loc[best_row,best_col_str])
        # print(f'row: {best_row}, column: {best_col_str}')

        if best_row == 0 or best_row == 3:
            speicher = lkwplan_.loc[best_row, best_col_str]
            lkwplan_.loc[best_row, best_col_str] = lkwplan_.loc[best_row + 1, best_col_str]
            lkwplan_.loc[best_row + 1, best_col_str] = speicher
        elif best_row == 1 or best_row == 4:
            speicher = lkwplan_.loc[best_row - 1, best_col_str]
            lkwplan_.loc[best_row - 1, best_col_str] = lkwplan_.loc[best_row + 1, best_col_str]
            lkwplan_.loc[best_row + 1, best_col_str] = speicher
        elif best_row == 2 or best_row == 5:
            speicher = lkwplan_.loc[best_row, best_col_str]
            lkwplan_.loc[best_row, best_col_str] = lkwplan_.loc[best_row - 1, best_col_str]
            lkwplan_.loc[best_row - 1, best_col_str] = speicher

    # in plan_tauschpotential sagt uns Zeile...
    # 0 - Differenz 0 u 1
    # 1 - Differenz 0 u 2
    # 2 - Differenz 1 u 2
    # 3 - Differenz 3 u 4
    # 4 - Differenz 3 u 5
    # 5 - Differenz 4 u 5

    # aus Meeting mit Herrn Fünfer (13.01.2023):
    # Die schwerere Seite sollte bevorzugt links (=Zeilen 2+5) sein.
    # Grund: Wenn der LKW rechts von der Straße abkommt, kann der Fahrer es so leichter korrigieren.
    z_sum_new = lkwplan_.sum(axis=1)
    if (z_sum_new[0] + z_sum_new[3]) > (z_sum_new[2] + z_sum_new[5]):  # if rechts>links
        speicher_u_r = pd.DataFrame(lkwplan_.iloc[0, :].copy(deep=True))  # unten: rechte Seite zwischenspeichern
        speicher_o_r = pd.DataFrame(lkwplan_.iloc[3, :].copy(deep=True))  # oben: rechte Seite zwischenspeichern

        lkwplan.iloc[0, :] = pd.DataFrame(lkwplan_.iloc[2, :].copy(deep=True))  # unten: links nach rechts stellen
        lkwplan.iloc[3, :] = pd.DataFrame(lkwplan_.iloc[5, :].copy(deep=True))  # oben: links nach rechts stellen

        lkwplan.iloc[2, :] = pd.DataFrame(speicher_u_r.iloc[0, :].copy(deep=True))  # unten: rechts nach links stellen
        lkwplan.iloc[5, :] = pd.DataFrame(speicher_o_r.iloc[0, :].copy(deep=True))  # oben: rechts nach links stellen

    return lkwplan_


# In[16]:


def plaene_erstewahl_optimieren(tabelle_o, plaene_o):
    for pl in range(0, len(plaene_o)):
        plaene_o[pl][0] = gewichte_optimieren(tabelle_o, plaene_o[pl][0], plaene_o[pl][1])
        plaene_o[pl][1] = plan_bewertung(tabelle_o, plaene_o[pl][0])

    plaene_o = plaene_erstewahl_sort(plaene_o)
    return plaene_o


# In[17]:


def ladebalken_ausgleich(tabelle_, lkwplan_):
    lkwplan_gewichte = gewichtsplan(tabelle_, lkwplan_)
    sp_sum_oben = lkwplan_gewichte.loc[3:].sum(axis=0)
    sp_sum = lkwplan_gewichte.sum(axis=0)

    for idx in range(0, len(sp_sum_oben)):
        if sp_sum_oben[idx] > 2000:
            if sp_sum[idx] - sp_sum_oben[idx] <= 2000:  # dann tausche oben und unten komplett
                speicher = pd.DataFrame(lkwplan_.iloc[:3, idx].copy(deep=True))
                lkwplan_.iloc[:3, idx] = pd.DataFrame(lkwplan_.iloc[3:, idx].copy(deep=True)).iloc[:, 0]
                lkwplan_.iloc[3:, idx] = pd.DataFrame(speicher.copy(deep=True)).iloc[:, 0]
            else:
                for a in [1, 2]:  # tausche schwerste oben mit leichtester unten (2x)
                    row_min = lkwplan_gewichte.iloc[:3, idx].idxmin()
                    row_max = lkwplan_gewichte.iloc[3:, idx].idxmax()
                    if row_max > row_min:
                        speicher = pd.DataFrame(lkwplan_.iloc[row_min, idx].copy(deep=True))
                        lkwplan_.iloc[row_min, idx] = pd.DataFrame(lkwplan_.iloc[row_max, idx].copy(deep=True)).iloc[:,
                                                      0]
                        lkwplan_.iloc[row_max, idx] = pd.DataFrame(speicher.copy(deep=True)).iloc[:, 0]

    return lkwplan_


# In[18]:


def tauschpartner_andere_reihe(lkwplan_, lkwplan_n_werte, tabelle_2, pal_row_idx, pal_col_idx, col_idx_neu, n_wert):
    tauschpartner = []  # schreibe eine Liste mit potenziellen Tauschpartnern als [row,col]-ELemente
    fuer_dreiertausch = []
    fuer_drt_row_gleiches_n = []

    h_wert = tabelle_2.loc[lkwplan_.iloc[pal_row_idx, pal_col_idx], 'h_i']
    t_wert = tabelle_2.loc[lkwplan_.iloc[pal_row_idx, pal_col_idx], 't_i']

    if ((lkwplan_n_werte.iloc[3:, pal_col_idx] == 'x').all() == (lkwplan_n_werte.iloc[3:, col_idx_neu] == 'x').all()):
        # h_wert stellt hier kein Problem dar
        if (lkwplan_n_werte.iloc[:, col_idx_neu] == n_wert).any():  # es muss mind. ein gleiches n geben
            for row_n in range(0, 6):
                if lkwplan_n_werte.iloc[row_n, col_idx_neu] == n_wert:
                    tauschpartner.append([row_n, col_idx_neu])
                    fuer_drt_row_gleiches_n.append(row_n)
                elif lkwplan_n_werte.iloc[row_n, col_idx_neu] != 'x':
                    fuer_dreiertausch.append(row_n)
                    # dann muss ein Dreiertausch mit einer anderen Paletten desselben n-Werts passieren

            if len(fuer_drt_row_gleiches_n) > 0 and len(fuer_dreiertausch) > 0:
                for B in fuer_drt_row_gleiches_n:
                    for C in fuer_dreiertausch:
                        tauschpartner.append([[B, col_idx_neu], [C, col_idx_neu]])

    elif h_wert == 0:
        # wenn h_wert 0 ist, könnte es problematisch werden, wenn h_wert des Tauschpartners 1 ist
        if (lkwplan_n_werte.iloc[:, col_idx_neu] == n_wert).any():  # es muss mind. ein gleiches n geben
            for row_n in range(0, 6):
                if lkwplan_n_werte.iloc[row_n, col_idx_neu] != 'x':
                    h0_true = bool(tabelle_2.loc[lkwplan_.iloc[row_n, col_idx_neu], 'h_i'] == 0)
                else:
                    continue

                if lkwplan_n_werte.iloc[row_n, col_idx_neu] == n_wert and h0_true:
                    tauschpartner.append([row_n, col_idx_neu])
                    fuer_drt_row_gleiches_n.append(row_n)
                elif lkwplan_n_werte.iloc[row_n, col_idx_neu] != 'x' and h0_true:
                    fuer_dreiertausch.append(row_n)
                    # dann muss ein Dreiertausch mit einer anderen Paletten desselben n-Werts passieren

            if len(fuer_drt_row_gleiches_n) > 0 and len(fuer_dreiertausch) > 0:
                for B in fuer_drt_row_gleiches_n:
                    for C in fuer_dreiertausch:
                        tauschpartner.append([[B, col_idx_neu], [C, col_idx_neu]])

    return tauschpartner


# In[19]:


def planverb_zufaellig(tabelle_, lkwplan_, lkwplan_bew, max_tausche):
    # Funktion für zufällige Palettentausche mit der gleichen, vorherigen oder nächsthöheren Reihe
    # Elemente mit Reihe davor und dahinter vergleichen macht mehr Sinn als mit n+-1
    # Grund: könnte ggf. Palette A (n=3) in Reihe 10 mit B (n=5) in Reihe 9 tauschen (und nicht z. B. nur mit n=4 in Reihe 9)

    # Indizes von 'tabelle_' ändern, damit wir einfacher auf n_i zugreifen können
    tabelle_2 = tabelle_.set_index('i', inplace=False, drop=False)  # erzeugt eine Kopie

    # alten Plan kopieren, um später auf Verbesserung überprüfen zu können
    lkwplan_v = pd.DataFrame(lkwplan_.copy(deep=True))

    # neue Tabelle bzw. Beladungsplan mit Nr. Auslieferungsreihenfolge erstellen
    lkwplan_n_werte = pd.DataFrame(lkwplan_.copy(deep=True))

    for col in range(0, lkwplan_n_werte.shape[1]):
        for row in range(0, lkwplan_n_werte.shape[0]):
            if type(lkwplan_n_werte.iloc[row, col]) != str:
                lkwplan_n_werte.iloc[row, col] = tabelle_2.loc[lkwplan_v.iloc[row, col], 'n_i']
            else:
                lkwplan_n_werte.iloc[row, col] = 'x'  # setze zur Vereinfachung auch mögliche 'o' auf 'x'

    tauschnr = 0
    while tauschnr < max_tausche:
        # zufällige Palette auswählen
        pal_row_idx = randint(0, lkwplan_v.shape[
            0] - 1)  # -1, da wir den Index nutzen und randint(0,2) von 0 bis einschl. 2 zieht
        pal_col_idx = randint(0, lkwplan_v.shape[1] - 1)

        n_wert = lkwplan_n_werte.iloc[pal_row_idx, pal_col_idx]

        if n_wert != 'x':

            tauschpartner = []

            # alle Elemente in gleicher Reihe gehen immer
            for row_n in range(0, 6):
                if row_n != pal_row_idx:
                    if lkwplan_n_werte.iloc[row_n, pal_col_idx] != 'x':
                        tauschpartner.append([row_n, pal_col_idx])

                        # bei den anderen Reihen müssen h_wert und t_wert berücksichtigt werden
            # wir berücksichtigen nur h, weil t ggf. vernachlässigt werden darf

            # Tausch mit vorheriger Reihe
            if pal_col_idx > 0:
                col_idx_neu = pal_col_idx - 1
                liste = tauschpartner_andere_reihe(lkwplan_v, lkwplan_n_werte, tabelle_2, pal_row_idx, pal_col_idx,
                                                   col_idx_neu, n_wert)
                tauschpartner.extend(liste)

            # Tausch mit nächsthöherer Reihe
            if pal_col_idx < 10:
                col_idx_neu = pal_col_idx + 1
                liste = tauschpartner_andere_reihe(lkwplan_v, lkwplan_n_werte, tabelle_2, pal_row_idx, pal_col_idx,
                                                   col_idx_neu, n_wert)
                tauschpartner.extend(liste)

            # zufälligen Tauschpartner bestimmen
            randidx = randint(0, len(tauschpartner) - 1)

            if type(tauschpartner[randidx][0]) == int:
                speicher = lkwplan_v.iloc[pal_row_idx, pal_col_idx]
                lkwplan_v.iloc[pal_row_idx, pal_col_idx] = lkwplan_v.iloc[
                    tauschpartner[randidx][0], tauschpartner[randidx][1]]
                lkwplan_v.iloc[tauschpartner[randidx][0], tauschpartner[randidx][1]] = speicher

            else:  # Dreiertausch benötigt: A=Ausgangspal, B=gleiches n, C=anderes n (bleibt in der Reihe)
                # setze A in den Speicher
                # setze B auf A
                # setze C auf B
                # setze Speicher(A) auf C

                speicher = lkwplan_v.iloc[pal_row_idx, pal_col_idx]
                lkwplan_v.iloc[pal_row_idx, pal_col_idx] = lkwplan_v.iloc[
                    tauschpartner[randidx][0][0], tauschpartner[randidx][0][1]]
                lkwplan_v.iloc[tauschpartner[randidx][0][0], tauschpartner[randidx][0][1]] = lkwplan_v.iloc[
                    tauschpartner[randidx][1][0], tauschpartner[randidx][1][1]]
                lkwplan_v.iloc[tauschpartner[randidx][1][0], tauschpartner[randidx][1][1]] = speicher

            # Bewertung des veränderten Plans
            lkwplan_v = gewichte_optimieren(tabelle_, lkwplan_v, plan_bewertung(tabelle_, lkwplan_v))
            lkwplan_v_bew = plan_bewertung(tabelle_, lkwplan_v)

            if sum(lkwplan_v_bew[0:6]) <= 0.001 and lkwplan_v_bew[-1] <= diff_optimal_ab:
                return lkwplan_v, lkwplan_v_bew

                # Abbruch der gesamten Funktion mit return lwkplan_v, wenn alle "Optimal"-Kriterien erfüllt sind
                # wenn noch nicht optimal aber besser als vorher, wollen wir das als neues Ergebnis speichern
                # und damit in den nächsten Durchlauf der while-Schleife gehen

            else:
                # zunächst noch Ladebalken-Verbesserung durchführen (nur wenn das das einzige Problem ist)
                if lkwplan_v_bew[4] != 0 and sum(lkwplan_v_bew[:3]) + lkwplan_v_bew[5] == 0 and lkwplan_v_bew[
                    3] <= 0.001:
                    lkwplan_v = ladebalken_ausgleich(tabelle_, lkwplan_v)
                    lkwplan_v_bew = plan_bewertung(tabelle_, lkwplan_v)
                    if lkwplan_v_bew[4] == 0:
                        lkwplan_v = gewichte_optimieren(tabelle_, lkwplan_v, lkwplan_v_bew)

                # gucken ob neuer Plan besser ist als vorher: wenn ja dann damit weitermachen, sonst mit dem alten

                if sum(lkwplan_v_bew[:6]) > sum(lkwplan_bew[:6]) or (
                        sum(lkwplan_v_bew[0:6]) == sum(lkwplan_bew[0:6]) and lkwplan_v_bew[-1] >= lkwplan_bew[-1]):
                    # keine Verbesserung -> setze alten Plan als lkwplan_v und nutze ihn erneut für den nächsten Durchgang
                    lkwplan_v = pd.DataFrame(lkwplan_.copy(deep=True))

                    # idx0 (übrige Paletten) wird sich nicht ändern
                    # idx1 auch nicht, weil HPal-Bed. berücksichtigt werden
                    # idx3 auch nicht, weil freie Reihen oben so bleiben

                    # idx2 kühl/trocken kann sich ändern
                    # idx4 Ladebalken kann sich ändern
                    # idx5 Achslast kann sich ändern
                    # idx6 Gewichtsdifferenz kann sich ändern

                    """elif len(np.where(np.asarray(lkwplan_v_bew[4:6])>0)) >= len(np.where(np.asarray(lkwplan_bew[4:6])>0)):
                        #keine Verbesserung -> setze alten Plan als lkwplan_v und nutze ihn erneut für den nächsten Durchgang
                        lkwplan_v=pd.DataFrame(lkwplan_.copy(deep=True)) """

            tauschnr += 1
        # nächster Durchlauf der while-Schleife

    return lkwplan_v, lkwplan_v_bew


# In[20]:


def planauswahl_final(tabelle, planliste, planliste_v2, planliste_v3, diff_optimal_ab, max_tausche):
    bester_plan = pd.DataFrame(planliste[0][0].copy(deep=True))
    bester_plan_bew = planliste[0][1]

    if len(planliste) > 0:
        if sum(bester_plan_bew[0:6]) <= 0.001 and bester_plan_bew[-1] <= diff_optimal_ab:
            return bester_plan, bester_plan_bew

        for pl in planliste:

            # nur Ladebalken-Verstoß:
            if pl[1][4] != 0 and sum(pl[1][:3]) + pl[1][5] == 0 and pl[1][3] <= 0.001:
                pl[0] = ladebalken_ausgleich(tabelle, pl[0])
                pl[1] = plan_bewertung(tabelle, pl[0])

            # pl[0]=gewichte_optimieren(tabelle,pl[0],pl[1]) #jeden Plan zunächst optimieren
            # ist überflüssig, weil 1. Wahl-Liste schon vor dieser Funktion optimiert wird
            # anderen Listen haben noch weitere "Probleme", benötigen also planverb_zufaellig und dort ist es integriert

            if sum(pl[1][0:6]) <= 0.001 and pl[1][-1] <= diff_optimal_ab:  # könnte man aus dem gleichen Grund weglassen
                return pl[0], pl[1]
            else:
                pl[0], pl[1] = planverb_zufaellig(tabelle, pl[0], pl[1],
                                                  max_tausche)  # beinhaltet auch gewichte_optimieren
                if sum(pl[1][0:6]) <= 0.001 and pl[1][-1] <= diff_optimal_ab:
                    return pl[0], pl[1]

                elif sum(pl[1][:6]) < sum(bester_plan_bew[:6]) or (
                        sum(pl[1][0:6]) == sum(bester_plan_bew[0:6]) and pl[1][-1] < bester_plan_bew[-1]):
                    # setze pl[0] als neuen besten Plan
                    bester_plan = pd.DataFrame(pl[0].copy(deep=True))
                    bester_plan_bew = pl[1]

    if len(planliste_v2) > 0:
        bester_pl_v2, bester_pl_v2_bew = planauswahl_final(tabelle, planliste_v2, planliste_v3, [], diff_optimal_ab,
                                                           max_tausche)

        if sum(bester_pl_v2[0:6]) <= 0.001 and bester_pl_v2_bew[-1] <= diff_optimal_ab:
            return bester_pl_v2, bester_pl_v2_bew

        elif sum(bester_pl_v2_bew[:6]) < sum(bester_plan_bew[:6]) or (
                sum(bester_pl_v2_bew[0:6]) == sum(bester_plan_bew[0:6]) and bester_pl_v2_bew[-1] < bester_plan_bew[-1]):
            # setze pl[0] als neuen besten Plan
            bester_plan = pd.DataFrame(bester_pl_v2.copy(deep=True))
            bester_plan_bew = bester_pl_v2_bew

    return bester_plan, bester_plan_bew


# In[ ]:


# In[21]:


"""
______________________________________________________________________________

Ende Funktionsdefinitionen
als Nächstes relevante Werte definieren
______________________________________________________________________________
"""

# In[ ]:


# In[22]:


# FÜR JEDE TOUR EINZELN:

"""tour_idx=2   #11 hat wieder die richtigen h_i-Werte; bei 8 noch testen wieso zwei zweitewahl keine 100 für h_i erhalten
tabelle=pd.DataFrame({'i': np.arange(len(paletten_je_tour[tour_idx]['n_i'])),
                      'n_i': paletten_je_tour[tour_idx]['n_i'],
                      'h_i': paletten_je_tour[tour_idx]['h_i'],
                      'm_i': paletten_je_tour[tour_idx]['m_i'],
                      't_i': paletten_je_tour[tour_idx]['t_i'],
                      'zeile': paletten_je_tour[tour_idx]['zeile']})"""

# In[36]:


# hier eine Tour absichtlich zu Testzwecken verändert

tour_nr_04587 = dict(paletten_je_tour[11])  # dict() benötigt, um eine Kopie zu erzeugen
h04587 = list(np.zeros(len(tour_nr_04587['n_i'])))
# h04587[10]=1
# h04587[11]=1
h04587[37] = 1
tour_nr_04587['h_i'] = h04587

tabelle = pd.DataFrame({'i': np.arange(46), 'n_i': tour_nr_04587['n_i'], 'h_i': tour_nr_04587['h_i'],
                        'm_i': tour_nr_04587['m_i'], 't_i': tour_nr_04587['t_i'], 'zeile': tour_nr_04587['zeile']})

# In[37]:


tabelle

# In[24]:


# zu definierende Grenzwerte:
diff_optimal_ab = 10  # noch zu definierende Grenze, ab der eine Lösung optimal ist (z. B. 10, also 45 % <-> 55 % i.O.)
diff_zulaessig_ab = 50  # zulässig ab einer Verteilung von 75 % <-> 25 %

max_zufaell_tausche = 10  # für Funktion "planverb_zufaellig"

# generelle Annahmen zum LKW:
# hier am Bsp. Zugmaschine MAN + Cool Liner KRONE
radstand_trailer = 7.46
radstand_tractor = 3.6
sattelvorm_tractor = 0.575  # Kingpin 575 mm vor Hinterachse
abst_kp_stw_trailer = 1.45
m_tractor = 7943
m_trailer = 8590
massenschw_vorHA_tractor = 2.538
massenschw_zuStw_trailer = 6.609  # Abstand zur Stirnwand (hier leicht gerundet, s. Excel)
m_HA_max_ges = 11500  # gesetzliche Vorgabe
m_t_max_ges = 24000  # gesetzliche Vorgabe

# In[25]:


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

# In[26]:


anz_pal = max(tabelle['i']) + 1  # da Tabelle nullbasiert
oben = max(anz_pal - 33, 0)

platzhalter_hpal = math.ceil(sum(tabelle['h_i']) / 3) * 3

if anz_pal + platzhalter_hpal > 66:
    raise Exception("Mitnahme aller Paletten nicht möglich!")

# In[ ]:


# In[27]:


"""
______________________________________________________________________________

Ende Vorarbeit
Beginn des tatsächlichen Verfahrens - zunächst Multi-Startverfahren
______________________________________________________________________________
"""

# In[ ]:


# In[28]:


varianten = {'A': {'by': ['n_i', 't_i', 'm_i'],
                   'ascending': [False, True, False]},
             'B': {'by': ['n_i', 't_i', 'm_i'],
                   'ascending': [False, True, True]},
             'C': {'by': ['n_i', 't_i', 'h_i'],
                   'ascending': [False, True, False]},
             'D': {'by': ['n_i', 't_i', 'h_i'],
                   'ascending': [False, True, True]},
             'E': {'by': ['n_i', 't_i'],
                   'ascending': [False, True]},
             'F': {'by': ['n_i', 't_i'],
                   'ascending': [False, True]},
             'G': {'by': ['n_i'],
                   'ascending': [False]},
             'H': {'by': ['n_i'],
                   'ascending': [False]}}

# zweimal zufällig mit t_i für hoffentlich gute HPal-Verteilung
# zweimal zufällig ohne t_i - das darf man ggf. vernachlässigen, falls man ansonsten nichts findet


# In[29]:


lkwplan = pd.DataFrame({str(reihe_k): ['o' for o in range(6)] for reihe_k in range(1, 12)})
plaene = []

for var in varianten:
    # zu verbessern: 'x'-Sperrung & wissen, ob 1 oder 2 Pläne pro Variante muss man nicht für jede Variante wieder prüfen
    # nur von anz_pal abhängig; vorher definieren spart ggf. Rechenaufwand
    tabelle = tabelle.sample(frac=1)  # shuffle all rows to randomize their order
    tabelle.sort_values(by=varianten[var]['by'], ascending=varianten[var]['ascending'], inplace=True)
    tabelle.reset_index(inplace=True, drop=True)

    for planoption in range(1, 4):  # 1 bis 4 ist hier für: plan_fuellen(...,option):

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

# In[30]:


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

# Pläne nach Potential aufteilen
plaene_zweitewahl = []
plaene_pal_ueber = []
pl = 0
while pl < len(plaene):
    if plaene[pl][1][0] > 0:
        plaene_pal_ueber.append(plaene.pop(pl))
    elif sum(plaene[pl][1][0:6]) > 0.001:
        plaene_zweitewahl.append(plaene.pop(pl))
    else:
        pl += 1

# Listen sortieren
plaene = plaene_erstewahl_sort(plaene)
plaene_zweitewahl = plaene_zweitewahl_sort(plaene_zweitewahl)
plaene_pal_ueber = plaene_pal_ueber_sort(plaene_pal_ueber)

# In[ ]:


# In[31]:


"""
______________________________________________________________________________

Erzeugte Startlösungen sortiert
Beginn des Verbesserungsverfahrens, Auswahl der finalen Lösung
______________________________________________________________________________
"""

# In[ ]:


# In[32]:


plaene = plaene_erstewahl_optimieren(tabelle, plaene)

plan_final, plan_final_bew = planauswahl_final(tabelle, plaene, plaene_zweitewahl, plaene_pal_ueber, diff_optimal_ab,
                                               max_zufaell_tausche)

# In[33]:


if sum(plan_final_bew[0:6]) <= 0.001 and plan_final_bew[-1] <= diff_optimal_ab:
    print(
        f'Optimale Lösung gefunden:\n\n{plan_final}\n\nGewichtsdifferenz*:{plan_final_bew[-1]: .2f} %  -  entspricht ca.{plan_final_bew[-1] / 100 * sum(tabelle["m_i"]): .2f} kg Mehrgewicht auf einer Seite')
    print('\t*wenn links 45 % und rechts 55 % des Ladungsgewichts stehen, beträgt die Gewichtsdifferenz 10 %')
elif sum(plan_final_bew[0:6]) <= 0.001 and plan_final_bew[-1] <= diff_zulaessig_ab:
    print(
        f'Zulässige Lösung gefunden:\n\n{plan_final}\n\nGewichtsdifferenz*:{plan_final_bew[-1]: .2f} %  -  entspricht ca.{plan_final_bew[-1] / 100 * sum(tabelle["m_i"]): .2f} kg Mehrgewicht auf einer Seite')
    print('\t*wenn links 45 % und rechts 55 % des Ladungsgewichts stehen, beträgt die Gewichtsdifferenz 10 %')
else:
    print('Noch keine zulässige Lösung gefunden.')
    print(
        f'Beste bisherige Lsg.:\n\n{plan_final}\n\nGewichtsdifferenz*:{plan_final_bew[-1]: .2f} %  -  entspricht ca.{plan_final_bew[-1] / 100 * sum(tabelle["m_i"]): .2f} kg Mehrgewicht auf einer Seite')
    print('\t*wenn links 45 % und rechts 55 % des Ladungsgewichts stehen, beträgt die Gewichtsdifferenz 10 %')

# In[34]:


print(f'bisherige Dauer:{time.time() - starttime: .3f} s')




#___________________________________________________
#TODO:



# für alle zusammen:
# gesamtzeilenliste=np.arange(len(pss_vor))
#
# -> für jede Tour einzeln
#
#     tabelle set index i
#     for row in range(0,6):
#         for col in range(0,11):
#             wert=plan_final.iloc[row,col]
#             psszeile=tabelle[wert]['zeile']
#
#             pss_vor[psszeile][Stellen im string]=... Position als string ' 1' (also Kombi aus row und col)
#                 3x für Ebene, X und Y
#                 DOCK A
#
#
#             pss_vor[psszeile][letzten 5 Stellen bis 101 für Tournr]=tarnr_tarspd[tour_idx][0]
#
#             immer psszeile aus gesamtzeilenliste löschen mit gesamtzeilenliste.remove(psszeile)
#
#
#
#
#
#
# -> am Ende insg. 1x
#
# for i in gesamtzeilenliste:
#     pss_vor[i][Stellen im string]= kein Platz
#
#
#
# new=open(pss_pfad,'w')
# new.writelines(pss_vor)
# new.close()

# In[ ]:





