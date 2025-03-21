#ifndef GENPARTICLE_H
#define GENPARTICLE_H

#include "Object.h"
#include "IDTypes.h"
#include "Collection.h"

#include <TLeaf.h>

class GenParticle : public Object { 

 public:

  GenParticle();
  GenParticle(Collection& c, unsigned short i, short j = 0);
  
  // Kinematic variables

  float Mass();

  // IDs 

  bool PassUserID ( ID id, bool verbose = false); 
  
  // ID variables  

  int PdgId       ();
  int MotherIndex ();
  int Status      ();
  int NumDaughters();
  int MotherLQIndex();

  int StatusFlags ();
  
  bool IsHardProcess();
  bool IsFromHardProcess();
  bool IsFromHardProcessFinalState();
  bool IsLastCopy();

 private:
  
  int m_MotherLQIndex = -1;

  bool PassUserID_FromLQ              (bool verbose);
  bool PassUserID_FromDY              (bool verbose);
  bool PassUserID_FromW               (bool verbose);
  bool PassUserID_GenEleFromLQ        (bool verbose);
  bool PassUserID_GenMuonFromLQ       (bool verbose);
  bool PassUserID_GenTauFromLQ        (bool verbose);
  bool PassUserID_MuonFiducial        (bool verbose);
  bool PassUserID_ECALFiducial        (bool verbose);
  bool PassUserID_GenEleHardScatter   (bool verbose);
  bool PassUserID_GenNuHardScatter    (bool verbose);
  bool PassUserID_GenMuHardScatter    (bool verbose);
  bool PassUserID_GenQuarkHardScatter (bool verbose);
  bool PassUserID_GenQuarkHardProcess (bool verbose);

  //bool PassUserID_GenWHardScatter     (bool verbose);
  bool PassUserID_GenZFromHardProcessLastCopy(bool verbose);
  bool PassUserID_GenNuFromW          (bool verbose);
  bool PassUserID_GenEleFromW         (bool verbose);
  bool PassUserID_GenEleFromDY        (bool verbose);

  bool PassUserID_GenLQ               (bool verbose);
  bool PassUserID_GenTop              (bool verbose);
  bool PassUserID_Status62            (bool verbose);
  bool PassUserID_GenEleHardProcessFinalState            (bool verbose);
  bool PassUserID_GenIsLastCopy       (bool verbose);

};

std::ostream& operator<< (std::ostream& stream, GenParticle& object);

#endif
