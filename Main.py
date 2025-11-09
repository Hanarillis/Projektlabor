import tkinter as tk
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-4.1-mini", 
    messages= [
        {"role":"system", "content":"You are a Dungeons and Dragons 2024 Dungeon Master"}, 
        {"role":"user", "content": "Generate me a lvl1 wizard statblock" }
    ], 
    temperature=0.7
)
print(response.choices[0].message.content)

root = tk.Tk()
frame = tk.Frame(master=root, width=200, height=100)
frame.pack()
label = tk.Label(master=frame, text="hello world!")
label.place(x=50, y=30)


root.mainloop()
