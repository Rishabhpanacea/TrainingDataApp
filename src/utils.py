import pydicom
import os
import numpy as np
from PIL import Image
import cv2 as cv2
import pydicom as dicom

def GetSegmentLabelDict(SegObjectPath):
    uniqueSegmentLabel = {}
    ds = pydicom.dcmread(SegObjectPath)
    SegmentSequence = ds['SegmentSequence']
    for item in SegmentSequence:
        SegmentLabel = item['SegmentLabel'].value
        SegmentNumber = item['SegmentNumber'].value
        uniqueSegmentLabel[SegmentNumber] = SegmentLabel
    return uniqueSegmentLabel

def CreateRequiredFolders(SopID, MaskDir, TrainingLabelDict):
    SegSopPath = os.path.join(MaskDir, SopID)
    os.makedirs(SegSopPath, exist_ok=True)
    for classes in TrainingLabelDict.keys():
        os.makedirs(os.path.join(SegSopPath, classes), exist_ok=True)
    return SegSopPath


def GenerateRemainingMasks(SegObjectPath, TrainingLabelDict, SegSopPath):
    ds = pydicom.dcmread(SegObjectPath)
    
    ReferencedSeriesSequence = ds['ReferencedSeriesSequence'][0]
    SeriesInstanceUID = ds['ReferencedSeriesSequence'][0]['SeriesInstanceUID']
    ReferencedInstanceSequence = ds['ReferencedSeriesSequence'][0]['ReferencedInstanceSequence']
    
    for item in ReferencedInstanceSequence:
        ReferencedSOPInstanceUID = item['ReferencedSOPInstanceUID'].value
        Filename = ReferencedSOPInstanceUID + '.png'
        for classes in TrainingLabelDict.keys():
            classFolderPath = os.path.join(SegSopPath ,classes)
            files = os.listdir(classFolderPath)
            if Filename not in files:
                ZerosArray = np.zeros((512, 512))
                ZerosArray = ZerosArray.astype(np.uint8)
                image = Image.fromarray(ZerosArray)
                ClassPath = os.path.join(SegSopPath, classes)
                imageFilePath = os.path.join(ClassPath , Filename)
                print(imageFilePath)
                image.save(imageFilePath, quality=100)



def window_image(img, window_center, window_width, intercept, slope, rescale=True):
    img = (img * slope + intercept)  # for translation adjustments given in the dicom file.
    img_min = window_center - window_width // 2  # minimum HU level
    img_max = window_center + window_width // 2  # maximum HU level
    img[img < img_min] = img_min  # set img_min for all HU levels less than minimum HU level
    img[img > img_max] = img_max  # set img_max for all HU levels higher than maximum HU level
    if rescale:
        img = (img - img_min) / (img_max - img_min) * 255.0
    return img
    
def get_first_of_dicom_field_as_int(x):
    # get x[0] as in int is x is a 'pydicom.multival.MultiValue', otherwise get int(x)
    if type(x) == dicom.multival.MultiValue:
        return int(x[0])
    else:
        return int(x)
        
def get_windowing(data):
    dicom_fields = [data[('0028', '1050')].value,  # window center
                    data[('0028', '1051')].value,  # window width
                    data[('0028', '1052')].value,  # intercept
                    data[('0028', '1053')].value]  # slope
    return [get_first_of_dicom_field_as_int(x) for x in dicom_fields]
    
def saveDicomAsJPEG(image_path):
    ds = dicom.dcmread(image_path)

    window_center, window_width, intercept, slope = get_windowing(ds)
    output = window_image(ds.pixel_array.astype(float), window_center, window_width, intercept, slope, rescale=False)

    new_image = output.astype(float)
    scaled_image = (np.maximum(new_image, 0) / new_image.max()) * 255.0
    scaled_image = np.uint8(scaled_image)

    return scaled_image


def GenerateTrainingdata(CTseriesPath, TrainingImagesPath):
    CTfiles = os.listdir(CTseriesPath)
    for filename in CTfiles:
        ds = pydicom.dcmread(os.path.join(CTseriesPath, filename))
        SOPInstanceUID = ds['SOPInstanceUID'].value
        pngfilename = SOPInstanceUID + '.png'
        pngPath = os.path.join(TrainingImagesPath , pngfilename)
        CTfilePath = os.path.join(CTseriesPath, filename)
        data = saveDicomAsJPEG(CTfilePath)
        image = Image.fromarray(data)
        image.save(pngPath, quality=100)