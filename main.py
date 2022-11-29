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




