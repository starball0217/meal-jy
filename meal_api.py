import os
import requests
from dotenv import load_dotenv

load_dotenv()

NEIS_API_KEY = os.getenv("NEIS_API_KEY")
SCHOOL_DATA_BASE_URL = os.getenv("SCHOOL_DATA_BASE_URL")
MEAL_DATA_BASE_URL = os.getenv("MEAL_DATA_BASE_URL")


def _request(url, root_key, params):
    query = {"KEY": NEIS_API_KEY, "Type": "json", "pIndex": 1, "pSize": 100, **params}
    res = requests.get(url, params=query, timeout=10)
    res.raise_for_status()

    data = res.json()
    if root_key in data:
        result = data[root_key][0]["head"][1]["RESULT"]
        rows = data[root_key][1].get("row", [])
    else:
        result = data["RESULT"]
        rows = []

    if result["CODE"] == "INFO-200":
        return []
    if result["CODE"] != "INFO-000":
        raise RuntimeError(f"{result['CODE']}: {result['MESSAGE']}")
    return rows


def search_schools(school_name):
    return _request(SCHOOL_DATA_BASE_URL, "schoolInfo", {"SCHUL_NM": school_name})


def fetch_meals(atpt_code, school_code, ymd):
    return _request(MEAL_DATA_BASE_URL, "mealServiceDietInfo", {
        "ATPT_OFCDC_SC_CODE": atpt_code,
        "SD_SCHUL_CODE": school_code,
        "MLSV_FROM_YMD": ymd,
        "MLSV_TO_YMD": ymd,
    })
