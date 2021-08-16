
class SASFile:
    def __init__(self, sas_stream):
        self.invarians = list()
        begin_operator = False
        end_operator = False
        for line in sas_stream:
            line = line.strip()
            if 'begin_operator' == line:
                begin_operator = True
                continue
            if begin_operator:
                begin_operator = False
                line = line.split(' ')
                self.invarians.append(line)
    
    def __str__(self):
        lines = []
        for invariant in self.invarians:
            lines.append( " ".join(invariant))
        return "\n".join(lines)
