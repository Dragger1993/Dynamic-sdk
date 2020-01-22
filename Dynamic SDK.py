#!/usr/bin/python
import urllib2
import httplib
import json
import logging
import time
import os


from openpyxl import Workbook
RETURN_CODE=[99,99,99,99,99,99,99]
# maestro_url='http://62.92.49.58/api/v1'
maestro_url = 'http://10.237.187.56/api/v1'
maestro_login = 'automation@arris.com'
maestro_pass = 'witbe77Auto'

# log_level = logging.DEBUG
log_level = logging.INFO

dev_name = 'SKY_PERFECT_SMOKE_TEST'
# task_name = 'EPG Test'
#dev_name = 'Test_long_key_press'
task_name = 'DUMMY TEST'

def make_report(returncode,user_returncode,NO_OF_TEST_CASES):
    filename = "test_report.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet["A1"] = "SL"
    sheet["B1"] = "TEST CASE DETAILS"
    sheet["C1"] = "RESULT"
    sheet["D1"] = "REMARKS"
    sheet["A2"] = "1"
    sheet["B2"] = "Check for boot screen"
    sheet["A3"] = "2"
    sheet["B3"] = "DUMMY1"
    sheet["A4"] = "3"
    sheet["B4"] = "DUMMY2"
    sheet["A5"] = "4"
    sheet["B5"] = "DUMMY3"
    i=0
    while i<NO_OF_TEST_CASES:
        j = i
        c = "C" + str(j + 2)
        d = "D" + str(j + 2)

        if user_returncode[i] != 99 and user_returncode[i] != None and len(user_returncode[i]) is not 0 :
            sheet[c] = "Conditional_pass"
            sheet[d] = "With return code" +str(user_returncode[i][0])
        elif returncode[i] == 0 :

            sheet[c] = "PASS"
            sheet[d] = "NA"
        elif returncode == -400:
            sheet[c] = "FAIL"
            sheet[d] = "Test terminated by user"
        else:
            sheet[c] = "FAIL"
            sheet[d] = "Test failed"
        i=i+1
    workbook.save(filename=filename)








def send_maestro_heartbeat(token):
    logging.info('sending heartbeat')
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=0), urllib2.HTTPSHandler(debuglevel=0))
    urllib2.install_opener(opener)
    json_heart = json.dumps('{"active_streams": { "devices": [] }}')
    req = urllib2.Request(maestro_url + '/heartbeats?authentication_token=' + token, json_heart)
    req.add_header('Content-Type', 'application/json')
    token = ''
    try:
        data = opener.open(req).read()
        logging.debug(data)
    except urllib2.HTTPError, e:
        logging.error('session HTTPError = ' + str(e.code) + "\n" + str(e.headers))
        raise
    except urllib2.URLError, e:
        logging.error('session URLError = ' + str(e.reason))
        raise
    except httplib.HTTPException, e:
        logging.error('session HTTPException')
        raise
    except Exception:
        logging.warn('session failed')
        raise
    except:
        logging.warn('Auth failed')
        raise
    return
def get_keys(dl, keys_list):
    if isinstance(dl, dict):
        keys_list += dl.keys()
        map(lambda x: get_keys(x, keys_list), dl.values())
    elif isinstance(dl, list):
        map(lambda x: get_keys(x, keys_list), dl)
keys = []

def login():
    keys = []
    logging.info('doing login')
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=0), urllib2.HTTPSHandler(debuglevel=0))
    urllib2.install_opener(opener)
    login = {'admin_user':
                 {'email': maestro_login, 'password': maestro_pass},
             'email': maestro_login, 'password': maestro_pass
             }

    json_login = json.dumps(login)
    req = urllib2.Request(maestro_url + '/sessions/?force=1', json_login)
    req.add_header('Content-Type', 'application/json')
    token = ''
    try:
        data = opener.open(req).read()

        token = json.loads(data)['authentication_token']
        logging.debug(data)
    except urllib2.HTTPError, e:
        logging.error('session HTTPError = ' + str(e.code) + "\n" + str(e.headers))
        raise
    except urllib2.URLError, e:
        logging.error('session URLError = ' + str(e.reason))
        raise
    except httplib.HTTPException, e:
        logging.error('session HTTPException')
        raise
    except Exception:
        logging.warn('session failed')
        raise
    except:
        logging.warn('Auth failed')
        raise
    return token


