import sys
from pandas import *
import numpy as np
import matplotlib
from matplotlib import pyplot
import itertools as it
import matplotlib.backends.backend_pdf
import math
from matplotlib.pyplot import cm
from dateutil import parser
import scipy
from scipy.stats import mstats
import re
import matplotlib.dates as mdates
import datetime
import msprime
import random
from scipy.stats import norm
from argparse import ArgumentParser
# import pdb

parser = ArgumentParser()
parser.add_argument("-r", "--repetitions", dest="L",
                    help="number of simulated genotypes to run, corrisponding to the number of causal variants")
parser.add_argument("-s", "--samplesize", dest="samp_size",
                    help="number of genotypes that will be simulated for each run")
parser.add_argument("-w", "--window", dest="window",
                    help="window size to use as a spacer between the SNPs generated by the simulation")
parser.add_argument("-n", "--num_inds", dest="num_individuals",
                    help="number of individuals that will be used to create the genotypes and phenotypes")
parser.add_argument("-l", "--sequence_length", dest="seq_len",
                    help="length of the sequence that will be simulated; the only variant that will be used from this is the causal one")
parser.add_argument("-b", "--beta", dest="beta_type",
                    help="string keyword that corrisponds to how we want to assign the beta value for the phenotype (ie constant means the beta value will be the same for all causal variants)")
parser.add_argument("-o", "--out", dest="out_name",
                    help="name of the file to be saved, the files <out_name>.phenodist.png, <out_name>.pheno.vcf, <out_name>.geno.vcf and <out_name>.phenotypes  will be created")



def assign_genotype_index(samp_size,num_inds):
    ind_haps_dict = {}
    haps_used = []
    x = num_inds
#     x = int(samp_size/2)
    for n in range(x):
        curr_haps = []
        while (len(curr_haps) != 2):
            temp_seq_num = random.randint(0,(samp_size-1))
            if(temp_seq_num not in haps_used and temp_seq_num not in curr_haps):
                curr_haps.append(temp_seq_num)
                haps_used.append(temp_seq_num)
        ind_haps_dict[n] = curr_haps
    return ind_haps_dict

def save_pheno_vcf(samp_size,seq_len,num_individuals,outname):
    tree_sequence = msprime.simulate(sample_size=samp_size, Ne=1e4, length=seq_len, recombination_rate=2e-8,mutation_rate=2e-8) 
    new_ids = []
    for i in range(num_individuals):
        new_ids.append(''.join(['ID',str(i)]))
        
    with open('{0}.vcf'.format(outname), "w") as vcf_file:
        tree_sequence.write_vcf(vcf_file, ploidy=2,individual_names=new_ids)

def estimate_pheno(genotypes,beta):
#     causal_pos = 0 #int(len(genotype[0])/2)
    full_phenovals = []
    for g in genotypes:
        try:
            c_al1 = float(g[0])
            c_al2 = float(g[1])
            full_phenovals.append((c_al1 + c_al2)*beta)
        except:
            print("Error!",g)
    return sum(full_phenovals)

def plot_phenodist(pheno_dict, num_inds,outname):
    pheno_df = DataFrame(pheno_dict.values(),index=pheno_dict.keys(),columns=['Pheno_value'])

    mu, std = norm.fit(pheno_df['Pheno_value'])

    pyplot.hist(pheno_df['Pheno_value'])

    xmin, xmax = pyplot.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = (norm.pdf(x, mu, std))*(num_inds*2)
    pyplot.plot(x, p, 'k', linewidth=2)
    title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
    pyplot.title(title)
    pyplot.ylabel('Number of Individuals in Bin')
    pyplot.xlabel('Phenotype Value')
    pyplot.savefig('{0}.phenodist.png'.format(outname))

def generate_betas(num_inds,dist_type='normal'):
    if(dist_type == 'normal'):
        dist = np.random.normal(0,0.1,num_inds)
    return dist

def write_phenofile(outname,pheno_dict):
    pheno_file = open('{0}.phenotypes'.format(outname),'w')
    new_ids = []
    for i in range(len(pheno_dict.items())):
        new_ids.append(''.join(['ID',str(i)]))
    for ind,p in pheno_dict.items():
        pheno_file.write('{0}\t{1}\n'.format(new_ids[ind],p))
    pheno_file.close()

