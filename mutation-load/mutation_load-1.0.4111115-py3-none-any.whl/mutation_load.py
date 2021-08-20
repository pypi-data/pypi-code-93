#!/usr/bin/env python

import subprocess
import os
import time
from datetime import datetime
import collections
import optparse
import re
import csv
import random
import configparser
import pkg_resources

#import regex_patterns
#from mutation_load.regex_patterns import regex_patterns
def package_repo_imports():
    """Makes imports and finds configuration file depending on if the file is run as a package or cloned from git."""
    global regex_patterns
    try:
        from regex_patterns import regex_patterns
    except ModuleNotFoundError:
        from mutation_load.regex_patterns import regex_patterns
    if not os.path.isfile(os.path.dirname(os.path.realpath(__file__))+'/resources/mutation_load_config.ini'):
        config_path=pkg_resources.resource_filename(__name__, os.path.join("resources", "mutation_load_config.ini"))
    else:
        config_path=os.path.dirname(os.path.realpath(__file__))+'/resources/mutation_load_config.ini'
    return config_path

config_path=package_repo_imports()
parser=configparser.ConfigParser()
parser.read(config_path)
samtools_location = parser.get('tools_and_envs','samtools') #Location for samtools
bedtools_location = parser.get('tools_and_envs','bedtools') #Location for bedtools


#Makes program report
def make_report(values):
    """Makes a report file with headers"""
    currentDT=datetime.now()
    report = values.prefix+"_report_"+currentDT.strftime("%Y%m%dT%H%M%S")+".txt" #Report name with timestamp
    report_name=values.destination+'/'+report #Report with path so it can easily be opened later
    with open(report_name, 'w+') as f: #Makes report and writes header
        f.write(os.path.basename(__file__)+" report, "+currentDT.strftime("%Y-%m-%d %H:%M:%S")+".\n") #Writes report introduction
        if values.ignore!='0': #If there are flags set to ignore, it is written to report
            f.write("Ignored positions with bitflags "+values.ignore+'.\n') #Writes ignored flags to report
        if values.include!=' ': #If there are flags that should be included
            f.write("Counted only positions with bitflags "+values.include+'.\n') #Writes ignored flags to report
        if values.number==None: #If reference number was not given, CDF was counted
            f.write("Counted CDF from largest to smallest: "+str(values.reverse)+'.\nIntervals of the prints are min '+str(values.percent_interval)+'%.\n') #Writes, if CDF was counted from largest to smallest or not and the interval
        else: #If reference number was given
            f.write("Counted CDF only for given number "+str(values.number)+'.\n') #Writes that CDF was counted only for given number
            f.write("Counted how many genomic positions had more (True) or less (False) reads than given number: "+str(values.more)+'.\n') #Writes, whetever number of reads exceed or underspend given reference number
        f.write("Limit is "+str(values.limit)+'\n') #Write given limit
        f.write("Counted average of numbers below the limit: "+str(values.lower)+'.\n') #Write, if average was counted below or above of limit
        if values.head!='': #If head argument was given
            f.write("Used argument head -n "+values.head+'.\n') #Writes used argument
        if values.orig_bed!='': #Checks if bed-file was given
            f.write("Used bedfile(s) ",values.orig_bed,'.\n') #Writes used bed-file
        if values.other_args!='': #Check if there were some other arguments given for samtools view
            f.write("Other samtools arguments used: "+values.other_args+'.\n') #Writes other samtools arguments used

    return report_name #Returns report name for further use

#Writes CDF-fucntion to report
def write_report_cdf(report,percent,word,current_number, tot_count):
    """Writes to report how large read depth has to be to include given percent of genomic positions."""
    with open(report, 'a') as f: #Opens reads covering sites report
        if percent==0: #If it is first time that function is called
            f.write('\n') #Adds a line break
        if current_number==-1: #If current_number is still initialized number
            f.write("0 genomic positions with given requirements found.\n") #Writes that no genomic position with given requirements was found
            return
        if percent==101: #Program has gone through all lines
            f.write("100% of "+str(tot_count)+" genomic positions have "+str(current_number)+" or "+word+" reads covering site.\n") #Write last number to CDF-function
            return
        if percent==0 and current_number==1 and word=="less": #There is no numbers between 0 and 1, so it would be stupid to write "There are no numbers below 1 but greater than 0"
            return

        if percent==0: #If current number is first one and larger than 1 (different formatting if number is 1 and function goes upwards in numbers)
            f.write("0%  of covered genomic positions have "+word+" than "+str(current_number)+" reads covering site.\n") #Write how many percent has only 1 read
        elif current_number==1 and word=="less": #If current number is 1 and program is going upwards, 1 must be the first number when occuring. Percent is already changed.
            f.write('{:.2f}'.format(100*percent)+"% ("+str(tot_count)+" pcs.) of covered genomic positions have 1 read covering site.\n") #Write how many percent has only 1 read
        else: #Current number is not the first one
            f.write('{:.2f}'.format(100*percent)+"% ("+str(tot_count)+" pcs.) of covered genomic positions have "+str(current_number)+" reads or "+word+" covering site.\n") #Writes how many percent and amount of genomic positions with reads more or less than current number


def sample_lines_from_file(file, amount):
    """Samples given amount of lines from given file."""
    if amount==0:
        return []
    with open(file, 'r') as fr:
        sum=0
        for line in fr:
            sum+=1
        fr.seek(0)
        indices = sorted(random.sample(range(sum), amount))
        max_index=max(indices)
        sampled_lines=list()
        for n, line in enumerate(fr):
            if n>max_index:
                break
            if n in indices:
                sampled_lines.append(line)
    return sampled_lines


def write_permutated_lines(f_vcf, lines, type_amount):
    """Writes given amount of permutated lines to given permutated VCF and returns lines, where the not used lines are written for later use."""
    for line in lines[:type_amount]:
        columns=line.split()
        f_vcf.write(columns[0]+'\t'+columns[1]+'\t.\t'+columns[2]+'\t'+columns[3]+'\t.\t.\t.\tGT\t0/1\n') #Write to vcf file
    return lines[type_amount:]

def create_indel(length):
    """Permutates given length indel"""
    bases=['A','T','C','G'] #Different possible bases
    return random.choices(bases,k=length) #Randomly samples bases, k is insertion size minus reference base


def permutate_insertion(f_vcf, pair, region_lines, region_mutation_count, insertions, mut_files_location):
    """Makes indel to permutated VCF.

    Depending on insertion argument, function permutates insertion or deletion to a permutated VCF file.
    Function uses files generated earlier, that contain all positions, that the original bam file covered.
    From a file, that contains positions from the same area as in pair[1] argument, function samples one line, to which it makes the indel."""
    #bases=['A','T','C','G'] #Different possible bases
    type=pair[1]
    if type in region_lines:
        lines=region_lines[type]
    else:
        if type==".":
            type="dot"
        type_mod=type.replace(";", "_")
        lines=sample_lines_from_file(mut_files_location+'/'+type_mod+'.txt', region_mutation_count[type])
        region_lines[type]=lines

    #variant_list=random.choices(bases,k=pair[0]) #Randomly samples bases, k is insertion size minus reference base
    lines_to_remove=list()
    for line in lines[0:insertions[pair]]:#region_lines[type][0:indels[pair]]:
        columns=line.split()
        variant=columns[2]+''.join(create_indel(pair[0])) #Add insertion to reference base to variant position
        f_vcf.write(columns[0]+'\t'+columns[1]+'\t.\t'+columns[2]+'\t'+variant+'\t.\t.\t.\tGT\t0/1\n') #Write to vcf file
        lines_to_remove.append(line)
    for line in lines_to_remove:
        region_lines[type].remove(line)
    return region_lines


def remove_permutated_lines(file, string):
    """Removes line containing given string from the given file"""
    os.system("sed -i '/"+string+"/d' "+file)

def find_file(location, string):
    """Finds file that contains the given string from the given location."""
    p = subprocess.Popen(("grep -P '"+string+"' "+location+'/*'), \
      shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) #Views file with header and captures output to stream
    out, err = p.communicate()
    if out.decode()=='': #Position is not covered with the given depth
        return None, None
    columns=out.decode().split(':')
    if len(columns<2):
        raise RuntimeError("Grep failed with command grep -P '"+string+"' "+location+"/*. Columns: ",columns)
    return columns[0], columns[1] #rest contains one line and next file separated by linebreak

def count_file_lines(file):
    """Counts line count of the given file."""
    line_sum=0
    with open(file, 'r') as fr:
        for line in fr:
            line_sum+=1
    return line_sum

