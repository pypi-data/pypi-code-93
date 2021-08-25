# Databricks notebook source
# MAGIC %md
# MAGIC ### CreateMountPoints
# MAGIC This notebook creates the mount points in Databricks for folders in Data Lake that are used in the Gen 2 platform.
# MAGIC 
# MAGIC 
# MAGIC >#### Important Note:
# MAGIC >If other clusters are <i>running</i>, you'll need to run <b>dbutils.fs.refreshMounts()</b> ON THOSE CLUSTERS in order for them to be visible

# COMMAND ----------

# DBTITLE 1,List all existing mount points
dbutils.fs.mounts()

# COMMAND ----------

# DBTITLE 1,Widget Setup
#dbutils.widgets.removeAll()
 
dbutils.widgets.dropdown("ForceRemount", "FALSE", ["TRUE", "FALSE"])
 
force_remount = dbutils.widgets.get("ForceRemount") == "TRUE"

print('Force Remount\t', force_remount)

# COMMAND ----------

def check_if_mount_exists(folder_name: str, mount_root: str="mnt") -> bool:
    """
    Function to check if a mount already exists
    Default mount root:  "mnt"
    """
    ret_value = False
    mount_point = "/" + mount_root.lower() + "/" + folder_name.upper()
    all_mounts = dbutils.fs.mounts()
    for mnt in all_mounts:
        if mnt.mountPoint == mount_point:
            ret_value = True
            break
    return ret_value

# COMMAND ----------

# DBTITLE 1,Create the mount points
import os

folders = ['RAW','STAGE','DELTA','DROPBOX','TE','DATAMODEL_CONFIG']
adls_file_system = "maindl"
adls_storage_account = os.environ.get("DATALAKE_ACCOUNT"); 
adb_secret_scope = os.environ.get("KEY_VAULT");

# abfss
configs = {"fs.azure.account.auth.type": "OAuth",
        "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
        "fs.azure.account.oauth2.client.id": dbutils.secrets.get(scope = adb_secret_scope, key = "adb-app-reg-id"),
        "fs.azure.account.oauth2.client.secret": dbutils.secrets.get(scope = adb_secret_scope, key = "adb-app-reg-secret"),
        "fs.azure.account.oauth2.client.endpoint": "https://login.microsoftonline.com/{}/oauth2/token".format(dbutils.secrets.get(scope = adb_secret_scope, key = "ad-tenant-id")),
        "fs.azure.createRemoteFileSystemDuringInitialization": "false"}


for folder in folders:
    found = False
    print(f"Processing folder: {folder}")

    # First check if mount already exists
    found = check_if_mount_exists(folder)
    
    if found:
        print(f"\tMount already exists for folder: {folder}")
    else:  # Didn't find the file
        print(f"\tMissing mount for folder: {folder}")
    
    # If the mount exists AND we're forcing a re-mount
    if force_remount and found:
        # Remove mount if already exists
        try:
            dbutils.fs.unmount("/mnt/{}".format(folder))
            print(f"\tUnmounting folder: {folder}")
        except:
            pass
    
    # If the mount doesn't exist OR we've unmounted it above
    if not found or force_remount:
        # Mount folder(s)
        try:
            print(f"\tMounting folder: {folder}")
            dbutils.fs.mount(
                source = f"abfss://{adls_file_system}@{adls_storage_account}.dfs.core.windows.net/{folder}",
                mount_point = f"/mnt/{folder}",
                extra_configs = configs)
        except:
            print(f"\tERROR Mounting folder: {folder}")
            pass
    

# COMMAND ----------

# DBTITLE 1,List all existing mounts
dbutils.fs.mounts()
