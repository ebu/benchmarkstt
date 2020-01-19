#!/usr/bin/env python
# coding: utf-8

# check the name entity
from copy import deepcopy
import re
import benchmarkstt


# find the position of one NE 
# a NE can contains more than one word
def find_pattern(search_list, named_entity):
    entity = ''.join(named_entity).split(' ')
    le = len(entity)
    cursor = 0
    idx_found = []
    for idx, elt in enumerate(search_list):
        if elt == entity[cursor]:
            cursor += 1
            if cursor == le:
                idx_found.append([idx for idx in range(idx-le+1, idx-le+1+le)])
                cursor = 0
        else:
            cursor = 0
    return(idx_found)

# replace all the words that are not a NE by 'x' 
def generate_list_x(list_parsed, named_entities, replacement = 'x'):

    list_x = [replacement]*len(list_parsed)
    index_entities = []

    # detect the index of the entities
    for entity in named_entities:
        index_entity = find_pattern(list_parsed, entity)
        index_entities.extend(index_entity)

    # flatten
    index_entities = [item for sublist in index_entities for item in sublist]

    # just copy-past the entity found in the list with x
    for k in index_entities:
        list_x[k] = list_parsed[k]

    return(list_x)

#generate a list containing the detected NEs in list_parsed
def generate_list_ne(list_parsed, named_entities):

    list_ne = []
    index_entities = []

    for entity in named_entities:
        index_entity = find_pattern(list_parsed,entity)
        index_entities.extend(index_entity)

    # sort on the position of the first part of the entity
    index_entities.sort(key=lambda l: l[0])

    # copy-past the entity found in the list with x
    for k_list in index_entities:
        list_ne.append(' '.join(list_parsed[k_list[0]:k_list[-1]+1]))

    return(list_ne)

# computes the NEER 
def compute_neer(named_entities, list_hypothesis_ne, list_reference_ne):
    neer = {}
    neer_av = 0
    for entity in named_entities:
        count_hypothesis = list_hypothesis_ne.count(entity)
        count_ref = list_reference_ne.count(entity)
        neer[entity] = abs(count_ref-count_hypothesis)/count_ref
        # accumulate the distance per entity
        neer_av += count_ref * neer[entity]
    neer_av = neer_av / len(list_reference_ne)
    neer['av_neer'] = neer_av
    return(neer)

def main():

    # ### Named entities definition
    
    named_entities = ["minister","theresa may"]
    
    
    # ### Generates the files and lists for testing
    
    hypothesis_file = open("qt_kaldi_hypothesis_normalized.txt")
    hypothesis_txt = hypothesis_file.read()
    hypothesis_file.close()  
    reference_file = open("qt_reference_normalized.txt")
    reference_txt = reference_file.read()
    reference_file.close()  
    
    
    # clean-up the reference files : erease spaces to make it clearer
    reference_txt = reference_txt.replace('\n', ' ').replace('\r', '')
    # supress multi space could be added as a regex
    reference_txt = re.sub('\s+',' ', reference_txt)
    
    #generate the lists corresponding to the files
    hypothesis_list_full = hypothesis_txt.split(' ')
    reference_list_full = reference_txt.split(' ')
    
    hypothesis_list = hypothesis_list_full[0:200]
    reference_list = reference_list_full[0:200]
    
    #replace all the words of the list by x except named entities 
    list_hypothesis_x = generate_list_x(hypothesis_list,named_entities)
    list_reference_x = generate_list_x(reference_list,named_entities)
    
    # extact the named entities
    list_hypothesis_ne = generate_list_ne(hypothesis_list,named_entities)
    list_reference_ne = generate_list_ne(reference_list,named_entities)
    
    
    # ### Method 1 to compute WER from files with NE and x
    print('')
    print('=======================================')
    print('Method 1 to compute WER from files with NE and x')
    print('=======================================')

    # compute the wer with the published method
    #generate the str ...
    str_hypothesis_x = ' '.join(list_hypothesis_x)
    str_reference_x = ' '.join(list_reference_x)
    
    text_file = open("reference_x.txt", "w")
    text_file.write(str_reference_x)
    text_file.close()
    
    text_file = open("hypothesis_x.txt", "w")
    text_file.write(str_hypothesis_x)
    text_file.close()
    
    print('=======================================')
    print('reference')
    print('=======================================')
    print(str_reference_x)
    print('')
    print('=======================================')
    print('hypothesis')
    print('=======================================')
    print(str_hypothesis_x)
    print('')
    print('')
    
    get_ipython().system('benchmarkstt --reference reference_x.txt --hypothesis hypothesis_x.txt --wer --diffcounts')
    
    
    # ### Methode 2 computes the NEER
    
    print('Check the alinment of the extracted entities')
    print('============================================')
    print('')
    for idx,elt  in enumerate(list_reference_ne) : 
        try :
            print('{1} ------ {1}'.format(list_hypothesis_ne[idx], elt))
        except:
            print('{1} ------ {1}'.format('xx', elt))
    
    
    # ### Insert errors : just to see the effect on NEER
    
    list_hypothesis_ne_error = deepcopy(list_hypothesis_ne)
    list_hypothesis_ne_error[1] = 'minister'
    list_hypothesis_ne_error.pop()
    
#    print('======================================')
#    print('Extracted NE from reference file')
#    print('======================================')
#    print(list_reference_ne)
#    print('')
#    print('======================================')
#    print('Extracted NE from hypothesis file with errors')
#    print('======================================')
#    print(list_hypothesis_ne_error)
    
    
    # the wer takes into account the position of the named entity 
    # wer on list of ne
    
    str_hypothesis_ne = ' '.join(list_hypothesis_ne_error)
    str_reference_ne = ' '.join(list_reference_ne)
    
    print('======================================')
    print('Extracted NE from reference file')
    print('======================================')
    print(str_reference_ne)
    print('')
    print('======================================')
    print('Extracted NE from hypothesis file with errors')
    print('======================================')
    print(str_hypothesis_ne)
    print('')
    
    # saves the files
    file = open("hypothesis_ne.txt", "w")  
    file.write(str_hypothesis_ne)
    file.close()
    file = open("reference_ne.txt", "w")
    file.write(str_reference_ne)
    file.close()
    
    
    get_ipython().system('benchmarkstt --reference reference_ne.txt --hypothesis hypothesis_ne.txt --wer --diffcounts')
    
    
    wer_ne = compute_neer ( named_entities, list_hypothesis_ne_error, list_reference_ne )
    print('======================================')
    print('NEER computes considering bag of words')
    print('======================================')
    print(wer_ne)

  
if __name__== "__main__":
  main()



