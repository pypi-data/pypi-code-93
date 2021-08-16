from phcli.ph_storage.model.s3_storage import PhS3Storage
from phcli.ph_storage import static as st


# 测试上传S3
def upload2S3():
    download_path = "/Users/qianpeng/Desktop/tmp"
    file_name = "面试问题.txt"
    sub_path = "tmp"
    upload_path = (st.UPLOADPATH + "/" + sub_path + "/" + file_name).replace("//", "/")
    s3 = PhS3Storage()
    s3.upload(download_path + "/" + file_name, st.BUCKET, upload_path)
