from benchmarkstt.metrics.cli import main as main_wer
from datetime import datetime
from sttmetrics.Tools import Tools as tl
import subprocess
import difflib
import copy
import jaro
import re

#Args class to pass as an parameters for the wer command line
class Args:
    def __init__(self, refPath, hypPath):
        self.reference = refPath
        self.reference_type = "infer"
        self.hypothesis = hypPath
        self.hypothesis_type = "infer"
        self.metrics = [['wer']]
        self.output_format = "restructuredtext"
        self.diffcounts = True



class Metric :
    def __init__(self):
        self


    # Metric to get the gender of the speaker detected given the speaker id
    def get_spraker_gender(self,speakerId, speakers):
        for speaker in speakers:
            if "gender" in speaker and speaker["id"] == speakerId:
                return speaker["gender"]
        return None

    # Method of metric : to calculate word speakers and genders differencies between ref and res word lists
    def word_diff(self, transcript_ref, transcript_res):
        threshhold = 0.66
        conf_time = 0.2
        different_speaker_number = 0
        different_gender_number = 0
        for index_ref, word_ref in enumerate(transcript_ref["words"]):
            wrd_ref = word_ref["content"]
            spk_ref = word_ref["speakerId"]
            start_ref = word_ref["startTime"]
            for index_res, word_res in enumerate(transcript_res["words"]):
                wrd_res = word_res["content"]
                spk_res = word_res["speakerId"]
                start_res = word_res["startTime"]
                if (start_ref - conf_time) <= start_res and (start_ref + conf_time) >= start_res:
                    if (wrd_ref == wrd_res) or ( difflib.SequenceMatcher(None, wrd_ref.lower(), wrd_res.lower()).ratio() >= threshhold):
                        if spk_ref != spk_res and spk_res is not None:
                            different_speaker_number += 1
                        gen_res = self.get_spraker_gender(spk_res, transcript_res["speakers"])
                        gen_ref = self.get_spraker_gender(spk_ref, transcript_ref["speakers"])
                        if gen_ref != gen_res and gen_res is not None and different_gender_number is not None:
                            different_gender_number += 1
                        elif gen_res == None:
                            different_gender_number = None
                        break
                    elif index_res + 1 < len(transcript_res["words"]) and wrd_ref != \
                                transcript_res["words"][index_res + 1]["content"] and \
                                (difflib.SequenceMatcher(None, wrd_ref.lower(),
                                                         wrd_res.lower() + transcript_res["words"][index_res + 1][
                                                             "content"].lower()).ratio() >= threshhold):
                        if spk_ref != spk_res and spk_res is not None:
                            different_speaker_number += 1
                        gen_res = self.get_spraker_gender(spk_res, transcript_res["speakers"])
                        gen_ref = self.get_spraker_gender(spk_ref, transcript_ref["speakers"])
                        if gen_ref != gen_res and gen_res is not None and different_gender_number is not None:
                            different_gender_number += 1
                        elif gen_res == None:
                            different_gender_number = None
                        break
        if len(transcript_ref["words"]) != 0:
            word_speaker_diff = different_speaker_number / len(transcript_ref["words"])
            if different_gender_number is not None :
                word_gender_diff = different_gender_number / len(transcript_ref["words"])
            else:
                word_gender_diff = None
            return word_speaker_diff, word_gender_diff
        else:
            return None




    # Method that compute word rate error command line
    def compute_wer(self,tmpPath, transcript_ref, transcript_res):
        # make temporary files as parameters for Wer command line


        normalized_text_ref = re.sub('([.,;!?()\'])', r' \1 ', transcript_ref.lower())
        normalized_text_ref = re.sub('\s{2,}', ' ',normalized_text_ref)
        normalized_text_ref = re.sub('\s+', ' ',normalized_text_ref)


        normalized_text_res = re.sub('([.,;!?()\'])', r' \1 ', transcript_res.lower())
        normalized_text_res = re.sub('\s{2,}', ' ',normalized_text_res)
        normalized_text_res = re.sub('\s+', ' ',normalized_text_res)

        text_ref_path, text_res_path = tl.make_temp_files(tmpPath,
                                                          normalized_text_ref,
                                                          normalized_text_res)

        # Wer command line
        wer_value = self.wer(text_ref_path, text_res_path)

        # Delete temporaty files
        tl.delete_temp_files(text_ref_path, text_res_path)

        return wer_value
    

    def compute_wer_cli(self, tmpPath, transcript_ref, transcript_res):
        # make temporary files as parametrs for Wer command line

        text_ref_path, text_res_path = tl.make_temp_files(tmpPath,
                                                          transcript_ref,
                                                          transcript_res)
        # Call to CLI
        command = "benchmarkstt -r {} -h {} --wer --lowercase".format(text_res_path, text_ref_path)
        retour = subprocess.run(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
        if retour.stderr.decode() == '':
            return float(retour.stdout.decode()[9:-2])
        else:
            raise Exception(str(retour.stderr.decode()))
        # Delete temporatu files
        tl.delete_temp_files(text_ref_path, text_res_path)

    # Method to get the current date and time
    def date_time(self):
        now = datetime.now()
        return now.strftime("%Y/%m/%d %H:%M:%S")

    # Method to compute ponctuation error rate based on rules
    def punctuation_error_rate(self, transcript_ref, transcript_res):
        punctuation = ['.', ',', '?', '!']
        conf_time = 1.0

        ref_punct = []
        for i in range(len(transcript_ref["words"])):
            if transcript_ref["words"][i]['content'] in punctuation:
                next_elem = " "
                if i+1 < len(transcript_ref["words"]):
                    next_elem = transcript_ref["words"][i+1]["content"]
                ref_punct.append((transcript_ref["words"][i]["content"], transcript_ref["words"][i]["startTime"], transcript_ref["words"][i]["endTime"], next_elem))

        res_punct = []
        for i in range(len(transcript_res["words"])):
            if transcript_res["words"][i]['content'] in punctuation:
                next_elem = " "
                if i+1 < len(transcript_res["words"]):
                    next_elem = transcript_res["words"][i+1]["content"]
                res_punct.append((transcript_res["words"][i]["content"], transcript_res["words"][i]["startTime"], transcript_res["words"][i]["endTime"],next_elem))

        punct_score = []
        nb_match = 0
        i=0
        for punct_ref in ref_punct:
            found = False
            prev_i = i
            while i < len(res_punct):
                punct_res = res_punct[i]
                if (punct_ref[1] - conf_time) <= punct_res[1] and (punct_ref[1] + conf_time) >= punct_res[1]:

                    if punct_ref[0] == punct_res[0]:
                        if (punct_res[0] in [","]):
                            punct_score.append(1)
                        elif (punct_res[0] in ["!","?","."]) and (punct_res[3][0].isupper() or punct_res[3]==" ") :
                            punct_score.append(1)
                        else:
                            punct_score.append(0)
                    elif punct_res[0] == ",":
                        if punct_ref[0] == ".":
                            punct_score.append(1)
                        else:
                            punct_score.append(0)
                    elif (punct_res[0] == "." and (punct_res[3][0].isupper() or punct_res[3]==" ") ):
                        if (punct_ref[0] == "," ):
                            punct_score.append(1)
                        elif (punct_ref[0] in ["!", "?"]):
                            punct_score.append(0.5)

                    found = True
                    i += 1
                    break
                i += 1
            if found == False:
                i = prev_i
            else:
                nb_match += 1

        if(len(ref_punct) != 0 and len(res_punct) != 0):
            punct_error_rate = ((len(res_punct) - sum(punct_score)) + (len(ref_punct) - len(res_punct))) / len(ref_punct)
            return punct_error_rate
        else :
            return None



    # Method for metric : general speaker diff between the list of speakers of the ref and res transcript
    def general_speaker_diff(self,transcript_ref, transcript_res):
        ref_speakers_number = len(transcript_ref['speakers'])
        res_speakers_number = len(transcript_res['speakers'])

        res_speakers = [ int(elem["id"]) for elem in transcript_res["speakers"] ]
        ref_speakers = [ int(elem["id"]) for elem in transcript_ref["speakers"] ]

        nb_spk_error = 0
        for res_spk in res_speakers:
            if res_spk not in ref_speakers:
                #missing speaker
                nb_spk_error += 1

        if(ref_speakers_number > res_speakers_number):
            nb_spk_error += (ref_speakers_number - res_speakers_number)

        if ref_speakers_number != 0:
            return nb_spk_error / ref_speakers_number
        else:
            return None

    # Method for metric : average response time between the start and end of the ref transcript and the speak duration
    def avg_response_time(self,transcript_ref):
        speak_duration = (transcript_ref["words"][-1]["endTime"] -
                          transcript_ref["words"][0]["startTime"])
        if speak_duration != 0 and "stt_duration" in transcript_ref:
            return transcript_ref["stt_duration"] / speak_duration
        else:
            return None

    # Method that command line for word rate error
    def wer(self,refPath, hypPath):
        args = Args(refPath, hypPath)
        parser = None
        return main_wer(parser, args)

    # Method that computes the named entity error rate based on the orderd list of named entities
    def compute_neer(self,named_entities, list_hypothesis_ne, list_reference_ne):
        neer = {}
        neer_av = 0
        for entity in named_entities:
            count_hypothesis = list_hypothesis_ne.count(entity)
            count_ref = list_reference_ne.count(entity)
            if (count_ref != 0):
                neer[entity] = float(abs(count_ref - count_hypothesis) / count_ref)
                # accumulate the distance per entity
                neer_av += count_ref * neer[entity]
        if len(list_reference_ne) != 0 :
            neer_av = neer_av / len(list_reference_ne)
            neer['av_neer'] = neer_av
            return (neer['av_neer'])
        else:
            return None


    # Method of metric : named entity error rate methode 2 b based
    def compute_neer_methode(self,named_entities, list_hypothesis_ne, list_reference_ne):
        # NEER computes considering bag of words
        wer_ne = self.compute_neer(named_entities, list_hypothesis_ne, list_reference_ne)
        return (wer_ne)


    # Method of metric : verb error rate
    def verb_error_rate(self,verb_list_ref,verb_list_res):
        conf_time = 5.0
        verb_score_error = 0
        i = 0
        for verb_ref in verb_list_ref:
            found = False
            prev_i = i
            while i < len(verb_list_res):
                verb_res = verb_list_res[i]
                if (verb_ref["lemma"] == verb_res["lemma"] ) and ((verb_ref["start_time"] - conf_time) <= verb_res["start_time"] and (verb_ref["start_time"] + conf_time) >= verb_res["start_time"]  ):
                    if (verb_ref["verb"] != verb_res["verb"]):
                        if ("Tense" in verb_ref and "Tense" in verb_res and verb_ref["Tense"] != verb_res["Tense"]):
                            verb_score_error += 0.25
                        if ("Gender" in verb_ref and "Gender" in verb_res and verb_ref["Gender"] != verb_res["Gender"]):
                            verb_score_error += 0.25
                        if ("Number" in verb_ref and "Number" in verb_res and verb_ref["Number"] != verb_res["Number"]):
                            verb_score_error += 0.25
                        if ("VerbForm" in verb_ref and "VerbForm" in verb_res and verb_ref["VerbForm"] != verb_res[
                            "VerbForm"]):
                            verb_score_error += 0.25
                    found = True

                    i += 1
                    break
                i += 1
            if found == False:
                verb_score_error += 1
                i = prev_i

        if len(verb_list_ref) != 0:
            verb_error_rate = verb_score_error / len(verb_list_ref)
            return verb_error_rate
        else :
            return None

    # Method to clean data before computing cver
    def clean_data_custom_vocabulary_error_rate(self, transcript_ref, transcript_res):
        space_punct = [',', '.']
        data_ref = copy.copy(transcript_ref["text"])
        data_res = copy.copy(transcript_res["text"])
        # cleaning data
        for punct in space_punct:
            data_ref = data_ref.replace(punct, " ")
            data_res = data_res.replace(punct, " ")
        data_ref = data_ref.split()
        dict_json = transcript_ref["words"]
        return dict_json, data_ref, data_res

    # Method to compute custom vocabulary error rate
    def compute_custom_vocabulary_error_rate(self, custom_vocabulary, transcript_ref, transcript_res):
        list_conj = ["la", "le", "les", "du", "des", "ces", "ses", "sa", "son", 'ce', "cet", "cette", "l'"]
        list_cv = custom_vocabulary
        list_match_ref_cv = []
        list_ref_cv = []
        list_res_cv = []
        dict_json, data_ref, data_res = self.clean_data_custom_vocabulary_error_rate(transcript_ref, transcript_res)
        # custom vocabulary matches on ref transcript
        # defines list_match_ref_cv
        if(custom_vocabulary is not None):
            for i, word in enumerate(data_ref):
                if word in list_cv:
                    for element in transcript_ref["words"]:
                        if element["content"] == word:
                            prev_word = data_ref[i - 1]
                            det_ref = None
                            if prev_word in list_conj:
                                det_ref = prev_word
                            list_match_ref_cv.append((det_ref, word, element["endTime"], element["startTime"]))
            # defines list_ref_cv
            for list_ref in list_match_ref_cv:
                list_ref_cv.append(list_ref[1])

            # custom vocabulary matches on res transcript (based on cv matches in ref transcript)
            for element_ref in list_match_ref_cv:
                measure = 0
                det = element_ref[0]
                word = element_ref[1]
                end_time = element_ref[2] + 0.2
                start_time = element_ref[3] - 0.2

                for i, word_res in enumerate(transcript_res["words"]) :
                    if word_res["startTime"] >= start_time and word_res["endTime"] <= end_time:
                        measure = jaro.jaro_winkler_metric(word, word_res["content"])
                        prev_word = dict_json[i-1]
                        # words similarity : identical
                        if measure == 1:
                            if det is not None and prev_word["content"] != det:
                                list_res_cv.append(0.75)
                                break
                            else:
                                list_res_cv.append(1)
                                break
                            # words similarity : almost identical
                        elif 0.85 <= measure < 1:
                            if det is not None and prev_word["content"] != det:
                                list_res_cv.append(0.25)
                                break
                            else:
                                list_res_cv.append(0.5)
                                break

            # custom vocabulary error rate
            if len(list_ref_cv) != len(list_res_cv):
                list_res_cv.extend([0 for i in range(len(list_ref_cv) - len(list_res_cv))])
            if len(list_match_ref_cv) != 0 :
                custom_vocavulary_error_rate = (1 - (sum(list_res_cv) / len(list_match_ref_cv)))
                return custom_vocavulary_error_rate
            else:
                return None
        else:
            return None