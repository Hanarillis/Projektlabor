import tkinter as tk
from tkinter import ttk, messagebox
from openai import OpenAI
import os
import json  

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RACES = [
    "Human",
    "Elf",
    "Dwarf",
    "Halfling",
    "Gnome",
    "Half-Elf",
    "Half-Orc",
    "Tiefling",
    "Dragonborn"
]

CLASS_TO_SUBCLASSES = {
    "Barbarian": ["Path of the Berserker", "Path of the Totem Warrior"],
    "Bard": ["College of Lore", "College of Valor"],
    "Cleric": ["Life Domain", "Light Domain", "Trickery Domain"],
    "Druid": ["Circle of the Land", "Circle of the Moon"],
    "Fighter": ["Champion", "Battle Master", "Eldritch Knight"],
    "Monk": ["Way of the Open Hand", "Way of Shadow"],
    "Paladin": ["Oath of Devotion", "Oath of Vengeance"],
    "Ranger": ["Hunter", "Beast Master"],
    "Rogue": ["Thief", "Assassin", "Arcane Trickster"],
    "Sorcerer": ["Draconic Bloodline", "Wild Magic"],
    "Warlock": ["Fiend", "Archfey", "Great Old One", "Hexblade"],
    "Wizard": ["Evocation", "Illusion", "Necromancy", "Abjuration"],
}

CLASSES = list(CLASS_TO_SUBCLASSES.keys())


