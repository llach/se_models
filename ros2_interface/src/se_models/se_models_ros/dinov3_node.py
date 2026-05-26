import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import time

from se_models_msgs.srv import GetEmbeddings
from se_models.dinov3_client import Dinov3Client

class Dinov3Node(Node):
    def __init__(self):
        super().__init__('dinov3_node')
        
        self.declare_parameter('api_url', 'http://localhost:8002')
        api_url = self.get_parameter('api_url').value
        
        self.bridge = CvBridge()
        
        self.get_logger().info(f'Connecting to DINOv3 API at {api_url}...')
        while rclpy.ok():
            try:
                self.client = Dinov3Client(api_url)
                self.get_logger().info('Successfully connected and verified DINOv3 API health.')
                break
            except Exception as e:
                self.get_logger().warn(f'Failed to connect to DINOv3 API: {e}. Retrying in 2 seconds...')
                time.sleep(2)
                
        self.srv = self.create_service(GetEmbeddings, 'get_embeddings', self.get_embeddings_callback)
        self.get_logger().info('DINOv3 service is ready.')

    def get_embeddings_callback(self, request, response):
        self.get_logger().info('Received get_embeddings request.')
        
        try:
            # Convert ROS Image to CV2 Image
            cv_image = self.bridge.imgmsg_to_cv2(request.image, desired_encoding='passthrough')
            
            # Encode image to JPEG
            _, img_encoded = cv2.imencode('.jpg', cv_image)
            image_bytes = img_encoded.tobytes()
            
            # Run prediction via the client class
            start_time = time.time()
            client_resp = self.client.get_embeddings(image_bytes)
            end_time = time.time()
            
            self.get_logger().info(f"DINOv3 feature extraction took {end_time - start_time:.3f} seconds.")
            
            response.embeddings = client_resp.embeddings
            response.shape = client_resp.shape
            response.h_patches = client_resp.h_patches
            response.w_patches = client_resp.w_patches
            response.success = True
            response.error_message = ""
            
        except Exception as e:
            response.success = False
            response.error_message = str(e)
            self.get_logger().error(f"Failed to process request: {e}")
            
        return response

def main(args=None):
    rclpy.init(args=args)
    node = Dinov3Node()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
