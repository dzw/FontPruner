"""Usage:
  FontPruner.py --inputPath=<inputPaths>... --inputFont=<inputFont>...  [--tempPath=<tempPath>]
"""
import argparse
import io

import os
import re

SepPath = os.path.sep
TempPathDefault = "tmp"
InputFilelist = "input_filelist.txt"
OutputFolder = "output"
IntermediateFolder = OutputFolder  # "intermediate"
ChineseOutPut = "ChineseOutPut.txt"
UnChineseOutPut = "unChineseOutPut.txt"
Succ = 0


def read_text(file_path, encoding=None):
    if encoding is None:
        encoding = 'UTF-8'

    file = io.open(file_path, "rt", encoding=encoding)
    # file = open(file_path, "rt", encoding=encoding)

    text = file.read()
    file.close()
    return text


def writeText(filePathOut, content, encoding=None):
    if encoding is None:
        encoding = 'UTF-8'

    file_out = open(filePathOut, "wb")
    encoded_content = content.encode(encoding)
    file_out.write(encoded_content)
    file_out.close()


def walkFilesRegExp(inputPath, file_pattern, rel=None):
    lst = []
    if not os.path.exists(inputPath):
        return lst
    for root, dirs, files in os.walk(inputPath):
        for filename in sorted(files):
            if re.search(file_pattern, filename) is not None:
                file_full_pth = os.path.join(root, filename)
                if rel is not None:
                    jsfile2 = os.path.relpath(file_full_pth, rel)
                    jsfile = jsfile2.replace("\\", "/")
                    lst.append(jsfile)
                else:
                    lst.append(file_full_pth.replace("\\", "/"))
    return lst


def walkFiles(inputPath, targetExt, rel=None):
    pattern = "\." + targetExt + "$"
    return walkFilesRegExp(inputPath, pattern)


def genFilePathList(inputPath, FileListOP):
    fullPara = ""
    for path in inputPath:
        print("path = " + path)
        fullPara += path + " "
    fullPara += " " + FileListOP + SepPath + InputFilelist
    command = "java -jar bin" + SepPath + "GenFileList.jar " + fullPara
    if os.system(command) is not Succ:
        raise Exception('generate fileList.txt error!' + command)
    print("genFilePathList completed" + "   " + fullPara)


def extractFileString(temp):
    fileListPath = os.path.normpath(os.path.join(temp, InputFilelist))
    outputPath = os.path.normpath(os.path.join(temp, IntermediateFolder))

    text = read_text(fileListPath)
    splitlines = text.splitlines()

    all_chars = []
    for splitline in splitlines:
        print(splitline)
        normpath = os.path.normpath(os.path.join(temp, splitline))
        chars = read_text(normpath)
        s = set(chars)
        all_chars.extend(s)
    chinese = []
    not_chinese = []
    for char in all_chars:
        match = re.match(ur"[\u4E00-\u9FA5]", char)
        if match:
            chinese.append(char)
        else:
            not_chinese.append(char)

    writeText(os.path.join(outputPath, ChineseOutPut), "".join(chinese))
    writeText(os.path.join(outputPath, UnChineseOutPut), "".join(not_chinese))
    #
    # command = "java -jar bin" + SepPath + "fontExtract.jar " + fileListPath + " " + outputPath
    # if os.system(command) is not Succ:
    #     raise Exception('extract font string  error!' + command)
    # print("extractFileString completed")


def bulidNewFont(originPath, outPutPath):
    fullOutPut = os.path.normpath(os.path.join(outPutPath, OutputFolder))

    if not os.path.exists(fullOutPut):
        os.makedirs(fullOutPut)

    fontName = os.path.basename(originPath)

    ttf_output = os.path.normpath(os.path.join(fullOutPut, fontName))
    fullPara = " ".join([
        os.path.normpath(os.path.join(outPutPath, IntermediateFolder, ChineseOutPut)),
        os.path.normpath(os.path.join(outPutPath, IntermediateFolder, UnChineseOutPut)),
        os.path.normpath(originPath),
        ttf_output
    ])

    normpath = os.path.normpath(os.path.join("bin", "sfnttool.jar"))
    command = "java -jar %s -c " % (normpath) + fullPara

    if os.system(command) is not Succ:
        raise Exception('build new font error!' + command)
    print("bulidNewFont completed " + ttf_output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputFont", required=False, dest="inputFont", help='inputFont')
    parser.add_argument("--inputPath", required=False, dest="inputPath", help='inputPath')
    parser.add_argument("--tempPath", required=False, dest="tempPath", help='tempPath')
    args = parser.parse_args()

    print(args)

    tmp = args.tempPath
    if tmp is None:
        tmp = TempPathDefault
    else:
        if not os.path.exists(tmp):
            raise Exception("tempPath - bad path: " + tmp)

    # genFilePathList(args.inputPath, tmp)

    extractFileString(tmp)

    bulidNewFont(args.inputFont, tmp)
