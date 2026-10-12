#!/usr/bin/env bash
set -e

# parse yml file
caseid=$(cat recipe.yml |grep 'caseid' |cut -d: -f2 |sed 's/ //g')
year_start=$(cat recipe.yml |grep 'year_start' |cut -d: -f2 |sed 's/ //g')
year_end=$(cat recipe.yml |grep 'year_end' |cut -d: -f2 |sed 's/ //g')
www_root=$(cat recipe.yml |grep 'www_root' |cut -d: -f2 |sed 's/ //g')

project=$(echo $www_root |grep -oP 'NS\d+K' |tr '[:upper:]' '[:lower:]')
if echo $www_root | grep 'datalake' ; then
  dataservice='datalake'
else
  dataservice='datapeak'
fi

# set permission
umask 002

# activate conda
source /cluster/software/Miniforge3/24.1.2-0/etc/profile.d/conda.sh
conda activate /nird/datalake/NS16000B/blomster-env

# generate TOC and inject parameters to notebooks
python configure.py
python compute_climo.py

# build the book
jupyter-book clean .
jupyter-book build -qq -n .

# Backup configs 
cp _config.yml _toc.yml recipe.yml settings.yml _build/jupyter_execute/

# Publish
chmod -R g+w _build/html
if test -w ${www_root} ; then
  www_sub=${caseid}/yrs${year_start}to${year_end}-obs
  mkdir -p ${www_root}/${www_sub}
  rsync -au --delete --remove-source-files _build/html/ ${www_root}/${www_sub}
  echo 'Gedneratd diagnostics is at:'
  echo "https://${project}.web.sigma2.no/${dataservice}/diagnostics/blomster/${www_sub}"
else
  echo "You do not have write permission to ${www_root}."
  echo "Generated diagnostics is under:"
  echo "$pwd/_build/html"
fi

# cleanup
#for nbdir in $(cat recipe.yml|grep '\- file: ' |cut -d: -f2 |awk -F/ '{print $(NF-1)}' |uniq)
#do
  #echo $nbdir
  #rm -rf $nbdir
#done
