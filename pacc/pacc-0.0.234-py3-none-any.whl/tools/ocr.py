import easyocr
from datetime import datetime

s = datetime.now()

# reader = easyocr.Reader(['ch_sim', 'en'])
reader = easyocr.Reader(['en'])
result = reader.readtext(r'C:\Users\Coco\Pictures\1.png', detail=False)
print(result)
for r in result:
    print(r)
print(datetime.now() - s)