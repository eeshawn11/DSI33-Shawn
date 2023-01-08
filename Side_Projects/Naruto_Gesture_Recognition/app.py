import os
import numpy as np
import streamlit as st

import tensorflow as tf
from object_detection.utils import label_map_util, config_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder
import cv2

# set up paths for easier reference
ANNOTATION_PATH = './annotations'
MODEL_PATH = './models/my_ssd_mobilenet_v2_fpnlite'
LOG_PATH = MODEL_PATH + '/train'
CONFIG_PATH = MODEL_PATH + '/pipeline.config'
CHECKPOINT_PATH = MODEL_PATH

with st.experimental_singleton():
    def build_model():
    # load pipeline config and build model
        configs = config_util.get_configs_from_pipeline_file(CONFIG_PATH)
        detection_model = model_builder.build(model_config=configs['model'], is_training=False)
        return detection_model

detection_model = build_model()

# restore checkpoint
ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
ckpt.restore(os.path.join(CHECKPOINT_PATH, 'ckpt-13')).expect_partial()

@tf.function
def detect_fn(image):
    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)
    return detections

def __draw_label(img, text, pos, bg_color):
   font_face = cv2.FONT_HERSHEY_SIMPLEX
   scale = 0.4
   color = (0, 0, 0)
   thickness = cv2.FILLED
   margin = 2
   txt_size = cv2.getTextSize(text, font_face, scale, thickness)

   end_x = pos[0] + txt_size[0][0] + margin
   end_y = pos[1] - txt_size[0][1] - margin

   cv2.rectangle(img, pos, (end_x, end_y), bg_color, thickness)
   cv2.putText(img, text, pos, font_face, scale, color, 1, cv2.LINE_AA)

category_index = label_map_util.create_category_index_from_labelmap(ANNOTATION_PATH+'/label_map.pbtxt')

def run_capture():
    # setup CV2 capture
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    while True:
        ret, frame = cap.read()
        image_np = np.array(frame)

        if ret == True:
            __draw_label(frame, "'Q' to exit", (20,20), (255,0,0))

        input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
        detections = detect_fn(input_tensor)

        num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
        detections['num_detections'] = num_detections

        detections['detection_classes'] = detections['detection_classes'].astype(np.int32)

        label_id_offset = 1
        image_np_with_detections = image_np.copy()

        viz_utils.visualize_boxes_and_labels_on_image_array(
            image_np_with_detections,
            detections['detection_boxes'],
            detections['detection_classes']+label_id_offset,
            detections['detection_scores'],
            category_index,
            use_normalized_coordinates=True,
            max_boxes_to_draw=1,
            min_score_thresh=0.85,
            agnostic_mode=False
        )

        cv2.imshow('Naruto Hand Seal Detection', cv2.resize(image_np_with_detections, (800, 600)))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            cv2.waitKey(1)
            break

if __name__ == "__main__":
    run_capture()