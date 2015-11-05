# -*- coding: utf-8 -*-
"""
Created on Wed Nov 04 14:41:28 2015

@author: muttik
Set creds using environment variables
AWS_ACCESS_KEY_ID - Your AWS Access Key ID
AWS_SECRET_ACCESS_KEY - Your AWS Secret Access Key
"""

import boto.sqs
from boto.sqs.message import Message

conn = boto.sqs.connect_to_region(
     "us-west-2",
     #aws_access_key_id='',
     #aws_secret_access_key='',
     )
     
     
#q = conn.create_queue('nazar-sqs')

#qs = conn.get_all_queues()

#print qs
my_queue = conn.get_queue('nazar-sqs')
m = Message()

m.set_body('This is my first message.')
my_queue.write(m)

#rm = my_queue.get_messages()
#print rm

newm = my_queue.read()
print newm.get_body()

my_queue.delete_message(newm)

newm = my_queue.read()
print newm.get_body()

#conn.delete_queue(my_queue)