def get_syn_nonsyn_lines(mut_files_location, tot_amount):
    """Samples exonic lines from nonsynonymous and synonymous temp_perm_files"""
    wc_syn=count_file_lines(mut_files_location+'/perm_exon_syno.txt')
    wc_nonsyn=count_file_lines(mut_files_location+'/perm_exon_nonsyno.txt')
    if wc_syn>wc_nonsyn:
        amount_nonsyn=random.sample(range(max(0,tot_amount-wc_syn), min(wc_nonsyn,tot_amount)+1),1)[0]
        amount_syn=tot_amount-amount_nonsyn
    else:
        amount_syn=random.sample(range(max(0,tot_amount-wc_nonsyn), min(wc_syn,tot_amount)+1),1)[0]
        amount_nonsyn=tot_amount-amount_syn
    lines=sample_lines_from_file(mut_files_location+'/perm_exon_syno.txt', amount_syn)
    lines+=sample_lines_from_file(mut_files_location+'/perm_exon_nonsyno.txt', amount_nonsyn)
    return lines


def permutate_dels(values, dels, mut_files_location, f_vcf):
    """Permutates deletions from temp_mut_location files."""
    sum_dels=sum(dels.values())
    while sum_dels>0:
        for length, type in dels:
            if type==".":
                type="dot"
            type_mod=type.replace(";", "_")
            if type=="exonic" and values.separate_syn:
                lines=get_syn_nonsyn_lines(mut_files_location, dels[length, type])
            else:
                lines=sample_lines_from_file(mut_files_location+'/'+type_mod+'.txt', dels[length, type])
            for line in lines:
                columns=line.split()
                chrom=columns[0]
                #pos=str(int(columns[1])-int(length)) #It doesn't matter if negative, because grep won't find it
                pos=str(int(columns[1])-1) #It doesn't matter if negative, because grep won't find it
                file, rest=find_file(mut_files_location, chrom+'\t'+pos+'\t')
                if file==None:
                    continue
                line=rest.split('\n')[0]+'\n'
                columns=line.split()
                variant_list=create_indel(length)
                variant=columns[2] #Variant is only the reference base
                columns[2]=columns[2]+''.join(variant_list)#Add deletion to reference base
                f_vcf.write(columns[0]+'\t'+columns[1]+'\t.\t'+columns[2]+'\t'+variant+'\t.\t.\t.\tGT\t0/1\n') #Write to vcf file
                for i in range(int(pos)-1, int(pos)+int(length)):
                    file, _ = find_file(mut_files_location, chrom+'\t'+str(i)+'\t')
                    remove_permutated_lines(file, chrom+'\t'+str(i)+'\t') #Removes every possible line after the deletion.
                dels[length,type]-=1
        sum_dels=sum(dels.values())

def create_permutated_vcf(values, vcf_file, tot_sum, snv, dels, insertions, synonymous, nonsynonymous, not_exonic, mut_files_location):
    """Permutates mutations for permutated VCF file.

    Permutates mutations using temporal region files made in make_perm_mut_files to permutate mutations.
    For SNV mutations, function samples ready lines from file having the same region and type as its name as the original mutation had.
    For indel mutations, function uses make_indel function.
    Uses region_lines to keep count about lines that were not used and can be used later."""
    f_vcf = open(vcf_file,'a') #Opens vcf file for appending
    permutate_dels(values, dels, mut_files_location, f_vcf)
    region_mutation_count=collections.Counter() #Keep count of how many different region mutations there are, so you can permutate right amount of lines
    for pair in dels: #Go through deletions
        region_mutation_count[pair[1]]+=dels[pair]
    region_lines=dict()
    for pair in insertions:
        region_mutation_count[pair[1]]+=insertions[pair]
    if values.separate_regions:
        if values.separate_syn:
            sampled_lines=sample_lines_from_file(mut_files_location+"/perm_exon_syno.txt", synonymous+region_mutation_count["exonic"])
            region_lines["exonic"]=write_permutated_lines(f_vcf, sampled_lines, synonymous)
            sampled_lines=sample_lines_from_file(mut_files_location+"/perm_exon_nonsyno.txt", nonsynonymous+region_mutation_count["exonic"])
            region_lines["exonic"]=region_lines["exonic"]+write_permutated_lines(f_vcf, sampled_lines, nonsynonymous)
        else:
            sampled_lines=sample_lines_from_file(mut_files_location+'/exonic.txt', snv+region_mutation_count["exonic"])
            region_lines["exonic"]=write_permutated_lines(f_vcf, sampled_lines, snv)
    else:
        sampled_lines=sample_lines_from_file(mut_files_location+'/perm_snv.txt', tot_sum)
        region_lines["useless"]=write_permutated_lines(f_vcf, sampled_lines, snv)

    for type in not_exonic: #Goes through not exonic mutations and samples lines from corresponding files to the permutated VCF
        type_mod=type
        if type==".":
            type_mod="dot"
        type_mod=type_mod.replace(";", "_")
        sampled_lines=sample_lines_from_file(mut_files_location+'/'+type_mod+'.txt', not_exonic[type]+region_mutation_count[type])
        region_lines[type]=write_permutated_lines(f_vcf, sampled_lines, not_exonic[type])
    for pair in insertions:
        region_lines=permutate_insertion(f_vcf, pair, region_lines, region_mutation_count, insertions, mut_files_location)
    #insertion=False
    #for pair in dels:
#        region_lines=make_indel(f_vcf, pair, region_lines, region_mutation_count, dels, insertion, mut_files_location)

    f_vcf.close()


def write_temp_mut_line(fw, line):
    """Writes only necessary columns to temporal mutation file."""
    columns=line.split()
    for i in range(5):
        if i==2: #Otherwise writes the position twice
            continue
        fw.write(columns[i])
        if i<4:
            fw.write('\t')
    fw.write('\n')

def make_perm_mut_files(values, anno_file, index, timestamp):
    """Creates region files, that contain all covered positions and their possible mutations, to temporal temp_perm_mutations folder.

    Depending on the settings, function creates files for each region type, where the mutations will be permutated. that is covered in original bam file.
    In addition, if defined in the parameters, it separates synonymous and nonsynonymous mutations to files "perm_exon_syno.txt" and "perm_exon_nonsyno.txt".
    If specified, function also creates files for different type of exon mutations and for different regions."""
    if not os.path.isdir(values.destination+'/temp_perm_mutations/'):
        os.mkdir(values.destination+'/temp_perm_mutations/')
    location=values.destination+'/temp_perm_mutations/'+str(index)+'_'+timestamp+'/'
    if not os.path.isdir(location):
        os.mkdir(location)
    not_exonic=dict()
    if not values.separate_regions:
        f_snv=open(location+'/perm_snv.txt', 'a+')
    elif values.separate_syn:
        f_syn=open(location+'/perm_exon_syno.txt', 'a+')
        f_nonsyn=open(location+'/perm_exon_nonsyno.txt', 'a+')
    else:
        f_exon=open(location+'/exonic.txt', 'a+')
    f_anno=open(anno_file, 'r')
    f_anno_lines=f_anno.readlines()
    for line in f_anno_lines[1:]: #Reads stdout line by line, skips header
        components = line.split() #Decodes line values and separate them
        if components[5]!="exonic" and values.skip_nonexon:
            continue
        if values.separate_regions:
            if components[5]!="exonic":
                if not components[5] in not_exonic:
                    not_exonic[components[5]]=list()
                not_exonic[components[5]].append(line)
            else:
                if values.separate_syn:
                    if components[8]=='synonymous':
                        write_temp_mut_line(f_syn, line)
                    elif components[8]=='nonsynonymous':
                        write_temp_mut_line(f_nonsyn, line)
                    else:
                        if not components[8] in not_exonic:
                            not_exonic[components[8]]=list()
                        not_exonic[components[8]].append(line)
                else:
                    write_temp_mut_line(f_exon, line)
        else:
            write_temp_mut_line(f_snv, line)
    f_anno.close()
    if not values.separate_regions:
        f_snv.close()
    elif values.separate_syn:
        f_syn.close()
        f_nonsyn.close()
    else:
        f_exon.close()
    time.sleep(0.5)
    for type in not_exonic:
        if type==".":
            type_mod="dot"
        else:
            type_mod=type.replace(";", "_")
        with open(location+'/'+type_mod+'.txt', 'a+') as fw:
            for line in not_exonic[type]:
                write_temp_mut_line(fw, line)
                #fw.write(line)
    return location



