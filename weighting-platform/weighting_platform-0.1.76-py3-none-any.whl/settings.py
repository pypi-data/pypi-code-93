""" Пакет содержит все настройки """
# Словарь содержит описание порядков открывания из протоколов авто согласно
# тому, с какой стороны машины подъехала (курс используется как ключ)
protocol_gate_description_dict = {'external':
                                      {'near': 'external', 'far': 'internal'},
                                  'internal':
                                      {'near': 'internal', 'far': 'external'}}