import tkinter as tk
root = tk.Tk()
frame = tk.Frame(master=root, width=200, height=100)
frame.pack()
label = tk.Label(master=frame, text="hello world!")
label.place(x=50, y=30)


root.mainloop()
