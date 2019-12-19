#! /home/dharris/miniconda3/bin/python
######### Simulates 4 human populations and 1 Archaic popultion. Introgression occurs from AFR1 to Altai and Altai to AFR4.
######### 2 Command line arguments: 1) Output file for tskit trees, and 2) Output vcf file. Also generates a random number usung random.randrnge for the random seed.

import tskit
import msprime
import numpy
import sys
import random

NUM = random.randrange(1,2147483648)
print(NUM)

# Population IDs
Altai, AFR1, AFR2, AFR3, AFR4 = 0, 1, 2, 3, 4
def BothIntrogression_4Pops(random_seed=None):
    ts = msprime.simulate(
        Ne=10**4, ### Constant Effective Population size of 10,000
        recombination_rate=1e-8, 
        mutation_rate=1e-8,
        length=100000000, #10MB,
        
        #### Sample 30 haplotypes (15 diploid individuals) from each Modern human population at present time
        #### Also sample 2 haplotypes (1 individal) of Altai Neanderthal at 50,000 years ago
        samples = [msprime.Sample(time=0, population=AFR1)]*30 +[msprime.Sample(time=0, population=AFR2)]*30+ [msprime.Sample(time=0, population=AFR3)]*30 + [msprime.Sample(time=0, population=AFR4)]*30 + [msprime.Sample(time=(50000/30), population=Altai)]*2,
             
        population_configurations = [
            msprime.PopulationConfiguration(), # Altai
            msprime.PopulationConfiguration(), # AFR1
            msprime.PopulationConfiguration(), # AFR2
            msprime.PopulationConfiguration(), # AFR3
            msprime.PopulationConfiguration(), # AFR4
        ],
        demographic_events = [
            ### Archaic Introgression from Altai into AFR4 at 60,000 years ago
            msprime.MassMigration(time = (60000/30),
            source=AFR4, destination=Altai, proportion=0.05),

            ### Divergence of AFR3 and AFR4 at 100,000 years ago
            msprime.MassMigration(time = (70000/30),
            source=AFR4, destination=AFR3, proportion=1),
            
            ### Modern Human Introgression into Altai from AFR1 at 100,000 years ago
            msprime.MassMigration(time = (100000/30),
            source=Altai, destination=AFR1, proportion=0.05),

            ## Divergence of AFR2 and AFR3 at 125,000 years ago
            msprime.MassMigration(time = (125000/30),
            source=AFR3, destination=AFR2, proportion=1),
            
            ### Divergence of Modern Humans 150,000 years ago
            msprime.MassMigration(time = (150000/30),
            source=AFR2, destination=AFR1, proportion=1),
                               
            ### Divergence of Modern Human and Neanderthal at 765,000 years ago
            msprime.MassMigration(time = (765000/30),
            source=Altai, destination=AFR1, proportion=1),                
       ],
    record_migrations=True,
    random_seed=NUM,
    )
    return ts
ts = BothIntrogression_4Pops(NUM)

##### Write trees to output file
ts.dump(sys.argv[1])

##### Write Diploid VCF file
##### Population Order tsk_0-14 = POP1, tsk_15-29 = POP2, tsk_30-44 = POP3, tsk_45-59 = POP4, tsk_60 = Altai
with open(sys.argv[2], "w") as vcf_file:
    ts.write_vcf(vcf_file, 2)





                 