def run_pheno_simulation(samp_size,seq_len,L,num_individuals,outname,beta,causal_var_id=1):
    genotype_index_byinds = assign_genotype_index(samp_size,num_individuals) #randomly take the <samp_size> number of genomes simulated, and randomly assign to each individual 2 of them
    causalgenotypes_byind = {x:[] for x in range(num_individuals)}
    causalgenotypes_byrep = {x:[] for x in range(L)}  #Each repetition, add the genotype from that rep (as a tuple) to this dictionary. Then we can just iterate through the list of values to generate the final phenotype
    fullgenotypes_byrep = {x:[] for x in range(L)}
    causalpositions_byrep = {x:0 for x in range(L)}
    rep = 0
    while (rep < L):
        tree_sequence = msprime.simulate(sample_size=samp_size, Ne=1e4, length=seq_len, recombination_rate=2e-8,mutation_rate=2e-8) 
        curr_causal_var = []
        curr_causal_pos = ''
        curr_full_vars_posgeno_dict = {}
        for variant in tree_sequence.variants():
            curr_full_vars_posgeno_dict[round(variant.site.position)] = list(variant.genotypes)
            if(variant.site.id == causal_var_id):
                curr_causal_var = list(variant.genotypes)
                curr_causal_pos = round(variant.site.position)
        if(len(curr_causal_var) != samp_size):
            print('no causal variants in rep {0}, redoing'.format(rep))
            rep -= 1
            continue

        causalpositions_byrep[rep] = curr_causal_pos
        curr_rep_genotypes = []
        for indiv,index in genotype_index_byinds.items():
            try:
                causalgenotypes_byind[indiv].append((curr_causal_var[index[0]],curr_causal_var[index[1]]))
                curr_rep_genotypes.append((curr_causal_var[index[0]],curr_causal_var[index[1]]))
            except:
                print(indiv,index)
        causalgenotypes_byrep[rep] = [curr_causal_pos,curr_rep_genotypes]

        curr_rep_fullgenos = {}
        for pos,geno in curr_full_vars_posgeno_dict.items():
            temp_fullgeno = []
            for indiv,index in genotype_index_byinds.items():
                try:
                    temp_fullgeno.append((geno[index[0]],geno[index[1]]))
                except:
                    print(indiv,index)
            curr_rep_fullgenos[pos] = temp_fullgeno
        fullgenotypes_byrep[rep] = curr_rep_fullgenos
        rep += 1

    phenotypes_byinds = {x:0 for x in range(num_individuals)}
    beta_list = generate_betas(num_inds=num_individuals,dist_type=beta)
    for i in range(num_individuals):
        curr_beta = beta_list[i]
        phenotypes_byinds[i] = estimate_pheno(causalgenotypes_byind[i],curr_beta)

    plot_phenodist(phenotypes_byinds,num_individuals,outname)
    write_phenofile(outname,phenotypes_byinds)

    return causalpositions_byrep,fullgenotypes_byrep

def run_geno_simulation(samp_size,seq_len,L,num_individuals,causal_var_id=1):
    genotype_index_byinds = assign_genotype_index(samp_size,num_individuals) #randomly take the <samp_size> number of genomes simulated, and randomly assign to each individual 2 of them
    causalgenotypes_byrep = {x:[] for x in range(L)} #Each repetition, add the genotype from that rep (as a tuple) to this dictionary. Then we can just iterate through the list of values to generate the final phenotype
    fullgenotypes_byrep = {x:[] for x in range(L)}
    causalpositions_byrep = {x:0 for x in range(L)}
    rep = 0
    while (rep < L):
        tree_sequence = msprime.simulate(sample_size=samp_size, Ne=1e4, length=seq_len, recombination_rate=2e-8,mutation_rate=2e-8) 
        num_vars = 0
        for variant in tree_sequence.variants():
            num_vars += 1
        if(num_vars == 0):
            print('no variants in rep {0}, redoing'.format(rep))
            rep = rep-1
            continue
        causal_var_id = random.randint(0,(num_vars-1))
        curr_causal_var = []
        curr_causal_pos = 0
        curr_full_vars_posgeno_dict = {}
        for variant in tree_sequence.variants():
            curr_full_vars_posgeno_dict[round(variant.site.position)] = list(variant.genotypes)
            if(variant.site.id == causal_var_id):
                curr_causal_var = list(variant.genotypes)
                curr_causal_pos = round(variant.site.position)

        if(len(curr_causal_var) != samp_size):
            print('no causal variants in rep {0}, redoing'.format(rep))
            rep -= 1
            continue
        causalpositions_byrep[rep] = curr_causal_pos
        curr_rep_genotypes = []
        for indiv,index in genotype_index_byinds.items():
            try:
                curr_rep_genotypes.append((curr_causal_var[index[0]],curr_causal_var[index[1]]))
            except:
                print(indiv,index)
        causalgenotypes_byrep[rep] = [curr_causal_pos,curr_rep_genotypes]

        curr_rep_fullgenos = {}
        for pos,geno in curr_full_vars_posgeno_dict.items():
            temp_fullgeno = []
            for indiv,index in genotype_index_byinds.items():
                try:
                    temp_fullgeno.append((geno[index[0]],geno[index[1]]))
                except:
                    print(indiv,index)
            curr_rep_fullgenos[pos] = temp_fullgeno
        fullgenotypes_byrep[rep] = curr_rep_fullgenos

        rep += 1
    return causalpositions_byrep,fullgenotypes_byrep


