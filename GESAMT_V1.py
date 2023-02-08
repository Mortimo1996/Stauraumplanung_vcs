import numpy as np
import pandas as pd
import math
import time
from random import randint
from tkinter import *
from tkinter.ttk import *


starttime = time.time()


"""
______________________________________________________________________________

GUI erzeugen
______________________________________________________________________________
"""

def quit():
    window.destroy()

window = Tk()
window.title("Stauraumplanung")
window.width = 300
window.height = 50
window.eval('tk::PlaceWindow . center')

percent = StringVar()
bar = Progressbar(window,orient=HORIZONTAL,length=400)
bar.pack(pady=10)

percentlabel = Label(window,textvariable=percent).pack()
button2 = Button(window,text="Close",command=quit)
button2.pack()

bar['value'] = 0
#percent.set('0 %')
window.update_idletasks()



"""
______________________________________________________________________________

benötigte Daten aus asc-Dateien einlesen
______________________________________________________________________________
"""

#tar_pfad='C:/Users/laras/Documents/Master WiSe 2021/04 Vorlesungen/IT-Studienprojekt/Rohdaten/Testdaten 2017/20171115_1nach/tar.asc'
#tar_pfad='C:/Users/laras/Documents/Master WiSe 2021/04 Vorlesungen/IT-Studienprojekt/Rohdaten/Testdaten August 2022/Daten vor Stauraumplanung/tar.asc'
tar_pfad = 'C:/Users/laras/Documents/Master WiSe 2021/04 Vorlesungen/IT-Studienprojekt/Rohdaten/Testdaten November 2022/Daten vor Stauraumplanung/tar.asc'
tar = open(tar_pfad, 'r')
tar_vor = tar.readlines()
tar.close()

#blk_pfad='C:/Users/laras/Documents/Master WiSe 2021/04 Vorlesungen/IT-Studienprojekt/Rohdaten/Testdaten 2017/20171115_1nach/blk.asc'
#blk_pfad='C:/Users/laras/Documents/Master WiSe 2021/04 Vorlesungen/IT-Studienprojekt/Rohdaten/Testdaten August 2022/Daten vor Stauraumplanung/blk.asc'
blk_pfad = 'C:/Users/laras/Documents/Master WiSe 2021/04 Vorlesungen/IT-Studienprojekt/Rohdaten/Testdaten November 2022/Daten vor Stauraumplanung/blk.asc'
blk = open(blk_pfad, 'r')
blk_vor = blk.readlines()
blk.close()

#pss_pfad='C:/Users/laras/Documents/Master WiSe 2021/04 Vorlesungen/IT-Studienprojekt/Rohdaten/Testdaten 2017/20171115_1nach/pss.asc'
#pss_pfad='C:/Users/laras/Documents/Master WiSe 2021/04 Vorlesungen/IT-Studienprojekt/Rohdaten/Testdaten August 2022/Daten vor Stauraumplanung/pss.asc'
pss_pfad = 'C:/Users/laras/Documents/Master WiSe 2021/04 Vorlesungen/IT-Studienprojekt/Rohdaten/Testdaten November 2022/Daten vor Stauraumplanung/pss.asc'
pss = open(pss_pfad, 'r')
pss_vor = pss.readlines()
pss.close()

vorgaben_spediteure = pd.read_csv('C:/Users/laras/Downloads/Fahrzeugdefinitionen.csv', delimiter=';')
vorgaben_spediteure.set_index('Spediteur',inplace=True,drop=False)

laendervorgaben = pd.read_csv('C:/Users/laras/Downloads/Laendervorgaben.csv', delimiter=';')
laendervorgaben.set_index('Laendercode',inplace=True,drop=False)


blkblo_blktre_blkk02={}
for z_blk in blk_vor: #nicht in späteres identisches for integriert, weil ich dies nicht für jede z_tar in tar_vor wiederholen möchte
    if z_blk[14:16] == 'LK':
        # dictionary füllen mit Blockauftragsnr.: [Auslieferungsreihenfolge, Kommission/Klima]
        blkblo_blktre_blkk02[z_blk[16:23]] = [z_blk[431:436], z_blk[281:282]]


tarnr_tarspd = {}
blkblo_je_tour={}
warnungen={}
fazit={}
zeilennr_tar = 0
idx = 0
for z_tar in tar_vor:
    if z_tar[14:16] == 'AR': # ansonsten ist die Tour von uns nicht zu berücksichtigen
        warnungen[idx]=[]
        fazit[idx] = ' '

        if (vorgaben_spediteure.loc[:, 'Spediteur'] == z_tar[53:63].strip()).any(): # wenn es den Spediteur aus tar in unseren Spediteursvorgaben gibt
            # starte Index von TARNR erst bei 18 statt 16, da Nr. in blk nur fünfstellig
            tarnr_tarspd[idx] = [z_tar[18:23], z_tar[53:63].strip(), zeilennr_tar] #erzeugt dict {idx: [Tournr., Spediteur, Zeile]}
        else: # ansonsten wähle als Vorgaben hier den Defaultwert Andere
            tarnr_tarspd[idx] = [z_tar[18:23], 'Andere', zeilennr_tar]

        #alt (für Variante ohne csv Datei):
        #tarnr_tarspd[idx] = [z_tar[18:23], z_tar[53:63]]  # erzeugt dict {idx: [Tournr., Spediteur]}

        #blkblo_je_tour[idx]=[]
        blkblo_je_tour[idx] = {'Auftragsnr':[], 'Land':[]}
        for z_blk in blk_vor:
            if z_blk[426:431] == z_tar[18:23]:  # gleiche Tournr.
                blkblo_je_tour[idx]['Auftragsnr'].append(z_blk[16:23])  # Liste aller Blockauftragsnummern dieser Tour
                blkblo_je_tour[idx]['Land'].append(z_blk[165:167])  # Liste aller Zielländer dieser Tour

        idx += 1
    zeilennr_tar += 1
anzahl_touren=idx


