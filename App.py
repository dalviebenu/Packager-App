import tkinter as tk
from PIL import Image, ImageTk
from packager import pack
from utils import *
from pathlib import Path

default_text = ["Product Name", "Version", "Description", "Base Game Version", "Min Engine Version", "Path In",
                "Path Out", "UUID Override: World Template", "UUID Override: Skin Pack"]


def default_text_erase(event):
    if event.widget.get() in default_text:
        event.widget.delete(0, tk.END)


def default_text_write(event):
    val = event.widget.get()

    if val == "":
        event.widget.insert(0, "Product Name")


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
    pack(src, dst, name, uuid_w, uuid_s)


background = '#1d1d1d'
entry_background = '#242225'
font_color = '#ffffff'
btn_color = '#58c8b3'

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

prod_name = tk.Entry(master=upper_frame, highlightbackground=background, bg=entry_background, fg=font_color)
prod_name.configure(width=50)
prod_name.insert(0, 'Product Name')
prod_name.bind("<Button-1>", default_text_erase)
prod_name.bind("<FocusOut>", default_text_write)
prod_name.pack(side=tk.LEFT, padx=20, pady=5)

version = tk.Entry(master=upper_frame, highlightbackground=background, bg=entry_background, fg=font_color)
version.configure(width=12)
version.insert(0, 'Version')
version.pack(side=tk.RIGHT, padx=20)

# insert description entry form
desc_frame = tk.Frame(master=window, relief=tk.FLAT, borderwidth=1, bg=background)
desc_frame.grid(row=2, column=0, padx=20, pady=3)

desc = tk.Text(master=desc_frame, bg=entry_background, fg=font_color)
desc.configure(height=5, width=77)
desc.configure(highlightbackground=background)
desc.insert("1.0", "Description")
desc.configure(font=('helvetica ', 12))
desc.pack(side=tk.LEFT)

# insert Base game version and min engine version
game_version_frame = tk.Frame(master=window, bg=background)
game_version_frame.grid(row=3, column=0, padx=28, pady=5, sticky='news')

base_game_version = tk.Entry(master=game_version_frame, width=15, bg=entry_background,
                             fg=font_color, highlightbackground=background)
base_game_version.insert(0, "Base Game Version")
base_game_version.pack(side=tk.LEFT)

min_eng_version = tk.Entry(master=game_version_frame, width=15, bg=entry_background,
                           fg=font_color, highlightbackground=background)
min_eng_version.insert(0, "Min Engine Version")
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

path_in = tk.Entry(master=path_frame, width=widget_width, bg=entry_background, fg=font_color,
                   highlightbackground=background)
path_in.insert(0, "Path In")
path_in.pack( pady=5)

path_out = tk.Entry(master=path_frame, width=widget_width, bg=entry_background, fg=font_color,
                    highlightbackground=background)
path_out.insert(0, "Path Out")
path_out.pack( pady=5)

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

uuid_world = tk.Entry(master=uuid_frame, width=widget_width, bg=entry_background, fg=font_color,
                      highlightbackground=background)
uuid_world.insert(0, "UUID Override: World Template")
uuid_world.pack(pady=5)

uuid_skin = tk.Entry(master=uuid_frame, width=widget_width, bg=entry_background, fg=font_color,
                     highlightbackground=background)
uuid_skin.insert(0, "UUID Override: Skin Pack")
uuid_skin.pack(pady=5)

# Insert package button
package_btn = tk.Button(text='Package', bg='blue', fg=btn_color, height=2, width=10, highlightbackground=background,
                        activebackground=btn_color, command=package)
package_btn.grid(row=7, column=0, columnspan=2, sticky='n', pady=10)

window.mainloop()
