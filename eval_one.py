'''

   Evaluation File

'''

import cPickle as pickle
import tensorflow as tf
from scipy import misc
from tqdm import tqdm
import numpy as np
import argparse
import random
import ntpath
import sys
import os
import time
import time
import glob
import cPickle as pickle
from tqdm import tqdm

sys.path.insert(0, 'ops/')
sys.path.insert(0, 'nets/')
from tf_ops import *

import data_ops

if __name__ == '__main__':

   if len(sys.argv) < 3:
      print 'You must provide an info.pkl file and an image'
      exit()

   pkl_file = open(sys.argv[1], 'rb')
   a = pickle.load(pkl_file)

   LEARNING_RATE = a['LEARNING_RATE']
   LOSS_METHOD   = a['LOSS_METHOD']
   BATCH_SIZE    = a['BATCH_SIZE']
   EPOCHS        = a['EPOCHS']
   L1_WEIGHT     = a['L1_WEIGHT']
   IG_WEIGHT     = a['IG_WEIGHT']
   NETWORK       = a['NETWORK']
   DATA          = a['DATA']
   LAYER_NORM    = a['LAYER_NORM']

   EXPERIMENT_DIR = 'checkpoints/LOSS_METHOD_'+LOSS_METHOD\
                     +'/NETWORK_'+NETWORK\
                     +'/LAYER_NORM_'+str(LAYER_NORM)\
                     +'/L1_WEIGHT_'+str(L1_WEIGHT)\
                     +'/IG_WEIGHT_'+str(IG_WEIGHT)\
                     +'/DATA_'+DATA+'/'\

   test_image = sys.argv[2]

   print
   print 'LEARNING_RATE: ',LEARNING_RATE
   print 'LOSS_METHOD:   ',LOSS_METHOD
   print 'BATCH_SIZE:    ',BATCH_SIZE
   print 'NETWORK:       ',NETWORK
   print 'EPOCHS:        ',EPOCHS
   print 'LAYER_NORM:    ',LAYER_NORM
   print

   if NETWORK == 'pix2pix': from pix2pix import *
   if NETWORK == 'resnet':  from resnet import *

   # global step that is saved with a model to keep track of how many steps/epochs
   global_step = tf.Variable(0, name='global_step', trainable=False)

   # underwater image
   image_u = tf.placeholder(tf.float32, shape=(1, 256, 256, 3), name='image_u')

   # generated corrected colors
   gen_image = netG(image_u, LOSS_METHOD)

   saver = tf.train.Saver(max_to_keep=1)

   init = tf.group(tf.local_variables_initializer(), tf.global_variables_initializer())
   sess = tf.Session()
   sess.run(init)

   ckpt = tf.train.get_checkpoint_state(EXPERIMENT_DIR)
   if ckpt and ckpt.model_checkpoint_path:
      print "Restoring previous model..."
      try:
         saver.restore(sess, ckpt.model_checkpoint_path)
         print "Model restored"
      except:
         print "Could not restore model"
         pass
   
   step = int(sess.run(global_step))

   img_name = ntpath.basename(test_image)

   img_name = img_name.split('.')[0]

   batch_images = np.empty((1, 256, 256, 3), dtype=np.float32)

   a_img = misc.imread(test_image).astype('float32')
   a_img = misc.imresize(a_img, (256, 256, 3))
   a_img = data_ops.preprocess(a_img)
   batch_images[0, ...] = a_img

   gen_images = np.asarray(sess.run(gen_image, feed_dict={image_u:batch_images}))

   misc.imsave('./'+img_name+'_real.png', batch_images[0])
   misc.imsave('./'+img_name+'_gen.png', gen_images[0])

