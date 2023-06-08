#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 22:18:21 2023

@author: hill103

this script handles retrieving and updating Redis Keys and Hashes

the Flask application's global variables are NOT shared across multiple workers when using Gunicorn or other multi-process servers. Each worker will have its own separate instance of the Flask application.

To handle this situation, you should use an external storage system to store information. One common solution is to use a key-value store like Redis

Redis only supports string values, so if you want to store more complex data structures like dictionaries or lists, you need to serialize them into a string format, such as JSON string representation. If it is already a plain string, you can store it directly in Redis without any serialization

Redis Keys and Hashes have been initialized in Redis CLI (Command Line Interface)

There are two Redis Keys ("n_search", "n_online") and one Hashes ("online_target_jobs")
"""



import redis
import os



'''
using a connection pool is a good idea when working with Redis in Python. Connection pooling helps manage the connections to the Redis server and efficiently reuse existing connections, which can improve the performance of your application.

Note Gunicorn spawns multiple worker processes, and each worker process runs its own instance of the Flask app, which is not shared among these worker processes, so each process will have its own separate connection pool.

To ensure that you are using the connection pool efficiently, you can create a new Redis connection for each request or function by getting a connection from the pool via redis.Redis(connection_pool=POOL)

Note Redis works on bytes rather than strings. When you use redis-py to access a Redis key using a normal Python string, the library will automatically convert the string to bytes before sending the command to Redis

Use get().decode() to convert bytes to Python strings. Also you can use decode_responses=True when creating a Redis instance to automatically decode the returned byte strings to Unicode strings.

Please note that when using decode_responses=True, all Redis responses will be decoded to Unicode strings, including key names, values, and any other data returned by Redis commands. If you're working with binary data or need to handle the raw bytes, you should not use this option.

Update: decode_responses=True need to be specified in ConnectionPool if it's used (https://github.com/redis/redis-py/issues/701)

Update: decode_responses=True not supported by RQ (https://python-rq.org/docs/connections/#encoding--decoding)
'''


POOL = redis.ConnectionPool(host=os.environ.get("REDIS_HOST"), port=int(os.environ.get("REDIS_PORT")), db=int(os.environ.get("REDIS_DB")))



# ---------------------------- Counter -- ---------------------------------#

def getVariable(variable_name):
    return int(redis.Redis(connection_pool=POOL).get(variable_name).decode())


def setVariable(variable_name, variable_value):
    redis.Redis(connection_pool=POOL).set(variable_name, variable_value)
 

def incrVariable(variable_name):
    redis.Redis(connection_pool=POOL).incrby(variable_name)


# ---------------------------- Job Stauts of online target---------------------------#

def setJob(job_id, job_status):
    # Use the HSET command to store the job_status in the hash
    # it can be used for both adding new key or updating the current value of key
    redis.Redis(connection_pool=POOL).hset('online_target_jobs', job_id, job_status)


def hasJob(job_id):
    # use the HEXISTS command to quickly check if a hash has a specific field (key)
    return redis.Redis(connection_pool=POOL).hexists('online_target_jobs', job_id)


def getJob(job_id):
    # Use the HGET command to retrieve the job_status from the hash
    # if job_id not exist, return None
    return redis.Redis(connection_pool=POOL).hget('online_target_jobs', job_id).decode()


'''
When you use hgetall(), Redis retrieves all field-value pairs in the hash. If the hash contains a large number of field-value pairs, the operation could consume a significant amount of memory and processing time, both on the Redis server and in your Python application.

so avoid use hgetall() frequently
'''

def getAllJob():
    # Get all fields and values in a hash, result is a Python dict
    return {key.decode(): value.decode() for key, value in redis.Redis(connection_pool=POOL).hgetall('online_target_jobs').items()}