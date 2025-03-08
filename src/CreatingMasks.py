import os
import pydicom
import numpy as np
import json
from PIL import Image
from config import SegFilesDir, RootDir, SegFilesDir, DictOfSegmentationPath, TrainingDataPath, datadict
from utils import *
def main():
    AllPatientIDFiles = os.listdir(SegFilesDir)
    AllBleedSegSop = {}
    for file in AllPatientIDFiles:
        filepath = os.path.join(SegFilesDir, file)
        ds = pydicom.dcmread(filepath)
        SOPInstanceUID = ds['SOPInstanceUID'].value
        AllBleedSegSop[SOPInstanceUID] = file
    
    os.makedirs(TrainingDataPath, exist_ok=True)
    MaskPath = os.path.join(TrainingDataPath, 'Masks')
    os.makedirs(MaskPath, exist_ok=True)

    with open(DictOfSegmentationPath, 'r', encoding='utf-8') as file:
        DictOfSegmentation = json.load(file)  # Load JSON content into a dictionary

    assert list(AllBleedSegSop.keys()) == list(DictOfSegmentation.keys())


    SegCount = 0
    for SopID in list(DictOfSegmentation.keys()):
        SegObjectPath = os.path.join(SegFilesDir, AllBleedSegSop[SopID])
        ds = pydicom.dcmread(SegObjectPath)
        pixelarray = ds.pixel_array
        
        uniqueSegmentLabel = GetSegmentLabelDict(SegObjectPath)
        SegSopPath = CreateRequiredFolders(SopID, MaskPath, datadict)
        SOPInstanceUID = ds['SOPInstanceUID'].value
        ReferencedSeriesSequence = ds['ReferencedSeriesSequence']
    
        classes = os.listdir(SegSopPath)
    
        i = 0
        for item in ds['PerFrameFunctionalGroupsSequence']:
            ReferencedSegmentNumber = item['SegmentIdentificationSequence'][0]['ReferencedSegmentNumber'].value
            ReferencedSOPInstanceUID = item['DerivationImageSequence'][0]['SourceImageSequence'][0]['ReferencedSOPInstanceUID'].value
            if len(pixelarray.shape) == 3:
                slice1 = pixelarray[i,:,:]
            else:
                slice1 = pixelarray
            # print(slice1.shape)
            i = i + 1
            # print(uniqueSegmentLabel[item['SegmentIdentificationSequence'][0]['ReferencedSegmentNumber'].value],' ',item['DerivationImageSequence'][0]['SourceImageSequence'][0]['ReferencedSOPInstanceUID'].value)
            if uniqueSegmentLabel[ReferencedSegmentNumber] in classes:
                image = Image.fromarray(slice1)
                imageFilename = ReferencedSOPInstanceUID + '.png'
                ClassPath = os.path.join(SegSopPath, uniqueSegmentLabel[ReferencedSegmentNumber])
                imageFilePath = os.path.join(ClassPath , imageFilename)
                print(imageFilePath)
                image.save(imageFilePath, quality=100)
    
        GenerateRemainingMasks(SegObjectPath, datadict, SegSopPath)
        SegCount = SegCount + 1


if __name__ == "__main__":
    main()