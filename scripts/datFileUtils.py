#!/usr/bin/env python

import sys


def ReadDatFile(datFilePath, weight=-1, rounding=-1, stopAtPreselection=True):
    print("INFO: reading datFile:", datFilePath, "...", end=' ')
    sys.stdout.flush()
    modLines = []
    colNames = []
    with open(datFilePath) as datFile:
        lastLineForSampleReached = False
        for j, line in enumerate(datFile):
            line = line.strip()
            if not len(line):
                continue
            elif len(line.strip("# ").split()) == 1:
                sample = line.strip("# ").split()[0]
                lastLineForSampleReached = False
            else:
                if "variableName" in line:
                    if len(colNames) < 1:
                        colNamesFromLine = line.split()
                        colNames = ["sample"] + colNamesFromLine
                    continue
                elif not lastLineForSampleReached:
                    # splitLine = line.split()
                    # splitLine = [float(x) for x in line.split()[1:]]
                    splitLine = []
                    for idx, x in enumerate(line.split()):
                        try:
                            val = 0
                            if "N" in colNames[idx + 1]:
                                if weight < 0:
                                    val = float(x) / 1000.0
                                else:
                                    val = float(x) / weight
                            elif idx==0:
                                val = int(x)
                            else:
                                val = float(x)
                            if rounding > 0:
                                splitLine.append(round(val, rounding))
                            else:
                                splitLine.append(val)
                        except ValueError:
                            splitLine.append(x)
                    # splitLine = line.split(0) + splitLine
                    # stop reading table for this sample after trainingSelection
                    if (
                        "trainingSelection" in splitLine[1]
                        or "preselection" in splitLine[1]
                        and stopAtPreselection
                    ):
                        lastLineForSampleReached = True
                        splitLine[0] = "preselection"
                    # print 'line looks line:"'+line+'" with length=',len(line)
                    lineToAdd = [sample] + splitLine
                    # modLines.append(tuple(sample+'\t'+line))
                    modLines.append(tuple(x for x in lineToAdd))
    print("Done")
    return modLines, colNames
