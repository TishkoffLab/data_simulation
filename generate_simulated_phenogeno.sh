#!/bin/bash

set -e

plink_path='/home/jake/tools/plink'
script_path='/local3/jake/admix_simul'
outname=""
reps=0
length=0
beta='normal'
file=""
mut_rate=0
recomb_rate=0
record_pheno='false'
ooafrica='false'
recomb_map=""
window=0

print_usage() {
  printf "Usage: ..."
}

while getopts 'apo:r:w:l:b:f:m:c:g:' flag; do
  case "${flag}" in
    a) ooafrica='True' ;;
    p) record_pheno='True' ;;
    o) outname="${OPTARG}" ;;
	  r) reps="${OPTARG}" ;;
	  w) window="${OPTARG}" ;;
	  l) length="${OPTARG}" ;;
	  b) beta="${OPTARG}" ;;
    f) file="${OPTARG}" ;;
    m) mut_rate="${OPTARG}" ;;
    c) recomb_rate="${OPTARG}" ;;
    g) recomb_map="${OPTARG}" ;;
    *) print_usage
       exit 1 ;;
  esac
done

argflags_string=''

if [[ $ooafrica = "True" ]]; then
    argflags_string+='-a '
fi
if [[ $record_pheno = "True" ]]; then
    argflags_string+='-p '
fi

echo "argflags used: ${argflags_string}"

if [[ $recomb_map ]]; then
  echo "starting script with recombination map"
  python ${script_path}/generate_simulated_phenogeno.py -r ${reps} -g ${recomb_map} -o ${script_path}/${outname} -f ${file} -m ${mut_rate} -b ${beta} -w ${window} ${argflags_string}
else
  python ${script_path}/generate_simulated_phenogeno.py -r ${reps} -c ${recomb_rate} -l ${length} -o ${script_path}/${outname} -f ${file} -m ${mut_rate} -b ${beta} -w ${window} ${argflags_string}
fi

rm ${script_path}/${outname}.epoch*.rep*.genotypes.temp

# ${plink_path} --vcf ${outname}.pheno.vcf --make-bed --out ${outname}.pheno

# ${plink_path} --vcf ${outname}.geno.vcf --make-bed --out ${outname}.geno

# awk 'NR < 7 {print $0}' ${outname}.vcf >> ${outname}.updated_alleles.vcf
# awk 'BEGIN{OFS="\t"}NR > 6 {$4="A"; $5="G"; print $0}'  ${outname}.vcf >> ${outname}.updated_alleles.vcf