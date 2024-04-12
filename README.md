# radiology-simulator
Simulator to send images to DICOM server

## Requisites
* Install docker + docker-compose
* Download dataset
* Run: LOCAL_DATASET_PATH=/path/to/dataset docker-compose up


Currently, the code is adapted for the NIH chest X-ray dataset, found at: https://www.kaggle.com/datasets/nih-chest-xrays/data. For datasets with different formats, the code needs to be adapted for input file names, image paths, etc.
