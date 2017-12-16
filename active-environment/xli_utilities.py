import re
import json


def s3_path_combine(*args):
    ret_val = ('/'.join(args)).replace('//', '/').replace('https:/', 'https://')
    ret_val = ret_val[1:] if ret_val.startswith('/') else ret_val

    return ret_val


def do_match(regex, string, group_idx=1):
    match = re.search(regex, string)
    if match:
        return match.group(group_idx)

    return ""


def get_json(file_name):
    try:
        with open(file_name, 'r') as fp:
            ret_data = json.load(fp)
    except Exception as ex:
        print(ex)
        ret_data = {}

    return ret_data


def put_json(file_name, json_data):
    try:
        with open(file_name, 'w') as fp:
            fp.write(json.dumps(json_data, indent=2))
    except Exception as ex:
        print(ex)