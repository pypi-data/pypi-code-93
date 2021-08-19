try:
    #ลำดับมีผลพยายามโหลดที่ ใน folder ที่กำลัง Implement ก่อน
    from starfishX import config as con 
    #print("Dev")
except:
    #print("Debug")
    import starfishX.config as con

prefix = "starfishX."

if(con.__mode__=="debug"):
    prefix = ""


exec("from "+prefix+"npl_fn import *")

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.models import load_model

import json

def sentimentAnalysis(content,path=""):
    #Load the previously saved weights

    #drive.mount('/content/drive')

    weight_path = path+"sa_model.h5"
    #weight_path1 = os.path.dirname(weight_path)
    #print(weight_path1)
    model = create_model()
    #print(model.summary())
    model.load_weights(weight_path)
    
    with open(path+'dictionary.json', 'r') as dictionary_file:
      dictionary = json.load(dictionary_file)
    
    tokenizer = Tokenizer(num_words=2200)
    tokenizer.word_index = dictionary  #tokenizer.word_index
    setTokenizer(tokenizer)
    
    tw = pre_process_txt(content)
    prediction = model.predict(tw)
    result = trans_result(prediction)
    return result