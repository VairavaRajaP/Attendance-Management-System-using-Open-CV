import json

from django.utils.timezone import now
from rest_framework import request

import jsontoxl
import os
import export_to_xl
import sqlite3
import cv2
from backend.align_custom import AlignCustom
from backend.face_feature import FaceFeature
from backend.mtcnn_detect import MTCNNDetect
from backend.tf_graph import FaceRecGraph
import sys
import numpy as np
import requests
from datetime import datetime


class Log:
    def auth(self):
        # scale_factor, rescales image for faster detection
        url = 'http://127.0.0.1:8000/attendance/'
        print("[INFO] camera sensor warming up...")
        # vs = cv2.VideoCapture(0)  # get input from webcam
        vs = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # get input from webcam
        # url = "https://192.168.0.104:8080"  # Your url might be different, check the app
        # vs = cv2.VideoCapture(url + "/video")
        datetime.now().time()
        # time_mid = datetime.strptime("12:30:00", "%H:%M:%S")

        time_end_less = datetime.strptime("15:59:30", "%H:%M:%S")
        time_end = datetime.strptime("16:00:00", "%H:%M:%S")


        while True:
            _, frame = vs.read()
            # print(frame)
            if frame is None:
                # print("Error")
                vs.release()
                cv2.destroyAllWindows()
                self.running()
            else:
                if (time_end_less < datetime.strptime(datetime.now().time().strftime("%H:%M:%S"),
                                                      "%H:%M:%S") < time_end):
                    conn = None
                    try:
                        # conn = sqlite3.connect("faculty_details.db")
                        conn = sqlite3.connect("db.sqlite3")
                    except sqlite3.Error as e:
                        print(e)

                    curr = conn.cursor()
                    url = 'http://127.0.0.1:8000/attendance/'
                    curr.execute("SELECT staff_id FROM main_staff WHERE is_active=True")

                    staffs_onroll = curr.fetchall()

                    today = datetime.now().strftime('%Y-%m-%d')
                    curr.execute("SELECT id FROM main_date WHERE date=?", [today])
                    date_id = curr.fetchone()[0]

                    # print(staffs_onroll)
                    for on_roll in staffs_onroll:
                        data = {"total_remarks": "Leave", "in_time": None, "out_time": None,
                                "work_duration": None, "forenoon_remarks": None, "afternoon_remarks": None,
                                "staff": on_roll[0], "date": date_id}
                        response = requests.post(url=url, json=data)

            # cv2.imshow("Captured face", frame)
            # u can certainly add a roi here but for the sake of a demo i'll just leave it as simple as this
                rects, landmarks = face_detect.detect_face(frame, 80)  # min face size is set to 80x80
                aligns = []
                positions = []

                for (i, rect) in enumerate(rects):
                    aligned_face, face_pos = aligner.align(160, frame, landmarks[i])
                    if len(aligned_face) == 160 and len(aligned_face[0]) == 160:
                        aligns.append(aligned_face)
                        positions.append(face_pos)
                    else:
                        print("Align face failed") #log

                if len(aligns) > 0:
                    features_arr = extract_feature.get_features(aligns)
                    person_name = self.findPeople(features_arr, positions)
                    # print(person_name)
                    if person_name[0][0] != "Unknown":

                        data = {"in_time": datetime.now().time().strftime("%H:%M:%S"), "out_time": None,
                                "work_duration": None, "forenoon_remarks": None, "afternoon_remarks": None,
                                "total_remarks": None, "staff": person_name[0][0], "date": person_name[0][3]}
                        response = requests.post(url=url, json=data)

                        if response.status_code == 400:  # and (datetime.strptime(datetime.now().time().strftime("%H:%M:%S"), "%H:%M:%S") > time_mid):
                            url = f'http://127.0.0.1:8000/attendance/{person_name[0][0]}/{person_name[0][3]}/'

                            data = {"in_time": person_name[0][1],
                                    "out_time": datetime.now().time().strftime("%H:%M:%S"),
                                    "work_duration": None, "staff": person_name[0][0],
                                    "forenoon_remarks": person_name[0][2], "afternoon_remarks": None,
                                    "total_remarks": None, "date": person_name[0][3]}
                            response = requests.put(url=url, json=data)

                        return person_name[0][4], datetime.now().date().strftime("%d/%m/%y"), \
                               datetime.now().time().strftime("%I:%M:%S %p")
                    vs.release()
                    cv2.destroyAllWindows()

    def running(self):
        user = Log()
        list_attend = []
        while True:
            logger = user.auth()
            print(logger)
            list_attend.append(logger)
            data_found = {logger[0]: {logger[1]: {"IN": logger[2], "OUT": ""}}}
            if os.path.isfile('attendance.json') and os.path.getsize('attendance.json'):
                with open('attendance.json', 'r+') as file:
                    data = json.load(file)
                    if logger[0] in data:
                        if logger[1] not in data[logger[0]]:
                            data[logger[0]].update(data_found[logger[0]])
                            if data[logger[0]][logger[1]]["OUT"] == "":
                                data[logger[0]][logger[1]]["IN"] = logger[2]
                                data[logger[0]][logger[1]]["OUT"] = logger[2]
                            else:
                                data[logger[0]][logger[1]]["OUT"] = logger[2]
                        else:
                            if data[logger[0]][logger[1]]["OUT"] == "":
                                data[logger[0]][logger[1]]["IN"] = logger[2]
                                data[logger[0]][logger[1]]["OUT"] = logger[2]
                            else:
                                data[logger[0]][logger[1]]["OUT"] = logger[2]
                    else:
                        data.update(data_found)
                        if data[logger[0]][logger[1]]["OUT"] == "":
                            data[logger[0]][logger[1]]["IN"] = logger[2]
                            data[logger[0]][logger[1]]["OUT"] = logger[2]
                        else:
                            data[logger[0]][logger[1]]["OUT"] = logger[2]
                    file.seek(0)
                    json.dump(data, file, indent=2)
            else:
                with open('attendance.json', 'w') as json_file:
                    data_found[logger[0]][logger[1]]["OUT"] = logger[2]
                    json.dump(data_found, json_file, indent=2)

            # Audio Out
            # audio.audio(logger[0])

            # first export format
            jsontoxl.export_to_xl()

            # second export format
            export_to_xl.jsontoxl()

            # print(list_attend)

    def findPeople(self, features_arr, positions, thres=0.6, percent_thres=75):
        '''
        :param features_arr: a list of 128d Features of all faces on screen
        :param positions: a list of face position types of all faces on screen
        :param thres: distance threshold
        :return: person name and percentage
        '''

        conn = None
        try:
            # conn = sqlite3.connect("faculty_details.db")
            conn = sqlite3.connect("db.sqlite3")
        except sqlite3.Error as e:
            print(e)

        curr = conn.cursor()
        curr.execute("SELECT * FROM main_facedata")
        rows = curr.fetchall()



        returnRes = []
        for (i, features_128D) in enumerate(features_arr):
            result = "Unknown"
            person_name = "Unknown"
            in_time = None
            date_id = None
            forenoon_remarks = None

            smallest = sys.maxsize

            for person_details, l_row, r_row, c_row in rows:  # zip(rows_left, rows_right, rows_center, rows_person):
                data_set = {"Left": tuple(map(float, (l_row[2:-2]).split(","))),
                            "Right": tuple(map(float, (r_row[2:-2]).split(","))),
                            "Center": tuple(map(float, (c_row[2:-2]).split(",")))}
                # print(data_set)
                person = person_details[0]
                today = datetime.now().strftime('%Y-%m-%d')
                # print(today)
                curr.execute("SELECT id FROM main_date WHERE date=?", [today])
                date_id = curr.fetchone()[0]
                # print(date_id)
                curr.execute("SELECT in_time, forenoon_remarks FROM main_attendance WHERE staff_id=? and date_id=?", [person, date_id])

                try:
                    in_time, forenoon_remarks = curr.fetchone()
                except Exception:
                    in_time = None
                    forenoon_remarks = None

                curr.execute("SELECT name FROM main_staff WHERE staff_id=?", person)
                person_name = curr.fetchone()[0]




                # curr.execute("SELECT time_slot_in, time_slot_out FROM main_timeslot WHERE id=?", str(time_slot_id))
                # time_slot_in, time_slot_out = curr.fetchone()

                person_data = [data_set[positions[i]]]
                for data in person_data:
                    distance = np.sqrt(np.sum(np.square(data - features_128D)))
                    if distance < smallest:
                        smallest = distance
                        result = person
                        in_time = in_time
                        date_id = date_id
                        person_name = person_name
                        forenoon_remarks = forenoon_remarks

            percentage = min(100, 100 * thres / smallest)
            if percentage <= percent_thres:
                result = "Unknown"
                person_name = "Unknown"
                in_time = None
                date_id = None
                forenoon_remarks = None



            returnRes.append((result, in_time, forenoon_remarks, date_id, person_name, percentage))
            return returnRes


if __name__ == '__main__':
    FRGraph = FaceRecGraph()
    aligner = AlignCustom()
    extract_feature = FaceFeature(FRGraph)
    face_detect = MTCNNDetect(FRGraph, scale_factor=2)
    user = Log()
    user.running()


