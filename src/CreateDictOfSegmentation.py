import os
import pydicom
import numpy as np
from config import SegFilesDir
import json

def main():
    files = os.listdir(SegFilesDir)
    DictOfSegmentation = {}
    for i in range(len(files)):
        file = os.path.join(SegFilesDir, files[i])
        ds = pydicom.dcmread(file)
        SOPInstanceUID = ds['SOPInstanceUID'].value
        DictOfSegmentation[SOPInstanceUID] = {}
        for item in ds['PerFrameFunctionalGroupsSequence']:
            ReferencedSegmentNumber = item['SegmentIdentificationSequence'][0]['ReferencedSegmentNumber'].value
            ReferencedSOPInstanceUID = item['DerivationImageSequence'][0]['SourceImageSequence'][0]['ReferencedSOPInstanceUID'].value
            if ReferencedSegmentNumber not in DictOfSegmentation[SOPInstanceUID].keys():
                DictOfSegmentation[SOPInstanceUID][ReferencedSegmentNumber] = [ReferencedSOPInstanceUID]
            else:
                DictOfSegmentation[SOPInstanceUID][ReferencedSegmentNumber].append(ReferencedSOPInstanceUID)
            print(item['SegmentIdentificationSequence'][0]['ReferencedSegmentNumber'].value,' ',item['DerivationImageSequence'][0]['SourceImageSequence'][0]['ReferencedSOPInstanceUID'].value)
        


    with open("DictOfSegmentation.json", "w") as file:
        json.dump(DictOfSegmentation, file, indent=4)  # 'indent' makes it more readable

if __name__ == "__main__":
    main()