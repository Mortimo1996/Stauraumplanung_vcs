import numpy as np
import pandas as pd
import math
from random import randint


"""
______________________________________________________________________________

Relevante Dateipfade
______________________________________________________________________________
"""

pfad_vorgabenspediteure='.../Fahrzeugdefinitionen.csv'
pfad_laendervorgaben='.../Laendervorgaben.csv'


tar_pfad = '.../Testdaten November 2022/Daten vor Stauraumplanung/tar.asc'
blk_pfad = '.../Testdaten November 2022/Daten vor Stauraumplanung/blk.asc'
pss_pf_nach_F = '.../Testdaten November 2022/Daten nach Stauraumplanung/pss.asc'
pss_pf_nach_wir = '.../Testdaten November 2022/Daten nach_eigene Lösung/pss.asc'


"""
______________________________________________________________________________

Definitionen vorab
______________________________________________________________________________
"""

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

benötigte Daten aus asc-Dateien einlesen und aufbereiten
______________________________________________________________________________
"""

tar = open(tar_pfad, 'r')
tar_vor = tar.readlines()
tar.close()

blk = open(blk_pfad, 'r')
blk_vor = blk.readlines()
blk.close()

pss = open(pss_pf_nach_F, 'r')
pss_nach_F = pss.readlines()
pss.close()

pss = open(pss_pf_nach_wir, 'r')
pss_nach_wir = pss.readlines()
pss.close()


vorgaben_spediteure = pd.read_csv(pfad_vorgabenspediteure, delimiter=';')
vorgaben_spediteure.set_index('Spediteur',inplace=True,drop=False)

laendervorgaben = pd.read_csv(pfad_laendervorgaben, delimiter=';')
laendervorgaben.set_index('Laendercode',inplace=True,drop=False)


blkblo_blktre_blkk02 = {}
for z_blk in blk_vor:  # nicht in späteres identisches for integriert, weil ich dies nicht für jede z_tar in tar_vor wiederholen möchte ...
    # ... und es außerdem seit separater Berücksichtigung des Usps auch 'fertig' benötige
    if z_blk[14:16] == 'LK':
        """alte Version vor separater Berücksichtigung des Usps:
        # dictionary füllen mit Blockauftragsnr.: [Auslieferungsreihenfolge, Kommission/Klima]
        blkblo_blktre_blkk02[z_blk[16:23]] = [z_blk[431:436], z_blk[281:282]]"""
        # blkblo_blktre_blkk02 dictionary füllen mit Blockauftragsnr.: [Tournr.-Usp als Platzhalter für späteres n, Kommission/Klima]
        usp = z_blk[54:60].strip()
        if usp == '0':  # Usp 0 ist nichtssagend, hier Auslieferungsreihenfolge der Kundennr. nutzen
            usp = 'kd' + (z_blk[46:53].strip())  # Spalte Kunde in BLK
            # Kennzeichnung kd benötigt, da es z. B. Kundennr. 5 gibt, die NICHT Umschlagspunkt 5 entspricht
        blkblo_blktre_blkk02[z_blk[16:23]] = [(z_blk[426:431] + '-' + usp), z_blk[281:282]]

tarnr_tarspd = {}
blkblo_je_tour = {}
usp_touren = {}  # Umschlagspunkte
warnungen = {}
fazit = {}
zeilennr_tar = 0
idx = 0
for z_tar in tar_vor:
    if z_tar[14:16] == 'AR':  # ansonsten ist die Tour von uns nicht zu berücksichtigen
        warnungen[idx] = []
        fazit[idx] = ' '

        if (vorgaben_spediteure.loc[:, 'Spediteur'] == z_tar[53:63].strip()).any():  # wenn es den Spediteur aus tar in unseren Spediteursvorgaben gibt
            # starte Index von TARNR erst bei 18 statt 16, da Nr. in blk nur fünfstellig
            tarnr_tarspd[idx] = [z_tar[18:23], z_tar[53:63].strip(), zeilennr_tar]  # erzeugt dict {idx: [Tournr., Spediteur, Zeile]}
        else:  # ansonsten wähle als Vorgaben hier den Defaultwert Andere
            tarnr_tarspd[idx] = [z_tar[18:23], 'Andere', zeilennr_tar]

        # alt (für Variante ohne csv Datei):
        # tarnr_tarspd[idx] = [z_tar[18:23], z_tar[53:63]]  # erzeugt dict {idx: [Tournr., Spediteur]}

        # blkblo_je_tour[idx]=[]
        blkblo_je_tour[idx] = {'Auftragsnr': [], 'Land': []}
        for z_blk in blk_vor:
            if z_blk[426:431] == z_tar[18:23]:  # gleiche Tournr.
                blkblo_je_tour[idx]['Auftragsnr'].append(z_blk[16:23])  # Liste aller Blockauftragsnummern dieser Tour
                blkblo_je_tour[idx]['Land'].append(z_blk[165:167])  # Liste aller Zielländer (der Umschlagspunkte) dieser Tour

                usp = z_blk[54:60].strip()
                if usp == '0':  # Usp 0 ist nichtssagend, hier Auslieferungsreihenfolge der Kundennr. nutzen
                    # auch hinter einer Kundennr. bei Usp 0 können mehrere Auslieferungsnr. stecken - später auch hier Min. wählen
                    usp = 'kd' + (z_blk[46:53].strip())  # Spalte Kunde in BLK
                    # Kennzeichnung kd benötigt, da es z. B. Kundennr. 5 gibt, die NICHT Umschlagspunkt 5 entspricht

                if (z_blk[426:431] + '-' + usp) not in usp_touren:
                    usp_touren[(z_blk[426:431] + '-' + usp)] = [int(z_blk[431:436].strip())]  # Auslieferungsreihenfolge, erstes Element zu diesem Usp
                else:
                    usp_touren[(z_blk[426:431] + '-' + usp)].append(int(z_blk[431:436].strip()))  # append Auslieferungsreihenfolge

        idx += 1
    zeilennr_tar += 1
anzahl_touren = idx

# haben jetzt das dict usp_touren mit allen Auslieferungsreihenfolgenummern zu jedem Umschlagspunkt jeder Tour
# für jeden Umschlagspunkt nur noch das Minimum behalten
for u in usp_touren:
    usp_touren[u] = min(usp_touren[u])

for b in blkblo_blktre_blkk02:  # mit Auslieferungsreihenfolge des dazugehörigen Usps überschreiben
    blkblo_blktre_blkk02[b][0] = usp_touren[blkblo_blktre_blkk02[b][0]]

paletten_je_tour_f = {}
paletten_je_tour_wir = {}

for idx in range(0, anzahl_touren):  # nicht in vorherige for-Schleife integrierbar, weil wir blkblo_je_tour benötigen
    paletten_je_tour_f[idx] = {'n_i': [], 'h_i': [], 'hoehe': [], 'm_i': [], 't_i': [], 'zeile': [], 'row': [],
                               'col': [], 'dock': []}
    paletten_je_tour_wir[idx] = {'n_i': [], 'h_i': [], 'm_i': [], 't_i': [], 'zeile': [], 'row': [], 'col': [],
                                 'dock': []}
    zeilennr_pss = 0
    for z in range(0, len(pss_nach_F)):

        if pss_nach_F[z][25:32] in blkblo_je_tour[idx]['Auftragsnr']:  # wenn BLKNR zur aktuell bearbeiteten Tour gehört
            paletten_je_tour_f[idx]['n_i'].append(int(blkblo_blktre_blkk02[pss_nach_F[z][25:32]][0]))

            paletten_je_tour_f[idx]['hoehe'].append(int(pss_nach_F[z][45:55]))
            if int(pss_nach_F[z][45:55]) > 1070:
                paletten_je_tour_f[idx]['h_i'].append(1)
            else:
                paletten_je_tour_f[idx]['h_i'].append(0)

            paletten_je_tour_f[idx]['m_i'].append(int(pss_nach_F[z][82:94]) / 1000)

            if blkblo_blktre_blkk02[pss_nach_F[z][25:32]][
                1] == 'Y':  # wenn Kennz.Kommission/Klima=Y, da der Kühlstatus nur dann für uns relevant ist
                if int(pss_nach_F[z][110:111]) != 2:  # wollen nur den originalen Eintrag, wenn dieser nicht 2 ist
                    paletten_je_tour_f[idx]['t_i'].append(int(pss_nach_F[z][110:111]))
            else:  # alles andere wird als Trockenware behandelt
                paletten_je_tour_f[idx]['t_i'].append(0)

            paletten_je_tour_f[idx]['zeile'].append(zeilennr_pss)
            paletten_je_tour_f[idx]['dock'].append(pss_nach_F[z][123:133].strip())

            """Ebene 1,3 unten -> %2 = 1
            Ebene 2,4 oben -> %2 = 0
            Y-Koord.: 1 links, 2 mittig, 3 rechts (von der Tür geguckt)
                bei mir unten links = 2
                        unten mittig = 1
                        unten rechts = 0
                        oben links = 5
                        oben mittig = 4
                        oben rechts = 3"""
            ebene = int(pss_nach_F[z][101:103].strip())
            x = int(pss_nach_F[z][103:106].strip())
            if x <= 11:
                paletten_je_tour_f[idx]['col'].append(x - 1)  # -1 weil später auf col indexbasiert zugegriffen wird
            else:
                paletten_je_tour_f[idx]['col'].append(x - 12)
            y = int(pss_nach_F[z][106:109].strip())
            if ebene == 1 or ebene == 3:  # unten
                if y == 1:  # links
                    paletten_je_tour_f[idx]['row'].append(2)
                elif y == 2:  # mittig
                    paletten_je_tour_f[idx]['row'].append(1)
                elif y == 3:  # rechts
                    paletten_je_tour_f[idx]['row'].append(0)
                else:
                    paletten_je_tour_f[idx]['row'].append(0)
            elif ebene == 2 or ebene == 4:  # oben
                if y == 1:  # links
                    paletten_je_tour_f[idx]['row'].append(5)
                elif y == 2:  # mittig
                    paletten_je_tour_f[idx]['row'].append(4)
                elif y == 3:  # rechts
                    paletten_je_tour_f[idx]['row'].append(3)
                else:
                    paletten_je_tour_f[idx]['row'].append(0)
            else:
                paletten_je_tour_f[idx]['row'].append(0)

        if pss_nach_wir[z][25:32] in blkblo_je_tour[idx][
            'Auftragsnr']:  # wenn BLKNR zur aktuell bearbeiteten Tour gehört
            paletten_je_tour_wir[idx]['n_i'].append(int(blkblo_blktre_blkk02[pss_nach_wir[z][25:32]][0]))

            if int(pss_nach_wir[z][45:55]) > 1070:
                paletten_je_tour_wir[idx]['h_i'].append(1)
            else:
                paletten_je_tour_wir[idx]['h_i'].append(0)

            paletten_je_tour_wir[idx]['m_i'].append(int(pss_nach_wir[z][82:94]) / 1000)

            if blkblo_blktre_blkk02[pss_nach_wir[z][25:32]][
                1] == 'Y':  # wenn Kennz.Kommission/Klima=Y, da der Kühlstatus nur dann für uns relevant ist
                if int(pss_nach_wir[z][110:111]) != 2:  # wollen nur den originalen Eintrag, wenn dieser nicht 2 ist
                    paletten_je_tour_wir[idx]['t_i'].append(int(pss_nach_wir[z][110:111]))
            else:  # alles andere wird als Trockenware behandelt
                paletten_je_tour_wir[idx]['t_i'].append(0)

            paletten_je_tour_wir[idx]['zeile'].append(zeilennr_pss)
            paletten_je_tour_wir[idx]['dock'].append(pss_nach_wir[z][123:133].strip())

            ebene = int(pss_nach_wir[z][101:103].strip())
            x = int(pss_nach_wir[z][103:106].strip())
            if x == 0:  # dann hat die Palette keinen Platz mehr - Kennzeichnung für diesen Vergleich mit 'x'
                paletten_je_tour_wir[idx]['col'].append('x')
            elif x <= 11:
                paletten_je_tour_wir[idx]['col'].append(x - 1)  # -1 weil später auf col indexbasiert zugegriffen wird
            else:
                paletten_je_tour_wir[idx]['col'].append(x - 12)
            y = int(pss_nach_wir[z][106:109].strip())
            if ebene == 1 or ebene == 3:  # unten
                if y == 1:  # links
                    paletten_je_tour_wir[idx]['row'].append(2)
                elif y == 2:  # mittig
                    paletten_je_tour_wir[idx]['row'].append(1)
                elif y == 3:  # rechts
                    paletten_je_tour_wir[idx]['row'].append(0)
                else:
                    paletten_je_tour_wir[idx]['row'].append(0)
            elif ebene == 2 or ebene == 4:  # oben
                if y == 1:  # links
                    paletten_je_tour_wir[idx]['row'].append(5)
                elif y == 2:  # mittig
                    paletten_je_tour_wir[idx]['row'].append(4)
                elif y == 3:  # rechts
                    paletten_je_tour_wir[idx]['row'].append(3)
                else:
                    paletten_je_tour_wir[idx]['row'].append(0)
            else:
                paletten_je_tour_wir[idx]['row'].append(0)

        zeilennr_pss += 1



"""
______________________________________________________________________________