def gen_mutations_to_files(values, generated_vcf_file_list, f_report, index, timestamp):
    """Annotates generated VCF files and writes them to corresponding temporal mutation files.

    Goes generated VCF files (which contain all possible mutations for the covered positions with the given requirements in original bam file) through
    one by one, annotates them and gives them to make_perm_mut_files function, which then collects all mutations to corresponding files based on their region and type."""
    for count, generated_vcf in enumerate(generated_vcf_file_list):
        if not os.path.isfile(generated_vcf):
            break
        if not os.path.isdir(values.destination+'/'+"gen_vcf_annotations"):
            os.mkdir(values.destination+'/'+"gen_vcf_annotations")
        prefix=values.destination+"/gen_vcf_annotations/temp_mutation_load"+timestamp+'_'+str(index)+'_'+str(count)
        recursion_counter=0
        while not os.path.isfile(prefix+".hg38_multianno.txt"):
            os.system("rm "+prefix+'*')
            time.sleep(1)
            recursion_counter+=1
            if recursion_counter>1:
                print("Restarting ANNOVAR because of failed annotation.")
                f_report.write("Restarted ANNOVAR for file "+generated_vcf+"\n")
            os.system('time '+values.table_annovar+' '+generated_vcf+' '+\
            values.annovar+' -buildver '+values.buildver+' -otherinfo -remove --vcfinput -protocol refGene -operation g -out '+prefix)
            print('Executing command \'time '+values.table_annovar+' '+generated_vcf+' '+\
            values.annovar+' -buildver '+values.buildver+' -otherinfo -remove --vcfinput -protocol refGene -operation g -out '+prefix+"'")
        if recursion_counter>1:
            print("ANNOVAR was started "+str(recursion_counter)+" times for file "+generated_vcf+'_'+str(count)+'.')
            f_report.write("Recursion was done "+str(recursion_counter)+" times for file "+generated_vcf+'_'+str(count)+".\n")
        os.system("rm "+prefix+'*.vcf '+prefix+'*.avinput')
        location=make_perm_mut_files(values, prefix+".hg38_multianno.txt", index, timestamp)
        if not values.keep_temp_files:
            os.system("rm "+prefix+'*')
        time.sleep(1)
    return location


def count_vcf_mutations(values,vcf_files, prefix="temp"):
    """Annotates given VCF file (with the given prefix) and counts different type of variants in them"""
    snv=tot_sum=synonymous=nonsynonymous=0
    dels, insertions,not_exonic= (collections.Counter() for i in range(3))
    if not os.path.isdir(values.destination+'/ref_vcf_anno'):
        os.mkdir(values.destination+'/ref_vcf_anno')
    anno_prefix=values.destination+'/ref_vcf_anno/'+prefix+"_orig_vcf"+datetime.now().strftime("_%Y%m%dT%H%M%S")
    for file in vcf_files: #Goes through every vcf file, annotates them and counts mutations and their types, categorizing them for random bam-file
        print('Executing command \'time '+values.table_annovar+' '+file+' \
        '+values.annovar+' -buildver '+values.buildver+' -otherinfo -remove --vcfinput -protocol refGene -operation g -out '+anno_prefix+'\'')
        while not os.path.isfile(anno_prefix+'.hg38_multianno.txt'):
            os.system("rm "+anno_prefix+'*')
            os.system('time '+values.table_annovar+' '+file+' \
            '+values.annovar+' -buildver '+values.buildver+' -otherinfo -remove --vcfinput -protocol refGene -operation g -out '+anno_prefix)
        f_anno=open(anno_prefix+'.hg38_multianno.txt', 'r')
        f_anno_lines=f_anno.readlines()
        for line in f_anno_lines[1:]: #Reads stdout line by line, skips header
            components = line.split() #Decodes line values and separate them
            if components[5]!="exonic" and values.skip_nonexon:
                continue
            if not values.separate_regions:
                components[5]="perm_snv"
            if len(components[3])>1 or components[4]=='-': #If variant is deletion
                dels[len(components[3]),components[5]]+=1 #Add deletion's length, original base has already been removed
            elif len(components[4])>1 or components[3]=='-': #If variant is insertion
                insertions[len(components[4]),components[5]]+=1 #Add insertion's length, original base has already been removed
            else:
                if values.separate_regions:
                    if components[5]!="exonic":
                        not_exonic[components[5]]+=1
                    else:
                        if values.separate_syn:
                            if components[8]== 'synonymous':
                                synonymous+=1
                            elif components[8] == 'nonsynonymous':
                                nonsynonymous+=1
                            else:
                                not_exonic[components[8]]+=1
                        else:
                            snv+=1
                else:
                    snv+=1 #Add snv to sum
            tot_sum+=1 #Total sum of variants increases by one
        if not values.keep_temp_files:
            os.system("rm "+anno_prefix+"*")
        f_anno.close()
    return tot_sum, snv, dels, insertions, synonymous, nonsynonymous, not_exonic #Returns sums


#Sorts vcf file by chromosome and position
def sort_vcf(values,vcf_file):
    """Sorts the given vcf_file"""
    vcf_sorted=open(values.destination+"/sorted_temp.vcf", 'w+') #Create new vcf file where lines are sorted
    vcf_orig=open(vcf_file,'r') #Open originally created vcf file for reading
    not_header=list() #Create list for not header lines
    for line in vcf_orig: #Go original vcf file line by line
        if line.startswith('#'): #If line is a header
            vcf_sorted.write(line) #Write line to new sorted vcf
        else: #Line is not header, it must be sorted
            not_header.append(line) #Add line to not headers list
    for line in sorted(not_header, key=lambda line: (int(line.split()[0]) if line.split()[0].isdigit() else 999, line.split()[0], int(line.split()[1]))): #Sort not header lines by chromosome
        vcf_sorted.write(line) #Write lines to sorted vcf, first they are sorted by chromosome then by position
    vcf_sorted.close() #Close sorted vcf
    vcf_orig.close() #Close original vcf-file
    os.remove(vcf_file) #Remove unsorted vcf
    os.rename(values.destination+"/sorted_temp.vcf", vcf_file) #Rename sorted vcf file


def filter_given_vcf(values, vcf_file, patient_name):
    """Filters positions that were not covered with the given requirements from the given VCF."""
    ignored_positions=list()
    with open(vcf_file, 'r') as fr:
        for line in fr:
            if line.startswith('#'):
                continue
            columns=line.strip().split()
            ignored_positions.append(columns[0]+','+columns[1])
    with open(values.destination+'/'+patient_name+"_coverages.txt", 'r') as fr:
        for line in fr:
            columns=line.strip().split()
            while columns[0]+','+columns[1] in ignored_positions:
                ignored_positions.remove(columns[0]+','+columns[1])
    new_vcf=values.destination+'/'+patient_name+"_vcf_modified.vcf"
    with open(vcf_file, 'r') as fr, open(new_vcf, 'w+') as fw:
        for line in fr:
            columns=line.strip().split()
            if len(columns)>=2:
                if columns[0]+','+columns[1] in ignored_positions:
                    continue
            fw.write(line)
    return new_vcf

def create_new_vcf(orig_vcf, new_vcf):
    """Creates the new VCF file with the same headers as the original VCF file."""
    with open(orig_vcf, 'r') as fr, open(new_vcf, 'w+') as fw:
        for line in fr:
            if not line.startswith("#"):
                break
            fw.write(line)


