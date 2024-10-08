cmake_minimum_required(VERSION 3.14.0)

set(MY_PROJECT_VERSION 0.9.0 CACHE STRING "project version number")

project(lqAnalysis VERSION ${MY_PROJECT_VERSION})

if(PROJECT_SOURCE_DIR STREQUAL PROJECT_BINARY_DIR)
  message(
    FATAL_ERROR
      "In-source builds not allowed. Please make a new directory (called a build directory) and run CMake from there."
  )
endif()

### compile_commands.json DB
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# for warnings
#message(STATUS "Enabling more warnings")
#
### From cpp-best-practices
### https://github.com/cpp-best-practices/cpp_starter_project/blob/master/cmake/CompilerWarnings.cmake
#option(WARNINGS_AS_ERRORS "Treat compiler warnings as errors" OFF)
#
#set(COMMON_WARNINGS
#    -Wall
#    #-Wextra                  # reasonable and standard
#    #-Wshadow                 # warn the user if a variable declaration shadows one from a
#                             # parent context
#    -Wcast-align             # warn for potential performance problem casts
#    #-Wunused                 # warn on anything being unused
#    -Wpedantic               # warn if non-standard C++ is used
#    -Wconversion             # warn on type conversions that may lose data
#    -Wsign-conversion        # warn on sign conversions
#    -Wnull-dereference       # warn if a null dereference is detected
#    #-Wdouble-promotion       # warn if float is implicit promoted to double
#    -Wformat=2               # warn on security issues around functions that format output
#                             # (ie printf)
#    -Wimplicit-fallthrough   # warn on statements that
#)
#set(GCC_WARNINGS
#    ${COMMON_WARNINGS}
#    -Wmisleading-indentation # warn if indentation implies blocks where blocks do not exist
#    -Wduplicated-cond        # warn if if / else chain has duplicated conditions
#    -Wduplicated-branches    # warn if if / else branches have duplicated code
#    -Wlogical-op             # warn about logical operations being used where bitwise were probably wanted
#    # -Wuseless-cast           # warn if you perform a cast to the same type
#)
#
#set(GCC_CXX_WARNINGS
#    ${COMMON_CXX_WARNINGS}
#    # -Wuseless-cast           # warn if you perform a cast to the same type
#)
#
#if(CMAKE_CXX_COMPILER_ID MATCHES ".*Clang")
#    set(PROJECT_WARNINGS ${CLANG_WARNINGS})
#    set(PROJECT_CXX_WARNINGS ${CLANG_CXX_WARNINGS})
#elseif(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
#    set(PROJECT_WARNINGS ${GCC_WARNINGS})
#    set(PROJECT_CXX_WARNINGS ${GCC_CXX_WARNINGS})
#else()
#    message(AUTHOR_WARNING "No compiler warnings set for '${CMAKE_CXX_COMPILER_ID}' compiler.")
#endif()
#
#message(AUTHOR_WARNING "Setting compiler warnings for '${CMAKE_C_COMPILER_ID}' to ${PROJECT_WARNINGS}.")
#message(AUTHOR_WARNING "Setting additional compiler warnings for '${CMAKE_CXX_COMPILER_ID}' to ${PROJECT_CXX_WARNINGS}.")
#
#add_compile_options(${PROJECT_WARNINGS})
#
#foreach(CXX_WARNING ${PROJECT_CXX_WARNINGS})
#  add_compile_options($<$<COMPILE_LANGUAGE:CXX>:${CXX_WARNING}>)
#endforeach()

