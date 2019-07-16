# Moon
## Description
This is an Object Detection assistant tool which you can see Ground Truth bounding boxes and your prediction bounding boxes on images.

## Requirement
- Python 3
- Pyqt 5
- opencv-python

## Usage
- Step 1: Commond: `python main.py`
- Step 2: Choose Prediction Folder
  - Note that this folder contains your prediction `.txt` files, filenames are the same with picture names' prefix.
  - In `.txt` prediction files, data of each line organized in following format:
  `name score xmin ymin xmax ymax`, 
- Step 3: Choose Images Folder
  - All the corresponding images of prediction files should be exist in this folder.
- Step 4: Choose xml Folder
  - All the corresponding xml ground truth files of prediction files should be exist in this folder.
  