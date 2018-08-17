
import os
import main
from flask import Flask, render_template, request

import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile

from collections import defaultdict
from io import StringIO
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



@app.route('/')

def hello_world():

    return render_template('index.html')



@app.route('/upload', methods=['POST'])

def upload_file():

    file = request.files['image']

    image = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

	# the array based representation of the image will be used later in order to prepare the
	# result image with boxes and labels on it.
    image_np = main.load_image_into_numpy_array(image)
	# Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
	# Actual detection.
    output_dict = main.run_inference_for_single_image(image_np, detection_graph)
	# Visualization of the results of a detection.
    vis_util.visualize_boxes_and_labels_on_image_array(
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

    # add your custom code to check that the uploaded file is a valid image and not a malicious file (out-of-scope for this post)

    file.save(f)



    return render_template('index.html')
