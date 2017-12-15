import socket
import re
from datetime import datetime


def do_match(regex, string, group_idx=1):
    match = re.search(regex, string)
    if match:
        return match.group(group_idx)

    return ""


def set_all_inactive(environments):
    for e in environments:
        e['active'] = False

    return environments


def get_current_active_environment(environments):
    active_count = 0
    ret_val = {}

    for e in environments:
        if e['active']:
            ret_val = e
            active_count += 1

    if active_count > 1:
        raise RuntimeError("Found more than one active environments")

    return ret_val


def update_last_active(environments):
    ret_val = environments.copy()

    for e in ret_val:
        if e['active']:
            e['last-time-active'] = datetime.utcnow().isoformat()

    return ret_val


def update_became_active(environments, env_name):
    ret_val = set_all_inactive(environments.copy())

    for e in ret_val:
        if e['name'] == env_name:
            e['last-time-active'] = datetime.utcnow().isoformat()
            e['became-active'] = datetime.utcnow().isoformat()
            e['active'] = True

    return ret_val


def update_environments(environments, active_env):
    """
    environments is predefined JSON list.  Each object must contain at least these keys:
    - name              : used to identify environment
    - active            : indicates if environment is currently active
    - became-active     : ISO timestamp when environment became active
    - last-time-active  : ISO timestamp when environment was active last (last audit time)

    Only one environment in the list can be active
        
    :param environments: 
    :param active_env: 
    :return: 
    """

    current_active_env = get_current_active_environment(environments)

    if 'name' in current_active_env and current_active_env['name'] == active_env:
        ret_val = update_last_active(environments)
    else:
        ret_val = update_became_active(environments, active_env)

    return ret_val


def audit(config):
    active_env = find_active(config)

    config['environments'] = update_environments(config['environments'], active_env)

    return config


def find_active(config):
    return find_active_by_type(config['audit'])


def find_active_by_type(audit_config):
    if audit_config['type'] == 'url':
        return find_active_by_url(audit_config['params'])


def find_active_by_url(params):
    host_info = socket.gethostbyname_ex(params['url'])

    return do_match(params['regex'], host_info[0])