def read_devices_from_maestro(token):
    tab_devices_maestro = []
    logging.info('getting devices from maestro')
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=0), urllib2.HTTPSHandler(debuglevel=0))

    req = urllib2.Request(maestro_url + '/devices?authentication_token=' + token)
    try:
        data = opener.open(req).read()
        logging.debug(data)
        jdata=json.loads(data)
        tab_devices_maestro = json.loads(data)['devices']
    except urllib2.HTTPError, e:
        logging.error('channels HTTPError = ' + str(e.code) + "\n" + str(e.headers))
        raise
    except urllib2.URLError, e:
        logging.error('channels URLError = ' + str(e.reason))
        raise
    except httplib.HTTPException, e:
        logging.error('channels HTTPException')
        raise
    except Exception:
        logging.warn('channels failed')
        raise
    except:
        logging.warn('channels failed')
        raise

    return tab_devices_maestro


def read_tasks_from_maestro(token):
    tab_devices_maestro = []
    keys = []

    logging.info('getting devices from maestro')
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=0), urllib2.HTTPSHandler(debuglevel=0))
    req = urllib2.Request(maestro_url + '/campaigns?authentication_token=' + token)

    try:
        data = opener.open(req).read()
        logging.debug(data)

        tab_devices_maestro = json.loads(data)
        #print tab_devices_maestro["tasks"]
        #print tab_devices_maestro
        get_keys(tab_devices_maestro,keys)
        #print keys
        #print tab_devices_maestro["model_type'"]
    except urllib2.HTTPError, e:
        logging.error('channels HTTPError = ' + str(e.code) + "\n" + str(e.headers))
        raise
    except urllib2.URLError, e:
        logging.error('channels URLError = ' + str(e.reason))
        raise
    except httplib.HTTPException, e:
        logging.error('channels HTTPException')
        raise
    except Exception:
        logging.warn('channels failed')
        raise
    except:
        logging.warn('channels failed')
        raise

    return tab_devices_maestro

def read_task_instance_device(token, device_uuid):
    task_instances_device = []

    logging.info('getting task instances from maestro for device')
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=0), urllib2.HTTPSHandler(debuglevel=0))
    req = urllib2.Request(maestro_url + '/devices/' + device_uuid + '/task_instances?authentication_token=' + token)
    try:

        data = opener.open(req).read()
        logging.debug(data)
        task_instances_device = json.loads(data)['instances']
        #print str(json.loads(data))
        logging.debug(task_instances_device)
    except urllib2.HTTPError, e:

        logging.error('channels HTTPError = ' + str(e.code) + "\n" + str(e.headers))
        raise
    except urllib2.URLError, e:

        logging.error('channels URLError = ' + str(e.reason))
        raise
    except httplib.HTTPException, e:

        logging.error('channels HTTPException')
        raise
    except Exception:

        logging.warn('channels failed')
        raise
    except:

        logging.warn('channels failed')
        raise

   # print (str(task_instances_device)+"hello")
    return task_instances_device


def retrive_result_of_scenario(token, uuid):
    task_instances_device = []
    keys = []

    logging.info('getting campaign instances from maestro for device')
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=0), urllib2.HTTPSHandler(debuglevel=0))
    req = urllib2.Request(maestro_url + '/results/?authentication_token=' + token)
    try:

        data = opener.open(req).read()
        # print data
        logging.debug(data)
        jdata = json.loads(data)


        # print str(json.loads(data))
    except urllib2.HTTPError, e:

        logging.error('channels HTTPError = ' + str(e.code) + "\n" + str(e.headers))
        raise
    except urllib2.URLError, e:

        logging.error('channels URLError = ' + str(e.reason))
        raise
    except httplib.HTTPException, e:

        logging.error('channels HTTPException')
        raise
    except Exception:

        logging.warn('channels failed')
        raise
    except:

        logging.warn('channels failed')
        raise

    # print (str(task_instances_device)+"hello")

    return task_instances_device
def retrive_campaign(token,device_uuid):
    task_instances_device = []
    keys = []


    logging.info('getting campaign instances from maestro for device')
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=0), urllib2.HTTPSHandler(debuglevel=0))
    req = urllib2.Request(maestro_url +'/campaigns/?authentication_token=' + token)
    try:

        data = opener.open(req).read()
        #print data
        logging.debug(data)
        task_instances_device = json.loads(data)['campaigns']
        #get_keys(task_instances_device,keys)
        task_instances_device=task_instances_device[7]
        get_keys(task_instances_device,keys)

        #print task_instances_device
        #get_keys(task_instances_device,keys)
        #print keys
        exit()
        #print str(json.loads(data))
        logging.debug(task_instances_device)
    except urllib2.HTTPError, e:

        logging.error('channels HTTPError = ' + str(e.code) + "\n" + str(e.headers))
        raise
    except urllib2.URLError, e:

        logging.error('channels URLError = ' + str(e.reason))
        raise
    except httplib.HTTPException, e:

        logging.error('channels HTTPException')
        raise
    except Exception:

        logging.warn('channels failed')
        raise
    except:

        logging.warn('channels failed')
        raise

   # print (str(task_instances_device)+"hello")

    return task_instances_device


