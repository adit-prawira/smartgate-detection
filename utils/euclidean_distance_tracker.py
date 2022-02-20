import math
from pprint import pprint

# Euclidean distance tracker class
class EuclideanDistanceTracker:
    def __init__(self) -> None:
        self.centerPoints = {} # this will store the center point of detected object
        self.id = 0 # this will be the primary key of a detected object which will increase by 1
    def update(self, detectionCollections):
        objectBoundingBoxDicts = []
        for detection in detectionCollections:
            x, y, w, h = detection["boundingBox"]
            centerX = (2*x + w)//2
            centerY = (2*y + h)//2
            
            # this will find out if the same object is being detected
            isSameObject = False
            print("The fucking item", self.centerPoints.items())
            for id, point in self.centerPoints.items():
                print("the fucking ID", id, "and the fucking point", point)
                xCoordinate, yCoordinate = point
                distance = math.hypot(centerX - xCoordinate, centerY - yCoordinate)
                print("Distance", distance)
                if distance < 25:
                    self.centerPoints[id] = (centerX, centerY)
                    className = detection["className"]
                    objectBoundingBoxDicts.append({
                        "id": self.id,
                        "label": f"{className} {self.id}",
                        "boundingBox":[x, y, w, h]
                    })
                    isSameObject = True
                    break
            print("Is this the same fucking object? ", isSameObject)
            if not isSameObject:
                print("NOT THE SAME OBJECT")
                self.centerPoints[self.id] = (centerX, centerY)
                className = detection["className"]
                objectBoundingBoxDicts.append({
                    "id": self.id,
                    "label": f"{className} {self.id}",
                    "boundingBox":[x, y, w, h]
                })
                self.id += 1
        print("boundingboxDicts")
        pprint(objectBoundingBoxDicts)
        print("center points")
        pprint(self.centerPoints)    
        # Clean dictionary by center points to remove IDs that are not used anymore
        newCenterPoints = {}
        for obbDicts in objectBoundingBoxDicts:
            try:
                objectId = obbDicts["id"]
                center = self.centerPoints[objectId]
                newCenterPoints[objectId] = center
            except Exception as e:
                print(e)
        
        # # Update dictionary with IDs that are not being used
        self.centerPoints = newCenterPoints.copy()
        
        return objectBoundingBoxDicts