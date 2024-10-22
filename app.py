import os
#import main
from flask import Flask, render_template, request, send_file, jsonify

import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import json

from collections import defaultdict
from io import StringIO
import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt
from PIL import Image

# requires path to OBJRec API
sys.path.append("/tensorflow/models/research")
sys.path.append("/tensorflow/models/research/object_detection")

from object_detection.utils import ops as utils_op

from utils import label_map_util
from utils import visualization_utils as vis_utils

#Path to frozen detection graph
PATH_TO_FROZEN_GRAPH = "frozen_inference_graph_face.pb"

# List of strings that is used to add correct label for each box
PATH_TO_LABELS = "face_label_map.pbtxt"

NUM_CLASSES = 1

# Load Graph
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

        
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

IMAGE_SIZE = (12, 8)

app = Flask(__name__)



UPLOAD_FOLDER = os.path.basename('uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)

def run_inference_for_single_image(image, graph):
  with graph.as_default():
    with tf.Session() as sess:
      # Get handles to input and output tensors
      ops = tf.get_default_graph().get_operations()
      all_tensor_names = {output.name for op in ops for output in op.outputs}
      tensor_dict = {}
      for key in [
          'num_detections', 'detection_boxes', 'detection_scores',
          'detection_classes', 'detection_masks'
      ]:
        tensor_name = key + ':0'
        if tensor_name in all_tensor_names:
          tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
              tensor_name)
      if 'detection_masks' in tensor_dict:
        # The following processing is only for single image
        detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
        detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
        # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
        real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
        detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
        detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
            detection_masks, detection_boxes, image.shape[0], image.shape[1])
        detection_masks_reframed = tf.cast(
            tf.greater(detection_masks_reframed, 0.5), tf.uint8)
        # Follow the convention by adding back the batch dimension
        tensor_dict['detection_masks'] = tf.expand_dims(
            detection_masks_reframed, 0)
      image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

      # Run inference
      output_dict = sess.run(tensor_dict,
                             feed_dict={image_tensor: np.expand_dims(image, 0)})

      # all outputs are float32 numpy arrays, so convert types as appropriate
      output_dict['num_detections'] = int(output_dict['num_detections'][0])
      output_dict['detection_classes'] = output_dict[
          'detection_classes'][0].astype(np.uint8)
      output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
      output_dict['detection_scores'] = output_dict['detection_scores'][0]
      if 'detection_masks' in output_dict:
        output_dict['detection_masks'] = output_dict['detection_masks'][0]
  return output_dict

@app.route('/')

def hello_world():
    #delete any old images from folder
    filename = os.path.join(app.config['UPLOAD_FOLDER'], 'image.jpeg')
    if os.path.isfile(filename):
        os.remove(filename)
    return render_template('index.html')



@app.route('/upload', methods=['POST'])

def upload_file():
    
    try:
        file = request.files['image']
    except:
        return render_template('NoImage.html')
	# need to add code for handling othe file formats
    filename = os.path.join(app.config['UPLOAD_FOLDER'], 'image.jpeg')
	#delete any old images from folder
    if os.path.isfile(filename):
        os.remove(filename)
    file.save(filename)
    image = Image.open(filename)
	# the array based representation of the image will be used later in order to prepare the
	# result image with boxes and labels on it.
    image_np = load_image_into_numpy_array(image)
	# Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
	# Actual detection.
    output_dict = run_inference_for_single_image(image_np, detection_graph)
	# Visualization of the results of a detection.
    if output_dict['num_detections'] >= 1:
        vis_utils.visualize_boxes_and_labels_on_image_array(
	    	image_np,
		output_dict['detection_boxes'],
		output_dict['detection_classes'],
		output_dict['detection_scores'],
		category_index,
		instance_masks=output_dict.get('detection_masks'),
		use_normalized_coordinates=True,
		line_thickness=8)
        plt.figure(figsize=IMAGE_SIZE)
        plt.imshow(image_np)
	# Edits to save image image for return    
        plt.savefig(filename)
        response = send_file(filename, mimetype='image/jpeg')
        d_num_d = output_dict['num_detections']
        d_num_djson = json.dumps(d_num_d)
        d_boxes = output_dict['detection_boxes'].tolist()
        d_boxesjson = json.dumps(d_boxes)
        d_classes = output_dict['detection_classes'].tolist()
        d_classesjson = json.dumps(d_classes)
        d_scores = output_dict['detection_scores'].tolist()
        d_scoresjson = json.dumps(d_scores)
        response.headers['number_of_detections'] = d_num_djson
        response.headers['boxes_in_image'] = d_boxesjson
        response.headers['classes'] = d_classesjson
        response.headers['confidence_scores'] = d_scoresjson
        return response
    else:
        return 'No Faces or Number Plates found in this image'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
