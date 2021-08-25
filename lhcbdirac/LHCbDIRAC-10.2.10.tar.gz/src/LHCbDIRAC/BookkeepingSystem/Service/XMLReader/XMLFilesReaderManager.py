###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""It interprets the XML reports and make a job, file, or replica object."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from xml.parsers.expat import ExpatError
from xml.dom.minidom import parse, parseString
from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.DataManagementSystem.Client.DataManager import DataManager
from LHCbDIRAC.BookkeepingSystem.DB.OracleBookkeepingDB import OracleBookkeepingDB
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.Job.FileParam import FileParam
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.Job.JobParameters import JobParameters
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.JobReader import JobReader
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.ReplicaReader import ReplicaReader
from LHCbDIRAC.BookkeepingSystem.DB.DataTakingConditionInterpreter import BeamEnergyCondition, \
    VeloCondition, \
    MagneticFieldCondition, \
    EcalCondition, \
    HcalCondition, \
    HltCondition, \
    ItCondition, \
    LoCondition, \
    MuonCondition, \
    OtCondition, \
    Rich1Condition, \
    Rich2Condition, \
    Spd_prsCondition, \
    TtCondition, \
    VeloPosition, \
    Context

__RCSID__ = "$Id$"


class XMLFilesReaderManager(object):
  """XMLFilesReaderManager class."""
  #############################################################################

  def __init__(self):
    """initialize the member of class."""
    self.jobReader_ = JobReader()
    self.replicaReader_ = ReplicaReader()

    self.bkClient_ = OracleBookkeepingDB()
    self.dm_ = DataManager()
    self.fileTypeCache = {}

    self.log = gLogger.getSubLogger('XMLFilesReaderManager')

  #############################################################################
  @staticmethod
  def readFile(filename):
    """reads an file content which format is XML."""
    try:
      with open(filename) as stream:
        doc = parse(stream)

      docType = doc.doctype  # job or replica
      xmltype = docType.name
    except NameError as ex:
      gLogger.error("XML reading error", filename)
      return S_ERROR(ex)

    return xmltype, doc, filename

  #############################################################################
  def readXMLfromString(self, xmlString):
    """read the xml string."""
    try:
      doc = parseString(xmlString)

      docType = doc.doctype  # job or replica
      xmltype = docType.name

      if xmltype == 'Replicas':
        replica = self.replicaReader_.readReplica(doc, "IN Memory")
        result = self.processReplicas(replica)
        del replica
        return result
      elif xmltype == 'Job':
        job = self.jobReader_.readJob(doc, "IN Memory")
        result = self.processJob(job)
        del job
        return result
      else:
        self.log.error("unknown XML file!!!")
    except ExpatError as ex:
      self.log.error("XML reading error", repr(ex))
      return S_ERROR(ex)

  #############################################################################
  def processJob(self, job):
    """interprets the xml content."""
    self.log.debug("Start Job Processing")

    # prepare for the insert, check the existence of the input files and retreive the fileid
    inputFiles = [inputFile.getFileName() for inputFile in job.getJobInputFiles()]
    if inputFiles:
      result = self.bkClient_.bulkgetIDsFromFilesTable(inputFiles)
      if not result['OK']:
        return result
      if result['Value']['Failed']:
        self.log.error("The following files are not in the bkk",
                       "%s" % (",".join(result['Value']['Failed'])))
        return S_ERROR("Files not in bkk")

      for inputFile in job.getJobInputFiles():
        lfn = inputFile.getFileName()
        fileID = int(result['Value']['Successful'][lfn]['FileId'])
        inputFile.setFileID(fileID)

    outputFiles = job.getJobOutputFiles()
    dqvalue = None
    for outputfile in outputFiles:

      typeName = outputfile.getFileType()
      typeVersion = outputfile.getFileVersion()
      cahedTypeNameVersion = typeName + '<<' + typeVersion
      if cahedTypeNameVersion in self.fileTypeCache:
        self.log.debug(cahedTypeNameVersion + ' in the cache!')
        typeID = self.fileTypeCache[cahedTypeNameVersion]
        outputfile.setTypeID(typeID)
      else:
        result = self.bkClient_.checkFileTypeAndVersion(typeName, typeVersion)
        if not result['OK']:
          self.log.error("The [type:version] is missing",
                         "[%s: %s]" % (str(typeName), str(typeVersion)))
          return S_ERROR("[type:version] missing")

        self.log.debug(cahedTypeNameVersion + " added to the cache!")
        typeID = int(result['Value'])
        outputfile.setTypeID(typeID)
        self.fileTypeCache[cahedTypeNameVersion] = typeID

      if job.getParam('JobType') and \
         job.getParam('JobType').getValue() == 'DQHISTOMERGING':  # all the merged histogram files have to be visible
        newFileParams = FileParam()
        newFileParams.setParamName('VisibilityFlag')
        newFileParams.setParamValue('Y')
        outputfile.addFileParam(newFileParams)
        self.log.debug('The Merged histograms visibility flag has to be Y!')

      params = outputfile.getFileParams()
      evtExists = False

      for param in params:
        paramName = param.getParamName()
        self.log.debug('ParamName check of ' + str(paramName))

        if paramName == "EventType":
          value = int(param.getParamValue())
          result = self.bkClient_.checkEventType(value)
          if not result['OK']:
            errorMessage = "The event type %s is missing!" % (str(value))
            return S_ERROR(errorMessage)

        if paramName == "EventTypeId":
          if param.getParamValue() != '':
            value = int(param.getParamValue())
            result = self.bkClient_.checkEventType(value)
            if not result['OK']:
              errorMessage = "The event type %s is missing!" % (str(value))
              return S_ERROR(errorMessage)
            evtExists = True

      if not evtExists and outputfile.getFileType() not in ['LOG']:
        inputFiles = job.getJobInputFiles()
        if inputFiles:
          fileName = inputFiles[0].getFileName()
          res = self.bkClient_.getFileMetadata([fileName])
          if res['OK']:
            fileMetadata = res['Value']['Successful'].get(fileName)
            if fileMetadata:
              if 'EventTypeId' in fileMetadata:
                if outputfile.exists('EventTypeId'):
                  param = outputfile.getParam('EventTypeId')
                  param.setParamValue(str(fileMetadata['EventTypeId']))
                else:
                  newFileParams = FileParam()
                  newFileParams.setParamName('EventTypeId')
                  newFileParams.setParamValue(str(fileMetadata['EventTypeId']))
                  outputfile.addFileParam(newFileParams)
            else:
              errMsg = "Can not get the metadata of %s file" % fileName
              self.log.error(errMsg)
              return S_ERROR(errMsg)
          else:
            return res
        elif job.getOutputFileParam('EventTypeId') is not None:
          param = job.getOutputFileParam('EventTypeId')
          newFileParams = FileParam()
          newFileParams.setParamName('EventTypeId')
          newFileParams.setParamValue(param.getParamValue())
          outputfile.addFileParam(newFileParams)
        else:
          return S_ERROR('It can not fill the EventTypeId because there is no input files!')

      infiles = job.getJobInputFiles()
      if not job.exists('RunNumber') and infiles:
        tck = -2
        runnumbers = []
        tcks = []
        for i in infiles:
          fileName = i.getFileName()
          retVal = self.bkClient_.getRunNbAndTck(fileName)

          if not retVal['OK']:
            return retVal
          if len(retVal['Value']) > 0:
            self.log.debug('RunTCK:', '%s' % retVal['Value'])

            for i in retVal['Value']:
              if i[0] not in runnumbers:
                runnumbers += [i[0]]
              if i[1] not in tcks:
                tcks += [i[1]]

          if len(runnumbers) > 1:
            self.log.warn('Different runs are reconstructed:', '%s' % runnumbers)
            runnumber = None
          else:
            runnumber = runnumbers[0]

          if len(tcks) > 1:
            self.log.warn('Different TCKs are reconstructed:', '%s' % tcks)
            tck = -2
          else:
            tck = tcks[0]

          self.log.debug('The output files of the job inherits the following run:', "%s" % runnumber)
          self.log.debug('The output files of the job inherits the following TCK:', '%s' % tck)

          if not job.exists('Tck'):
            newJobParams = JobParameters()
            newJobParams.setName('Tck')
            newJobParams.setValue(tck)
            job.addJobParams(newJobParams)

          if runnumber is not None:
            prod = None
            newJobParams = JobParameters()
            newJobParams.setName('RunNumber')
            newJobParams.setValue(str(runnumber))
            job.addJobParams(newJobParams)

            if job.getParam('JobType') and job.getParam('JobType').getValue() == 'DQHISTOMERGING':
              self.log.debug('DQ merging!')
              retVal = self.bkClient_.getJobInfo(fileName)
              if retVal['OK']:
                prod = retVal['Value'][0][18]
                newJobParams = JobParameters()
                newJobParams.setName('Production')
                newJobParams.setValue(str(prod))
                job.addJobParams(newJobParams)
                self.log.debug('Production inherited from input:', '%s' % prod)
            else:
              prod = job.getParam('Production').getValue()
              self.log.debug('Production:', '%s' % prod)

            retVal = self.bkClient_.getProductionProcessingPassID(prod)
            if retVal['OK']:
              proc = retVal['Value']

              retVal = self.bkClient_.getRunAndProcessingPassDataQuality(runnumber, proc)
              if retVal['OK']:
                dqvalue = retVal['Value']
              else:
                dqvalue = None
                message = (
                    "The rundataquality table does not contain run=%d proc_id=%s. Consequently, "
                    "the Dq flag is inherited from the ancestor file!"
                ) % (runnumber, proc)
                self.log.warn(message)
            else:
              dqvalue = None
              self.log.warn('Bkk can not set the quality flag because the processing \
              pass is missing for % d production (run number: %d )!' % (int(prod), int(runnumber)))

    inputfiles = job.getJobInputFiles()

    sumEventInputStat = 0
    sumEvtStat = 0
    sumLuminosity = 0

    if job.exists('JobType'):
      job.removeParam('JobType')

    # This must be replaced by a single call!!!!
    # ## It is not urgent as we do not have a huge load on the database
    for i in inputfiles:
      fname = i.getFileName()
      res = self.bkClient_.getJobInfo(fname)
      if not res['OK']:
        return res

      value = res["Value"]
      if value and value[0][2] is not None:
        sumEventInputStat += value[0][2]

      res = self.bkClient_.getFileMetadata([fname])
      if not res['OK']:
        return res

      fileMetadata = res['Value']['Successful'].get(fname)
      if fileMetadata:
        if fileMetadata['EventStat'] is not None:
          sumEvtStat += fileMetadata['EventStat']
        if fileMetadata['Luminosity'] is not None:
          sumLuminosity += fileMetadata['Luminosity']
        if dqvalue is None:
          dqvalue = fileMetadata.get('DataqualityFlag', fileMetadata.get('DQFlag', None))
      else:
        errMsg = "Can not get the metadata of %s file" % fname
        self.log.error(errMsg)
        return S_ERROR(errMsg)

    evtinput = 0
    if int(sumEvtStat) > int(sumEventInputStat):
      evtinput = sumEvtStat
    else:
      evtinput = sumEventInputStat

    if inputfiles:
      if not job.exists('EventInputStat'):
        newJobParams = JobParameters()
        newJobParams.setName('EventInputStat')
        newJobParams.setValue(str(evtinput))
        job.addJobParams(newJobParams)
      else:
        currentEventInputStat = job.getParam('EventInputStat')
        currentEventInputStat.setValue(evtinput)

    self.log.debug('Luminosity:', '%s' % sumLuminosity)
    outputFiles = job.getJobOutputFiles()
    for outputfile in outputFiles:
      if outputfile.getFileType() not in ['LOG'] and \
         sumLuminosity > 0 and not outputfile.exists('Luminosity'):
        newFileParams = FileParam()
        newFileParams.setParamName('Luminosity')
        newFileParams.setParamValue(sumLuminosity)
        outputfile.addFileParam(newFileParams)
        self.log.debug('Luminosity added to ', '%s' % outputfile.getFileName())
      ################

    config = job.getJobConfiguration()
    params = job.getJobParams()

    for param in params:
      if param.getName() == "RunNumber":
        value = int(param.getValue())
        if value <= 0 and len(job.getJobInputFiles()) == 0:
          # The files which inherits the runs can be entered to the database
          return S_ERROR('The run number not greater 0!')

    result = self.__insertJob(job)

    if not result['OK']:
      errorMessage = "Unable to create Job: %s , %s, %s .\n Error: %s" % (str(config.getConfigName()),
                                                                          str(config.getConfigVersion()),
                                                                          str(config.getDate()),
                                                                          str(result['Message']))
      return S_ERROR(errorMessage)
    else:
      jobID = int(result['Value'])
      job.setJobId(jobID)

    if job.exists('RunNumber'):
      try:
        runnumber = int(job.getParam('RunNumber').getValue())
      except ValueError:
        runnumber = -1
      if runnumber != -1:
        self.log.verbose("Registering the run status for ", "Run number %s,  JobId %s" %
                         (runnumber, job.getJobId()))
        result = self.bkClient_.insertRunStatus(runnumber, job.getJobId(), "N")
        if not result['OK']:
          errorMessage = ("Unable to register run status", runnumber + result['Message'])
          self.log.error(errorMessage[0], errorMessage[1])
          res = self.bkClient_.deleteJob(job.getJobId())
          if not res['OK']:
            self.log.warn("Unable to delete job", str(job.getJobId()) + res['Message'])
          return S_ERROR(errorMessage[0])

        # we may using HLT2 output to flag the runs as a consequence we may flagged the
        # runs before they registered to the bookkeeping.
        # we can flag a run using the newrunquality table
        retVal = self.bkClient_.getProductionProcessingPassID(-1 * int(runnumber))
        if retVal['OK']:
          retVal = self.bkClient_.getRunAndProcessingPassDataQuality(runnumber, retVal['Value'])
          if retVal['OK']:
            dqvalue = retVal['Value']
            self.log.verbose("The run data quality flag for", "run %d is %s" % (runnumber, dqvalue))
          else:
            # The report will be entered to the db.
            self.log.warn(retVal['Message'])
        else:
          self.log.error(retVal['Message'])
      else:
        # we reconstruct multiple runs
        self.log.warn("Run number can not determined for production:", job.getParam('Production').getValue())

    inputFiles = job.getJobInputFiles()
    for inputfile in inputFiles:
      result = self.bkClient_.insertInputFile(job.getJobId(), inputfile.getFileID())
      if not result['OK']:
        errorMessage = ("Unable to insert input file",
                        (str(inputfile.getFileName())) + result['Message'])
        self.log.error(errorMessage[0], errorMessage[1])
        res = self.bkClient_.deleteJob(job.getJobId())
        if not res['OK']:
          self.log.warn("Unable to delete job", str(job.getJobId()) + res['Message'])
        return S_ERROR(errorMessage[0])

    outputFiles = job.getJobOutputFiles()
    prod = job.getParam('Production').getValue()
    stepid = job.getParam('StepID').getValue()
    retVal = self.bkClient_.getProductionOutputFileTypes(prod, stepid)
    if not retVal['OK']:
      return retVal
    outputFileTypes = retVal['Value']
    for outputfile in outputFiles:
      if dqvalue is not None:
        newFileParams = FileParam()
        newFileParams.setParamName('QualityId')
        newFileParams.setParamValue(dqvalue)
        outputfile.addFileParam(newFileParams)
      if not job.exists('RunNumber'):  # if it is MC
        newFileParams = FileParam()
        newFileParams.setParamName('QualityId')
        newFileParams.setParamValue('OK')
        outputfile.addFileParam(newFileParams)
      ftype = outputfile.getFileType()
      if ftype in outputFileTypes:
        vFileParams = FileParam()
        vFileParams.setParamName('VisibilityFlag')
        vFileParams.setParamValue(outputFileTypes[ftype])
        outputfile.addFileParam(vFileParams)
        self.log.debug('The visibility flag is:' + outputFileTypes[ftype])

      result = self.__insertOutputFiles(job, outputfile)
      if not result['OK']:
        errorMessage = ("Unable to insert output file",
                        "%s ! ERROR: %s" % (str(outputfile.getFileName()),
                                            result["Message"]))
        self.log.error(errorMessage[0], errorMessage[1])
        res = self.bkClient_.deleteInputFiles(job.getJobId())
        if not res['OK']:
          self.log.warn("Unable to delete inputfiles of", str(job.getJobId()) + res['Message'])
        res = self.bkClient_.deleteJob(job.getJobId())
        if not res['OK']:
          self.log.warn("Unable to delete job", str(job.getJobId()) + res['Message'])
        return S_ERROR(errorMessage[0])
      else:
        fileid = int(result['Value'])
        outputfile.setFileID(fileid)

      replicas = outputfile.getReplicas()
      for replica in replicas:
        params = replica.getaprams()
        for param in params:  # just one param exist in params list, because JobReader only one param add to Replica
          name = param.getName()
        result = self.bkClient_.updateReplicaRow(outputfile.getFileID(), 'No')  # , name, location)
        if not result['OK']:
          errorMessage = "Unable to create Replica %s !" % (str(name))
          return S_ERROR(errorMessage)

    self.log.debug("End Processing!")

    return S_OK()

  def __insertJob(self, job):
    """Inserts the job to the database."""
    config = job.getJobConfiguration()

    production = None

    condParams = job.getDataTakingCond()
    if condParams is not None:
      datataking = condParams.getParams()
      config = job.getJobConfiguration()

      ver = config.getConfigVersion()  # online bug fix
      ver = ver.capitalize()
      config.setConfigVersion(ver)
      self.log.debug("Data taking:", "%s" % datataking)
      context = Context(datataking, config.getConfigName())
      conditions = [BeamEnergyCondition(), VeloCondition(),
                    MagneticFieldCondition(), EcalCondition(),
                    HcalCondition(), HltCondition(),
                    ItCondition(), LoCondition(),
                    MuonCondition(), OtCondition(),
                    Rich1Condition(), Rich2Condition(),
                    Spd_prsCondition(), TtCondition(),
                    VeloPosition()]
      for condition in conditions:
        condition.interpret(context)

      self.log.debug(context.getOutput())
      datataking['Description'] = context.getOutput()

      res = self.bkClient_.getDataTakingCondDesc(datataking)
      dataTackingPeriodDesc = None
      if res['OK']:
        daqid = res['Value']
        if len(daqid) != 0:  # exist in the database datataking
          dataTackingPeriodDesc = res['Value'][0][0]
          self.log.debug('Data taking condition id', dataTackingPeriodDesc)
        else:
          res = self.bkClient_.insertDataTakingCond(datataking)
          if not res['OK']:
            return S_ERROR("DATA TAKING Problem:" + str(res['Message']))
          dataTackingPeriodDesc = datataking['Description']
          # The new data taking condition inserted. The name should be the generated name.
      else:
        # Note we allow to insert data quality tags when only the description is different.
        res = self.bkClient_.insertDataTakingCond(datataking)
        if not res['OK']:
          return S_ERROR("DATA TAKING Problem:" + str(res['Message']))
        dataTackingPeriodDesc = datataking['Description']
        # The new data taking condition inserted. The name should be the generated name.

      # insert processing pass
      programName = None
      programVersion = None
      conddb = None
      dddb = None
      found = False
      for param in job.getJobParams():
        if param.getName() == 'ProgramName':
          programName = param.getValue()
        elif param.getName() == 'ProgramVersion':
          programVersion = param.getValue()
        elif param.getName() == 'CondDB':
          conddb = param.getValue()
        elif param.getName() == 'DDDB':
          dddb = param.getValue()
        elif param.getName() == 'RunNumber':
          production = int(param.getValue()) * -1
          found = True

      if job.exists('CondDB'):
        job.removeParam('CondDB')
      if job.exists('DDDB'):
        job.removeParam('DDDB')

      if not found:
        self.log.error('Run number is missing!')
        return S_ERROR('Run number is missing!')

      retVal = self.bkClient_.getStepIdandNameForRUN(programName, programVersion, conddb, dddb)

      if not retVal['OK']:
        return retVal

      stepid = retVal['Value'][0]

      # now we have to get the list of eventtypes
      eventtypes = []
      for outputFiles in job.getJobOutputFiles():
        for outPutfileParam in outputFiles.getFileParams():
          outputFileParamName = outPutfileParam.getParamName()
          if outputFileParamName == "EventTypeId":
            eventtypes.append(int(outPutfileParam.getParamValue()))

      steps = {'Steps':
               [{'StepId': stepid,
                 'StepName': retVal['Value'][1],
                 'ProcessingPass':retVal['Value'][1],
                 'Visible':'Y',
                 'OutputFileTypes':[{'FileType': 'RAW'}]}]}

      self.log.debug('Pass_indexid', "%s" % steps)
      self.log.debug('Data taking', "%s" % dataTackingPeriodDesc)
      self.log.debug('production', production)

      newJobParams = JobParameters()
      newJobParams.setName('StepID')
      newJobParams.setValue(str(stepid))
      job.addJobParams(newJobParams)

      message = "StepID for run: %s" % (str(production))
      self.log.info(message, stepid)

      res = self.bkClient_.addProduction(production,
                                         simcond=None,
                                         daq=dataTackingPeriodDesc,
                                         steps=steps['Steps'],
                                         inputproc='',
                                         configName=config.getConfigName(),
                                         configVersion=config.getConfigVersion(),
                                         eventType=eventtypes)
      if res['OK']:
        self.log.verbose("New processing pass has been created!")
        self.log.verbose("New production is:", production)
      elif job.exists('RunNumber'):
        self.log.warn('The run already registered!')
      else:
        self.log.error("Failing adding production", production + res['Message'])
        retVal = self.bkClient_.deleteStepContainer(production)
        if not retVal['OK']:
          return retVal
        return S_ERROR('Failing adding production')

    attrList = {'ConfigName': config.getConfigName(),
                'ConfigVersion': config.getConfigVersion(),
                'JobStart': None}

    for param in job.getJobParams():
      attrList[str(param.getName())] = param.getValue()

    res = self.bkClient_.checkProcessingPassAndSimCond(attrList['Production'])
    if not res['OK']:
      self.log.error('check processing pass and simulation condition error', res['Message'])
    else:
      value = res['Value']
      if value[0][0] == 0:
        errorMessage = "Missing processing pass and simulation conditions: "
        errorMessage += "please fill it. Production = %s" % (str(attrList['Production']))
        self.log.warn(errorMessage)

    if attrList['JobStart'] is None:
      # date = config.getDate().split('-')
      # time = config.getTime().split(':')
      # dateAndTime = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), 0, 0)
      attrList['JobStart'] = config.getDate() + ' ' + config.getTime()

    if production is not None:  # for the online registration
      attrList['Production'] = production

    res = self.bkClient_.insertJob(attrList)

    if not res['OK'] and production < 0:
      self.log.error("Failed inserting job", res['Message'])
      retVal = self.bkClient_.deleteProductionsContainer(production)
      if not retVal['OK']:
        self.log.error(retVal['Message'])
    return res

  #############################################################################
  def __insertOutputFiles(self, job, outputfile):
    """insert the files produced by a job."""
    attrList = {'FileName': outputfile.getFileName(),
                'FileTypeId': outputfile.getTypeID(),
                'JobId': job.getJobId()}

    fileParams = outputfile.getFileParams()
    for param in fileParams:
      attrList[str(param.getParamName())] = param.getParamValue()
    return self.bkClient_.insertOutputFile(attrList)

  #############################################################################
  def processReplicas(self, replica):
    """process the replica registration request."""
    outputfile = replica.getFileName()
    self.log.debug("Processing replicas:", "%s" % outputfile)
    fileID = -1

    params = replica.getaprams()
    delete = True

    replicaFileName = ""
    for param in params:
      replicaFileName = param.getFile()
      location = param.getLocation()
      delete = param.getAction() == "Delete"

      result = self.bkClient_.checkfile(replicaFileName)
      if not result['OK']:
        message = "No replica can be "
        if delete:
          message += "removed"
        else:
          message += "added"
        message += " to file " + str(replicaFileName) + " for " + str(location) + ".\n"
        return S_ERROR(message)
      else:
        fileID = int(result['Value'][0][0])
        self.log.debug("FileId:", fileID)

      if delete:
        result = self.dm_.getReplicas(replicaFileName)
        replicaList = result['Value']['Successful']
        if len(replicaList) == 0:
          result = self.bkClient_.updateReplicaRow(fileID, "No")
          if not result['OK']:
            self.log.warn("Unable to set the Got_Replica flag for ", "%s" % replicaFileName)
            return S_ERROR("Unable to set the Got_Replica flag for ", "%s" % replicaFileName)
      else:
        result = self.bkClient_.updateReplicaRow(fileID, "Yes")
        if not result['OK']:
          return S_ERROR("Unable to set the Got_Replica flag for " + str(replicaFileName))

    self.log.debug("End Processing replicas!")

    return S_OK()
