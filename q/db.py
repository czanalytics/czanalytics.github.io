# db.py implement kb.py endpoints

import logging as log # log.debug/info/warning 
import json
import pandas as pd
import datetime
#import net


# available knowledgebases
conf_kb = {'kb': 'toll'}
conf_schema = {'schema': 'null'}

conf = {'version': '0.06',
        'app_ip': '0.0.0.0',
        'kb_port': 5555,
        'data': conf_kb,
        'schema': conf_schema
        }


lv = log.DEBUG
log.basicConfig(format='%(asctime)s, %(name)s, %(levelname)s: %(message)s, %(funcName)s:%(lineno)s', level=lv)

#dp = pd.read_csv("./nuts.csv") # data for lite-models

#log.INFO('data read')

def get_conf():
    """
    The use assumes KB file in YAML format.
    """
    with open('./kb.yml', 'r') as JSON:
        dic = json.load(JSON)
    return dic

#con = get_conf()

def kb_est(d, mod):
    """
    Evaluate the KB query.
    """

    d = 0

    return d

