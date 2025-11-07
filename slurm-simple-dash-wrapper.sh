#!/bin/bash

# get standard distro name and major release version
. /etc/os-release
versionmajor=$( echo ${VERSION_ID} | cut -f1 -d. )
export OSVERSION=${ID}${versionmajor}
export OSrelease=${OSVERSION}
export ARCH
ARCH=$( /usr/bin/arch )

export CUBICLOCAL=/cubic/software/${OSVERSION}

# need to separate the CentOS 7 Spack from Alma 9 Spack
export SPACK_USER_CONFIG_PATH=~/.spack_${OSVERSION}
export SPACK_USER_CACHE_PATH=${SPACK_USER_CONFIG_PATH}/cache

# base local software needed for Spack
export PATH=${CUBICLOCAL}/bin:${PATH}
export MANPATH=${CUBICLOCAL}/share/man:${MANPATH}

# setup Spack
if [[ ! -d ${SPACK_USER_CONFIG_PATH} ]] ; then
    echo "INFO: setting up Spack for the first time. Please wait..."
    mkdir -p ${SPACK_USER_CONFIG_PATH}
fi
. ${CUBICLOCAL}/spack/share/spack/setup-env.sh

module use /cbica/share/modules
module load slurm/current

# this only works on infr4

logger -p cron.info "Updating Slurm load web page"

cd /admin/centos7/httpd/var/www/html/slurm-load

# this is python 3.11.14 ivybridge
spack load /45euzfe

source ~/Venvs/slurmdash/bin/activate
python3 /admin/bin/slurm-simple-dash.py

if [[ $(python3 /admin/bin/slurm-simple-dash.py) ]]
then
    exit 0
else
    logger -p cron.error "Error running slurm-simple-dash.py"
    exit 1
fi