paletten_je_tour = {}
for idx in range(0,anzahl_touren): #nicht in vorherige for-Schleife integrierbar, weil wir blkblo_je_tour benötigen
    paletten_je_tour[idx] = {'n_i': [], 'h_i': [], 'm_i': [], 't_i': [], 'zeile': []}
    zeilennr_pss = 0
    for z_pss in pss_vor:

        if z_pss[25:32] in blkblo_je_tour[idx]['Auftragsnr']: # wenn BLKNR zur aktuell bearbeiteten Tour gehört
            paletten_je_tour[idx]['n_i'].append(int(blkblo_blktre_blkk02[z_pss[25:32]][0]))

            if int(z_pss[45:55]) > 1070:
                paletten_je_tour[idx]['h_i'].append(1)
            else:
                paletten_je_tour[idx]['h_i'].append(0)

            paletten_je_tour[idx]['m_i'].append(int(z_pss[82:94]) / 1000)


            if blkblo_blktre_blkk02[z_pss[25:32]][1] == 'Y': # wenn Kennz.Kommission/Klima=Y, da der Kühlstatus nur dann für uns relevant ist
                if int(z_pss[110:111]) != 2:  # wollen nur den originalen Eintrag, wenn dieser nicht 2 ist
                    paletten_je_tour[idx]['t_i'].append(int(z_pss[110:111]))
            else:  # alles andere wird als Trockenware behandelt
                paletten_je_tour[idx]['t_i'].append(0)


            paletten_je_tour[idx]['zeile'].append(zeilennr_pss)

        zeilennr_pss += 1



"""
______________________________________________________________________________

bis hier war nur Vorarbeit zum Einlesen der Daten
als Nächstes Definition allgemeingültiger Werte für alle Touren
______________________________________________________________________________
"""

#zu definierende Grenzwerte:
diff_optimal_ab=10 #Grenze, ab der eine Lösung optimal ist (z. B. 10, also 45 % <-> 55 % i.O.)
diff_zulaessig_ab=50 #zulässig ab einer Verteilung von 75 % <-> 25 %

max_zufaell_tausche=7 #für Funktion "planverb_zufaellig" - bricht vorher ab, falls alle NB erfüllt und diff_optimal_ab erreicht


#generelle Annahmen zum LKW:
#hier am Bsp. Zugmaschine MAN + Cool Liner KRONE
radstand_trailer=7.46
radstand_tractor=3.6
sattelvorm_tractor=0.575 #Kingpin 575 mm vor Hinterachse
abst_kp_stw_trailer=1.45
m_tractor=7943
m_trailer=8590
massenschw_vorHA_tractor=2.538
massenschw_zuStw_trailer=6.609 #Abstand zur Stirnwand

last_kp_durch_m_trailer=(1-(massenschw_zuStw_trailer-abst_kp_stw_trailer)/radstand_trailer)*m_trailer
last_t_durch_m_trailer=(massenschw_zuStw_trailer-abst_kp_stw_trailer)/radstand_trailer*m_trailer
last_HA_durch_m_tractor=(1-massenschw_vorHA_tractor/radstand_tractor)*m_tractor



"""
______________________________________________________________________________

Ende allgemeingültiger Werte
als Nächstes folgen die Funktionsdefinitionen
______________________________________________________________________________
"""


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

    return lkwplan




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




def plan_bewertung(tabelle_, lkwplan_):
    bewertung = [0 for i in range(7)]  # erzeugt Liste mit 7 Nullen, 0 bedeutet "alles gut"

    # ---kein idx, da im Startverf.: Restreihe ist "an der Tür"; außerdem Restreihe_einzeln am Rand, zwei mittig&Rand
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




def sort_erstewahl_a(e):
    return e[1][3] #sortiert Pläne mit freien Reihen an der Stirnwand weiter nach hinten

def sort_erstewahl_b(e):
    return e[1][-1] #Gewichtsdifferenz

def plaene_erstewahl_sort(plaene_liste):
    plaene_liste.sort(key=sort_erstewahl_a)
    plaene_liste.sort(key=sort_erstewahl_b)
    return plaene_liste




def sort_zweitewahl_a(e):
    return e[1][-1] #Gewichtsdifferenz

def sort_zweitewahl_b(e):
    return e[1][4] #Ladebalkenverletzung nach vorne holen, damit diese bei Summe in c weiter oben stehen

def sort_zweitewahl_c(e):
    return sum(e[1][:6]) #Summe der anderen Bewertungsindizes exkl. Gewichtsdifferenz

def plaene_zweitewahl_sort(plaene_liste):
    plaene_liste.sort(key=sort_zweitewahl_a)
    plaene_liste.sort(reverse=True,key=sort_zweitewahl_b)
    plaene_liste.sort(key=sort_zweitewahl_c)
    return plaene_liste




def sort_3_a(e):
    return e[1][-1] #Gewichtsdifferenz

def sort_3_b(e):
    return sum(e[1][1:6])  # Summe der anderen Bewertungsindizes exkl. Gewichtsdifferenz

def sort_3_c(e):
    return e[1][0] #Anz. übriger Paletten

def sort_3_d(e):
    # idx1: HPal zulässiger Platz
    # idx4: Ladebalkenbelastung eingehalten (nicht so schlimm wie die anderen beiden, da voraussichtlich besser optimierbar
    # idx5: Achslastvorgaben eingehalten
    return (0 if e[1][1]<1 else 5)+(0 if e[1][4]<1 else 2)+(0 if e[1][5]<1 else 5)

def plaene_pal_ueber_sort(plaene_liste):
    plaene_liste.sort(key=sort_3_a)
    plaene_liste.sort(key=sort_3_b)
    plaene_liste.sort(key=sort_3_c)
    plaene_liste.sort(key=sort_3_d)
    return plaene_liste




def gewichte_optimieren(tabelle_, lkwplan_, bewertung_):
    opt_gewicht = bewertung_[-1]
    plan_gewichte = gewichtsplan(tabelle_, lkwplan_)

    z_sum = plan_gewichte.sum(axis=1,numeric_only=True)
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
    z_sum_new = lkwplan_.sum(axis=1,numeric_only=True)
    if (z_sum_new[0] + z_sum_new[3]) > (z_sum_new[2] + z_sum_new[5]):  # if rechts>links
        speicher_u_r = pd.DataFrame(lkwplan_.iloc[0, :].copy(deep=True))  # unten: rechte Seite zwischenspeichern
        speicher_o_r = pd.DataFrame(lkwplan_.iloc[3, :].copy(deep=True))  # oben: rechte Seite zwischenspeichern

        lkwplan.iloc[0, :] = pd.DataFrame(lkwplan_.iloc[2, :].copy(deep=True))  # unten: links nach rechts stellen
        lkwplan.iloc[3, :] = pd.DataFrame(lkwplan_.iloc[5, :].copy(deep=True))  # oben: links nach rechts stellen

        lkwplan.iloc[2, :] = pd.DataFrame(speicher_u_r.iloc[0, :].copy(deep=True))  # unten: rechts nach links stellen
        lkwplan.iloc[5, :] = pd.DataFrame(speicher_o_r.iloc[0, :].copy(deep=True))  # oben: rechts nach links stellen

    return lkwplan_




