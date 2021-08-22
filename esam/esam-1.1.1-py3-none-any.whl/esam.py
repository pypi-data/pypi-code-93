import logging
import operator
import eons
import json
import jsonpickle
import sys
import os
import argparse
from abc import abstractmethod

######## START CONTENT ########

class Serializable(json.JSONEncoder):

    def ToJSON(self):
        return jsonpickle.encode(self)

    #This isn't necessary.
    #Problem: How do you know what object to call FromJSON on if the class is defined in the json, which has not yet been read?
    # def FromJSON(self, json):
    #     #TODO: can we make this safer?
    #     self = jsonpickles.decode(jsonEncoding)

#Extends eons.Datum so that it can be serialized for saving and loading.
#Also adds logic for knowing how close of a match *this is to a known value (i.e other Data)
#Derive from this class to create data structures for your species!
class Datum(eons.Datum, Serializable):

    def __init__(self, name=eons.INVALID_NAME()):
        super().__init__(name=name)

        #A unique id states that any 2 Data with the same id are, in fact, the same, regardless of what else might vary.
        #This should be a time-based value, etc.
        #For example, if you measure some chemical species that elutes off a column at a given rate, it won't matter how much eluate is present between different runs of the experiment, the time taken to observe the substance uniquely identifies that species.
        #Unique, time-based ids are especially valuable when there are multiple candidates vying for the same name (per names based on known time-based values). This underlies the bestMatch system, below.
        self.uniqueId = 0

        #Children of *this might have similar characteristics to one another (eons.g. if there is contamination in the sample)
        #Because of that, children are permitted to know about each other only in terms of whether or not they are the best of their classification
        #Using this is optional, so it defaults to Trues.
        #See IsBetterMatchThan, below, for more info.
        self.bestMatch = True

        #The nameMatchDiscrepancy is the difference between the known and experimental values.
        #This is useful when trying to determine bestMatch through comparison with other children.
        #We can then account for noisy data by how off a child is to what we expect.
        self.nameMatchDiscrepancy = 0

    #RETURNS: bestMatch
    def IsBestMatch(self):
        return self.bestMatch == True

    def SetBestMatch(self, newValue):
        self.bestMatch = newValue

    #Use a formula to pick out which children are the best fits for their names.
    #RETURNS: a boolean favoring self (true) or compare (false)
    #The caller can use this information to set self.bestMatch.
    #Basically, this says that stronger signals and more accurate signals are both equally valid metrics in determining the correct label for a children. These metrics obviously vary with each data set (some data are more precise and have large signals, causing this function to weight strength more heavily than accuracy, and vice versa). However, this rough calculation should serve for most data. Plus, hey, it's Python. Hack this!
    def IsBetterMatchThan(self, compare, attribute):
        try:
            selfValue = getattr(self, attribute)
            compareValue = getattr(compare, attribute)
            if(self.nameMatchDiscrepancy != 0):
                selfValue /= abs(self.nameMatchDiscrepancy)
            if(compare.nameMatchDiscrepancy != 0):
                compareValue /= abs(compare.nameMatchDiscrepancy)
        except Exception as e:
            logging.error(f"Error comparing {self.name} and {compare.name}: {e.message}")
            return False;

        return selfValue > compareValue


