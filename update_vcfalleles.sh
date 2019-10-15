#!/bin/bash

set -e

outname='test_treeoutput.recoded.vcf'
vcf='test_treeoutput.vcf'

print_usage() {
  printf "Usage: ..."
}

while getopts 'v:o:' flag; do
  case "${flag}" in
    v) vcf="${OPTARG}" ;;
    o) outname="${OPTARG}" ;;
    *) print_usage
       exit 1 ;;
  esac
done

# while read line; do
#   # curr_line=(`echo "${line}" | cut -d$'\t' -f 3,4`)
#   curr_line=(`echo ${line} | cut -d$'\t' -f5-`)
#   echo $curr_line
#   # echo ${line} | cut -d ' ' -f 5-6
# done <"test_treeoutput.vcf"
# # done <"${vcf}"
# awk 'NR < 7 {print $0}' ${vcf} >> ${outname}
# awk -v i=`echo ${0} | cut -d$'\t' -f5-` 'BEGIN{OFS="\t"}NR > 6 {print $1,$2,$3,"A","G",$i}' ${vcf} >> ${outname}

awk 'NR < 7 {print $0}' ${vcf} >> ${outname}
awk 'BEGIN{OFS="\t"}NR > 6 {$4="A"; $5="G"; print $0}'  ${vcf} >> ${outname}