import tkinter as tk
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

root = tk.Tk()
root.title("DnD NPC Generator")

def add_to_list(event=None):
    text = entry.get()
    if text:
        text_list.insert(tk.END, text)
        entry.delete(0, tk.END)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

frame = tk.Frame(root)
frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

frame.columnconfigure(0, weight=1)
frame.rowconfigure(1, weight=1)

entry = tk.Entry(frame)
entry.grid(row=0, column=0, sticky="ew")

entry.bind("<Return>", add_to_list)

entry_btn = tk.Button(frame, text="Add", command=add_to_list)
entry_btn.grid(row=0, column=1)

text_list = tk.Listbox(frame)
text_list.grid(row=1, column=0, columnspan=2, sticky="nsew")

#label = tk.Label(master=frame, text="hello world!")
#label.place(x=50, y=30)


root.mainloop()