def plaene_erstewahl_optimieren(tabelle_o,plaene_o):
    for pl in range(0,len(plaene_o)):
        plaene_o[pl][0]=gewichte_optimieren(tabelle_o,plaene_o[pl][0],plaene_o[pl][1])
        plaene_o[pl][1]=plan_bewertung(tabelle_o,plaene_o[pl][0])

    plaene_o=plaene_erstewahl_sort(plaene_o)
    return plaene_o




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




def planverb_zufaellig(tabelle_, lkwplan_, lkwplan_bew, max_tausche):
    # Funktion für zufällige Palettentausche mit der gleichen, vorherigen oder nächsthöheren Reihe
    # Elemente mit Reihe davor und dahinter vergleichen macht mehr Sinn als mit n+-1
    # Grund: könnte ggf. Palette A (n=3) in Reihe 10 mit B (n=5) in Reihe 9 tauschen (und nicht z. B. nur mit n=4 in Reihe 9)

    # Indizes von 'tabelle_' ändern, damit wir einfacher auf n_i zugreifen können
    tabelle_2 = tabelle_.set_index('i', inplace=False, drop=False)  # erzeugt eine Kopie

    # alten Plan kopieren, um später auf Verbesserung überprüfen zu können
    lkwplan_a = pd.DataFrame(lkwplan_.copy(deep=True))
    lkwplan_a_bew = lkwplan_bew
    lkwplan_v = pd.DataFrame(lkwplan_.copy(deep=True))

    # neue Tabelle bzw. Beladungsplan mit Nr. Auslieferungsreihenfolge erstellen
    lkwplan_n_werte_a = pd.DataFrame(lkwplan_.copy(deep=True))

    # Plan mit n-Werten füllen
    for col in range(0, lkwplan_n_werte_a.shape[1]):
        for row in range(0, lkwplan_n_werte_a.shape[0]):
            if type(lkwplan_n_werte_a.iloc[row, col]) != str:
                lkwplan_n_werte_a.iloc[row, col] = tabelle_2.loc[lkwplan_a.iloc[row, col], 'n_i']
            else:
                lkwplan_n_werte_a.iloc[row, col] = 'x'  # setze zur Vereinfachung auch mögliche 'o' auf 'x'

    lkwplan_n_werte_v = pd.DataFrame(lkwplan_n_werte_a.copy(deep=True))

    tauschnr = 0
    while tauschnr < max_tausche:
        # zufällige Palette auswählen
        pal_row_idx = randint(0, lkwplan_a.shape[0] - 1)  # -1, da wir den Index nutzen und randint(0,2) von 0 bis einschl. 2 zieht
        pal_col_idx = randint(0, lkwplan_a.shape[1] - 1)

        n_wert = lkwplan_n_werte_a.iloc[pal_row_idx, pal_col_idx]

        if n_wert != 'x':

            tauschpartner = []

            # alle Elemente in gleicher Reihe gehen immer
            for row_n in range(0, 6):
                if row_n != pal_row_idx:
                    if lkwplan_n_werte_a.iloc[row_n, pal_col_idx] != 'x':
                        tauschpartner.append([row_n, pal_col_idx])

                        # bei den anderen Reihen müssen h_wert und t_wert berücksichtigt werden
            # wir berücksichtigen nur h, weil t ggf. vernachlässigt werden darf (Bewertung findet hinterher trotzdem die bessere Lsg)

            # Tausch mit vorheriger Reihe
            if pal_col_idx > 0:
                col_idx_neu = pal_col_idx - 1
                liste = tauschpartner_andere_reihe(lkwplan_a, lkwplan_n_werte_a, tabelle_2, pal_row_idx, pal_col_idx,
                                                   col_idx_neu, n_wert)
                tauschpartner.extend(liste)

            # Tausch mit nächsthöherer Reihe
            if pal_col_idx < 10:
                col_idx_neu = pal_col_idx + 1
                liste = tauschpartner_andere_reihe(lkwplan_a, lkwplan_n_werte_a, tabelle_2, pal_row_idx, pal_col_idx,
                                                   col_idx_neu, n_wert)
                tauschpartner.extend(liste)


            # zufälligen Tauschpartner bestimmen
            randidx = randint(0, len(tauschpartner) - 1)

            if type(tauschpartner[randidx][0]) == int:
                lkwplan_v.iloc[pal_row_idx, pal_col_idx] = lkwplan_a.iloc[tauschpartner[randidx][0], tauschpartner[randidx][1]]
                lkwplan_v.iloc[tauschpartner[randidx][0], tauschpartner[randidx][1]] = lkwplan_a.iloc[pal_row_idx, pal_col_idx]

                lkwplan_n_werte_v.iloc[pal_row_idx, pal_col_idx] = lkwplan_n_werte_a.iloc[tauschpartner[randidx][0], tauschpartner[randidx][1]]
                lkwplan_n_werte_v.iloc[tauschpartner[randidx][0], tauschpartner[randidx][1]] = lkwplan_n_werte_a.iloc[pal_row_idx, pal_col_idx]

            else:  # Dreiertausch benötigt: A=Ausgangspal, B=gleiches n, C=anderes n (bleibt in der Reihe)
                # setze A_a auf C_v
                # setze B_a auf A_v
                # setze C_a auf B_v

                lkwplan_v.iloc[tauschpartner[randidx][1][0], tauschpartner[randidx][1][1]] = lkwplan_a.iloc[pal_row_idx, pal_col_idx]
                lkwplan_v.iloc[pal_row_idx, pal_col_idx] = lkwplan_a.iloc[tauschpartner[randidx][0][0], tauschpartner[randidx][0][1]]
                lkwplan_v.iloc[tauschpartner[randidx][0][0], tauschpartner[randidx][0][1]] = lkwplan_a.iloc[tauschpartner[randidx][1][0], tauschpartner[randidx][1][1]]

                lkwplan_n_werte_v.iloc[tauschpartner[randidx][1][0], tauschpartner[randidx][1][1]] = lkwplan_n_werte_a.iloc[pal_row_idx, pal_col_idx]
                lkwplan_n_werte_v.iloc[pal_row_idx, pal_col_idx] = lkwplan_n_werte_a.iloc[tauschpartner[randidx][0][0], tauschpartner[randidx][0][1]]
                lkwplan_n_werte_v.iloc[tauschpartner[randidx][0][0], tauschpartner[randidx][0][1]] = lkwplan_n_werte_a.iloc[tauschpartner[randidx][1][0], tauschpartner[randidx][1][1]]


            # Bewertung des veränderten Plans
            lkwplan_v = gewichte_optimieren(tabelle_, lkwplan_v, plan_bewertung(tabelle_, lkwplan_v))
            lkwplan_v_bew = plan_bewertung(tabelle_, lkwplan_v)

            if math.floor(lkwplan_v_bew[1]) + math.floor(lkwplan_v_bew[2]) + sum(lkwplan_v_bew[4:6]) <= 0.001 and lkwplan_v_bew[-1] <= diff_optimal_ab:
                # bei dem gewählten Vorgehen bleiben Palettenanz. (idx0) und benötigte Ladungssicherung oben (idx3) identisch
                # eine bessere Lsg kann hier nicht erzeugt werden
                return lkwplan_v, lkwplan_v_bew
            else:
                # Abbruch der gesamten Funktion mit return lwkplan_v, wenn alle "Optimal"-Kriterien erfüllt sind
                # wenn noch nicht optimal aber besser als vorher, wollen wir das als neues Ergebnis speichern
                # und damit in den nächsten Durchlauf der while-Schleife gehen
                # zunächst noch Ladebalken-Verbesserung durchführen
                # nur wenn die anderen beiden notwendigen Indizes 1 und 5 passend erfüllt sind
                if lkwplan_v_bew[4] != 0 and math.floor(lkwplan_v_bew[1]) + lkwplan_v_bew[5] == 0:
                    lkwplan_v = ladebalken_ausgleich(tabelle_, lkwplan_v)
                    lkwplan_v_bew = plan_bewertung(tabelle_, lkwplan_v)
                    if lkwplan_v_bew[4] == 0:
                        lkwplan_v = gewichte_optimieren(tabelle_, lkwplan_v, lkwplan_v_bew)
                        lkwplan_v_bew = plan_bewertung(tabelle_, lkwplan_v)


                # gucken ob neuer Plan besser ist als vorher: wenn ja dann damit weitermachen, sonst mit dem alten
                # bei dem gewählten Vorgehen bleiben Palettenanz. (idx0) und benötigte Ladungssicherung oben (idx3) identisch
                verbessert=False
                if lkwplan_v_bew[1]<=lkwplan_a_bew[1] and lkwplan_v_bew[4]<=lkwplan_a_bew[4] and lkwplan_v_bew[5]<=lkwplan_a_bew[5]:
                    if lkwplan_v_bew[1]<lkwplan_a_bew[1] or lkwplan_v_bew[4]<lkwplan_a_bew[4] or lkwplan_v_bew[5]<lkwplan_a_bew[5]:
                        verbessert=True
                    elif lkwplan_v_bew[2]<lkwplan_a_bew[2]:
                        verbessert=True
                    elif lkwplan_v_bew[2]==lkwplan_a_bew[2] and lkwplan_v_bew[6]<lkwplan_a_bew[6]:
                        verbessert=True

                if verbessert:
                    # Verbesserung erzielt: setze lkwplan_v als den Ausgangsplan lkwplan_a und nutze ihn für den nächsten Durchgang
                    lkwplan_a = pd.DataFrame(lkwplan_v.copy(deep=True))
                    lkwplan_a_bew = lkwplan_v_bew
                    lkwplan_n_werte_a = pd.DataFrame(lkwplan_n_werte_v.copy(deep=True))

                else: # lkwplan_v wieder auf lkwplan_a zurücksetzen, damit Verbesserungsschritte der nächsten Runde keine Altlasten beinhalten
                    lkwplan_v = pd.DataFrame(lkwplan_a.copy(deep=True))
                    lkwplan_n_werte_v = pd.DataFrame(lkwplan_n_werte_a.copy(deep=True))
                    # lkwplan_v_bew wird im nächsten Durchgang sowieso neu bestimmt, bevor etwas davon benötigt wird


            tauschnr += 1
        # nächster Durchlauf der while-Schleife

    return lkwplan_a, lkwplan_a_bew