def read_task(token, task_id):
    task = {}

    logging.info('getting task from maestro')
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=0), urllib2.HTTPSHandler(debuglevel=0))

    req = urllib2.Request(maestro_url + '/tasks/' + str(task_id) + '?authentication_token=' + token)
    try:
        data = opener.open(req).read()
        logging.debug(data)
        task = json.loads(data)

    except urllib2.HTTPError, e:
        logging.error('channels HTTPError = ' + str(e.code) + "\n" + str(e.headers))
        raise
    except urllib2.URLError, e:
        logging.error('channels URLError = ' + str(e.reason))
        raise
    except httplib.HTTPException, e:
        logging.error('channels HTTPException')
        raise
    except Exception:
        logging.warn('channels failed')
        raise
    except:
        logging.warn('channels failed')
        raise

    return task
def read_campaign(token, task_id):
    task = {}

    logging.info('getting task from maestro')
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=0), urllib2.HTTPSHandler(debuglevel=0))

    req = urllib2.Request(maestro_url + '/campaigns/' + str(task_id) + '?authentication_token=' + token)
    try:
        data = opener.open(req).read()
        logging.debug(data)
        task = json.loads(data)

    except urllib2.HTTPError, e:
        logging.error('channels HTTPError = ' + str(e.code) + "\n" + str(e.headers))
        raise
    except urllib2.URLError, e:
        logging.error('channels URLError = ' + str(e.reason))
        raise
    except httplib.HTTPException, e:
        logging.error('channels HTTPException')
        raise
    except Exception:
        logging.warn('channels failed')
        raise
    except:
        logging.warn('channels failed')
        raise

    return task
def read_campaign_instance(token, device_uuid):
    task = {}
    logging.info('getting task from maestro')
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=0), urllib2.HTTPSHandler(debuglevel=0))

    req = urllib2.Request(maestro_url + '/devices/' + device_uuid +'/campaign_instances?authentication_token=' + token)
    try:
        data = opener.open(req).read()
        logging.debug(data)
        task_instances_device = json.loads(data)['instances']
        get_keys(task_instances_device,keys)
    except urllib2.HTTPError, e:
        logging.error('channels HTTPError = ' + str(e.code) + "\n" + str(e.headers))
        raise
    except urllib2.URLError, e:
        logging.error('channels URLError = ' + str(e.reason))
        raise
    except httplib.HTTPException, e:
        logging.error('channels HTTPException')
        raise
    except Exception:
        logging.warn('channels failed')
        raise
    except:
        logging.warn('channels failed')
        raise
    return task_instances_device



def run_task_instance(token, task_id, task_instance_id):
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=0), urllib2.HTTPSHandler(debuglevel=0))

    # http://192.168.252.192/api/v1/tasks/170/instances/1830/runs
    logging.info('run task on maestro')
    json_run = json.dumps('{"resource_token": ""}')
    req = urllib2.Request(maestro_url + '/tasks/' + str(task_id) + '/instances/' + str(
        task_instance_id) + '/runs?authentication_token=' + token, json_run)
    req.add_header('Content-Type', 'application/json')

    try:
        data = opener.open(req).read()
        logging.debug(data)
        run_data = json.loads(data)
    except urllib2.HTTPError, e:
        logging.error('channels HTTPError = ' + str(e.code) + "\n" + str(e.headers))
        raise
    except urllib2.URLError, e:
        logging.error('channels URLError = ' + str(e.reason))
        raise
    except httplib.HTTPException, e:
        logging.error('channels HTTPException')
        raise
    except Exception:
        logging.warn('channels failed')
        raise
    except:
        logging.warn('channels failed')
        raise

    return run_data

def run_campaign_instance(token, task_id, task_instance_id):
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=0), urllib2.HTTPSHandler(debuglevel=0))

    # http://192.168.252.192/api/v1/tasks/170/instances/1830/runs
    logging.info('run task on maestro')
    json_run = json.dumps('{"resource_token": ""}')
    req = urllib2.Request(maestro_url + '/campaigns/' + str(task_id) + '/instances/' + str(
        task_instance_id) + '/runs?authentication_token=' + token, json_run)
    req.add_header('Content-Type', 'application/json')

    try:
        data = opener.open(req).read()
        logging.debug(data)
        run_data = json.loads(data)
    except urllib2.HTTPError, e:
        logging.error('channels HTTPError = ' + str(e.code) + "\n" + str(e.headers))
        raise
    except urllib2.URLError, e:
        logging.error('channels URLError = ' + str(e.reason))
        raise
    except httplib.HTTPException, e:
        logging.error('channels HTTPException')
        raise
    except Exception:
        logging.warn('channels failed')
        raise
    except:
        logging.warn('channels failed')
        raise
    return run_data