Funktionsdefinitionen
______________________________________________________________________________
"""

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
    bewertung = [0 for i in range(8)]
    # erzeugt Liste mit 8 Nullen, 0 bedeutet "alles gut"

    # Hauptskript:
    # ---kein idx, da im Startverf.: Restreihe ist "an der Tür"; außerdem Restreihe_einzeln am Rand, zwei mittig&Rand
    # ---kein idx, da im Startverf.: oben stehen genau Q Paletten
    # ---kein idx, da Start&Verbesserung berücksichtigen: Auslieferungsreihenfolge

    # Unterschied in diesem Vergleichsskript:
    # Indizes 0 bis 6 identisch zu Hauptdatei; idx7 neu für Verstöße Auslieferungsreihenfolge

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
    # = 20, wenn Ladungsschwerpunkt zu nah an der Stirnwand + Abstand zum erlaubten Intervall
    # = 30, wenn Ladungsschwerpunkt zu nah an der Tür + Abstand zum erlaubten Intervall
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

    if lsp_u > ladungsschw:
        bewertung[5] = 20 + round(lsp_u - ladungsschw, 4)  # Ladungsschwerpunkt zu weit an der Stirnwand
    elif lsp_o < ladungsschw:
        bewertung[5] = 30 + round(ladungsschw - lsp_o, 4)  # Ladungsschwerpunkt zu weit an der Tür

    # G idx6: Gewichtsdifferenz
    """gew_rechts=z_sum[0]+z_sum[3]
    gew_links=z_sum[2]+z_sum[5]
    bewertung[6]=abs(gew_rechts-gew_links)  """

    # Gewichtsdifferenz NEU: in %
    # gew_rechts=z_sum[0]+z_sum[3]
    gew_mitte = z_sum[1] + z_sum[4]
    gew_links = z_sum[2] + z_sum[5]

    prozent_links = (gew_links + gew_mitte / 2) / sum(z_sum) * 100
    bewertung[6] = round(abs(50 - prozent_links) * 2, 4)

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
    hpaletten = tabelle_.loc[tabelle_['h_i'] > 0].reset_index(inplace=False, drop=True)

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
    bewertung[1] = round(bewertung[1], 2)

    # R idx2: kühl-trocken-Trennung auch nach Austausch berücksichtigt
    kuehlpaletten = tabelle_.loc[tabelle_['t_i'] > 0].reset_index(inplace=False, drop=True)

    for tpal in range(kuehlpaletten.shape[0]):  # für jede Kühlpalette einzeln
        tpal_fehler = False
        try:
            col_tpal = int(list(lkwplan_.columns[lkwplan_.isin([kuehlpaletten.loc[tpal, 'i']]).any()])[0])
            # col_tpal ist hier der Reihenname (1-11) als Zahl dargestellt
        except:
            bewertung[2] += 0.01  # als Kennzeichen, dass Kühlpalette nicht mehr eingeplant werden konnte
        else:
            # alle n in der nächsthöheren Reihe müssen kleiner sein ODER gleich wenn t auch 1 ist
            tabelle_vgl = tabelle_.set_index('i', inplace=False, drop=False)
            if col_tpal <= 10:
                for jedes in lkwplan_.loc[:, str(col_tpal + 1)]:
                    if jedes != 'x' and jedes != 'o':

                        if tabelle_vgl.loc[jedes, 'n_i'] > tabelle_vgl.loc[kuehlpaletten.loc[tpal, 'i'], 'n_i']:
                            tpal_fehler = True

                        elif tabelle_vgl.loc[jedes, 'n_i'] == tabelle_vgl.loc[kuehlpaletten.loc[tpal, 'i'], 'n_i']:
                            if tabelle_vgl.loc[jedes, 't_i'] < 1:
                                tpal_fehler = True
                if tpal_fehler:
                    bewertung[
                        2] += 1  # für jede Kühlpal um 1 hochzählen, bei der die n bzw. t der nächsthöheren Reihe nicht passen
    bewertung[2] = round(bewertung[2], 2)

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

    # --------------------------------------------------------------------------------------
    # neu für diesen Vergleich:
    n_verstoesse = 0
    # Plan mit n-Werten füllen
    lkwplan_n_werte = pd.DataFrame(lkwplan_.copy(deep=True))

    for col in range(0, 11):
        for row in range(0, 6):
            if lkwplan_.iloc[row, col] != 'o':
                lkwplan_n_werte.iloc[row, col] = tabelle_.loc[lkwplan_.iloc[row, col], 'n_i']
                # tabelle_.loc[tabelle_['i+h']==lkwplan_.iloc[row, col]]['n_i']
            else:
                lkwplan_n_werte.iloc[row, col] = 'x'  # setze zur Vereinfachung auch mögliche 'o' auf 'x'

    print('Auslieferungsnummern:\n', lkwplan_n_werte)

    for c in range(2, 12):
        c_vorher = lkwplan_n_werte.loc[:, str(c - 1)]  # .values.tolist()
        c_aktuell = lkwplan_n_werte.loc[:, str(c)]  # .values.tolist()

        if (c_vorher == 'x').all() or (c_aktuell == 'x').all():
            continue

        if max(element for element in c_aktuell if element != 'x') > min(
                element for element in c_vorher if element != 'x'):
            if n_verstoesse == 0:
                print('Auslieferungsreihenfolge verletzt:')
            print(f'\tNummer in Reihe {c - 1} kleiner als in Reihe {c}')
            n_verstoesse += 1

    bewertung[7] = n_verstoesse

    return bewertung



"""
______________________________________________________________________________

