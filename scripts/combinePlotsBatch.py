#!/usr/bin/env python3

# ---Import
import sys
import string
from optparse import OptionParser
import os
from ROOT import TFile, gROOT, SetOwnership, TObject
import re
import multiprocessing
import traceback
import subprocess
import shlex
import shutil
import copy
import time
from graphlib import TopologicalSorter
from collections import OrderedDict
import pprint
import tempfile
from termcolor import colored

import combineCommon

gROOT.SetBatch(True)


def RunCommand(args):
    timeStarted = time.time()
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    timeDelta = time.time() - timeStarted
    if proc.returncode != 0:
        print(colored("command '{}' failed.".format(" ".join(args)), "red"))
        print(colored("stdout = ", stdout, "green"))
        print(colored("stderr = ", stderr, "red"))
        raise RuntimeError("RunCommand failed")
    return timeDelta


def CheckForFile(filename):
    filename = filename.replace("root://eoscms/", "/eos/cms/").replace("root://eosuser/", "/eos/user/")
    if not filename.startswith("/eos"):
        if os.path.isfile(filename):
            return True
    else:
        if not filename.startswith("/eos/user"):
            serverName = filename.split('/store')[0].strip('/').replace('/', '')
        else:
            serverName = "eosuser"
        my_env = os.environ.copy()
        my_env["EOS_MGM_URL"] = "root://{}.cern.ch/".format(serverName)
        result = subprocess.run(["eos", "ls", filename], env=my_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result == 0:
            return True
    return False


def RemoveFile(filename):
    filename = filename.replace("root://eoscms/", "/eos/cms/").replace("root://eosuser/", "/eos/user/")
    if not os.path.isfile(filename):
        return
    if not filename.startswith("/eos"):
        os.remove(filename)
    else:
        if not filename.startswith("/eos/user"):
            serverName = filename.split('/store')[0].strip('/').replace('/', '')
        else:
            serverName = "eosuser"
        my_env = os.environ.copy()
        my_env["EOS_MGM_URL"] = "root://{}.cern.ch/".format(serverName)
        result = subprocess.check_call(["eos", "rm", filename], env=my_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def RenameLHECombBins(histo):
    binsToRename = ["LHEPdf_UpComb", "LHEPdf_DownComb", "LHEScale_UpComb", "LHEScale_DownComb"]
    renamedBins = ["LHEPdfCombUp", "LHEPdfCombDown", "LHEScaleCombUp", "LHEScaleCombDown"]
    for idx, binName in enumerate(binsToRename):
        binNum = histo.GetYaxis().FindBin(binName)
        if binNum > 0:
            histo.GetYaxis().SetBinLabel(binNum, renamedBins[idx])


def SavePrunedSystHistos(inputRootFileName, outputRootFileName):
    classesToKeep = ["TH1", "TProfile", "TMap"]
    myFile = TFile.Open(inputRootFileName)
    if not myFile:
        raise RuntimeError("Could not open file '{}'.".format(inputRootFileName))
    myOutputFile = TFile.Open(outputRootFileName, "recreate", "", 207)
    for key in myFile.GetListOfKeys():
        nBytes = 0
        histoName = key.GetName()
        htemp = key.ReadObj()
        if not htemp or htemp is None:
            raise RuntimeError("failed to get histo named:", histoName, "from file:", myFile.GetName())
        if not any(htemp.InheritsFrom(className) for className in classesToKeep):
            continue
        SetOwnership(htemp, True)
        myOutputFile.cd()
        if "systematics" not in histoName.lower() or htemp.InheritsFrom("TMap"):
            myOutputFile.cd()
            if htemp.InheritsFrom("TMap"):
                nBytes = htemp.Write(htemp.GetName(), TObject.kSingleKey)
            else:
                nBytes = htemp.Write()
            if nBytes <= 0:
                raise RuntimeError("Error writing into the output file '{}': wrote {} bytes to file when writing object '{}' of class '{}'.".format(myOutputFile.GetName(), nbytes, histoName, htemp.ClassName()))
            continue
        pdfWeightLabels = [label.GetString().Data() for label in htemp.GetYaxis().GetLabels() if "LHEPdfWeight" in label.GetString().Data()]
        shapeSystLabels = [htemp.GetYaxis().GetBinLabel(yBin) for yBin in range(0, htemp.GetNbinsY()+1) if "LHEScaleWeight_" in htemp.GetYaxis().GetBinLabel(yBin)][1:]  # remove all but first and use that one for the comb.
        binsToRemove = pdfWeightLabels+shapeSystLabels
        myOutputFile.cd()
        htemp = combineCommon.RemoveHistoBins(htemp, "y", binsToRemove)
        RenameLHECombBins(htemp)
        myOutputFile.cd()
        nBytes = htemp.Write()
        if nBytes <= 0:
            raise RuntimeError("Error writing into the output file '{}': wrote {} bytes to file when writing object '{}' of class '{}'.".format(myOutputFile.GetName(), nbytes, histoName, htemp.ClassName()))
    myOutputFile.Close()
    myFile.Close()


def CalculateWeight(Ntot, xsection_val, intLumi, sumWeights, dataset_fromInputList, lhePdfWeightSumw=0.0, pdfReweight=False):
    if xsection_val == "-1":
        weight = 1.0
        plotWeight = 1.0
        xsection_X_intLumi = Ntot
        sumWeights = -1
        print("\t[data]", end=' ', flush=True)
    else:
        xsection_X_intLumi = float(xsection_val) * float(intLumi)
        print("\t[MC]", end=' ', flush=True)

        # removed 2018 March 2
        # XXX: This is incorrect anyway.
        # if re.search('TT_',dataset_fromInputList):
        #  avgTopPtWeight = sumTopPtWeights / Ntot
        #  print '\tapplying extra TopPt weight of',avgTopPtWeight,'to',dataset_fromInputList
        #  xsection_X_intLumi/=avgTopPtWeight

        if pdfReweight:
            print("\tapplying LHEPdfWeight={} to dataset={}".format(lhePdfWeightSumw, dataset_fromInputList)+"[instead of original sumWeights={}]".format(sumWeights), flush=True)
            sumWeights = lhePdfWeightSumw

        # now calculate the actual weight
        # weight = 1.0
        # if Ntot == 0:
        #     weight = float(0)
        # else:
        #     print "\tapplying sumWeights=", sumWeights, "to", dataset_fromInputList
        #     weight = xsection_X_intLumi / sumWeights
        print("\tapplying sumWeights=", sumWeights, "to", dataset_fromInputList, flush=True)
        weight = xsection_X_intLumi / sumWeights
        plotWeight = weight / 1000.0
    return weight, plotWeight, xsection_X_intLumi


def MakeCombinedSample(sample, dictSamples, dictDatasetsFileNames, tfileNameTemplate, datFileNameTemplate, samplesToSave, dictFinalHisto, dictFinalTables):
    sampleInfo = dictSamples[sample]
    pieceList = sampleInfo["pieces"]
    corrLHESysts = sampleInfo["correlateLHESystematics"]
    isMC = sampleInfo["isMC"]
    outputTfile = TFile.Open(tfileNameTemplate.format(sample), "RECREATE", "", 207)
    outputDatFile = datFileNameTemplate.format(sample)
    histoDictThisSample = OrderedDict()
    # tablesThisSample = []
    sampleTable = {}
    piecesAdded = []
    isQCD = "qcd" in tfileNameTemplate.lower()

    combineCommon.ParseXSectionFile(options.xsection)
    # piecesToAdd = combineCommon.PartialExpand(pieceList)
    piecesToAdd = combineCommon.ExpandPieces(pieceList, dictSamples)
    # print("For sample {}, piecesToAdd looks like {}, dictDatasetsFileNames={}".format(sample, piecesToAdd, dictDatasetsFileNames))
    datasetsFileNamesCleaned = {combineCommon.SanitizeDatasetNameFromInputList(k): v for k, v in dictDatasetsFileNames.items()}
    # print("For sample {}, datasetsFileNamesCleaned={}".format(sample, datasetsFileNamesCleaned))

    # ---Loop over datasets in the inputlist
    for currentPiece in piecesToAdd:
        if currentPiece in datasetsFileNamesCleaned.keys():
            matchingPiece = currentPiece
        else:
            raise RuntimeError("ERROR: for sample {}, could not find currentPiece={} in datasetsFileNamesCleaned={}".format(sample, currentPiece, datasetsFileNamesCleaned))

        print("\t[{}] found matching dataset:".format(sample), matchingPiece + " ... ")
        print("\t[{}] looking up xsection...".format(sample), end=' ', flush=True)
        try:
            xsection_val = combineCommon.lookupXSection(matchingPiece)
            xsectionFound = True
            print("found", xsection_val, "pb", flush=True)
        except RuntimeError:
            print("did not find xsection", flush=True)
            xsectionFound = False

        print("For sample {}, datasetsFileNamesCleaned[{}]={}".format(sample, currentPiece, datasetsFileNamesCleaned[currentPiece]))
        sumWeights = 0
        lhePdfWeightSumw = 0
        Ntot = 0
        thisPieceTable = {}
        thisPieceHistos = {}
        for rootFilename in datasetsFileNamesCleaned[currentPiece]:
            doWeightingThisFile = False
            if len(datasetsFileNamesCleaned[currentPiece]) == 1:
                doWeightingThisFile = True
            inputDatFile = rootFilename.replace(".root", ".dat").replace("plots", "tables").replace("root://eoscms/", "/eos/cms/").replace("root://eosuser/", "/eos/user/")
            print("\tfile: {}".format(rootFilename), flush=True)
            # print("INFO: TFilenameTemplate = {}".format(tfileNameTemplate.format(sample)))
            if useInclusionList:
                sampleHistos = GetHistosFromInclusionList(rootFilename, sample, histoNamesToUse, xsectionFound)
            else:
                sampleHistos = combineCommon.GetSampleHistosFromTFile(rootFilename, sample, xsectionFound)

            # ---Read .dat table
            data = combineCommon.ParseDatFile(inputDatFile)
            NtotThisFile = float(data[0]["Npass"])
            sampleNameForHist = ""

            if xsectionFound:
                # ---Calculate weight
                sumWeightsThisFile = 0
                lhePdfWeightSumwThisFile = 0
                for hist in sampleHistos:
                    if "SumOfWeights" in hist.GetName():
                        sumWeightsThisFile = hist.GetBinContent(1) if "powhegMiNNLO" not in rootFilename else hist.GetBinContent(3)
                    elif "LHEPdfSumw" in hist.GetName():
                        lhePdfWeightSumwThisFile = hist.GetBinContent(1)  # sum[genWeight*pdfWeight_0]
                if doWeightingThisFile:
                    doPDFReweight = False
                    # if "2016" in inputRootFile:
                    #     if "LQToBEle" in inputRootFile or "LQToDEle" in inputRootFile:
                    #         doPDFReweight = doPDFReweight2016LQSignals
                    weight, plotWeight, xsection_X_intLumi = CalculateWeight(
                        NtotThisFile, xsection_val, options.intLumi, sumWeightsThisFile, matchingPiece, lhePdfWeightSumwThisFile, doPDFReweight
                    )
                    # print "xsection: " + xsection_val,
                    print("\t[{}] weight(x1000): ".format(sample) + str(weight) + " = " + str(xsection_X_intLumi), "/", end=' ', flush=True)
                    print(str(sumWeightsThisFile), flush=True)
                else:
                    sumWeights += sumWeightsThisFile
                    lhePdfWeightSumw += lhePdfWeightSumwThisFile
                    plotWeight = 1.0
                    Ntot += NtotThisFile
            elif rootFilename == tfileNameTemplate.format(matchingPiece):
                if not doWeightingThisFile:
                    raise RuntimeError("this '{}' should be a file already scaled, but there are multiple files in the currentPiece '{}' of the sample '{}' {}:".format(
                        rootFilename, currentPiece, sample, datasetsFileNamesCleaned[currentPiece]))
                print("\t[{}] histos taken from file already scaled".format(sample), flush=True)
                # xsection_val = 1.0
                weight = 1.0
                plotWeight = 1.0
                xsection_X_intLumi = NtotThisFile
                sampleNameForHist = matchingPiece
                # print("\t[{}] zeroing negative histo bins".format(sample), flush=True)
                # combineCommon.ZeroNegativeHistoBins(sampleHistos)
                ##XXX FIXME PUT BACK
            else:
                raise RuntimeError("xsection not found")

            # ---Update table
            dataThisFile = combineCommon.FillTableErrors(data, rootFilename, sampleNameForHist)
            if doWeightingThisFile:
                data = combineCommon.CreateWeightedTable(dataThisFile, weight, xsection_X_intLumi)
                Ntot = float(data[0]["Npass"])
                print("INFO: inputDatFile={} for sample={}, NoCuts(weighted)={}".format(inputDatFile, sample, Ntot), flush=True)
                sampleTable = combineCommon.UpdateTable(data, sampleTable)
                print("INFO: sampleTable for sample={} now has NoCuts(weighted)={}".format(sample, float(sampleTable[0]["Npass"])), flush=True)
                # print("\t[{}] zeroing negative table yields".format(sample), flush=True)
                # combineCommon.ZeroNegativeTableYields(sampleTable)
                ##XXX FIXME PUT BACK
                # tablesThisSample.append(data)
            else:
                thisPieceTable = combineCommon.UpdateTable(dataThisFile, thisPieceTable)

            if not options.tablesOnly:
                print("INFO: doWeightingThisFile=", doWeightingThisFile, "; updating thisPieceHistos using plotWeight=", plotWeight)
                thisPieceHistos = combineCommon.UpdateHistoDict(thisPieceHistos, sampleHistos, matchingPiece, "", plotWeight, corrLHESysts, not isMC, isQCD)

        if not doWeightingThisFile:
            doPDFReweight = False
            # if "2016" in inputRootFile:
            #     if "LQToBEle" in inputRootFile or "LQToDEle" in inputRootFile:
            #         doPDFReweight = doPDFReweight2016LQSignals
            weight, plotWeight, xsection_X_intLumi = CalculateWeight(
                Ntot, xsection_val, options.intLumi, sumWeights, matchingPiece, lhePdfWeightSumw, doPDFReweight
            )
            print("\t[{}] weight(x1000): ".format(currentPiece) + str(weight) + " = " + str(xsection_X_intLumi), "/", end=' ', flush=True)
            print(str(sumWeights), flush=True)
            data = combineCommon.CreateWeightedTable(thisPieceTable, weight, xsection_X_intLumi)
            Ntot = float(data[0]["Npass"])
            print("INFO: for sample={}, currentPiece={} NoCuts(weighted)={}".format(sample, currentPiece, Ntot), flush=True)
            sampleTable = combineCommon.UpdateTable(data, sampleTable)
            print("INFO: done with currentPiece={}, sampleTable for sample={} now has NoCuts(weighted)={}".format(currentPiece, sample, float(sampleTable[0]["Npass"])), flush=True)
            # tablesThisSample.append(data)
        else:
            plotWeight = 1.0
        if not options.tablesOnly:
            print("INFO: finally, doWeightingThisFile=", doWeightingThisFile, "; updating histoDictThisSample using plotWeight=", plotWeight, "sample=", sample)
            histoDictThisSample = combineCommon.UpdateHistoDict(histoDictThisSample, thisPieceHistos.values(), matchingPiece, sample, plotWeight, corrLHESysts, not isMC, isQCD)
        piecesAdded.append(matchingPiece)

    # validation of combining pieces
    # if set(piecesAdded) != set(pieceList):
    if set(piecesAdded) != set(piecesToAdd):
        errMsg = "ERROR: for sample {}, the following pieces requested in sampleListForMerging were not added: ".format(sample)
        errMsg += str(list(set(piecesAdded).symmetric_difference(set(piecesToAdd))))
        errMsg += "\twhile the pieces indicated as part of the sample were:"
        errMsg += str(sorted(piecesToAdd))
        errMsg += "\tand the pieces added were:"
        errMsg += str(sorted(piecesAdded))
        errMsg += "\tRefusing to proceed."
        raise RuntimeError("sample validation failed: {}".format(errMsg))

    # ---Create final tables
    combinedTableThisSample = combineCommon.CalculateEfficiency(sampleTable)
    with open(outputDatFile, "w") as theFile:
        combineCommon.WriteTable(combinedTableThisSample, sample, theFile)
    # for writing tables later
    dictFinalTables[sample] = combinedTableThisSample

    # write histos
    if not options.tablesOnly:
        combineCommon.WriteHistos(outputTfile, histoDictThisSample, sample, corrLHESysts, isMC, True)
        # always keep tmap, eventspassingcuts, and 2-D syst hists in final root file
        if not sampleInfo["save"]:
            objectNamesToKeep = ["eventspassingcuts", "systematicnametobranchesmap"]
            histsToKeep = {k:v for k, v in histoDictThisSample.items() if any(objectName in v.GetName().lower() for objectName in objectNamesToKeep) or (v.InheritsFrom("TH2") and "systematics" in v.GetName().lower())}
            tfileKeepName = tfileNameTemplate.format(sample).replace("_plots.root", "_keep_plots.root")
            outputTfileKeep = TFile.Open(tfileKeepName, "RECREATE", "", 207)
            combineCommon.WriteHistos(outputTfileKeep, histsToKeep, sample, corrLHESysts, isMC, True)
            outputTfileKeep.Close()
            # remove for now to keep pdf/scale weight bins
            # print("INFO: saving pruned hists", flush=True)
            if pruneSystHists:
                SavePrunedSystHistos(tfileKeepName, tfileKeepName.replace("_keep_plots.root", "_keep_plots_pruned.root"))
            # print("INFO: done saving pruned hists", flush=True)
        if sample in samplesToSave:
            dictFinalHisto[sample] = histoDictThisSample
    outputTfile.Close()
    # remove for now to keep pdf/scale weight bins
    # print("INFO: [save] saving pruned hists", flush=True)
    if pruneSystHists:
        SavePrunedSystHistos(tfileNameTemplate.format(sample), tfileNameTemplate.format(sample).replace("_plots.root", "_plots_pruned.root"))
    # print("INFO: [save] done saving pruned hists", flush=True)
    #dictDatasetsFileNames[sample] = tfileNameTemplate.format(sample)
    #print("[{}] now dictDatasetsFileNames={}".format(sample, dictDatasetsFileNames), flush=True)
    return tfileNameTemplate.format(sample), outputDatFile


def GetHistosFromInclusionList(tfileName, sample, inclusionList, keepHistName=True):
    histNameToHistDict = {}
    if tfileName.startswith("/eos/cms"):
        tfileName = "root://eoscms/" + tfileName
    elif tfileName.startswith("/eos/user"):
        tfileName = "root://eosuser/" + tfileName
    tfile = TFile.Open(tfileName)
    tempHistList = []
    if keepHistName==True:
        for histName in inclusionList:
            hist = tfile.Get(histName)
            #print("get hist ",histName," from ",tfile)
            tempHistList.append(hist)
    else:
        for key in tfile.GetListOfKeys():
            histoName = key.GetName()
            hist = key.ReadObj()
            tempHistList.append(hist)
    for htemp in tempHistList:
        htempName = htemp.GetName()
        SetOwnership(htemp, True)
        if htemp.InheritsFrom("TH1"):
            htemp.SetDirectory(0)
        histNameToHistDict[htempName] = htemp
    sortedDict = dict(sorted(histNameToHistDict.items()))
    for htemp in sortedDict.values():
        if not keepHistName:
            hname = htemp.GetName()
            if "cutHisto" in hname:
                prefixEndPos = hname.rfind("cutHisto")
            elif len(re.findall("__", hname)) > 2:
                raise RuntimeError("Found hist {} in file {} and unclear how to shorten its name".format(hname, tfile.GetName()))
            else:
                prefixEndPos = hname.rfind("__")+2
            htemp.SetName(hname[prefixEndPos:])
    sampleHistos = list(sortedDict.values())
    tfile.Close()
    if len(sampleHistos) < 1:
        raise RuntimeError(
                "GetHistosFromInclusionList({}, {}) -- failed to read any histos for the sampleName from this file!".format(tfile.GetName(), sampleName))
    return sampleHistos

####################################################################################################
# RUN
####################################################################################################
pruneSystHists = False  # remove individual PDF/LHE weight bins from syst histos, but takes forever


# ---Run
# Turn off warning messages
gROOT.ProcessLine("gErrorIgnoreLevel=2001;")

# ---Option Parser
usage = "usage: %prog [options] \nExample: \n./combinePlotsBatch.py -i /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/config/inputListAllCurrent.txt -c analysisClass_genStudies -d /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/data/output -l 100 -x /home/santanas/Data/Leptoquarks/RootNtuples/V00-00-06_2008121_163513/xsection_pb_default.txt -o /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/data/output -s /home/santanas/Workspace/Leptoquarks/rootNtupleAnalyzer/config/sampleListForMerging.txt"

parser = OptionParser(usage=usage)

parser.add_option(
    "-i",
    "--inputList",
    dest="inputList",
    help="list of all datasets to be used (full path required)",
    metavar="LIST",
)

parser.add_option(
    "-c",
    "--code",
    dest="analysisCode",
    help="name of the CODE.C code used to generate the rootfiles (which is the beginning of the root file names before ___)",
    metavar="CODE",
)

parser.add_option(
    "-d",
    "--inputDir",
    dest="inputDir",
    help="the directory INDIR contains the rootfiles with the histograms to be combined (full path required)",
    metavar="INDIR",
)

parser.add_option(
    "-l",
    "--intLumi",
    dest="intLumi",
    help="results are rescaled to the integrated luminosity INTLUMI (in pb-1)",
    metavar="INTLUMI",
)

parser.add_option(
    "-x",
    "--xsection",
    dest="xsection",
    help="the file XSEC contains the cross sections (in pb) for all the datasets (full path required). Use -1 as cross section value for no-rescaling",
    metavar="XSEC",
)

parser.add_option(
    "-o",
    "--outputDir",
    dest="outputDir",
    help="the directory OUTDIR contains the output of the program (full path required)",
    metavar="OUTDIR",
)

parser.add_option(
    "-s",
    "--sampleListForMerging",
    dest="sampleListForMerging",
    help="put in the file SAMPLELIST the name of the sample with the associated strings which should  match with the dataset name (full path required)",
    metavar="SAMPLELIST",
)

parser.add_option(
    "-t",
    "--tablesOnly",
    action="store_true",
    dest="tablesOnly",
    default=False,
    help="only combine tables, do not do plots",
    metavar="TABLESONLY",
)

parser.add_option(
    "-b",
    "--ttbarBkg",
    action="store_true",
    dest="ttbarBkg",
    default=False,
    help="do the ttbar background prediction from data; don't write out any other plots",
    metavar="TTBARBKG",
)

parser.add_option(
    "-q",
    "--qcdClosure",
    action="store_true",
    dest="qcdClosure",
    default=False,
    help="do the QCD observed 1 pass HEEP 1 fail HEEP yield (cej), subtracting non-QCD processes from data using MC; don't write out any other plots",
    metavar="QCDCLOSURE",
)

parser.add_option(
    "-k",
    "--keepInputFiles",
    action="store_true",
    dest="keepInputFiles",
    default=False,
    help="Don't delete individual sample root files (intermediate outputs); defaults to False",
    metavar="KEEPINPUTFILES",
)

parser.add_option(
    "-z", #all the letters that I thought were sensible to use for this were already taken. -Emma
    "--histInclusionList",
    dest="histInclusionList",
    default="",
    help="Use an inclusion list to specify which histograms make it into the output file. Defaults to False",
    metavar="HISTINCLUSIONLIST",
)

parser.add_option(
    "--sample",
    dest="sample",
    help="sample to combine",
    metavar="SAMPLE",
)

(options, args) = parser.parse_args()

requiredOpts = [options.inputList, options.analysisCode, options.inputDir, options.intLumi, options.xsection, options.outputDir, options.sampleListForMerging, options.sample]
if any(opt is None for opt in requiredOpts):
    print("ERROR: one or more required options not given: {}".format([opt for opt in requiredOpts if opt is None]))
    raise RuntimeError(usage)

# ---Check if sampleListForMerging file exists
if os.path.isfile(options.sampleListForMerging) is False:
    raise RuntimeError("File " + options.sampleListForMerging + " not found")

# ---Check if xsection file exists
if os.path.isfile(options.xsection) is False:
    raise RuntimeError("File " + options.xsection + " not found")

useInclusionList = False
histoNamesToUse = []
if os.path.isfile(options.histInclusionList) is True:
    print("using inclusion list: ",options.histInclusionList)
    useInclusionList = True
    with open(options.histInclusionList) as f:
        histoNamesToUse = [line.rstrip() for line in f]
#print("including histos: ",histoNamesToUse)

sample = options.sample

print("Launched like:")
print("python ", end=' ')
for arg in sys.argv:
    print(" " + arg, end=' ')
print()

doPDFReweight2016LQSignals = False
if doPDFReweight2016LQSignals:
    print("Doing PDF reweighting for 2016 LQ B/D signal samples")

if not os.path.exists(options.outputDir):
    os.makedirs(options.outputDir)

xsectionDict = combineCommon.ParseXSectionFile(options.xsection)
# print 'Dataset      XSec'
# for key,value in xsectionDict.iteritems():
#  print key,'  ',value

dictSamples = combineCommon.GetSamplesToCombineDict(options.sampleListForMerging)
dictSamplesPiecesAdded = {}
for key in dictSamples.keys():
    dictSamplesPiecesAdded[key] = []

# --- Declare efficiency tables
dictFinalTables = {}
# --- Declare histograms
dictFinalHisto = {}
# --- Samples to save in final histo dict
samplesToSave = {}
sampleFiles = {}

if options.ttbarBkg or options.qcdClosure:
    raise RuntimeError("TTBar Bkg and QCD closure options not yet implemented here")

# if not options.tablesOnly:
#     if options.ttbarBkg:
#         ttbarDataRawSampleName = "TTBarUnscaledRawFromDATA"
#         nonTTbarAMCBkgSampleName = "NONTTBARBKG_amcatnloPt_amcAtNLODiboson_emujj"
#         samplesToSave.extend([ttbarDataRawSampleName, nonTTbarAMCBkgSampleName])
#     if options.qcdClosure:
#         qcdDataSampleName = "SinglePhoton_all"
#         nonQCDBkgSampleName = "ALLBKG_powhegTTBar_ZJetWJetPt_amcAtNLODiboson"  # Z, W, TTBar, SingleTop, Diboson, gamma+jets
#         samplesToSave.extend([qcdDataSampleName, nonQCDBkgSampleName])

# check to make sure we have xsections for all samples
# FIXME to look at only files we need in this job
for lin in open(options.inputList):
    lin = lin.strip("\n")
    if lin.startswith("#"):
        continue
    dataset_fromInputList = lin.split("/")[-1].split(".")[0]
    dataset_fromInputList = dataset_fromInputList.replace("_tree", "")
    xsection_val = combineCommon.lookupXSection(
        combineCommon.SanitizeDatasetNameFromInputList(
            dataset_fromInputList.replace("_tree", "")
        )
    )
foundAllFiles, dictDatasetsFileNames = combineCommon.FindInputFiles(options.inputList, options.analysisCode, options.inputDir)
if not foundAllFiles:
    raise RuntimeError("Some files not found.")
else:
    print("\bDone.  All root/dat files are present.")
    print()

tfileOutputPath = options.outputDir
if options.outputDir.startswith("/eos/"):
    if options.outputDir.startswith("/eos/cms"):
        cmd = "EOS_MGM_URL=root://eoscms/ eos mkdir {}".format(options.outputDir)
    elif options.outputDir.startswith("/eos/user"):
        cmd = "EOS_MGM_URL=root://eosuser/ eos mkdir {}".format(options.outputDir)
    else:
        raise RuntimeError("Don't know how to handle output dir like '{}'".format(outputDir))
    if not os.path.isdir(options.outputDir):
        try:
            proc = subprocess.run(shlex.split(cmd), check=True, universal_newlines=True, stdout=sp.PIPE, stderr=sp.PIPE)
        except subprocess.CalledProcessError as ex:
            print(colored("cmd '{}' failed.".format(cmd), "red"))
            print(colored("stdout = ", ex.stdout, "green"))
            print(colored("stderr = ", ex.stderr, "red"))
            raise RuntimeError("cmd {} failed".format(cmd))
else:
    if not os.path.isdir(options.outputDir):
        os.makedirs(options.outputDir)

print("INFO: Writing files to {}".format(tfileOutputPath))

# outputTableFilename = tfileOutputPath+"/"+options.analysisCode+"_tables.dat"
# outputTableFile = open(outputTableFilename,"w")
# tfilePrefix = tfileOutputPath + "/" + options.analysisCode
tfilePrefix = options.analysisCode
sampleTFileNameTemplate = tfilePrefix + "_{}_plots.root"
sampleDatFileNameTemplate = tfilePrefix + "_{}_tables.dat"

outputFile, outputDatFile = MakeCombinedSample(sample, dictSamples, dictDatasetsFileNames, sampleTFileNameTemplate, sampleDatFileNameTemplate, samplesToSave, dictFinalHisto, dictFinalTables)

# --- Write tables
# haveDatFile = True
# print("INFO: Writing final tables ==> sampleTable for sample={} now has NoCuts={}".format(sample, float(dictFinalTables[sample][0]["Npass"])), flush=True)
# combineCommon.WriteTable(dictFinalTables[sample], sample, outputTableFile)
# # trust, but verify and try to write again if needed
# if not os.path.isfile(outputTableFilename):
#     for sample in dictSamples.keys():
#         print("INFO: Re-writing final tables ==> sampleTable for sample={} now has NoCuts={}".format(sample, float(dictFinalTables[sample][0]["Npass"])), flush=True)
#         combineCommon.WriteTable(dictFinalTables[sample], sample, outputTableFile)
#     if not os.path.isfile(outputTableFilename):
#         print("ERROR: something bad happened when trying to write the table file, as we didn't find a file here: {}".format(outputTableFilename))
#         haveDatFile = False
# if haveDatFile:
#     print("output tables at: {}".format(outputTableFilename), flush=True)


# now handle special backgrounds
# FIXME: will need special handling of these
# if options.ttbarBkg:
#     # special actions for TTBarFromData
#     # subtract nonTTbarBkgMC from TTbarRaw
#     # FIXME: we hardcode the sample names for now
#     ttbarDataPredictionTable = dictFinalTables[ttbarDataRawSampleName]
#     # nonTTbarAMCBkgSampleName = 'NONTTBARBKG_amcatnloPt_emujj'
#     # move to amcAtNLO diboson
#     nonTTbarAMCBkgTable = dictFinalTables[nonTTbarAMCBkgSampleName]
#     ttBarPredName = "TTBarFromDATA"
#     # Mar17 fixing muon pt and eta-->2.4
#     Rfactor = 0.418559  # Ree,emu = Nee/Nemu[TTbarMC]
#     errRfactor = 0.002474
#     print("TTBar data-driven: Using Rfactor =", Rfactor, "+/-", errRfactor)
#     print("TTBar data-driven: Using non-ttbar background sample:", nonTTbarAMCBkgSampleName)
#     # print '0) WHAT DOES THE RAW DATA TABLE LOOK LIKE?'
#     # WriteTable(ttbarDataPredictionTable, ttbarDataRawSampleName, outputTableFile)
#     # remove the x1000 from the nonTTbarBkgMC
#     combineCommon.ScaleTable(nonTTbarAMCBkgTable, 1.0 / 1000.0, 0.0)
#     # print '1) WHAT DOES THE SCALED MC TABLE LOOK LIKE?'
#     # WriteTable(nonTTbarMCBkgTable, nonTTbarMCBkgSampleName, outputTableFile)
#     # subtract the nonTTBarBkgMC from the ttbarRawData, NOT zeroing entries where we run out of data
#     combineCommon.SubtractTables(nonTTbarAMCBkgTable, ttbarDataPredictionTable)
#     # print '2) WHAT DOES THE SUBTRACTEDTABLE LOOK LIKE?'
#     # WriteTable(ttbarDataPredictionTable, ttBarPredName, outputTableFile)
#     # scale by Ree,emu
#     combineCommon.ScaleTable(ttbarDataPredictionTable, Rfactor, errRfactor)
#     # print '3) WHAT DOES THE RfactroCorrectedTABLE LOOK LIKE?'
#     # WriteTable(ttbarDataPredictionTable, ttBarPredName, outputTableFile)
#     combineCommon.SquareTableErrorsForEfficiencyCalc(ttbarDataPredictionTable)
#     combineCommon.CalculateEfficiency(ttbarDataPredictionTable)
#     # print '4) WHAT DOES THE SCALEDTABLE AFTER EFF CALCULATION LOOK LIKE?'
#     combineCommon.WriteTable(ttbarDataPredictionTable, ttBarPredName, outputTableFile)
# 
# if options.qcdClosure:
#     # special actions for the QCD closure test
#     # subtract nonQCD from QCDData yield
#     qcdDataTable = dictFinalTables[qcdDataSampleName]
#     nonQCDBkgTable = dictFinalTables[nonQCDBkgSampleName]
#     qcdClosureSampleName = "QCDClosureObserved"
#     # print "TTBar data-driven: Using non-ttbar background sample:", nonTTbarAMCBkgSampleName
#     # print '0) WHAT DOES THE RAW DATA TABLE LOOK LIKE?'
#     # WriteTable(ttbarDataPredictionTable, ttbarDataRawSampleName, outputTableFile)
#     # remove the x1000 from the nonQCDBkgMC
#     combineCommon.ScaleTable(nonQCDBkgTable, 1.0 / 1000.0, 0.0)
#     # print '1) WHAT DOES THE SCALED MC TABLE LOOK LIKE?'
#     # WriteTable(nonTTbarMCBkgTable, nonTTbarMCBkgSampleName, outputTableFile)
#     # subtract the nonTTBarBkgMC from the ttbarRawData, NOT zeroing entries where we run out of data
#     combineCommon.SubtractTables(nonQCDBkgTable, qcdDataTable)
#     # print '2) WHAT DOES THE SUBTRACTEDTABLE LOOK LIKE?'
#     # WriteTable(ttbarDataPredictionTable, ttBarPredName, outputTableFile)
#     combineCommon.SquareTableErrorsForEfficiencyCalc(qcdDataTable)
#     combineCommon.CalculateEfficiency(qcdDataTable)
#     # print '4) WHAT DOES THE SCALEDTABLE AFTER EFF CALCULATION LOOK LIKE?'
#     combineCommon.WriteTable(qcdDataTable, qcdClosureSampleName, outputTableFile)
# 
# outputTableFile.close()


if not options.tablesOnly:
# FIXME for ttbar/QCD
#     if options.ttbarBkg:
#         # special actions for TTBarFromData
#         # subtract nonTTbarBkgMC from TTbarRaw
#         ttbarDataPredictionHistos = dictFinalHisto[ttbarDataRawSampleName]
#         # print 'ttbarDataPredictionHistos:',ttbarDataPredictionHistos
#         for n, histo in ttbarDataPredictionHistos.items():
#             # subtract the nonTTBarBkgMC from the ttbarRawData
#             # find nonTTbarMCBkg histo; I assume they are in the same order here
#             histoToSub = dictFinalHisto[nonTTbarAMCBkgSampleName][n]
#             ## also write histos that are subtracted
#             # histToSub.Write()
#             # print 'n=',n,'histo=',histo
#             outputTfile.cd()
#             histoTTbarPred = histo.Clone()
#             histoTTbarPred.Add(histoToSub, -1)
#             # scale by Rfactor
#             histoTTbarPred.Scale(Rfactor)
#             histoTTbarPred.SetName(
#                 re.sub(
#                     "__.*?__",
#                     "__" + ttBarPredName + "__",
#                     histoTTbarPred.GetName(),
#                     flags=re.DOTALL,
#                 )
#             )
#             histoTTbarPred.Write()
# 
#     if options.qcdClosure:
#         # special actions for QCDClosure observed
#         # subtract nonQCDBkgMC from data
#         qcdClosureHistos = dictFinalHisto[qcdDataSampleName]
#         # print 'qcdClosureHistos:',qcdClosureHistos
#         for n, histo in qcdClosureHistos.items():
#             # find nonTTbarMCBkg histo; assume they are in the same order here
#             histoToSub = dictFinalHisto[nonQCDBkgSampleName][n]
#             ## also write histos that are subtracted
#             # histToSub.Write()
#             # print 'n=',n,'histo=',histo
#             histoQCDClosure = histo.Clone()
#             histoQCDClosure.Add(histoToSub, -1)
#             histoQCDClosure.SetName(
#                 re.sub(
#                     "__.*?__",
#                     "__" + qcdClosureSampleName + "__",
#                     histoQCDClosure.GetName(),
#                     flags=re.DOTALL,
#                 )
#             )
#             histoQCDClosure.Write()
# 
    if not CheckForFile(outputFile):
        print("ERROR: something bad happened when trying to write the root file, as we didn't find a file here: {}".format(outputFile))
    else:
        print("output plots at: {}".format(outputFile), flush=True)

if options.outputDir.startswith("/eos"):
    print("copy files to {}".format(options.outputDir))
    # if os.path.isfile("{}/{}_plots.root".format(options.outputDir ,options.analysisCode)):
    #     command = ["rm", "{}/{}_plots.root".format(options.outputDir ,options.analysisCode)]
    #     proc = subprocess.run(command, check=True, universal_newlines=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
    
    command = ["xrdcp", "-f", outputFile, "{}/{}".format(options.outputDir, outputFile)]
    # proc = subprocess.run(command, check=True, universal_newlines=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
    RunCommand(command)
    
    if not os.path.isfile("{}/{}".format(options.outputDir, outputFile)):
        print("ERROR: failed to copy root file to eos")
    else:
        print("output plots copied to: {}/{}".format(options.outputDir, outputFile))
    
    # if os.path.isfile("{}/{}_tables.dat".format(options.outputDir ,options.analysisCode)):
    #     command = ["rm", "{}/{}_tables.dat".format(options.outputDir ,options.analysisCode)]
    #     proc = subprocess.run(command, check=True, universal_newlines=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
     
    command = ["xrdcp", "-f", outputDatFile, "{}/{}".format(options.outputDir, outputDatFile)]
    # proc = subprocess.run(command, check=True, universal_newlines=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
    RunCommand(command)
    
    # command = ["rm", "/tmp/{}_plots.root".format(options.analysisCode), "/tmp/{}_tables.dat".format(options.analysisCode)]
    # proc = subprocess.run(command, check=True, universal_newlines=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE)

    if not os.path.isfile("{}/{}".format(options.outputDir, outputDatFile)):
        print("ERROR: failed to copy dat file to eos")
    else:
        print("output plots copied to: {}/{}".format(options.outputDir, outputDatFile))

    if not options.keepInputFiles:
        RemoveFile(outputFile.replace("plots", "keep_plots"))

# ---TODO: CREATE LATEX TABLE (PYTEX?) ---#
