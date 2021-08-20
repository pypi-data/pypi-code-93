import argparse
import os
import subprocess
import sys

def launch(args):
    parser = argparse.ArgumentParser(description="Launch Nion Swift using native Qt front end.")
    parser.add_argument("--alias",  dest="alias", action="store_true", help="create a desktop alias")
    parser.add_argument("--app",  dest="app", action="store", help="override app package", default="nionui_app.nionswift")
    parser.add_argument("args", nargs=argparse.REMAINDER)
    parsed_args = parser.parse_args()

    if parsed_args.alias:
        if sys.platform == "win32":
            from win32com.shell import shell, shellcon
            import pythoncom
            import datetime
            stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
            desktop_path = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)
            filename = desktop_path + "\\Nion Swift " + stamp + ".lnk"
            base = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
            base.SetPath(os.path.join(sys.exec_prefix, "Scripts", "NionSwiftLauncher", "NionSwift.exe"))
            base.SetArguments(str(sys.prefix) + " nionui_app.nionswift")
            base.SetDescription("Nion Swift Shortcut")
            base.SetWorkingDirectory(os.path.join(sys.exec_prefix, "Scripts", "NionSwiftLauncher"))
            print("Writing Nion Swift shortcut to " + filename)
            base.QueryInterface(pythoncom.IID_IPersistFile).Save(filename, 0)
    else:
        if sys.platform == "darwin":
            exe_path = os.path.join(sys.exec_prefix, "bin", "Nion Swift.app", "Contents", "MacOS", "Nion Swift")
        elif sys.platform == "linux":
            exe_path = os.path.join(sys.exec_prefix, "bin", "NionSwiftLauncher", "NionSwiftLauncher")
        elif sys.platform == "win32":
            exe_path = os.path.join(sys.exec_prefix, "Scripts", "NionSwiftLauncher", "NionSwift.exe")
        else:
            exe_path = None
        if exe_path:
            python_prefix = sys.prefix
            proc = subprocess.Popen([exe_path, python_prefix, parsed_args.app] + parsed_args.args, universal_newlines=True)
            proc.communicate()

def main():
    launch(sys.argv)
