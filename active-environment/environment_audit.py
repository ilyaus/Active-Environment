import environment
import s3


AWS_PROFILE = ''
AWS_REGION = ''
S3_BUCKET = ''
ENV_STATUS_KEY = 'audit-config.json'
ENV_STATUS_KEY_RESULT = 'audit-config.json'


def run(event, context):
    s3_obj = s3.AwsS3(s3=S3_BUCKET)
    s3_obj.put_json(ENV_STATUS_KEY_RESULT, environment.audit(s3_obj.get_json(ENV_STATUS_KEY)))


def main():
    pass

if __name__ == "__main__":
    main()
