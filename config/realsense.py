import pyrealsense2 as rs
from time import sleep


class Realsense:

    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.context = rs.context()
        pipelineWrapper = rs.pipeline_wrapper(self.pipeline)
        pipelineProfile = self.config.resolve(pipelineWrapper)
        self.device = pipelineProfile.get_device()
        self.deviceProductLine = str(self.device.get_info(rs.camera_info.product_line))
        
    def hasRgbSensor(self):
        for s in self.device.sensors:
            if s.get_info(rs.camera_info.name) == "RGB Camera":
                return True
        return False
    
    def enableDepthStream(self):
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    
    def enableColorStream(self):
        if self.deviceProductLine == 'L500':
            self.config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
        else:
            self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
            
    def reset(self):
        self.pipeline.stop()
        for device in self.context.query_devices():
            device.hardware_reset()
        sleep(0.5)