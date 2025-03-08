import os
import pydicom
import numpy as np
from config import SegFilesDir

def main():
    DirList = os.listdir(SegFilesDir)
    for SegFile in DirList:
        SegPath = os.path.join(SegFilesDir, SegFile)
        ds = pydicom.dcmread(SegPath)
        try:
            pixelarray = ds.pixel_array
            if len(np.unique(pixelarray)) < 2:
                os.remove(SegPath)
        except:
            os.remove(SegPath)
            print("wrong file")
        print(pixelarray.shape)

if __name__ == "__main__":
    main()