def permutate_vcf(values, generated_vcf_files, report):
    """Permutates from generated_vcf_files similar and same amount of mutations as in VCF files values.vcf_file"""
    vcf_files=values.vcf_file.split() #Separates vcf files, doesn't matter if only 1 exists
    f_report=open(report, "a")
    if len(generated_vcf_files)==0:
        raise RuntimeError("There are no generated vcf files.\n") #Raises error
    timestamp=datetime.now().strftime("%Y%m%dT%H%M%S")
    if len(vcf_files)!=len(generated_vcf_files):
        raise RuntimeError("There is a different amount of original and generated vcf files. Probably not wanted.\n")
        tot_sum, snv, dels, insertions, synonymous, nonsynonymous, not_exonic = count_vcf_mutations(values,vcf_files) #Sum of different variant types
        for generated_vcf_file_list in generated_vcf_files:
            mut_files_location=gen_mutations_to_files(values, generated_vcf_file_list, f_report, index, timestamp)
        if not os.path.isdir(values.destination+"/permutations"):
            os.mkdir(values.destination+"/permutations")
        for i in range(values.perm_amount):
            if len(generated_vcf_files)==1:
                new_vcf_file=values.destination+"/permutations/"+separate_sample_id(values, generated_vcf_files[0][0])+"_permutated_"+str(i)+".vcf" #Name of the new vcf-file
            else:
                new_vcf_file=values.destination+"/permutations/permutated_"+str(i)+".vcf" #Name of the new vcf-file
            create_new_vcf(vcf_files[0], new_vcf_file)
            create_permutated_vcf(values, annotated_vcf, new_vcf_file,tot_sum, snv, dels, insertions, synonymous, nonsynonymous, not_exonic,lines_of_annotated_vcf) #Creates new vcf and writes random variants based on above variant sums and coverages file
            sort_vcf(values, new_vcf_file) #Sort new vcf file
    else:
        index=0
        for orig_vcf_file, generated_vcf_file_list in zip(vcf_files, generated_vcf_files):
            f_report.write("\nPermutating vcf_file "+orig_vcf_file+" from generated vcf file(s) starting from "+generated_vcf_file_list[0]+'\n')
            patient_name=separate_sample_id(values, generated_vcf_file_list[0])
            with open(orig_vcf_file, 'r') as fr:
                empty=True
                for line in fr.readlines():
                    if not '#' in line:
                        empty=False
                        break
            if not empty:
                if values.no_vcf_filter:
                    temp_vcf_file=orig_vcf_file
                else:
                    temp_vcf_file=filter_given_vcf(values,orig_vcf_file, patient_name)
                tot_sum, snv, dels, insertions, synonymous, nonsynonymous, not_exonic = count_vcf_mutations(values,[temp_vcf_file], patient_name) #Sum of different variant types
                mut_files_location=gen_mutations_to_files(values, generated_vcf_file_list, f_report, index, timestamp)
            if values.perm_amount>1:
                if not os.path.isdir(values.destination+"/"+patient_name+"_permutations"):
                    os.mkdir(values.destination+"/"+patient_name+"_permutations")
            for i in range(values.perm_amount):
                if values.perm_amount>1:
                    new_vcf_file=values.destination+"/"+patient_name+"_permutations/"+patient_name+"_permutated_"+str(i)+".vcf"
                else:
                    new_vcf_file=values.destination+"/"+patient_name+"_permutated_"+str(i)+datetime.now().strftime("_%Y%m%dT%H%M%S")+".vcf" #Name of the new vcf-file
                create_new_vcf(orig_vcf_file, new_vcf_file)
                if not empty:
                    create_permutated_vcf(values, new_vcf_file, tot_sum, snv, dels, insertions, synonymous, nonsynonymous, not_exonic, mut_files_location) #Creates new vcf and writes random variants based on above variant sums and coverages file
                    sort_vcf(values, new_vcf_file) #Sort new vcf file
            index+=1
            if not values.keep_temp_files and not values.no_vcf_filter:
                os.system("rm "+temp_vcf_file)
    f_report.close()



def compare_one_number(file, numbers_tot, count, more, number, report):
    """User has given number argument, so only one number is compared to others in CDF."""
    percent=0
    tot_count=0
    while bool(count): #While there exists numbers is collections
        current_number=int(min(count.items(), key=lambda x: x[0])[0]) #Get the smallest number from the collection
        if more and current_number<number or not more and current_number>number: #Check if current number does not fulfil requirements
            del count[current_number] #Number did not fulfil the requirements so it is deleted
            continue #Program moves to the next number
        amount_of_number=int(min(count.items(), key=lambda x: x[0])[1]) #Number matched to the requirements, its amount is the second element from the collection
        tot_count+=amount_of_number #Add amount of the number to the total count
        percent+=amount_of_number/numbers_tot #Add percent of the number compared to the total amount of numbers to the total percent of numbers fulfilling requirements
        del count[current_number] #Delete counted number, moves to the next one

    if more: #If user wants to know how many numbers exceed the given number
        word="more" #Word written to the report is "more"
    else: #User wants to know how many numbers are smaller than given one
        word="less" #Word written to the report is "less"
    with open(report, 'a') as f: #Writes result to the report
        #Writes how many and what percent of positions have more or less than given number of reads covering site.
        f.write('{:.2f}'.format(100*percent)+"% ("+str(tot_count)+" pcs.) of "+str(numbers_tot)+" covered genomic positions have "+word+" than "+str(number)+" reads covering site.\n")


def config_intervals(values, number):
    """Gets the configuration intervals for the CDF plot."""
    last_interval=0 #Initializes last interval
    for interval in values.plot_intervals: #Runs over all the intervals in the config file
        if number<int(interval): #if number is smaller than the interval
            next_interval=int(interval)
            break #Breaks so last_interval is the last number is greater or equal to
        else: #Number is greater or equal
            last_interval=interval #Save current interval to the last
            next_interval=float('inf')
    return last_interval, next_interval #Return last interval that number was greater or equal to


def cdf_function(values, numbers_tot, count, report, writer, fnames, genome_size, bam_file):
    """Counts the CDF function of the read depths of given file"""
    percent=0 #Count cumulative percent for number of lines
    percent_printed=0 #Keep count what was the last percent that was printed
    tot_count=0 #Keep count of numbers that have been run through
    tot_sum=sum(count.values()) #Sum of total mapped reads
    current_number=-1 #Initialize current number, so program knows if there was not any in the collection
    word="less" #Initialize word
    sample_id=separate_sample_id(values, bam_file)
    next_interval=0
    while bool(count): #Goes through every number in the collection
        if values.reverse: #If user wants CDF-function to be counted from largest to smallest
            current_number=int(max(count.items(), key=lambda x: x[0])[0]) #Current number is the largest one from the collection
            amount_of_number=int(max(count.items(), key=lambda x: x[0])[1]) #Amount of that largest number
            word = "more" #Word used in reverse order is "more"
        else: #User wants to CDF-function from smallest to largest
            current_number=int(min(count.items(), key=lambda x: x[0])[0]) #Current number is the smallest one from the collection
            amount_of_number=int(min(count.items(), key=lambda x: x[0])[1]) #Amount of that smallest number
        if percent==0: #If current number is the first one
            write_report_cdf(report,percent,word,current_number, tot_count) #Writes report with 0 percent, current number already differs from -1
        tot_count+=amount_of_number #Add amount of current number to the total count
        if current_number>=next_interval:
            plot_interval, next_interval=config_intervals(values, current_number)
        writer.writerow({fnames[0]: sample_id, fnames[1] : current_number, fnames[2]: amount_of_number, fnames[3]: tot_count, fnames[4]: amount_of_number/genome_size, \
        fnames[5]: plot_interval})
        percent+=amount_of_number/numbers_tot #Add percent of the current number to the total percent
        if 100*(percent-percent_printed) >= values.percent_interval: #If the difference between lastly printed and current percent differs more than given interval
            write_report_cdf(report,percent,word,current_number, tot_count) #Writes report with that interval
            percent_printed=percent #Change lastly printed percent
        del count[current_number] #Delete current number from collection and move to the next one

    if current_number==-1: #There were no numbers in the collection
        write_report_cdf(report,percent,word,current_number, tot_count) #Make a note to the report
        print("0 covered genomic positions with given requirements found.") #Inform user
    else: #There were numbers in the collection
        write_report_cdf(report,101,word,current_number, tot_count) #Write to the report that  all numbers have been went through. 101 percent can't be achieved otherwise


def write_report_averages_and_limits(report, limit, undersized_count, numbers_tot, tot_average_count, tot_average_sum, lower):
    """Writes how many genomic positions had less than limit reads covering site and and average of numbers more or less than given limit"""
    if lower: #If user wants to know average of numbers less than given limit
        word="less" #Word used is less
    else: #User wants to know average of numbers more than given limit
        word="more" #Word is more

    with open(report, 'a') as f: #Opens program report
        if limit>1: #There are no reads less than 1 but more than 0, so check that limit is more than 1
            f.write(str(undersized_count)+" ("+'{:.2f}'.format(100*(undersized_count/numbers_tot))+'%) covered genomic positions had more than zero '+\
            'but less than '+str(limit)+' reads covering site.\n')#Writes how many positions had 0<reads<limit
        if tot_average_count>0: #If there were numbers found that are more or less than given limit
            f.write("Average of reads "+word+" than "+str(limit)+" is "+'{:.2f}'.format(tot_average_sum/tot_average_count)+".\n") #Writes average to the report
        else: #There were no reads more or less than limit
            f.write("Average of reads "+word+" than "+str(limit)+" is 0.\n") #Writes that average was 0



def whole_genome_length(file):
    """Counts the length of whole reference genome with given BAM file."""
    print("Counting whole genome length from stream "+samtools_location+' view -h '+file)
    stream = subprocess.Popen((samtools_location+' view -h '+file), \
      shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) #Views file with header and captures output to stream
    sum=0 #Initialize sum of the length
    for line in stream.stdout: #Go output line by line
        values = line.decode('utf-8').split() #Split columns on line and decode it
        if values[0][0]!='@': #If value does not start with '@', header has ended and counting can be stopped
            break #Ends stream
        if values[0]!="@SQ": #If value does not specify sequence dictionary
            continue #Moves to the next line
        sum+=int(values[2][3:]) #Gets reference sequence length and sums is to total length
    return sum #Returns total length 3099750718


def bed_genome_length(bed_file):
    """Counts length of the area covered by merged final BED file."""
    tot_length=0
    with open(bed_file, 'r') as fr:
        for line in fr:
            columns=line.split()
            if len(columns)<3:
                continue
            length=int(columns[2])-int(columns[1]) #0-based start 0A1A2T3C, 1-based end G=8, T=9, T=10...
            tot_length+=length
    return tot_length


def write_coverages_and_vcf_files(components, f_cov, f_vcf, values):
    """Write lines that have enough depth, and if there is enough variants also write vcf_file. Components=mpileup line columns."""
    count_forward = len(re.findall('[.ACGTN>*]', components[4])) #Count forward depth
    count_reverse = len(re.findall('[,acgtn<#]', components[4])) #Count reverse depth
    bases=['A', 'C', 'G', 'T']
    if components[2] not in bases:
        pass
    elif count_forward>=values.for_limit and count_reverse>=values.rev_limit and int(components[3])>=values.depth_lim: #If forward, reverse and total depths are enough
            f_cov.write(components[0]+'\t'+components[1]+'\t\t'+components[2]+'\t\t'+components[3]+'\t\t'+str(count_forward)+'\t\t'+str(count_reverse)+'\n') #Write to coverages file
            if f_vcf!=None:
                bases.remove(components[2])
                for variant in bases:
                    f_vcf.write(components[0]+'\t'+components[1]+'\t'+'.'+'\t'+components[2]+'\t'+variant+'\t.\t.\t') #Writes chromosome, position, id and reference base
                    f_vcf.write("DP="+components[3]) #Max depth?
                    f_vcf.write("\t") #Separates with tab to the next column
                    f_vcf.write("GT:AD:ADF:ADR\t0/1:"+components[3]+':'+str(count_forward)+':'+str(count_reverse)+'\n') #Total depth, forward depth and reverse depth
                return True
    return False

#Check that positions is indeed in bed regions, not outside them
def check_in_bedregion(values, components):
    for region in values.bed_regions[components[0]]: #balues.bed_regions is a dictionary, where keys are chromosomes, and values are lists with region tuples
        if region[0]<int(components[1])<=region[1]: #Region[0]=start in 0-base, components[1] real coordinate in 1-base, region[1] end region with 1-base
            return True
    return False #Position was not in area


def stream_line_by_line(stream, values, report, sample_id, bam_file):
    """Goes given stream through line by line.

    Writes positions, that are covered with given limits to the coverages file.
    In addition, creates all possible three mutations for these positions.
    Also, writes read depths to the CDF file in amounts and percents compared to the reference genome."""
    current_vcf_lines=-1
    index=0
    coverages=values.destination+'/'+separate_sample_id(values, bam_file)+"_coverages.txt" #Create coverages file
    f_cov = open(coverages, "w+")
    f_cov.write("Here are genomic positions from file "+bam_file+". Made "+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'\n')
    f_cov.write("Chr\tPos\tRef. base\tTotal depth\tForward depth\tReverse depth"+'\n')
    generated_vcf=list()
    for line in stream.stdout: #Reads stdout line by line
        components = line.decode('utf-8').split() #Decodes line values and separate them
        if len(components) != 6 or int(components[3])==0: #If line isn't about reads or there are 0 reads covering site, it is skipped
            continue #Moves to next line
        if values.orig_bed!='':
            if not check_in_bedregion(values, components):
                continue
        if current_vcf_lines==-1 or current_vcf_lines>values.lbuffer:
            if current_vcf_lines!=-1:
                f_vcf.close()
            new_vcf=values.vcf_location_sample+'/'+sample_id+"_generated_"+str(index)+".vcf"
            f_vcf=open(new_vcf, 'a+') #Name for that vcf file of that bam file
            generated_vcf.append(new_vcf) #Add coverages file's new vcf file to all vcf files, 'a')
            index+=1
            current_vcf_lines=0
        if write_coverages_and_vcf_files(components, f_cov, f_vcf, values):
            current_vcf_lines+=3 #Count line to total lines written to generated VCF
    f_cov.close()
    if f_vcf!=None:
        f_vcf.close()
    return generated_vcf #Returns total number of genomic positions and collection of numbers and their amounts.



def stream_command(values, bam_file):
    """Makes the stream command with given values and opens the stream"""
    if values.include!=' ': #If there are flags that should be included
        include=' -f '+values.include+' ' #Makes included flags to right format for the stream
    else:
        include=' '
    if values.head!='': #If there is a head argument
        head = "|head -n "+values.head #Make head to right format for the stream
    else:
        head=''
    if values.orig_bed!='': #If there is a given bed-file
        bed_command=' -L '+values.bed+' ' #Make bed command
    else:
        bed_command=''
    #if not reverse:
    stream = subprocess.Popen((samtools_location+' view '+values.other_args+' -b -F '+values.ignore+include+bed_command+bam_file+' | '+samtools_location+' mpileup \
      --ff 0 - -f '+values.reference+head), \
      shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) #Open stream, first runs bedtools if given, then pipes it to samtools view. Finaly pipes everything to mpileup

    print("Executing command \'"+samtools_location+' view '+values.other_args+' -b -F '+values.ignore+include+bed_command+bam_file+' | '+samtools_location+' mpileup -A -Q 0 \
    --ff 0 - -f '+values.reference+head+"'")

    return stream #Returns stream to further use


def go_through_bam(values, report, sample_id, bam_file):
    """Calls for stream_command-function, passes returned stream to stream_line_by_line function, counts genome size with whole_genome_length-function and returns numbers_tot and count"""
    stream=stream_command(values, bam_file) #Get stream from stream_command
    generated_vcf=stream_line_by_line(stream, values, report, sample_id, bam_file) #Get total numbers and collection of different amount of reads covering sites from function.
    return generated_vcf


def continue_permutation(values):
    """Continues from permutation skipping CDF and creation of large VCF files"""
    all_vcf=dict()
    for root, dirs, files in os.walk(values.gen_vcf_location):
        for file in files:
            if not file.endswith(".vcf") or "permutated" in file or "temp_mutation" in file:
                continue
            all_vcf[root+'/'+file]=separate_sample_id(values, root+'/'+file)
    generated_vcf_files=list()
    for file in values.bam: #Go through every given bam file
        sample_vcf_list=list()
        for vcf in all_vcf: #Go through every found VCF
            if all_vcf[vcf] in file: #If same sample id is found from bam and vcf, they are a match
                sample_vcf_list.append(vcf)
        if len(sample_vcf_list)==0:
            raise RuntimeError("Did not found VCF for file "+file+'.')
        generated_vcf_files.append(sample_vcf_list)
    vcf_files=values.vcf_file.split()
    for vcf_file, generated_vcf_file_list in zip(vcf_files, generated_vcf_files):
        with open(values.report, 'a') as f_r:
            f_r.write("Paired "+vcf_file+' and '+generated_vcf_file_list[0]+'. Total amount of found generated VCFs for file: '+str(len(generated_vcf_file_list))+'.\n')
    permutate_vcf(values, generated_vcf_files, values.report)



def make_bed_command(values):
    """Makes bed command for samtools view"""
    beds_splitted = values.orig_bed.split() #Separates different bed files
    i=0 #Iterator for different bed files
    timestamp=datetime.now().strftime("%Y%m%dT%H%M%S")
    final_bed=values.destination+'/temp_bed_sorted_merged_expanded_'+values.bed_prefix+timestamp+'.bed'
    values.bed_regions=dict() #Memorizes all the bed regions, so later non-bed regions wont be counted
    for bed in beds_splitted: #For there is bed file
        print("Executing command '"+bedtools_location+' sort -i '+bed+' > '+values.destination+'/temp_bed_sorted_'+values.bed_prefix+timestamp+'.bed\'')
        os.system(bedtools_location+' sort -i '+bed+' > '+values.destination+'/temp_bed_sorted_'+values.bed_prefix+timestamp+'.bed') #Sorts bed file
        print("Executing command '"+bedtools_location+' sort -i '+bed+' > '+values.destination+'/temp_bed_sorted_'+values.bed_prefix+timestamp+'.bed\'')
        os.system(bedtools_location+' merge -i temp_bed_sorted_'+values.bed_prefix+timestamp+'.bed > '+values.destination+'/temp_bed_sorted_merged'+str(i)+'_'+values.bed_prefix+timestamp+'.bed') #Merges bed file
        print("Removing "+values.destination+"/temp_bed_sorted file.")
        os.remove(values.destination+"/temp_bed_sorted_"+values.bed_prefix+timestamp+".bed") #Removes temp sorted bed file
        i+=1 #Increases index
    if i>1: #If there were more than 1 bed file
        j=1 #another index
        string=bedtools_location+" intersect -a "+values.destination+"/temp_bed_sorted_merged0_"+values.bed_prefix+timestamp+".bed -b " #Initialize intersect command with first bed file
        while j<i: #While there is a bedfile
            string+=values.destination+'/temp_bed_sorted_merged'+str(j)+'_'+values.bed_prefix+timestamp+'.bed ' #Add bed file to intersect command
            j+=1 #Increase index
        os.system(string+'> '+values.destination+'/temp_bed_intersect_'+values.bed_prefix+timestamp+'.bed') #Store output to single bed file
        os.system(bedtools_location+"  merge -i "+values.destination+"/temp_bed_intersect_"+values.bed_prefix+timestamp+".bed > "+values.destination+"/temp_bed_intersect_merged_"+values.bed_prefix+timestamp+".bed") #Merge output bed file
        os.remove(values.destination+"/temp_bed_intersect_"+values.bed_prefix+timestamp+".bed") #Remove original intersect file
        j=0 #Initialize index
        while j<i: #Remove all single merged bed files
            os.remove(values.destination+"/temp_bed_sorted_merged"+str(j)+"_"+values.bed_prefix+timestamp+".bed")
            j+=1
        os.rename(values.destination+'/temp_bed_intersect_merged_'+values.bed_prefix+timestamp+'.bed',values.destination+'/temp_bed_sorted_merged0_'+values.bed_prefix+timestamp+'.bed') #Rename intersect file to default file
    with open(values.destination+'/temp_bed_sorted_merged0_'+values.bed_prefix+timestamp+'.bed', 'r') as fr:
        with open(final_bed, 'w+') as fw:
            for line in fr:
                columns=line.split()
                start=int(columns[1])
                end=int(columns[2])
                start+=values.flank_upstream
                end+=values.flank_downstream
                columns[1]=str(start)
                columns[2]=str(end)
                for column in columns:
                    fw.write(column+'\t')
                if not columns[0] in values.bed_regions:
                    values.bed_regions[columns[0]]=list()
                values.bed_regions[columns[0]].append((start,end))
                i+=1
                fw.write('\n')
    os.system("rm "+values.destination+'/temp_bed_sorted_merged0_'+values.bed_prefix+timestamp+'.bed')
    values.bed=final_bed
    return values #Return values with bed file added
    #return ' -L temp_bed_sorted_merged0.bed ' #Return command


def create_gen_vcf_folder(values, bam_file):
    """Creates a folder for temporal generated VCF files."""
    sample_id=separate_sample_id(values, bam_file)
    if sample_id==None:
        raise RuntimeError("No sample_id for file "+bam_file)
    if not os.path.isdir(values.destination+'/generated_vcf'):
        os.mkdir(values.destination+'/generated_vcf')
    gen_vcf_location=values.destination+'/generated_vcf/'+sample_id
    if not os.path.isdir(values.destination+'/generated_vcf/'+sample_id):
        os.mkdir(gen_vcf_location)
    values.vcf_location_sample=gen_vcf_location
    return values, sample_id

def start_permutation(values, report):
    """Starts permutation from the beginning, counterpart for continue_permutation()."""
    if values.orig_bed!='':
        values=make_bed_command(values)
    generated_vcf_files=list() #Add all generated vcf files for vcf permutation
    for bam in values.bam: #Go through every file
        if not os.path.isfile(bam): #If bam does not exist
            raise RuntimeError("Could not find bam file "+bam+' from directory '+os.getcwd()+'.\n') #Raises error
        with open(report, 'a') as f:
            f.write("\nGenerating VCF files for bam file "+bam+'.\n')
        values, sample_id=create_gen_vcf_folder(values, bam)
        generated_vcf=go_through_bam(values, report, sample_id, bam) #Gets total amount of genomic positions in the file, makes CDF and returns coverages file
        generated_vcf_files.append(generated_vcf) #Add coverages file's new vcf file to all vcf files
    permutate_vcf(values, generated_vcf_files, report) #Creates new vcf file with last coverage file


def plot_cdf_function(cdf_file, values):
    """Uses R functions to plot the CDF function of read depths."""
    if values.bam_amount==1: #If there is only one file, plots different cumulative plot
        r_script=os.path.dirname(os.path.realpath(__file__))+'/r_scripts/mutation_load_coverages_onefile.R'
        if not os.path.isfile(r_script):
            r_script=pkg_resources.resource_filename(__name__, os.path.join("r_scripts", "mutation_load_coverages_onefile.R"))
        #r_script='/csc/mustjoki2/variant_move/epi_ski/hus_hematology/Timo/bachelor_thesis/mutation_permutation_tool/mutation_load_coverages_onefile.R'
    else: #There are multiple files
        r_script=os.path.dirname(os.path.realpath(__file__))+'/r_scripts/mutation_load_coverages_multiple_files.R'
        if not os.path.isfile(r_script):
            r_script=pkg_resources.resource_filename(__name__, os.path.join("r_scripts", "mutation_load_coverages_multiple_files.R"))
        #r_script='/csc/mustjoki2/variant_move/epi_ski/hus_hematology/Timo/bachelor_thesis/mutation_permutation_tool/mutation_load_coverages_multiple_files.R'
    print('Executing command \'Rscript '+r_script+' '+ \
            cdf_file+datetime.now().strftime(" "+values.destination+"/"+values.prefix+"_cdf_%Y%m%dT%H%M%S.jpg ") \
            + datetime.now().strftime(values.destination+"/"+values.prefix+"_cdf_zoomed_%Y%m%dT%H%M%S.jpg'"))
    os.system('Rscript '+r_script+' '+ \
            cdf_file+datetime.now().strftime(" "+values.destination+"/"+values.prefix+"_cdf_%Y%m%dT%H%M%S.jpg ")\
            + datetime.now().strftime(values.destination+"/"+values.prefix+"_cdf_zoomed_%Y%m%dT%H%M%S.jpg")) #Gives 2 to program so it nows what to plot


def write_csv_file(values, report, bam_file, sample_id, dp_file, csv_file, fnames, writer):
    """Writes CSV file of the read depths"""
    count=collections.Counter()
    tot_covered=0
    undersized_count=0 #Initializes how many numbers are below the limit
    tot_average_sum=0 #Initializes total sum of reads more or less than given limit
    tot_average_count=0 #Initializes how many genomic positions have reads more or less than given limit
    with open(dp_file, 'r') as fr:
        for line in fr:
            columns=line.strip().split()
            amount=int(columns[0])
            read_depth=int(columns[1])
            if read_depth==0:
                continue
            count[read_depth]=amount
            tot_covered+=amount
            if read_depth<values.limit:
                undersized_count+=1 #Amount of numbers below the limit increasees
            if values.lower and read_depth<values.limit or not values.lower and read_depth>values.limit: #If number is above or below (depending on the user) from given limit
                tot_average_sum+=read_depth*amount #Amount of reads covering sites is added to total sum of numbers differing from the limit
                tot_average_count+=amount #Add position to differing positions
    if tot_covered==0: #If there were no reads covering site and ignore=False (We are interested in the data)
        with open(report,'a') as f: #Open program report
            f.write("No reads covering sites were found.\n")
    else: #There were reads over 0 found, information is written to the report
        write_report_averages_and_limits(report, values.limit, undersized_count, tot_covered, tot_average_count, tot_average_sum, values.lower) #Writes to the report with function
    tot_genomic_positions=get_genome_size(values, report, bam_file, tot_covered)
    if values.number: #If user gave number that other reads covering site amounts should be compared to
        compare_one_number(bam_file, tot_covered, count, values.more, values.number, report) #Compare other numbers to that one
    else: #User wants traditional CDF-function
        cdf_function(values, tot_covered, count, report, writer, fnames, tot_genomic_positions, bam_file)


def get_genome_size(values, report, bam_file, tot_covered):
    """Gets the size of the whole genome and writes the report."""
    with open(report,'a') as f: #Opens program report for writing
        if values.orig_bed=='': #Doesn't count whole genome length if bed was given
            genome_size=whole_genome_length(bam_file) #Get size of the whole reference genome with function
            f.write("The total length of the genome is "+str(genome_size)+" base pairs.\n") #Write how large the total genome is
        else:
            genome_size=bed_genome_length(bam_file)
            f.write("The total length of the BED file is "+str(genome_size)+" base pairs.\n") #Write how large the total genome is
        if genome_size>0:
            f.write(str(genome_size-tot_covered)+" genomic positions ("+str(100*(genome_size-tot_covered)/genome_size)+"%) were not covered with given filters.\n") #Write how many genomic positions were covered with file
    return genome_size

def create_cdf_writer(values):
    """Creates csv file and writer to it."""
    currentDT=datetime.now()
    csv_file=values.destination+'/'+values.prefix+currentDT.strftime("_cdf_%Y%m%dT%H%M%S.csv")
    csv_stream = open(csv_file, 'w+') #Open csv file for writing
    fnames=['bam_file', 'number_of_reads', 'amount_of_number', 'cumulative_sum', 'percent', 'interval'] #Make column names
    writer = csv.DictWriter(csv_stream, fieldnames=fnames) #Writer for csv writing
    writer.writeheader() #Write csv header
    return csv_file, csv_stream, fnames, writer


