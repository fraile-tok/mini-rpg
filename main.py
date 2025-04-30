import tkinter as tk
import json
import re
import os

# Load story and character data from folders
with open("stories/test.json", "r") as f:
    story = json.load(f)

with open("characters/oltheon.json", "r") as f:
    character = json.load(f)

class TextRPG:
    def __init__(self, root):
        self.root = root
        self.root.title("Text RPG")
        self.root.configure(bg="black")

        self.text_area = tk.Text(
            root, wrap=tk.WORD, bg="black", fg="lime",
            font=("Fira Code", 14), height=20, width=60
        )
        self.text_area.pack(padx=10, pady=10)
        self.text_area.config(state=tk.DISABLED)

        self.button_frame = tk.Frame(root, bg="black")
        self.button_frame.pack(pady=5)

        self.root.bind("<Key>", self.handle_key)

        self.current_node = "start"
        self.history = []
        self.current_choices = []

        self.show_node(self.current_node)

    def show_node(self, node_key):
        if self.current_node != node_key:
            self.history.append(self.current_node)

        node = story[node_key]
        self.current_node = node_key
        self.current_choices = list(node.get("choices", {}).items())

        raw_text = node["text"]

        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)

        # Display ASCII art if exists
        if "ascii_art" in node:
            art_path = os.path.join("ascii_art", node["ascii_art"])
            if os.path.exists(art_path):
                with open(art_path, "r") as art_file:
                    ascii_content = art_file.read()
                    self.text_area.insert(tk.END, ascii_content + "\n\n")

        self.insert_rich_text(raw_text)
        self.text_area.insert(tk.END, "\n\n")

        if self.current_choices:
            for i, (choice_text, _) in enumerate(self.current_choices, start=1):
                self.text_area.insert(tk.END, f"{i}. {choice_text}\n")
            self.text_area.insert(tk.END, "\nPress number to choose. Press Backspace to go back.")
        else:
            self.text_area.insert(tk.END, "\n--- THE END ---\n")
            self.text_area.insert(tk.END, "Press Backspace to return.\n")

        self.text_area.config(state=tk.DISABLED)

    def insert_rich_text(self, text):
        # Configure styles
        self.text_area.tag_configure("highlighted", foreground="yellow", font=("Fira Code", 14, "bold italic"))
        self.text_area.tag_configure("red", foreground="red")
        self.text_area.tag_configure("blue", foreground="blue")
        self.text_area.tag_configure("green", foreground="green")
        self.text_area.tag_configure("gold", foreground="goldenrod")
        self.text_area.tag_configure("b", font=("Fira Code", 14, "bold"))
        self.text_area.tag_configure("i", font=("Fira Code", 14, "italic"))

        i = 0
        while i < len(text):
            # Match $$placeholder
            if text[i:i+2] == "$$":
                match = re.match(r"\$\$(\w+)", text[i:])
                if match:
                    var_name = match.group(1)
                    value = character.get(var_name, f"{{missing:{var_name}}}")
                    start_idx = self.text_area.index(tk.INSERT)
                    self.text_area.insert(tk.END, value)
                    end_idx = self.text_area.index(tk.INSERT)
                    self.text_area.tag_add("highlighted", start_idx, end_idx)
                    i += len(match.group(0))
                    continue

            # Match [tag]text[/tag]
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

            # Otherwise, insert one character
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

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = TextRPG(root)
    root.mainloop()