#SampleSets extend eons.DataContainers by adding extra logic for use with esam.Data. In particular are means of comparing unknown Data to known Data and operations involving uniqueIds.
class SampleSet(eons.DataContainer, Serializable):
    def __init__(self, name=eons.INVALID_NAME()):
        super().__init__(name)

    #RETURNS: the sum of datumAttribute for all data
    #If bestMatch is True, only Data with bestMatch of True will be summed.
    #If ignoreNames is specified, any Data of those names will be ignored.
    def GetDatumTotal(self, datumAttribute, bestMatch = False, ignoreNames = []):
        try:
            ret = 0
            for d in self.data:
                if (bestMatch and not d.bestMatch):
                    continue
                if (ignoreNames and d.name in ignoreNames):
                    continue
                ret += getattr(d, datumAttribute)
            return ret
        except Exception as e:
            logging.error(f"{self.name} - {e.message}")
            return 0

    #RETURNS: the Data with an absolute maximum (or minimum) of the given attributes.
    #For useful relations, see https://docs.python.org/3/library/operator.html.
    def GetDatumOfExtremeRelation(self, datumAttribute, relation):
        try:
            ret = None
            toBeat = 0 #FIXME: Possible bugs here if looking for a maximum of negative values, etc.
            for d in self.data:
                if (relation(getattr(d, datumAttribute), toBeat)):
                    toBeat = getattr(d, datumAttribute)
                    ret = d
            return d
        except Exception as e:
            logging.error(f"{self.name} - {e.message}")
            return self.InvalidDatum()

    #RETURNS: the smallest gap between unique ids in data
    def GetSmallestGapOfUniqueIds(self, shouldSort=True):
        if (shouldSort):
            self.SortData()

        gap = 1000000 #too big #FIXME: Arbitrary values.
        for i in range(len(self.data)):
            if (i == len(self.data)-1):
                break #we look at i and i+1, so break before last i
            dUI = abs(self.data[i].uniqueId - self.data[i+1].uniqueId)
            if (dUI < gap):
                gap = dUI
        return gap

    #RETURNS: the Data past the starting id, which has an attribute that is of the given relation to both Data next to it.
    #RETURNS: InvalidDatum() if the requested value does not exist
    #startingId will be adjusted to the first valid id that is >= to startingId
    def GetNextLocalExtremity(self, startingId, datumAttribute, relation, shouldSort=True):
        if (shouldSort):
            self.SortData()

        #check corner cases first
        if (startingId >= self.data[-1].uniqueId): #startingId is too high.
            return self.InvalidDatum()

        try:
            for i in range(len(self.data)):
                if (self.data[i].uniqueId < startingId):
                    continue
                if (not self.data[i].IsValid()):
                    continue
                if (i == 0):
                    if (relation(getattr(self.data[i], datumAttribute), getattr(self.data[i+1], datumAttribute))):
                        return self.data[i]
                    else:
                        continue
                if (i == len(self.data)-1):
                    if (relation(getattr(self.data[i], datumAttribute), getattr(self.data[i-1], datumAttribute))):
                        return self.data[i]
                    else:
                        return self.InvalidDatum()
                if (relation(getattr(self.data[i], datumAttribute), getattr(self.data[i+1], datumAttribute)) and relation(getattr(self.data[i], datumAttribute), getattr(self.data[i-1], datumAttribute))):
                    return self.data[i]
        except Exception as e:
            logging.error(f"{self.name} - {e.message}")
            return self.InvalidDatum()


    #RETURNS: a list of all Data in *this that are local extremities of the given relation.
    def GetAllLocalExtremities(self, datumAttribute, relation, shouldSort=True):
        if (shouldSort):
            self.SortData()

        startingId = self.data[0].uniqueId
        ret = SampleSet()
        while (True):
            tempData = self.GetNextLocalExtremity(startingId, datumAttribute, relation, False)
            startingId = tempData.uniqueId
            if (tempData.IsValid()):
                ret.AddDatum(tempData)
            else:
                return ret

    #Uses a standard to translate raw data into a usable ratio.
    #Basically, this gives someDatum.datumAttribute / standard.datumAttribute * self.stdAttribute / self.selfAttribute, for each Data in *this. This value is stored in each Data under datumAttributeToSet.
    #REQUIREMENTS:
    #   1. all Data have been labeled
    #   2. all Data have a valid, numeric datumAttribute
    #   3. the stdName provided matches a Datum within *this
    #   4. stdAttribute and selfAttribute are defined and are valid numbers in *this
    #EXAMPLE:
    #   *this, a SampleSet, contains data from a gas chromatograph, which includes a known standard, with name given by stdNames. Each Datum in *this, an individual fatty acid methyl ester, would be an instance of a FAME class, which would be a child of Datum containing a peak area. Thus, the datumAttribute would be something like "peakArea", the member variable of our FAME class. By comparing peak areas, the known mass of the standard can be used to calculate the known mass of each other Datum in *this. Thus, stdAttribute would be something like "mgStd", meaning self.mgStd would return a valid number for *this. We then calculate the attributeFraction by comparing the stdAttribute with the corresponding selfAttribute, in this case the mass of our sample, something like "mgDryWeight". The resulting value is stored in the FAME instance for each Datum, perhaps as a member by name of "percentFA".
    #   This gives us a way to translate raw data into real-world, relevant information, which can be compared between samples.
    #   To recap, we use:
    #       stdName = the name of our standard (eons.g. "C:17")
    #       datumAttribute = peak area (eons.g. "peakArea")
    #       datumAttributeToSet = mg/mg fatty acid ratio (eons.g. "percentFA")
    #       stdAttribute = mg standard in sample (eons.g. "mgStd")
    #       selfAttribute = mg sample used (eons.g. "mgDryWeight")
    #   and we get:
    #       A mg / mg ratio of each fatty acid species to dry weight of samples.
    #   This is given by:
    #       {datum.peak area} / {std.peak area} * {std.mass} / {samples.mass}
    #NOTE: The reason stdAttribute is a member of a SampleSet child and not a Datum child is that calculating the stdAttribute for all Data is almost always meaningless until those values are normalized to how much of each Datum was used in the experiment. Thus, instead of eating up more RAM and CPU time sorting through extra values that won't be used, stdAttribute is only stored once, within *this.
    def CalculateAttributePercent(self, stdName, datumAttribute, datumAttributeToSet, stdAttribute, selfAttribute):
        std = self.GetDatum(stdName)
        if (not std.IsValid()):
            logging.info(f"{self.name} - Percent of {selfAttribute} not calculated: no valid {stdName} found.")
            return
        try:
            fractionDenominator = getattr(self, selfAttribute)
            if (fractionDenominator == 0):
                logging.info(f"Invalid {selfAttribute} in {self.name}")
                return
            
            fractionNumerator = getattr(self, stdAttribute)
            if (fractionNumerator == 0):
                logging.info(f"Invalid {stdAttribute} in {self.name}")
                return

            stdComparator = getattr(std, datumAttribute)
            if (stdComparator == 0):
                logging.info(f"Invalid {datumAttribute} of standard {std.name} in {self.name}")
                return

            attributeFraction = fractionNumerator / fractionDenominator
            for d in self.data:
                if (not d.IsValid()):
                    continue
                if (d.name == "INVALID NAME" or not d.bestMatch):
                    continue
                if (d.name == std.name):
                    continue
                setattr(d, datumAttributeToSet, getattr(d, datumAttribute) /stdComparator * attributeFraction)
        except Exception as e:
            logging.error(f"{self.name} - Error calculating percent {selfAttribute}: {e.message}")
            return

    #Changes name of each Data to be that of the labeledData with the closest unique id.
    def ApplyNamesWithClosestMatchFrom(self, labeledData, shouldSort=True):
        if (shouldSort):
            self.SortData()

        acceptableGapLow = 1 #BIG but not too big.. #FIXME: calculate this?
        for i in range(len(labeledData)):
            if (i != len(labeledData)-1):
                acceptableGapHigh = abs(labeledData[i+1].uniqueId - labeledData[i].uniqueId) / 2
                # logging.info("Next acceptable gap is", acceptableGapHigh, "making range", labeledData[i].uniqueId - acceptableGapLow,"to", labeledData[i].uniqueId + acceptableGapHigh)
            else:
                acceptableGapHigh = 0
            for d in self.data:
                if (d.uniqueId > labeledData[i].uniqueId - acceptableGapLow and d.uniqueId <= labeledData[i].uniqueId + acceptableGapHigh):
                    d.name = labeledData[i].name
                    d.nameMatchDiscrepancy = d.uniqueId - labeledData[i].uniqueId
            acceptableGapLow = acceptableGapHigh

    #Once Data have names, this method may be called to find which one "best" matches its label.
    #This is useful iff 2+ Data have the same label, but not the same id.
    #This method relies on IsBetterMatchThan(...) to determine what a "best" match is.
    def FindBestMatchingData(self, datumAttribute):
        currentName = ""
        matchToBeat = Datum()
        matchToBeat.Invalidate()
        for d in self.data:
            #find local min for nameMatchDiscrepancy
            if (d.name != currentName):
                currentName = d.name
                matchToBeat = d
                d.bestMatch = True
            elif (not matchToBeat.IsValid() or d.IsBetterMatchThan(matchToBeat, datumAttribute)):
                matchToBeat.bestMatch = False
                matchToBeat = d;
                d.bestMatch = True



