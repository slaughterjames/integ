#!/bin/bash -
#===============================================================================
#integ v0.1 - Copyright 2018 James Slaughter,
#This file is part of integ v0.1.

#integ v0.1 is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#integ v0.1 is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with integ v0.1.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================
#------------------------------------------------------------------------------
#
# Install integ on top of an Ubuntu-based Linux distribution.
#
#------------------------------------------------------------------------------

__ScriptVersion="Integ-v0.1-1"
LOGFILE="/var/log/integ-install.log"
DIR="/opt/integ/"
SCRIPT_REPO_DIR="/home/scalp/integ/script_repo/"
DIFF_DIR="/home/scalp/integ/diff/"
OUTPUT_DIR="/home/scalp/integ/output/"

echoerror() {
    printf "${RC} * ERROR${EC}: $@\n" 1>&2;
}

echoinfo() {
    printf "${GC} * INFO${EC}: %s\n" "$@";
}

echowarn() {
    printf "${YC} * WARN${EC}: %s\n" "$@";
}

__apt_get_install_noinput() {
    sudo apt-get install -y -o DPkg::Options::=--force-confold $@; return $?
}

__apt_get_upgrade_noinput() {
    sudo apt-get upgrade -y -o DPkg::Options::=--force-confold $@; return $?
}

__pip_install_noinput() {
    pip install --upgrade $@; return $?
}


usage() {
    echo "usage"
    exit 1
}


install_ubuntu_deps() {

  echoinfo "Updating the base APT repository package list... "
  apt-get update >> $LOGFILE 2>&1

  echoinfo "Upgrading all APT packages to latest versions..."
  __apt_get_upgrade_noinput >> $LOGFILE 2>&1

  ldconfig
  return 0
}

install_ubuntu_packages() {
    #Ubuntu packages that need to be installed
    packages="python
    python-dev
    automake
    python-pip
    python-setuptools
    python-magic"

    if [ "$@" = "dev" ]; then
        packages="$packages"
    elif [ "$@" = "stable" ]; then
        packages="$packages"
    fi

    for PACKAGE in $packages; do
        echoinfo "Installing APT Package: $PACKAGE"
        __apt_get_install_noinput $PACKAGE >> $LOGFILE 2>&1
        ERROR=$?
        if [ $ERROR -ne 0 ]; then
            echoerror "Install Failure: $PACKAGE (Error Code: $ERROR)"
        fi
    done    
    
    return 0
}


install_pip_packages() {
  #Python Libraries that need to be installed
  pip_packages="termcolor
  subprocess
  datetime
  time
  hashlib
  urllib2"

  if [ "$@" = "dev" ]; then
    pip_packages="$pip_packages"
  elif [ "$@" = "stable" ]; then
    pip_packages="$pip_packages"
  fi

  for PACKAGE in $pip_packages; do
    CURRENT_ERROR=0
    echoinfo "Installing Python Package: $PACKAGE"
    __pip_install_noinput $PACKAGE >> $LOGFILE 2>&1 || (let ERROR=ERROR+1 && let CURRENT_ERROR=1)
    if [ $CURRENT_ERROR -eq 1 ]; then
      echoerror "Python Package Install Failure: $PACKAGE"
    fi
  done

  if [ $ERROR -ne 0 ]; then
    return 1
  fi

  return 0
}

install_integ_package() {
  #Pull integ from GitHub, unzip and install it
  echoinfo "Installing integ"
  wget -q "https://github.com/slaughterjames/integ/archive/master.zip" --output-document "/tmp/master.zip"
  unzip -q "/tmp/master.zip" -d "/tmp/"
  chmod a+w "/tmp/integ-master/" 
  mv "/tmp/integ-master"/* "$DIR" 
  rm -R "/tmp/integ-master/"

  if [ $ERROR -ne 0 ]; then
    return 1
  fi

  return 0
}

configure_integ() {
  #Creates the necessary directories for integ in /opt/integ
  echoinfo "Creating directories"

  mkdir -p $DIR >> $LOGFILE 2>&1
  chmod a+w $DIR >> $LOGFILE 2>&1

  mkdir -p $SCRIPT_REPO_DIR >> $LOGFILE 2>&1
  chmod a+w $SCRIPT_REPO_DIR >> $LOGFILE 2>&1

  mkdir -p $DIFF_DIR >> $LOGFILE 2>&1
  chmod a+w $DIFF_DIR >> $LOGFILE 2>&1

  mkdir -p $OUTPUT_DIR >> $LOGFILE 2>&1
  chmod a+w $OUTPUT_DIR >> $LOGFILE 2>&1

  echo "<Remove this line - Enter list of targets in the following format:>" > $DIR/targets.txt
  echo "<Remove this line - someaddress.com;https://locationoffiletoverify.com/file.js;MD5Hash>" > $DIR/targets.txt
  chmod a+w $DIR/keywords.txt $LOGFILE 2>&1

  return 0
}

complete_message() {
    #Message that displays on completion of the process
    echoinfo "---------------------------------------------------------------"
    echoinfo "integ Installation Complete!"
    echoinfo "Reboot for the settings to take full effect (\"sudo reboot\")."
    echoinfo "---------------------------------------------------------------"

    return 0
}

#Grab the details about the system
OS=$(lsb_release -si)
ARCH=$(uname -m | sed 's/x86_//;s/i[3-6]86/32/')
VER=$(lsb_release -sr)

#Print out details about the system
echo "Installing integ on: $OS"
echo "Architecture is: $ARCH bit"
echo "Version is: $VER"
echo ""

#Bail if installation isn't
if [ `whoami` != "root" ]; then
    echoerror "The integ installation script must run as root."
    echoerror "Usage: sudo ./get-integ.sh"
    exit 3
fi

if [ "$SUDO_USER" = "" ]; then
    echoerror "The SUDO_USER variable doesn't seem to be set"
    exit 4
fi

while getopts ":hvnicu" opt
do
case "${opt}" in
    h ) echo "Usage:"
        echo ""
        echo "sudo ./get-integ.sh [options]"
        echo ""
        exit 0
        ;;
    v ) echo "$0 -- Version $__ScriptVersion"; exit 0 ;;
    \?) echo ""
        echoerror "Option does not exist: $OPTARG"
        usage
        exit 1
        ;;
esac
done

shift $(($OPTIND-1))

if [ "$#" -eq 0 ]; then
    ITYPE="stable"
else
    __check_unparsed_options "$*"
    ITYPE=$1
    shift
fi

echo "---------------------------------------------------------------" >> $LOGFILE
echo "Running integ installer version $__ScriptVersion on `date`" >> $LOGFILE
echo "---------------------------------------------------------------" >> $LOGFILE

echoinfo "Installing integ. Details logged to $LOGFILE."

#Function calls
install_ubuntu_deps $ITYPE
install_ubuntu_packages $ITYPE
install_pip_packages $ITYPE
configure_integ
install_integ_package $ITYPE
complete_message
