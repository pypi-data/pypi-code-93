"""
indi game engine offline develop tools

convert 3d assets
convert images to platform dipend format
make ige package
upload package to devserver

"""

import py_compile
import shutil
import glob
import os.path
import igeCore as core
from igeCore import apputil
from igeCore.devtool._igeTools import *
from igeCore import apputil
from igeCore.apputil import launch_server
import hashlib
import tokenize

def isHiddenFolder(path):
    if path.find('/.') != -1 or path.find('\\.') != -1 :
        return True
    return False

def findFiles(path, exts = ['.*']):
    list = []
    for root, dirs, files in os.walk(path):
        if isHiddenFolder(root): continue
        for fname in files:
            name, ext = os.path.splitext(fname)
            for e in exts:
                if e == '.*' or e == ext:
                    list.append(os.path.join(root, fname))
                    break
    return list

def findImageFiles(path):
    list = []
    for root, dirs, files in os.walk(path):
        if isHiddenFolder(root): continue
        for fname in files:
            name, ext = os.path.splitext(fname)
            extl = ext.lower()
            if extl == '.png' or extl == '.dds' or extl == '.tga' or extl == '.psd' or extl == '.jpg':
                list.append(os.path.join(root, fname))
    return list

def find3DSceneFiles(path):
    dict = {}
    for root, dirs, files in os.walk(path):
        if root.find('\.') != -1: continue
        folder = os.path.basename(root)

        folderRule = False
        for f in files:
            name, ext = os.path.splitext(f)
            if name == folder:
                folderRule = True
                baseFile = f
                break

        if folderRule:
            daes = [os.path.join(root, baseFile)]
            for f2 in files:
                f2_name, f2_ext = os.path.splitext(f2)
                if (f2_ext.lower() == '.dae' or f2_ext.lower() == '.fbx') and f2_name != folder:
                    daes.append(os.path.join(root, f2))
            dict[folder] = daes
        else:
            for f2 in files:
                f2_name, f2_ext = os.path.splitext(f2)
                if f2_ext.lower() == '.dae' or f2_ext.lower() == '.fbx':
                    dict[f2_name] = [os.path.join(root, f2)]
    return dict

def createDirectoryTree(filelist, root):
    imageDirectory = dict()
    for img in filelist:
        while True:
            img, file = os.path.split(img)
            if img not in imageDirectory:
                imageDirectory[img] = {file: 0};
            elif file not in imageDirectory[img]:
                imageDirectory[img][file] = 0
            if img == root: break
    return imageDirectory

def findFileFromDiorectoryTree(imageDirectory, file, dir):
    files = imageDirectory.get(dir)
    if files is None: return None
    if file in files:
        return os.path.join(dir, file)
    for d in files:
        _, ext = os.path.splitext(d)
        if ext is '':
            rv = findFileFromDiorectoryTree(imageDirectory, file, os.path.join(dir, d))
            if rv: return rv
    return None

def removeRoot(path, root):
    newpath = path.replace(root, '', 1)
    if len(newpath) >0:
        if newpath[0] == '/' or newpath[0] == '\\':
            newpath = newpath[1:]
    else:
        newpath = ""
    return newpath

def replaceExt(file, ext):
    name, extold = os.path.splitext(file)
    return name + ext

def readAndCalcHash(srcfile, dstfile, hashfile):
    hashcode = '00000000000000000000000000000000'
    newhash  = 'ffffffffffffffffffffffffffffffff'
    if os.path.exists(dstfile):
        try:
            with open(hashfile, 'r') as f:
                hashcode = f.read()
        except : None

    with open(srcfile, 'rb') as f:
        fileDataBinary = f.read()
        if len(fileDataBinary) is not 0:
            hash = hashlib.md5()
            hash.update(fileDataBinary)
            newhash = hash.hexdigest()
    return hashcode,newhash

def saveHash(hashfile, newhash):
    if newhash != 'ffffffffffffffffffffffffffffffff':
        apputil.makeDirectories(hashfile)
        with open(hashfile, 'w') as f:
            f.write(newhash)

def readFigureConf(path):
    mode = 0
    label = ''
    keyvalue = {}
    with open(path, 'rb') as f:
        for token in tokenize.tokenize(f.readline):
            if token.type is tokenize.ENDMARKER:
                break
            elif token.type is tokenize.NAME:
                if mode is 0:
                    label = token.string
                else:
                    keyvalue[label] = token.string
                    mode = 0
            elif token.type is tokenize.OP:
                mode = 1
            elif token.type is tokenize.NUMBER:
                if mode is 1:
                    try:
                        keyvalue[label] = int(token.string)
                    except ValueError:
                        keyvalue[label] = float(token.string)
                    mode = 0
    return keyvalue

