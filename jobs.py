#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 16 03:35:55 2023

@author: hill103

this script defines variables and functions to handle tRFtarget-pipeline jobs

deprecated
"""



import os
import hashlib
import uuid
import gzip
import subprocess

'''
Python has a built-in library called concurrent.futures that provides a high-level interface for asynchronously executing callables. It can work with both threads and processes

Note that if your task is I/O-bound or requires a lot of CPU resources, it's better to use a process-based executor like ProcessPoolExecutor instead of a thread-based executor like ThreadPoolExecutor.

However, in the case of running a Docker command, the command itself will manage CPU resources, so using ThreadPoolExecutor should be sufficient

Update: Gunicorn runs multiple worker processes to handle incoming requests, and each worker process runs a separate instance of your Flask app. This means that if you are using concurrent.futures.ThreadPoolExecutor within your Flask app, you may have more concurrent tasks than you expect, since each Gunicorn worker process will create its own ThreadPoolExecutor with the specified number of max_workers.

To limit the number of concurrent tasks across all worker processes, use a shared task queue like Celery or RQ (Redis Queue)

Note in RQ job will expire, i.e. older jobs are not kept any more. So just use RQ to arrange jobs, and use a separated Redis Hashes to store all job IDs and status
'''


'''deprecated
import concurrent.futures

# Create a ThreadPoolExecutor with 2 workers thread
executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
'''



# folder for saving and serving files for online service
cache_folder = os.environ.get("CACHE_FOLDER")



'''
create a dict to store submitted jobs by users
key: unique job id, value: 'QUEUED', 'RUNNING', 'COMPLETED', 'FAILED'

When you pass a dictionary to a function, you are passing a reference to the dictionary, not a copy. This means that any changes made to the dictionary inside the function will affect the original dictionary

But it not works in flask, so use Redis instead
'''



import redis
from redis_fun import setJob, hasJob, getJob, getAllJob, POOL
from rq import Queue

# specify a queue name
q = Queue('online_targets', connection=redis.Redis(connection_pool=POOL))



# ------------------------ Sending email --------------------------------------#

# Send email from within a job, before returning - IMO preferred solution, as it's explicit what your job does

# A basic checking for email address, like it has exactly one @ sign, and at least one . in the part after the @
import re
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

def checkEmail(email_address):
    '''check an email address
    '''
    # Python ≥3.4 has re.fullmatch which is preferable to re.match
    if EMAIL_REGEX.fullmatch(email_address):
        return email_address
    else:
        return None



import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# get my email account from environment variable
my_email = os.environ.get("MY_EMAIL")
my_password = os.environ.get("MY_PASSWORD")


def send_email(job_id, job_status, recipient_email):
    '''send email to user
    '''
    # Create the MIME object
    msg = MIMEMultipart("alternative")
    msg["From"] = my_email
    msg["To"] = recipient_email
    msg["Subject"] = "Your job in tRFtarget has been completed"

    # Add the email body
    # Create the plain text of the email
    text = f"""\
    Dear user,
    
    Thanks for your interest in tRFtarget.
    
    Your job has been completed. Here are the details:

    Job ID: {job_id}
    Status: {job_status}
    
    Please visit http://trftarget.net/online_result/{job_id} to access the results.
    
    Note that the results will be kept for only 14 days.
    
    This is an automated email; please do not reply. If you have any questions or need assistance, please contact us through our GitHub repository tRFtarget (https://github.com/ZWang-Lab/tRFtarget).

    Best regards,
    tRFtarget team
    """
    
    # Create the HTML parts of the email
    if job_status == 'COMPLETED':
        text_color = 'green'
    else:
        text_color = 'red'
        
    html = f"""\
    <html>
    <body>
        <p>Dear user,<br><br>
        Thanks for your interest in tRFtarget.<br><br>
        Your job has been completed. Here are the details:<br><br>
        <strong>Job ID:</strong> {job_id}<br>
        <strong>Status:</strong> <span style='color: {text_color}'><strong>{job_status}</strong></span><br><br>
        Please visit <a href="http://trftarget.net/online_result/{job_id}" target="_blank" rel="noopener noreferrer">http://trftarget.net/online_result/{job_id}</a> to access the results.<br><br>
        Note that <span style='color: red'>the results will be kept for only 14 days</span>.<br><br>
        This is an automated email; please do not reply. If you have any questions or need assistance, please contact us through our GitHub repository <a href="https://github.com/ZWang-Lab/tRFtarget" target="_blank" rel="noopener noreferrer">tRFtarget</a>.<br><br>
        Best regards,<br>
        tRFtarget team
        </p>
    </body>
    </html>
    """
    
    # Attach the plain text and HTML parts to the email message
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))
    
    # use GoDaddy's secure SMTP server
    with smtplib.SMTP_SSL("smtpout.secureserver.net", 465) as server:
        server.ehlo()
        server.login(my_email, my_password)
        # when including HTML in your email, you'll need to use send_message() instead of sendmail()
        server.send_message(msg)



# -------------------- Online Service of tRFtarget-pipeline ---------------------------------#

def generateNewJobID():
    '''generate a Universal Unique Identifier (UUID) as job ID
    uuid.uuid1() generates a UUID based on the current time and the MAC address of the computer
    uuid.uuid4() generates a random UUID, and doesn’t compromise with privacy
    str(uuid.uuid4()) convert a UUID to a string of hex digits in standard form. Notes it has 4 hyphens, and is more human-readable
    uuid.uuid4().hex provides the hexadecimal representation of the UUID as a 32-character string without hyphens
    '''
    while True:
        job_id = uuid.uuid4().hex
        if (not hasJob(job_id)) and (not os.path.exists(os.path.join(cache_folder, job_id))):
            break
    return job_id


def checkFASTA(blob, sha256):
    '''receieved object is <FileStorage: 'blob' ('application/octet-stream')>
    it's gzipped Uint8Array
    don't forget to compare the SHA-256 hash which is a hexadecimal string
    '''
    # Decompress the gzipped data and Decode the decompressed bytes to a string
    # note we already make sure to use UTF-8 encoding in frontend
    # The gzip.decompress() function returns a bytes object (which is the same as a b-string). When you use the .decode('utf-8') method on this bytes object, it converts the bytes object to a regular Python string
    # but hashlib.sha256 expectes bytes-like objects (normally bytes) 
    original_bytes = gzip.decompress(blob)
   
    this_hash = hashlib.sha256(original_bytes).hexdigest()
    
    if this_hash == sha256:
        return original_bytes.decode('utf-8')
    else:
        # SHA-256 checksum mismatch
        return None


def saveFASTA(to_write, job_id, file_name):
    '''write a string to file named as file_name
    this one row string already has new lines in itself and passed FASTA checking, so no need to use Bio to write it as FASTA file
    '''
    with open(os.path.join(cache_folder, job_id, file_name), 'w') as f:
        f.write(to_write)


def addNewJob(job_id):
    '''checking passed, a new valid job submitted
    add this job to queue, and create corresponding folder
    '''
    setJob(job_id, 'QUEUED')
    # The os.mkdir() method in OS module raises a FileExistsError if the directory in the location specified as path already exists. 
    # The default mode value is 0o777 (octal), i.e. readable, writable and executable by all users
    os.mkdir(os.path.join(cache_folder, job_id))
    

# If you want to execute a function whenever a job completes or fails, RQ provides on_success and on_failure callbacks (https://python-rq.org/docs/#job-callbacks)
# Use them to make sure the job status will be updated correctly, especially when job failed, the status updation inside job will not be performed
def report_success(job, connection, result, *args, **kwargs):
    setJob(job.id, 'COMPLETED')


def report_failure(job, connection, type, value, traceback):
    setJob(job.id, 'FAILED')


def oneJob(job_id, cmd, email_address=None):
    '''in one job, we run the docker cmd, update the job_queue dict
    '''
    setJob(job_id, 'RUNNING')
    # stdout and stderr is handled in the cmd string
    # if check=True, the subprocess.run function will raise a CalledProcessError exception if the command returns a non-zero exit code. If check=False, manually check the returncode attribute of the returned CompletedProcess object
    process = subprocess.run(cmd, shell=True)
    # A return code of 0 usually means the command executed successfully, while a non-zero return code indicates an error
    if process.returncode == 0:
        setJob(job_id, 'COMPLETED')
        # compress files into one file
        # cd into the folder, then the path will be omitted from the compressed file
        subprocess.run(f'cd {os.path.join(cache_folder, job_id)} && tar -czf {job_id}.tar.gz *.csv', shell=True)
        # send email
        if email_address is not None:
            send_email(job_id, getJob(job_id), email_address)
    else:
        setJob(job_id, 'FAILED')
        # add an error.log file, which is just the last 5 lines of log
        subprocess.run(f'tail -n 5 {os.path.join(cache_folder, job_id, "job.log")} > {os.path.join(cache_folder, job_id, "error.log")}', shell=True)
        # also send email
        if email_address is not None:
            send_email(job_id, getJob(job_id), email_address)


def getJobQueueStatus():
    '''get the number of jobs with different status
    '''
    count = {'QUEUED': 0, 'RUNNING': 0, 'COMPLETED': 0, 'FAILED': 0}
    for k, v in getAllJob().items():
        count[v] += 1
    return count


def getJobStatus(job_id):
    '''get the status of one job by job id
    note the job id may not recorded in Queue (after reboot, Queue reset) or invalid
    '''
    
    if hasJob(job_id):
        
        job_status = getJob(job_id)
        
        if job_status == 'QUEUED' or job_status == 'RUNNING':
            message = 'Please check back later.\nBookmarking this page will make it easier to return and view your results.\nA notification will be sent through email once the job is completed if email address is provided.'
        elif job_status == 'COMPLETED':
            if os.path.exists(os.path.join(cache_folder, job_id, job_id+".tar.gz")):
                message = 'Please click below button to download your results.\nNote the results will be kept for only 14 days.'
            else:
                job_status = 'DELETED'
                message = 'Your job has been completed and deleted as the results were kept for only 14 days.\nPlease submit a new job in <a href="http://trftarget.net/online_targets">Online Service</a>.\nWe sincerely apologize for any inconvenience.'
                
        elif job_status == 'FAILED':
            if os.path.exists(os.path.join(cache_folder, job_id, "error.log")):
                with open(os.path.join(cache_folder, job_id, "error.log")) as f:
                    # including newlines \n
                    message = f.read()
            else:
                message = 'Your job failed for unknown issues.\nPlease submit a new job again in <a href="http://trftarget.net/online_targets">Online Service</a>.\nWe sincerely apologize for any inconvenience.'
                
    else:
        
        # does the job folder exist?
        if os.path.exists(os.path.join(cache_folder, job_id)):
            # we need to infer the job status from the content in that folder
            if os.path.exists(os.path.join(cache_folder, job_id, job_id+".tar.gz")):
                job_status = 'COMPLETED'
                message = 'Please click below button to download your results.\nNote the results will be kept for only 14 days.'
            elif os.path.exists(os.path.join(cache_folder, job_id, "error.log")):
                job_status = 'FAILED'
                with open(os.path.join(cache_folder, job_id, "error.log")) as f:
                    # including newlines \n
                    message = f.read()
            else:
                # the job is terminated unexpectedly
                job_status = 'TERMINATED'
                message = 'Your job is terminated unexpectedly due to server reboot or other unknown issues.\nPlease submit this job again in <a href="http://trftarget.net/online_targets">Online Service</a>.\nWe sincerely apologize for any inconvenience.'
        
        else:
            # also no job folder found, an invalid or deleted job id is provided
            job_status = 'NOT FOUND'
            message = 'An invalid job ID.\nPlease submit a new job in <a href="http://trftarget.net/online_targets">Online Service</a>.'

    return job_status, message