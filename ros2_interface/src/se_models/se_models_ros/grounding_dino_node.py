import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import time

from se_models_msgs.srv import GetDetections
from se_models_msgs.msg import Detection, BoundingBox

from se_models.grounding_dino_client import GroundingDinoClient

class GroundingDinoNode(Node):
    def __init__(self):
        super().__init__('grounding_dino_node')
        
        self.declare_parameter('api_url', 'http://localhost:8000')
        api_url = self.get_parameter('api_url').value
        
        self.bridge = CvBridge()
        
        self.get_logger().info(f'Connecting to GroundingDINO API at {api_url}...')
        while rclpy.ok():
            try:
                self.client = GroundingDinoClient(api_url)
                self.get_logger().info('Successfully connected and verified GroundingDINO API health.')
                break
            except Exception as e:
                self.get_logger().warn(f'Failed to connect to GroundingDINO API: {e}. Retrying in 2 seconds...')
                time.sleep(2)
        
        self.srv = self.create_service(GetDetections, 'get_detections', self.get_detections_callback)
        self.get_logger().info('GroundingDINO service is ready.')

    def get_detections_callback(self, request, response):
        self.get_logger().info(f'Received request with prompt: "{request.prompt}"')
        
        if self.client is None:
            response.success = False
            response.error_message = "GroundingDinoClient was not initialized successfully due to connection error."
            self.get_logger().error(response.error_message)
            return response
            
        try:
            # Convert ROS Image to CV2 Image
            cv_image = self.bridge.imgmsg_to_cv2(request.image, desired_encoding='passthrough')
            
            # Encode image to JPEG
            _, img_encoded = cv2.imencode('.jpg', cv_image)
            image_bytes = img_encoded.tobytes()
            
            # Run prediction via the client class
            start_time = time.time()
            client_resp = self.client.predict(
                image_bytes=image_bytes,
                prompt=request.prompt,
                box_threshold=request.box_threshold,
                text_threshold=request.text_threshold
            )
            end_time = time.time()
            
            self.get_logger().info(f"Model prediction took {end_time - start_time:.3f} seconds.")
            
            for det in client_resp.detections:
                detection_msg = Detection()
                detection_msg.label = det.label
                detection_msg.confidence = det.confidence
                
                bbox_msg = BoundingBox()
                bbox_msg.x_min = det.bbox.x_min
                bbox_msg.y_min = det.bbox.y_min
                bbox_msg.x_max = det.bbox.x_max
                bbox_msg.y_max = det.bbox.y_max
                
                detection_msg.bbox = bbox_msg
                response.detections.append(detection_msg)
            
            response.success = True
            response.error_message = ""
            
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
