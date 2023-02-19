import pickle as pkl
import time
<<<<<<< Updated upstream

import boto3
=======
>>>>>>> Stashed changes
import openai
import pandas as pd
from flask import Flask


def get_text(soap_note):
    return f"""Date: {soap_note['date']}\n
    Subjective: {soap_note['subjective']}\n
    Objective: {soap_note['objective']}\n
    Assessment: {soap_note['assessment']}\n
    Plan: {soap_note['plan']}"""


app = Flask(__name__)
openai.api_key = "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"
full_string = ""
soaps = pkl.load(open("data/users/1/soaps.pkl", "rb"))
for i in range(len(soaps)):
    full_string += f"Note {i}: {soaps[i]}\n"

transcribe = boto3.client(
    "transcribe",
    aws_access_key_id="AKIA3CCUOX3QCZY2TVF2",
    aws_secret_access_key="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",
    region_name="us-west-1",
)


def check_job_name(job_name):
    job_verification = True
    # all the transcriptions
    existed_jobs = transcribe.list_transcription_jobs()
    for job in existed_jobs["TranscriptionJobSummaries"]:
        if job_name == job["TranscriptionJobName"]:
            job_verification = False
            break
        if job_verification == False:
            command = input(
                job_name
                + " has existed. \nDo you want to override the existed job (Y/N): "
            )
            if command.lower() == "y" or command.lower() == "yes":
                transcribe.delete_transcription_job(TranscriptionJobName=job_name)
            elif command.lower() == "n" or command.lower() == "no":
                job_name = input("Insert new job name? ")
                check_job_name(job_name)
        else:
            print("Input can only be (Y/N)")
            command = input(
                job_name
                + " has existed. \nDo you want to override the existed job (Y/N): "
            )
    return job_name


@app.route("/soap/transcribe")
def amazon_transcribe(audio_file_name, max_speakers=-1):

    if max_speakers > 10:
        raise ValueError("Maximum detected speakers is 10.")

    job_uri = "s3://treehacksath/" + audio_file_name
    job_name = (audio_file_name.split(".")[0]).replace(" ", "")

    # check if name is taken or not
    job_name = check_job_name(job_name)
    if max_speakers != -1:
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": job_uri},
            MediaFormat=audio_file_name.split(".")[1],
            LanguageCode="en-US",
            Settings={"ShowSpeakerLabels": True, "MaxSpeakerLabels": max_speakers},
        )
    else:
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": job_uri},
            MediaFormat=audio_file_name.split(".")[1],
            LanguageCode="en-US",
            Settings={"ShowSpeakerLabels": True},
        )
    while True:
        result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if result["TranscriptionJob"]["TranscriptionJobStatus"] in [
            "COMPLETED",
            "FAILED",
        ]:
            break
        time.sleep(15)
    if result["TranscriptionJob"]["TranscriptionJobStatus"] == "COMPLETED":
        data = pd.read_json(
            result["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
        )
    data = pd.read_json(result["TranscriptionJob"]["Transcript"]["TranscriptFileUri"])
    transcript = data["results"][2][0]["transcript"]
    return transcript

@app.route("/soap/soapify")
def soapify(audio_file_name):
    transcript = amazon_transcribe(audio_file_name, max_speakers=2)
    conv = f"""Here is a conversation between a doctor and a patient having hypertension:\n" 
    + {transcript} 
    + "\nCan you convert this conversation to a medical SOAP format?
    """
    openai.api_key = "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"

    response = openai.Completion.create(
        model="text-davinci-003", prompt=conv, temperature=0.7, max_tokens=1024
    )
    return response["choices"][0]["text"]



@app.route("/dummy")
def dummy():
    return {"22/12/12": 10}


@app.route("/soap/summary")
def hello_world():
    note_summaries = []
    full_string = ""
    soap_list = pkl.load(open("data/users/1/soaps.pkl", "rb"))
    for ind, soap_note in enumerate(soap_list):
        prompt = f"{soap_note}\n What is the most important insight from this SOAP?"

        note_summaries.append(
            openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=512,
                temperature=0,
            )
            .choices[0]
            .text
        )

        full_string += f"Note {ind}:\n {soap_note}\n"

    full_story = (
        openai.Completion.create(
            model="text-davinci-003",
            prompt=f"""{full_string} What is the summary of this series of
             soap notes as a story which is useful for a doctor?""",
            max_tokens=512,
            temperature=0,
        )
        .choices[0]
        .text
    )

    ret = {"full_summary": full_story, "note_summaries": note_summaries}

    return ret


def get_value(test_type, timestamp):
    if test_type == "Urine":
        data = pkl.load(open("data/users/1/urine.pkl", "rb"))
    elif test_type == "ECG":
        data = pkl.load(open("data/users/1/ecg.pkl", "rb"))
    elif test_type == "Echocardiogram":
        data = pkl.load(open("data/users/1/echo.pkl", "rb"))
    elif test_type == "Blood":
        data = pkl.load(open("data/users/1/blood.pkl", "rb"))
    elif test_type == "Metabolic":
        data = pkl.load(open("data/users/1/meta.pkl", "rb"))
    else:
        raise ValueError

    for i, j in data:
        if i == timestamp:
            return j
    raise IndexError


def find_soap(timestamp):
    for i in range(len(soaps)):
        if soaps[i] == timestamp:
            return soaps[i]


@app.route("/tests")
def return_tests():
    tests = pkl.load(open("data/users/1/tests.pkl", "rb"))
    recommended_tests = pkl.load(open("data/users/1/tests.pkl", "rb"))
    tests_ret = []
    for test_type in recommended_tests:
        for timestamp in recommended_tests[test_type]:
            if timestamp not in tests[test_type]:
                tests_ret.append(
                    {
                        "Type": test_type,
                        "Done": False,
                        "Value": get_value(test_type, timestamp),
                    }
                )
            else:
                tests_ret.append(
                    {
                        "Type": test_type,
                        "Done": True,
                        "Value": get_value(test_type, timestamp),
                        "Reason": openai.Completion.create(
                            prompt=f"{find_soap(timestamp)} Imagine you are a doctor. What is the reason that you ordered the {test_type} readings for this patient based on the SOAP notes?",
                            model="text-davinci-003",
                            max_tokens=512,
                            temperature=0,
                        )
                        .choices[0]
                        .text.strip(),
                    }
                )
    return {"tests": tests_ret}