# LCG sets this to 20 for EL9, and it defaults to 17 for EL7 anyway, so no need to explicitly set the C++ standard.
# but the root dictionary generation goes back to C++17 for some reason...
if(CMAKE_SYSTEM_VERSION MATCHES "el9")
  message("
  Found el9 host system, so building for c++20.
")
  set(CMAKE_CXX_STANDARD 20)
#elseif(CMAKE_SYSTEM_VERSION MATCHES "el7")
#  message("
#  Found el7 host system, so building for c++17.
#")
#  set(CMAKE_CXX_STANDARD 17)
endif()

#add_compile_options(-fno-omit-frame-pointer -fsanitize=address,undefined,leak)
#add_link_options(-fsanitize=address,undefined,leak)
add_compile_options(-DSAVE_ALL_HISTOGRAMS)
add_compile_options(-DUSE_FULL_NTUPLE)
##add_compile_options(-DUSE_EXAMPLE)
add_compile_options(-O2)
#add_compile_options(-fsanitize=address,undefined,leak)
#add_link_options(-fsanitize=address,undefined,leak)
#add_compile_options(-fno-omit-frame-pointer)
#add_compile_options(-fsanitize-recover=all)
#add_compile_options(--param=max-vartrack-size=50000000)
#add_compile_options(-g)
#add_compile_options(-pg)
#add_compile_options(${USER_CXXFLAGS})
#set_source_files_properties(JMEUncertainties.C PROPERTIES COMPILE_FLAGS -g)

find_package(Boost REQUIRED iostreams regex)
find_package(ROOT REQUIRED Hist Tree TreePlayer Physics TMVA)
find_package(correctionlib REQUIRED)
find_package(Threads)
find_package(ZLIB)

if(REDUCED_SKIM)
  include(FetchContent)
  FetchContent_Declare(CMSJMECalculators
    GIT_REPOSITORY https://gitlab.cern.ch/cp3-cms/CMSJMECalculators.git
    GIT_TAG        9aa89b97524472cc94262ec9566873f3b42517fa  # head as of July 10, 2024
    )
  FetchContent_MakeAvailable(CMSJMECalculators)
else()
endif()

#add_library(mylib
#  src/mylib.cpp
#  )
#
#set_target_properties(mylib PROPERTIES CXX_STANDARD 17)

# target_compile_options(lsplib
#   PUBLIC "$<$<COMPILE_LANG_AND_ID:CXX,MSVC>:/permissive->")

# Link dependencies
#target_link_libraries(lsplib)

#target_include_directories(mylib
#  PUBLIC
#    $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/include>
#    $<INSTALL_INTERFACE:include/${PROJECT_NAME}-${PROJECT_VERSION}>
#)
include_directories(${CMAKE_SOURCE_DIR}/include)

if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/src/analysisClassQCD.C AND NOT IS_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src/analysisClassQCD.C AND NOT REDUCED_SKIM)
  set(HAS_QCD TRUE)
      message("
      Found analysisClassQCD.C, so building mainQCD binary using it.
")
else()
  set(HAS_QCD FALSE)
endif()

if(REDUCED_SKIM)
  add_executable(main
    src/TTreeReaderTools.C
    src/main.C
    src/analysisClass.C
    src/baseClass.C
    src/Collection.C
    src/CorrectionHandler.C
    src/Electron.C
    src/ElectronIDs.C
    src/GenJet.C
    src/GenJetIDs.C
    src/GenParticle.C
    src/GenParticleIDs.C
    src/LHEParticle.C
    src/LHEParticleIDs.C
    src/HLTriggerObject.C
    src/HLTriggerObjectCollectionHelper.C
    src/LooseElectron.C
    src/HistoReader.C
    src/Muon.C
    src/MuonIDs.C
    src/Object.C
    src/PFJet.C
    src/PFJetIDs.C
    src/QCDFakeRate.C
    src/eventListHelper.C
    src/jsonParser.C
    src/JMEUncertainties.C
    src/EWKCorrections.C
    )
else()
  add_executable(main
    src/TTreeReaderTools.C
    src/main.C
    src/analysisClass.C
    src/baseClass.C
    src/HistoReader.C
    src/jsonParser.C
    src/QCDFakeRate.C
    )
  if(HAS_QCD)
    add_executable(mainQCD
      src/TTreeReaderTools.C
      src/main.C
      src/analysisClassQCD.C
      src/baseClass.C
      src/HistoReader.C
      src/jsonParser.C
      src/QCDFakeRate.C
      )
  endif()
endif()

root_generate_dictionary(myapp_dict ${CMAKE_SOURCE_DIR}/include/baseClass.h LINKDEF ${CMAKE_SOURCE_DIR}/include/LinkDef.h)
add_library(myapp_dict_lib SHARED myapp_dict)

if(REDUCED_SKIM)
target_link_libraries(main
  PUBLIC
  Boost::iostreams
  Boost::regex
  ROOT::Hist
  ROOT::Tree
  ROOT::TreePlayer
  ROOT::Physics
  ROOT::TMVA
  correctionlib
  CMSJMECalculators
  myapp_dict_lib
)
else()
  target_link_libraries(main
    PUBLIC
    Boost::iostreams
    Boost::regex
    ROOT::Hist
    ROOT::Tree
    ROOT::TreePlayer
    ROOT::Physics
    ROOT::TMVA
    myapp_dict_lib
    )
  if(HAS_QCD)
    target_link_libraries(mainQCD
      PUBLIC
      Boost::iostreams
      Boost::regex
      ROOT::Hist
      ROOT::Tree
      ROOT::TreePlayer
      ROOT::Physics
      ROOT::TMVA
      myapp_dict_lib
      )
  endif()
endif()
