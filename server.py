import pickle as pkl
import time
import boto3
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

    file_name = "/content/conv.mp3"
    s3_file = "conv.mp3"
    bucket_name = "treehacksath"
    s3.upload_file(file_name, bucket_name, s3_file)

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
    return {
        "response": [
            {
                "title": "high blood pressure",
                "data": [
                    ["2019-08-02", 126.09855939181719],
                    ["2019-08-09", 127.05119024810843],
                    ["2019-08-16", 126.74394319560402],
                    ["2019-08-24", 128.8752234926254],
                    ["2019-08-31", 128.86968358227782],
                    ["2019-09-08", 129.8505387381672],
                    ["2019-09-15", 133.33162115938256],
                    ["2019-09-23", 133.515862285795],
                    ["2019-09-30", 134.83635028979305],
                    ["2019-10-08", 134.20226165245072],
                    ["2019-10-15", 138.94658562502067],
                    ["2019-10-22", 139.32648621363748],
                    ["2019-10-30", 138.18657568444905],
                    ["2019-11-06", 140.29519898128902],
                    ["2019-11-14", 138.9818728919338],
                    ["2019-11-21", 140.15477438809842],
                    ["2019-11-29", 143.84067317750188],
                    ["2019-12-06", 144.0893919603239],
                    ["2019-12-14", 143.81655543062243],
                    ["2019-12-21", 143.36899828718987],
                    ["2019-12-28", 145.5883510147245],
                    ["2020-01-05", 147.33268107189437],
                    ["2020-01-12", 145.38001316662968],
                    ["2020-01-20", 146.22415569188635],
                    ["2020-01-27", 146.85178434878327],
                    ["2020-02-04", 146.69940542737095],
                    ["2020-02-11", 145.16510215846995],
                    ["2020-02-19", 146.85324333810138],
                    ["2020-02-26", 146.57951443491547],
                    ["2020-03-05", 148.22311344257048],
                    ["2020-03-12", 145.62674182065956],
                    ["2020-03-19", 147.3813087842703],
                    ["2020-03-27", 144.7729334878882],
                    ["2020-04-03", 141.51833249518134],
                    ["2020-04-11", 142.151934691492],
                    ["2020-04-18", 139.980479099949],
                    ["2020-04-26", 139.3805773268839],
                    ["2020-05-03", 137.26279898427268],
                    ["2020-05-11", 139.6111022912123],
                    ["2020-05-18", 135.09620054911636],
                    ["2020-05-25", 133.14159266230214],
                    ["2020-06-02", 132.7242043735578],
                    ["2020-06-09", 132.03171201242216],
                    ["2020-06-17", 130.5606914714524],
                    ["2020-06-24", 128.7528309265567],
                    ["2020-07-02", 131.15724489229126],
                    ["2020-07-09", 129.49496536470807],
                    ["2020-07-17", 128.80290868625343],
                    ["2020-07-24", 125.96921248957533],
                    ["2020-08-01", 125.44867636229678],
                ],
            },
            {
                "title": "low blood pressure",
                "data": [
                    ["2019-08-02", 66.8230006029143],
                    ["2019-08-09", 65.19938518076572],
                    ["2019-08-16", 67.7599720636864],
                    ["2019-08-24", 63.78622869328084],
                    ["2019-08-31", 67.3749589406387],
                    ["2019-09-08", 65.06485416338887],
                    ["2019-09-15", 67.92911041440956],
                    ["2019-09-23", 67.34754649044322],
                    ["2019-09-30", 68.96558407627153],
                    ["2019-10-08", 68.41797155129957],
                    ["2019-10-15", 72.77041557628056],
                    ["2019-10-22", 70.24485996893058],
                    ["2019-10-30", 73.18929008745714],
                    ["2019-11-06", 73.33243602730282],
                    ["2019-11-14", 73.4906568818186],
                    ["2019-11-21", 74.9692781212494],
                    ["2019-11-29", 76.65455828473773],
                    ["2019-12-06", 77.29643756414556],
                    ["2019-12-14", 76.4667116887368],
                    ["2019-12-21", 78.1498083409428],
                    ["2019-12-28", 76.16892321900546],
                    ["2020-01-05", 78.51171504141261],
                    ["2020-01-12", 79.76795913550984],
                    ["2020-01-20", 77.2543913236534],
                    ["2020-01-27", 79.6573719346215],
                    ["2020-02-04", 79.6977592739311],
                    ["2020-02-11", 78.30476856521216],
                    ["2020-02-19", 78.43675542865594],
                    ["2020-02-26", 79.06236905088798],
                    ["2020-03-05", 76.39832165238478],
                    ["2020-03-12", 76.8310295938742],
                    ["2020-03-19", 75.98445372590908],
                    ["2020-03-27", 74.36021369752694],
                    ["2020-04-03", 74.14798895139401],
                    ["2020-04-11", 75.7890569806462],
                    ["2020-04-18", 72.67840639587908],
                    ["2020-04-26", 71.1407145345221],
                    ["2020-05-03", 75.0761450417319],
                    ["2020-05-11", 71.97023924882144],
                    ["2020-05-18", 69.1047618092741],
                    ["2020-05-25", 69.79620792303045],
                    ["2020-06-02", 70.99363139812033],
                    ["2020-06-09", 69.05522371320065],
                    ["2020-06-17", 67.99080244042408],
                    ["2020-06-24", 65.61156833445659],
                    ["2020-07-02", 67.91683241792813],
                    ["2020-07-09", 67.66740549069705],
                    ["2020-07-17", 64.66306334134258],
                    ["2020-07-24", 64.51981101403003],
                    ["2020-08-01", 62.97881176028637],
                ],
            },
        ]
    }


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
