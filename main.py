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

# class App():
#    def __init__(self):
#        self.root = tkinter.Tk()
#        button = tkinter.Button(self.root, text = 'root quit', command=self.quit)
#        button.pack()
#        self.root.mainloop()
#
#    def quit(self):
#        self.root.destroy()
#
# app = App()

# #https://www.youtube.com/watch?v=0WRMYdOwHYE
def start():
    tasks = 10 #In unserem Beispiel könnten das die Rechenoperationen sein, welche wir zu der Zeit durchlaufen
    x = 0 #x stellt die Rechenoperation dar, welche gerade ausgeführt wird
    while (x < tasks):
        time.sleep(1)
        bar['value'] += 10 #die zehn sind hier ein Beispiel, wenn es 5 Operationen wären bspw 20
        x+=1 #inkrementieren nach jeder ausgeführten Rechenoperation
        percent.set(str((x/tasks)*100)+"%")
        window.update_idletasks()

def quit():
    window.destroy()

window = Tk()

percent = StringVar()
bar = Progressbar(window,orient=HORIZONTAL,length=300)
bar.pack(pady=10)

percentlabel = Label(window,textvariable=percent).pack()
button = Button(window,text="Download",command=start).pack()
button2 = Button(window,text="Close",command=quit).pack()

window.mainloop()


#for i in tqdm(range(100), desc="Loading...", ascii=False,ncols=75):
    #time.sleep(0.01)

#print("Complete")

#https://derlinuxwikinger.de/ladebalken-mit-python-tkinter/ -> PROGRESSBAR
#https://stackoverflow.com/questions/50815547/simple-loading-screen-in-python-tkinter -> EINBETTUNG IN LAUFZEIT -> RECHENZEIT



# window = Tk()
# window.title("Progressbar")
#
# ### Window size
# window_width = 300
# window_height = 50
#
# ### Screen dimension, center point and positioning of the window
# screen_width = window.winfo_screenwidth()
# screen_height = window.winfo_screenheight()
# center_x = int(screen_width/4 - window_width / 2)
# center_y = int(screen_height/2 - window_height / 2)
# window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
#
# ### Klasse 'progressbar'
# class progressbar():
#   def start_progressbar(self):
#     ### Erstellung des Ladefensters
#     global loadingWindow
#     loadingWindow = Toplevel(window)
#
#     ### Position und Kosmetik
#     loadingWindow.geometry(f'{300}x{95}+{center_x}+{center_y}')
#     loadingWindow.overrideredirect(True)
#     loadingWindow.lift()
#     loadingWindow_frame = Frame(loadingWindow, highlightbackground="black", highlightthickness=2, bg='white')
#     loadingWindow_frame.pack()
#
#     ### Ladeanimation
#     pb = ttk.Progressbar(loadingWindow_frame, orient='horizontal', mode='indeterminate', length=280)
#     pb.pack(padx=10, pady=10)
#     loadingWindow_lbl = Label(loadingWindow_frame, text="Prozess gestartet.\nBitte warten ...", font=("Arial", 15), bg='white')
#     loadingWindow_lbl.pack()
#
#     ### Start progressbar
#     threading.Thread(target=pb.start()).start()
#
#   def close_progressbar(self):
#     loadingWindow.destroy()
#
#   def check_process(self):
#     z = proc.is_alive()
#     while z is True:
#       z = proc.is_alive()
#     self.close_progressbar()
#
#   def check_process_thread(self):
#     threading.Thread(target=self.check_process).start()
#
# ### Klasse 'action_timer'
# class action_timer():
#   def action_timer_command(self):
#     time.sleep(5)
#
#   def action_timer_thread(self):
#     global proc
#     proc = threading.Thread(target=self.action_timer_command)
#     proc.start()


#progressbar_btn = Button(window, text="Prozess starten", bg='white', command=lambda: [progressbar().start_progressbar(), action_timer().action_timer_thread(), progressbar().check_process_thread()])
#progressbar_btn.pack()

#window.mainloop()

#print(myfunc(1,3))
#print("Pimm")
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

#später in GUS-Schnittstelle https://blogs.sap.com/2020/06/09/connecting-python-with-sap-step-by-step-guide/
#https://www.heise.de/ratgeber/Programmieren-mit-Python-Schnittstellen-entwickeln-mit-Pycharm-und-FastAPI-4940182.html
#https://towardsdatascience.com/the-right-way-to-build-an-api-with-python-cd08ab285f8f