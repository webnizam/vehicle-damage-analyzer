# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np
import tensorflow as tf
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt


def load_graph(model_file):
    graph = tf.Graph()
    graph_def = tf.GraphDef()

    with open(model_file, "rb") as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)

    return graph


def read_tensor_from_image_file(file_name,
                                input_height=299,
                                input_width=299,
                                input_mean=0,
                                input_std=255):
    input_name = "file_reader"
    output_name = "normalized"
    file_reader = tf.read_file(file_name, input_name)
    if file_name.endswith(".png"):
        image_reader = tf.image.decode_png(
            file_reader, channels=3, name="png_reader")
    elif file_name.endswith(".gif"):
        image_reader = tf.squeeze(
            tf.image.decode_gif(file_reader, name="gif_reader"))
    elif file_name.endswith(".bmp"):
        image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
    else:
        image_reader = tf.image.decode_jpeg(
            file_reader, channels=3, name="jpeg_reader")
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0)
    resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    sess = tf.Session()
    result = sess.run(normalized)

    return result


def load_labels(label_file):
    label = []
    proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
    for l in proto_as_ascii_lines:
        label.append(l.rstrip())
    return label


def find_match(file):
    file_name = file
    model_file = "static/ai_models/quantized_model.pb"
    label_file = "static/ai_models/retrained_labels.txt"
    input_height = 299
    input_width = 299
    input_mean = 0
    input_std = 255
    input_layer = "Placeholder"
    output_layer = "final_result"

    # parser = argparse.ArgumentParser()
    # parser.add_argument("--image", help="image to be processed")
    # args = parser.parse_args()
    # if args.image:
    #     file_name = args.image

    graph = load_graph(model_file)
    t = read_tensor_from_image_file(
        file_name,
        input_height=input_height,
        input_width=input_width,
        input_mean=input_mean,
        input_std=input_std)

    input_name = "import/" + input_layer
    output_name = "import/" + output_layer
    input_operation = graph.get_operation_by_name(input_name)
    output_operation = graph.get_operation_by_name(output_name)

    with tf.Session(graph=graph) as sess:
        results = sess.run(output_operation.outputs[0], {
            input_operation.outputs[0]: t
        })
    results = np.squeeze(results)

    top_k = results.argsort()[-5:][::-1]
    labels = load_labels(label_file)

    return results, labels
    # for i in top_k:
    #     print(labels[i], results[i])


def get_sample(data):
    return data


# Create your views here.

# def homePageView(request):
#     results, labels = find_match(
#         "/home/nizamuudin/PycharmProjects/AiExperiments/WreckedCarClassifier/datasets/wrecked/1. f2y0vll.jpg")
#
#     return HttpResponse('Hello, Oiii World! ' + str(labels[0]) + " : " + str(results[0]))

@csrf_exempt
def homePageView(request):
    results, labels = find_match(
        "/home/nizamuudin/PycharmProjects/AiExperiments/WreckedCarClassifier/datasets/wrecked/1. f2y0vll.jpg")
    zipped_list = zip(labels, results)
    return render_to_response('home/home.html', {'results': zipped_list})


from .forms import ImageUploadForm
from .models import ExampleModel
from django.http import HttpResponseForbidden
from django.shortcuts import render
import os
import shutil


@csrf_exempt
def upload_pic(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            course_id = 1
            shutil.rmtree('static/intellijScanner/')
            m = ExampleModel()
            try:
                m.model_pic = form.cleaned_data['image']
                m.save()
                print("success")
            except ExampleModel.DoesNotExist:
                print("fail")
                m = None
            # return render_to_response('result/result.html', {'results': zipped_list})
            print(m.url)
            img_list = os.listdir("static/intellijScanner/")
            image_path = "static/intellijScanner/" + img_list[0]
            results, labels = find_match(image_path)
            zipped_list = zip(labels, results)

            browser_stats = [(labels[0].capitalize(), float(results[0] * 100)),
                             (labels[1].capitalize(), float(results[1] * 100))]

            return render(request, 'result/result.html',
                          {'results': zipped_list, 'image_path': 'intellijScanner/' + img_list[0],
                           'browser_stats': browser_stats})
            # return HttpResponse('image upload success')
    return HttpResponseForbidden('allowed only via POST')
