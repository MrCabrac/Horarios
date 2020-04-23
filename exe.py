from cx_Freeze import setup, Executable
import sys

#main
exe = Executable(
    script = "main.py",
    targetName = "Horarios.exe",
    #icon = "icon.png",
    base = "Win32GUI",
    copyright = "Copyright (C) BSS - Brayan 2019"
    )
buildOptions = dict(
    excludes = ["tkinter"],
    includes = ["idna.idnadata"],
    include_files = ["main.ui", "readExcel.ui", "horarios/opciones", "teacher_list.npy"],
    optimize = 1,
    )
setup(
    name = "Horarios",
    version = "1.0",
    description = "Crear las opciones de todos los horarios",
    author = "Brayan Martínez",
    executables = [exe],
    options = dict(build_exe = buildOptions)
    )

#### COMO CONSTRUIR EL EXE
'''py exe.py build'''
'''pyuic5 -x untitled.ui -o gui.py'''
'''pyuic iconos.qrc -o iconos_rc.py'''
