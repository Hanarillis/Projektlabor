import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkfont
from openai import OpenAI
import os
import json
import random

THINKING_MESSAGE = "AI is thinking, please wait..."
MODEL_NAME = "gpt-4.1-mini"

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

JSON_SCHEMA = """
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

api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None


def generate_statblock_from_ai(
    race,
    char_class,
    subclass,
    level,
    include_spells=True,
    role_description=""
):
    subclass_text = subclass or "no specific subclass"

    spells_requirement = (
        "Include appropriate spell lists for the NPC.\n"
        if include_spells
        else "Do NOT include spells. Focus on non-magical or simple features.\n"
    )

    role_text = ""
    if role_description:
        role_text = (
            f'The NPC\'s role / flavor description from the user: '
            f'"{role_description}".\n'
        )

    user_prompt = f"""
You are a Dungeons & Dragons 5e / 2024 NPC generator.

Create a single NPC stat block based on:

- Race: {race}
- Class: {char_class}
- Subclass: {subclass_text}
- Level: {level}

{role_text}

Requirements:
- Fill out all fields in the following JSON structure.
- Make the numbers and choices consistent with the concept (no nonsense values).
- Keep lists (skills, attacks, spells, features) reasonably short but useful.
- {spells_requirement}

VERY IMPORTANT:
- Return ONLY valid JSON.
- Do NOT wrap it in markdown.
- Do NOT include ``` or ```json fences.
- The response must start with '{{' and end with '}}'.

JSON structure:

