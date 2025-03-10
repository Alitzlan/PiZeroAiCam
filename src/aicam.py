#!/usr/bin/python3

import math
import sys
import threading
import time
import libcamera
from displayhatmini import DisplayHATMini
from pathlib import Path
from PIL import Image
from PIL import ImageDraw
from picamera2 import Picamera2
from pycoral.adapters import common
from pycoral.adapters import detect
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter

# Configure filesystem
script_path = Path(__file__)
script_dir = script_path.parent

# Configure display
width = DisplayHATMini.WIDTH
height = DisplayHATMini.HEIGHT
disp_buffer = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(disp_buffer)
displayhatmini = DisplayHATMini(disp_buffer)

# Configure camera
picam2 = Picamera2()
capture_config = picam2.create_still_configuration(
    main={"size": (width, height), "format": "RGB888"},
    lores=None,
    raw=None,
    colour_space=libcamera.ColorSpace.Raw(),
    buffer_count=6,
    controls={"AfMode": libcamera.controls.AfModeEnum.Continuous},
    queue=True
    )
picam2.configure(capture_config)
picam2.start()

# Configure interpreter
image_buffer = Image.new("RGB", (width, height))
labels = read_label_file(str(script_dir / "../model/mobilenet_coco/coco_labels.txt"))
interpreter = make_interpreter(str(script_dir / "../model/mobilenet_coco/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite"))
interpreter.allocate_tensors()

detected_objs = []
inference_latency = sys.float_info.max

def is_duplicate(center1, center2):
    dist_thresh = 15
    return dist_thresh >= math.dist(center1, center2)

def run_interpreter():
    global image_buffer, detected_objs, inference_latency, dedup_latency

    start = time.perf_counter()

    _, scale = common.set_resized_input(
        interpreter, image_buffer.size, lambda size: image_buffer.resize(size, Image.ANTIALIAS))
    interpreter.invoke()

    inference_latency = time.perf_counter() - start

    dedup_map = {}
    objs = detect.get_objects(interpreter, 0.4, scale)
    filtered_objs = []

    for obj in objs:
        bbox = obj.bbox
        center = ((bbox.xmax + bbox.xmin) / 2, (bbox.ymax + bbox.ymin) / 2)

        bucket = dedup_map.get(obj.id)
        if bucket is not None:
            should_continue = False
            for other_center in bucket:
                if is_duplicate(center, other_center):
                    should_continue = True
                    break
            if should_continue:
                continue
        else:
            dedup_map[obj.id] = []
        dedup_map[obj.id].append(center)
        filtered_objs.append((obj, bbox))

    detected_objs = filtered_objs

inference_thread = threading.Thread(target=run_interpreter)

last_frame_time = time.perf_counter()
framerate = 0

# Main loop
try:
    while True:
        disp_buffer.paste(picam2.capture_image())

        if not inference_thread.is_alive():
            image_buffer.paste(disp_buffer)
            inference_thread = threading.Thread(target=run_interpreter)
            inference_thread.start()

        for detected_obj in detected_objs:
            obj = detected_obj[0]
            bbox = detected_obj[1]
            draw.rectangle([(bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax)],
                        outline='yellow')
            draw.text((bbox.xmin + 10, bbox.ymin + 10),
                    '%s\n%.2f' % (labels.get(obj.id, obj.id), obj.score),
                    fill='yellow')

        draw.text((10, 10),
                '%02d fps\n%.2f ms' % (framerate, inference_latency * 1000),
                fill='white')

        disp_buffer.paste(disp_buffer.transpose(Image.ROTATE_180))

        displayhatmini.display()

        this_frame_time = time.perf_counter()
        framerate = 1 / (this_frame_time - last_frame_time)
        last_frame_time = this_frame_time
finally:
    if inference_thread.is_alive():
        inference_thread.join()
