import os
import requests
from config import orthancURL, username, password, SegFilesDir

def main():
    StudiesURL = os.path.join(orthancURL,'studies')
    response = requests.get(StudiesURL, auth=(username, password))
    StudiesList = list(response.json())
    for studyID in StudiesList:
        studyURL = os.path.join(orthancURL,'studies', studyID)
        response = requests.get(studyURL, auth=(username, password))
        response = response.json()
        if response["PatientMainDicomTags"]["PatientName"].startswith("Bleed") or response["PatientMainDicomTags"]["PatientName"].startswith("bleed"):
            PatientName = response["PatientMainDicomTags"]["PatientName"]
            SeriesList = list(response["Series"])
            for seriesID in SeriesList:
                SeriesURL = os.path.join(orthancURL, 'series', seriesID)
                response = requests.get(SeriesURL, auth=(username, password))
                response = response.json() 
                if response["MainDicomTags"]["Modality"] == "SEG":
                    print(PatientName)
                    InstancesList = list(response["Instances"])
                    for instanceID in InstancesList:
                        InstanceURL = os.path.join(orthancURL, 'instances', instanceID, 'file')
                        response = requests.get(InstanceURL, auth=(username, password))
                        if response.status_code == 200:
                            file_name = instanceID + ".dcm"
                            instancePath = os.path.join(SegFilesDir, file_name)
                            with open(instancePath, "wb") as file:
                                file.write(response.content)
                            print(f"File saved as {instancePath}")
                        else:
                            print(f"Failed to download file. Status code: {response.status_code}")

if __name__ == "__main__":
    main()
