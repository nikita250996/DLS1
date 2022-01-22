import tensorflow as tf
import numpy as np
import json
import base64


def proceed_sketch(a):
    with open(a.input_file, "rb") as f:
        input_data = f.read()

    input_instance = dict(
        input=base64.urlsafe_b64encode(input_data).decode("ascii"), key="0"
    )
    input_instance = json.loads(json.dumps(input_instance))

    with tf.Session() as sess:
        saver = tf.train.import_meta_graph(a.model_dir + "/export.meta")
        saver.restore(sess, a.model_dir + "/export")
        input_vars = json.loads(tf.get_collection("inputs")[0])
        output_vars = json.loads(tf.get_collection("outputs")[0])
        input = tf.get_default_graph().get_tensor_by_name(input_vars["input"])
        output = tf.get_default_graph().get_tensor_by_name(output_vars["output"])

        input_value = np.array(input_instance["input"])
        output_value = sess.run(
            output, feed_dict={input: np.expand_dims(input_value, axis=0)}
        )[0]

    output_instance = dict(output=output_value.decode("ascii"), key="0")

    b64data = output_instance["output"]
    b64data += "=" * (-len(b64data) % 4)
    output_data = base64.urlsafe_b64decode(b64data.encode("ascii"))

    with open(a.output_file, "wb") as f:
        f.write(output_data)
