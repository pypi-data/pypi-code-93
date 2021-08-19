try:
    import yaml
    import xlwt
except:
    raise ImportError('Please `pip install -r requirements.txt`.')
else:
    versions = []
    versions.extend([
        yaml.__version__ == '5.4.1'
        , xlwt.__VERSION__ == '1.3.0'
    ])

    if not all(versions):
        raise ImportError('''\
requirements: yaml==5.4.1, xlwt==1.3.0\
''')