def planauswahl_final(tabelle, planliste, planliste_v2, planliste_v3, diff_optimal_ab, max_tausche):

    if len(planliste) > 0:
        bester_plan = pd.DataFrame(planliste[0][0].copy(deep=True))
        bester_plan_bew = planliste[0][1]

        if sum(bester_plan_bew[0:6]) <= 0.001 and bester_plan_bew[-1] <= diff_optimal_ab:
            return bester_plan, bester_plan_bew

        for pl in planliste:

            # nur Ladebalken-Verstoß:
            # if pl[1][4] != 0 and sum(pl[1][:3]) + pl[1][5] == 0 and pl[1][3] <= 0.001:
            if pl[1][4] != 0 and math.floor(pl[1][1]) + pl[1][5] == 0:
                pl[0] = ladebalken_ausgleich(tabelle, pl[0])
                pl[1] = plan_bewertung(tabelle, pl[0])
                if pl[1][4] == 0:
                    pl[0] = gewichte_optimieren(tabelle, pl[0], pl[1])
                    pl[1] = plan_bewertung(tabelle, pl[0])

            # pl[0]=gewichte_optimieren(tabelle,pl[0],pl[1])  # könnte hier jeden Plan zunächst optimieren
            # ist überflüssig, weil 1. Wahl-Liste schon vor dieser Funktion optimiert wird
            # anderen Listen haben noch weitere "Probleme", benötigen also planverb_zufaellig und dort ist es integriert

            if sum(pl[1][0:6]) <= 0.001 and pl[1][-1] <= diff_optimal_ab:
                return pl[0], pl[1]
            else:
                pl[0], pl[1] = planverb_zufaellig(tabelle, pl[0], pl[1], max_tausche)  # beinhaltet auch gewichte_optimieren

                # verschiedenste Pläne miteinander vergleichen - idx0 & idx3 können sich jetzt also auch ändern
                verbessert=False
                if sum(pl[1][0:6]) <= 0.001 and pl[1][-1] <= diff_optimal_ab:
                    return pl[0], pl[1]

                elif pl[1][0]<bester_plan_bew[0]: # mehr Paletten mitnehmen können ist immer besser (wenn notw. Kriterien erfüllt sind)
                    if pl[1][1] <= bester_plan_bew[1] and pl[1][4] <= bester_plan_bew[4] and pl[1][5] <= bester_plan_bew[5]:
                        verbessert=True

                elif pl[1][0] == bester_plan_bew[0]:
                    if pl[1][1] <= bester_plan_bew[1] and pl[1][4] <= bester_plan_bew[4] and pl[1][5] <= bester_plan_bew[5]:
                        if pl[1][1] < bester_plan_bew[1] or pl[1][4] < bester_plan_bew[4] or pl[1][5] < bester_plan_bew[5]:
                            verbessert = True
                        elif sum(pl[1][2:4]) < sum(bester_plan_bew[2:4]): #kühl-trocken + Ladungssicherung oben
                            verbessert=True
                        elif sum(pl[1][2:4]) == sum(bester_plan_bew[2:4]) and pl[1][6]<bester_plan_bew[6]: # Gewichtsdiff. verkleinert
                            verbessert = True

                if verbessert:
                    # setze pl[0] als neuen besten Plan
                    bester_plan = pd.DataFrame(pl[0].copy(deep=True))
                    bester_plan_bew = pl[1]


    if len(planliste_v2) > 0:
        if len(planliste) == 0: # hier hätten wir bester_plan noch nicht belegt
            bester_plan = pd.DataFrame(planliste_v2[0][0].copy(deep=True))
            bester_plan_bew = planliste_v2[0][1]

        bester_pl_v2, bester_pl_v2_bew = planauswahl_final(tabelle, planliste_v2, planliste_v3, [], diff_optimal_ab, max_tausche)

        verbessert = False
        if sum(bester_pl_v2_bew[0:6]) <= 0.001 and bester_pl_v2_bew[-1] <= diff_optimal_ab:
            return bester_pl_v2, bester_pl_v2_bew

        elif bester_pl_v2_bew[0] < bester_plan_bew[0]:  # mehr Paletten mitnehmen können ist immer besser (wenn notw. Kriterien erfüllt sind)
            if bester_pl_v2_bew[1] <= bester_plan_bew[1] and bester_pl_v2_bew[4] <= bester_plan_bew[4] and bester_pl_v2_bew[5] <= bester_plan_bew[5]:
                verbessert = True

        elif bester_pl_v2_bew[0] == bester_plan_bew[0]:
            if bester_pl_v2_bew[1] <= bester_plan_bew[1] and bester_pl_v2_bew[4] <= bester_plan_bew[4] and bester_pl_v2_bew[5] <= bester_plan_bew[5]:
                if bester_pl_v2_bew[1] < bester_plan_bew[1] or bester_pl_v2_bew[4] < bester_plan_bew[4] or bester_pl_v2_bew[5] < bester_plan_bew[5]:
                    verbessert = True
                elif sum(bester_pl_v2_bew[2:4]) < sum(bester_plan_bew[2:4]):  # kühl-trocken + Ladungssicherung oben
                    verbessert = True
                elif sum(bester_pl_v2_bew[2:4]) == sum(bester_plan_bew[2:4]) and bester_pl_v2_bew[6] < bester_plan_bew[6]:  # Gewichtsdiff. verkleinert
                    verbessert = True

        if verbessert:
            # setze bester_pl_v2 als neuen besten Plan
            bester_plan = pd.DataFrame(bester_pl_v2.copy(deep=True))
            bester_plan_bew = bester_pl_v2_bew


    if len(planliste) > 0 or len(planliste_v2) > 0:
        return bester_plan, bester_plan_bew




