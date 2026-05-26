import rclpy
from rclpy.node import Node
import sys
import os

from se_models_msgs.srv import GetEmbeddings
from sensor_msgs.msg import Image
import cv2
import numpy as np
from cv_bridge import CvBridge

class TestDinov3Client(Node):
    def __init__(self):
        super().__init__('test_dinov3_client')
        self.cli = self.create_client(GetEmbeddings, 'get_embeddings')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service "/get_embeddings" not available, waiting again...')
        self.req = GetEmbeddings.Request()
        self.bridge = CvBridge()

    def send_request(self, image_path):
        cv_img = cv2.imread(image_path)
        if cv_img is None:
            cv_img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.rectangle(cv_img, (100, 100), (300, 400), (0, 0, 255), -1)  # Red rectangle
            cv2.circle(cv_img, (500, 200), 50, (0, 255, 0), -1)             # Green circle
        
        cv_bridge_msg = self.bridge.cv2_to_imgmsg(cv_img, encoding='bgr8')
        self.req.image = cv_bridge_msg
        self.get_logger().info('Sending request to /get_embeddings...')
        self.future = self.cli.call_async(self.req)

def main(args=None):
    rclpy.init(args=args)
    
    client_node = TestDinov3Client()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "stack.png")
    
    client_node.send_request(image_path)
    
    while rclpy.ok():
        rclpy.spin_once(client_node)
        if client_node.future.done():
            try:
                response = client_node.future.result()
                if response.success:
                    client_node.get_logger().info('Success!')
                    client_node.get_logger().info(f'Shape of features: {list(response.shape)}')
                    client_node.get_logger().info(f'Patch resolution: h_patches={response.h_patches}, w_patches={response.w_patches}')
                    client_node.get_logger().info(f'Number of flattened values: {len(response.embeddings)}')
                    
                    expected_len = response.shape[0] * response.shape[1]
                    if len(response.embeddings) == expected_len:
                        client_node.get_logger().info("Verification PASSED: Flattened length matches shape!")
                    else:
                        client_node.get_logger().error(f"Verification FAILED: Flattened length is {len(response.embeddings)}, expected {expected_len}")
                else:
                    client_node.get_logger().error(f'Server returned failure: {response.error_message}')
            except Exception as e:
                client_node.get_logger().error(f'Service call failed: {e}')
            break

    client_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
