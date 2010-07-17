from bundlebuilder import buildapp
from plistlib import Plist, Dict


plist = Plist(
    CFBundleDocumentTypes = [
        Dict(
            CFBundleTypeExtensions = ["xml", "xml.gz", "*"],
            CFBundleTypeName = "XML File",
            CFBundleTypeRole = "Editor",
            NSDocumentClass = "ImageDocument",
        ),
        Dict(
            CFBundleTypeExtensions = ["dwg"],
            CFBundleTypeName = "DWG File",
            CFBundleTypeRole = "Viewer",
            NSDocumentClass = "ImageDocument",
        ),
    ]
)


buildapp(
	mainprogram = "PythonCad.py",
	resources = ["PythonCAD/Interface/Cocoa/MainMenu.nib", "PythonCAD/Interface/Cocoa/ImageDocument.nib", "PythonCAD", "prefs.py"],
	nibname = "MainMenu",
    plist = plist,
)