def createFigureConfTree(path, unit=1.0):
    filelist = []
    for root, dirs, files in os.walk(path):
        if root.find('\.') != -1: continue
        for fname in files:
            if fname == 'figure.conf':
                filelist.append(os.path.join(root, fname))
    figureConfTree = dict()
    for filepath in filelist:
        conf = readFigureConf(filepath)
        dir, file = os.path.split(filepath)
        figureConfTree[dir] = conf

    for dir, val in figureConfTree.items():
        while True:
            dir, _ = os.path.split(dir)
            if len(dir) is 0:
                break
            parent = figureConfTree.get(dir)
            if parent is not None:
                for parentkey, parentval in parent.items():
                    if val.get(parentkey) is None:
                        val[parentkey] = parentval

    if len(figureConfTree) == 0:
        figureConfTree[path] = {}

    for conf in figureConfTree.values():
        if conf.get('BASE_SCALE') is None:
           conf['BASE_SCALE'] = unit
        #if conf.get('OPTIMIZE_MESH') is None:
        #   conf['OPTIMIZE_MESH'] = True

    return figureConfTree

def findFigureConf(dir: str, tree: dict):
    while True:
        dir, _ = os.path.split(dir)
        if len(dir) is 0:
            break
        conf = tree.get(dir)
        if conf is not None:
            return conf
    return dict()

def load3DScene(tmpfig, files, conf):
    loadCollada(files[0], tmpfig, conf)
    for i in range(1, len(files)):
        loadColladaAnimation(files[i], tmpfig, conf)

def replaceTexturePath(tmpfig, imageDirectory, startPath, endPath, allTextures, subFolder):
    texs = tmpfig.getTextureSource()
    for tex in texs:
        filename = os.path.basename(tex['path'])
        current = startPath
        inputimage = None
        while True:
            inputimage = findFileFromDiorectoryTree(imageDirectory, filename, current)
            if inputimage is not None: break
            if current == endPath: break
            current, _ = os.path.split(current)
        if inputimage is None:
            print('file not found ' + tex['path'])
        else:
            allTextures[inputimage] = tex;
            inputimage = removeRoot(inputimage, endPath);
            inputimage, ext = os.path.splitext(inputimage)
            inputimage = os.path.join(subFolder, inputimage)
            inputimage = inputimage.replace('\\', '/')
            newTex = {'path': inputimage, 'normal': tex['normal'], 'wrap': tex['wrap']}
            tmpfig.replaceTextureSource(tex, newTex)

def setMaterialAlpha(tmpfig, imageDirectory, startPath, endPath):
    texs = tmpfig.getTextureSource()
    for tex in texs:
        filename = os.path.basename(tex['path'])
        current = startPath
        inputimage = None
        while True:
            inputimage = findFileFromDiorectoryTree(imageDirectory, filename, current)
            if inputimage is not None: break
            if current == endPath: break
            current, _ = os.path.split(current)
        if inputimage is not None:
            if isAlpha(inputimage):
                tmpfig.enableAlphaModeByTexture(tex['path'])

def getHashPath(root, source, platform):
    abspath = os.path.abspath(source)
    if abspath[0]=='/' or abspath[0]=='\\':
       abspath = abspath[1:]
    elif abspath[2]=='\\':
        abspath = abspath[3:]
    return os.path.join(os.path.join(root, apputil.targetFolderName(platform)), abspath)

def convertImages(allTextures, sourceDir, destDir, platform):
    print('----------------------')
    print('Convert image files')
    print('----------------------')
    for key, val in allTextures.items():
        outfile = os.path.normpath(key.replace(sourceDir, destDir, 1))
        outfile = replaceExt(outfile, '.pyxi')
        hashfile = getHashPath('.tmp/hash', key, platform)
        hashcode, newhash = readAndCalcHash(key, outfile, hashfile)
        if hashcode != newhash:
            print("convert {} for {}".format(key,apputil.targetFolderName(platform)))
            apputil.makeDirectories(outfile)
            convertTextureToPlatform(key, outfile, platform, val['normal'], val['wrap'])
            saveHash(hashfile, newhash)
        else:
            print("skip {} ".format(key))

