from google.cloud import storage

def test_bucket():
    client = storage.Client()
    buckets = client.list_buckets()
    print(list(buckets))
#    https://console.cloud.google.com/storage/browser/[bucket-id]/
    bucket = client.get_bucket('jupytery-content-b1')
    print(bucket)
#    blob = bucket.get_blob('remote/path/to/file.txt')
#    print(blob.download_as_string())
#    blob.upload_from_string('New contents!')
#    blob2 = bucket.blob('remote/path/storage.txt')
#    blob2.upload_from_filename(filename='/local/path.txt')


if __name__ == "__main__":
    test_bucket()
