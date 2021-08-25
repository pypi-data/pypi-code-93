# import os
# import subprocess
# import threading
# import time

# from django.core.files.storage import default_storage
# from django.core.files.uploadedfile import UploadedFile

# from limes_common import config
# from limes_common.connections import eLab as ELC
# from limes_common.models.network.elab import MetaField, SampleModel
# from limes_common.models.network.server import FileMeta

# BLAST_PATH = config.SERVER_DB_PATH + '/blast/'
# DB_NAMES_FILE = config.SERVER_DB_PATH + '/dbNames'

# def _fsPath(folder, file):
#     return '%s/%s/%s' % (config.SERVER_DB_PATH, folder, file)

# # todo: breakup and organize this file

# def TryAddFile(token: str, meta: FileMeta, file: UploadedFile) -> tuple[bool, str]:
#     ec = ELC.ELabConnection()
#     ec.SetToken(token)
#     sampleRes = ec.GetSample(meta.SampleId)

#     if sampleRes.Code != 200:
#         return False, 'Sample [%s] not found' % (meta.SampleId)
#     sample = sampleRes.Sample
#     fsPath = _fsPath(sample.Id, meta.FileName)
#     if default_storage.exists(fsPath): 
#         return False, 'File [%s] already exists for sample [%s]' % (meta.FileName, sample.Name)

#     try:
#         default_storage.save(fsPath, file)
#     except Exception as err:
#         return False, str(err)

#     sampleMeta = ec.GetSampleMeta(str(sample.Id))
#     metaKey = 'Data - Fasta'
#     trackedFiles = sampleMeta.Fields.get(metaKey, MetaField()).value.split('\n')
#     newField = ''
#     for f in trackedFiles:
#         item = f.split(':')
#         if item[0] != meta.FileName:
#             newField += '%s\n' % f
#     newField += '%s: %s' % (meta.FileName, meta.FilePath)

#     ec.UpdateSampleMeta(str(sample.Id), metaKey, newField)

#     thisDBName = BLAST_PATH + meta.FileName
#     newNames: str = ''
#     try:
#         with default_storage.open(DB_NAMES_FILE, 'r') as dbNames:
#             names = dbNames.readlines()
#             names = list(map(lambda l: l.replace('\n', ''), names))
#             for name in names:
#                 if name != thisDBName:
#                     newNames += name + '\n'
#     except:
#         pass
#     newNames += thisDBName
#     with default_storage.open(DB_NAMES_FILE, 'w') as dbNames:
#         dbNames.write(newNames)
        
    
#     aliasList = '"%s"' % " ".join(list(map(lambda n: os.path.abspath(n), newNames.split('\n'))))
#     # print(aliasList)
#     aliasOut = BLAST_PATH + 'all'
#     aliasOut = os.path.abspath(aliasOut)
#     def makeDb():
#         blast = subprocess.run(('makeblastdb -in %s -parse_seqids -dbtype nucl -out %s'%(fsPath, thisDBName)).split(' '))
#         aliasCmd = ('blastdb_aliastool -dbtype nucl -title aggregate -out %s -dblist' % (aliasOut)).split(' ')
#         aliasCmd.append(aliasList)
#         # aliasCmd.append('"limes_server/db/blast/testmil.fasta limes_server/db/blast/122"')
#         # time.sleep(3)
#         # alias = subprocess.run(aliasCmd) # this doesn't work, for some reason
#         os.system(" ".join(aliasCmd))
#     thread = threading.Thread(target=makeDb)
#     thread.start()

#     print('added file: %s for sample: %s' % (meta.FileName, sample.Name))
#     return True, sample.Name

# def Blast(query: UploadedFile) -> str:
#     queryPath = _fsPath('queries', query.name)
#     default_storage.save(queryPath, query)

#     out = queryPath + '.out'

#     blast = subprocess.run([
#         'blastn', '-query', queryPath,
#         '-db', '%sall'%BLAST_PATH,
#         '-out', out,
#         '-outfmt', '7',
#     ])
#     with default_storage.open(out, 'r') as resultFile:
#         result = resultFile.read()
#     default_storage.delete(out)

#     default_storage.delete(queryPath)
#     return result
