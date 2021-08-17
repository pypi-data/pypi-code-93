import shutil
import __main__
from artify import utilities

def archive_file():
    final_archive_name= ''
    root_dir = __main__.os.path.join(__main__.archive_rootdir, __main__.archive_basedir)
    if __main__.debug == 1:
        print('DEBUG: Archive Name: ',__main__.archive_basename)
        print('DEBUG: Archive Base Directory: ',__main__.archive_basedir)
        print('DEBUG: Archive Root Directory: ', __main__.archive_rootdir)
        print('DEBUG: Final Root directory: ', root_dir)
        print('DEBUG: Archive Format: ',__main__.archive_format)
        
    
    if __main__.options == 'create-filename':
        c_version = utilities.get_current_application_version(__main__.archive_rootdir)

        if c_version == None or c_version == '':
            c_version = '1.0.0'
            print("INFO: Defaulting to version 1.0.0. Version number not found")
            
        final_archive_name = __main__.archive_basename + "-" + c_version
        if __main__.debug == 1:
            print('DEBUG: Application Version found: ', c_version)
            print('DEBUG: Archive name with version number: ', final_archive_name)
    else:
        final_archive_name = __main__.archive_basename
    final_archive_name = __main__.os.path.join(__main__.archive_rootdir,final_archive_name)
    if __main__.debug == 1:
        print('DEBUG: Archive output path and name: ', final_archive_name)
    return shutil.make_archive(final_archive_name, __main__.archive_format,root_dir)
    #return shutil.make_archive(final_archive_name, __main__.archive_format,__main__.archive_rootdir, __main__.archive_basedir)