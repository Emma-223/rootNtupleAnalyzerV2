#include <map>
#include <vector>
#include "TTreeReaderValue.h"
#include "TTreeReaderArray.h"
#include "TTreeReader.h"

class TTreeReaderTools {
  public:
    TTreeReaderTools() = delete;
    TTreeReaderTools(TTree* tree);
    template <typename T> T ReadValueBranch(const std::string& branchName);
    template <typename T> T ReadArrayBranch(const std::string& branchName);
    void LoadEntry(Long64_t entry);

  private:
    void checkReaderIsClean();
    void remakeAllReaders();
    std::string getTypeName(const std::string& branchName) const;
    void gotoEntry(Long64_t entry, bool forceCall = false);

    std::map<std::string, TTreeReaderValue<UInt_t>    > m_ttreeValueUIntReaders;
    std::map<std::string, TTreeReaderValue<ULong64_t> > m_ttreeValueULong64Readers;
    std::map<std::string, TTreeReaderValue<Float_t>   > m_ttreeValueFloatReaders;
    std::map<std::string, TTreeReaderValue<Int_t>     > m_ttreeValueIntReaders;
    std::map<std::string, TTreeReaderValue<UChar_t>   > m_ttreeValueUCharReaders;
    std::map<std::string, TTreeReaderValue<Bool_t>    > m_ttreeValueBoolReaders;

    std::map<std::string, TTreeReaderArray<Float_t> > m_ttreeArrayFloatReaders;
    std::map<std::string, TTreeReaderArray<Int_t>   > m_ttreeArrayIntReaders;
    std::map<std::string, TTreeReaderArray<Bool_t>  > m_ttreeArrayBoolReaders;
    std::map<std::string, TTreeReaderArray<UChar_t> > m_ttreeArrayUCharReaders;

    bool m_readerIsClean;
    TTreeReader* m_reader;
    TTree* m_tree;
    Long64_t m_entry;
    Long64_t m_entries;
};

//#include <iostream>
//#include <string>
////#include "include/TTreeReaderTools.h"
//
//TTreeReaderTools::TTreeReaderTools(TTree* tree) :
//  m_tree(tree), m_readerIsClean(true), m_entry(-1) {
//    m_reader = new TTreeReader(tree);
//    m_entries = m_reader->GetEntries(false);
//}
//
//void TTreeReaderTools::LoadEntry(Long64_t entry) {
//  m_entry = entry;
//  gotoEntry(entry);
//}
//
//template <typename T> T TTreeReaderTools::ReadValueBranch(const std::string& branchName) {
//  checkReaderIsClean();
//  std::string type = getTypeName(branchName);
//  if(type=="UInt_t") {
//    std::map<std::string, TTreeReaderValue<UInt_t> >::iterator itr;
//    itr = m_ttreeValueUIntReaders.find(branchName);
//    if(itr != m_ttreeValueUIntReaders.end())
//      return *(itr->second.Get());
//    else {
//      if(!m_readerIsClean)
//        remakeAllReaders();
//      TTreeReaderValue<UInt_t> ttrv = TTreeReaderValue<UInt_t>(*m_reader, branchName.c_str());
//      //m_ttreeValueUIntReaders.insert(std::pair<std::string,TTreeReaderValue<UInt_t> >(branchName,ttrv));
//      gotoEntry(m_entry,true);
//      return *(ttrv.Get());
//    }
//  }
//  else {
//    std::cout << "ERROR: ReadValueBranch for type: " << type << " is not implemented." << std::endl;
//    exit(1);
//  }
//  //else if(type=="ULong64_t") {
//  //}
//  //else if(type=="Float_t") {
//  //}
//  //else if(type=="Int_t") {
//  //}
//  //else if(type=="UChar_t") {
//  //}
//  //else if(type=="Bool_t") {
//  //}
//
//}
//
//template <typename T> T TTreeReaderTools::ReadArrayBranch(const std::string& branchName) {
//  checkReaderIsClean();
//}
//
//
//void TTreeReaderTools::checkReaderIsClean() {
//  if (m_readerIsClean) {
//    std::cout << "ERROR: ReadBranch must not be called before calling GotoEntry" << std::endl;
//    exit(1);
//  }
//}
//
//std::string TTreeReaderTools::getTypeName(const std::string& branchName) const {
//  TBranch* branch = m_reader->GetTree()->GetBranch(branchName.c_str());
//    if(!branch) {
//      std::cout << "ERROR: Unknown branch " << branchName << std::endl;
//      exit(2);
//    } 
//    TLeaf* leaf = branch->GetLeaf(branchName.c_str());
//    return std::string(leaf->GetTypeName());
//}
//
//void TTreeReaderTools::gotoEntry(Long64_t entry, bool forceCall) {
//  m_readerIsClean = false;
//  if(m_entry != entry || forceCall) {
//    if(m_entry == entry-1 && entry!=0)
//      m_reader->Next();
//    else {
//      m_reader->SetEntry(entry);
//      m_entry = entry;
//    }
//  }
//}
//
//void TTreeReaderTools::remakeAllReaders() {
//  delete m_reader;
//  m_reader = new TTreeReader(m_tree);
//  m_readerIsClean = true;
//  std::vector<std::string> branchNames;
//  for(auto itr = m_ttreeValueUIntReaders.begin(); itr != m_ttreeValueUIntReaders.end(); ++itr)
//    branchNames.push_back(itr->first);
//  m_ttreeValueUIntReaders.clear();
//  for(auto itr = branchNames.begin(); itr != branchNames.end(); ++itr)
//    m_ttreeValueUIntReaders.insert(
//        std::pair<std::string,TTreeReaderValue<UInt_t> >(*itr,TTreeReaderValue<UInt_t>(*m_reader,itr->c_str())));
//}
