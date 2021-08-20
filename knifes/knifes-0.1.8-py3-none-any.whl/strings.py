def desensitizePhone(phone):
    return '****'.join([phone[:3], phone[7:]])


def abbreviate(text, maxLen=2, marker='...'):
    if len(text) > maxLen:
        return text[0:maxLen] + marker
    else:
        return text
