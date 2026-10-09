#!/usr/bin/env bash
set -e

# get version from yml file
source_id=$(cat experiment.yml |grep 'source_id' |cut -d: -f2 |sed 's/ //g')
experiment_id=$(cat experiment.yml |grep 'experiment_id' |cut -d: -f2 |sed 's/ //g')
variant_label=$(cat experiment.yml |grep 'variant_label' |cut -d: -f2 |sed 's/ //g')
version=$(cat experiment.yml |grep 'version' |cut -d: -f2 |sed 's/ //g')

# set default value
www_root=/nird/datalake/NS9560K/www/diagnostics/blomster
exp_root=${www_root}

# check group id
if id |grep -q 'ipcc' ; then
  gid='ipcc'
elif id |grep 'ns9560k' ; then
  gid='ns9560k'
else
  gid='null'
fi

# set permission
umask 002

# activate conda
source /cluster/software/Miniforge3/24.1.2-0/etc/profile.d/conda.sh
conda activate /nird/datalake/NS16000B/blomster-env

# generate TOC and inject parameters to notebooks
python configure.py

# build the book
jupyter-book clean .
jupyter-book build -qq -n .

# Publish
# backup configs 
mkdir _build/config
cp _config.yml _toc.yml recipe.yml _build/config
# copy and sync
chmod -R g+w _build/html
if [ $gid == 'null' ]; then
  echo "Generated diagnostics is under:"
  echo "$pwd/_build/html"
  echo "It is not copied to ${www_root} since you do not blong to the 'ipcc' group or 'ns9560k' group."
else
  mkdir -p ${www_root}/${source_id}/${experiment_id}/${version}
  rsync -au --chown=$USER:$gid --delete --remove-source-files _build/html/ ${www_root}/${source_id}/${experiment_id}/${version}/
  echo 'Gedneratd diagnostics is at:'
  echo "https://ns9560k.web.sigma2.no/datalake/diagnostics/cmip7validate/${source_id}/${experiment_id}/${version}"
fi

# cleanup
for nbdir in $(cat recipe.yml|grep '\- file: ' |cut -d: -f2 |awk -F/ '{print $(NF-1)}' |uniq)
do
  echo $nbdir
  #rm -rf $nbdir
done
