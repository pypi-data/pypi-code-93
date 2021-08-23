CONFIG = {
    'log': {
        'level': 'DEBUG',   # 与log库的level一致，包括DEBUG, INFO, ERROR
                            #   DEBUG   - Enable stdout, file, mail （如果在dest中启用）
                            #   INFO    - Enable file, mail         （如果在dest中启用）
                            #   ERROR   - Enable mail               （如果在dest中启用）
        'dest': {
            'stdout': 1, 
            'file': 1, 
            'mail': 1       # 0     - 不使用； 
                            # 1     - 使用，收件人使用mail中设置的to；
                            # 字符串 - 直接指定收件人， Ex. : 'Henry TIAN <chariothy@gmail.com>'
        }
    },
    'mail': {
        'from': 'Henry TIAN <chariothy@gmail.com>',
        'to': 'Henry TIAN <chariothy@gmail.com>,Henry TIAN <6314849@qq.com>'
    },
    'smtp': {
        'host': 'smtp.google.com',
        'port': 25,
        'user': 'chariothy@gmail.com',
        'pwd': '123456'
    }
}