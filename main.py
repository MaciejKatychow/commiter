import calendar
import subprocess
from datetime import datetime, timedelta, date
from typing import Optional
from pandas import read_csv
from pathlib import Path
import random
import os
import sys

FILENAME = "changeable.txt"
WEEK_LEN = 7
SENTENCE_LEN = 50
WEEKS_IN_YEAR = 53
YEAR = 2022
DAYS = 365
GIT_PUSH = "git push"
GIT_ADD = f"git add {FILENAME}"


def commit_by_date(date: date) -> None:
    def subprocess_run(command: str) -> None:
        subprocess.run(["powershell", "-Command", command], check=True)

    with open(FILENAME, "w") as f:
        f.write(str(random.random()))

    mail = os.environ.get("EMAIL")
    commit_date = datetime(date.year, date.month, date.day, 6, 0, 0, tzinfo=None)
    command = f'git config --global user.email "{mail}"; $env:GIT_AUTHOR_DATE="{commit_date}"; $env:GIT_COMMITTER_DATE=$env:GIT_AUTHOR_DATE; git commit -m "commit"'

    subprocess_run(GIT_ADD)
    subprocess_run(command)
    subprocess_run(GIT_PUSH)


def get_sentence(filename: Path) -> dict[int, list[str]]:
    lines = read_csv(filename, sep=",", header=None).values.tolist()

    if len(lines) != WEEK_LEN:
        raise Exception("Wrong amount of rows")

    for line in lines:
        if len(line) > SENTENCE_LEN:
            raise Exception("Too long sentence")

    if not all(len(line) == len(lines[0]) for line in lines):
        raise Exception("Rows not equal")

    return {
        6: lines[0],  # sunday
        0: lines[1],  # monday
        1: lines[2],  # tuesday
        2: lines[3],  # wendesday
        3: lines[4],  # thursday
        4: lines[5],  # friday
        5: lines[6],  # saturday
    }


def sentence_to_datetimes(sentence: dict[int, list[int]]) -> list[date]:
    dates = []
    days_in_year = DAYS + calendar.isleap(YEAR)
    current_date = date(year=YEAR, month=1, day=1)
    for _ in range(0, days_in_year):
        week = __get_github_week(current_date)
        if week is None or week >= SENTENCE_LEN:
            current_date += timedelta(days=1)
            continue

        if sentence[current_date.weekday()][week]:
            dates.append(current_date)

        current_date += timedelta(days=1)

    return dates


def __get_github_week(current_date: date) -> Optional[int]:
    # 52 as first week until first monday:
    iso_week = current_date.isocalendar().week

    if current_date.month != 1 and iso_week > SENTENCE_LEN:
        return None

    if iso_week == 52 and current_date.weekday() != 6:
        return None

    if iso_week == 52:
        week = -1
    else:
        week = iso_week - 1

    if current_date.weekday() == 6:
        week += 1
    return week


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a file path as an argument.")
        sys.exit(1)

    if os.name != "nt":
        print("Only Windows OS is supported for now.")
        sys.exit(1)

    if os.environ.get("EMAIL") is None:
        print("Provide an email in env.")
        sys.exit(1)

    sentence = get_sentence(Path(sys.argv[1]))
    commit_dates = sentence_to_datetimes(sentence)
    for commit_date in commit_dates:
        commit_by_date(commit_date)

    print(f"Finished committing sentece from file: {sys.argv[1]}")
