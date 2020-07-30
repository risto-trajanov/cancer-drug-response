import tempfile
import pymongo
import boto3
from airflow.contrib.hooks.mongo_hook import MongoHook
from airflow.hooks.S3_hook import S3Hook

S3_BUCKET_NAME = 'cancerdrugresponse'
aws_access_key_id = "AKIAJR6DOH7PB4S3RFLA"
aws_secret_access_key = "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"




def download_s3(file):
    s3 = S3Hook(aws_conn_id='my_conn_S3')
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        s3.get_key(file, S3_BUCKET_NAME).download_fileobj(tmp)
        return tmp.name


def upload_s3(file):
    s3 = S3Hook(aws_conn_id='my_conn_S3')
    return s3.load_file(file, file, bucket_name=S3_BUCKET_NAME, replace=True)

def get_mongo_connection():
    # hook = MongoHook(conn_id='mongo_db')
    # conn = hook.get_connection('mongo_db')
    # admin = conn.login,
    # password = conn.password,
    # database = conn.schema
    # mongo_connection_string = f'mongodb+srv://{admin}:{password}@cluster.hwdmn.gcp.mongodb.net/{database}?retryWrites=true&w=majority'
    mongo_connection_string = "mongodb+srv://risto_admin:riste123@cluster.hwdmn.gcp.mongodb.net/cancer_drug_response?retryWrites=true&w=majority&connectTimeoutMS=300000"
    return pymongo.MongoClient(mongo_connection_string)

def upload_mongo(database, collection, json):
    client = get_mongo_connection()
    db = client[database]
    drugs = db[collection]
    drugs.insert_many(json)


def donwload_mongo(database, collection):
    client = get_mongo_connection()
    db = client[database]
    drugs = db[collection]
    return drugs


def upload_s3_local(file):
    s3_resources = boto3.resource('s3')
    bucket = s3_resources.Bucket(name=S3_BUCKET_NAME)
    bucket.load_file(Filename=file, Key=file, replace=True)


def download_s3_local(file):
    s3_resources = boto3.resource('s3')
    s3_resources.Object(S3_BUCKET_NAME, file).download_file(file)