def make_cdf_plot(values, report):
    """Makes CDF plot of the given bam files and writes the CDF to the report."""
    csv_file, csv_stream, fnames, writer = create_cdf_writer(values)
    if values.orig_bed!='':
        values=make_bed_command(values)
    for bam_file in values.bam:
        with open(report, 'a') as f:
            f.write("\nCounting reads covering sites in bam file "+bam_file+'.\n')
        sample_id=separate_sample_id(values, bam_file)
        prefix=values.destination+'/'+values.prefix+datetime.now().strftime("_%Y%m%dT%H%M%S_")+sample_id
        bed_command=''
        if values.orig_bed!='':
            bed_command="-L "+values.bed+' '
        if values.include!=' ': #If there are flags that should be included
            include=' -f '+values.include+' ' #Makes included flags to right format for the stream
        else:
            include=' '
        if values.head!='': #If there is a head argument
            head = "|head -n "+values.head #Make head to right format for the stream
        else:
            head=''
        print("Executing command '"+samtools_location+' view '+values.other_args+' -b -F '+values.ignore+include+bed_command+bam_file+' | '+samtools_location+' mpileup \
        --ff 0 - -f '+values.reference+head+' | cut -f 4  > '+prefix+'_depths.txt\'')
        os.system(samtools_location+' view '+values.other_args+' -b -F '+values.ignore+include+bed_command+bam_file+' | '+samtools_location+' mpileup \
        --ff 0 - -f '+values.reference+head+' | cut -f 4  > '+prefix+'_depths.txt')
        print("Executing command 'sort -n "+prefix+'_depths.txt | uniq -c > '+prefix+'_read_counted_depths.txt\'')
        os.system("sort -n "+prefix+'_depths.txt | uniq -c > '+prefix+'_read_counted_depths.txt')
        write_csv_file(values, report, bam_file, sample_id, prefix+'_read_counted_depths.txt', csv_file, fnames, writer)
    csv_stream.close()
    plot_cdf_function(csv_file, values)
    if not values.keep_temp_files:
        os.system("rm "+prefix+'_depths.txt')
        os.system("rm "+prefix+'_read_counted_depths.txt')
        os.system("rm "+csv_file)

def get_file_from_path(file):
    """Separates file name from the whole file path based on the last '/' character."""
    pattern=re.compile("/[^/]*$")
    return pattern.search(file).group(0)[1:]

def separate_sample_id(values, file):
    """Separates sample_id or part of the file name for file naming."""
    if values.regex_sampleid:
        return regex_patterns.main(file)
    else:
        file_path_removed=get_file_from_path(file)
        return file_path_removed[values.name_start_index:values.name_end_index]


def find_sample_ids(values):
    """Test function on how the program separates sample ids or parts of the filename before execution."""
    sample_ids=list()
    for file in values.bam:
        sample_id=separate_sample_id(values, file)
        if sample_id in sample_ids:
            print("Found the same sample id ("+sample_id+") multiple times.")
        elif sample_id==None:
            print("Sample id was None for file "+file)
        else:
            print("For file "+file+" sample id was "+sample_id)
        sample_ids.append(sample_id)
    exit()


def remove_directories(values):
    """Removes all the temporal directories."""
    if os.path.isdir(values.destination+'/temp_perm_mutations'):
        os.system("rm -r "+values.destination+'/temp_perm_mutations')
    if os.path.isdir(values.destination+'/gen_vcf_annotations'):
        os.system("rm -r "+values.destination+'/gen_vcf_annotations')
    if os.path.isdir(values.destination+'/generated_vcf'):
        os.system("rm -r "+values.destination+'/generated_vcf')
    if os.path.isdir(values.destination+'/ref_vcf_anno'):
        os.system("rm -r "+values.destination+'/ref_vcf_anno')
    if hasattr(values, "bed"):
        os.system("rm "+values.bed)

def get_all_bam_files(directory):
    """Searches all bam files from the given directory and returns list of them."""
    if not os.path.isdir(directory): #Checks first that directory even exists
        optparser.error("Could not find directory "+directory+' from directory '+os.getcwd()+'.\n') #Directory was not found
    list_of_files=list() #Initializes list for bam files
    for root, dirs, files in os.walk(directory, topdown=True): #Goes through every directory, subdirectory and file in the starting_directory
        for file in files: #Every file in the directory
            if file.endswith('.bam'):
                list_of_files.append(root+'/'+file) #Adds file and its root to list
    return list_of_files #Returns all bam files


def check_optparsing(optparser,values):
    """Checks that the optparsing passed without errors."""
    if values.bam==None and values.directory==None: #Checks that either file or directory is given
        optparser.error("Give file (-b /path/to/file) or directory (-d path/to/directory)") #Raises error if not
    if values.directory!=None: #If directory was given
        values.bam=get_all_bam_files(values.directory) #Searches all bam files from the directory
    else: #Directory was not given
        values.bam=values.bam.split() #Splits file argument in case there were multiple files given
    if values.get_id_only:
        return values
    if values.destination==None:
        optparser.error("Give destination directory for permutations, report etc.") #Raises error if not
    if (not values.skip_perm and not values.cont_perm) and values.vcf_file==None:
        optparser.error("Give VCF-files corresponding to the BAM-files (--vcf_file \"path/to/file1.vcf path/to/file2.vcf\" or skip permutation by --skip_perm.")
    if not os.path.isdir(values.destination): #Checks that destination directory exists
        optparser.error("Could not find directory "+values.destination+' from directory '+os.getcwd()+'.\n') #Directory was not found
    if values.cont_perm:
        if values.gen_vcf_location==None:
            optparser.error("Give directory containing generated VCF files (--gen_vcf_location path/to/directory)")
        if not os.path.isdir(values.gen_vcf_location):
            optparser.error("Could not find directory "+values.gen_vcf_location+' from directory '+os.getcwd()+'.\n') #Directory was not found
        if values.report==None:
            optparser.error("Give report file (--report path/to/file.txt)")
        if not os.path.isfile(values.report):
            optparser.error("Could not find file "+values.report+' from directory '+os.getcwd()+'.\n') #Directory was not found
        if values.skip_perm:
            optparser.error("Cant continue permutation (--continue) and skip it (--skip_permutation) at the same time.")
    if values.vcf_file!=None:
        if values.skip_perm:
            optparser.error("Do not give VCF files if you want to skip permutation.")
        for file in values.vcf_file.split():
            assert os.path.isfile(file), "Could not find file "+file+" from directory"+os.getcwd()+'.\n'
    if len(values.bam)>1: #There are multiple files
        values.bam_amount=2 #Argument so R program knows later how to plot the results
    else: #Only 1 file was given
        values.bam_amount=1 #Argument so R program knows later how to plot the results
    if not os.path.isdir(values.destination+'/'+"mutation_load_permutations"):
        try:
            os.mkdir(values.destination+'/'+"mutation_load_permutations")
        except FileExistsError:
            pass
    values.plot_intervals=values.plot_intervals.split(',')
    for index, interval in enumerate(values.plot_intervals):
        values.plot_intervals[index]=interval.strip()
        assert interval.isnumeric(), "Interval "+interval+" was not numeric. Give intervals separated by dots (\"int1,int2,int3\")"
    values.destination=values.destination+'/'+"mutation_load_permutations"
    return values


