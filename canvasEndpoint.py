import requests
import data.keys as keys
import pandas as pd
from datetime import datetime

BASE_URL = "https://mcpsmd.instructure.com"
TOKEN = keys.canvasKey

headers = {"Authorization": f"Bearer {TOKEN}"}

assignmentDf = pd.DataFrame()

def getCurrentDate():
    return datetime.now().strftime("%Y-%m-%d")

def getPreviousYearDate():
    yearAgo = datetime.now().replace(year=datetime.now().year - 1)
    return yearAgo.strftime("%Y-06-01")

def getAssignments(courseId, startDate, endDate):
    global assignmentDf

    params = {
        "per_page": 100
    }

    assignments = requests.get(
        f"{BASE_URL}/api/v1/courses/{courseId}/assignments",
        headers=headers,
        params=params
    ).json()

    assignmentNames = [assignment['name'] for assignment in assignments]
    assignmentDates = [assignment['due_at'] for assignment in assignments]
    assignmentPoints = [assignment['points_possible'] for assignment in assignments]

    assignmentDf = pd.DataFrame({
        "Name": assignmentNames,
        "Due Date": assignmentDates,
        "Points": assignmentPoints
    })

    for index, row in assignmentDf.iterrows():
        if  isinstance(row["Due Date"], str):
            dueDate = row["Due Date"][:10]

            if not startDate <= dueDate <= endDate:
                assignmentDf.drop(index, inplace=True)

        else:
            assignmentDf.drop(index, inplace=True)

    return assignmentDf

def getCourses():
    params = {
        "per_page": 100
    }

    courses = requests.get(
        f"{BASE_URL}/api/v1/courses",
        headers=headers,
        params=params
    ).json()

    codes = []
    ids = []
    startDates = []

    for course in courses:
        try:
            codes.append(course['course_code'])
        except:
            codes.append(0)

        try:
            ids.append(course['id'])
        except:
            ids.append(' ')

        try:
            startDates.append(course['created_at'])
        except:
            startDates.append(0)

    coursesDf = pd.DataFrame({
        "Code": codes,
        "ID": ids,
        "Start Date": startDates
    })

    for (index, row) in coursesDf.iterrows():
        if isinstance(row["Start Date"], str):
            coursesDf.at[index, "Start Date"] = row["Start Date"][:10]

            

            if row["Start Date"] <= getPreviousYearDate():
                coursesDf.drop(index, inplace=True)
                continue

        else:
            coursesDf.drop(index, inplace=True)
            continue

        if row["Code"] == 0:
            coursesDf.drop(index, inplace=True)
            continue
        
        if row["ID"] == ' ':
            coursesDf.drop(index, inplace=True)
            continue

    return coursesDf

def getAllCurrentAssignments():
    allAssignments = pd.DataFrame(columns=["Course", "Name", "Due Date", "Points"])

    coursesDf = getCourses()

    for (index, row) in coursesDf.iterrows():
        courseId = row["ID"]
        startDate = getPreviousYearDate()
        endDate = getCurrentDate()
        courseAssignments = getAssignments(courseId, startDate, endDate)
        
        for (aIndex, aRow) in courseAssignments.iterrows():
            allAssignments = pd.concat([allAssignments, pd.DataFrame({
                "Course": [row["Code"]],
                "Name": [aRow["Name"]],
                "Due Date": [aRow["Due Date"]],
                "Points": [aRow["Points"]]
            })], ignore_index=True)

    return allAssignments