def read_result_from_maestro(token, run_uuid):
    result = []
    logging.info('getting result from maestro')
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=0), urllib2.HTTPSHandler(debuglevel=0))

    req = urllib2.Request(maestro_url + '/campaign_results/' + str(run_uuid) + '?full=1&authentication_token=' + token)


    try:
        data = opener.open(req).read()

        data = opener.open(req).read()
        logging.debug(data)
        result = json.loads(data)
        get_keys(result,keys)
    except urllib2.HTTPError, e:
        if str(e.code) != '404':
            logging.error('channels HTTPError = ' + str(e.code) + "\n" + str(e.headers))
            raise
    except urllib2.URLError, e:
        logging.error('channels URLError = ' + str(e.reason))
        raise
    except httplib.HTTPException, e:
        logging.error('channels HTTPException')
        raise
    except Exception as e:
        logging.warn('channels failed')
        raise



    return result


def main():
    keys = []
    temp=""
    USER_RETURN_CODE_STORE = [99, 99, 99, 99, 99, 99, 99]
    RETURN_CODE_STORE = [99, 99, 99, 99, 99, 99, 99]

    print ("Automated smoke test started")
    print ("Waiting for a new build")
    while True:
        if os.path.isfile("C:\\Update_box\\main_sw.amg"):
            print ("New file detected")
            logging.basicConfig(level=log_level, format='%(asctime)s %(levelname)-8s | %(message)s', datefmt='%Y%m%d %H:%M:%S')
            target_device = {"MULTICHOICE -HAL TEST"}
            token = login()
            target_device = None
            target_task = None
            target_instance = None
            if token != '':
                devices = read_devices_from_maestro(token)
                logging.debug('devices = %s', devices)
                for d in devices:
                    if d['infos']['name'] == dev_name:
                    #if True:
                        print("Device is detected")
                        logging.debug('device = %s', d)
                        target_device = d

                        task_instances=read_campaign_instance(token,target_device['uuid'])

                        for ti in task_instances:
                            t = read_campaign(token, ti['campaign_id'])
                            time.sleep(5)


                            if t['name'] == task_name:
                                logging.debug('Found task_instance %s', ti)
                                target_task = t
                                target_instance = ti
                                break
                            else:
                                print ("Still searching ")
                                print(t['name'])

        # Finding campaign details from witbe system
            if target_device is not None and target_task is not None and target_instance is not None:

                run_data = run_campaign_instance(token, target_instance['campaign_id'], target_instance['id'])
                time.sleep(4)
                if "progress" in run_data['reason']:
                    logging.info("Task running with run uuid = %s", run_data['uuid'])
                    trys = 0
                    while trys < 10:
                        result = read_result_from_maestro(token, run_data['uuid'])
                        if len(result):
                            #logging.info('result = %s', result)
                            time.sleep(1)
                            temp=result["scenario"]["path"][0]["path"][0]["output_parameters"]["returncode"]
                            temp1=result["scenario"]["path"][0]["path"][1]["output_parameters"]["returncode"]
                            temp2=result["scenario"]["path"][0]["path"][2]["output_parameters"]["returncode"]
                            No_of_test_case=len(result["scenario"]["path"][0]["path"])

                            i=0
                            while i<No_of_test_case:
                                USER_RETURN_CODE_STORE[i] =result["scenario"]["path"][0]["path"][i]["output_parameters"]["user_error_codes"]

                                RETURN_CODE_STORE[i]= result["scenario"]["path"][0]["path"][i]["output_parameters"]["returncode"]
                                uuid=result["scenario"]["path"][0]["path"][i]["name"]


                                i=i+1
                            print USER_RETURN_CODE_STORE + RETURN_CODE_STORE
                            make_report(RETURN_CODE_STORE,USER_RETURN_CODE_STORE,No_of_test_case)

                            if 'legacy' in result['data']:
                                logging.info('legacy = \n%s', result['data']['legacy'])
                            break
                        else:
                            logging.info("No result, sleeping 30s")
                            send_maestro_heartbeat(token)
                            time.sleep(30)
                            trys = trys + 1

                else:
                    logging.warn("Task not running, maestro response %s", run_data)
            else:
                logging.warn("Task Not found")
        exit(1)


if __name__ == "__main__":
    main()

# vi: set bg=dark:


