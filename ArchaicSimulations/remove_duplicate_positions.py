############# Removes duplicate positions from msprime output vcf file.
############# Currently reads uncompressed vcf files. In order to read compressed vcf file, comment out lines: 7 and 15, and uncomment lines: 8,16,17
############# Takes two command line arguments: 1) Input vcf file, and 2) Output vcf file.
import sys
import re
import gzip
data = open(sys.argv[1])
#data = gzip.open(sys.argv[1])
write_file = open(sys.argv[2], "w")

ALL = {}
ALL_DATA = []

for line in data:
    lines = line.rstrip("\n")
    #lines = line.rstrip(b"\n")
    #lines = lines.decode()
    if re.match("#", lines):
        write_file.write(str(lines) + "\n")
    else:
        col = re.split("\t", lines)
        POS = col[1]
        ALL_DATA.append(lines)
        try:
            VAL = ALL[POS]
            ALL[POS] = VAL + 1
        except KeyError:
            ALL[POS] = 1
data.close()

for lines in ALL_DATA:
    col = re.split("\t", lines)
    POS = col[1]
    VAL = ALL[POS]
    if VAL > 1:
        continue
    else:
        write_file.write(str(lines) + "\n")
write_file.close()