def generate_statblock_from_ai(race, char_class, subclass, level):

    if not subclass:
        subclass_text = "no specific subclass"
    else:
        subclass_text = subclass

    json_schema = """
{
  "name": "string",
  "race": "string",
  "class": "string",
  "subclass": "string",
  "level": 0,
  "hp": 0,
  "ac": 0,
  "speed": "string",
  "abilities": {
    "STR": 0,
    "DEX": 0,
    "CON": 0,
    "INT": 0,
    "WIS": 0,
    "CHA": 0
  },
  "saving_throws": ["string"],
  "skills": ["string"],
  "attacks": ["string"],
  "spells": ["string"],
  "features": ["string"]
}
"""

    user_prompt = f"""
You are a Dungeons & Dragons 5e / 2024 NPC generator.

Create a single NPC stat block based on:

- Race: {race}
- Class: {char_class}
- Subclass: {subclass_text}
- Level: {level}

Requirements:
- Fill out all fields in the following JSON structure.
- Make the numbers and choices consistent with the concept (no nonsense values).
- Keep lists (skills, attacks, spells, features) reasonably short but useful.

Return ONLY valid JSON, with this exact structure and keys:

{json_schema}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful Dungeons and Dragons 2024 Dungeon Master assistant. "
                           "You always respond with valid JSON when asked to."
            },
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )

    content = response.choices[0].message.content.strip()

    try:
        data = json.loads(content)
        return data  
    except json.JSONDecodeError:
        return content  


def format_statblock(data):
    
    if not isinstance(data, dict):
        return str(data)

    lines = []

    name = data.get("name", "Unnamed")
    race = data.get("race", "")
    char_class = data.get("class", "")
    subclass = data.get("subclass", "")
    level = data.get("level", "?")

    header = f"{name} (Level {level} {race} {char_class})"
    lines.append(header)
    if subclass and subclass.lower() != "none":
        lines.append(f"Subclass: {subclass}")
    lines.append("-" * len(header))

    hp = data.get("hp", "?")
    ac = data.get("ac", "?")
    speed = data.get("speed", "?")
    lines.append(f"HP: {hp}   AC: {ac}   Speed: {speed}")
    lines.append("")

    abilities = data.get("abilities", {})
    if abilities:
        lines.append("Abilities")
        lines.append(
            "  STR: {STR:>2}   DEX: {DEX:>2}   CON: {CON:>2}".format(
                STR=abilities.get("STR", "?"),
                DEX=abilities.get("DEX", "?"),
                CON=abilities.get("CON", "?"),
            )
        )
        lines.append(
            "  INT: {INT:>2}   WIS: {WIS:>2}   CHA: {CHA:>2}".format(
                INT=abilities.get("INT", "?"),
                WIS=abilities.get("WIS", "?"),
                CHA=abilities.get("CHA", "?"),
            )
        )
        lines.append("")

    saving_throws = data.get("saving_throws", [])
    if saving_throws:
        lines.append("Saving Throws:")
        lines.append("  " + ", ".join(saving_throws))
        lines.append("")

    skills = data.get("skills", [])
    if skills:
        lines.append("Skills:")
        for s in skills:
            lines.append("  - " + s)
        lines.append("")

    attacks = data.get("attacks", [])
    if attacks:
        lines.append("Attacks:")
        for a in attacks:
            lines.append("  - " + a)
        lines.append("")

    spells = data.get("spells", [])
    if spells:
        lines.append("Spells:")
        for sp in spells:
            lines.append("  - " + sp)
        lines.append("")

    features = data.get("features", [])
    if features:
        lines.append("Features:")
        for f in features:
            lines.append("  - " + f)
        lines.append("")

    return "\n".join(lines)


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DnD NPC Generator")

        self.columnconfigure(0, weight=1)

        input_frame = ttk.Frame(self, padding=10)
        input_frame.grid(row=0, column=0, sticky="nsew")
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Race (faj):").grid(
            row=0, column=0, sticky="w", padx=2, pady=2
        )
        self.race_var = tk.StringVar()
        self.race_combo = ttk.Combobox(
            input_frame,
            textvariable=self.race_var,
            values=RACES,
            state="readonly"
        )
        self.race_combo.grid(
            row=0, column=1, sticky="ew", padx=2, pady=2
        )

        ttk.Label(input_frame, text="Class:").grid(
            row=1, column=0, sticky="w", padx=2, pady=2
        )
        self.class_var = tk.StringVar()
        self.class_combo = ttk.Combobox(
            input_frame,
            textvariable=self.class_var,
            values=CLASSES,
            state="readonly"
        )
        self.class_combo.grid(
            row=1, column=1, sticky="ew", padx=2, pady=2
        )
        self.class_combo.bind("<<ComboboxSelected>>", self.on_class_changed)

        ttk.Label(input_frame, text="Subclass (opcionális):").grid(
            row=2, column=0, sticky="w", padx=2, pady=2
        )
        self.subclass_var = tk.StringVar()
        self.subclass_combo = ttk.Combobox(
            input_frame,
            textvariable=self.subclass_var,
            values=[],
            state="readonly"
        )
        self.subclass_combo.grid(
            row=2, column=1, sticky="ew", padx=2, pady=2
        )

        ttk.Label(input_frame, text="Level (szint):").grid(
            row=3, column=0, sticky="w", padx=2, pady=2
        )
        self.level_var = tk.StringVar()
        self.level_combo = ttk.Combobox(
            input_frame,
            textvariable=self.level_var,
            values=[str(i) for i in range(1, 21)],
            state="readonly"
        )
        self.level_combo.grid(
            row=3, column=1, sticky="ew", padx=2, pady=2
        )
        self.level_combo.current(0)

        generate_button = ttk.Button(
            input_frame,
            text="Generate statblock",
            command=self.on_generate
        )
        generate_button.grid(row=4, column=0, columnspan=2, pady=10)

        output_frame = ttk.Frame(self, padding=10)
        output_frame.grid(row=1, column=0, sticky="nsew")
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(1, weight=1)

        ttk.Label(output_frame, text="Eredmény:").grid(
            row=0, column=0, sticky="w"
        )

        self.output_text = tk.Text(
            output_frame,
            width=60,
            height=20,
            state="disabled"
        )
        self.output_text.grid(row=1, column=0, sticky="nsew")

    def on_class_changed(self, event=None):
        selected_class = self.class_var.get()
        subclasses = CLASS_TO_SUBCLASSES.get(selected_class, [])
        self.subclass_combo["values"] = subclasses
        self.subclass_var.set("")

    def on_generate(self):
        race = self.race_var.get().strip()
        char_class = self.class_var.get().strip()
        subclass = self.subclass_var.get().strip()
        level_str = self.level_var.get().strip()

        if not race or not char_class or not level_str:
            messagebox.showerror(
                "Hiba",
                "Kérlek add meg a fajt, class-t és szintet!"
            )
            return

        try:
            level = int(level_str)
        except ValueError:
            messagebox.showerror(
                "Hiba",
                "A szintnek egész számnak kell lennie!"
            )
            return

        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "AI gondolkodik, kérlek várj...\n")
        self.output_text.config(state="disabled")
        self.update_idletasks()

        try:
            data = generate_statblock_from_ai(
                race, char_class, subclass, level
            )
            formatted = format_statblock(data)
        except Exception as e:
            messagebox.showerror(
                "Hiba",
                f"Hiba történt az AI hívás vagy formázás során:\n{e}"
            )
            return

        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, formatted)
        self.output_text.config(state="disabled")


def main():
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
