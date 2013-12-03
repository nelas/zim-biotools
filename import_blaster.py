#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Import BLASTer results into Zim.'''

import os
import sys

from biolib import make_header, make_dir


def main(blaster_file, root_page):
    # Remove extension.
    root = os.path.splitext(root_page)[0]

    # Make sure there is a folder to the root.
    make_dir(root)

    # Define organism and initials by reading the root name.
    organism = os.path.basename(root).replace('_', ' ')
    initials = organism.split()[0][0] + organism.split()[1][:3]

    # Create page for genes and directory.
    genes_file = os.path.join(root, 'Genes.txt')
    genes_page = open(genes_file, 'w')
    genes_page.write(make_header('Genes'))
    genes_page.close()

    # Define genes directory.
    genes_dir = os.path.join(root, 'Genes')
    make_dir(genes_dir)

    # Open BLASTer file.
    genes = open(blaster_file)

    # Create variables for parsing.
    plain = ''
    space_count = 0
    reciprocal = False
    contig_id = ''
    gene_names = []
    first = True

    # Iterate over each locus.
    for line in genes.readlines():

        #import pdb; pdb.set_trace()
        
        # Saves splitted line for parsing.
        splitted = line.split()

        # If first line define id first.
        if first:
            plain += line
            contig_id = splitted[0]
            first = False

        # New record trigger.
        if space_count == 2 and reciprocal:

            # Trims out first empty record.
            if splitted:

                # Define file name.
                gene_name = '%s_%s' % (initials, '_'.join(gene_names))

                # Sanitize gene_file, just in case.
                gene_name = gene_name.replace('/', '-')

                # Define gene filepath.
                gene_file = os.path.join(genes_dir, '%s.txt' % gene_name)

                # Verify if page already exists.
                try:
                    gene_page = open(gene_file, 'r')
                    gene_page.close()
                    # If it does, skip page.
                    continue
                except:
                    # If not, create page.
                    pass

                # Create gene_page and write header.
                gene_page = open(gene_file, 'w')
                gene_page.write(make_header(gene_name.replace('_', ' ')))

                # Write contig location.
                gene_page.write('[[%s:Loci:%s]]' % (organism, contig_id.replace('/', '-')))
                gene_page.write('\n\n')
                gene_page.write('===== Reciprocal BLASTs =====\n')
                gene_page.write('\n\'\'\'\n%s\'\'\'\n' % plain)

                # Close locus file.
                gene_page.close()

                # Reset variables.
                plain = ''
                reciprocal = False
                contig_id = ''
                gene_names = []

                # Start over adding the next line.
                plain += line
                contig_id = splitted[0]

        elif space_count == 2 and not reciprocal:
                # Reset variables.
                plain = ''
                reciprocal = False
                contig_id = ''
                gene_names = []
                # Start over adding the next line.
                plain += line
                contig_id = splitted[0]
        else:
            plain += line

        # Count empty lines to know when a record is finished.
        if not splitted:
            space_count += 1
        else:
            space_count = 0

        # Only consider entries with positive reciprocal blasts.
        if '<<' in splitted:
            reciprocal = True
            if not splitted[0] in gene_names:
                gene_names.append(splitted[0])

    # Exit program.
    sys.exit(0)

if __name__ == '__main__':
    # arg1: blaster results file
    # arg2: root page
    main(sys.argv[1], sys.argv[2])
