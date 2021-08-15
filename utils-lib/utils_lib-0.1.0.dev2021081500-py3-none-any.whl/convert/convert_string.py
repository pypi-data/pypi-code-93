
class ConvertString (object):
    @staticmethod
    def list_to_string (source_list, sep='|'):
        """
        Convert the list to string. (With special character)

        @params [IN] source_list : The list of string convert to string.
        @params [IN] sep         : The character use to seperate the different
                                   element.

        @return      string      : Combine the string to specific character.
        """
        string = ""
        if len (source_list) == 0:
            pass
        else:
            # 使用特殊符號作區隔
            for sub_list in source_list:
                string = string + sep + str (sub_list)

            string = string[1:]

        return string