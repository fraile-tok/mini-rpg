import tkinter as tk
import tkinter.font as tkfont
import json
import os
import re

# === GLOBALS ===
STORY_DIR = "stories"
CHARACTER_DIR = "characters"
ASCII_DIR = "ascii_art"
FONT = "Kelmscott Mono"

class StartMenu:
    def __init__(self, root, on_start_game):
        self.root = root
        self.root.title("Select Story and Character")
        self.root.configure(bg="black")

        self.on_start_game = on_start_game

        self.story_files = [f for f in os.listdir(STORY_DIR) if f.endswith(".json")]
        self.char_files = [f for f in os.listdir(CHARACTER_DIR) if f.endswith(".json")]

        # GUI elements
        tk.Label(root, text="Choose a Story:", fg="lime", bg="black", font=(FONT, 14)).pack()
        self.story_var = tk.StringVar(value=self.story_files[0])
        tk.OptionMenu(root, self.story_var, *self.story_files).pack(pady=20)

        tk.Label(root, text="Choose a Character:", fg="lime", bg="black", font=(FONT, 14)).pack()
        self.char_var = tk.StringVar(value=self.char_files[0])
        tk.OptionMenu(root, self.char_var, *self.char_files).pack(pady=20)

        tk.Button(root, text="Start Game", font=(FONT, 14),
                  command=self.start_game).pack(pady=20)

    def start_game(self):
        story_file = os.path.join(STORY_DIR, self.story_var.get())
        char_file = os.path.join(CHARACTER_DIR, self.char_var.get())
        self.on_start_game(story_file, char_file)


class TextRPG:
    def __init__(self, root, story_file, char_file):
        # Load data
        with open(story_file, "r") as f:
            self.story = json.load(f)
        with open(char_file, "r") as f:
            self.character = json.load(f)

        self.root = root
        story_title = self.story.get("title", "Untitled")
        self.root.title(f"{story_title} | Text RPG")
        self.root.configure(bg="black")

        for widget in root.winfo_children():
            widget.destroy()

        self.text_area = tk.Text(
            root, wrap=tk.WORD, bg="black", fg="lime",
            font=(FONT, 14), height=20, width=60
        )
        self.text_area.pack(padx=10, pady=10)
        self.text_area.config(state=tk.DISABLED)

        self.root.bind("<Key>", self.handle_key)

        self.current_node = "start"
        self.history = []
        self.current_choices = []

        self.show_node(self.current_node)

    def show_node(self, node_key):
        if self.current_node != node_key:
            self.history.append(self.current_node)

        node = self.story[node_key]
        self.current_node = node_key
        self.current_choices = list(node.get("choices", {}).items())

        raw_text = node["text"]

        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)

        if "ascii_art" in node:
            art_path = os.path.join(ASCII_DIR, node["ascii_art"])
            if os.path.exists(art_path):
                with open(art_path, "r") as art_file:
                    ascii_content = art_file.read()
                    self.text_area.insert(tk.END, ascii_content + "\n\n")

        self.insert_rich_text(raw_text)
        self.text_area.insert(tk.END, "\n\n")

        if self.current_choices:
            for i, (choice_text, _) in enumerate(self.current_choices, start=1):
                self.text_area.insert(tk.END, f"{i}. {choice_text}\n")
            self.text_area.insert(tk.END, "\nPress number to choose.\nPress Backspace to go back.")
        else:
            self.text_area.insert(tk.END, "\n--- THE END ---\n")
            self.text_area.insert(tk.END, "\nPress Backspace to return.\nPress Return to restart.")

        self.text_area.config(state=tk.DISABLED)

    def insert_rich_text(self, text):
        self.text_area.tag_configure("highlighted", foreground="yellow", font=(FONT, 14, "bold italic"))
        self.text_area.tag_configure("red", foreground="red")
        self.text_area.tag_configure("blue", foreground="blue")
        self.text_area.tag_configure("green", foreground="green")
        self.text_area.tag_configure("gold", foreground="goldenrod")
        self.text_area.tag_configure("b", font=(FONT, 14, "bold"))
        self.text_area.tag_configure("i", font=(FONT, 14, "italic"))

        i = 0
        while i < len(text):
            if text[i:i+2] == "$$":
                match = re.match(r"\$\$(\w+)", text[i:])
                if match:
                    var_name = match.group(1)
                    value = self.character.get(var_name, f"{{missing:{var_name}}}")
                    start_idx = self.text_area.index(tk.INSERT)
                    self.text_area.insert(tk.END, value)
                    end_idx = self.text_area.index(tk.INSERT)
                    self.text_area.tag_add("highlighted", start_idx, end_idx)
                    i += len(match.group(0))
                    continue

            match = re.match(r"\[([a-zA-Z]+)\](.+?)\[/\1\]", text[i:], flags=re.DOTALL)
            if match:
                tag = match.group(1)
                content = match.group(2)
                if tag in self.text_area.tag_names():
                    start_idx = self.text_area.index(tk.INSERT)
                    self.text_area.insert(tk.END, content)
                    end_idx = self.text_area.index(tk.INSERT)
                    self.text_area.tag_add(tag, start_idx, end_idx)
                    i += len(match.group(0))
                    continue

            self.text_area.insert(tk.END, text[i])
            i += 1

    def handle_key(self, event):
        key = event.keysym
        if key.isdigit():
            index = int(key) - 1
            if 0 <= index < len(self.current_choices):
                _, next_node = self.current_choices[index]
                self.show_node(next_node)
        elif key == "BackSpace" and self.history:
            prev_node = self.history.pop()
            self.show_node(prev_node)
        elif key == "Return" and self.history:
            self.history.clear()
            self.show_node("start")

# === Start GUI ===
if __name__ == "__main__":
    root = tk.Tk()
    app = StartMenu(root, lambda s, c: TextRPG(root, s, c))
    root.mainloop()
