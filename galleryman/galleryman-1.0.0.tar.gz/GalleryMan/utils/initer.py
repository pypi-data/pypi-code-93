import urllib.request
import os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Initer:
    def __init__(self) -> None:
        pass
    
    def init(self):
        print("{} {}".format(bcolors.OKCYAN + bcolors.BOLD + "\n::" + bcolors.ENDC , bcolors.OKGREEN + "Welcome to GalleryMan!" + bcolors.ENDC))
                
        print("{} {}".format(bcolors.OKCYAN + bcolors.BOLD + "\n::" + bcolors.ENDC , bcolors.OKGREEN + "Initing GalleryMan... Please Wait" + bcolors.ENDC))
            
        print("{} {}".format(bcolors.OKCYAN + bcolors.BOLD + "\n::" + bcolors.ENDC , bcolors.OKGREEN + "Creating files..." + bcolors.ENDC))
            
        res = True    
                        
        try:
            with open(os.path.join(os.path.expanduser("~") , ".config" , "galleryman" , "config.ini") , "r") as f:
                pass
            
            print("{} {}".format(bcolors.OKCYAN + bcolors.BOLD + "\n::" + bcolors.ENDC , bcolors.WARNING + "You alread have a config file created. Overwrite? (y/[n]) ") + bcolors.ENDC , end="")
            
            res = input()
            
            if(res == "y"):
                res = True
            else:
                res = False
                
        except:
            
            pass
        
        if(res):
            try:
                os.makedirs(os.path.join(os.path.expanduser("~") , ".config" , "galleryman"))
            except:
                pass
            
            with open(os.path.join(os.path.expanduser("~") , ".config" , "galleryman" , "config.ini") , "w") as f:
                with urllib.request.urlopen('https://raw.githubusercontent.com/0xsapphir3/galleryman/main/GalleryMan/config.ini') as response:
                
                    f.write(bytes(response.read()).decode("utf-8"))

                        
            print("{} {}".format(bcolors.OKCYAN + bcolors.BOLD + "\n::" + bcolors.ENDC , bcolors.OKGREEN + "Config file is located at {}".format(os.path.join(os.path.expanduser("~") , ".config" , "galleryman" , "config.ini")) + bcolors.ENDC))
        
        
        try:
            os.makedirs(os.path.join(os.path.expanduser("~") , ".galleryman" , "data"))
        except:
            pass
        
        try:
            os.makedirs(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "trashFiles"))
        except:
            pass
        
        for files in [os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "trashLogs.txt") , os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "likedFolders.txt") , os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "scan_dirs.txt")]:
            with open(files , "w") as file:
                file.write("[]")
        
        with open(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "galleryman.status") , "w") as f:
            f.write("NOT REGISTERED")
            
    
        print("{} {}".format(bcolors.OKCYAN + bcolors.BOLD + "\n::" + bcolors.ENDC , bcolors.OKGREEN + "Completed! Run `galleryman` to start the application" + bcolors.ENDC))
    