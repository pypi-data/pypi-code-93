"""STEPS FOR REUPLOADING TO PYPI
    0. UPDATE SETUP.PY VERSION
    1. PUSH TO GITHUB
    2. DELETE DIST FOLDER
    3. setup.py sdist bdist_wheel
    4. python -m twine upload dist/*
    5. Enter username
    6. Enter password
    7. Profit
"""
