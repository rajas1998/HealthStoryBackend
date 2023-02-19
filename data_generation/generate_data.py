# Importing required libraries

import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta
import pickle as pkl

# Creating a series of data of in range of 1-50.
x = np.linspace(0, 1, 50)


def high_bp(x, mean, sd):
    prob_density = (np.pi * sd) * np.exp(-0.5 * ((x - mean) / sd) ** 2) * 30
    prob_density += 120
    prob_density += (np.random.rand(prob_density.shape[0]) - 0.5) * 5
    return prob_density


def low_bp(x, mean, sd):
    prob_density = (np.pi * sd) * np.exp(-0.5 * ((x - mean) / sd) ** 2) * 20
    prob_density += 60
    prob_density += (np.random.rand(prob_density.shape[0]) - 0.5) * 5
    return prob_density


def resp_rate(x):
    prob_density = np.random.rand(x.shape[0]) * 4 + 12
    return prob_density


# Calculate mean and Standard deviation.
mean = np.mean(x)
sd = np.std(x)

# Apply function to the data.
high_bp_pdf = high_bp(x, mean, sd)
low_bp_pdf = low_bp(x, mean, sd)
resp_pdf = resp_rate(x)

starting_date = date.fromisoformat("2019-08-02")
high_data = []
low_data = []
resp_data = []
for index, i in enumerate(x):
    curr_date = starting_date + timedelta(int(i * 365))
    high_data.append([str(curr_date), high_bp_pdf[index]])
    low_data.append([str(curr_date), low_bp_pdf[index]])
    resp_data.append([str(curr_date), resp_pdf[index]])

with open("../data/users/1/high_bp.pkl", "wb") as f:
    pkl.dump(high_data, f)

with open("../data/users/1/low_bp.pkl", "wb") as f:
    pkl.dump(low_data, f)

with open("../data/users/1/resp.pkl", "wb") as f:
    pkl.dump(resp_data, f)

with open("../data/users/1/urine.pkl", "wb") as f:
    urine = [
        [str(date.fromisoformat("2019-12-01")), 129],
        [str(date.fromisoformat("2020-03-19")), 147],
    ]
    pkl.dump(urine, f)

with open("../data/users/1/ecg.pkl", "wb") as f:
    ecg = [[str(date.fromisoformat("2019-08-28")), 73]]
    pkl.dump(ecg, f)

with open("../data/users/1/echo.pkl", "wb") as f:
    echo = [[str(date.fromisoformat("2019-08-28")), 84]]
    pkl.dump(echo, f)

with open("../data/users/1/blood.pkl", "wb") as f:
    blood = [
        [str(date.fromisoformat("2020-03-01")), 53.7],
        [str(date.fromisoformat("2020-05-26")), 48.2],
    ]
    pkl.dump(blood, f)

with open("../data/users/1/meta.pkl", "wb") as f:
    meta = [
        [str(date.fromisoformat("2020-03-01")), 146.7],
        [str(date.fromisoformat("2020-05-26")), 139.4],
    ]
    pkl.dump(meta, f)

with open("../data/users/1/tests.pkl", "wb") as f:
    tests = {
        "Urine": [
            str(date.fromisoformat("2019-12-01")),
            str(date.fromisoformat("2020-03-19")),
        ],
        "ECG": [str(date.fromisoformat("2019-08-28"))],
        "Echocardiogram": [str(date.fromisoformat("2019-08-28"))],
        "Blood": [
            str(date.fromisoformat("2020-03-01")),
            str(date.fromisoformat("2020-05-26")),
        ],
        "Metabolic": [
            str(date.fromisoformat("2020-03-01")),
            str(date.fromisoformat("2020-05-26")),
        ],
    }
    pkl.dump(tests, f)

with open("../data/users/1/soaps.pkl", "wb") as f:
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
    pkl.dump(soap_list, f)
# Urine
# ECG
# Echocardiogram
# blood count
# metabolic panel
# Blood count
# Metabolic panel
