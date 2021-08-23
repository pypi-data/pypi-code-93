class Polynomials:
    def __init__(self, string):
        if isinstance(string, str):
            self.string = string
            self.particles = string.replace("-", "+-").split("+")  # 分成几部分
        elif isinstance(string, list):
            self.particles = string
            self.string = "+".join(string).replace("+-", "-")

    def __str__(self):
        return self.string

    def __add__(self, other):
        if isinstance(other, Polynomials):
            k = self.particles
            k.extend(other.particles)
            return Polynomials(k)
        elif isinstance(other, (int, float)):
            k = self.particles
            k.append(str(other))
            return Polynomials(k)

    def get_value(self, **names):
        particles = []
        for i in self.particles:
            i = i.replace('^', '**')
            for j in i:  # 寻找每部分第一个是字母的字符
                if j.isalpha():
                    break
                    # 有字母！滨江这个字母命名J
            else:
                j = "-------------------------------------------绝对不会包含在多项式里的东西----------------------------------"
                # 这项是纯数字
            k = i.find(j)  # 看看这个字母的位置！
            if k != -1:  # 找到了这个字母（这项不是纯数字）
                if k != 0:
                    if not (i[k - 1] == "*" or i[k - 1] == "/"):
                        i = i[0:k] + "*" + '*'.join(i[k:])  # 当前面无符号时把字母和数字键添加称号
                tmp = []
                tmp2 = [j for j in i if j.isalpha()]  # 寻找所有子母
                for j in tmp2:
                    if j not in tmp:
                        tmp.append(j)  # 去重
                del tmp2  # 烧掉辅助
                for j in tmp:
                    i = i.replace(j, str(names[j]))  # @1048576你忘记赋值给i了。。
                particles.append(i)

            else:
                particles.append(i)

        return sum([eval(i) for i in particles])  # 最后求和
    def solve_linear(self,result):
        #TODO
        pass



if __name__ == "__main__":
    print(Polynomials("2xy").get_value(x=10,y=20))
