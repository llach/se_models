import rclpy
from rclpy.node import Node
import sys
import os
import json

from se_models_msgs.srv import GetSegmentation
from se_models_msgs.msg import Segmentation
from sensor_msgs.msg import Image
import cv2
import numpy as np
from cv_bridge import CvBridge

class TestSam2Client(Node):
    def __init__(self):
        super().__init__('test_sam2_client')
        self.cli = self.create_client(GetSegmentation, 'get_segmentation')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service "/get_segmentation" not available, waiting again...')
        self.req = GetSegmentation.Request()
        self.bridge = CvBridge()

    def send_request(self, image_path, bboxes_json):
        cv_img = cv2.imread(image_path)
        if cv_img is None:
            # Create a dummy image
            cv_img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.rectangle(cv_img, (100, 100), (300, 400), (0, 0, 255), -1)  # Red rectangle
            cv2.circle(cv_img, (500, 200), 50, (0, 255, 0), -1)             # Green circle
        self.cv_img = cv_img
        
        cv_bridge_msg = self.bridge.cv2_to_imgmsg(cv_img, encoding='bgr8')
        self.req.image = cv_bridge_msg
        self.req.bboxes_json = bboxes_json
        self.get_logger().info(f'Sending request with bboxes: {bboxes_json}')
        self.future = self.cli.call_async(self.req)

def main(args=None):
    rclpy.init(args=args)
    
    example_bboxes = [{"x_min": 100.0, "y_min": 100.0, "x_max": 300.0, "y_max": 400.0, "label": "red rectangle"}]
    bboxes_json = json.dumps(example_bboxes)

    client_node = TestSam2Client()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "stack.png")
    
    client_node.send_request(image_path, bboxes_json)
    
    while rclpy.ok():
        rclpy.spin_once(client_node)
        if client_node.future.done():
            try:
                response = client_node.future.result()
                if response.success:
                    client_node.get_logger().info('Success!')
                    client_node.get_logger().info(f'Received {len(response.segmentations)} segmentations.')
                    
                    import base64
                    overlay = client_node.cv_img.copy()
                    
                    for i, seg in enumerate(response.segmentations):
                        client_node.get_logger().info(
                            f'[{i}] confidence: {seg.confidence:.2f}, mask length: {len(seg.mask_base64)} chars'
                        )
                        # Decode base64 PNG mask
                        mask_bytes = base64.b64decode(seg.mask_base64)
                        mask_arr = np.frombuffer(mask_bytes, dtype=np.uint8)
                        mask_img = cv2.imdecode(mask_arr, cv2.IMREAD_GRAYSCALE)
                        
                        # Colorize mask with red/green
                        color = [0, 255, 0] if i == 0 else [0, 0, 255]
                        bool_mask = mask_img > 128
                        
                        # Blend overlay
                        alpha = 0.5
                        overlay[bool_mask] = (overlay[bool_mask] * (1 - alpha) + np.array(color) * alpha).astype(np.uint8)
                    
                    output_path = "/tmp/sam2_output.png"
                    cv2.imwrite(output_path, overlay)
                    client_node.get_logger().info(f"Saved mask overlay image to {output_path}")
                else:
                    client_node.get_logger().error(f'Server returned failure: {response.error_message}')
            except Exception as e:
                client_node.get_logger().error(f'Service call failed: {e}')
            break

    client_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
