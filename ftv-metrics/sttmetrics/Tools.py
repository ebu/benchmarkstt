import json
import os
import pandas as pd
#Class for abstract methods for reading and writing files or temporary files
class Tools:

    #Methode for reading the json file of the transcrpt and reference transcript
    @staticmethod
    def read_transcript_files(referencePath, transcriptPath):
        try:
            transcript_ref = json.load(open(referencePath,'rt',encoding='utf-8'))
        except FileNotFoundError:
            transcript_ref = None

        try:
            transcript_res = json.load(open(transcriptPath,'rt',encoding='utf-8'))
        except FileNotFoundError :
            transcript_res = None

        return transcript_ref, transcript_res

    #Methode that return the custom vocabulary from a json files
    @staticmethod
    def get_custom_vocabulary(custom_vocabulary_path):
        custom_vocabulary = []
        try :
            with open(custom_vocabulary_path, mode="rt",encoding='utf-8') as file:
                custom_vocabulary_ref = file.read()

                custom_vocabulary += custom_vocabulary_ref.split("\n")
                custom_vocabulary = list(set(custom_vocabulary))
                return custom_vocabulary

        except FileNotFoundError:
            return None


    #Mehtode fot writing a result of the metrics into a json file
    @staticmethod
    def dump_result_file(destinationPath, metrics):
        df = pd.DataFrame(data=metrics, index=None)
        if(len(df) != 0):

            df.to_csv(destinationPath,encoding='utf-8', index=False)
        else:
            raise NameError('No evaluation data are available, check the provider transcriptions or the reference transcription on S3')


    #Methode that makes temporary files for intermediate steps in the process
    @staticmethod
    def make_temp_files(tmpFolderPath, transcript_ref_txt, transcript_res_txt):
        text_ref_path = os.path.join(tmpFolderPath, "ref.txt")
        text_res_path = os.path.join(tmpFolderPath, "res.txt")
        with open(text_ref_path, mode="w",encoding='utf-8') as file:
            file.write(transcript_ref_txt)

        with open(text_res_path, mode="w",encoding='utf-8') as file:
            file.write(transcript_res_txt)

        return text_ref_path, text_res_path

    #Methode to delete the intermediate/temporary files after use
    @staticmethod
    def delete_temp_files(text_ref_path, text_res_path):
        os.remove(text_ref_path)
        os.remove(text_res_path)
