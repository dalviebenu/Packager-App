import tkinter as tk
from PIL import Image, ImageTk
from packager import pack
from utils import *
from pathlib import Path

default_text = ["Product Name", "Version", "Description", "Base Game Version", "Min Engine Version", "Path In",
                "Path Out", "UUID Override: World Template", "UUID Override: Skin Pack"]


class DefaultEntry(tk.Entry):
    def __init__(self, master=None, label="", **kwargs):
        tk.Entry.__init__(self, master, **kwargs)
        self.label = label
        self.default_text_write()
        self.bind("<FocusIn>", self.default_text_erase)
        self.bind("<FocusOut>", self.default_text_write)

    def default_text_erase(self, event=None):
        if self.get() in default_text:
            self.delete(0, tk.END)
            self.configure(fg='white')

    def default_text_write(self, event=None):
        val = self.get()

        if val == "":
            self.insert(0, self.label)
            self.configure(fg='grey')


class DefaultText(tk.Text):
    def __init__(self, master=None, label="", **kwargs):
        tk.Text.__init__(self, master, **kwargs)
        self.label = label
        self.bind("<FocusIn>", self.default_text_erase)
        self.bind("<FocusOut>", self.default_text_write)

    def default_text_erase(self, event=None):
        val = self.get(1.0, tk.END)
        val = ''.join(val.split('\n'))

        if val in default_text:
            self.delete(1.0, tk.END)
            self.configure(fg='white')

    def default_text_write(self, event=None):
        val = self.get(1.0, tk.END)
        val = ''.join(val.split('\n'))

        if val == "":
            self.insert(1.0, self.label)
            self.configure(fg='grey')


def write_json_not_sorted(path, data):
    with open(path, 'w', encoding='UTF-8') as f:
        json.dump(data, f, sort_keys=False, indent=2)
    # This method is the same as in utils but with sort_keys as False. This is repeated to avoid changing code
    # in the packager by adding a parameter to the method


def gen_pack_info(des, base_game_ver, lock_option, src):
    """
    Creates packager_data.json that the packager uses.
    """
    result = {
        "texts": {
            "pack.description": ""
        },
        "manifest": {
            "lock_template_options": True,
            "base_game_version": [1, 0, 0]
        }
    }

    result['texts']['pack.description'] = des
    result['manifest']['lock_template_options'] = lock_option
    result['manifest']["base_game_version"] = base_game_ver

    path = Path(src)
    world = Path(path / "world")
    w = []
    if world.is_dir():
        w = list(filter(is_world, world.iterdir()))
        # returns a list of worlds in the worlds directory which contain levelname.txt

        if len(w) == 1:
            w = w[0]
        else:
            print("Multiple world folders...")
            exit()

    write_json_not_sorted(w / "packager_data.json", result)
    f = load_json(w / "packager_data.json")


def package():
    src = path_in.get()
    src = ''.join(src.split('\n'))

    dst = path_out.get()
    dst = ''.join(dst.split('\n'))

    name = prod_name.get()

    vers = version.get()
    vers = vers.split('.')
    for i in range(0,len(vers)):
        vers[i] = int(vers[i])

    descr = desc.get(1.0, tk.END)
    descr = ''.join(descr.split('\n'))

    bgv = base_game_version.get()
    bgv = bgv.split('.')
    for i in range(0, len(bgv)):
        bgv[i] = int(bgv[i])

    mev = min_eng_version.get()

    uuid_check_val = check_uuid.get()
    if uuid_check_val == 1:
        uuid_w = uuid_world.get()
        uuid_s = uuid_skin.get()
    else:
        uuid_w = None
        uuid_s = None

    temp_opt = check_var.get()
    if temp_opt == 0:
        temp_opt = False
    elif temp_opt == 1:
        temp_opt = True

    gen_pack_info(descr, bgv, temp_opt, src)
    pack(src, dst, name, uuid_w, uuid_s, vers)


background = '#1d1d1d'
entry_background = '#242225'
font_color = '#ffffff'
btn_color = '#58c8b3'
default_font_color = 'grey'

# create window
window = tk.Tk()
window.title('Packager')
window.configure(background=background)
window.rowconfigure([1, 2, 3, 4, 5, 6, 7], weight=1)
window.columnconfigure([0, 1], weight=1)

