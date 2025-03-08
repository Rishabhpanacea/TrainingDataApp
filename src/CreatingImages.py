import os
import pydicom
import shutil
from config import SegFilesDir, RootDir, SegFilesDir, DictOfSegmentationPath, TrainingDataPath, datadict
from utils import *

def main():
    DicomCTseriesPath = os.path.join(RootDir, 'CtScans')
    DicomCTseries = os.listdir(DicomCTseriesPath)
    SegFiles = os.listdir(SegFilesDir)
    TrainingimagesPath = os.path.join(TrainingDataPath, 'Images')
    os.makedirs(TrainingimagesPath, exist_ok=True)


    for SegFilename in SegFiles:
        SegPath = os.path.join(SegFilesDir, SegFilename)
        ds = pydicom.dcmread(SegPath)
        ReferencedInstanceSequence = ds['ReferencedSeriesSequence'][0]['ReferencedInstanceSequence'].value
        ReferenceSeriesListBySeg = []
        for item in ReferencedInstanceSequence:
            ReferenceSeriesListBySeg.append(item['ReferencedSOPInstanceUID'].value)
        ReferenceSeriesListBySeg = sorted(ReferenceSeriesListBySeg)
        if SegFilename[:-4] in DicomCTseries:
            CurrentCTseriesPath = os.path.join(DicomCTseriesPath, SegFilename[:-4])
            CurrentSeriesFiles = os.listdir(CurrentCTseriesPath)
            ReferenceSeriesListByCTFolder = []
            for CTfilename in CurrentSeriesFiles:
                ds = pydicom.dcmread(os.path.join(CurrentCTseriesPath, CTfilename))
                ReferenceSeriesListByCTFolder.append(ds['SOPInstanceUID'].value)
            ReferenceSeriesListByCTFolder = sorted(ReferenceSeriesListByCTFolder)
            if ReferenceSeriesListByCTFolder == ReferenceSeriesListBySeg:
                GenerateTrainingdata(CurrentCTseriesPath, TrainingimagesPath)
                print("yess")
            else:
                shutil.rmtree(CurrentCTseriesPath)
                print("no")

if __name__ == "__main__":
    main()