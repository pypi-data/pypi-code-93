class TableTemplete():

    #dc 是一个字典类型,key是jsonObject中的key, value是该key所对应的页面上的名称
    #例如 jsonObject={documentNum:"广公机场（二派）行罚决[2020]40"}
    # dc = {"documentNum":"发文字号"}
    @staticmethod
    def getTableHtmlByDictionaryAndJson(dc,jsonObject,type):
        if(type ==1):
            return TableTemplete.crosswiseTableTemplete(dc,jsonObject)
        else:
            return TableTemplete.columnTableTemplete(dc,jsonObject)

    #table的标题是纵向显示
    @staticmethod
    def columnTableTemplete(dc,jsonObject):
        string_list  = []
        if(len(dc)> 0):
            string_list.append("<table border=\"1\">")
            for key,value in dc.items():
                json_value = jsonObject[key]
                td_value =  '' if json_value == None else json_value
                string_list.append("<tr><td>"+str(value)+": </td><td>"+str(td_value)+"</td></tr>")
            string_list.append("</table>")

        return "".join(string_list)

    # table的标题是横向显示
    @staticmethod
    def crosswiseTableTemplete(dc,jsonObject):
        table_list = []
        value_list =[]
        if (len(dc) > 0):
            table_list.append("<table border=\"1\">")
            #拼接表头
            table_list.append("<tr>");
            for key, value in dc.items():
                table_list.append("<td>"+str(value)+"</td>")
                value_list.append(key);
            table_list.append("</tr>");
            #拼接内容
            table_list.append("<tr>");
            for value in value_list:
                json_value = jsonObject[value]
                td_value = '' if json_value == None else json_value
                table_list.append("<td>" + str(td_value) + "</td>")
            table_list.append("</tr>");
            table_list.append("</table>")
        return "".join(table_list)

    # table的标题是纵向显示
    @staticmethod
    def columnTableTempleteByDictionary(dc):
        string_list = []
        if (len(dc) > 0):
            string_list.append("<table border=\"1\" style='width:70%'>")
            for key, value in dc.items():
                td_value = '' if value == None else value
                string_list.append("<tr><td>" + str(key) + ": </td><td>" + str(td_value) + "</td></tr>")
            string_list.append("</table>")

        return "".join(string_list)
    # table的标题是横向显示
    @staticmethod
    def crosswiseTableTempleteByDictionary(dc):
            table_list = []
            value_list = []
            if (len(dc) > 0):
                table_list.append("<table border=\"1\">")
                # 拼接表头
                table_list.append("<tr>");
                for key, value in dc.items():
                    table_list.append("<td>" + str(key) + "</td>")
                    value_list.append(value);
                table_list.append("</tr>");
                # 拼接内容
                table_list.append("<tr>");
                for value in value_list:
                    td_value = '' if value == None else value
                    table_list.append("<td>" + str(td_value) + "</td>")
                table_list.append("</tr>");
                table_list.append("</table>")
            return "".join(table_list)