def copyFiles(src, dst, exts=['.*']):
    for root, dirs, files in os.walk(src):
        if isHiddenFolder(root): continue
        for fname in files:
            name, ext = os.path.splitext(fname)
            for e in exts:
                if e == '.*' or ext == e:
                    srcPath = os.path.join(root, fname)
                    dstPath = os.path.join(dst, removeRoot(srcPath, src))
                    apputil.makeDirectories(dstPath)
                    shutil.copy2(srcPath, dstPath)
                    print("copy {}".format(dstPath))
                    break

def compilePrograms(src, dst):
    list = findFiles(src, ['.py'])
    for infile in list:
        outfile = os.path.normpath(infile.replace(src, dst, 1))
        apputil.makeDirectories(outfile)
        if os.path.basename(infile) == 'root.py':
            shutil.copy(infile, outfile)
        else:
            outfile = replaceExt(outfile, '.pyc')
            apputil.makeDirectories(outfile)
            print('compile : '+infile)
            py_compile.compile(infile, outfile)

def hashCheck(files, outfile, platform):
    changed = False
    for file in files:
        hashfile = getHashPath('.tmp/hash', file, platform)
        hashcode, newhash = readAndCalcHash(file, outfile, hashfile)
        if hashcode != newhash:
            changed = True
            saveHash(hashfile, newhash)
    return changed

def buildAppPackage(src, dest):
    apputil.makeDirectories(dest)
    list =glob.glob(os.path.join(src,'*' ))
    for dir in list:
        if os.path.isdir(dir):
            outpath = os.path.join(dest,os.path.basename(dir))

            list = findFiles(dir)
            if hashCheck(list, outpath+'.pyxd', 0):
                print("build asset database {}.pyxd".format(outpath))
                compressFolder(dir, outpath)
            else:
                print("skip asset database {}.pyxd".format(outpath))
        else:
            print("copy {}".format(dir))
            shutil.copy2(dir, dest)


def findConvertReplaceTextures(fig : core.editableFigure, sourceRoot, destRoot, platform=core.TARGET_PLATFORM_PC, figurePath=""):
    """
    Find and convert the texture file linked from editableFigure.

    :param sourceRoot: Root folder to search for texture files
    :param destRoot: Root folder to save the textures
    :param editableFigure: The location where the editableFigure was saved (optional). It must be included under sourceRoot.
    :param platform: Formats to convert textures to.　TARGET_PLATFORM_PC or TARGET_PLATFORM_MOBILE

    :return: None

    The figurePath must always be under the sourceRoot.
    The specified folder hierarchy may contain multiple texture files with the same name.
    When figurePath is specified, the texture file closest to it will be selected.

    Example.
        ・File path saved in editableFigure
            D:/aaa/bbb/ccc/test.png
        ・Location of the actual file
            C:/user/input/images/test.png
        ・sourceRoot
            C:/user/input
        ・destRoot
            C:/user/output
        ・The actual output file
            C:/user/output/images/test.pyxi
        ・New file path to be saved in editableFigure
            images/test
    """
    sourceRoot = os.path.abspath(sourceRoot).replace('\\', '/')
    destRoot = os.path.abspath(destRoot).replace('\\', '/')

    if figurePath == "":
        daepath = figurePath = sourceRoot
    else:
        figurePath = os.path.abspath(figurePath).replace('\\', '/')
        daepath, _ = os.path.split(figurePath)
        if len(daepath) == 0 : daepath = os.path.abspath(".").replace('\\', '/')


    imageList = findImageFiles(sourceRoot)
    imageDirectoryTree = createDirectoryTree(imageList, sourceRoot)

    allTextures = dict()
    replaceTexturePath(fig, imageDirectoryTree, daepath, sourceRoot, allTextures, removeRoot(destRoot,sourceRoot))
    convertImages(allTextures, sourceRoot, destRoot, platform)


