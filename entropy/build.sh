#!/bin/bash
# *****************************************************************************
# \file build.sh
# \brief Build EntropyAssessment tool
# \project skzi [security requirements for cryptographic modules]
# \created 2023.01.25
# \version 2023.01.25
# \ref https://github.com/usnistgov/SP800-90B_EntropyAssessment
# *****************************************************************************

root=`pwd`
build_root=$root/.build
ea_name=SP800-90B_EntropyAssessment
ea_root=$root/.build/$ea_name
ea_host=https://github.com/usnistgov

clean(){
  rm -rf $build_root
}

install_build_prereq(){
  apt-get update
  apt-get -y install sudo
  sudo apt-get update
  sudo apt-get -y install git gcc \
    libbz2-dev libdivsufsort-dev libjsoncpp-dev libssl-dev libmpfr-dev
}

build_ea(){
  mkdir -p $build_root && cd $build_root &&\
  git clone --depth 1 $ea_host/$ea_name &&\
  cd $ea_root/cpp && make -j8 &&\
  cd selftest &&  ./selftest && cd .. &&\
  mv ea_conditioning $build_root &&\
  mv ea_iid $build_root &&\
  mv ea_non_iid $build_root &&\
  mv ea_restart $build_root &&\
  mv ea_transpose $build_root
}

clean && install_build_prereq && build_ea
