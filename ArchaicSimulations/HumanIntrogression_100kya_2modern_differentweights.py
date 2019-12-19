#! /home/dharris/miniconda3/bin/python
######### Simulates 2 human populations and 1 Archaic popultion. Introgression occurs from AFR1 to Altai.
######### 3 Command line arguments: 1) Output file for tskit trees, 2) Output vcf file, and 3) Introgression weight
import tskit
import msprime
import numpy
import sys

# Population IDs
Altai, AFR1, AFR2 = 0, 1, 2
def human_introgression(random_seed=None):
    ts = msprime.simulate(
        Ne=10**4,
        recombination_rate=1e-8,
        mutation_rate=1e-8,
        length=100000000, #10MB,
        #Introgression_VAL = float(sys.argv[3]),
        samples = [msprime.Sample(time=0, population=AFR1)]*30 +[msprime.Sample(time=0, population=AFR2)]*30+ [msprime.Sample(time=(50000/30), population=Altai)]*2,
            #[msprime.Sample(time=0, population=AFR)]*10,
            #[msprime.Sample(time=(50000/30), population=Altai)]*10,
            #],
        population_configurations = [
            msprime.PopulationConfiguration(), # Altai
            msprime.PopulationConfiguration(), # AFR1
            msprime.PopulationConfiguration(), # AFR2
        ],
        demographic_events = [

            ### AFR1 intorgression to Altai at 100,000 years ago
            msprime.MassMigration(time = (100000/30),
            source=Altai, destination=AFR1, proportion=float(sys.argv[3])),
            
            ### Divergence of Modern Humans 150,000 years ago
            msprime.MassMigration(time = (150000/30),
            source=AFR2, destination=AFR1, proportion=1),
                               
            ### Divergence of Modern Human and Neanderthal at 765,000 years ago
            msprime.MassMigration(time = (765000/30),
            source=Altai, destination=AFR1, proportion=1),                
       ],
    record_migrations=True,
    random_seed=1,
    )
    return ts
ts = human_introgression(1)

ts.dump(sys.argv[1])
with open(sys.argv[2], "w") as vcf_file:
    ts.write_vcf(vcf_file, 2)



                 
