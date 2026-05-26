import rclpy
from rclpy.node import Node
import sys
import os

from se_models_msgs.srv import GetDetections
from sensor_msgs.msg import Image
import cv2
import numpy as np
from cv_bridge import CvBridge

class TestGroundingDinoClient(Node):
    def __init__(self):
        super().__init__('test_grounding_dino_client')
        self.cli = self.create_client(GetDetections, 'get_detections')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service "/get_detections" not available, waiting again...')
        self.req = GetDetections.Request()
        self.bridge = CvBridge()

    def send_request(self, image_path, prompt):
        cv_img = cv2.imread(image_path)
        if cv_img is None:
            # Create a dummy image (e.g. if run without host image file)
            cv_img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.rectangle(cv_img, (100, 100), (300, 400), (0, 0, 255), -1)  # Red rectangle
            cv2.circle(cv_img, (500, 200), 50, (0, 255, 0), -1)             # Green circle
        self.cv_img = cv_img
        
        cv_bridge_msg = self.bridge.cv2_to_imgmsg(cv_img, encoding='bgr8')
        self.req.image = cv_bridge_msg
        self.req.prompt = prompt
        self.req.box_threshold = 0.35
        self.req.text_threshold = 0.25
        self.get_logger().info(f'Sending request with prompt: "{prompt}"')
        self.future = self.cli.call_async(self.req)

def main(args=None):
    rclpy.init(args=args)
    if len(sys.argv) < 2:
        prompt = "red rectangle"
    else:
        prompt = sys.argv[1]

    client_node = TestGroundingDinoClient()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "stack.png")
    
    client_node.send_request(image_path, prompt)
    
    while rclpy.ok():
        rclpy.spin_once(client_node)
        if client_node.future.done():
            try:
                response = client_node.future.result()
                if response.success:
                    client_node.get_logger().info('Success!')
                    client_node.get_logger().info(f'Found {len(response.detections)} detections.')
                    
                    overlay = client_node.cv_img.copy()
                    
                    for i, det in enumerate(response.detections):
                        bbox = det.bbox
                        client_node.get_logger().info(
                            f'[{i}] label: "{det.label}", conf: {det.confidence:.2f}, '
                            f'bbox: [{bbox.x_min:.1f}, {bbox.y_min:.1f}, {bbox.x_max:.1f}, {bbox.y_max:.1f}]'
                        )
                        
                        # Draw bounding box
                        x_min, y_min = int(bbox.x_min), int(bbox.y_min)
                        x_max, y_max = int(bbox.x_max), int(bbox.y_max)
                        cv2.rectangle(overlay, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
                        
                        # Draw label
                        label_text = f"{det.label} ({det.confidence:.2f})"
                        cv2.putText(overlay, label_text, (x_min, max(y_min - 5, 15)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                                    
                    output_path = "/tmp/grounding_dino_output.png"
                    cv2.imwrite(output_path, overlay)
                    client_node.get_logger().info(f"Saved detection overlay image to {output_path}")
                else:
                    client_node.get_logger().error(f'Server returned failure: {response.error_message}')
            except Exception as e:
                client_node.get_logger().error(f'Service call failed: {e}')
            break

    client_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