"""
______________________________________________________________________________

Ende Funktionsdefinitionen
jetzt kann über die Touren iteriert und Lösungen gefunden werden
______________________________________________________________________________
"""



# Zeilen der pss-Datei zur späteren Befüllung mitverfolgen
gesamtzeilenliste=list(np.arange(len(pss_vor)))


for tour_idx in range(0,anzahl_touren):
    time_tour = time.time()

    percent.set(f'Tour {tour_idx+1}/{anzahl_touren}')
    window.update_idletasks()


    if tarnr_tarspd[tour_idx][1] == 'Andere': # bei Spediteur "Andere" die Paletten beliebig durchnummerieren und unser Verfahren gar nicht durchlaufen
        print(f'Tour {tour_idx} -> Spediteur: "Andere"')

        ladenr = 0
        for z in paletten_je_tour[tour_idx]['zeile']:
            gesamtzeilenliste.remove(z)
            ladenr+=1

            # Tournummer
            pss_vor[z] = pss_vor[z][:94] + "00" + str(tarnr_tarspd[tour_idx][0]) + pss_vor[z][101:]

            # Ladereihenfolge
            if ladenr < 10:
                pss_vor[z] = pss_vor[z][:115] + "   " + str(ladenr) + pss_vor[z][119:]
            else:
                pss_vor[z] = pss_vor[z][:115] + "  " + str(ladenr) + pss_vor[z][119:]

            # Dock
            pss_vor[z] = pss_vor[z][:123] + " DOCK A   " + pss_vor[z][133:]


        bar['value'] += 100 / anzahl_touren
        percent.set(str((tour_idx + 1) / anzahl_touren * 100) + "%")
        window.update_idletasks()
        continue


    #erzeuge ein Dataframe mit allen relevanten Infos zu dieser Tour - Vorteil: erleichtert alle späteren Schritte
    tabelle=pd.DataFrame({'i': np.arange(len(paletten_je_tour[tour_idx]['n_i'])),
                          'n_i': paletten_je_tour[tour_idx]['n_i'],
                          'h_i': paletten_je_tour[tour_idx]['h_i'],
                          'm_i': paletten_je_tour[tour_idx]['m_i'],
                          't_i': paletten_je_tour[tour_idx]['t_i'],
                          'zeile': paletten_je_tour[tour_idx]['zeile']})

    # Ländervorgaben - individuell je Tour prüfen, da Touren verschiedene Zielländer haben können
    tour_laender = set(blkblo_je_tour[tour_idx]['Land']) # eine Menge (set) erhält jedes Element nur einmal

    if len(tour_laender)==1:
        m_HA_max_ges = laendervorgaben.loc[min(tour_laender),'Achslast Sattelzug Hinten']  # min gibt hier das eine Element der Menge zurück
        m_t_max_ges = laendervorgaben.loc[min(tour_laender),'Auflieger Dreiachsig']
    else:
        m_HA_max_ges = laendervorgaben.loc[min(tour_laender), 'Achslast Sattelzug Hinten']  # min gibt hier ein Element der Menge zurück
        m_t_max_ges = laendervorgaben.loc[min(tour_laender), 'Auflieger Dreiachsig']
        for ld in tour_laender:
            if ld != min(tour_laender):
                m_HA_v2 = laendervorgaben.loc[ld, 'Achslast Sattelzug Hinten']
                m_t_v2 = laendervorgaben.loc[ld, 'Auflieger Dreiachsig']
                if m_HA_v2<m_HA_max_ges:
                    m_HA_max_ges=m_HA_v2
                if m_t_v2<m_t_max_ges:
                    m_t_max_ges=m_t_v2

    m_kp_max_vor_m_trailer = (m_HA_max_ges - last_HA_durch_m_tractor) / (1 - sattelvorm_tractor / radstand_tractor)
    m_kp_max = m_kp_max_vor_m_trailer - last_kp_durch_m_trailer
    m_t_max = m_t_max_ges - last_t_durch_m_trailer

    #tourenabhängige Werte
    m_lad=tabelle['m_i'].sum() # Einheit kg

    #Untergrenze:
    lsp_u = radstand_trailer*(1-m_kp_max/m_lad)+abst_kp_stw_trailer

    #Obergrenze:    -> Annahme: mindestens 25% des aktuellen Gesamtgewichts auf HA der Zugmaschine
    anteil_mKP_HA=1-sattelvorm_tractor/radstand_tractor #KP-Last zu ...% auf der HA der Zugmaschine:
    lsp_o = min(m_t_max/m_lad*radstand_trailer+abst_kp_stw_trailer, abst_kp_stw_trailer+radstand_trailer/m_lad*(0.7025*(m_lad+m_trailer)-0.2975*m_tractor+1/anteil_mKP_HA*last_HA_durch_m_tractor))

    #print(f'Untergrenze (in m ab Stirnwand): {lsp_u:.3f} \nObergrenze (in m ab Stirnwand): {lsp_o:.3f}')


    anz_pal=max(tabelle['i'])+1 #da Tabelle nullbasiert
    oben=max(anz_pal-33,0)

    platzhalter_hpal=math.ceil(sum(tabelle['h_i'])/3)*3 # Hochpaletten versperren in oberer Ebene MINDESTENS so viele Plätze


    # eine Tour ist problematisch bzw. so nicht zu verplanen, wenn
    if anz_pal > vorgaben_spediteure.loc[tarnr_tarspd[tour_idx][1],'Gesamtkapazitaet']: #Spediteursvorgaben zur maximalen Palettenanz. (entweder Doppelstock=66 oder nicht=33) überschritten?
        warnungen[tour_idx].append('Zu viele Paletten für diesen Spediteur eingeplant!')

    elif m_lad > vorgaben_spediteure.loc[tarnr_tarspd[tour_idx][1],'Zulaessige Nutzlast']: #Spediteursvorgaben zur maximalen Nutzlast überschritten?
        warnungen[tour_idx].append(f'Max. zulässige Nutzlast des Spediteurs von {vorgaben_spediteure.loc[tarnr_tarspd[tour_idx][1],"Nutzlast"]} kg um {m_lad - vorgaben_spediteure.loc[tarnr_tarspd[tour_idx][1],"Nutzlast"]} überschritten!')

    elif anz_pal+platzhalter_hpal > 66 and vorgaben_spediteure.loc[tarnr_tarspd[tour_idx][1],'Gesamtkapazitaet']==66:
        warnungen[tour_idx].append('Mitnahme aller Paletten nicht möglich - Reihen über Hochpaletten müssen frei bleiben')



    """
    ______________________________________________________________________________

    Ende Vorarbeit
    Beginn des tatsächlichen Verfahrens - nur, wenn keine Warnung erzeugt wurde
    zunächst Multi-Startverfahren
    ______________________________________________________________________________
    """


    #if len(warnungen[tour_idx])==0:

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
                 'G': {'by': ['n_i', 't_i'],
                       'ascending': [False, True]},
                 'H': {'by': ['n_i', 't_i'],
                       'ascending': [False, True]},
                 'I': {'by': ['n_i', 't_i'],
                       'ascending': [False, True]},
                 'J': {'by': ['n_i', 'h_i'],
                       'ascending': [False, True]},
                 'K': {'by': ['n_i', 'h_i'],
                       'ascending': [False, False]},
                 'L': {'by': ['n_i', 'm_i'],
                       'ascending': [False, True]},
                 'M': {'by': ['n_i', 'm_i'],
                       'ascending': [False, False]},
                 'N': {'by': ['n_i'],
                       'ascending': [False]},
                 'O': {'by': ['n_i'],
                       'ascending': [False]},
                 'P': {'by': ['n_i'],
                       'ascending': [False]},
                 'Sonderfall':{}}

    lkwplan = pd.DataFrame({str(reihe_k): ['o' for o in range(6)] for reihe_k in range(1, 12)})
    plaene = []

    for var in varianten:

        if var != 'Sonderfall':
            tabelle = tabelle.sample(frac=1)  # Zeilen zufällig mischen, um ihre Reihenfolge zu verändern
            tabelle.sort_values(by=varianten[var]['by'], ascending=varianten[var]['ascending'], inplace=True)
            tabelle.reset_index(inplace=True, drop=True)
        else:
            # print('SONDERFALL')
            for n_einzeln in range(1, max(tabelle['n_i']) + 1):

                if n_einzeln % 2 == 0:  # für gerade n
                    tabelle_n = tabelle.loc[tabelle['n_i'] == n_einzeln].sort_values(by='h_i', ascending=True)
                else:  # für ungerade n
                    tabelle_n = tabelle.loc[tabelle['n_i'] == n_einzeln].sort_values(by='h_i', ascending=False)

                if n_einzeln == 1:  # im ersten Durchlauf zunächst tabelle_alle erzeugen
                    tabelle_alle = pd.DataFrame(tabelle_n.copy(deep=True))
                else:
                    tabelle_alle = pd.concat([tabelle_alle, tabelle_n])

            tabelle = tabelle_alle.reset_index(inplace=False, drop=True)


        planoption = 1
        anz_opt_plan_fuellen = 3
        while planoption <= anz_opt_plan_fuellen:
            # vorher: for planoption in range(1, 4):  # 1 bis einschl. 3 ist hier für: plan_fuellen(...,option):
            # von for zu while geändert, um bei früh gefundener 'optimaler' Lsg. (break) auch die for-Schleife beenden zu können
            # ermöglicht Zeitersparnis, aber auch ggf. etwas schlechtere (dennoch als 'optimal' geltende) Lösungen

            plaene.append([pd.DataFrame(lkwplan.copy(deep=True)), None])

            zweioptionen = False
            if anz_pal <= 33:
                plaene[-1][0].iloc[3:, :] = 'x'

                if anz_pal <= 30:  # bei weniger als 31 gibt es zwei Möglichkeiten für ganz freie Reihen
                    plaene.append([pd.DataFrame(plaene[-1][0].copy(deep=True)), None])
                    zweioptionen = True

                    for frei in range(0, 11 - math.ceil(anz_pal / 3)):
                        plaene[-1][0].iloc[:3, frei] = 'x'  # hier ist -1 dann der neu hinzugefügte

            elif anz_pal <= 63:  # auch hier gibt es zwei Möglichkeiten für ganz freie Reihen
                plaene.append([pd.DataFrame(plaene[-1][0].copy(deep=True)), None])
                zweioptionen = True

                for frei in range(0, 11 - math.ceil(oben / 3)):
                    plaene[-1][0].iloc[3:, frei] = 'x'  # hier ist -1 dann der neu hinzugefügte

            # bei 64 oder mehr mache nichts, weil Restreihe an der Tür ist & alle anderen Reihen voll sind

            # dann kann man beide Versionen füllen und falls HPal kommt, ganze Reihen sperren
            # trotzdem weiter befüllen, aber Strafkosten vergeben, damit ideale Lösung (wenn es eine gibt) besser ist

            plaene[-1][0] = plan_fuellen(tabelle, plaene[-1][0], anz_pal, oben, planoption)
            plaene[-1][1] = plan_bewertung(tabelle, plaene[-1][0])

            if zweioptionen:
                plaene[-2][0] = plan_fuellen(tabelle, plaene[-2][0], anz_pal, oben, planoption)
                plaene[-2][1] = plan_bewertung(tabelle, plaene[-2][0])
                """if (sum(plaene[-2][1][0:6]) <= 0.001 and plaene[-2][1][-1] <= diff_optimal_ab):
                    # break bricht nur die innere "while planoption<=4"-Schleife ab
                    break

            if (sum(plaene[-1][1][0:6]) <= 0.001 and plaene[-1][1][-1] <= diff_optimal_ab):
                # Sortierung dieses ifs nach if zweioptionen gewählt, um beide Optionen noch mitzunehmen
                # break bricht nur die innere "while planoption<=4"-Schleife ab
                break"""

            planoption += 1

        if planoption < anz_opt_plan_fuellen:
            # break bricht bei zuvor schon gefundener optimaler Lsg. jetzt auch die "for var in varianten"-Schleife ab
            break



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

    waehle_else = True
    if len(plaene)>0: # wenn es Lösungen gibt, die alle Paletten mitnehmen können, löschen wir die anderen direkt
        plaene_pal_ueber=[]
        waehle_else = False
    elif len(plaene_zweitewahl)>0: # wird nur durchlaufen, wenn len(plaene)==0
        for p in range(0,len(plaene_zweitewahl)):
            if plaene_zweitewahl[p][1][1]+sum(plaene_zweitewahl[p][1][4:6])==0:
                # prüfe, ob idx1+idx4+idx5==0 (später notwendige Bedingungen)
                # man kann z. B. idx4 voraussichtlich gut optimieren, aber in dieser Code-Sortierung nicht mit Sicherheit gegeben
                # wenn das für mind. einen Plan der 2. Wahl erfüllt ist, können wir plaene_pal_ueber löschen
                # ansonsten könnte es sein, dass 2. Wahl die wirklich notwendigen Bed. niemals erfüllt & wir doch pal_ueber brauchen
                plaene_pal_ueber = []
                waehle_else = False
                break

    if len(plaene)+len(plaene_zweitewahl)==0 or waehle_else:
        plaene_pal_ueber = plaene_pal_ueber_sort(plaene_pal_ueber)

        # folgenden Zeilen ggf. nur sinnvoll, solange das Verbesserungsverfahren keine Hinzunahme weiterer Paletten ermöglicht
        # plaene_pal_ueber ist nach Anz. fehlender Paletten, aber übergeordnet nochmal nach Bewertung idx1,idx4,idx5 sortiert
        # mit der Sortierung erreiche ich, dass ich die Anz. fehlender Paletten einer akzeptablen Lsg. als Untergrenze setzen kann
        plaene_ueber_neu = [plaene_pal_ueber[0]]
        for p in range(1,len(plaene_pal_ueber)):
            if plaene_pal_ueber[p][1][0] <= plaene_pal_ueber[0][1][0]: # wenn die Anzahl nicht mitnehmbarer Paletten der der akzeptablen Lsg. entspricht
                plaene_ueber_neu.append(plaene_pal_ueber[p])
            else:
                break # kann die for-Schleife vorzeitig verlassen, weil plaene_pal_ueber nach Anz. fehlender Paletten sortiert ist
        plaene_pal_ueber = plaene_ueber_neu.copy()



    """
    ______________________________________________________________________________

    Erzeugte Startlösungen sortiert
    Beginn des Verbesserungsverfahrens, Auswahl der finalen Lösung
    ______________________________________________________________________________
    """


    plaene = plaene_erstewahl_optimieren(tabelle, plaene)

    if len(plaene)>0 or len(plaene_zweitewahl)>0:
        plan_final, plan_final_bew = planauswahl_final(tabelle, plaene, plaene_zweitewahl, plaene_pal_ueber, diff_optimal_ab, max_zufaell_tausche)
    else:
        plan_final, plan_final_bew = planauswahl_final(tabelle, plaene_pal_ueber, [], [], diff_optimal_ab, max_zufaell_tausche)


    if sum(plan_final_bew[0:6]) <= 0.001 and plan_final_bew[-1] <= diff_optimal_ab:
        fazit[tour_idx]=f'Optimale Lösung gefunden, Gewichtsdifferenz beträgt {plan_final_bew[-1]: .2f} %  -  entspricht ca. {plan_final_bew[-1] / 100 * sum(tabelle["m_i"]): .2f} kg Mehrgewicht auf einer Seite'
    elif sum(plan_final_bew[0:6]) <= 0.001 and plan_final_bew[-1] <= diff_zulaessig_ab:
        fazit[tour_idx]=f'Zulässige Lösung gefunden, Gewichtsdifferenz beträgt {plan_final_bew[-1]: .2f} %  -  entspricht ca.{plan_final_bew[-1] / 100 * sum(tabelle["m_i"]): .2f} kg Mehrgewicht auf einer Seite'
    elif sum(plan_final_bew[0:2])+sum(plan_final_bew[4:5]) <= 0.001 and plan_final_bew[-1] <= diff_zulaessig_ab:
        if plan_final_bew[2]>0 and plan_final_bew[3]>0.001:
            problem = 'Kühl-trocken-Trennung verletzt und zusätzliche Ladungssicherung benötigt'
        elif plan_final_bew[2]>0:
            problem = f'Kühl-trocken-Trennung bei {plan_final_bew[2]} Paletten nicht eingehalten.'
        elif plan_final_bew[3]>0.001:
            problem = 'Oben zusätzliche Ladungssicherung benötigt.'
        else:
            problem='' # kann eigentlich nicht passieren
        fazit[tour_idx] = f'Lösung gefunden, Einschränkung: {problem} \nGewichtsdifferenz beträgt {plan_final_bew[-1]: .2f} %  -  entspricht ca.{plan_final_bew[-1] / 100 * sum(tabelle["m_i"]): .2f} kg Mehrgewicht auf einer Seite'

    else:
        fazit[tour_idx]=f'Keine zulässige Lösung gefunden. Die beste bisherige Lösung hat folgende Bewertung: {plan_final_bew}'



    # Überschreiben der pss-Datei vorbereiten
    tabelle.set_index('i', inplace=True)
    ladenr=0
    for col in range(0, 11):
        for row in [1, 0, 2, 4, 3, 5]:
            wert = plan_final.iloc[row, col]
            if type(wert) != str:
                ladenr += 1
                psszeile = tabelle.loc[wert, 'zeile']
                gesamtzeilenliste.remove(psszeile)

                # Tournummer
                pss_vor[psszeile] = pss_vor[psszeile][:94] + "00" + str(tarnr_tarspd[tour_idx][0]) + pss_vor[psszeile][101:]

                # Beladungsebene
                if row < 3:
                    pss_vor[psszeile] = pss_vor[psszeile][:101] + " 1" + pss_vor[psszeile][103:]
                else:
                    pss_vor[psszeile] = pss_vor[psszeile][:101] + " 2" + pss_vor[psszeile][103:]

                # X-Koordinate
                if col < 9:
                    pss_vor[psszeile] = pss_vor[psszeile][:103] + "  " + str(col + 1) + pss_vor[psszeile][106:]
                else:
                    pss_vor[psszeile] = pss_vor[psszeile][:103] + " " + str(col + 1) + pss_vor[psszeile][106:]

                # Y-Koordinate
                if row == 0 or row == 3:
                    pss_vor[psszeile] = pss_vor[psszeile][:106] + "  3" + pss_vor[psszeile][109:]
                elif row == 1 or row == 4:
                    pss_vor[psszeile] = pss_vor[psszeile][:106] + "  2" + pss_vor[psszeile][109:]
                else:
                    pss_vor[psszeile] = pss_vor[psszeile][:106] + "  1" + pss_vor[psszeile][109:]

                # Ladereihenfolge
                if ladenr < 10:
                    pss_vor[psszeile] = pss_vor[psszeile][:115] + "   " + str(ladenr) + pss_vor[psszeile][119:]
                else:
                    pss_vor[psszeile] = pss_vor[psszeile][:115] + "  " + str(ladenr) + pss_vor[psszeile][119:]

                # Dock
                pss_vor[psszeile] = pss_vor[psszeile][:123] + " DOCK A   " + pss_vor[psszeile][133:]


    tar_vor[tarnr_tarspd[tour_idx][2]] = tar_vor[tarnr_tarspd[tour_idx][2]][:97] + "001" + tar_vor[tarnr_tarspd[tour_idx][2]][100:]

    """print('\n',plan_final)
    if len(warnungen[tour_idx]) > 0:
        print(warnungen[tour_idx][0])
    print(plan_final_bew)"""
    print(f'Verfahrensdauer Tour {tour_idx}: {time.time() - time_tour}')


    bar['value'] += 100 / anzahl_touren
    #percent.set(str((tour_idx + 1) / anzahl_touren * 100) + "%")
    window.update_idletasks()



