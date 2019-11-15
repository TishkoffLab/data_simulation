## Simulating Data

### msprime

Right now the functionality available is to simulate any number of epochs, and for each epoch generate a set of genotypes and phenotypes for the specified number of individuals. 
The script to run is 
```
generate_simulated_phenogeno.py
```

Input is provided as a series of flags when you run the program, as well as a file that lays out the specifics of each epoch that you want to simulate.



The output is two files per epoch: 
```
- a vcf file; <outname>.epoch<N>.pheno.vcf
- a phenotype file; <outname>.phenotypes
```

For the VCF file, each variant entry corrisponds to a single mutation generated in the course of a simulation  