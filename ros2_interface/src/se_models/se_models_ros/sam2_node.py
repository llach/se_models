import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import time

from se_models_msgs.srv import GetSegmentation
from se_models_msgs.msg import Segmentation

from se_models.sam2_client import Sam2Client

class Sam2Node(Node):
    def __init__(self):
        super().__init__('sam2_node')
        
        self.declare_parameter('api_url', 'http://localhost:8001')
        api_url = self.get_parameter('api_url').value
        
        self.bridge = CvBridge()
        
        self.get_logger().info(f'Connecting to SAM2 API at {api_url}...')
        while rclpy.ok():
            try:
                self.client = Sam2Client(api_url)
                self.get_logger().info('Successfully connected and verified SAM2 API health.')
                break
            except Exception as e:
                self.get_logger().warn(f'Failed to connect to SAM2 API: {e}. Retrying in 2 seconds...')
                time.sleep(2)
            
        self.srv = self.create_service(GetSegmentation, 'get_segmentation', self.get_segmentation_callback)
        self.get_logger().info('SAM2 service is ready.')

    def get_segmentation_callback(self, request, response):
        self.get_logger().info(f'Received segmentation request with {len(request.bboxes_json)} bytes of bbox data.')
        
        if self.client is None:
            response.success = False
            response.error_message = "Sam2Client was not initialized successfully due to connection error."
            self.get_logger().error(response.error_message)
            return response
            
        try:
            # Convert ROS Image to CV2 Image
            cv_image = self.bridge.imgmsg_to_cv2(request.image, desired_encoding='passthrough')
            
            # Encode image to JPEG
            _, img_encoded = cv2.imencode('.jpg', cv_image)
            image_bytes = img_encoded.tobytes()
            
            import json
            try:
                boxes = json.loads(request.bboxes_json)
            except Exception as e:
                boxes = []
                self.get_logger().error(f"Failed to parse bboxes_json: {e}")

            # Normalize box schemas to the format expected by the SAM2 server
            normalized_boxes = []
            for b in boxes:
                if isinstance(b, dict):
                    if 'x_min' in b and 'y_min' in b and 'x_max' in b and 'y_max' in b:
                        normalized_boxes.append({
                            'x_min': float(b['x_min']),
                            'y_min': float(b['y_min']),
                            'x_max': float(b['x_max']),
                            'y_max': float(b['y_max'])
                        })
                    elif 'box_2d' in b and len(b['box_2d']) == 4:
                        box_2d = b['box_2d']
                        normalized_boxes.append({
                            'x_min': float(box_2d[0]),
                            'y_min': float(box_2d[1]),
                            'x_max': float(box_2d[2]),
                            'y_max': float(box_2d[3])
                        })
                    elif 'bbox' in b and isinstance(b['bbox'], dict):
                        bbox = b['bbox']
                        normalized_boxes.append({
                            'x_min': float(bbox['x_min']),
                            'y_min': float(bbox['y_min']),
                            'x_max': float(bbox['x_max']),
                            'y_max': float(bbox['y_max'])
                        })

            # Workaround for server-side array squeezing error when N = 1
            duplicated = False
            if len(normalized_boxes) == 1:
                normalized_boxes = [normalized_boxes[0], normalized_boxes[0]]
                duplicated = True

            server_bboxes_json = json.dumps(normalized_boxes)

            # Run prediction via the client class
            start_time = time.time()
            client_resp = self.client.predict(
                image_bytes=image_bytes,
                bboxes_json=server_bboxes_json
            )
            end_time = time.time()
            
            self.get_logger().info(f"Model prediction took {end_time - start_time:.3f} seconds.")
            
            results_to_process = client_resp.results
            if duplicated and len(results_to_process) == 2:
                results_to_process = [results_to_process[0]]

            for seg in results_to_process:
                seg_msg = Segmentation()
                seg_msg.mask_base64 = seg.mask_base64
                seg_msg.confidence = seg.confidence
                response.segmentations.append(seg_msg)
            
            response.success = True
            response.error_message = ""
            
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