print(f'\nÜber alle {anzahl_touren} Touren konnten insgesamt {len(gesamtzeilenliste)} von {len(pss_vor)} Paletten nicht passend eingeplant werden.')
for restz in gesamtzeilenliste:
    pss_vor[restz] = pss_vor[restz][:123] + "kein Platz" + pss_vor[restz][133:]



#pss-Datei überschreiben bzw. hier zu Testzwecken neue Datei erzeugen
#pss_pfad
pss_pfad_unsere_lsg='C:/Users/laras/Documents/Master WiSe 2021/04 Vorlesungen/IT-Studienprojekt/Rohdaten/Testdaten November 2022/Daten nach_eigene Lösung/pss.asc'
new_pss=open(pss_pfad_unsere_lsg,'w')
new_pss.writelines(pss_vor)
new_pss.close()


#tar-Datei überschreiben bzw. hier zu Testzwecken neue Datei erzeugen
tar_pfad_unsere_lsg='C:/Users/laras/Documents/Master WiSe 2021/04 Vorlesungen/IT-Studienprojekt/Rohdaten/Testdaten November 2022/Daten nach_eigene Lösung/tar.asc'
new_tar=open(tar_pfad_unsere_lsg,'w')
new_tar.writelines(tar_vor)
new_tar.close()


percent.set("Verfahren abgeschlossen")
window.update_idletasks()

window.mainloop()



"""
______________________________________________________________________________

Alle Touren durchlaufen
Feedback an den Benutzer ausgeben (-> GUI)
______________________________________________________________________________
"""


print('\n')
for tour_idx in range(0,anzahl_touren):

    if tarnr_tarspd[tour_idx][1] == 'Andere':
        print(f'Tour {tarnr_tarspd[tour_idx][0]} hat Spediteurkennzeichen "Andere" und erhält deshalb nur eine aufsteigende Durchnummerierung ')

    else:
        if len(warnungen[tour_idx])>0:
            print(f'Es gab bereits in der Vorüberprüfung folgendes Problem mit Tour {tarnr_tarspd[tour_idx][0]}:')
            for w in warnungen[tour_idx]: #dürfte eigentlich nur ein Eintrag sein, sicherheitshalber iterieren
                print('\t',w)

        print(f'Verfahren für Tour {tarnr_tarspd[tour_idx][0]} durchlaufen. Ergebnis:')
        print(fazit[tour_idx])

    print(' ')

print(f'Benötigte Gesamtzeit: {time.time()-starttime}')
