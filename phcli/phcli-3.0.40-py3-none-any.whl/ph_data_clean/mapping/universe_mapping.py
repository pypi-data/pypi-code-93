# -*- coding: utf-8 -*-

def universe_blue_grey_mapping():
    return [
        {
            "blue_col_name": "PHA_ID",
            "grey_col_name": ["3#PHA ID", "3#PHA_ID"],
        },
        {
            "blue_col_name": "PHA_HOSP_NAME",
            "grey_col_name": ["2#PHA Hospname", "2#PHA_Hospname"],
        },
        {
            "blue_col_name": "SPECIALTY_CATE",
            "grey_col_name": ["29#Specialty_1", ],
        },
        {
            "blue_col_name": "SPECIALTY_ADMIN",
            "grey_col_name": ["30#Specialty_2", ],
        },
    ]


def universe_blue_orange_mapping():
    return [
        {
            "blue_col_name": "PHA_HOSP_NAME",
            "orange_col_name": ["63#医院名称", ],
        },
        {
            "blue_col_name": "PROVINCE",
            "orange_col_name": ["64#省份", ],
        },
        {
            "blue_col_name": "CITY",
            "orange_col_name": ["65#城市", ],
        },
        {
            "blue_col_name": "DISTRICT",
            "orange_col_name": ["66#区/县", ],
        },
        {
            "blue_col_name": "HOSP_LEVEL",
            "orange_col_name": ["67#医院级别", ],
        },
        {
            "blue_col_name": "HOSP_QUALITY",
            "orange_col_name": ["70#公立/私立", ],
        },
        {
            "blue_col_name": "SPECIALTY_CATE",
            "orange_col_name": ["68#综合/专科", ],
        },
        {
            "blue_col_name": "SPECIALTY_ADMIN",
            "orange_col_name": ["69#专科类别", ],
        },
        {
            "blue_col_name": "DOCTORS_NUM",
            "orange_col_name": ["72#医生数", ],
        },
        {
            "blue_col_name": "ANNU_DIAG_TIME",
            "orange_col_name": ["78#年诊疗人次", ],
        },
        {
            "blue_col_name": "OUTP_DIAG_TIME",
            "orange_col_name": ["79#门诊诊次", ],
        },
    ]