def write_genovcf(full_geno_dict,causal_pos_dict,outname,num_inds,seq_len,window_spacer=1000):
    full_len = len(full_geno_dict)*(window_spacer+seq_len)
    header_string = '##fileformat=VCFv4.2 \n##source=tskit 0.2.2 \n##FILTER=<ID=PASS,Description="All filters passed"> \n##INFO=<ID=CS,Number=0,Type=Flag,Description="SNP Causal to Phenotype"> \n##contig=<ID=1,length={0}>\n##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype"> \n'.format(full_len)
    vcf_file = open('{0}.vcf'.format(outname),'w')
    vcf_file.write(header_string)
    vcf_file.write('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t')
    new_ids = []
    for i in range(num_inds):
        curr_nid = ''.join(['ID',str(i)])
        new_ids.append(curr_nid)
        vcf_file.write('{0}\t'.format(curr_nid))
    vcf_file.write('\n')
    # print('{0} genotypes to be written'.format(len(geno_dict)))
    for rep,geno_dict in full_geno_dict.items():
        is_rep_causalsnp = False
        for pos,genos in geno_dict.items():
            try:
                curr_pos = (int(rep)*(window_spacer+seq_len))+pos
                if(pos == causal_pos_dict[rep]):
                    is_rep_causalsnp = True
                    vcf_file.write('1\t{0}\t.\tA\tG\t.\tPASS\tCS\tGT\t'.format(curr_pos))
                else:
                    vcf_file.write('1\t{0}\t.\tA\tG\t.\tPASS\t.\tGT\t'.format(curr_pos))
                for g in genos:
                    vcf_file.write('{0}|{1}\t'.format(g[0],g[1]))
                vcf_file.write('\n')
            except:
                print(rep,genos)
    # for rep,genos in geno_dict.items():
    #     try:
    #         curr_pos = (int(rep)*seq_len)+genos[0]
    #         vcf_file.write('1\t{0}\t.\tA\tG\t.\tPASS\t.\tGT\t'.format(curr_pos))
    #         for g in genos[1]:
    #             vcf_file.write('{0}|{1}\t'.format(g[0],g[1]))
    #         vcf_file.write('\n')
    #     except:
    #         print(rep,genos)
        
    

if __name__ == "__main__":
    args = parser.parse_args()
    if(args.beta_type is None):
        beta = "normal"
    else:
        beta = args.beta_type
    cpos_pheno_byinds,pgenos_byinds = run_pheno_simulation(int(args.samp_size),int(args.seq_len),int(args.L),int(args.num_individuals),args.out_name,beta)
    write_genovcf(pgenos_byinds,cpos_pheno_byinds,'{0}.pheno'.format(args.out_name),int(args.num_individuals),int(args.seq_len),int(args.window))

    cpos_geno_byind,genos_byinds = run_geno_simulation(int(args.samp_size),int(args.seq_len),int(args.L),int(args.num_individuals))
    write_genovcf(genos_byinds,cpos_geno_byind,'{0}.geno'.format(args.out_name),int(args.num_individuals),int(args.seq_len),int(args.window))














