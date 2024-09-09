import logging
import json

from trestle.common import log

logger = logging.getLogger(__name__)
trace = log.Trace(logger)


def deep_merge(a: dict, b: dict) -> dict:
    for key in b:
        if key in a and a[key]:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                trace.log(f'Deep merge for {key}')
                deep_merge(a[key], b[key])
            elif isinstance(a[key], list) and isinstance(b[key], list):
                trace.log(f'List merge for {key}')
                a[key] = _deduplicated_list(a[key], b[key])
            else:
                trace.log(f'Not copying key: {key}')
        else:
            trace.log(f'Copying {key} to a')
            a[key] = b[key]
    return a


def _deduplicated_list(a: list, b: list) -> list:
    if len(b) == 0:
        return a
    combined_list = b + a
    if 'id' in a[0]:
        # deduplicate by id
        return list({x['id']: x for x in combined_list}.values())
    elif 'uuid' in a[0]:
        # deduplicate by uuid
        return list({x['uuid']: x for x in combined_list}.values())
    else:
        try:
            # deduplicate by all fields via json string
            dedupped = set(json.dumps(item, sort_keys=True) for item in combined_list)
            return list(json.loads(x) for x in dedupped)
        except TypeError:
            # error dumping to json, just combine the lists
            return combined_list
