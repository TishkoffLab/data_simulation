#! /home/dharris/miniconda3/bin/python
######### Simulates 2 human populations and 1 Archaic popultion. Introgression occurs from Altai to AFR1
######### 2 Command line arguments: 1) Output file for tskit trees, and 2) Output vcf file
import tskit
import msprime
import numpy
import sys

# Population IDs
Altai, AFR1, AFR2 = 0, 1, 2
def archaic_introgression(random_seed=None):
    ts = msprime.simulate(
        Ne=10**4,
        recombination_rate=1e-8,
        mutation_rate=1e-8,
        length=100000000, #10MB,
        samples = [msprime.Sample(time=0, population=AFR1)]*30 +[msprime.Sample(time=0, population=AFR2)]*30+ [msprime.Sample(time=(50000/30), population=Altai)]*2,
        
        population_configurations = [
            msprime.PopulationConfiguration(), # Altai
            msprime.PopulationConfiguration(), # AFR1
            msprime.PopulationConfiguration(), # AFR2
        ],
        demographic_events = [

            ### Neanderthal Introgression to AFR1 at 100,000 years ago
            msprime.MassMigration(time = (100000/30),
            source=AFR1, destination=Altai, proportion=0.05),
            
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
ts = archaic_introgression(1)

ts.dump(sys.argv[1])

with open(sys.argv[2], "w") as vcf_file:
    ts.write_vcf(vcf_file, 2)





                 
