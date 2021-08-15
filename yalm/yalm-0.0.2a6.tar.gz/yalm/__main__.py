from yalm import licenses

mit, apache, gpl2, gpl3, *_ = list(licenses.spdx_licenses.values())

template = gpl2
key = '9409774ee89c484fe0f4b65d12bda1d2923d4687686858679172d473cd83038c.txt'
key = 'c65379247414a47f9353192b1e85bbcccb2b703ee3f0df95e0d7eb682035f09d.txt'
key = '078071470494c96d5f99581e8a13af5d28e7a34050e9e6f3e4c9394c25bbfed5.txt'

raw_doc = template.positive_sample(key).document
doc = licenses._normalize_text(raw_doc)
pattern = gpl2.regex.pattern

print(doc, end='\n\n\n\n\n')
print(pattern)
