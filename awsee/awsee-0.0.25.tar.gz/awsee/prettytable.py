import sys, os
from awsee.utils import Utils
from awsee.style import Style
import locale
import xlsxwriter
from os.path import expanduser

class PrettyTable:

    idx_lin            = 0
    content            = []
    columentSorted     = -1
    sizeColumns        = None
    qtdeColumns        = 0
    header             = None
    printedTable       = ""
    addlineSeparator   = True
    groupSeparator     = {}
    sortTablePerformed = False
    ascendingSortOrder = False
    numberSeparator    = False

    def __init__(self, header):
        self.content = []
        self.idx_lin = 0
        self.header  = header

    def isEmpty(self):
        if len(self.content) > 0:
           return False
        return True

    def modifyHeader(self, newHeader):
        self.header = newHeader

    def addRow(self, columns):
        if len(self.header) != len(columns):
            print("HOUSTON, WE HAVE A PROBLEM! The size of Header does not match with this row of columns %d != %d" %( len(self.header), len(columns)) )
            print("Header=" + str(self.header))
            print("Columns=" + str(columns))
            raise ValueError("Header number not macthing the Columns")
            sys.exit()

        # How many columns I will have
        if self.qtdeColumns == 0:
           self.qtdeColumns = len(columns)
        else:
           if len(columns) < self.qtdeColumns or len(columns) > self.qtdeColumns:
               print("HOUSTON, WE HAVE A PROBLEM! This line of columns if invalid, does not have the size of %d" %self.qtdeColumns)
               sys.exit()

        # Define the length of each column by the larger one
        idx_col=0
        # Initiate the Size of Columns if not yet
        marginsLeftRightTotal = 2
        if not self.sizeColumns:
            self.sizeColumns = [0] * len(self.header)
            for header in self.header:
                sizeCol = len(header) + marginsLeftRightTotal
                # In case the columne is smaller than 2, let's put 4
                if sizeCol <= 2:
                    sizeCol += 4
                self.sizeColumns[idx_col] = sizeCol
                idx_col+=1

            # Check the first Line inserted (in case the table has only this one)    
            idx_col=0
            for col in columns:
                # Remove Characters for Colors (do not imply on the size (are invisible))
                col = Utils.removeCharsColors(col)
                addExtraSize = self.checkExtrSizeForNumberFormat(col)    
                if (len(str(col)) + marginsLeftRightTotal + addExtraSize) > (self.sizeColumns[idx_col]):
                   self.sizeColumns[idx_col] = len(str(col)) + marginsLeftRightTotal + addExtraSize
                idx_col+=1    
        else:    
            # If already initiated, iterate and replace only the values with greater length
            for col in columns:
                # Remove Characters for Colors (do not imply on the size (are invisible))
                col = Utils.removeCharsColors(col)
                addExtraSize = self.checkExtrSizeForNumberFormat(col)    
                if (len(str(col)) + marginsLeftRightTotal + addExtraSize) > (self.sizeColumns[idx_col]):
                   self.sizeColumns[idx_col] = len(str(col)) + marginsLeftRightTotal + addExtraSize
                idx_col+=1   

        # Store the values at a new row
        self.content.insert(self.idx_lin, columns)
        self.idx_lin+=1

    def writeExcel(self, excelFileName):
        TMP_EXCEL_PATH = expanduser("~") + ""
        #TMP_EXCEL_PATH = "/mnt/c/Users/Equipo/"
        excelColumns = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','X','Y','W','Z']

        file = os.path.join(TMP_EXCEL_PATH,"{}_{}.xlsx".format(excelFileName, Utils.labelTimestamp()))
        workbook = xlsxwriter.Workbook(file)
        worksheet = workbook.add_worksheet()
        for idx_col, header in enumerate(self.header):
            cell  = excelColumns[idx_col] + "1"
            value = Utils.removeCharsColors(header)
            worksheet.write(cell, value)

        
        for idx_row, row in enumerate(self.content):
            """ if str(self.content[idx_row][1]).startswith("-----") or \
               str(self.content[idx_row][1]).startswith("=====") or \
               str(self.content[idx_row][1]).strip().rstrip() == "":
               # Do not write a line with second col with dashes, it is a Inner Group Separator or Group Separator (not useful for excel sheet)
               pass
            else: """
            for idx_col, val in enumerate(row):
                cell  = excelColumns[idx_col] + str(idx_row + 2)
                value = Utils.removeCharsColors(val)
                worksheet.write(cell, value)

        workbook.close()

    def checkExtrSizeForNumberFormat(self,col):
        addExtraSize = 0
        if not self.numberSeparator or not self.is_number(col):
           return addExtraSize

        if int(col) > 999999999:     
            addExtraSize = 3
        elif int(col) > 999999:     
            addExtraSize = 2    
        elif int(col) > 999:
            addExtraSize = 1    
        return addExtraSize    

    def sortByColumn(self, col):
        if self.columentSorted == -1 or self.columentSorted != col:
           self.sortTablePerformed = False

        self.columentSorted = col;

    def addSeparatorGroup(self):
        row = len(self.content) + 1;
        self.groupSeparator[str(row)] = True

    def sortTable(self):
        #Check if the chosen column is numneric of string for the sort
        isSortColumnNumeric = False

        idx_col = 0
        for line in self.content:
            if self.columentSorted == idx_col:
                if self.is_number(line[idx_col]):
                   isSortColumnNumeric = True
                   break

        if isSortColumnNumeric:
           self.content.sort(key=lambda x:int(x[self.columentSorted]), reverse=not self.ascendingSortOrder)
        else:   
           self.content.sort(key=lambda x:x[self.columentSorted], reverse=not self.ascendingSortOrder)

        self.sortTablePerformed = True   

    def printMe(self, origin, addlineSeparator, tableArgs=None):
        self.addlineSeparator = addlineSeparator
        # Implements in the future other formats
        format = "ASCII"

        if not self.sortTablePerformed:
           self.sortTable()

        if format == "ASCII":
           self.printMeInAscii(tableArgs)

        # Excel File
        if tableArgs.excelFile:
           self.writeExcel(origin)

        # TODO: one day maybe
        #self.printMeInHtml(tableArgs)

        return self.printedTable

    def printHeader(self):
        self.printedTable += self.lineSeparator() + "\n"
        vlr_row = "| "
        idx_col = 0
        for header in self.header:
            number_remain_space = self.sizeColumns[idx_col] - len(header)
            space_remaining     = ' '.ljust(number_remain_space,' ')
            value               = Style.BLUE + header + Style.RESET + space_remaining + Style.RESET
            vlr_row             = vlr_row + value
            idx_col+=1
            vlr_row += "| "    
        self.printedTable += vlr_row + "\n"
        self.printedTable += self.lineSeparator() + "\n"


    def printMeInHtml(self, tableArgs=None):
        #locale.setlocale(locale.LC_ALL, 'es_ES')       
        locale.setlocale(locale.LC_ALL, '')       

        # idx_row = 0
        # for row in self.content:
        #     idx_row       += 1
        #     vlr_row       = ""
        #     idx_col       = 0
        #     for col in row:
        #         value = str(col)
        #         if self.is_number(col):
        #            decimalPlaces = 0
        #            if isinstance(col, (float)):
        #               numberCol     = float(col)
        #               decimalPlaces = 2
        #            else:
        #               numberCol = int(col)
        #            vlrNumber = Utils.formatNumber(numberCol,3,decimalPlaces,True) if self.numberSeparator and numberCol > 999 else str(col)
        #            value = vlrNumber
        #         vlr_row = vlr_row + "|" + value
        #         idx_col+=1
        #     vlr_row += "| "   

        #     # Mark the Line Number in case there's a highlight --> a " | value " as complement in the command
        #     originalHighLightValue = self._isThereHighLightValueSeeked(vlr_row, tableArgs)
        #     if originalHighLightValue:
        #        vlr_row = Utils.removeCharsColors(vlr_row)                          
        #        vlr_row = highLightValue_backGroundColor + Style.BLACK + vlr_row.strip() + Style.RESET
        #        vlr_row = vlr_row.replace(originalHighLightValue, Style.IBLUE + originalHighLightValue + Style.BLACK )

        #     # Check if filter were requested " | grep value"
        #     if not tableArgs.filterValue or tableArgs.filterValue.strip() == "":
        #        # if not, print everything
        #        self.printedTable += vlr_row + "\n"
        #     else:
        #        # otherwise only if if presented on the current line   
        #        originalFilterValue = self._isThereFilterValueSeekd(vlr_row, tableArgs)
        #        if originalFilterValue:
        #           vlr_row = vlr_row.replace(originalFilterValue, Style.IBLUE + originalFilterValue + Style.GREEN ) 
        #           self.printedTable += vlr_row + "\n" 
            
        #     if self.addlineSeparator:
        #        self.printedTable += self.lineSeparator() + "\n"
        #     # In case the Group Separator was asked, close the group when is the case (end of a group, Ex: All the Subnets of a VPC List)
        #     # If sort was asked, do not add group separator anymore (not sorted approprietaly anymore, group separator does not make sense with sort)   
        #     if str(idx_row + 1) in self.groupSeparator and (self.columentSorted == 0 and self.ascendingSortOrder):
        #        self.printedTable += self.lineGroupSeparator() + "\n" 
        
        # # Just close the table, even though the line separator wasn't requested
        # # Mandatory close even if the option for LineSeparator wasnt required (to close the table, not separate the line)
        # # If sort was asked, do not add group separator anymore (not sorted approprietaly anymore, group separator does not make sense with sort)   
        # if not self.addlineSeparator and not (str(idx_row + 1) in self.groupSeparator and self.columentSorted == 0 and self.ascendingSortOrder):
        #    self.printedTable += self.lineSeparator() + "\n"

    def printMeInAscii(self, tableArgs=None):
        self.printHeader()

        #locale.setlocale(locale.LC_ALL, 'es_ES')       
        locale.setlocale(locale.LC_ALL, '')       

        #highLightValue_backGroundColor = '\033[103m'
        highLightValue_backGroundColor = '\033[104m'

        idx_row = 0
        for row in self.content:
            idx_row       += 1
            vlr_row       = ""
            idx_col       = 0
            for col in row:
                addExtraSize        = self.checkExtrSizeForNumberFormat(col)
                lenCol              = len(Utils.removeCharsColors(str(col))) + addExtraSize
                number_remain_space = self.sizeColumns[idx_col] - lenCol
                space_remaining     = ' '.ljust(number_remain_space,' ')
                value               = Style.GREEN + " " + str(col) + space_remaining + Style.RESET
                if self.is_number(col):
                   decimalPlaces = 0
                   if isinstance(col, (float)):
                      numberCol     = float(col)
                      decimalPlaces = 2
                   else:
                      numberCol = int(col)
                   vlrNumber = Utils.formatNumber(numberCol,3,decimalPlaces,True) if self.numberSeparator and numberCol > 999 else str(col)
                   value = space_remaining + Style.GREEN + vlrNumber + Style.RESET + " "
                vlr_row = vlr_row + "|" + value
                idx_col+=1
            vlr_row += "| "   

            # Mark the Line Number in case there's a highlight --> a " | value " as complement in the command
            originalHighLightValue = self._isThereHighLightValueSeeked(vlr_row, tableArgs)
            if originalHighLightValue:
               vlr_row = Utils.removeCharsColors(vlr_row)                          
               vlr_row = highLightValue_backGroundColor + Style.BLACK + vlr_row.strip() + Style.RESET
               vlr_row = vlr_row.replace(originalHighLightValue, Style.BLACK + originalHighLightValue + Style.BLACK )

            # Check if filter were requested " | grep value"
            if not tableArgs.filterValue or tableArgs.filterValue.strip() == "":
               # if not, print everything
               self.printedTable += vlr_row + "\n"
            else:
               # otherwise only if if presented on the current line   
               originalFilterValue = self._isThereFilterValueSeekd(vlr_row, tableArgs)
               if originalFilterValue:
                  vlr_row = vlr_row.replace(originalFilterValue, Style.IBLUE + originalFilterValue + Style.GREEN ) 
                  self.printedTable += vlr_row + "\n" 
            
            if self.addlineSeparator:
               self.printedTable += self.lineSeparator() + "\n"
            # In case the Group Separator was asked, close the group when is the case (end of a group, Ex: All the Subnets of a VPC List)
            # If sort was asked, do not add group separator anymore (not sorted approprietaly anymore, group separator does not make sense with sort)   
            if str(idx_row + 1) in self.groupSeparator and (self.columentSorted == 0 and self.ascendingSortOrder):
               self.printedTable += self.lineGroupSeparator() + "\n" 
        
        # Just close the table, even though the line separator wasn't requested
        # Mandatory close even if the option for LineSeparator wasnt required (to close the table, not separate the line)
        # If sort was asked, do not add group separator anymore (not sorted approprietaly anymore, group separator does not make sense with sort)   
        if not self.addlineSeparator and not (str(idx_row + 1) in self.groupSeparator and self.columentSorted == 0 and self.ascendingSortOrder):
           self.printedTable += self.lineSeparator() + "\n"

    def _isThereFilterValueSeekd(self,line,tableArgs):
        if not tableArgs.filterValue or tableArgs.filterValue.strip() == "":
           return None
        originalFilterValue = None   
        filterValueIndex = str(line).lower().find(tableArgs.filterValue.strip().lower())
        if filterValueIndex > -1:
           originalFilterValue = str(line)[filterValueIndex:filterValueIndex+len(tableArgs.filterValue)]
        return originalFilterValue   

    def _isThereHighLightValueSeeked(self, line, tableArgs):
        originalHighLightValue = None
        if not tableArgs.highlightValue or tableArgs.highlightValue.strip() == "":
           return originalHighLightValue
        highLightValueIndex = str(line).lower().find(tableArgs.highlightValue.strip().lower())
        if highLightValueIndex > -1:
           # Grab the original value format (capital letter, small letter format, etc) to colorize below 
           originalHighLightValue = str(line)[highLightValueIndex:highLightValueIndex+len(tableArgs.highlightValue)]
        return originalHighLightValue

    def lineSeparator(self):
        lineSeparator = ""
        for colLength in self.sizeColumns:
            diff = 2
            lineSeparator += '+'.ljust(colLength + diff,'-')
        return lineSeparator + "+"

    def lineGroupSeparator(self):
        lineSeparator = ""
        for colLength in self.sizeColumns:
            diff = 2
            lineSeparator += '+'.ljust(colLength + diff,'-')
        return lineSeparator + "+"     

    def ascendingOrder(self, ascending):
        self.ascendingSortOrder = ascending

    def sortByColumn(self, column):
        if column > self.qtdeColumns:
           print("HOUSTON, WE HAVE A PROBLEM! There's no so much column on your table, check it again")
           raise ValueError("Header number not macthing the Columns")
           sys.exit()
        self.columentSorted = column

    def is_number(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False        