Ende Funktionsdefinitionen
jetzt kann über die Touren iteriert und Lösungen verglichen werden
______________________________________________________________________________
"""

for tour_idx in range(0, anzahl_touren):
    # for tour_idx in range(3,4):
    # for tour_idx in range(12,13):
    # for tour_idx in range(14,15):

    # Spediteur Thomsen ist dem Fraunhofer-Tool vermutlich nicht bekannt, da es für diesen fehlerhafte Lösungen erzeugt.
    # -> wird hier deshalb ausgeschlossen
    if tarnr_tarspd[tour_idx][1] == 'THOMSEN':
        print(f'Tour {tarnr_tarspd[tour_idx][0]}: Spediteur Thomsen -> wird nicht gewertet')
        continue

    # erzeuge ein Dataframe mit allen relevanten Infos zu dieser Tour - Vorteil: erleichtert alle späteren Schritte
    tabelle = pd.DataFrame({'i': np.arange(len(paletten_je_tour_f[tour_idx]['n_i'])),
                            'i+h': np.arange(len(paletten_je_tour_f[tour_idx]['n_i'])),
                            'n_i': paletten_je_tour_f[tour_idx]['n_i'],
                            'h_i': paletten_je_tour_f[tour_idx]['h_i'],
                            'hoehe': paletten_je_tour_f[tour_idx]['hoehe'],
                            'm_i': paletten_je_tour_f[tour_idx]['m_i'],
                            't_i': paletten_je_tour_f[tour_idx]['t_i'],
                            'zeile': paletten_je_tour_f[tour_idx]['zeile'],
                            'fr_row': paletten_je_tour_f[tour_idx]['row'],
                            'fr_col': paletten_je_tour_f[tour_idx]['col'],
                            'fr_dock': paletten_je_tour_f[tour_idx]['dock'],
                            'wir_row': paletten_je_tour_wir[tour_idx]['row'],
                            'wir_col': paletten_je_tour_wir[tour_idx]['col'],
                            'wir_dock': paletten_je_tour_wir[tour_idx]['dock']})

    for i in range(0, len(paletten_je_tour_f[tour_idx]['n_i'])):
        if tabelle.loc[i, 'h_i'] == 1:
            tabelle.loc[i, 'i+h'] = str(i) + 'h'

    # Ländervorgaben - individuell je Tour prüfen, da Touren verschiedene Zielländer haben können
    tour_laender = set(blkblo_je_tour[tour_idx]['Land'])  # eine Menge (set) erhält jedes Element nur einmal

    if len(tour_laender) == 1:
        m_HA_max_ges = laendervorgaben.loc[
            min(tour_laender), 'Achslast Sattelzug Hinten']  # min gibt hier das eine Element der Menge zurück
        m_t_max_ges = laendervorgaben.loc[min(tour_laender), 'Auflieger Dreiachsig']
    else:
        m_HA_max_ges = laendervorgaben.loc[
            min(tour_laender), 'Achslast Sattelzug Hinten']  # min gibt hier ein Element der Menge zurück
        m_t_max_ges = laendervorgaben.loc[min(tour_laender), 'Auflieger Dreiachsig']
        for ld in tour_laender:
            if ld != min(tour_laender):
                m_HA_v2 = laendervorgaben.loc[ld, 'Achslast Sattelzug Hinten']
                m_t_v2 = laendervorgaben.loc[ld, 'Auflieger Dreiachsig']
                if m_HA_v2 < m_HA_max_ges:
                    m_HA_max_ges = m_HA_v2
                if m_t_v2 < m_t_max_ges:
                    m_t_max_ges = m_t_v2

    m_kp_max_vor_m_trailer = (m_HA_max_ges - last_HA_durch_m_tractor) / (1 - sattelvorm_tractor / radstand_tractor)
    m_kp_max = m_kp_max_vor_m_trailer - last_kp_durch_m_trailer
    m_t_max = m_t_max_ges - last_t_durch_m_trailer

    # tourenabhängige Werte
    m_lad = tabelle['m_i'].sum()  # Einheit kg

    # Untergrenze:
    lsp_u = radstand_trailer * (1 - m_kp_max / m_lad) + abst_kp_stw_trailer

    # Obergrenze:    -> Annahme: mindestens 25% des aktuellen Gesamtgewichts auf HA der Zugmaschine
    anteil_mKP_HA = 1 - sattelvorm_tractor / radstand_tractor  # KP-Last zu ...% auf der HA der Zugmaschine:
    lsp_o = min(m_t_max / m_lad * radstand_trailer + abst_kp_stw_trailer,
                abst_kp_stw_trailer + radstand_trailer / m_lad * (0.7025 * (
                            m_lad + m_trailer) - 0.2975 * m_tractor + 1 / anteil_mKP_HA * last_HA_durch_m_tractor))

    # print(f'Untergrenze (in m ab Stirnwand): {lsp_u:.3f} \nObergrenze (in m ab Stirnwand): {lsp_o:.3f}')

    anz_pal = max(tabelle['i']) + 1  # da Tabelle nullbasiert
    oben = max(anz_pal - 33, 0)

    platzhalter_hpal = math.ceil(
        sum(tabelle['h_i']) / 3) * 3  # Hochpaletten versperren in oberer Ebene MINDESTENS so viele Plätze

    # eine Tour ist problematisch bzw. so nicht zu verplanen, wenn
    if anz_pal > vorgaben_spediteure.loc[tarnr_tarspd[tour_idx][
                                             1], 'Gesamtkapazitaet']:  # Spediteursvorgaben zur maximalen Palettenanz. (entweder Doppelstock=66 oder nicht=33) überschritten?
        warnungen[tour_idx].append('Zu viele Paletten für diesen Spediteur eingeplant!')

    elif m_lad > vorgaben_spediteure.loc[
        tarnr_tarspd[tour_idx][1], 'Zulaessige Nutzlast']:  # Spediteursvorgaben zur maximalen Nutzlast überschritten?
        warnungen[tour_idx].append(
            f'Max. zulässige Nutzlast des Spediteurs von {vorgaben_spediteure.loc[tarnr_tarspd[tour_idx][1], "Nutzlast"]} kg um {m_lad - vorgaben_spediteure.loc[tarnr_tarspd[tour_idx][1], "Nutzlast"]} überschritten!')

    elif anz_pal + platzhalter_hpal > 66 and vorgaben_spediteure.loc[
        tarnr_tarspd[tour_idx][1], 'Gesamtkapazitaet'] == 66:
        warnungen[tour_idx].append(
            'Mitnahme aller Paletten nicht möglich - Reihen über Hochpaletten müssen frei bleiben')


    """
    ______________________________________________________________________________

    Ende Vorarbeit
    -> weiterhin in der Schleife for tour_idx
    ______________________________________________________________________________
    """

    lkwplan_fr = pd.DataFrame({str(reihe_k): ['o' for o in range(6)] for reihe_k in range(1, 12)})
    lkwplan_wir = pd.DataFrame({str(reihe_k): ['o' for o in range(6)] for reihe_k in range(1, 12)})
    lkwplan_fr_print = pd.DataFrame({str(reihe_k): ['o' for o in range(6)] for reihe_k in range(1, 12)})
    lkwplan_wir_print = pd.DataFrame({str(reihe_k): ['o' for o in range(6)] for reihe_k in range(1, 12)})

    for i in tabelle.index:  # Index und 'i' stimmen in dieser Tabelle überein

        if tabelle.loc[i, 'fr_dock'] != 'kein Platz':
            lkwplan_fr.iloc[tabelle.loc[i, 'fr_row'], tabelle.loc[i, 'fr_col']] = i
            lkwplan_fr_print.iloc[tabelle.loc[i, 'fr_row'], tabelle.loc[i, 'fr_col']] = tabelle.loc[i, 'i+h']
        if tabelle.loc[i, 'wir_dock'] != 'kein Platz':
            lkwplan_wir.iloc[tabelle.loc[i, 'wir_row'], tabelle.loc[i, 'wir_col']] = i
            lkwplan_wir_print.iloc[tabelle.loc[i, 'wir_row'], tabelle.loc[i, 'wir_col']] = tabelle.loc[i, 'i+h']

    print(f'\nTour {tarnr_tarspd[tour_idx][0]}:')
    print(lkwplan_fr_print)
    print(f'F: {plan_bewertung(tabelle, lkwplan_fr)}')
    print(lkwplan_wir_print)
    print(f'W: {plan_bewertung(tabelle, lkwplan_wir)}\n\n')

    # print(tabelle.to_string())