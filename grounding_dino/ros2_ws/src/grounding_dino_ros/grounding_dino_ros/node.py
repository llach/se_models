import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import requests
import cv2
import numpy as np
import time

from grounding_dino_interfaces.srv import GetDetections
from grounding_dino_interfaces.msg import Detection, BoundingBox

class GroundingDinoNode(Node):
    def __init__(self):
        super().__init__('grounding_dino_node')
        
        self.declare_parameter('api_url', 'http://localhost:8000/predict_grounding_dino')
        self.api_url = self.get_parameter('api_url').value
        
        self.bridge = CvBridge()
        
        self.srv = self.create_service(GetDetections, 'get_detections', self.get_detections_callback)
        self.get_logger().info('GroundingDINO service is ready.')

    def get_detections_callback(self, request, response):
        self.get_logger().info(f'Received request with prompt: "{request.prompt}"')
        
        try:
            # Convert ROS Image to CV2 Image
            cv_image = self.bridge.imgmsg_to_cv2(request.image, desired_encoding='passthrough')
            
            # Encode image to JPEG
            _, img_encoded = cv2.imencode('.jpg', cv_image)
            image_bytes = img_encoded.tobytes()
            
            # Send request to FastAPI server
            files = {'image': ('image.jpg', image_bytes, 'image/jpeg')}
            data = {
                'prompt': request.prompt,
                'box_threshold': request.box_threshold,
                'text_threshold': request.text_threshold
            }
            
            start_time = time.time()
            api_resp = requests.post(self.api_url, files=files, data=data)
            end_time = time.time()
            
            self.get_logger().info(f"Model prediction took {end_time - start_time:.3f} seconds.")
            
            if api_resp.status_code == 200:
                result = api_resp.json()
                detections = result.get('detections', [])
                
                for det in detections:
                    detection_msg = Detection()
                    detection_msg.label = det['label']
                    detection_msg.confidence = det['confidence']
                    
                    bbox_msg = BoundingBox()
                    bbox_msg.x_min = det['bbox']['x_min']
                    bbox_msg.y_min = det['bbox']['y_min']
                    bbox_msg.x_max = det['bbox']['x_max']
                    bbox_msg.y_max = det['bbox']['y_max']
                    
                    detection_msg.bbox = bbox_msg
                    response.detections.append(detection_msg)
                
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
    node = GroundingDinoNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
