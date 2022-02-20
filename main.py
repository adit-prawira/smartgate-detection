import cv2
import numpy as np
import logging
from pprint import pprint
from config.realsense import Realsense
from config.dnn_detection_model_ssd import DnnDetectionModelSSD
from threading import enumerate as enumerateThreads
from time import sleep
from utils.queue_package import QueuePackage
from utils.event_logs import EventLogs
from globals.app_queue import q
from globals.thread_names import *
from threads.keyboard_event_receiver_thread import KeyboardEventReceiverThread

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )


class ObjectDetectionRS(EventLogs):
    def __init__(self, allowObjectLogs=False, allowIndividualBoundingBox=False):
        self.name = OBJECT_DETECTION_RS_THREAD_NAME
        self.camera = Realsense()
        self.ssd = DnnDetectionModelSSD(allowedClassNames=["person", "cell phone",
                                                           "keyboard", "handbag",
                                                           "suitcase"])
        self.allowObjectLogs = allowObjectLogs
        self.allowIndividualBoundingBox = allowIndividualBoundingBox
        self.detectionCollections = []

        if not self.camera.hasRgbSensor():
            print("Camera is required to have Depth camera with Color Sensors")
            exit(0)
        self.camera.enableDepthStream()
        self.camera.enableColorStream()
        self.ssd.applyConfiguration()
        self.camera.pipeline.start(self.camera.config)

    def getName(self):
        return self.name  # get thread name

    def __kill(self):
        if len(list(q.queue)) > 0:
            # when there are items still exist in queue
            # clear all of those items during termination uting mutex
            with q.mutex:
                q.queue.clear()

        # Send signal to all threads to terminate
        content = {"terminate": True}
        terminationPackage = QueuePackage(ALL_THREADS, self.getName(), content)
        q.put(terminationPackage)
        self.logSending(ALL_THREADS, content)

        # Wait until all threads except the Main Thread are already terminated
        while len(enumerateThreads()) > 1:
            logging.debug("WAITING: Waiting for all threads to be terminated...")
            sleep(1)

        # After all other threads expect main threads are already terminated
        # reset camera hardware state
        logging.debug("TERMINATING: Gracefully terminating...")
        self.camera.reset()

    def run(self):
        while True:
            # program will keep running as long as queue stack is not
            # overloaded
            if not q.full():
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.__kill()
                    break

                if key == ord("c"):
                    content = {"cropping": True}
                    packageToCropRoi = QueuePackage(KEYBOARD_EVENT_RECEIVER_THREAD_NAME, self.getName(), content)
                    q.put(packageToCropRoi)
                    self.logSending(KEYBOARD_EVENT_RECEIVER_THREAD_NAME, content)

                try:
                    frames = self.camera.pipeline.wait_for_frames()
                    colorFrame = frames.get_color_frame()
                    collections = []
                    if not colorFrame:
                        continue  # if there is no color frame go back to the top of the loop

                    colorImage = np.asanyarray(colorFrame.get_data())
                    classIds, confidences, boundingBoxes = self.ssd.getDetection(colorImage)

                    if len(boundingBoxes) > 0:
                        indices = cv2.dnn.NMSBoxes(boundingBoxes, confidences, self.ssd.CONFIDENCE_THRESHOLD,
                                                   self.ssd.NMS_THRESHOLD)

                        # Get data of the detected object with SSD and NMS
                        for i in indices:
                            # extra security layer to make sure that all indices
                            # has values maximum values of the total allowed classes
                            if self.ssd.isWithinAllowedClasses(classIds[i]):
                                existingClasses = []
                                x, y, w, h = tuple(boundingBoxes[i])
                                if len(collections) > 0:
                                    existingClasses = [c["className"] for c in collections]

                                # Add detected object to the detectionCollection list
                                collections.append({
                                    "classId": classIds[i],
                                    "className": self.ssd.getClassName(classIds[i]),
                                    "confidence": confidences[i],
                                    "boundingBox": boundingBoxes[i],
                                    "objectId": existingClasses.count(self.ssd.getClassName(classIds[i])) + 1
                                })

                                if self.allowIndividualBoundingBox:
                                    cv2.rectangle(colorImage, (x, y), (x + w, y + h), (0, 255, 0), 2)
                                    cv2.putText(colorImage,
                                                f"{self.ssd.getClassName(classIds[i])} {round(confidences[i] * 100, 2)}%".upper(),
                                                (x + 10, y + 30), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)

                        # here is the section where we will merge any overlapping bounding box between
                        # objects and combine them into one compact object with multiple features
                        # the rendering will be performed here
                        # =============================== MERGING SECTION ===============================
                        if len(collections) > 0:
                            if self.allowObjectLogs:
                                pprint(collections)

                            confidences = [c["confidence"] for c in collections]
                            points = list(map(lambda data: data["boundingBox"], collections))
                            classesAndIds = [{"className": collections[i]["className"],
                                              "id": collections[i]["objectId"]}
                                             for i in range(len(collections))]

                            xi = min([point[0] for point in points])
                            yi = min([point[1] for point in points])
                            xf = max([point[2] + xi for point in points])
                            yf = max([point[3] + yi for point in points])
                            cv2.rectangle(colorImage, (xi, yi), (xf, yf), (0, 255, 0), 2)

                            for i in range(len(classesAndIds)):
                                name = classesAndIds[i]["className"]
                                objectId = classesAndIds[i]["id"]
                                cv2.putText(colorImage, f"{name}-{objectId}: {round(confidences[i] * 100, 2)}%".upper(),
                                            (xi + 10, yi + (i + 1) * 30), cv2.FONT_HERSHEY_DUPLEX,
                                            0.5, (0, 255, 0), 2)

                        cv2.namedWindow("Realsense object detection", cv2.WINDOW_AUTOSIZE)
                        cv2.imshow("Realsense", colorImage)

                except Exception as e:
                    print(e)
                    print("Handling non-existing detection data")
                    print("Gracefully terminating...")

        cv2.destroyAllWindows()


if __name__ == "__main__":
    kert = KeyboardEventReceiverThread(name=KEYBOARD_EVENT_RECEIVER_THREAD_NAME)
    odr = ObjectDetectionRS()
    kert.start()
    odr.run()
    kert.join()
