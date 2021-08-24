from shangqi_cloud_lib.utils.ElasticsearchUtil import es_condition_by_match_phrase, es_condition_by_not_null, \
    es_condition_by_exist


def common_format_list_tags(result_tags, insert_tags, tags_index=10):
    if insert_tags is not None and len(insert_tags) > 0:
        insert_tag_list = insert_tags[0:tags_index]
        for tag in insert_tag_list:
            if isinstance(tag, str):
                if tag and tag.strip() != "":
                    result_tags.append(tag)


def common_format_string_tags(result_tags, data, key):
    if data.get(key) is not None and data.get(key) != "":
        result_tags.append(data.get(key))
    return result_tags

"""

# 政策通 政策标签
def format_policy_tags(policy):
    shangqi_tags = policy.get("tags",{})

    result_tags = {
        "support_object":policy.get("support_object", []),
        "support_way":policy.get("support_way", [])
    }

    common_format_list_tags(tags, )

    common_format_list_tags(tags, policy.get("support_behavior", []))
    common_format_string_tags(tags, policy, "is_declare")
    if shangqi_tags:
        industry_tags = [data["tag_name"] for data in shangqi_tags.get("industry_tag",[])]
        certification_tags = shangqi_tags.get("certification_tag",[])
        common_format_list_tags(tags, industry_tags)
        common_format_list_tags(tags, certification_tags)

    tags_list = [{
        "type": "other",
        "tabs": tags
    }]
    if policy.get("tags"):
        tags = policy["tags"]
        tags_list.append({
            "type": "产业类型",
            "tabs": [data["tag_name"] for data in tags.get("industry_tag", [])]
        })
    return tags_list


"""


def format_param_tag(self, bool_should_more_list, especial_tag_list):
    bool_should_list = []
    if especial_tag_list is not None:
        for tag in especial_tag_list:
            if tag in ["单项冠军", "小巨人", "瞪羚企业", "一条龙", "专精特新"]:
                es_condition_by_match_phrase(bool_should_list, "tags.national_tag.tag_name", tag)
            if tag in ["单项冠军", "隐形冠军", "成长", "小巨人", "瞪羚企业", "首台套", "专精特新","雏鹰"]:
                es_condition_by_match_phrase(bool_should_list, "tags.province_tag.tag_name", tag)
            if tag in ["雏鹰"]:
                es_condition_by_match_phrase(bool_should_list, "tags.city_tag.tag_name", tag)
            if tag in ["雏鹰"]:
                es_condition_by_match_phrase(bool_should_list, "tags.district_tag.tag_name", tag)
            if tag in ["独角兽"]:
                es_condition_by_match_phrase(bool_should_list, "tags.rank_tag.rank_name", tag)
            if tag in ["瞪羚企业"]:
                es_condition_by_match_phrase(bool_should_list, "tags.park_tag.tag_name", tag)
            if tag == "高新技术企业":
                es_condition_by_match_phrase(bool_should_list, "tags.certification.certification_name.keyword", tag)
            if tag == "上市企业":
                es_condition_by_exist(bool_should_list, "tags.market_tag")
    bool_should_more_list.append(bool_should_list)