# insert logo
img = ImageTk.PhotoImage(Image.open('sndbx_logo_white.png'))
image_frame = tk.Frame(bg=background)
panel = tk.Label(master=image_frame, background=background, image=img)
image_frame.grid(row=0, column=0)
panel.grid(row=0, column=0, pady=10)

# insert product name, version, lock temp options entry forms
upper_frame = tk.Frame(master=window, background=background, width=100)
upper_frame.grid(row=1, column=0, padx=10, pady=5, sticky='news')

prod_name = DefaultEntry(master=upper_frame, label="Product Name",
                         highlightbackground=background, bg=entry_background, fg=default_font_color)
prod_name.configure(width=50)
prod_name.pack(side=tk.LEFT, padx=20, pady=5)

version = DefaultEntry(master=upper_frame, label="Version",
                       highlightbackground=background, bg=entry_background, fg=font_color)
version.configure(width=12)
version.pack(side=tk.RIGHT, padx=20)

# insert description entry form
desc_frame = tk.Frame(master=window, relief=tk.FLAT, borderwidth=1, bg=background)
desc_frame.grid(row=2, column=0, padx=20, pady=3)

desc = DefaultText(master=desc_frame, bg=entry_background, fg='grey', label="Description")
desc.insert(1.0, "Description")
desc.configure(height=5, width=77)
desc.configure(highlightbackground=background)
desc.configure(font=('helvetica ', 12))
desc.pack(side=tk.LEFT)

# insert Base game version and min engine version
game_version_frame = tk.Frame(master=window, bg=background)
game_version_frame.grid(row=3, column=0, padx=28, pady=5, sticky='news')

base_game_version = DefaultEntry(master=game_version_frame, width=15, bg=entry_background, label="Base Game Version",
                                 fg=font_color, highlightbackground=background)
base_game_version.pack(side=tk.LEFT)

min_eng_version = DefaultEntry(master=game_version_frame, width=15, bg=entry_background, label="Min Engine Version",
                               fg=font_color, highlightbackground=background)
min_eng_version.pack(side=tk.LEFT, padx=10)

check_var = tk.IntVar()
lock_temp = tk.Checkbutton(master=game_version_frame, text='Lock Template Options', fg=font_color,
                           highlightbackground=background, background=background, variable=check_var)
lock_temp.select()
lock_temp.pack(side=tk.LEFT)

# insert Path in/out
widget_width = 68
path_frame = tk.Frame(master=window, background=background)
path_frame.grid(row=4, column=0, sticky='nw', padx=28, pady=5, columnspan=2)

path_in = DefaultEntry(master=path_frame, width=widget_width, bg=entry_background, fg=font_color, label="Path In",
                       highlightbackground=background)
path_in.pack(pady=5)

path_out = DefaultEntry(master=path_frame, width=widget_width, bg=entry_background, fg=font_color, label="Path Out",
                        highlightbackground=background)
path_out.pack(pady=5)

# insert uuid check box
uuid_check_box = tk.Frame(master=window, background=background)
uuid_check_box.grid(row=5, column=0, sticky='nw', padx=28, pady=5, columnspan=2)

check_uuid = tk.IntVar()
uuid_check = tk.Checkbutton(master=uuid_check_box, text='Override UUID', highlightbackground=background,
                            fg=font_color, background=background, variable=check_uuid, width=12)
uuid_check.pack(pady=5)

# insert uuids
uuid_frame = tk.Frame(master=window, background=background)
uuid_frame.grid(row=6, column=0, sticky='nw', padx=28, pady=5, columnspan=2)

uuid_world = DefaultEntry(master=uuid_frame, width=widget_width, bg=entry_background, fg=font_color,
                          label="UUID Override: World Template", highlightbackground=background)
uuid_world.pack(pady=5)

uuid_skin = DefaultEntry(master=uuid_frame, width=widget_width, bg=entry_background, fg=font_color,
                         label="UUID Override: Skin Pack", highlightbackground=background)
uuid_skin.pack(pady=5)

# Insert package button
package_btn = tk.Button(text='Package', bg='blue', fg=btn_color, height=2, width=10, highlightbackground=background,
                        activebackground=btn_color, command=package)
package_btn.grid(row=7, column=0, columnspan=2, sticky='n', pady=10)

window.mainloop()
