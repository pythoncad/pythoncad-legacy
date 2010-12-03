rem _PyInstaller
cd C:\Users\mboscolo\Desktop\R38\pyinstaller-trunk
python Makespec.py -n PythonCAD --icon C:\Users\mboscolo\Desktop\R38\pythoncad\PythonCAD\icons\pythoncad.ico -p C:\Users\mboscolo\Desktop\R38\pythoncad\PythonCAD;C:\Users\mboscolo\Desktop\R38\pythoncad\PythonCAD\Generic;C:\Users\mboscolo\Desktop\R38\pythoncad\PythonCAD\Generic\Kernel;C:\Users\mboscolo\Desktop\R38\pythoncad\PythonCAD\Interface C:\Users\mboscolo\Desktop\R38\pythoncad\PythonCAD\pythoncad_qt.py
python Build.py C:\Users\mboscolo\Desktop\R38\pyinstaller-trunk\pythoncad\PythonCAD.spec
