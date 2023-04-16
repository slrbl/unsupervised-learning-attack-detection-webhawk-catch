# About: Utilities
# Author: walid.daboubi@gmail.com
# Version: 2.0 - 2022/08/14

import configparser
import re
import sys
import time
import pandas as pd

def get_process_col_locations(header_line, list_col_names):
    col_locations = {}
    for idx, col_name in enumerate(list_col_names):
        col_width = len(col_name)
        col_locations[col_name] = {}
        
        if idx == 0:
            col_locations[col_name]['start_idx'] = 0
        else:
            col_locations[col_name]['start_idx'] = col_locations[list_col_names[idx-1]]['end_idx']
            
        if idx+1 < len(list_col_names):
            re_pattern = r"(?<={})(.*?)(?={})".format(col_name, list_col_names[idx+1])
        else:
            re_pattern = r"(?<={})(.*?)".format(col_name)
        whitespaces = re.findall(re_pattern, header_line)
        col_width += len(whitespaces[0])
        col_locations[col_name]['end_idx'] = col_locations[col_name]['start_idx']+col_width
    return col_locations

def parse_process_file(process_file):
    with open(process_file) as f:
        processes_lines = f.readlines()

    summary_line_pattern = r'^\D*:'
    is_header_line = False
    is_header_line_seen = False
    process_data = []
    
    for line in processes_lines:
        process_dict = {}

        is_summary_line = re.match(summary_line_pattern, line)
        if is_summary_line:
            is_header_line_seen = False
            
        is_header_line = True if 'PID' in line and '%CPU' in line else False
        if is_header_line:
            header_line = line.strip()
            list_col_names = header_line.split()
            col_locations = get_process_col_locations(header_line, list_col_names)
            is_header_line = False
            is_header_line_seen = True
            continue
        
        if is_header_line_seen:
            for col_name in col_locations:
                col_start_idx = col_locations[col_name]['start_idx']
                col_end_idx = col_locations[col_name]['end_idx']
                process_value = line[col_start_idx:col_end_idx].strip()
                try:
                    process_dict[col_name] = float(process_value)
                except:
                    process_dict[col_name] = process_value
                    
            process_data.append(process_dict)
    return process_data

def encode_single_line(single_line,features):
    return ",".join((str(single_line[feature]) for feature in features))


# Encode a single log line/Extract features
def encode_log_line(log_line,log_type,indices):
    # log_type is apache for the moment
    try:
        log_format = config['LOG'][log_type]
    except:
        print('Log type \'{}\' not defined. \nMake sure "settings.conf" file exits and the log concerned type is defined.\nExiting'.format(log_type))
        sys.exit(1)
    if log_format in [None,'']:
        print('Log format \'{}{}\' is empty'.format(log_type,log_format))
        sys.exit(1)
    try:
        log_line = re.match(log_format,log_line).groups()
    except:
        print('Something went wrong parsing the log format \'{}\''.format(log_type))
        sys.exit(0)

    # Getting log details for APACHE
    # Extracting the URL

    ip = log_line[0]
    http_query = log_line[2].split(' ')[0]
    url="".join(log_line[2].split(' ')[1:])
    # The features that are currently taken in account are the following
    return_code = log_line[3]
    params_number = len(url.split('&'))
    url_length = len(url)
    size = str(log_line[4]).rstrip('\n')
    url_depth = url.count("/")
    upper_cases = sum(1 for c in url if c.isupper())
    lower_cases = len(url) - upper_cases
    special_chars = sum(1 for c in url if c in SPECIAL_CHARS)
    size = 0 if '-' in size else int(size)
    user_agent=log_line[6]
    if (int(return_code) > 0):
        log_line_data = {}
        log_line_data['size'] = size
        log_line_data['params_number'] = params_number
        log_line_data['length'] = url_length
        log_line_data['return_code'] = float(return_code)
        log_line_data['upper_cases'] = upper_cases
        log_line_data['lower_cases'] = lower_cases
        log_line_data['special_chars'] = special_chars
        log_line_data['url_depth'] = float(url_depth)
        log_line_data['ip'] = indices['ips'].index(ip)+1
        log_line_data['http_query'] = 100*(indices['http_queries'].index(http_query)+1)
        log_line_data['user_agent'] = indices['user_agents'].index(user_agent)+1
    else:
        log_line_data = None
    return url, log_line_data

