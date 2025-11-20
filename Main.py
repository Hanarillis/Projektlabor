import tkinter as tk
from tkinter import ttk
from openai import OpenAI
import os

'''client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-4.1-mini", 
    messages= [
        {"role":"system", "content":"You are a Dungeons and Dragons 2024 Dungeon Master"}, 
        {"role":"user", "content": "Generate me a lvl1 wizard statblock" }
    ], 
    temperature=0.7
)
print(response.choices[0].message.content)'''

def main():
    app = Application()
    app.mainloop()

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DnD NPC Generator")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        frame = Inputform(self)
        frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        frame2 = Inputform(self)
        frame2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        

class Inputform(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.entry = tk.Entry(self)
        self.entry.grid(row=0, column=0, sticky="ew")

        self.entry.bind("<Return>", self.add_to_list)

        self.entry_btn = tk.Button(self, text="Add", command=self.add_to_list)
        self.entry_btn.grid(row=0, column=1)

        self.entry_btn2 = tk.Button(self, text="Clear", command=self.clear_list)
        self.entry_btn2.grid(row=0, column=2)

        self.text_list = tk.Listbox(self)
        self.text_list.grid(row=1, column=0, columnspan=3, sticky="nsew")
    
    def add_to_list(self, event=None):
        text = self.entry.get()
        if text:
            self.text_list.insert(tk.END, text)
            self.entry.delete(0, tk.END)    

    def clear_list(self):
        self.text_list.delete(0, tk.END) 


if __name__ == "__main__": 
    main()
    
