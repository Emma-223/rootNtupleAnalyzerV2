#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i config/2016_customNanoSkim_eosuser/inputListAllCurrent.txt -o rskSingleEleL_28may2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -j 500 -q workday -d /eos/user/s/scooper/LQ/Nano/rskSingleEleL_28may2019 -r
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i config/2016_nanoPostProc_eosuser/inputListAllCurrent.txt -o rskSingleEleL_31may2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -j 500 -q workday -d /eos/user/s/scooper/LQ/Nano/rskSingleEleL_31may2019 -r
# this one worked aside from ntuple format issue...
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i config/2016_nanoPostProc_eoscms/inputListAllCurrent.txt -o rskSingleEleL_7jun2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -j 100 -q workday -d /eos/user/s/scooper/LQ/Nano/rskSingleEleL_7jun2019 -r
# now use different binaries
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -e mainMGMC -i config/2016_nanoPostProc_eoscms/inputList_mgMC.txt -o rskSingleEleL_10jun2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -j 80 -q workday -d /eos/user/s/scooper/LQ/Nano/rskSingleEleL_10jun2019 -r
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -e mainPythiaMC -i config/2016_nanoPostProc_eoscms/inputList_pythiaMC.txt -o rskSingleEleL_10jun2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -j 80 -q workday -d /eos/user/s/scooper/LQ/Nano/rskSingleEleL_10jun2019 -r
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -e mainData -i config/2016_nanoPostProc_eoscms/inputList_data.txt -o rskSingleEleL_10jun2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -j 80 -q workday -d /eos/user/s/scooper/LQ/Nano/rskSingleEleL_10jun2019 -r
## increase queue time
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -e mainMGMC -i config/2016_nanoPostProc_eoscms/inputList_mgMC.txt -o rskSingleEleL_10jun2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -j 80 -q tomorrow -d /eos/user/s/scooper/LQ/Nano/rskSingleEleL_10jun2019 -r
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -e mainPythiaMC -i config/2016_nanoPostProc_eoscms/inputList_pythiaMC.txt -o rskSingleEleL_10jun2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -j 80 -q tomorrow -d /eos/user/s/scooper/LQ/Nano/rskSingleEleL_10jun2019 -r
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -e mainData -i config/2016_nanoPostProc_eoscms/inputList_data.txt -o rskSingleEleL_10jun2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -j 80 -q tomorrow -d /eos/user/s/scooper/LQ/Nano/rskSingleEleL_10jun2019 -r
# but don't need longer queue
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -e mainMGMC -i config/2016_nanoPostProc_eoscms_comb/inputList_mgMC.txt -o rskSingleEleL_14jun2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -j 10 -q longlunch -d /eos/user/s/scooper/LQ/Nano/rskSingleEleL_14jun2019 -r
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -e mainPythiaMC -i config/2016_nanoPostProc_eoscms_comb/inputList_pythiaMC.txt -o rskSingleEleL_14jun2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -j 10 -q longlunch -d /eos/user/s/scooper/LQ/Nano/rskSingleEleL_14jun2019 -r
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -e mainData -i config/2016_nanoPostProc_eoscms_comb/inputList_data.txt -o rskSingleEleL_14jun2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -j 10 -q longlunch -d /eos/user/s/scooper/LQ/Nano/rskSingleEleL_14jun2019 -r
# with ttreereadertools!
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i config/2016_nanoPostProc_eoscms_comb/inputListAllCurrent.txt -o /afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/nano/2016/rskSingleEleL_3jul2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -j 10 -q longlunch -d /eos/user/s/scooper/LQ/Nano/rskSingleEleL_3jul2019 -r
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i config/2016_nanoPostProc_eoscms/inputListAllCurrent.txt -o /afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/nano/2016/rskSingleEleL_9jul2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -j 10 -q longlunch -d /eos/user/s/scooper/LQ/Nano/rskSingleEleL_9jul2019 -r
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i config/2016_nanoPostProc_eoscms/inputListAllCurrent.txt -o /afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/nano/2016/rskSingleEleL_30jul2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -j 10 -q workday -d /eos/user/s/scooper/LQ/Nano/rskSingleEleL_30jul2019 -r
# move to tomorrow queue
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -i config/2016_nanoPostProc_eoscms/inputListAllCurrent.txt -o /afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/nano/2016/rskSingleEleL_30jul2019 -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -j 10 -q tomorrow -d /eos/user/s/scooper/LQ/Nano/rskSingleEleL_30jul2019 -r
#SKIMNAME=rskSingleEleL_27mar2020
#INPUTLIST=config/nanoV6_2017_postProc/inputListAllCurrent.txt
#python scripts/launchAnalysis_batch_ForSkimToEOS.py -j 20 -q tomorrow -i $INPUTLIST -o /afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/nanoV6/2017/$SKIMNAME -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2015/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -d /eos/user/s/scooper/LQ/NanoV6/2017/$SKIMNAME -r
# 2018
SKIMNAME=rskSingleEleL_15apr2020
INPUTLIST=config/nanoV6_2018_postProc/inputListAllCurrent.txt
python scripts/launchAnalysis_batch_ForSkimToEOS.py -j 20 -q tomorrow -i $INPUTLIST -o /afs/cern.ch/user/s/scooper/work/private/data/Leptoquarks/nanoV6/2018/$SKIMNAME -n Events -c /afs/cern.ch/user/s/scooper/work/private/LQNanoAODAttempt/Leptoquarks/analyzer/rootNtupleMacrosV2/config2018/ReducedSkims/cutTable_lq1_skim_SingleEle_loose.txt -d /eos/user/s/scooper/LQ/NanoV6/2018/$SKIMNAME -r