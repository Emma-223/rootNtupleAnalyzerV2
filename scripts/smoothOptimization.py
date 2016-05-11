#!/usr/bin/env python

import os, copy, math, sys, numpy
from prettytable import PrettyTable
from ROOT import *

gROOT.SetBatch(True)

optimizationFileName = 'optimization.root'
optimizationTFile = TFile(optimizationFileName)
optimizationTFile.cd()

maxMassPointToUse = 1100

sT_optCuts = []
mee_optCuts = []
mej_optCuts = []
lq_masses = []

for key in gDirectory.GetListOfKeys():
  print 'Key found:',key.GetName(),'with class:',key.GetClassName()
  if 'TGraph' in key.GetClassName():
    # look only at func2 --> pol2
    if not 'func2' in key.GetName():
      continue
    print 'looking at TGraph named',key.GetName()
    graph = optimizationTFile.Get(key.GetName())
    for func in graph.GetListOfFunctions():
      if not 'func2' in func.GetName():
        continue
      else:
        #print 'func=',func.GetName()
        fitFunction = graph.GetFunction(func.GetName()) # using pol2
        #print 'got fitFunction:',fitFunction.Print()
        pars = fitFunction.GetParameters()
        pars.SetSize(fitFunction.GetNpar())
        #print list(pars)
        xValues = graph.GetX()
        xValues.SetSize(graph.GetN())
        # round to nearest 5 GeV
        funcYvalues = [5*round(float(fitFunction.Eval(x))/5) if x <=maxMassPointToUse else 5*round(float(fitFunction.Eval(maxMassPointToUse))/5) for x in xValues]
        graphFunc = TGraph(len(funcYvalues),numpy.array(xValues),numpy.array(funcYvalues))
        graphFunc.SetMarkerStyle(20)
        # nominal graph style
        graph.SetMarkerStyle(24)
        canvas = TCanvas('canvas','',1000,500)
        canvas.cd()
        gStyle.SetOptFit(0)
        gStyle.SetOptStat(0)
        graph.GetListOfFunctions().FindObject("stats").Delete()
        mg = TMultiGraph()
        mg.Add(graph)
        mg.Add(graphFunc)
        mg.Draw('a')
        mg.GetXaxis().SetTitle('LQ mass [GeV]')
        mg.GetXaxis().SetTitleSize(0.04)
        mg.GetXaxis().SetTitleOffset(1.1)
        mg.GetXaxis().SetNdivisions(220)
        mg.GetXaxis().SetRangeUser(250,2050)
        mg.GetXaxis().SetLabelSize(0.03)
        mg.GetYaxis().SetLabelSize(0.03)
        if 'sT' in graph.GetName():
          mg.GetYaxis().SetTitle('Opt. S_{T} cut [GeV]')
        elif 'e1e1' in graph.GetName():
          mg.GetYaxis().SetTitle('Opt. M(ee) cut [GeV]')
        elif 'ej' in graph.GetName():
          mg.GetYaxis().SetTitle('Opt. M_{min}(ej) cut [GeV]')
        mg.GetYaxis().SetTitleSize(0.04)
        mg.GetYaxis().SetTitleOffset(1.0)
        mg.Draw('ap')
        leg = TLegend(0.5,0.2,0.85,0.3)
        leg.SetBorderSize(1)
        leg.AddEntry(graph,'"Raw result" of optimization','p')
        leg.AddEntry(fitFunction,'Fit (pol2) of "raw result"','l')
        leg.AddEntry(graphFunc,'Evaluation of fit','p')
        leg.Draw()
        canvas.Modified()
        gPad.Modified()
        gPad.Update()
        canvas.SaveAs(graph.GetName().replace('graph_','')+'.png')

        ### wait for input to keep the GUI (which lives on a ROOT event dispatcher) alive
        #if __name__ == '__main__':
        #   rep = ''
        #   while not rep in [ 'c', 'C' ]:
        #      rep = raw_input( 'enter "c" to continue: ' )
        #      if 1 < len(rep):
        #         rep = rep[0]
        # for tables
        if len(lq_masses)<=0:
          lq_masses = list(xValues)
        if 'sT' in graph.GetName():
          sT_optCuts = list(funcYvalues)
        elif 'e1e2' in graph.GetName():
          mee_optCuts = list(funcYvalues)
        elif 'ej' in graph.GetName():
          mej_optCuts = list(funcYvalues)
        break

# print tables
lq_masses = [int(mass) for mass in lq_masses]
sT_optCuts = [int(st) for st in sT_optCuts]
mee_optCuts = [int(mee) for mee in mee_optCuts]
mej_optCuts = [int(mej) for mej in mej_optCuts]
columnNames = [str(mass) for mass in lq_masses if mass<=maxMassPointToUse ]
columnNames[-1] = '>='+columnNames[-1]
columnNames.insert(0,'Var/LQMass')
#print columnNames
# reduce sizes
sT_optCuts = [st for i, st in enumerate(sT_optCuts) if lq_masses[i] <= maxMassPointToUse]
mee_optCuts = [mee for i, mee in enumerate(mee_optCuts) if lq_masses[i] <= maxMassPointToUse]
mej_optCuts = [mej for i, mej in enumerate(mej_optCuts) if lq_masses[i] <= maxMassPointToUse]
t = PrettyTable(columnNames)

t.float_format = "4.3"
#t.align['VarName'] = 'l'
t.align = 'l'
stRow = ['sT']
stRow.extend(sT_optCuts)
#print stRow
#print 'len columnNames:',len(columnNames),'len stRow:',len(stRow)
t.add_row(stRow)
meeRow = ['Mee']
meeRow.extend(mee_optCuts)
t.add_row(meeRow)
mejRow = ['Mej']
mejRow.extend(mej_optCuts)
t.add_row(mejRow)
print t

optimizationTFile.Close()
exit(0)
