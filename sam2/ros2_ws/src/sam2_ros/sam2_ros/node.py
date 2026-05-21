import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import requests
import cv2
import numpy as np
import time

from sam2_interfaces.srv import GetSegmentation
from sam2_interfaces.msg import Segmentation

class Sam2Node(Node):
    def __init__(self):
        super().__init__('sam2_node')
        
        self.declare_parameter('api_url', 'http://localhost:8001/predict_sam2')
        self.api_url = self.get_parameter('api_url').value
        
        self.bridge = CvBridge()
        
        self.srv = self.create_service(GetSegmentation, 'get_segmentation', self.get_segmentation_callback)
        self.get_logger().info('SAM2 service is ready.')

    def get_segmentation_callback(self, request, response):
        self.get_logger().info(f'Received segmentation request with {len(request.bboxes_json)} bytes of bbox data.')
        
        try:
            # Convert ROS Image to CV2 Image
            cv_image = self.bridge.imgmsg_to_cv2(request.image, desired_encoding='passthrough')
            
            # Encode image to JPEG
            _, img_encoded = cv2.imencode('.jpg', cv_image)
            image_bytes = img_encoded.tobytes()
            
            # Send request to FastAPI server
            files = {'image': ('image.jpg', image_bytes, 'image/jpeg')}
            data = {
                'bboxes_json': request.bboxes_json
            }
            
            start_time = time.time()
            api_resp = requests.post(self.api_url, files=files, data=data)
            end_time = time.time()
            
            self.get_logger().info(f"Model prediction took {end_time - start_time:.3f} seconds.")
            
            if api_resp.status_code == 200:
                result = api_resp.json()
                segmentations = result.get('results', [])
                
                for seg in segmentations:
                    seg_msg = Segmentation()
                    seg_msg.mask_base64 = seg['mask_base64']
                    seg_msg.confidence = seg['confidence']
                    response.segmentations.append(seg_msg)
                
                response.success = True
                response.error_message = ""
            else:
                response.success = False
                response.error_message = f"API Error {api_resp.status_code}: {api_resp.text}"
                self.get_logger().error(response.error_message)
                
        except Exception as e:
            response.success = False
            response.error_message = str(e)
            self.get_logger().error(f"Failed to process request: {e}")
            
        return response

def main(args=None):
    rclpy.init(args=args)
    node = Sam2Node()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
