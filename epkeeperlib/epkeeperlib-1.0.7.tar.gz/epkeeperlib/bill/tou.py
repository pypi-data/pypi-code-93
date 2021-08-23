TOU_HOUR = {
    310000: {  # 上海
        1: {  # 夏季
            "month": [7, 8, 9],
            "tip": [],
            "peak": [8, 9, 10, 13, 14, 18, 19, 20],
            "flat": [6, 7, 11, 12, 15, 16, 17, 21],
            "valley": [0, 1, 2, 3, 4, 5, 22, 23],
        },
        2: {  # 非夏季
            "month": [1, 2, 3, 4, 5, 6, 10, 11, 12],
            "tip": [],
            "peak": [8, 9, 10, 18, 19, 20],
            "flat": [6, 7, 11, 12, 13, 14, 15, 16, 17, 21],
            "valley": [0, 1, 2, 3, 4, 5, 22, 23],
        }
    },
    460000: {  # 海南
        "month": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "tip": [],
        "peak": [10, 11, 16, 17, 18, 19, 20, 21],
        "flat": [7, 8, 9, 12, 13, 14, 15, 22],
        "valley": [0, 1, 2, 3, 4, 5, 6, 23],
    },
    430000: {  # 湖南
        "month": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "tip": [19, 20, 21],
        "peak": [8, 9, 10, 15, 16, 17, 18],
        "flat": [7, 11, 12, 13, 14, 22],
        "valley": [0, 1, 2, 3, 4, 5, 6, 23],
    }
}


def get_season_code(province: int, month: int):
    if int(province) == 310000:
        if int(month) in range(7, 10):
            season_code = 1
        else:
            season_code = 0
        return season_code
    else:
        return


def get_tou_hour(province: int, season_code=None):
    hour = TOU_HOUR[province]
    if season_code:
        hour = hour[season_code]
    return hour
