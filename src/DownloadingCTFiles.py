import os
import pydicom
import requests
from config import SegFilesDir, RootDir, orthancURL, username, password

def main():
    CtScans = os.path.join(RootDir, 'CtScans')
    AllBleedSegFiles = os.listdir(SegFilesDir)
    os.makedirs(CtScans, exist_ok=True)

    wrongFiles = []
    for SegFile in AllBleedSegFiles:
        ds = pydicom.dcmread(os.path.join(SegFilesDir, SegFile))
        ReferencedSeriesInstanceUID = ds['ReferencedSeriesSequence'][0]['SeriesInstanceUID'].value
        SegInstanceURL = os.path.join(orthancURL,'instances', SegFile[:-4])
        CTseriesDirPath = os.path.join(CtScans, SegFile[:-4])
        os.makedirs(CTseriesDirPath, exist_ok=True)
        response = requests.get(SegInstanceURL, auth=(username, password))
        if response.status_code != 200:
            wrongFiles.append(SegFile)
        else:
            response = response.json()
            ParentSeries = response["ParentSeries"]
            ParentSeriesURL = os.path.join(orthancURL,'series', ParentSeries)
            response = requests.get(ParentSeriesURL, auth=(username, password))
            response = response.json()
            ParentStudy = response["ParentStudy"]
            ParentStudyURL = os.path.join(orthancURL, 'studies', ParentStudy)
            response = requests.get(ParentStudyURL, auth=(username, password))
            response = response.json()
            SeriesList = list(response["Series"])
            for seriesId in SeriesList:
                SeriesURL = os.path.join(orthancURL,'series', seriesId)
                response = requests.get(SeriesURL, auth=(username, password))
                response = response.json()
                if response['MainDicomTags']['SeriesInstanceUID'] == ReferencedSeriesInstanceUID:
                    Instances = response["Instances"]
                    for instance in Instances:
                        CTInstanceURL = os.path.join(orthancURL,'instances', instance, 'file')
                        response = requests.get(CTInstanceURL, auth=(username, password))
                        if response.status_code == 200:
                            file_name = instance + ".dcm"
                            instancePath = os.path.join(CTseriesDirPath, file_name)
                            with open(instancePath, "wb") as file:
                                file.write(response.content)
                            print(f"File saved as {instancePath}")
                        else:
                            print(f"Failed to download file. Status code: {response.status_code}")

    for filename in wrongFiles:
        os.remove(os.path.join(SegFilesDir , filename))

if __name__ == "__main__":
    main()