#A DataFunctor is used for manipulating the contents of a DataContainer
class DataFunctor(eons.UserFunctor):
    def __init__(self, name=eons.INVALID_NAME()):
        super().__init__(name)
        
        self.requiredKWArgs.append("data")

    #Make sure we can use the same functor object for multiple invocations
    #Override this if you add anything to your class that needs to be reset between calls.
    def Clear(self):
        self.data = eons.DataContainer()

    #Override of UserFunctor method.
    def PreCall(self, **kwargs):
        self.Clear()
        self.data = kwargs.get("data")
        

#A IOFormatFunctor is used for reading or writing structured data to / from a files.
#If you inherit from this, you must still override the abstract method UserFunction, from UserFunctor.
class IOFormatFunctor(DataFunctor):
    def __init__(self, name=eons.INVALID_NAME()):
        super().__init__(name)

        self.requiredKWArgs.append("file")

    #See DataFunctor.Clear() for more details.
    def Clear(self):
        super().Clear()
        self.file = None

    #Override of UserFunctor method.
    def PostCall(self, **kwargs):
        if (not self.file.closed):
            self.file.close()


class InputFormatFunctor(IOFormatFunctor):
    def __init__(self, name=eons.INVALID_NAME()):
        super().__init__(name)
        
        #self.data will be returned, so we shouldn't be asking for it.
        self.requiredKWArgs.remove("data")

    #Input Functors will be expected to populate self.data with the contents of self.file
    #The data member will be returned by UserFunction.
    #This is done to help enforce consistency.
    @abstractmethod
    def ParseInput(self):
        raise NotImplementedError

    def UserFunction(self, **kwargs):
        self.file = open(kwargs.get("file"), "r")
        self.ParseInput() #populate self.data
        return self.data

    #Override DataFunctor to ensure we don't try to read the unneeded data kwarg.
    def PreCall(self, **kwargs):
        self.Clear()