{JSON_SCHEMA}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful Dungeons and Dragons 2024 Dungeon Master assistant. "
                    "You always respond with valid JSON only, without markdown fences."
                )
            },
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```"):
        lines = content.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines).strip()

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
    if subclass and str(subclass).lower() != "none":
        lines.append(f"Subclass: {subclass}")
    lines.append("-" * len(header))

    hp = data.get("hp", "?")
    ac = data.get("ac", "?")
    speed = data.get("speed", "?")
    lines.append(f"HP: {hp}   AC: {ac}   Speed: {speed}")
    lines.append("")

    abilities = data.get("abilities", {})

    def _ability_val(key):
        val = abilities.get(key, "?")
        if isinstance(val, dict):
            score = val.get("score")
            if score is not None:
                return str(score)
            return str(val)
        return str(val)

    if isinstance(abilities, dict) and abilities:
        lines.append("Abilities")
        lines.append(
            "  STR: {STR:>2}   DEX: {DEX:>2}   CON: {CON:>2}".format(
                STR=_ability_val("STR"),
                DEX=_ability_val("DEX"),
                CON=_ability_val("CON"),
            )
        )
        lines.append(
            "  INT: {INT:>2}   WIS: {WIS:>2}   CHA: {CHA:>2}".format(
                INT=_ability_val("INT"),
                WIS=_ability_val("WIS"),
                CHA=_ability_val("CHA"),
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
            lines.append("  - " + str(s))
        lines.append("")

    attacks = data.get("attacks", [])
    if attacks:
        lines.append("Attacks:")
        for a in attacks:
            lines.append("  - " + str(a))
        lines.append("")

    spells = data.get("spells", [])
    if spells:
        lines.append("Spells:")
        for sp in spells:
            lines.append("  - " + str(sp))
        lines.append("")

    features = data.get("features", [])
    if features:
        lines.append("Features:")
        for f in features:
            lines.append("  - " + str(f))
        lines.append("")

    return "\n".join(lines)


def generate_spell_summaries(spell_list):
    if not spell_list:
        return {}

    spells_clean = [str(s) for s in spell_list if str(s).strip()]
    if not spells_clean:
        return {}

    prompt = f"""
You are summarizing Dungeons & Dragons spells in short mechanical form.

For each spell, write ONE very short rules-like line in English including:
- whether it uses an attack roll or a saving throw
- if a saving throw: which ability (Dex, Wis, etc.), vs. the caster's spell save DC
- what damage dice it deals and what damage type (e.g. 2d6 fire)
- any important extra effect (for example: frightened, prone, restrained, half damage on success, etc.)

Do NOT explain full rules. Be compact and game-oriented.

Return ONLY valid JSON in this exact format:
{
  "spell_summaries": {
    "Spell Name": "short mechanical summary",
    "Other Spell": "short mechanical summary"
  }
}

Spells to summarize:
{spells_clean}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You always return ONLY valid JSON in the requested format."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    text = response.choices[0].message.content.strip()

    try:
        data = json.loads(text)
        summaries = data.get("spell_summaries", {})
        return {str(k): str(v) for k, v in summaries.items()}
    except Exception:
        return {}


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DnD NPC Generator")

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.title_font = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        self.section_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.mono_font = tkfont.Font(family="Consolas", size=10)

        self.geometry("800x650")
        self.minsize(700, 550)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        self.theme_var = tk.StringVar(value="dark")
        menubar = tk.Menu(self)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_radiobutton(
            label="Light",
            variable=self.theme_var,
            value="light",
            command=self.on_theme_changed
        )
        view_menu.add_radiobutton(
            label="Dark",
            variable=self.theme_var,
            value="dark",
            command=self.on_theme_changed
        )
        menubar.add_cascade(label="View", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.on_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

        self.title_frame = ttk.Frame(self, style="AppTitle.TFrame")
        self.title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))
        self.title_frame.columnconfigure(0, weight=1)

        self.title_label = ttk.Label(
            self.title_frame,
            text="DnD NPC Generator",
            font=self.title_font,
            style="AppTitle.TLabel"
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        sep = ttk.Separator(self, orient="horizontal")
        sep.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 6))

        self.input_frame = ttk.Frame(self, padding=10, style="App.TFrame")
        self.input_frame.grid(row=2, column=0, sticky="nsew", padx=10)
        self.input_frame.columnconfigure(1, weight=1)

        self.race_label = ttk.Label(
            self.input_frame,
            text="Race:",
            style="AppInner.TLabel"
        )
        self.race_label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.race_var = tk.StringVar()
        self.race_combo = ttk.Combobox(
            self.input_frame,
            textvariable=self.race_var,
            values=RACES,
            state="readonly",
            style="App.TCombobox"
        )
        self.race_combo.grid(row=0, column=1, sticky="ew", padx=2, pady=2)

        self.class_label = ttk.Label(
            self.input_frame,
            text="Class:",
            style="AppInner.TLabel"
        )
        self.class_label.grid(row=1, column=0, sticky="w", padx=2, pady=2)
        self.class_var = tk.StringVar()
        self.class_combo = ttk.Combobox(
            self.input_frame,
            textvariable=self.class_var,
            values=CLASSES,
            state="readonly",
            style="App.TCombobox"
        )
        self.class_combo.grid(row=1, column=1, sticky="ew", padx=2, pady=2)
        self.class_combo.bind("<<ComboboxSelected>>", self.on_class_changed)

        self.subclass_label = ttk.Label(
            self.input_frame,
            text="Subclass (optional):",
            style="AppInner.TLabel"
        )
        self.subclass_label.grid(row=2, column=0, sticky="w", padx=2, pady=2)
        self.subclass_var = tk.StringVar()
        self.subclass_combo = ttk.Combobox(
            self.input_frame,
            textvariable=self.subclass_var,
            values=[],
            state="readonly",
            style="App.TCombobox"
        )
        self.subclass_combo.grid(row=2, column=1, sticky="ew", padx=2, pady=2)

        self.level_label = ttk.Label(
            self.input_frame,
            text="Level:",
            style="AppInner.TLabel"
        )
        self.level_label.grid(row=3, column=0, sticky="w", padx=2, pady=2)

        self.level_var = tk.StringVar(value="1")

        self.level_spin = ttk.Spinbox(
            self.input_frame,
            from_=1,
            to=20,
            textvariable=self.level_var,
            wrap=True,
            width=5,
            style="App.TSpinbox"
        )
        self.level_spin.grid(row=3, column=1, sticky="w", padx=2, pady=2)

        self.include_spells_var = tk.BooleanVar(value=True)
        self.include_spells_cb = ttk.Checkbutton(
            self.input_frame,
            text="Include spells",
            variable=self.include_spells_var,
            style="App.TCheckbutton"
        )
        self.include_spells_cb.grid(row=4, column=0, columnspan=2, sticky="w", pady=(5, 5))

        self.desc_label = ttk.Label(
            self.input_frame,
            text="NPC role / description (optional):",
            style="AppInner.TLabel"
        )
        self.desc_label.grid(row=5, column=0, sticky="nw", padx=2, pady=(5, 2))

        self.description_text = tk.Text(
            self.input_frame,
            width=40,
            height=3,
            wrap="word",
            relief="flat"
        )
        self.description_text.grid(row=5, column=1, sticky="ew", padx=2, pady=(5, 2))

        buttons_frame = ttk.Frame(self.input_frame, style="App.TFrame")
        buttons_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky="e")

        self.generate_button = ttk.Button(
            buttons_frame,
            text="Generate statblock",
            command=self.on_generate,
            style="App.TButton"
        )
        self.generate_button.grid(row=0, column=0, padx=(0, 5))

        self.random_button = ttk.Button(
            buttons_frame,
            text="Random NPC",
            command=self.on_random,
            style="App.TButton"
        )
        self.random_button.grid(row=0, column=1, padx=(0, 5))

        self.clear_selection_button = ttk.Button(
            buttons_frame,
            text="Clear selection",
            command=self.on_clear_selection,
            style="App.TButton"
        )
        self.clear_selection_button.grid(row=0, column=2)

        self.output_frame = ttk.Frame(self, padding=10, style="App.TFrame")
        self.output_frame.grid(row=3, column=0, sticky="nsew", padx=10)
        self.output_frame.columnconfigure(0, weight=1)
        self.output_frame.rowconfigure(1, weight=1)

        self.output_label = ttk.Label(
            self.output_frame,
            text="Result:",
            font=self.section_font,
            style="AppInner.TLabel"
        )
        self.output_label.grid(row=0, column=0, columnspan=2, sticky="w")

        self.output_text = tk.Text(
            self.output_frame,
            width=60,
            height=20,
            state="disabled",
            wrap="word",
            font=self.mono_font,
            relief="flat"
        )
        self.output_text.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            self.output_frame,
            orient="vertical",
            command=self.output_text.yview
        )
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.output_text.configure(yscrollcommand=scrollbar.set)

        buttons_out_frame = ttk.Frame(self.output_frame, style="App.TFrame")
        buttons_out_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))

        buttons_out_frame.columnconfigure(0, weight=1)
        buttons_out_frame.columnconfigure(1, weight=0)

        self.clear_result_button = ttk.Button(
            buttons_out_frame,
            text="Clear result",
            command=self.on_clear_result,
            style="App.TButton"
        )
        self.clear_result_button.grid(row=0, column=0, sticky="w")

        actions_frame = ttk.Frame(buttons_out_frame, style="App.TFrame")
        actions_frame.grid(row=0, column=1, sticky="e")

        self.copy_button = ttk.Button(
            actions_frame,
            text="Copy to clipboard",
            command=self.on_copy,
            style="App.TButton"
        )
        self.copy_button.grid(row=0, column=0, padx=(0, 5))

        self.copy_json_button = ttk.Button(
            actions_frame,
            text="Copy JSON",
            command=self.on_copy_json,
            style="App.TButton"
        )
        self.copy_json_button.grid(row=0, column=1, padx=(0, 5))

        self.save_button = ttk.Button(
            actions_frame,
            text="Save statblock",
            command=self.on_save,
            style="App.TButton"
        )
        self.save_button.grid(row=0, column=2)

        self.status_var = tk.StringVar(value="")
        self.status_bar = ttk.Label(
            self,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w",
            padding=5
        )
        self.status_bar.grid(row=4, column=0, sticky="ew", padx=10, pady=(4, 6))

        self.setup_base_styles()
        self.apply_theme("dark")

        self.race_combo.focus_set()
        self.bind("<Return>", lambda event: self.on_generate())

        self._buttons_to_toggle = [
            self.generate_button,
            self.random_button,
            self.save_button,
            self.copy_button,
            self.clear_result_button,
            self.copy_json_button,
        ]

        self.last_raw_data = None

        if client is None:
            self.set_status("OPENAI_API_KEY is missing – NPC generation is disabled.")

        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def set_status(self, text: str):
        self.status_var.set(text)
        self.update_idletasks()

    def set_buttons_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for btn in self._buttons_to_toggle:
            btn.config(state=state)

    def setup_base_styles(self):
        self.style.configure("App.TFrame")
        self.style.configure("AppTitle.TFrame")
        self.style.configure("App.TLabel")
        self.style.configure("AppTitle.TLabel")
        self.style.configure("AppInner.TLabel")
        self.style.configure("App.TCheckbutton")
        self.style.configure("App.TButton", padding=6)
        self.style.configure("App.TCombobox")
        self.style.configure("App.TSpinbox")
        self.style.configure("Vertical.TScrollbar")

    def apply_theme(self, theme: str):
        if theme == "light":
            self.configure(bg="#F0F0F0")

            self.style.configure("AppTitle.TFrame", background="#F0F0F0")
            self.style.configure(
                "AppTitle.TLabel",
                background="#F0F0F0",
                foreground="#000000"
            )

            self.style.configure("App.TFrame", background="#FFFFFF")
            self.style.configure(
                "App.TLabel",
                background="#FFFFFF",
                foreground="#000000"
            )
            self.style.configure(
                "AppInner.TLabel",
                background="#FFFFFF",
                foreground="#000000"
            )

            self.style.configure(
                "App.TCheckbutton",
                background="#FFFFFF",
                foreground="#000000"
            )
            self.style.map(
                "App.TCheckbutton",
                background=[("active", "#FFFFFF"), ("selected", "#FFFFFF")],
                foreground=[("active", "#000000"), ("selected", "#000000")]
            )

            self.style.configure(
                "App.TButton",
                background="#E0E0E0",
                foreground="#000000"
            )
            self.style.map(
                "App.TButton",
                background=[("active", "#D0D0D0")]
            )

            self.style.configure(
                "App.TCombobox",
                fieldbackground="#FFFFFF",
                foreground="#000000",
                background="#FFFFFF"
            )
            self.style.map(
                "App.TCombobox",
                fieldbackground=[("readonly", "#FFFFFF")],
                foreground=[("readonly", "#000000")],
                arrowcolor=[("!disabled", "#000000")]
            )

            self.style.configure(
                "App.TSpinbox",
                fieldbackground="#FFFFFF",
                foreground="#000000",
                background="#FFFFFF"
            )
            self.style.map(
                "App.TSpinbox",
                arrowcolor=[("!disabled", "#000000")]
            )

            self.style.configure("TSeparator", background="#D0D0D0")
            self.style.configure(
                "Vertical.TScrollbar",
                troughcolor="#F0F0F0",
                background="#C0C0C0",
                arrowcolor="#000000"
            )

            self.description_text.configure(
                bg="#FAFAFA",
                fg="#000000",
                insertbackground="#000000",
                relief="solid",
                bd=1,
                highlightthickness=0
            )
            self.output_text.configure(
                bg="#FFFFFF",
                fg="#000000",
                insertbackground="#000000",
                relief="solid",
                bd=1,
                highlightthickness=0
            )

            self.status_bar.configure(
                background="#E0E0E0",
                foreground="#000000"
            )

            self.option_add("*Menu.background", "#F0F0F0")
            self.option_add("*Menu.foreground", "#000000")
            self.option_add("*Menu.activeBackground", "#D0D0D0")
            self.option_add("*Menu.activeForeground", "#000000")

        else:
            self.configure(bg="#121212")

            self.style.configure("AppTitle.TFrame", background="#121212")
            self.style.configure(
                "AppTitle.TLabel",
                background="#121212",
                foreground="#F5F5F5"
            )

            self.style.configure("App.TFrame", background="#1E1E1E")
            self.style.configure(
                "App.TLabel",
                background="#1E1E1E",
                foreground="#F5F5F5"
            )
            self.style.configure(
                "AppInner.TLabel",
                background="#1E1E1E",
                foreground="#F5F5F5"
            )

            self.style.configure(
                "App.TCheckbutton",
                background="#1E1E1E",
                foreground="#F5F5F5"
            )
            self.style.map(
                "App.TCheckbutton",
                background=[("active", "#2A2A2A"), ("selected", "#2A2A2A")],
                foreground=[("active", "#F5F5F5"), ("selected", "#F5F5F5")]
            )

            self.style.configure(
                "App.TButton",
                background="#2D2D2D",
                foreground="#F5F5F5"
            )
            self.style.map(
                "App.TButton",
                background=[("active", "#3A3A3A")]
            )

            self.style.configure(
                "App.TCombobox",
                fieldbackground="#2A2A2A",
                foreground="#F5F5F5",
                background="#2A2A2A"
            )
            self.style.map(
                "App.TCombobox",
                fieldbackground=[("readonly", "#2A2A2A")],
                foreground=[("readonly", "#F5F5F5")],
                arrowcolor=[("!disabled", "#F5F5F5")]
            )

            self.style.configure(
                "App.TSpinbox",
                fieldbackground="#2A2A2A",
                foreground="#F5F5F5",
                background="#2A2A2A"
            )
            self.style.map(
                "App.TSpinbox",
                arrowcolor=[("!disabled", "#F5F5F5")]
            )

            self.style.configure("TSeparator", background="#333333")
            self.style.configure(
                "Vertical.TScrollbar",
                troughcolor="#1E1E1E",
                background="#3A3A3A",
                arrowcolor="#F5F5F5"
            )

            self.description_text.configure(
                bg="#2A2A2A",
                fg="#F5F5F5",
                insertbackground="#F5F5F5",
                relief="solid",
                bd=1,
                highlightthickness=0
            )
            self.output_text.configure(
                bg="#1E1E1E",
                fg="#F5F5F5",
                insertbackground="#F5F5F5",
                relief="solid",
                bd=1,
                highlightthickness=1,
                highlightbackground="#F5F5F5",
                highlightcolor="#F5F5F5"
            )

            self.status_bar.configure(
                background="#1A1A1A",
                foreground="#F5F5F5"
            )

            self.option_add("*Menu.background", "#1E1E1E")
            self.option_add("*Menu.foreground", "#F5F5F5")
            self.option_add("*Menu.activeBackground", "#3A3A3A")
            self.option_add("*Menu.activeForeground", "#F5F5F5")

    def on_theme_changed(self, event=None):
        self.apply_theme(self.theme_var.get())

    def on_about(self):
        messagebox.showinfo(
            "About",
            "DnD NPC Generator\n\n"
            "Simple Tkinter-based tool that uses OpenAI to generate "
            "Dungeons & Dragons NPC statblocks.",
            parent=self
        )

    def on_class_changed(self, event=None):
        selected_class = self.class_var.get()
        subclasses = CLASS_TO_SUBCLASSES.get(selected_class, [])
        self.subclass_combo["values"] = subclasses
        self.subclass_var.set("")

    def on_random(self):
        self.set_status("Setting random NPC parameters...")
        self.race_var.set(random.choice(RACES))
        c = random.choice(CLASSES)
        self.class_var.set(c)
        subclasses = CLASS_TO_SUBCLASSES.get(c, [])
        self.subclass_combo["values"] = subclasses
        if subclasses:
            self.subclass_var.set(random.choice(subclasses))
        else:
            self.subclass_var.set("")
        self.level_var.set(str(random.randint(1, 20)))
        self.set_status("Random NPC parameters set.")

    def on_generate(self):
        if client is None:
            messagebox.showerror(
                "Error",
                "Missing OPENAI_API_KEY environment variable.\n"
                "Please set it before generating NPCs.",
                parent=self
            )
            self.set_status("Missing API key.")
            return

        race = self.race_var.get().strip()
        char_class = self.class_var.get().strip()
        subclass = self.subclass_var.get().strip()
        level_str = self.level_var.get().strip()
        include_spells = self.include_spells_var.get()
        role_description = self.description_text.get("1.0", "end-1c").strip()

        if not race or not char_class or not level_str:
            messagebox.showerror("Error", "Please fill Race, Class and Level.", parent=self)
            self.set_status("Missing required fields.")
            return

        try:
            level = int(level_str)
        except ValueError:
            messagebox.showerror("Error", "Level must be an integer.", parent=self)
            self.set_status("Invalid level value.")
            return

        if level < 1 or level > 20:
            messagebox.showerror("Error", "Level must be between 1 and 20.", parent=self)
            self.set_status("Level must be between 1 and 20.")
            return

        self.set_buttons_enabled(False)
        self.set_status("Generating NPC...")

        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, THINKING_MESSAGE + "\n")
        self.output_text.config(state="disabled")
        self.update_idletasks()

        try:
            data = generate_statblock_from_ai(
                race,
                char_class,
                subclass,
                level,
                include_spells,
                role_description
            )
            if isinstance(data, dict):
                self.last_raw_data = data
            else:
                self.last_raw_data = None

            formatted = format_statblock(data)

            if isinstance(data, dict) and include_spells:
                spells = data.get("spells", [])
                summaries = generate_spell_summaries(spells)

                if summaries:
                    summary_lines = []
                    summary_lines.append("")
                    summary_lines.append("Spell summaries (rules):")
                    summary_lines.append("------------------------")
                    for sp in spells:
                        sp_name = str(sp)
                        line = summaries.get(sp_name)
                        if line:
                            summary_lines.append(f"- {sp_name}: {line}")
                    formatted += "\n" + "\n".join(summary_lines)
                elif spells:
                    formatted += "\n\n(Spell summaries could not be generated.)"

        except Exception as e:
            self.last_raw_data = None
            messagebox.showerror(
                "Error",
                f"An error occurred during AI call or formatting:\n{e}",
                parent=self
            )
            self.set_status("Error during NPC generation.")
        else:
            self.output_text.config(state="normal")
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, formatted)
            self.output_text.config(state="disabled")
            self.set_status("NPC generated. You can now save or copy.")
        finally:
            self.set_buttons_enabled(True)

    def on_save(self):
        content = self.output_text.get("1.0", "end-1c").strip()

        if not content or content.startswith(THINKING_MESSAGE):
            self.set_status("Nothing to save.")
            return

        self.set_status("Saving statblock...")

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save statblock",
            parent=self
        )

        if not file_path:
            self.set_status("Save cancelled.")
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            self.set_status(f"Error while saving: {e}")
            return

        self.set_status(f"Saved: {file_path}")

    def on_copy(self):
        content = self.output_text.get("1.0", "end-1c").strip()

        if not content or content.startswith(THINKING_MESSAGE):
            self.set_status("Nothing to copy.")
            return

        try:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.set_status("Statblock copied to clipboard.")
        except Exception as e:
            self.set_status(f"Error while copying: {e}")

    def on_copy_json(self):
        if not isinstance(self.last_raw_data, dict):
            self.set_status("No JSON data to copy.")
            return

        try:
            json_text = json.dumps(self.last_raw_data, indent=2)
            self.clipboard_clear()
            self.clipboard_append(json_text)
            self.set_status("JSON copied to clipboard.")
        except Exception as e:
            self.set_status(f"Error while copying JSON: {e}")

    def on_clear_result(self):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state="disabled")
        self.set_status("Result cleared.")

    def on_clear_selection(self):
        self.race_var.set("")
        self.class_var.set("")
        self.subclass_var.set("")
        self.subclass_combo["values"] = []
        self.level_var.set("1")
        self.include_spells_var.set(True)
        self.description_text.delete("1.0", tk.END)
        self.set_status("Selection cleared.")


def main():
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
