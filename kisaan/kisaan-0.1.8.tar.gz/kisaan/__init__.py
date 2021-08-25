from pymongo import MongoClient

def hello_kisaan():
	return "Hello Kisaan"

# Mongodb authentication

def mongodb_auth():
    uri="mongodb+srv://adityasingh98:adityasingh98@kisaan.kwm8f.mongodb.net/kisaan_corp?retryWrites=true&w=majority"
    client=MongoClient(uri,ConnectTimeoutMS=1000,retryWrites=True)
    return client

