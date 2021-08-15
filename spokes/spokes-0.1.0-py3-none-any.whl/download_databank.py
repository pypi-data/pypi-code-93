import os
def download_databank(directory):
    print("Downloading databank from Spokes Data Dropbox...")

    import dropbox

    filename = "data_bank.h5"
    databank_path = os.path.join(directory, filename)

    dbx = dropbox.Dropbox("t5nUAea8rv8AAAAAAAAAAUQwGoV0cxwF0UvnmyyJtiOM7J3-IoL1vfqkvyK_i7C8") # Access token to spokesdata@gmail.com Dropbox

    dbx.files_download_to_file(databank_path, '/' + filename)

    print("Databank downloaded successfully")
