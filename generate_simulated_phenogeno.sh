#!/bin/bash

set -e

outname='' #'test_treeoutput.recoded.vcf'
vcf='' #'test_treeoutput.vcf'
reps=0
samp_size=0
num_inds=0
length=0
beta='normal'
plink_path='/home/jake/tools/plink'

print_usage() {
  printf "Usage: ..."
}

while getopts 'v:o:r:s:n:l:b:' flag; do
  case "${flag}" in
    v) vcf="${OPTARG}" ;;
    o) outname="${OPTARG}" ;;
	r) reps="${OPTARG}" ;;
	s) samp_size="${OPTARG}" ;;
	n) num_inds="${OPTARG}" ;;
	l) length="${OPTARG}" ;;
	b) beta="${OPTARG}" ;;
    *) print_usage
       exit 1 ;;
  esac
done



python /local3/jake/admix_simul/generate_simulated_phenogeno.py -r ${reps} -s ${samp_size} -n ${num_inds} -l ${length} -o ${outname}

${plink_path} --vcf ${outname}.pheno.vcf --make-bed --out ${outname}.pheno

${plink_path} --vcf ${outname}.geno.vcf --make-bed --out ${outname}.geno

# awk 'NR < 7 {print $0}' ${outname}.vcf >> ${outname}.updated_alleles.vcf
# awk 'BEGIN{OFS="\t"}NR > 6 {$4="A"; $5="G"; print $0}'  ${outname}.vcf >> ${outname}.updated_alleles.vcf