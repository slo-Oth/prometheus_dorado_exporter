import configparser
import json
import requests
import urllib3
urllib3.disable_warnings()

config = configparser.ConfigParser()
config.read('config.ini')
port = config['DEFAULT']['port']
user = config['DEFAULT']['dorado_user']
password = config['DEFAULT']['dorado_password']


def api_connect(api_user, api_password, api_ip, api_port):
    api_url = "https://{0}:{1}/deviceManager/rest/xxxxx/sessions".format(api_ip, api_port)
    api_data = json.dumps({'scope': '0', 'username': api_user, 'password': api_password})
    headers = {'Connection': 'keep-alive', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    api_connect = requests.post(api_url, verify=False, data=api_data, headers=headers)
    api_connect_info = (json.loads(api_connect.content.decode('utf8')), api_connect.cookies)  # Decode нужен потому что объект имеет тип bytes
    return api_connect_info


def api_logout(api_ip, api_port, api_cookies, device_id, iBaseToken):
    headers = {'Connection': 'keep-alive', 'Content-Type': 'application/json', 'Accept': 'application/json', 'iBaseToken': iBaseToken}
    api_url_exit = "https://{0}:{1}/deviceManager/rest/{2}/sessions".format(api_ip, api_port, device_id)
    exit = requests.delete(api_url_exit, verify=False, headers=headers, cookies=api_cookies)

    convert_exit = json.loads(exit.content.decode('utf8'))
    return convert_exit['error']['code']


def get_data(api_connection, api_host, api_port, path, params={}):
    device_id = api_connection[0]['data']['deviceid']
    endpoint = "https://{0}:{1}/deviceManager/rest/{2}/{3}".format(api_host, api_port, device_id, path)
    api_cookies = api_connection[1]
    r = requests.get(endpoint, verify=False, cookies=api_cookies, params=params)
    result = json.loads(r.content.decode('cp1251'))
    return result


def get_disk_data(metrics, connection, api_host, api_port):
    data = get_data(connection, api_host, api_port, "disk")
    for entry in data["data"]:
        labels = [
                    ("type", "disk"),
                    ("serial", entry["SERIALNUMBER"]),
                    ("barcode", entry["barcode"]),
                    ("model", entry["MODEL"]),
                    ("location", entry["LOCATION"]),
                    ("id", entry["ID"])
                    ]
        metric_dict = {
                            "key": "huawei_storage_component_health_status",
                            "value": entry["HEALTHSTATUS"],
                            "customlabels": [("status_text", valuemap["health_status"][entry["HEALTHSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_component_running_status",
                            "value": entry["RUNNINGSTATUS"],
                            "customlabels": [("status_text", valuemap["running_status"][entry["RUNNINGSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_component_temperature",
                            "value": entry["TEMPERATURE"],
                            "customlabels": [],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_remainlife",
                            "value": entry["REMAINLIFE"],
                            "customlabels": [],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_usage",
                            "value": entry["CAPACITYUSAGE"],
                            "customlabels": [],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        stats_uid = "{0}:{1}".format(entry["TYPE"], entry["ID"])
        perfmetrics_list = [
                            "read_iops",
                            "read_mbytes",
                            "write_iops",
                            "write_mbytes",
                            "avg_read_latency",
                            "avg_write_latency",
                            "queue_length"
                            ]
        data_ids = ""
        for metric in perfmetrics_list:
            data_ids += valuemap["data_ids"][metric] + ','
        params = {"CMO_STATISTIC_UUID": stats_uid, "CMO_STATISTIC_DATA_ID_LIST": data_ids}
        data = get_data(connection, api_host, api_port, "performace_statistic/cur_statistic_data", params=params)
        values = data["data"][0]["CMO_STATISTIC_DATA_LIST"].split(',')
        i = 0
        for metric in perfmetrics_list:
            metric_dict = {
                                "key": "huawei_storage_metrics_{0}".format(metric),
                                "value": values[i],
                                "customlabels": [],
                                "labels": labels
                                }
            metrics.append(metric_dict)
            i += 1
    return metrics


def get_power_data(metrics, connection, api_host, api_port):
    data = get_data(connection, api_host, api_port, "power")
    for entry in data["data"]:
        labels = [
                    ("type", "PSU"),
                    ("serial", entry["SERIALNUMBER"]),
                    ("id", entry["ID"]),
                    ("model", entry["MODEL"]),
                    ("name", entry["NAME"]),
                    ("location", entry["LOCATION"]),
                    ]
        metric_dict = {
                            "key": "huawei_storage_component_health_status",
                            "value": entry["HEALTHSTATUS"],
                            "customlabels": [("status_text", valuemap["health_status"][entry["HEALTHSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_component_running_status",
                            "value": entry["RUNNINGSTATUS"],
                            "customlabels": [("status_text", valuemap["running_status"][entry["RUNNINGSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)

    return metrics


def get_bbu_data(metrics, connection, api_host, api_port):
    data = get_data(connection, api_host, api_port, "backup_power")
    for entry in data["data"]:
        # print(json.dumps(entry, indent=2))
        labels = [
                    ("type", "bbu"),
                    ("id", entry["ID"]),
                    ("name", entry["NAME"]),
                    ("location", entry["LOCATION"]),
                    ]
        metric_dict = {
                            "key": "huawei_storage_component_health_status",
                            "value": entry["HEALTHSTATUS"],
                            "customlabels": [("status_text", valuemap["health_status"][entry["HEALTHSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_component_running_status",
                            "value": entry["RUNNINGSTATUS"],
                            "customlabels": [("status_text", valuemap["running_status"][entry["RUNNINGSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_remainlife",
                            "value": entry["REMAINLIFEDAYS"],
                            "customlabels": [],
                            "labels": labels
                            }
        metrics.append(metric_dict)
    return metrics


def get_enclosure_data(metrics, connection, api_host, api_port):
    data = get_data(connection, api_host, api_port, "enclosure")
    for entry in data["data"]:
        # print(json.dumps(entry, indent=2))
        labels = [
                    ("type", "enclosure"),
                    ("serial", entry["SERIALNUM"]),
                    ("id", entry["ID"]),
                    ("name", entry["NAME"]),
                    ("model", entry["MODEL"]),
                    ]
        metric_dict = {
                            "key": "huawei_storage_component_health_status",
                            "value": entry["HEALTHSTATUS"],
                            "customlabels": [("status_text", valuemap["health_status"][entry["HEALTHSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_component_running_status",
                            "value": entry["RUNNINGSTATUS"],
                            "customlabels": [("status_text", valuemap["running_status"][entry["RUNNINGSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_component_temperature",
                            "value": entry["TEMPERATURE"],
                            "customlabels": [],
                            "labels": labels
                            }
        metrics.append(metric_dict)
    return metrics


def get_controller_data(metrics, connection, api_host, api_port):
    data = get_data(connection, api_host, api_port, "controller")
    for entry in data["data"]:
        # print(json.dumps(entry, indent=2))
        labels = [
                    ("type", "controller"),
                    ("id", entry["ID"]),
                    ("name", entry["NAME"]),
                    ("location", entry["LOCATION"]),
                    ]
        metric_dict = {
                            "key": "huawei_storage_component_health_status",
                            "value": entry["HEALTHSTATUS"],
                            "customlabels": [("status_text", valuemap["health_status"][entry["HEALTHSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_component_running_status",
                            "value": entry["RUNNINGSTATUS"],
                            "customlabels": [("status_text", valuemap["running_status"][entry["RUNNINGSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_controller_cpuusage",
                            "value": entry["CPUUSAGE"],
                            "customlabels": [],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_controller_memorysize",
                            "value": entry["MEMORYSIZE"],
                            "customlabels": [],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_controller_memoryusage",
                            "value": entry["MEMORYUSAGE"],
                            "customlabels": [],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        stats_uid = "{0}:{1}".format(entry["TYPE"], entry["ID"])
        perfmetrics_list = [
                            "queue_length",
                            "read_iops",
                            "read_mbytes",
                            "write_iops",
                            "write_mbytes",
                            "max_latency",
                            "avg_read_latency",
                            "avg_write_latency",
                            "avg_cpu_usage",
                            "avg_cache_usage",
                            "read_cache_hits",
                            "write_cache_hits",
                            "read_cache_usage",
                            "write_cache_usage",
                            "cache_page_usage",
                            "cache_chunk_usage",
                            "max_read_kbytes",
                            "max_write_kbytes",
                            # "failed_reads",
                            # "failed_writes",
                            # "usage"
                            ]
        data_ids = ""
        for metric in perfmetrics_list:
            data_ids += valuemap["data_ids"][metric] + ','
        params = {"CMO_STATISTIC_UUID": stats_uid, "CMO_STATISTIC_DATA_ID_LIST": data_ids}
        data = get_data(connection, api_host, api_port, "performace_statistic/cur_statistic_data", params=params)
        values = data["data"][0]["CMO_STATISTIC_DATA_LIST"].split(',')
        i = 0
        for metric in perfmetrics_list:
            metric_dict = {
                                "key": "huawei_storage_metrics_{0}".format(metric),
                                "value": values[i],
                                "customlabels": [],
                                "labels": labels
                                }
            metrics.append(metric_dict)
            i += 1
    return metrics


def get_intf_module_data(metrics, connection, api_host, api_port):
    data = get_data(connection, api_host, api_port, "intf_module")
    for entry in data["data"]:
        # print(json.dumps(entry, indent=2))
        labels = [
                    ("type", "intf_module"),
                    ("id", entry["ID"]),
                    ("name", entry["NAME"]),
                    ("model", entry["MODEL"]),
                    ("location", entry["LOCATION"])
                    ]
        metric_dict = {
                            "key": "huawei_storage_component_health_status",
                            "value": entry["HEALTHSTATUS"],
                            "customlabels": [("status_text", valuemap["health_status"][entry["HEALTHSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_component_running_status",
                            "value": entry["RUNNINGSTATUS"],
                            "customlabels": [("status_text", valuemap["running_status"][entry["RUNNINGSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
    return metrics


def get_eth_port_data(metrics, connection, api_host, api_port):
    data = get_data(connection, api_host, api_port, "eth_port")
    for entry in data["data"]:
        # print(json.dumps(entry, indent=2))
        labels = [
                    ("type", "eth_port"),
                    ("id", entry["ID"]),
                    ("name", entry["NAME"]),
                    ("mac", entry["MACADDRESS"]),
                    ("ipv4", entry["IPV4ADDR"]),
                    ("v4mask", entry["IPV4MASK"]),
                    ("location", entry["LOCATION"]),
                    ("port_type_id", entry["LOGICTYPE"]),
                    ("port_type_text", valuemap["eth_port_types"][entry["LOGICTYPE"]]),
                    ]
        metric_dict = {
                            "key": "huawei_storage_component_health_status",
                            "value": entry["HEALTHSTATUS"],
                            "customlabels": [("status_text", valuemap["health_status"][entry["HEALTHSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_component_running_status",
                            "value": entry["RUNNINGSTATUS"],
                            "customlabels": [("status_text", valuemap["running_status"][entry["RUNNINGSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_port_errors",
                            "value": entry["crcErrors"],
                            "customlabels": [("error_type", "crc"), ("port_type", "eth")],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_port_errors",
                            "value": entry["frameErrors"],
                            "customlabels": [("error_type", "frame"), ("port_type", "eth")],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_port_errors",
                            "value": entry["frameLengthErrors"],
                            "customlabels": [("error_type", "frame_length"), ("port_type", "eth")],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        if entry["LOGICTYPE"] == "0":
            # Here we have management and host ports. Management ports don't have metrics, so we don't query them for not "0" port type
            stats_uid = "{0}:{1}".format(entry["TYPE"], entry["ID"])
            perfmetrics_list = [
                                "usage",
                                "queue_length",
                                "read_iops",
                                "read_mbytes",
                                "write_iops",
                                "write_mbytes",
                                "max_latency",
                                "avg_read_latency",
                                "avg_write_latency",
                                # "avg_cpu_usage",
                                # "avg_cache_usage",
                                # "read_cache_hits",
                                # "write_cache_hits",
                                # "read_cache_usage",
                                # "write_cache_usage",
                                # "cache_page_usage",
                                # "cache_chunk_usage",
                                # "max_read_kbytes",
                                # "max_write_kbytes",
                                # "failed_reads",
                                # "failed_writes",

                                ]
            data_ids = ""
            for metric in perfmetrics_list:
                data_ids += valuemap["data_ids"][metric] + ','
            params = {"CMO_STATISTIC_UUID": stats_uid, "CMO_STATISTIC_DATA_ID_LIST": data_ids}
            data = get_data(connection, api_host, api_port, "performace_statistic/cur_statistic_data", params=params)
            # print(json.dumps(data, indent=2))
            values = data["data"][0]["CMO_STATISTIC_DATA_LIST"].split(',')
            i = 0
            for metric in perfmetrics_list:
                metric_dict = {
                                    "key": "huawei_storage_metrics_{0}".format(metric),
                                    "value": values[i],
                                    "customlabels": [],
                                    "labels": labels
                                    }
                metrics.append(metric_dict)
                i += 1
    return metrics


def get_sas_port_data(metrics, connection, api_host, api_port):
    # I don't have them connected, so this function may contain bugs. Check out
    data = get_data(connection, api_host, api_port, "sas_port")
    for entry in data["data"]:
        # print(json.dumps(entry, indent=2))
        labels = [
                    ("type", "sas_port"),
                    ("id", entry["ID"]),
                    ("name", entry["NAME"]),
                    ("location", entry["LOCATION"]),
                    ]
        metric_dict = {
                            "key": "huawei_storage_component_health_status",
                            "value": entry["HEALTHSTATUS"],
                            "customlabels": [("status_text", valuemap["health_status"][entry["HEALTHSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_component_running_status",
                            "value": entry["RUNNINGSTATUS"],
                            "customlabels": [("status_text", valuemap["running_status"][entry["RUNNINGSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_port_errors",
                            "value": entry["DISPARITYERROR"],
                            "customlabels": [("error_type", "disparity"), ("port_type", "sas")],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_port_errors",
                            "value": entry["PHYRESETERRORS"],
                            "customlabels": [("error_type", "phy_reset"), ("port_type", "sas")],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        stats_uid = "{0}:{1}".format(entry["TYPE"], entry["ID"])
        perfmetrics_list = [
                            # "usage",
                            # "queue_length",
                            "read_iops",
                            "read_mbytes",
                            "write_iops",
                            "write_mbytes",
                            "max_latency",
                            "max_read_latency",
                            "max_write_latency",
                            "avg_read_latency",
                            "avg_write_latency",
                            # "avg_cpu_usage",
                            # "avg_cache_usage",
                            # "read_cache_hits",
                            # "write_cache_hits",
                            # "read_cache_usage",
                            # "write_cache_usage",
                            # "cache_page_usage",
                            # "cache_chunk_usage",
                            # "max_read_kbytes",
                            # "max_write_kbytes",
                            # "failed_reads",
                            # "failed_writes",

                            ]
        data_ids = ""
        for metric in perfmetrics_list:
            data_ids += valuemap["data_ids"][metric] + ','
        params = {"CMO_STATISTIC_UUID": stats_uid, "CMO_STATISTIC_DATA_ID_LIST": data_ids}
        data = get_data(connection, api_host, api_port, "performace_statistic/cur_statistic_data", params=params)
        # print(json.dumps(data, indent=2))
        values = data["data"][0]["CMO_STATISTIC_DATA_LIST"].split(',')
        i = 0
        for metric in perfmetrics_list:
            metric_dict = {
                                "key": "huawei_storage_metrics_{0}".format(metric),
                                "value": values[i],
                                "customlabels": [],
                                "labels": labels
                                }
            metrics.append(metric_dict)
            i += 1
    return metrics


def get_fan_data(metrics, connection, api_host, api_port):
    data = get_data(connection, api_host, api_port, "fan")
    for entry in data["data"]:
        # print(json.dumps(entry, indent=2))
        labels = [
                    ("type", "fan"),
                    ("id", entry["ID"]),
                    ("name", entry["NAME"]),
                    ("location", entry["LOCATION"])
                    ]
        metric_dict = {
                            "key": "huawei_storage_component_health_status",
                            "value": entry["HEALTHSTATUS"],
                            "customlabels": [("status_text", valuemap["health_status"][entry["HEALTHSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_component_running_status",
                            "value": entry["RUNNINGSTATUS"],
                            "customlabels": [("status_text", valuemap["running_status"][entry["RUNNINGSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
    return metrics


def get_lun_data(metrics, connection, api_host, api_port):
    data = get_data(connection, api_host, api_port, "lun")
    for entry in data["data"]:
        # print(json.dumps(entry, indent=2))
        labels = [
                    ("type", "lun"),
                    ("id", entry["ID"]),
                    ("name", entry["NAME"]),
                    ("wwn", entry["WWN"])
                    ]
        metric_dict = {
                            "key": "huawei_storage_component_health_status",
                            "value": entry["HEALTHSTATUS"],
                            "customlabels": [("status_text", valuemap["health_status"][entry["HEALTHSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_component_running_status",
                            "value": entry["RUNNINGSTATUS"],
                            "customlabels": [("status_text", valuemap["running_status"][entry["RUNNINGSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_capacity_total",
                            "value": entry["CAPACITY"],
                            "customlabels": [],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_capacity_allocated",
                            "value": entry["ALLOCCAPACITY"],
                            "customlabels": [],
                            "labels": labels
                            }
        metrics.append(metric_dict)

        stats_uid = "{0}:{1}".format(entry["TYPE"], entry["ID"])
        perfmetrics_list = [
                            # "usage",
                            "queue_length",
                            "read_iops",
                            "read_mbytes",
                            "write_iops",
                            "write_mbytes",
                            "max_latency",
                            # "max_read_latency",
                            # "max_write_latency",
                            "avg_read_latency",
                            "avg_write_latency",
                            # "avg_cpu_usage",
                            # "avg_cache_usage",
                            "read_cache_hits",
                            "write_cache_hits",
                            # "read_cache_usage",
                            # "write_cache_usage",
                            # "cache_page_usage",
                            # "cache_chunk_usage",
                            # "max_read_kbytes",
                            # "max_write_kbytes",
                            # "failed_reads",
                            # "failed_writes",

                            ]
        data_ids = ""
        for metric in perfmetrics_list:
            data_ids += valuemap["data_ids"][metric] + ','
        params = {"CMO_STATISTIC_UUID": stats_uid, "CMO_STATISTIC_DATA_ID_LIST": data_ids}
        data = get_data(connection, api_host, api_port, "performace_statistic/cur_statistic_data", params=params)
        # print(json.dumps(data, indent=2))
        values = data["data"][0]["CMO_STATISTIC_DATA_LIST"].split(',')
        i = 0
        for metric in perfmetrics_list:
            metric_dict = {
                                "key": "huawei_storage_metrics_{0}".format(metric),
                                "value": values[i],
                                "customlabels": [],
                                "labels": labels
                                }
            metrics.append(metric_dict)
            i += 1
    return metrics


def get_disk_pool_data(metrics, connection, api_host, api_port):
    data = get_data(connection, api_host, api_port, "diskpool")
    for entry in data["data"]:
        # print(json.dumps(entry, indent=2))
        labels = [
                    ("type", "disk_pool"),
                    ("id", entry["ID"]),
                    ("name", entry["NAME"]),
                    ]
        metric_dict = {
                            "key": "huawei_storage_component_health_status",
                            "value": entry["HEALTHSTATUS"],
                            "customlabels": [("status_text", valuemap["health_status"][entry["HEALTHSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_component_running_status",
                            "value": entry["RUNNINGSTATUS"],
                            "customlabels": [("status_text", valuemap["running_status"][entry["RUNNINGSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_capacity_total",
                            "value": entry["TOTALCAPACITY"],
                            "customlabels": [],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_capacity_allocated",
                            "value": entry["USEDCAPACITY"],
                            "customlabels": [],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_remainlife",
                            "value": entry["remainLife"],
                            "customlabels": [],
                            "labels": labels
                            }
        metrics.append(metric_dict)

        stats_uid = "{0}:{1}".format(entry["TYPE"], entry["ID"])
        perfmetrics_list = [
                            # "usage",
                            "queue_length",
                            "read_iops",
                            "read_mbytes",
                            "write_iops",
                            "write_mbytes",
                            "max_latency",
                            # "max_read_latency",
                            # "max_write_latency",
                            "avg_read_latency",
                            "avg_write_latency",
                            # "avg_cpu_usage",
                            # "avg_cache_usage",
                            # "read_cache_hits",
                            # "write_cache_hits",
                            # "read_cache_usage",
                            # "write_cache_usage",
                            # "cache_page_usage",
                            # "cache_chunk_usage",
                            # "max_read_kbytes",
                            # "max_write_kbytes",
                            # "failed_reads",
                            # "failed_writes",

                            ]
        data_ids = ""
        for metric in perfmetrics_list:
            data_ids += valuemap["data_ids"][metric] + ','
        params = {"CMO_STATISTIC_UUID": stats_uid, "CMO_STATISTIC_DATA_ID_LIST": data_ids}
        data = get_data(connection, api_host, api_port, "performace_statistic/cur_statistic_data", params=params)
        # print(json.dumps(data, indent=2))
        values = data["data"][0]["CMO_STATISTIC_DATA_LIST"].split(',')
        i = 0
        for metric in perfmetrics_list:
            metric_dict = {
                                "key": "huawei_storage_metrics_{0}".format(metric),
                                "value": values[i],
                                "customlabels": [],
                                "labels": labels
                                }
            metrics.append(metric_dict)
            i += 1
    return metrics


def get_storage_pool_data(metrics, connection, api_host, api_port):
    data = get_data(connection, api_host, api_port, "storagepool")
    for entry in data["data"]:
        # print(json.dumps(entry, indent=2))
        labels = [
                    ("type", "storage_pool"),
                    ("id", entry["ID"]),
                    ("name", entry["NAME"]),
                    ]
        metric_dict = {
                            "key": "huawei_storage_component_health_status",
                            "value": entry["HEALTHSTATUS"],
                            "customlabels": [("status_text", valuemap["health_status"][entry["HEALTHSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_component_running_status",
                            "value": entry["RUNNINGSTATUS"],
                            "customlabels": [("status_text", valuemap["running_status"][entry["RUNNINGSTATUS"]])],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_capacity_total",
                            "value": entry["USERTOTALCAPACITY"],
                            "customlabels": [],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        metric_dict = {
                            "key": "huawei_storage_capacity_allocated",
                            "value": entry["USERWRITEALLOCCAPACITY"],
                            "customlabels": [],
                            "labels": labels
                            }
        metrics.append(metric_dict)
        stats_uid = "{0}:{1}".format(entry["TYPE"], entry["ID"])
        perfmetrics_list = [
                            # "usage",
                            "queue_length",
                            "read_iops",
                            "read_mbytes",
                            "write_iops",
                            "write_mbytes",
                            "max_latency",
                            # "max_read_latency",
                            # "max_write_latency",
                            "avg_read_latency",
                            "avg_write_latency",
                            # "avg_cpu_usage",
                            # "avg_cache_usage",
                            # "read_cache_hits",
                            # "write_cache_hits",
                            # "read_cache_usage",
                            # "write_cache_usage",
                            # "cache_page_usage",
                            # "cache_chunk_usage",
                            # "max_read_kbytes",
                            # "max_write_kbytes",
                            # "failed_reads",
                            # "failed_writes",

                            ]
        data_ids = ""
        for metric in perfmetrics_list:
            data_ids += valuemap["data_ids"][metric] + ','
        params = {"CMO_STATISTIC_UUID": stats_uid, "CMO_STATISTIC_DATA_ID_LIST": data_ids}
        data = get_data(connection, api_host, api_port, "performace_statistic/cur_statistic_data", params=params)
        # print(json.dumps(data, indent=2))
        values = data["data"][0]["CMO_STATISTIC_DATA_LIST"].split(',')
        i = 0
        for metric in perfmetrics_list:
            metric_dict = {
                                "key": "huawei_storage_metrics_{0}".format(metric),
                                "value": values[i],
                                "customlabels": [],
                                "labels": labels
                                }
            metrics.append(metric_dict)
            i += 1
    return metrics


def collect_data(full_host):
    api_host = full_host.split(':')[0]
    api_port = int(full_host.split(':')[1])
    connection = api_connect(user, password, api_host, api_port)
    metrics = []
    metrics = get_disk_data(metrics, connection, api_host, api_port)
    metrics = get_power_data(metrics, connection, api_host, api_port)
    metrics = get_enclosure_data(metrics, connection, api_host, api_port)
    metrics = get_controller_data(metrics, connection, api_host, api_port)
    metrics = get_bbu_data(metrics, connection, api_host, api_port)
    # metrics = get_expboard_data(metrics, connection, api_host, api_port)  TODO: parse expboard output. I don't have one
    metrics = get_intf_module_data(metrics, connection, api_host, api_port)
    metrics = get_eth_port_data(metrics, connection, api_host, api_port)
    metrics = get_sas_port_data(metrics, connection, api_host, api_port)
    # metrics = get_fc_port_data(metrics, connection, api_host, api_port) TODO: parse fc_port output. I don't have one
    metrics = get_fan_data(metrics, connection, api_host, api_port)
    metrics = get_lun_data(metrics, connection, api_host, api_port)
    metrics = get_disk_pool_data(metrics, connection, api_host, api_port)
    get_storage_pool_data(metrics, connection, api_host, api_port)
    device_id = connection[0]['data']['deviceid']
    api_cookies = connection[1]
    iBaseToken = connection[0]['data']['iBaseToken']
    api_logout(api_host, api_port, api_cookies, device_id, iBaseToken)
    return metrics


def prometheus_output(metrics):
    text_out = ""
    for metric in metrics:
        text_out += metric["key"] + '{'
        for label in metric["labels"]:
            text_out += label[0] + '="' + label[1] + '",'
        for label in metric["customlabels"]:
            text_out += label[0] + '="' + label[1] + '",'
        text_out = text_out[:-1] + '} ' + metric["value"] + '\n'
    return text_out


valuemap = {
            "health_status": {
                "0": "unknown",
                "1": "normal",
                "2": "faulty",
                "3": "about_to_fail",
                "5": "degraded",
                "9": "inconsistent",
                "11": "no input",
                "12": "low_battery"
                },
            "running_status": {
                    "0": "unknown",
                    "1": "normal",
                    "2": "running",
                    "3": "not_running",
                    "5": "sleep_in_high_temperature",
                    "8": "spin_down",
                    "10": "link_up",
                    "11": "link_down",
                    "12": "powering_on",
                    "13": "powering_off",
                    "14": "pre-copy",
                    "16": "reconstruction",
                    "27": "online",
                    "28": "offline",
                    "32": "balancing",
                    "48": "charging",
                    "49": "charging_completed",
                    "50": "discharging",
                    "32": "balancing",
                    "53": "initializing",
                    "103": "power_on_failed",
                    "106": "deleting",
                },
            "data_ids": {
                    "read_iops": "22",
                    "read_mbytes": "23",
                    "write_iops": "28",
                    "write_mbytes": "26",
                    "max_read_latency": "382",
                    "max_write_latency": "383",
                    "avg_read_latency": "384",
                    "avg_write_latency": "385",
                    "max_latency": "371",
                    "failed_reads": "532",
                    "failed_writes": "533",
                    "usage": "18",
                    "queue_length": "19",
                    "avg_cpu_usage": "68",
                    "avg_cache_usage": "69",
                    "read_cache_hits": "93",
                    "write_cache_hits": "95",
                    "read_cache_usage": "110",
                    "write_cache_usage": "120",
                    "cache_page_usage": "1055",
                    "cache_chunk_usage": "1056",
                    "max_read_kbytes": "802",
                    "max_write_kbytes": "803",
                },
            "eth_port_types": {
                    "0": "host_port/service_port",
                    "2": "management_port",
                    "3": "inner_port",
                    "4": "maintenance_port",
                    "5": "management/service_port",
                    "6": "maintenance/service_port",
                },
             }


resources = [
                # This array is "TODO" list. Commented elements are still in TODO but not done because I don't have such instances in my device
                # 'expboard',
                # 'fc_port',
                ]
