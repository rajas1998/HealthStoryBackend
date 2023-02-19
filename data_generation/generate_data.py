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

with open(
    "/home/dhruva/TreeHacks2023/HealthStoryBackend/data/users/1/high_bp.pkl", "wb"
) as f:
    pkl.dump(high_data, f)

with open(
    "/home/dhruva/TreeHacks2023/HealthStoryBackend/data/users/1/low_bp.pkl", "wb"
) as f:
    pkl.dump(low_data, f)

with open(
    "/home/dhruva/TreeHacks2023/HealthStoryBackend/data/users/1/resp.pkl", "wb"
) as f:
    pkl.dump(resp_data, f)

with open(
    "/home/dhruva/TreeHacks2023/HealthStoryBackend/data/users/1/urine.pkl", "wb"
) as f:
    urine = [
        [str(date.fromisoformat("2019-12-01")), 129],
        [str(date.fromisoformat("2020-03-19")), 147],
    ]
    pkl.dump(urine, f)

with open(
    "/home/dhruva/TreeHacks2023/HealthStoryBackend/data/users/1/ecg.pkl", "wb"
) as f:
    ecg = [[str(date.fromisoformat("2019-08-28")), 73]]
    pkl.dump(ecg, f)

with open(
    "/home/dhruva/TreeHacks2023/HealthStoryBackend/data/users/1/echo.pkl", "wb"
) as f:
    echo = [[str(date.fromisoformat("2019-08-28")), 84]]
    pkl.dump(echo, f)

with open(
    "/home/dhruva/TreeHacks2023/HealthStoryBackend/data/users/1/blood.pkl", "wb"
) as f:
    blood = [
        [str(date.fromisoformat("2020-03-01")), 53.7],
        [str(date.fromisoformat("2020-05-26")), 48.2],
    ]
    pkl.dump(blood, f)

with open(
    "/home/dhruva/TreeHacks2023/HealthStoryBackend/data/users/1/meta.pkl", "wb"
) as f:
    meta = [
        [str(date.fromisoformat("2020-03-01")), 146.7],
        [str(date.fromisoformat("2020-05-26")), 139.4],
    ]
    pkl.dump(meta, f)

with open(
    "/home/dhruva/TreeHacks2023/HealthStoryBackend/data/users/1/tests.pkl", "wb"
) as f:
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
# Urine
# ECG
# Echocardiogram
# blood count
# metabolic panel
# Blood count
# Metabolic panel
