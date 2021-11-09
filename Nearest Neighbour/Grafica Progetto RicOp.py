import tkinter as tk
import sys


root = tk.Tk()

root.geometry("500x500")
root.title("Grafica progetto RicOp")
root.configure(bg = "Black")

def scelta_soluzione():
    root.destroy()
    window = tk.Tk()
    #window.attributes('-fullscreen', True)
    window.title("Scelta algoritmo")
    window.configure(bg = "Black")

    def ciao1():
        import NeighborhoodBasedComplete
        CostoNB_STR = str(NeighborhoodBasedComplete.Costo)
        cost1 = tk.Label(window, text = "Il costo per percorrere il tragitto \n con l'algoritmo Neighborhood Based è...\n" + CostoNB_STR, bg = "Black", fg = "White")
        cost1.grid(row=4, column = 1, columnspan=3)
         
        
    def ciao2():
        pass

    def ciao3():
        pass
    
    Neighborhood = tk.Button(window, text = "NEIGHBORHOOD BASED", bg = "Red", fg = "Black",width=30, height=5, command = ciao1)
    Neighborhood.grid(row=1, column=1)
    Cheapest = tk.Button(window, text = "CHEAPEST INSERTION", bg = "Yellow", fg = "Black", width=30, height=5, command = ciao2)
    Cheapest.grid(row = 1, column = 2)
    Christofides = tk.Button(window, text = "CHRISTOFIDES", bg = "Green", fg = "Black",width=30, height=5, command = ciao3)
    Christofides.grid(row = 2, column = 1)
    Esci = tk.Button(window, text = "EXIT", bg = "Grey",width=30, height=5, fg = "Black", command = sys.exit)
    Esci.grid(row=2, column=2)
start = tk.Button(root, text = "START", bg = "Green", fg = "Black", width=30, height=5, command = scelta_soluzione)
start.grid(row=1, column=1)
back = tk.Button(root, text = "EXIT", bg = "Red", fg = "White",width=30, height=5, command = sys.exit)
back.grid(row=1, column=2)


root.mainloop()