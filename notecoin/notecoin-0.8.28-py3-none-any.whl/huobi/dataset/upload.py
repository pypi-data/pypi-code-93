from notedrive.lanzou import LanZouCloud
from notetool.tool.secret import read_secret

downer = LanZouCloud()
downer.ignore_limits()
downer.login_by_cookie()

print(downer.sync_directory(path_root='/root/workspace/tmp/coin', folder_id='3358325'))
