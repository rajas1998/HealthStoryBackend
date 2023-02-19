import openai
from flask import Flask
import boto3
import time
import pandas as pd


app = Flask(__name__)
openai.api_key = "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"

soap_list = [
    """Subjective:
The patient, a 50-year-old male, presents with a history of hypertension for the past 6 months. He reports feeling generally well but complains of occasional dizziness and shortness of breath during physical activity. “While work isn’t very stressful, I have been feeling dizzy while playing tennis lately. I am worried about my long term health because my grandmother died from a heart attack”. The patient mentions a family history of hypertension and heart disease, which has caused him to worry about his long-term health.

Objective:
Blood pressure measurements were taken and found to be consistently elevated, with an average reading of 155/95 mmHg. Physical examination was otherwise unremarkable.

A: Assessment
The patient is diagnosed with stage 2 hypertension, and additional testing is recommended to further evaluate the cause of his dizziness and shortness of breath during physical activity. The patient’s family history of hypertension and heart disease suggests that there may be a genetic component to his condition.

P: Plan
The patient is prescribed a daily dose of amlodipine 5 mg, a calcium channel blocker, to control his blood pressure. The patient is advised to maintain a healthy diet, exercise regularly, and avoid smoking and excessive alcohol intake. Follow-up appointments are scheduled every 3 months to monitor blood pressure and assess the effectiveness of treatment. An electrocardiogram (ECG) and echocardiogram tests have been ordered. A referral to a registered dietitian is also recommended to help the patient develop a healthy eating plan.
""",
    """
Subjective:
The patient reports that they have been taking their medication as prescribed, but they have experienced some occasional dizziness and fatigue. They also report some difficulty sleeping and mild anxiety. “I have been feeling really tired after playing a 3 set tennis game and when I come back home, I am unable to sleep despite being tired.”

O: Blood pressure is currently 130/80 mmHg, which is an improvement from the last visit. There are no signs of edema or fluid retention. The patient's heart and lung sounds are normal. The ECG and echocardiogram tests from last visit showed no signs of structural abnormalities or left ventricular hypertrophy.

A: The patient's hypertension is partially controlled with medication, but there may be room for improvement. The patient's symptoms of dizziness, fatigue, difficulty sleeping, and anxiety may be related to their medication.

P: The patient will be advised to continue taking their medication as prescribed, but to monitor their symptoms closely and report any significant changes. A sleep study may also be recommended to evaluate the patient's difficulty sleeping. A urine test has been recommended to understand how kidneys are responding to this medication. The patient will be advised to reduce their caffeine and sodium intake and increase their exercise routine to further manage their blood pressure. A follow-up appointment will be scheduled in three months.
""",
    """Subjective: "I forgot to take my medication a few times this week, and I've been feeling a bit more stressed than usual." The patient reports intermittent medication adherence and increased stress. The patient denies any chest pain, shortness of breath, or palpitations. The patient is compliant with their dietary and exercise regimen and reports losing an additional 3 pounds since their last visit.

Objective: The patient's blood pressure is measured at 150/95 mmHg, which is an abnormal increase from the previous visit. Their heart rate is 78 bpm and regular. Lungs are clear to auscultation, and heart sounds are normal with no murmurs or gallops. The patient's weight is measured and noted to have decreased by 3 pounds compared to their last visit. The urine test showed a slightly elevated protein level. The elevated protein in the urine indicates mild kidney damage, which will need to be monitored closely.

Assessment: The patient’s condition is worsening due to non-adherence to medication and increased stress.

Plan: Based on the test results, the medication will be changed to Losartan 50mg once daily, and hydrochlorothiazide 12.5mg once daily. The patient is advised to maintain their current lifestyle changes, including a low-sodium diet, regular exercise, and weight loss. The patient is recommended to monitor their blood pressure at home regularly and to return in 3 months for a follow-up visit. A lab workup, including a complete blood count and a comprehensive metabolic panel, will be ordered to assess their renal function and electrolyte balance. A referral will be made to a nephrologist to further evaluate the kidney damage. The patient is advised to follow up with their primary care physician for any other medical concerns.
""",
    """Subjective:
The patient reports feeling generally well since their last visit but has noticed some mild dizziness and fatigue lately. They also report experiencing some mild headaches and have been having some trouble sleeping. They state that they have been taking their medication regularly and have been following a healthy diet.

Objective:
Blood pressure today is 130/80 mmHg, which is an improvement from last visit. A blood count and metabolic panel were ordered since the patient has been on the new medication for the past 3 months. The blood count came back within normal limits. However, the metabolic panel showed elevated liver enzymes and potassium levels, which may be related to the patient's new medication.

Assessment:
The patient's blood pressure is improving, but they have been experiencing some mild side effects with their new medication, including elevated liver enzymes and potassium levels. The patient's symptoms of dizziness, fatigue, and headaches may be related to their medication or could be due to other factors, such as lack of sleep. The ECG showed no significant changes.

Plan:
The patient will also be advised to follow up with their primary care physician for further liver function tests. The patient will be advised to monitor their blood pressure at home and report any significant changes. They will also be advised to improve their sleep hygiene and to manage their stress levels to alleviate their symptoms of dizziness, fatigue, and headaches. A follow-up appointment in 3 months will be scheduled to monitor the patient's blood pressure and medication tolerance.
""",
    """
Subjective:
"I feel so much better now that I've made some changes. I'm grateful for the support." The patient expresses gratitude for the progress they have made in managing their hypertension.  The patient also reported that they have been taking their medications regularly and have been following the dietary and exercise guidelines as recommended.

Objective: Blood pressure reading is 120/80 mmHg, indicating a reduction in blood pressure. The liver tests from the physician were reviewed, showing no side effects of the medication on the patient's liver.

Assessment:
The patient's blood pressure has been well-controlled and there has been an improvement in kidney function and normal liver function, as evidenced by the latest blood test results. The patient has been compliant with medication and lifestyle modifications.

Plan:
The patient's medication has been reduced from 10mg of Lisinopril to 5mg, as the blood pressure readings have been stable. The patient will continue taking the reduced dosage and will return for follow-up in 6 months for blood pressure monitoring and kidney function tests. The patient will also continue to adhere to the recommended dietary and exercise guidelines.
""",
]

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


@app.route("/soap/summary")
def hello_world():
    note_summaries = []
    full_string = ""

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
            prompt=f"{full_string} What is the summary of this series of soap notes as a story which is useful for a doctor?",
            max_tokens=512,
            temperature=0,
        )
        .choices[0]
        .text
    )

    ret = {"full_summary": full_story, "note_summaries": note_summaries}

    return ret