def convertAssets(sourceDir, destDir, platform, unit=1.0, rootDir=None):
    """
    Convert model and image data to ige format
    model(.dae) -> .pyxf
    image(.png .dds .tga .psd ) -> .pyxi

    If model data with the same name as the folder name is found,
    it is regarded as base model data, and other model data in the
    same folder are regarded as motion files, and all are packed
    into one file
    If there is no model data with the same name as the folder name,
    Each model data as base model data and convert separately

    :param sourceDir: source root folder
    :param destDir: destination root folder
    :param platform: target platform (core.TARGET_PLATFORM_XX)
    :param unit: scale unit size of 3d model
    :return: None
    """
    if rootDir is None: rootDir = destDir

    imageList = findImageFiles(sourceDir)
    sceneList = find3DSceneFiles(sourceDir)
    imageDirectoryTree = createDirectoryTree(imageList, sourceDir)
    confTree = createFigureConfTree(sourceDir, unit)
    allTextures = dict()
    tmpfig = core.editableFigure("tmpfigure", True)

    print('----------------------')
    print('Convert 3d scene files')
    print('----------------------')

    for files in sceneList.values():
        tmpfig.clear()
        conf = findFigureConf(files[0], confTree)
        load3DScene(tmpfig, files, conf)

        daepath, _ = os.path.split(files[0])
        setMaterialAlpha(tmpfig, imageDirectoryTree, daepath, sourceDir)
        replaceTexturePath(tmpfig, imageDirectoryTree, daepath, sourceDir, allTextures, removeRoot(destDir,rootDir))

        outfile = os.path.normpath(files[0].replace(sourceDir, destDir, 1))
        outfile = replaceExt(outfile, '.pyxf')

        if hashCheck(files, outfile, platform):
            print("convert {}".format(files[0]))
            apputil.makeDirectories(outfile)

            if 'OPTIMIZE_VERTEX' in conf.keys() and conf['OPTIMIZE_VERTEX']:
                tmpfig.removeUnreferencedVertices()
            if 'OPTIMIZE_MESH' in conf.keys() and conf['OPTIMIZE_MESH']:
                tmpfig.mergeSameMaterialMesh()

            tmpfig.saveFigure(outfile)
        else:
            print("skip {}".format(files[0]))

    for img in imageList:
        if img not in allTextures:
            allTextures[img] = {'path': removeRoot(img,sourceDir), 'normal': False, 'wrap': False}
    convertImages(allTextures, sourceDir, destDir, platform)

    return allTextures


def deploy(projectFolder, userID, appName, appVersion, unit = 1.0, assetSource=None, assetDestination=None):
    if assetSource == None: assetSource = projectFolder
    if assetDestination == None: assetDestination = projectFolder
    allTextures = convertAssets(assetSource, assetDestination, core.TARGET_PLATFORM_PC, unit, projectFolder)

    deployTmp = '.tmp/deploy/'+appName+'/'+appVersion+'/'

    print('----------------------')
    print('Create non pack app image')
    print('----------------------')
    print('--- PC ---')
    copyFiles(projectFolder, deployTmp+'unpackimage/pc', ['.pyxf', '.json', '.pyxa', '.pyxb', '.pickle', '.zip', '.txt', '.db', '.ttf'])
    compilePrograms(projectFolder, deployTmp+'unpackimage/pc')
    convertImages(allTextures, assetSource, os.path.join(deployTmp+'unpackimage/pc',removeRoot(assetDestination, projectFolder)), core.TARGET_PLATFORM_PC)
    print('--- Mobile ---')
    copyFiles(projectFolder, deployTmp+'unpackimage/mobile', ['.pyxf', '.json', '.pyxa', '.pyxb', '.pickle', '.zip', '.txt', '.db', '.ttf'])
    compilePrograms(projectFolder, deployTmp+'unpackimage/mobile')
    convertImages(allTextures, assetSource, os.path.join(deployTmp+'unpackimage/mobile',removeRoot(assetDestination, projectFolder)), core.TARGET_PLATFORM_MOBILE)

    print('----------------------')
    print('Create packed app image')
    print('----------------------')
    print('--- PC ---')
    buildAppPackage(deployTmp+'unpackimage/pc', deployTmp+'packimage/pc')
    print('--- Mobile ---')
    buildAppPackage(deployTmp+'unpackimage/mobile', deployTmp+'packimage/mobile')

    print('----------------------')
    print('Upload app image to the server')
    print('----------------------')
    print('--- PC ---')
    launch_server.makeProjectDir(userID, appName, appVersion, "pc")
    launch_server.upload_files(deployTmp+'packimage/pc', '/'+userID+'/'+appName+'/'+appVersion+'/pc')
    print('--- Mobile ---')
    launch_server.makeProjectDir(userID, appName, appVersion, "mobile")
    launch_server.upload_files(deployTmp+'packimage/mobile',  '/'+userID+'/'+appName+'/'+appVersion+'/mobile')
