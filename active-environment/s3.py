import boto3
import botocore
import inspect
import json
import os
import xli_utilities as utils


class AwsS3:
    _aws_profile = "default"
    _aws_region = "us-east=1"

    _s3_bucket = ""
    _s3_base_key = ""

    _aws_client = None
    _aws_resource = None

    def __init__(self, **kwargs):
        self.properties = kwargs

        self._aws_profile = self.properties.get('aws_profile')
        self._aws_region = self.properties.get('aws_region')
        self._s3_bucket = self.get_s3(self.properties.get('s3'))
        self._s3_base_key = self.get_s3_base_key(self.properties.get('s3'))

        boto3.setup_default_session(profile_name=self._aws_profile)
        self._aws_client = boto3.client('s3', region_name=self._aws_region)
        self._aws_resource = boto3.resource('s3', region_name=self._aws_region)

    def copy_to_s3(self, full_file_path):
        s3_key = self.get_s3_key(full_file_path)
        self._aws_resource.meta.client.upload_file(os.path.abspath(full_file_path),
                                                   self._s3_bucket,
                                                   utils.s3_path_combine(self._s3_base_key, s3_key))

        return utils.s3_path_combine('https://s3.amazonaws.com', self._s3_bucket, self._s3_base_key, s3_key)

    def delete_s3_key(self, s3_key):
        print("INFO-S3: Deleting bucket: " + self._s3_bucket)
        print("INFO-S3: Deleting key: " + utils.s3_path_combine(self._s3_base_key, s3_key))

        return self._aws_client.delete_object(Bucket=self._s3_bucket,
                                              Key=utils.s3_path_combine(self._s3_base_key, s3_key))

    def get_json(self, key):
        """

        :param key:
        :return:
        """
        ret_val = []

        try:
            response = self._aws_client.get_object(Bucket=self._s3_bucket, Key=key)

            if 'Body' in response:
                ret_val = json.loads(response['Body'].read().decode('utf-8'))
                response['Body'].close()

        except Exception as ex:
            if not inspect.isclass(type(ex)):
                raise ex

        return ret_val

    def put_json(self, key, body):
        """

        :param key
        :param body:
        :return:
        """

        response = {}

        try:
            response = self._aws_client.put_object(Bucket=self._s3_bucket, Key=key, Body=json.dumps(body).encode())
        except botocore.exceptions.ClientError as ex:
            print("Cannot upload to bucket.  S3: {0}, key: {1}".format(self._s3_bucket, key))
        except Exception as ex:
            raise ex

        return response

    @staticmethod
    def get_s3(path):
        """
        Given full S3 path, extract just the name of the S3 bucket
        :param path: 
        :return: 
        """
        if str(path).startswith('s3://'):
            return utils.do_match('s3://([^/]*)', path, 1)
        else:
            return utils.do_match('([^/]*)', path, 1)

    @staticmethod
    def get_s3_base_key(path):
        """
        Given full path (S3), extract just the key (path after bucket name)
        :param path: 
        :return: 
        """
        if str(path).startswith('s3://'):
            return utils.do_match('s3://([^/]*)/(.*)', path, 2)
        else:
            return utils.do_match('([^/]*)/(.*)', path, 2)

    @staticmethod
    def get_s3_key(path):
        """
        Given full path (S3 or file), extract just the key (which is just the file name)
        :param path: 
        :return: 
        """
        path1 = str(path).replace('\\', '/')
        return path1[path1.rfind('/') + 1:]
