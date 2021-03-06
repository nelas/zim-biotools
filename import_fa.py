#!/usr/bin/python
# -*- coding: utf-8 -*-

'''FASTA importer tool for Zim.

Dependencies:
    - Python 2.7
    - Biopython 1.56

'''

import os
import sys
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

from biolib import make_header, make_dir


def main(fasta_file, root_page):
    # Remove extension.
    root = os.path.splitext(root_page)[0]

    # Make sure there is a folder to the root.
    make_dir(root)

    # Define organism tag by reading the root name.
    organism = os.path.basename(root)

    # Parse FASTA file.
    loci = SeqIO.parse(fasta_file, 'fasta')

    # Create loci page and directory.
    loci_file = os.path.join(root, 'Loci.txt')
    loci_page = open(loci_file, 'w')
    loci_page.write(make_header('Loci'))
    loci_page.close()

    # Define Loci directory.
    loci_dir = os.path.join(root, 'Loci')
    make_dir(loci_dir)

    # Iterate over each locus.
    for locus in loci:

        # Sanitize locus.id.
        locus_id = locus.id.replace('/', '-')

        # Define locus file.
        locus_file = os.path.join(loci_dir, '%s.txt' % locus_id)

        # Verify if page already exists.
        try:
            locus_page = open(locus_file, 'r')
            locus_page.close()
            # If it does, skip page.
            continue
        except:
            # If not, create page.
            pass

        # Identify the frame and the strand by parsing the description.
        # Example: >Lrub_5432 | frame: +1 | candidates: Six3-6, Optix
        frame = int(locus.description.split('|')[-2][-2])
        frame_step = frame - 1
        strand = locus.description.split('|')[-2][-3]

        # Always garantee that the sequence is a plus strand.
        if strand == '-':
            locus.seq = locus.seq.reverse_complement()
            locus.description = locus.description.replace('frame: %s%d' % (strand, frame), 'frame: +%d' % frame)

        # Translate using the correct frame.
        translated_seq = locus.seq[frame_step:].translate()
        # Create SeqRecord for protein.
        protein = SeqRecord(translated_seq, id=locus.id, name=locus.name, description=locus.description)

        # Create locus_page and write header.
        locus_page = open(locus_file, 'w')
        locus_page.write(make_header(locus_id))

        # Write organism name.
        locus_page.write('@%s ' % organism)
        locus_page.write('\n\n')

        # Write sequence in FASTA format.
        locus_page.write('@locus %d bp \n' % len(locus.seq))
        locus_page.write("'''\n")
        locus_page.write(locus.format('fasta'))
        locus_page.write("\n'''\n")

        # Write protein sequence.
        locus_page.write('@protein \n')
        locus_page.write("'''\n")
        locus_page.write(protein.format('fasta'))
        locus_page.write("\n'''\n")

        # Close locus file.
        locus_page.close()

    # Exit program.
    sys.exit(0)

if __name__ == '__main__':
    # arg1: fasta file
    # arg2: root page
    main(sys.argv[1], sys.argv[2])
