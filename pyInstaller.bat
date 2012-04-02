@echo off
cls

rem _PyInstaller
for /f "tokens=* delims= " %%a in ("%CD%") do set origPath=%%a
set ico			=%origPath%\PythonCAD\icons\pythoncad.ico
for /f "tokens=* delims= " %%a in ("%ico%") do set ico=%%a
set generic		=%origPath%\PythonCAD\Generic
for /f "tokens=* delims= " %%a in ("%generic%") do set generic=%%a
set kernel		=%origPath%\PythonCAD\Generic\Kernel
for /f "tokens=* delims= " %%a in ("%kernel%") do set kernel=%%a
set interface	=%origPath%\PythonCAD\Interface
for /f "tokens=* delims= " %%a in ("%interface%") do set interface=%%a
set pythoncad	=%origPath%\PythonCAD\pythoncad_qt.py
rem for /f "tokens=* delims= " %%a in ("%pythoncad%") do set pythoncad=%%a
echo ************************
echo "Set Variables"
echo ************************
echo "origPath	:"%origPath%
echo "Ico		:"%ico%
echo "generic	:"%generic%
echo "kernel	:"%kernel%
echo "interface	:"%interface%
echo "pythoncad	:"%pythoncad%
echo ************************
echo " "
cd ..\pyinstaller-1.5.1
set libPaths=%generic%;%kernel%;%interface%
for /f "tokens=* delims= " %%a in ("%libPaths%") do set libPaths=%%a
echo "libPaths	:"%libPaths%
python Makespec.py -n PythonCAD --icon=%ico% --paths=%libPaths% %pythoncad%

set specFile=%cd%\PythonCAD\PythonCAD.spec

echo ************************
echo "spec file:"%specFile%
echo ************************
echo " "
echo " "
python Build.py %specFile%

cd ..\pythoncad
rem "Build Comleted"