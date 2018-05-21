import numpy as np
#import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
import numpy as np
import math
import time

import argparse
import os.path
import sys

saved_model_file = "model.ckpt"

FLAGS = None

#def plot_train(batches, loss_batch, train_acc_batch, valid_acc_batch):
#    loss_plot = plt.subplot(211)
#    loss_plot.set_title('Loss')
#    loss_plot.plot(batches, loss_batch, 'g')
#    loss_plot.set_xlim([batches[0], batches[-1]])
#    acc_plot = plt.subplot(212)
#    acc_plot.set_title('Accuracy')
#    acc_plot.plot(batches, train_acc_batch, 'r', label='Training Accuracy')
#    acc_plot.plot(batches, valid_acc_batch, 'x', label='Validation Accuracy')
#    acc_plot.set_ylim([0, 1.0])
#    acc_plot.set_xlim([batches[0], batches[-1]])
#    acc_plot.legend(loc=4)
#    plt.tight_layout()
#    plt.show()

#features_count: all the pixels in the image 28*28
#labels: 0 to 9, total 10 labels
def train_model(X_train, y_train, X_valid, y_valid,
                learning_rate=0.2, n_input=784, n_classes=10,
                batch_size = 128, n_epochs = 100):
    # Remove previous Tensors and Operations
    tf.reset_default_graph()

    # Features and Labels
    features = tf.placeholder(tf.float32, [None, n_input], name="features")
    labels = tf.placeholder(tf.float32, [None, n_classes], name="labels")

    # Weights & bias
    W1 = tf.Variable(tf.truncated_normal((n_input, 32)), name="W1")
    b1 = tf.Variable(tf.zeros(32), name="b1")
    W2 = tf.Variable(tf.truncated_normal((32, n_classes)), name="W2")
    b2 = tf.Variable(tf.zeros(n_classes), name="b2")

    # Logits - xW + b
    hidden_layer = tf.add(tf.matmul(features, W1), b1)
    hidden_layer = tf.nn.relu(hidden_layer)
    #hidden_layer = tf.nn.dropout(hidden_layer, 0.8)#keep_prob
    logits = tf.add(tf.matmul(hidden_layer, W2), b2)
    prediction = tf.nn.softmax(logits, name="prediction")

    # Define loss and optimizer
    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=labels))
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(loss)

    # Calculate accuracy
    correct_prediction = tf.equal(tf.argmax(logits, 1), tf.argmax(labels, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32), name="accuracy")
    
    batches = []
    loss_batch = []
    train_acc_batch = []
    valid_acc_batch = []

    validation_accuracy = 0.0
    log_batch_step=50
    saver = tf.train.Saver()
    
#    config = tf.ConfigProto(device_count={'gpu':0})  
    config = tf.ConfigProto()  
    config.gpu_options.allow_growth=True 
    start_time = time.time()
    with tf.Session(config=config) as sess:
        sess.run(tf.global_variables_initializer())
        total_batch = int(math.ceil(len(X_train) / batch_size))
        
        # Training cycle
        for epoch in range(n_epochs):
            # Loop over all batches
            for i in range(total_batch):
                # Get a batch of training features and labels
                batch_start = i*batch_size
                batch_features = X_train[batch_start:batch_start + batch_size]
                batch_labels = y_train[batch_start:batch_start + batch_size]
                sess.run(
                    optimizer,
                    feed_dict={features: batch_features, labels: batch_labels})

                # Run optimizer and get loss
                _, l = sess.run(
                    [optimizer, loss],
                    feed_dict={features: batch_features, labels: batch_labels})

                # Log every 50 batches
                if not i % log_batch_step:
                    # Calculate Training and Validation accuracy
                    training_accuracy = sess.run(accuracy, feed_dict={features:X_train, labels:y_train})
                    validation_accuracy = sess.run(accuracy, feed_dict={features:X_valid, labels:y_valid})
                    # Log batches
                    previous_batch = batches[-1] if batches else 0
                    batches.append(log_batch_step + previous_batch)
                    loss_batch.append(l)
                    train_acc_batch.append(training_accuracy)
                    valid_acc_batch.append(validation_accuracy)
                    print("epoch {} batch {}:loss {}, training_accuracy {}, validation_accuracy {}."
                          .format(epoch, i, l, training_accuracy, validation_accuracy))
                    
        # Check accuracy against Validation data
        validation_accuracy = sess.run(accuracy, feed_dict={features:X_valid, labels:y_valid})
        # Save the model
        full_path = os.path.join(FLAGS.log_dir, saved_model_file)
        saver.save(sess, full_path)
        print('Trained Model Saved.')
        
    end_time = time.time()
    print("model trained in {} seconds".format(end_time-start_time))
    print("training process done, validation accuracy is:{}".format(validation_accuracy))
    #plot_train(batches, loss_batch, train_acc_batch, valid_acc_batch)a

def predict_data(X):
    meta_path = os.path.join(FLAGS.log_dir, saved_model_file + ".meta")
    saver = tf.train.import_meta_graph(meta_path) # input graph from saved model 
     
    config = tf.ConfigProto()  
    config.gpu_options.allow_growth=True 
    prediction = []
    with tf.Session(config=config) as sess:  
        full_path = os.path.join(FLAGS.log_dir, saved_model_file)
        saver.restore(sess, full_path)  
        graph = tf.get_default_graph() 
        features = graph.get_tensor_by_name("features:0")
        predictor = graph.get_tensor_by_name("prediction:0") 
        prediction = sess.run(predictor, feed_dict={features:X})
    return prediction

#def show_image(image_data):
#    plt.figure()
#    plt.imshow(image_data)
#    plt.show()

def main(_):
    old_v = tf.logging.get_verbosity()
    tf.logging.set_verbosity(tf.logging.ERROR)

    if not tf.gfile.Exists(FLAGS.log_dir):
        tf.gfile.MakeDirs(FLAGS.log_dir)

    mnist = input_data.read_data_sets(FLAGS.input_data_dir, one_hot=True)
    train_features = mnist.train.images
    train_labels = mnist.train.labels
    valid_features = mnist.validation.images
    valid_labels = mnist.validation.labels
    test_features = mnist.test.images
    test_labels = mnist.test.labels
    del mnist
    print("load data done.")
    

    #display one images
    test_idx = np.random.randint(len(train_features))
    test_image = train_features[test_idx].reshape((28,28))
    #show_image(test_image)

    train_model(train_features,train_labels, valid_features, valid_labels, n_epochs = FLAGS.max_steps)
    
    #test predict
    for i in range(10): # show 5 images
        test_idx = np.random.randint(len(test_features))
        test_image = test_features[test_idx]  
        print("true label: {}, prediction: {}".format(np.argmax(test_labels[test_idx]), np.argmax(predict_data([test_image]))))
        #show_image(test_image.reshape(28,28))
        
    tf.logging.set_verbosity(old_v)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--max_steps',
      type=int,
      default=100,
      help='Number of steps to run trainer.'
  )
  parser.add_argument(
      '--input_data_dir',
      type=str,
      default='/tmp/tensorflow/mnist/input_data',
      help='Directory to put the input data.'
  )
  parser.add_argument(
      '--log_dir',
      type=str,
      default='/tmp/tensorflow/mnist/logs/fully_connected_feed',
      help='Directory to put the log data.'
  )

  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