# Encode all the data in http log file (access_log)
def encode_log_file(log_file,log_type):
    data = {}
    indices = get_categorical_indices(log_file,log_type)
    log_file = open(log_file, 'r')
    for log_line in log_file:
        log_line=log_line.replace(',','#').replace(';','#')
        _,log_line_data = encode_log_line(log_line,log_type,indices)
        if log_line_data is not None:
            #data[url] = log_line_data
            data[log_line] = log_line_data
    return data


def get_categorical_indices(log_file,log_type):
    incides = {
        'http_queries':[],
        'user_agents':[],
        'ips':[]
    }
    log_file = open(log_file, 'r')
    for log_line in log_file:
        log_line=log_line.replace(',','#').replace(';','#')
        try:
            log_format = config['LOG'][log_type]
        except:
            print('Log type \'{}\' not defined. \nMake sure "settings.conf" file exits and the log concerned type is defined.\nExiting'.format(log_type))
            sys.exit(1)
        try:
            log_line = re.match(log_format,log_line).groups()
        except:
            print('Log type \'{}\' doesn\'t fit your log fomat.\nExiting'.format(log_type))
            sys.exit(1)

        http_query=log_line[2].split(' ')[0]
        if http_query not in incides['http_queries']:
            incides['http_queries'].append(http_query)

        user_agent=log_line[6]
        if user_agent not in incides['user_agents']:
            incides['user_agents'].append(user_agent)

        ip=log_line[0]
        if ip not in incides['ips']:
            incides['ips'].append(ip)

    return incides

def construct_enconded_data_file(data,set_simulation_label):
	labelled_data_str = f"{config['FEATURES']['features']},label,log_line\n"
	for url in data:
		# U for unknown
		attack_label = 'U'
		if set_simulation_label==True:
			attack_label = '0'
			# Ths patterns are not exhaustive and they are here just for the simulation purpose
			patterns = ('honeypot', '%3b', 'xss', 'sql', 'union', '%3c', '%3e', 'eval')
			if any(pattern in url.lower() for pattern in patterns):
				attack_label = '1'
		labelled_data_str += f"{encode_single_line(data[url],FEATURES)},{attack_label},{url}"
	return len(data),labelled_data_str




def gen_report(findings,log_file,log_type):
    gmt_time=time.strftime("%d/%m/%y at %H:%M:%S GMT", time.gmtime())
    report_str="""
        <head>
            <style>
                td {
                  padding: 5px;
                }
                th {
                  text-align:left;
                  padding: 10px;
                  background-color: whitesmoke;
                }
                div {
                  font-family:monospace;
                  padding: 50px;
                }
            </style>
        </head>
    """
    report_str+="""
        <div>
            <h1>Webhawk Catch Report</h1>
            <p>
                Unsupervised learning Web logs attack detection.
            </p>
            Date: {}
            <br>
            Log file: {}
            <br>
            Log type: {} logs
            <br>
            <h3>Findings: {}</h3>
        <table>
            <tr style="background:whitesmoke;padding:10px">
                <td>Severity</td>
                <td>Line#</td>
                <td>Log line</td>
            </tr>
    """.format(gmt_time,log_file,log_type,len(findings))
    for finding in findings:
        severity=finding['severity']
        if severity == 'medium':
            background='orange'
        if severity == 'high':
            background='OrangeRed'
        report_str+="""
            <tr>
                <td style="background:{};text-align:center;color:whitesmoke">{}</td>
                <td>{}</td>
                <td>{}</td>
            </tr>
        """.format(background,severity.capitalize(),finding['log_line_number']+1,finding['log_line'])
    report_str+="</table></div>"
    with open('./SCANS/scan_result_{}.html'.format(log_file.split('/')[-1]),'w') as result_file:
        result_file.write(report_str)


config = configparser.ConfigParser()
config.sections()
config.read('settings.conf')

SPECIAL_CHARS = set("[$&+,:;=?@#|'<>.^*()%!-]")

try:
    FEATURES = config['FEATURES']['features'].split(',')
except:
    print('No features defined. Make sure the file "settings.conf" exists and training/prediction features are defined.')
    print('Exiting..')
    sys.exit(1)
