import cv2


class DnnDetectionModelSSD:
    CLASS_PATH = "./dataset/coco-ssd.names"
    CONFIG_PATH = "./dataset/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
    WEIGHT_PATH = "./dataset/frozen_inference_graph.pb"
    CONFIDENCE_THRESHOLD = 0.61

    # lower threshold will reduce chances of more overllaping boxes that detect the same object
    NMS_THRESHOLD = 0.3

    def __init__(self, allowedClassNames=None):
        if allowedClassNames is None:
            allowedClassNames = []
        self.classNames = []
        self.allClasses = []
        with open(self.CLASS_PATH, "rt") as file:
            classes = file.read().rstrip("\n").split("\n")
            self.allClasses = classes
            if len(allowedClassNames) > 0:
                classes = list(filter(lambda name: name in allowedClassNames, classes))
            self.classNames = classes

        self.network = cv2.dnn_DetectionModel(self.WEIGHT_PATH, self.CONFIG_PATH)

    def applyConfiguration(self):
        self.network.setInputSize(320, 320)
        self.network.setInputScale(1.0 / 127.5)
        self.network.setInputMean((127.5, 127.5, 127.5))
        self.network.setInputSwapRB(True)

    def getDetection(self, frame):
        return self.network.detect(frame, confThreshold=self.CONFIDENCE_THRESHOLD)

    def isWithinAllowedClasses(self, classId):
        return self.allClasses[classId - 1] in self.classNames

    def getClassName(self, classId: int):
        targetClassName = self.allClasses[classId - 1]
        return self.classNames[self.classNames.index(targetClassName)]
