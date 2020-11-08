from cx_Freeze import setup, Executable

base = None
setup(
    name="App",
    options = {"build_exe": {"packages":["tkinter","zlib"]}},
    version="0.1",
    description="",
    executables= [Executable("App.py", base=base)]
)