class InputSavedJSON(InputFormatFunctor):
    def __init__(self, name=eons.INVALID_NAME()):
        super().__init__(name)

    #Uses jsonpickle to read the contents of self.file into self.data, which is RETURNED by UserFunction (see InputFormatFunctor for implementation).
    def ParseInput(self):
        self.data = jsonpickle.decode(self.file.read())



class OutputFormatFunctor(IOFormatFunctor):
    def __init__(self, name=eons.INVALID_NAME()):
        super().__init__(name)
        
    #Output Functors will be given expected to write the contents of self.data to self.file.
    #self.file will be overwritten!
    #RETURNS: nothing.
    #This is done to help enforce consistency.
    @abstractmethod
    def WriteFile(self):
        raise NotImplementedError

    def UserFunction(self, **kwargs):
        self.file = open(kwargs.get("file"), "w")
        self.WriteFile()
        
        #the point of no return.




class OutputSavedJSON(OutputFormatFunctor):
    def __init__(self, name=eons.INVALID_NAME()):
        super().__init__(name)

    #Uses Serializables.ToJSON of self.data to write to self.file
    def WriteFile(self):
        self.file.write(self.data.ToJSON())



#ESAM: a base class for all Sample analysis and managers.
#Extends eons.Executor to add logic for esam.SampleSets, saving and loading, and working with knowns and unknowns.
class ESAM(eons.Executor):

    def __init__(self, name=eons.INVALID_NAME(), descriptionStr="Sample Analysis and Manager. Not all arguments will apply to all workflows."):

        super().__init__(name=name, descriptionStr=descriptionStr)

        self.InitSaveLoad()

        #All of the following directories should contain UserFunctors.
        #These will be called with a filename, in the case of inputs and outputs, or self.data, in the case of analysis.
        self.RegisterDirectory("sam/analysis")
        self.RegisterDirectory("sam/format/input")
        self.RegisterDirectory("sam/format/output")

        #This path should contain esam.Datum children.
        self.RegisterDirectory("sam/data")
        
    #Data are separated into 2 categories. One for known data, the provided configuration, and the other for unknown data, those provided by input and loaded files.
    #These are easily accessible via the GetConfigData() and GetSampleData() methods, below.
    #Override of eons.Executor method. See that class for more information.
    def InitData(self):
        self.data.append(SampleSet(name="config"))
        self.data.append(SampleSet(name="sample"))

    def InitSaveLoad(self):
        self.loadFunctor = InputSavedJSON()
        self.saveFunctor = OutputSavedJSON()
        
    #Adds command line arguments.
    #Override of eons.Executor method. See that class for more information.
    def AddArgs(self):
        super().AddArgs()
        self.argparser.add_argument('-c','--config-file', type = str, metavar = 'config.xlsx', help = 'File containing configuration data, standards, and known values.', dest = 'configFile')
        self.argparser.add_argument('-cf', '--config-format', type = str, help = 'Format the config file', dest = 'configFormat')
        self.argparser.add_argument('--standard', metavar = 'standardName', type = str, help = 'Name of the standard used', dest = 'std')

        self.argparser.add_argument('-i', '--input-files', metavar = ('input1.xlsx','input2.xlsx'), type = str, help = 'Files to be analyzed.', dest = 'inputFiles', nargs = '*')
        self.argparser.add_argument('-if', '--input-format', type = str, help = 'Format of all input files', dest = 'inputFormat')

        self.argparser.add_argument('-s', '--save-file', metavar = 'saveTo.json', type = str, help = 'Save all data for easy access later.', dest = 'saveFile')
        self.argparser.add_argument('-l', '--load-file', metavar = ('saved1.xlsx', 'saved2.xlsx'), type = str, help = 'Recall a previously analyzed data set.', dest = 'loadFiles', nargs = '*')

        self.argparser.add_argument('-o', '--output-file', metavar = 'output.xlsx', type = str, help = 'Result of analysis.', dest = 'outputFile')
        self.argparser.add_argument('-of', '--output-format', type = str, help = 'Report format to generates.', dest = 'outputFormat')

        self.argparser.add_argument('-f', '--filter-by', metavar = ('name'), type = str, help = 'What parameter to filter by', dest = 'filter',)
        self.argparser.add_argument('--only', metavar = ('sample1','sample2'), type = str, help = 'Only read in samples that match the given list. Does not apply to config data.', dest = 'only', nargs = '*')
        self.argparser.add_argument('--ignore', metavar = ('sample1','sample2'), type = str, help = 'Read in all samples except those listed. Does not apply to config data.', dest = 'ignore', nargs = '*')

        self.argparser.add_argument('-a', '--analyze', metavar = ('analysis_step-1','analysis_step-2'), type = str, help = 'Analyze all data, including previously saved data. Names of analysis functors to be run in order.', dest = 'analysisSteps', nargs = '*')
        self.argparser.add_argument('--analyze-input-only', metavar = ('analysis_step-1','analysis_step-2'), type = str, help = 'Analyze input data only - not loaded data. Names of analysis functors to be run in order.', dest = 'inputOnlyAnalysisSteps', nargs = '*')

    #Override of eons.Executor method. See that class for more information.
    def ParseArgs(self):
        super().ParseArgs()

        if (not self.args.inputFiles and not self.args.loadFiles):
            self.ExitDueToErr("You must specify at least one input file via -i or -l")

        if (self.args.inputFiles and not self.args.inputFormat):
            self.ExitDueToErr(f"Please specify the format of the input files, {self.args.inputFiles}")

        if (self.args.configFile and not self.args.configFormat):
            self.ExitDueToErr(f"Please specify the format of the config file, {self.args.configFile}")

        #Not all workflows may require a config files.
        if (self.args.inputFiles and not self.args.configFile):
            logging.info("No config file specified for the given inputs")

        if (not self.args.outputFile and not self.args.saveFile):
            self.ExitDueToErr("You must specify at least one output file via -o or -s")

        if (self.args.only and self.args.ignore):
            self.ExitDueToErr("Please specify either --only or --ignore, not both (maybe run this command twice, in the order you would like?)")

        if (not self.args.filter and (self.args.only or self.args.ignore)):
            self.ExitDueToErr("Please specify what field to filter by with --filter-by")

        if (not self.args.std):
            logging.info("No standard specified, some analyses may fail")

    #TODO: can we make these faster?
    #TODO: what happens if these ever don't return a pointer?
    def GetConfigData(self):
        return self.GetDatum("config")
    def GetSampleData(self):
        return self.GetDatum("sample")

    #Called with operator () 
    #Override of eons.Executor (i.e. eons.UserFunctor) method. See that class for more information.
    def UserFunction(self, **kwargs):
        super().UserFunction(**kwargs)
        self.IngestConfig()
        self.IngestInputs()
        self.AnalyzeInputOnly()
        self.LoadFiles()
        self.TrimData()
        self.Analyze()
        self.GenerateOutput()

    def AnalyzeWith(self, functorName):
        self.data = self.GetRegistered(functorName)(data=self.GetSampleData(), config=self.GetConfigData(), standard=self.args.std)

    def IngestConfig(self):
        #we check for configFormat when validating input and GetRegistered will fail if it does not exist.
        if (not self.args.configFile):
            return
        configFormat = self.GetRegistered(self.args.configFormat)
        self.GetConfigData().ImportDataFrom(configFormat(file=self.args.configFile))
        
    def IngestInputs(self):
        if (not self.args.inputFiles):
            return
        inputFormat = self.GetRegistered(self.args.inputFormat)
        for i in self.args.inputFiles:
            self.GetSampleData().ImportDataFrom(inputFormat(file=i))

    #Analysis to be run before we load saved data.
    def AnalyzeInputOnly(self):
        if (not self.args.inputOnlyAnalysisSteps):
            return
        for step in self.args.inputOnlyAnalysisSteps:
            self.AnalyzeWith(step)

    def LoadFiles(self):
        if (not self.args.loadFiles):
            return
        for l in self.args.loadFiles:
            self.GetSampleData().ImportDataFrom(self.loadFunctor(file=l))

    #Removes any data specified with --only or --ignore
    def TrimData(self):
        if (self.args.only):
            removed = self.GetSampleData().KeepOnlyDataBy(self.args.filter, list(self.args.only))
        elif (self.args.ignore):
            removed = self.GetSampleData().RemoveDataBy(self.args.filter, list(self.args.ignore))
        logging.debug(f"Filtered out {len(removed)} samples by {self.args.filter}")

    #Runs analysis steps on all data in the order they were provided.
    def Analyze(self):
        if (not self.args.analysisSteps):
            return
        for step in self.args.analysisSteps:
            self.AnalyzeWith(step)

    #Order of operations:
    #   1. Save existing data, if desired (this is usually safe, so do it early)
    #   2. Write output files in output format.
    def GenerateOutput(self):
        if (self.args.saveFile):
            self.saveFunctor(file=self.args.saveFile, data=self.GetSampleData())
        if (self.args.outputFile):
            outputFormat = self.GetRegistered(self.args.outputFormat)
            outputFormat(file=self.args.outputFile, data=self.GetSampleData())


#AnalysisFunctors are used in data manipulation.
#They take a configuration of known values (config) in addition to sample data, which is contains unknown and/or values of interest.
class AnalysisFunctor(DataFunctor):
    def __init__(self, name=eons.INVALID_NAME()):
        super().__init__(name)

        self.requiredKWArgs.append("config")
        self.requiredKWArgs.append("standard")
        
    #AnalysisFunctor will take self.data, mutate it, and then return it.
    #Populating self.data, returning it, and then resetting it are handled here or by parents of *this.
    #All you have to do is override the Analyze method to manipulate self.data as you'd likes.
    #This is done to help enforce consistency.
    @abstractmethod
    def Analyze(self):
        raise NotImplementedError

    def UserFunction(self, **kwargs):
        self.Analyze()
        return self.data

    def Clear(self):
        super().Clear()
        self.config = SampleSet()
        self.standard = ""
    
    #Override of UserFunctor method.
    def PreCall(self, **kwargs):
        super().PreCall(**kwargs)
        self.config = kwargs.get("config")
        self.standard = kwargs.get("standard")
        
