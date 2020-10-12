import cv2
import numpy as np
import time

class HMap:
    def __init__(self, width, height, name, fade_interval=2):
        self.width = width
        self.height = height
        self.name = name
        self.accum_image = np.zeros((self.height, self.width), np.uint8)
        self.heatmap = np.zeros((self.height, self.width), np.uint8)
        
        self.fade_interval = fade_interval
        self.st = time.time()
    
    def reset_heatmap(self):
        self.accum_image = self.adjust_brightness_contrast(self.accum_image, brightness=-2)
        self.accum_image = cv2.blur(self.accum_image, (55,55))
    
    def adjust_brightness_contrast(self, image, brightness=0., contrast=0.):
        return cv2.addWeighted(image, 1 + float(contrast) / 100., image, 0, float(brightness))
        
    def get_mask_from_bbox(self, x1,y1,x2,y2):
        cx,cy = int(x1+(x2)/2), int(y1+(y2)/2)
        mask = np.zeros((self.height, self.width), np.uint8)
        radius = 20 #int(((x2-x1)+(y2-y1))/2)
        mask = cv2.circle(mask, (x1+20,y1+20), radius, (75,75,75), -1)
        mask = cv2.blur(mask, (105,105), cv2.BORDER_DEFAULT)
        return mask
        
    def apply_color_map(self, x1,y1,x2,y2):
        if time.time() - self.st > self.fade_interval:
            self.st = time.time()
            self.reset_heatmap()

        # create a mask from image and add it to accum_image
        mask  = self.get_mask_from_bbox(x1,y1,x2,y2)
        self.accum_image = cv2.add(self.accum_image, mask)
        self.heatmap = cv2.applyColorMap(self.accum_image, cv2.COLORMAP_JET)

    def get_heatmap(self, frame):
        frame = cv2.addWeighted(frame, 0.7, self.heatmap, 0.5, 0) 
        return frame