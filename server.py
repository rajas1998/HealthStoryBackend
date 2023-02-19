import calendar
import datetime
import os
import pickle as pkl
import time

import boto3
import openai
import pandas as pd
from flask import Flask, request
from flask_cors import CORS, cross_origin


def get_text(soap_note):
    return f"""Date: {soap_note['date']}\n
    Subjective: {soap_note['subjective']}\n
    Objective: {soap_note['objective']}\n
    Assessment: {soap_note['assessment']}\n
    Plan: {soap_note['plan']}"""


app = Flask(__name__)
CORS(app)
openai.api_key = "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"
full_string = ""
BASE_PATH = "data/users/1"
soaps = pkl.load(open(f"{BASE_PATH}/soaps.pkl", "rb"))
for i in range(len(soaps)):
    full_string += f"Note {i}: {soaps[i]}\n"

transcribe = boto3.client(
    "transcribe",
    aws_access_key_id="AKIA3CCUOX3QCZY2TVF2",
    aws_secret_access_key="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",
    region_name="us-west-1",
)

s3 = boto3.client(
    "s3",
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

    s3_file = "conv.webm"
    bucket_name = "treehacksath"
    s3.upload_file(audio_file_name, bucket_name, s3_file)

    if max_speakers > 10:
        raise ValueError("Maximum detected speakers is 10.")

    job_uri = "s3://treehacksath/" + s3_file
    job_name = str(calendar.timegm(time.gmtime()))

    # check if name is taken or not
    # job_name = check_job_name(job_name)
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
        time.sleep(0.01)
    if result["TranscriptionJob"]["TranscriptionJobStatus"] == "COMPLETED":
        data = pd.read_json(
            result["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
        )
    data = pd.read_json(result["TranscriptionJob"]["Transcript"]["TranscriptFileUri"])
    transcript = data["results"][2][0]["transcript"]

    # speaker differentiation
    labels = data["results"]["speaker_labels"]["segments"]
    speaker_start_times = {}

    for label in labels:
        for item in label["items"]:
            speaker_start_times[item["start_time"]] = item["speaker_label"]

    items = data["results"]["items"]
    lines = []
    line = ""
    curr_time = 0
    speaker = "null"
    i = 0

    # loop through all elements
    for item in items:
        i = i + 1
        content = item["alternatives"][0]["content"]
        # if it's starting time
        if item.get("start_time"):
            current_speaker = speaker_start_times[item["start_time"]]
        # in AWS output, there are types as punctuation
        elif item["type"] == "punctuation":
            line = line + content

        # handle different speaker
        if current_speaker != speaker:
            if speaker:
                if speaker == "spk_1":
                    lines.append(
                        {"speaker": "Patient", "line": line, "time": curr_time}
                    )
                elif speaker == "spk_0":
                    lines.append({"speaker": "Doctor", "line": line, "time": curr_time})
            line = content
            speaker = current_speaker
            curr_time = item["start_time"]
        elif item["type"] != "punctuation":
            line = line + " " + content

    if speaker == "spk_1":
        lines.append({"speaker": "Patient", "line": line, "time": curr_time})
    elif speaker == "spk_0":
        lines.append({"speaker": "Doctor", "line": line, "time": curr_time})

    # sort the results by the time
    sorted_lines = sorted(lines, key=lambda k: float(k["time"]))
    # write into the .txt file
    transcript = ""
    for line_data in sorted_lines:
        transcript += (
            "["
            + str(datetime.timedelta(seconds=int(round(float(line_data["time"])))))
            + "] "
            + line_data.get("speaker")
            + ": "
            + line_data.get("line")
        )

    return transcript


@app.route("/soap/soapify", methods=["POST"])
def soapify():
    file_path = f"temp.webm"
    file = request.files["myFile"]
    file.save(file_path)
    transcript = amazon_transcribe(file_path, max_speakers=2)
    conv = f"""Here is a conversation between a doctor and a patient having hypertension:\n"
    + {transcript}
    + "\nCan you convert this conversation to a medical SOAP format?
    """
    openai.api_key = "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"

    response = openai.Completion.create(
        model="text-davinci-003", prompt=conv, temperature=0.7, max_tokens=1024
    )
    if os.path.exists(file_path):
        os.remove(file_path)
    return response["choices"][0]["text"]


@app.route("/dummy")
def dummy():
    return "WORKING!!"


@app.route("/soap/summary")
def hello_world():
    note_summaries = []
    for i in range(len(soaps)):
        prompt = (
            f"{get_text(soaps[i])}\n What is the most important insight from this SOAP?"
        )

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
        data = pkl.load(open(f"{BASE_PATH}/urine.pkl", "rb"))
    elif test_type == "ECG":
        data = pkl.load(open(f"{BASE_PATH}/ecg.pkl", "rb"))
    elif test_type == "Echocardiogram":
        data = pkl.load(open(f"{BASE_PATH}/echo.pkl", "rb"))
    elif test_type == "Blood":
        data = pkl.load(open(f"{BASE_PATH}/blood.pkl", "rb"))
    elif test_type == "Metabolic":
        data = pkl.load(open(f"{BASE_PATH}/meta.pkl", "rb"))
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
    tests = pkl.load(open(f"{BASE_PATH}/tests.pkl", "rb"))
    recommended_tests = pkl.load(open(f"{BASE_PATH}/tests.pkl", "rb"))
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


@app.route("/best_graphs")
def return_best_graphs():
    return (
        openai.Completion.create(
            model="text-davinci-003",
            prompt=f"{full_string} Imagine you are a doctor. Using the SOAP notes mentioned, what are the top 3 tests that a doctor would want to see. Answer in the form of a numbered list",
            max_tokens=512,
            temperature=0,
        )
        .choices[0]
        .text.strip()
    )


@app.route("/data")
def return_data():
    best_graphs = return_best_graphs().strip(".").strip(" ")
    all_words = best_graphs.split(" ")
    sanitized_words = [
        i.replace("\n", " ").strip(" ").strip("(").strip(")").strip(".").lower()
        for i in all_words
    ]
    graph_set = set(sanitized_words)
    test_data_mapping = [
        ("high pressure", f"{BASE_PATH}/high_bp.pkl"),
        ("low pressure", f"{BASE_PATH}/low_bp.pkl"),
        ("ecg", f"{BASE_PATH}/ecg.pkl"),
        ("blood", f"{BASE_PATH}/blood.pkl"),
        ("metabolic", f"{BASE_PATH}/meta.pkl"),
        ("urine", f"{BASE_PATH}/urine.pkl"),
        ("echocardiogram", f"{BASE_PATH}/echo.pkl"),
    ]
    important_data = [
        i
        for i in test_data_mapping
        if len(set(i[0].split(" ")).intersection(graph_set)) > 0
    ]
    non_important_data = [
        i
        for i in test_data_mapping
        if len(set(i[0].split(" ")).intersection(graph_set)) == 0
    ]
    final_response = [
        {"title": i[0], "data": pkl.load(open(i[1], "rb"))} for i in important_data
    ]
    for i in non_important_data:
        final_response.append({"title": i[0], "data": pkl.load(open(i[1], "rb"))})

    return {"response": final_response}


@app.route("/drugs")
def return_drugs():
    drugs = pkl.load(f"{BASE_PATH}/drugs.pkl")
    return drugs


@app.route("/question", methods=["POST"])
def return_question():
    return (
        openai.Completion.create(
            model="text-davinci-003",
            prompt=f"{full_string} Imagine you are the assistant for a doctor and are given the previous SOAP notes as context. Answer the following question: {request.json['Question']}",
            max_tokens=512,
            temperature=0,
        )
        .choices[0]
        .text.strip()
    )


@app.route("/switch")
def do_switch():
    global soaps
    global full_string
    global BASE_PATH
    BASE_PATH = "data_new/users/1"
    soaps = pkl.load(open(f"{BASE_PATH}/soaps.pkl", "rb"))
    full_string = ""
    for i in range(len(soaps)):
        full_string += f"Note {i}: {soaps[i]}\n"
