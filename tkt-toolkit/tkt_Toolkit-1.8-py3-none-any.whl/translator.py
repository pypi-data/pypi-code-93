from googletrans import Translator

translator = Translator()
def Translate(text:str,dest,src:str='auto'):
    obj = translator.translate(text,dest,src)
    src_lng = obj.src
    dest_lng = obj.dest
    dest = obj.text
    src = text
    ext = (src_lng,dest_lng,src)
    return (dest,ext)