{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "57bb5dcb-6dc4-4720-871c-997601a43951",
   "metadata": {},
   "outputs": [],
   "source": [
    "from ultralytics import YOLO\n",
    "import cv2\n",
    "\n",
    "import util\n",
    "from sort.sort import *\n",
    "from utill import get_car, read_license_plate, write_csv\n",
    "\n",
    "results= {}\n",
    "\n",
    "mot_tracker=Sort()\n",
    "\n",
    "# load models\n",
    "coco_model= YOLO('yolov8n.pt')\n",
    "license_plate_detector=YOLO('./models/license_plate_detector.pt')\n",
    "\n",
    "# load video\n",
    "cap = cv2.VideoCapture('./sample.mp4')\n",
    "\n",
    "vehicles = [2, 3, 5, 7] # vehicles classes\n",
    "\n",
    "# read Frames\n",
    "frame_nmr = -1\n",
    "ret = True\n",
    "while ret:\n",
    "    frame_nmr += 1\n",
    "    ret,frame=cap.read()\n",
    "    if ret:\n",
    "        results[frame_nmr] = {}\n",
    "        # detect vehicles\n",
    "        detections = coco_model(frame)[0]\n",
    "        detections_ = []\n",
    "        for detection in detection.boxes.data.tolist():\n",
    "            x1, y1, x2, y2, score, class_id = detection\n",
    "            if int(class_id) in vehicles:\n",
    "                detections_.append([x1, y1, x2, y2, score])\n",
    "\n",
    "        # track vehicles\n",
    "        track_ids = mot_tracker.update(np.asarray(detections_))\n",
    "\n",
    "        # detect license plates\n",
    "        license_plates = license_plate_detector(frame)[0]\n",
    "        for license_plate in license_plates.boxes.data.tolist():\n",
    "            x1, y1, x2, y2, score, class_id = license_plate\n",
    "            # assign license plate to car\n",
    "            xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)\n",
    "\n",
    "\n",
    "            if car_id != -1 :\n",
    "\n",
    "                # crop license plate\n",
    "                license_plate_crop = frame[int(y1):int(y2), int(x1): int(x2), :]\n",
    "\n",
    "                # process license plate\n",
    "                license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)\n",
    "                _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)\n",
    "\n",
    "                # read license plate number\n",
    "                license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)\n",
    "\n",
    "                if license_plate_text is not None:\n",
    "                    results[frame_nmr][car_id] = {'car': {'bbox': [xcar1, ycar1, xcar2, ycar2]},\n",
    "                                                  'license_plate': {'bbox': [x1, y1, x2, y2],\n",
    "                                                                    'text': license_plate_text,\n",
    "                                                                    'bbox_score': score,\n",
    "                                                                    'text_score': license_plate_text_score}}\n",
    "\n",
    "# write results\n",
    "write_csv(results, './test.csv')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "996d94da-173d-463c-b340-90629250ad4d",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
