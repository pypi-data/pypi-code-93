"""The variable cipherGUIList contains the list of ciphergui modules.

If an import of the module ciphergui.PluginCipherGUIList succeeds when
importing this module, the contents of
ciphergui.PluginCipherGUIList.cipherGUIList will be appended to this
cipherGUIList.

cipherGUIList is a list of tuples of the form:

    (className, guiName, labelName, description).

"""


cipherGUIList = [
    ("Gie", "Gie's Code", "_Gie's Code", "A simple cipher doable by hand"),
    ("Caesar", "Caesar's Code", "_Caesar's Code", "Julius Caesar's code"),
    ("Rot", "Rot", "_Rot", "Linear rotation"),
    ("Vigenere", "Vigenere", "_Vigenere", 
        "A version of Rot that uses a private key")
]
try:
    import ciphergui.PluginCipherGUIList
    cipherGUIList.extend(ciphergui.PluginCipherGUIList.cipherGUIList)
except ImportError:
    pass