def optparsing():
    """Optparses user commands"""
    optparser = optparse.OptionParser(usage= "python3 %prog --bam <example.bam> --vcf_file <example.vcf> --destination <example/dir> "+
    "table_annovar </path/to/table_annovar.pl> --annovar </path/to/humandb> [options]\n"
    "Counts CDF of read depths for a given bam file. If vcf file is given, permutates random mutations from bam file with the same occurence as in "
    "the given vcf file. Program creates directory for output to the given destination directory.") #Make header for help page
    #Add options to parser
    group = optparse.OptionGroup(optparser, "Input options",
                    "Define your input files and directories.")
    group.add_option("-b", "--bam", dest="bam", help="Bam file(s) that will be read (-b /path/to/file).")
    group.add_option("--vcf_file", dest="vcf_file", help="VCF file(s) for permutation given in the same order as the corresponding bam files (--vcf_file /path/to/file.vcf).")
    group.add_option("-d", "--directory", dest="directory", help="If you want the program to run through all bam files in certain directory (-d /path/to/directory).")
    optparser.add_option_group(group)

    group = optparse.OptionGroup(optparser, "Output options",
                    "Define output directory and if you want to keep all temporal files for debugging.")
    group.add_option("--destination", dest="destination", help="Destination for cdf file, report, permutations etc. (--destination /path/to/directory).")
    group.add_option("--plot_cdf", dest="plot_cdf", action="store_true", default=False, help="If you do not want CDF plot of read depths. Default: %default.")
    group.add_option("--lbuffer", dest="lbuffer", default=821600, type="int", help="Maximum number of lines per generated vcf_file to save memory. Default is %default, which takes 3G memory with ANNOVAR.")
    group.add_option("--keep_temp_files", dest="keep_temp_files",action="store_true", default=False, help="If you want to keep temporal anno files, generated VCF and temporal mutation files for debugging. Set True, if you have parallel runs to the same destination. Default: %default.")
    optparser.add_option_group(group)

    group = optparse.OptionGroup(optparser, "Permutation options",
                    "With these options you can for example decide which mutations you want to include and keep count on permutation.")
    group.add_option("--perm_amount", dest="perm_amount", type="int", default=100, help="How many permutations you want for every bam, default: %default.")
    group.add_option("--skip_permutation", dest="skip_perm",action="store_true", default=False, help="If you do not want permutations.")
    group.add_option("--no_vcf_filter", dest="no_vcf_filter",action="store_true", default=False, help="If you do not want to filter given VCF based on BAM read depths.")
    group.add_option("--skip_nonexon", dest="skip_nonexon",action="store_true", default=False, help="If you want to skip all non exon mutations in permutation. Can be used without --separate_regions.")
    group.add_option("--separate_regions", dest="separate_regions",action="store_true", default=False, help="If you want to permutate same amount of mutations in same regions.")
    group.add_option("--separate_syn", dest="separate_syn",action="store_true", default=False, help="If you want same amount of synonymous and nonsynonymous mutations as in input VCF. Does not work without --separate_regions.")
    optparser.add_option_group(group)

    group = optparse.OptionGroup(optparser, "Naming policy",
                    "Naming options for files and sample names in coverages plot.")
    group.add_option("--prefix", dest="prefix", default="mutation_load", help="Prefix for you files.")
    group.add_option("--name_start_index", dest="name_start_index", default=0, type="int", help="Starting index of BAM file when creating name for plot and permutation files. Default: %default.")
    group.add_option("--name_end_index", dest="name_end_index", default=10, type="int", help="Ending index of BAM file when creating name for plot and permutation files. Default: %default.")
    group.add_option("--get_id_only", dest="get_id_only", action="store_true", default=False, help="If you want to check how program identifies the sample ids.")
    group.add_option("--regex_sampleid", dest="regex_sampleid", action="store_true", default=False, help="If you want to use modified regex_patterns.py to find sample ids for files. Default: %default.")
    optparser.add_option_group(group)


    group = optparse.OptionGroup(optparser, "Trimming and samtools options",
                    "With these options you can choose reference fasta file and exclude for example reads with certain bitflags or too little read depth.")
    group.add_option("--depth_lim", dest="depth_lim", default=10, type="int", help="Minimum depth to reads for coverages  and permutation files, default: %default.")
    group.add_option("--rev_limit", dest="rev_limit", default=3, type="int", help="Minimum reverse depth for coverages and permutation files, default: %default.")
    group.add_option("--for_limit", dest="for_limit", default=3, type="int", help="Minimum forward depth for coverages and permutation files, default: %default.")
    group.add_option("--reference", dest="reference", default='/csc/mustjoki2/bioinformatics/gatk/reference_data/GRCh38/GRCh38.p12/fasta/Homo_sapiens.GRCh38.dna.primary_assembly.fa', help="Reference fasta file (--reference /path/to/reference). Default: %default.") #/fs/vault/pipelines/gatk/data/homo_sapiens_v94/Homo_sapiens.GRCh38.dna.primary_assembly.fa
    group.add_option("-L", "--bed_file", dest="orig_bed", default='', help="If you want to limit area to certain certain region with bedfile, write -L BEDFILE.")
    group.add_option("--flank_upstream", dest="flank_upstream", default=0, type="int", help="How much you want to expand BED file coordinates to upstream. Default: %default.")
    group.add_option("--flank_downstream", dest="flank_downstream", default=0, type="int", help="How much you want to expand BED file coordinates to downstream. Default: %default.")
    group.add_option("-F", dest="ignore", default='0', help="Bit flags you want to ignore.")
    group.add_option("-f", dest="include", default=' ', help="Bit flags you want to be set.")
    group.add_option("--headn", dest="head", default='', help="If you want to limit area to certain size, write for example '-headn 10000'.")
    group.add_option("--other", dest="other_args", default='', help="If you want to use other samtools view -arguments, write for example '-- other \"-q 10 -m 3\"'.")
    optparser.add_option_group(group)

    group = optparse.OptionGroup(optparser, "CDF options",
                    "With these options you can decide information you want from CDF part")
    group.add_option("-p", "--percent_interval", dest="percent_interval", type="int", default=5, help="Percent with what distance the CDF-function will be at least printed, default: %default. For example '-p 5'.")
    group.add_option("--plot_intervals", dest="plot_intervals", default="1,5,7,10,20,30,40,50,75,100,150,200,300,400,500", help="Read depth intervals for the CDF plot.")
    group.add_option("-r", "--reverse", action="store_true", dest="reverse",  default=False, help="If you want to count CDF from largest to smallest, type -r. Default: %default.")
    group.add_option("-n", "--number", dest="number", type="int", help="If you only want to know how many numbers have less reads than given number (or more when compared to -m).")
    group.add_option("-m", "--more", dest="more", default=False, action="store_true", help="If you want to know how many genomic positions have more reads than given number.")
    group.add_option("-l", "--limit", dest="limit",type="int", default=1, help="Program writes how many genomic positions have more reads covering site than given limit. Default: %default.")
    group.add_option("--lower", dest="lower",action="store_true", default=False, help="If you want to know average of reads below the limit, default is average of reads exceeding the limit.")
    optparser.add_option_group(group)

    group = optparse.OptionGroup(optparser, "ANNOVAR options")
    group.add_option("--table_annovar", dest="table_annovar", default='/csc/mustjoki2/bioinformatics/gatk/gatk_process_fimm_tools/annovar-2015-03-22/table_annovar.pl', help="Location of table_annovar.pl. Default: %default.") #/fs/vault/pipelines/rnaseq/bin/2.7.0/annovar/table_annovar.pl
    group.add_option("--annovar", dest="annovar", default='/csc/mustjoki2/bioinformatics/gatk/gatk_process_fimm_tools/annovar-2015-03-22/humandb_060418', help="Location of ANNVOAR. Default: %default.") #/fs/vault/pipelines/rnaseq/bin/2.7.0/annovar/humandb_060418/
    group.add_option("--buildver", dest="buildver", default='hg38', help="Buildver version, default: %default.")
    optparser.add_option_group(group)

    group = optparse.OptionGroup(optparser, "Continue from permutation",
                    "If program crashed and you want to continue from the permutation, skipping the first part (CDF, generating VCFs containing all possible mutations...)."
                    " In addition, you need to specify bam files (-s path/to/file), original vcf files (--vcf_file ...), annovar, and permutation options.")
    group.add_option("--continue", dest="cont_perm", action="store_true", default=False, help="If you want to skip the first part.")
    group.add_option("--gen_vcf_location", dest="gen_vcf_location", help="Directory containing generated large VCF files containing all possible mutations for every genomic position from bam files (recursive, subdirectories don't matter).")
    group.add_option("--report", dest="report", help="Original report from earlier run.")
    optparser.add_option_group(group)

    group = optparse.OptionGroup(optparser, "Other options")
    group.add_option("--bed_prefix", dest="bed_prefix", default="", help="Prefix for temporal bed files (for debugging or for parallel runs).")
    optparser.add_option_group(group)

    (values, keys) = optparser.parse_args() #Separate values and keys from parser
    values=check_optparsing(optparser,values)
    return values #Returns optparser values


def main():
    """Depending on the settings, can prints sample ids, start or continue permutation and removes all temporal directories made for the program."""
    values = optparsing() #Function makes the optparsing
    if values.cont_perm:
        continue_permutation(values)
    else:
        report=make_report(values)
    if values.get_id_only:
        find_sample_ids(values)
    if values.plot_cdf:
        start_time = time.time()
        make_cdf_plot(values, report)
        print("Plotting took "+str(time.time() - start_time)+" seconds") #Prints consumed time
    if not values.skip_perm:
        start_time = time.time()
        start_permutation(values, report)
        print("Permutation took "+str(time.time() - start_time)+" seconds") #Prints consumed time
    if not values.keep_temp_files:
        remove_directories(values)


if __name__=='__main__':
    start_time = time.time()
    main()
    print("Program took "+str(time.time() - start_time)+" seconds") #Prints consumed time
