import os
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import ImageTk, Image
import io

import win32clipboard as clip
import win32con


class Textures:
    def __init__(self, assets_path):
        self.assets_path = assets_path
        self.textures_paths = {}
        self.get_textures_paths()

    def get_textures_paths(self):
        # List all files in the dir
        for root, dirs, files in os.walk(self.assets_path):
            for file in files:
                # CHecks if file is a png
                if file.endswith(".png"):
                    texture_name = file.removesuffix(".png")
                    # Check for duplicate names
                    if texture_name in self.textures_paths:
                        texture_root = os.path.split(root)[-1]
                        texture_name += f"_{texture_root}"
                    self.textures_paths[texture_name] = os.path.join(root, file)

        return self.textures_paths

    def search_texture_by_name(self, name):
        search_results = []
        for texture in self.textures_paths:
            if name in texture:
                search_results.append(texture)

        return search_results

    def get_texture_by_name(self, name):
        return self.textures_paths[name]



class Gui:
    def __init__(self):
        self.root = tk.Tk()

        self.texture_name = ""
        self.default_bg = self.root.cget("bg")
        self.textures = None

        # Frame definitions
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.left_frame = ttk.Frame(self.top_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_frame = ttk.Frame(self.top_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.footer_frame = tk.Frame(self.root, relief=tk.SUNKEN, bd=1)
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = ttk.Label(self.footer_frame, text="Ready")
        self.status_label.pack(side=tk.RIGHT)

        self.path_label = ttk.Label(self.footer_frame)
        self.path_label.pack(side=tk.LEFT)

        # Left frame
        self.texture_title = ttk.Label(self.left_frame, text="Textures List")
        self.texture_title.pack()

        self.treeview_frame = ttk.Frame(self.left_frame)
        self.treeview_frame.pack(side=tk.TOP, fill=tk.Y, expand=True)

        self.treeview_buttons_frame = ttk.Frame(self.left_frame)
        self.treeview_buttons_frame.pack(side=tk.BOTTOM)

        self.texture_treeview_scrollbar = ttk.Scrollbar(self.treeview_frame)
        self.texture_treeview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.texture_treeview = ttk.Treeview(self.treeview_frame, yscrollcommand=self.texture_treeview_scrollbar.set,
                                             show="tree")
        self.texture_treeview.pack(fill=tk.Y, expand=True)
        self.texture_treeview.bind("<<TreeviewSelect>>", self.show_texture)

        self.texture_treeview_scrollbar.configure(command=self.texture_treeview.yview)

        self.search_bar = ttk.Entry(self.treeview_frame)
        self.search_bar.pack(fill=tk.X)
        self.search_bar.bind("<KeyRelease>", self.search)


        self.select_folder_button = ttk.Button(self.treeview_buttons_frame, text="Choisir un dossier",
                                               command=self.pick_and_load_texturepack)
        self.select_folder_button.pack(side=tk.LEFT)

        #self.select_folder_button = ttk.Button(self.treeview_buttons_frame, text="Ouvrir le dossier (Explorer)",command=self.locate_folder)
        #self.select_folder_button.pack(side=tk.LEFT, pady=5)

        #self.export_pack_button = ttk.Button(self.treeview_buttons_frame, text="Export Pack", command=self.export_pack)
        #self.export_pack_button.pack(side=tk.LEFT)


        # Right Frame
        self.top_right_frame = ttk.Frame(self.right_frame)
        self.top_right_frame.pack(fill=tk.BOTH, expand=True)

        self.texture_label_image = tk.Label(self.top_right_frame)
        self.texture_label_image.pack(expand=True)

        self.bottom_right_frame = ttk.Frame(self.right_frame)
        self.bottom_right_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.export_texture_button = ttk.Button(self.bottom_right_frame, text="Export Texture", command=self.export_texture)
        self.export_texture_button.pack(side=tk.LEFT, pady=5)

        self.copy_button = ttk.Button(self.bottom_right_frame, text="Copy Texture",
                                      command=self.copy_image_to_clipboard)
        self.copy_button.pack(side=tk.LEFT, pady=5)

        self.replace_button = ttk.Button(self.bottom_right_frame, text="Replace Texture", command=self.replace_texture)
        self.replace_button.pack(side=tk.LEFT, pady=5)

    def pick_and_load_texturepack(self):
        self.folder_path = os.path.abspath(filedialog.askdirectory())
        self.textures = Textures(self.folder_path)
        self.show_textures()

    def show_textures(self):
        self.texture_treeview.delete(*self.texture_treeview.get_children())
        for texture in self.textures.textures_paths:
            self.texture_treeview.insert("", tk.END, text=str(texture))

    def show_texture(self, _ = None):
        current_item = self.texture_treeview.focus()
        self.texture_name = self.texture_treeview.item(current_item)["text"]
        texture_image_path = os.path.abspath(self.textures.get_texture_by_name(self.texture_name))
        self.texture_image = Image.open(texture_image_path)
        texture_image_resized = self.texture_image.resize((256, 256), Image.Resampling.NEAREST)

        self.texture_imagetk = ImageTk.PhotoImage(texture_image_resized)

        self.texture_label_image.configure(image=self.texture_imagetk)

        relative_texture_path = os.path.relpath(texture_image_path, self.folder_path)
        self.path_label.configure(text=relative_texture_path)


    def locate_folder(self):
        pass

    def export_texture(self):
        if not self.texture_name:
            return

        file = filedialog.asksaveasfilename(filetypes=(("PNG", ".png"), ("Tout", ".*")), initialfile=self.texture_name,
                                            defaultextension="png")
        self.texture_image.save(file)

        self.root.after(0, self.saved_status)
        self.root.after(3000, self.reset_status)

    def export_pack(self):
        ...

    def saved_status(self):
        self.status_label.configure(text="Saved", foreground="white", background="green")
        self.footer_frame.configure(bg="green")

    def reset_status(self):
        self.status_label.configure(text="Ready", foreground="black", background=self.default_bg)
        self.footer_frame.configure(bg=self.default_bg)

    def copy_image_to_clipboard(self):
        # Create an in-memory file-like object
        image_buffer = io.BytesIO()

        # Save the canvas image to the buffer in PNG format
        self.texture_image.save(image_buffer, format="BMP")
        data = image_buffer.getvalue()[14:]
        image_buffer.close()

        clip.OpenClipboard()
        clip.EmptyClipboard()
        clip.SetClipboardData(win32con.CF_DIB, data)
        clip.CloseClipboard()

    def replace_texture(self):
        current_item = self.texture_treeview.focus()
        texture_name = self.texture_treeview.item(current_item)["text"]

        file = filedialog.askopenfilename(defaultextension=".png", filetypes=(("PNG", ".png"), ("All", ".*")))
        texture_image = Image.open(file)

        texture_image.save(self.textures.get_texture_by_name(texture_name))

        self.show_texture()

    def search(self, _ = None):
        name = self.search_bar.get()

        self.texture_treeview.delete(*self.texture_treeview.get_children())

        for item in self.textures.textures_paths:
            if name in item:
                self.texture_treeview.insert("", tk.END, text=str(item))

    def run(self):
        self.root.mainloop()


textures = Textures(r"C:\Users\noamh\Documents\Code\Python\mcTexturePackHelper\1.8.9\assets")
textures.get_textures_paths()

gui = Gui()
gui.run()
