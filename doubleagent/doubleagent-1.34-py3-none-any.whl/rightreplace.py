def rightreplace(string, target, replace, count_right):
    repeat = 0
    text = string
    target_len = len(target)

    count_find = string.count(target)
    if count_right > count_find:  # 바꿀 횟수가 문자열에 포함된 target보다 많다면
        repeat = count_find  # 문자열에 포함된 target의 모든 개수(count_find)만큼 교체한다
    else:
        repeat = count_right  # 아니라면 입력받은 개수(count)만큼 교체한다

    while(repeat):
        find_index = text.rfind(target)  # 오른쪽부터 index를 찾기위해 rfind 사용
        text = text[:find_index] + replace + text[find_index+target_len:]

        repeat -= 1

    return text
