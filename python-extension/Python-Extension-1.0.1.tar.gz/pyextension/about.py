text = {
    '__init__' : {
        'askvalue' : '''
askvalue(title='', msg='', arg=())
If args are two int,
it will create a window with a Spinbox that can choose number between two int.

If args are strings,
it will create a window with a Spinvox that can choose things in args.
''',
        'askitem' : '''
askitem(title='', msg='', items=[], number=1, normal=0)
It will create a tkinter window with title, msg
and a Listbox that can choose things in the items.

The number of the things can choose depends on argument : number
And ‘normal’ means if you do not do anythings before enter,
the choosen item will be the index 'normal' in list 'items'.
''',
        }
    }
def search(class_='__init__', function='askvalue'):
    print(text[class_][function])
