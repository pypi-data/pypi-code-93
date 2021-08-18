import sys
    
def loadingBar(count,total,size):
    percent = float(count)/float(total)*100
    sys.stdout.write("\r" + str(int(count)).rjust(3,'0')+"/"+str(int(total)).rjust(3,'0') + ' [' + '='*int(percent/10)*size + ' '*(10-int(percent/10))*size + ']') 
    
def pangenome_loadingBar(count,total,size,pangenome_size):
    percent = float(count)/float(total)*100
    sys.stdout.write("\r" + "Elements: " + str(int(pangenome_size)) + ". Progress: " +  str(int(count)).rjust(3,'0')+"/"+str(int(total)).rjust(3,'0') + ' |' + '='*int(percent/10)*size + ' '*(10-int(percent/10))*size + '|') 
    
def core(genome_list, index, sim_threshold, freq_treshold, len_margin):

    genome = []
    genome_elements = []
      
    print("")
    print("B U I L D I N G  C O R E  P A N G E N O M E")
    print("_________________________________________________")
    print(" ")
        
    print("Loading genomes")
    for i in range(0, len(genome_list)):
        
        loadingBar(i+1,len(genome_list),3)
        
        element_list = open('alexandria/genome_library/'+str(genome_list[i])+'seq.txt').read().splitlines()
        elements = len(element_list)
        genome.append(element_list)
        genome_elements.append(elements)

    print("")
    print("Selecting genome with smaller number of element candidates")
    
    found = False
    
    too_short = 0
    
    while not found:
        
       ref_genome_index = genome_elements.index(min(genome_elements))
    
       if min(genome_elements) < 4000:      
           
           genome.pop(ref_genome_index)
           genome_elements.pop(ref_genome_index)
           too_short += 1 
          
       else:
           
           found = True
    
    ref_genome = genome[ref_genome_index]
    pangenome = ref_genome
    
    print(str(too_short), "genomes had too few elements and were deleted")
    print("The reference minimal genome presents",str(len(ref_genome)),"elements")
    print(" ")
    print("Removing reference genome from collection")
    
    genome.pop(ref_genome_index)
    genome_elements.pop(ref_genome_index)
    
    print(" ")
    print("Current elements found in the core pangenome:", len(ref_genome))            
    print(" ")
    print("A N A L Y S I N G   G E N O M E S")
    print("-------------------------------------------------")
    print(" ")
            
    for i in range(0, len(genome)):

        pangenome_loadingBar(i+1,len(genome),3,len(pangenome))
        
        if len(ref_genome) > 0:
        
            ref_genome = pangenome.copy()
            
            pangenome = []

            lengths = [[len(element) for element in ref_genome],[len(element) for element in genome[i]]]
            
            trials = 0
                
            for length in lengths[0]:
                
                found = False
                
                trials += 1
                
                if length in lengths[1]:
       
                    index_ref = lengths[0].index(length)
                    index_gen = lengths[1].index(length)
                    
                    seq1 = ref_genome[index_ref]
                    seq2 = genome[i][index_gen]
                    
                    match = sum(c1!=c2 for c1,c2 in zip(seq1,seq2))
                                                          
                    similarity = (match/length)*100
                    
                    if similarity > sim_threshold:
                        
                        found = True
                        
                        lengths[1].pop(index_gen)
                    
                if not found:
                          
                    gene_margin = int(length*len_margin)
                    
                    for j in range(0, gene_margin):
                                                    
                        if length+j in lengths[1]:
       
                            index_ref = lengths[0].index(length)
                            index_gen = lengths[1].index(length+j)
                    
                            seq1 = ref_genome[index_ref]
                            seq2 = genome[i][index_gen]
                    
                            match = sum(c1!=c2 for c1,c2 in zip(seq1,seq2))
                                                          
                            similarity = (match/length)*100
                    
                            if similarity > sim_threshold:
                        
                                found = True
                                
                                lengths[1].pop(index_gen)
                                
                                break
                        
                        if length-j in lengths[1]:
       
                            index_ref = lengths[0].index(length)
                            index_gen = lengths[1].index(length-j)
                    
                            seq1 = ref_genome[index_ref]
                            seq2 = genome[i][index_gen]
                    
                            match = sum(c1!=c2 for c1,c2 in zip(seq1,seq2))
                                                          
                            similarity = (match/length)*100
                    
                            if similarity > sim_threshold:
                        
                                found = True
                                
                                lengths[1].pop(index_gen)
                                
                                break
           
                                
                if found: 
                    
                    pangenome.append(seq1)
                        
                        
            if abs(len(pangenome)-len(ref_genome)) > 4000:
                
                print(" ")
                print("WARNING: Aberrant genome found, skipping")
                
                pangenome = ref_genome.copy()
   
        else: 
                
            print(" ")
            print("ERROR: No core shared elements found")
            break
    
    if len(ref_genome) > 0:
       
        print("")
        print("Pangenome built!")

    return pangenome


def subtraction(pangenome_A, pangenome_B, sim_threshold, margin):
    
    print("")
    print("S U B T R A C T I N G  P A N G E N O M E")
    print("___________________________________________")
    print(" ")
    
    print("Elements in pangenome A",str(len(pangenome_A)))
    print("Elements in pangenome B",str(len(pangenome_B)))
    
    differential_pangenome = pangenome_A.copy()
    
    lengths = [[len(element) for element in pangenome_A],[len(element) for element in pangenome_B]]
    
    trials = 0
        
    for length in lengths[0]:
        
        found = False
        
        trials += 1

        pangenome_loadingBar(trials,len(pangenome_A),3,len(differential_pangenome))
        
        if length in lengths[1]:
       
            index_ref = lengths[0].index(length)
            index_gen = lengths[1].index(length)
            
            seq1 = pangenome_A[index_ref]
            seq2 = pangenome_B[index_gen]
            
            match = sum(c1!=c2 for c1,c2 in zip(seq1,seq2))
                                                  
            similarity = (match/length)*100
            
            if similarity > sim_threshold:
                
                found = True
            
        if not found:
                  
            gene_margin = int(length*margin)
            
            for j in range(0, gene_margin):
                                            
                if length+j in lengths[1]:

                    index_ref = lengths[0].index(length)
                    index_gen = lengths[1].index(length+j)
            
                    seq1 = pangenome_A[index_ref]
                    seq2 = pangenome_B[index_gen]
            
                    match = sum(c1!=c2 for c1,c2 in zip(seq1,seq2))
                                                  
                    similarity = (match/length)*100
            
                    if similarity > sim_threshold:
                
                        found = True
                        
                        lengths[1].pop(index_gen)
                        
                        break
                
                if length-j in lengths[1]:

                    index_ref = lengths[0].index(length)
                    index_gen = lengths[1].index(length-j)
            
                    seq1 = pangenome_A[index_ref]
                    seq2 = pangenome_B[index_gen]
            
                    match = sum(c1!=c2 for c1,c2 in zip(seq1,seq2))
                                                  
                    similarity = (match/length)*100
            
                    if similarity > sim_threshold:
                
                        found = True
                        
                        lengths[1].pop(index_gen)
                        
                        break
   
                                
        if found: 
            
             differential_pangenome.remove(seq1)             
       
    print("")
    print("Pangenome subtraction completed!")

    return differential_pangenome

    