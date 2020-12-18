import difflib
import os
import json
import re


#A class of the preprocessing needed to compute the metrics
class Preprocess:

    def __init__(self):
        self

    # parametre : transcript, labels=[]
    def get_verb_list(self,transcript):
        verb_list = []
        for word in transcript["words"]:
            if 'pos' in word and word['pos'] in ['VERB','AUX'] and ('entity_type' not in word or word['entity_type'][0] == ''):
                param_dict = {}
                param_dict["verb"] = word['content']
                param_dict["lemma"] = word['lemma']
                tags = re.sub(word['pos'] + "__", "", word['tag'])

                tags_param = tags.split("|")
                for param in tags_param:
                    param_name = param.split("=")[0]
                    param_value = param.split("=")[1]
                    param_dict[param_name] = param_value

                param_dict['start_time'] = word['startTime']
                param_dict['end_time'] = word['endTime']
                
                verb_list.append(param_dict)

        return verb_list

    # parametre : transcript, labels=[]
    def get_named_entities(self,transcript, labels=[]):
        ne_list = []
        if len(labels) == 0 :

            ne_list = [ word['content'] for word in transcript['words'] if ('entity_type' in word and word['entity_type'][0] != "") ]
        else :
            ne_list = [ word['content'] for word in transcript['words'] if ('entity_type' in word and word['entity_type'][0] in labels) ]
        ne_list_result = sorted(list(set(ne_list)))
        return ne_list_result




    #Method return a normalized forme of ref and res transcript with corrected spaces, \n and punctuations
    def normalized_text(self,transcript_ref,transcript_res):
        # clean-up the reference files : erease spaces to make it clearer
        # split punctuation when here is no space between words and punctuations
        # added the fact that we lower every word to avoid unwanted mismatch
        reference_txt = transcript_ref["text"].replace('\n', ' ').replace('\r', '')
        reference_txt = re.sub('([.,;!?()\'])', r' \1 ', reference_txt)
        reference_txt = re.sub('\s{2,}', ' ', reference_txt)
        # supress multi space could be added as a regex
        reference_txt = re.sub('\s+', ' ', reference_txt)#.lower()


        hypothesis_txt=transcript_res["text"]
        hypothesis_txt = re.sub('([.,;!?()\'])', r' \1 ', hypothesis_txt)
        hypothesis_txt = re.sub('\s{2,}', ' ', hypothesis_txt)
        hypothesis_txt = re.sub('\s+', ' ', hypothesis_txt)#.lower()


        # generate the lists corresponding to the files
        hypothesis_list_full = hypothesis_txt.split(' ')
        reference_list_full = reference_txt.split(' ')

        # delete last element if it's an empty string '' due du punctuation split
        if(hypothesis_list_full[-1] == ''):
            hypothesis_list_full=hypothesis_list_full[:len(hypothesis_list_full)-1]
        if(reference_list_full[-1] == ''):
            reference_list_full=reference_list_full[:len(reference_list_full)-1]

        return hypothesis_list_full,reference_list_full

    #Method that finds the position of one NE
    def find_pattern(self,search_list, named_entity):

        # a NE can contains more than one word
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


    #Methode that generate a list containing the detected NEs in list_parsed
    def generate_list_ne(self,list_parsed, named_entities):
        list_ne = []
        index_entities = []

        for entity in named_entities:
            index_entity = self.find_pattern(list_parsed,entity)
            index_entities.extend(index_entity)

        # sort on the position of the first part of the entity
        index_entities.sort(key=lambda l: l[0])

        # copy-past the entity found in the list with x
        for k_list in index_entities:
            list_ne.append(' '.join(list_parsed[k_list[0]:k_list[-1]+1]))

        return(list_ne)
