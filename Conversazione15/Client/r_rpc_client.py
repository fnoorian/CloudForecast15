import requests
import json
import pandas

import sys
import pdb
import logging

def enable_stdout_logging():
    
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

class ForecastRPCClient:
    def __init__(self, url):
        self.url = url
        self.headers = {'content-type': 'application/json'}

    def _call(self, method, *kargs):
        # build payload
        payload = {
            "method": method,
            "params": list(kargs),
            "jsonrpc": "2.0",
            "id": 0,
        }

        logging.debug("URL: {0}".format(self.url))
        logging.debug("Payload: ")
        logging.debug(payload)

        # send response
        response = requests.post(self.url, data=json.dumps(payload), headers=self.headers,
                                 proxies={"http":""})

        logging.debug("Response: ")
        logging.debug(response.content)
        logging.debug(response.json())

        return response.json()["result"]

    def json_to_ts(self, x, typ='frame'):

        results = pandas.read_json(x, typ=typ)
        results.index = results.index.tz_localize('UTC').tz_convert('Australia/Sydney')

        return results

    def get_version(self):
        return self._call("forecast_market_get_version")

    def get_prediction_for_part_n(self, test_data_name, algorithm, part_to_forecast, max_parts):
        result = self._call("get_prediction_for_part_n_as_json",
            test_data_name, algorithm, part_to_forecast, max_parts)

        return self.json_to_ts(result, typ="series")

    def get_prediction_with_statistics(self, test_data_name, algorithm, part_to_forecast, max_parts):
        result = self._call("get_prediction_with_statistics",
            test_data_name, algorithm, part_to_forecast, max_parts)

        result["forecast"] = self.json_to_ts(result["forecast"], typ="series")
        result["observed"] = self.json_to_ts(result["observed"], typ="series")

        return result

    def get_ts(self, data_name):
        result = self._call("get_ts_as_json", data_name)

        return self.json_to_ts(result, typ="series")

    def get_data_names(self):
        return self._call("get_data_names")

    def get_algo_names(self):
        return self._call("get_algo_names")

#    def get_version(self):
#        return self._call("get_version", [])


def examples():

    rpc = ForecastRPCClient("http://127.0.0.1:4001/jsonrpc")
    print(rpc.get_version())

    ts = rpc.get_ts("austa")
    print(ts)
    
    pred = rpc.get_prediction_for_part_n("austa", "arima", 4, 5)
    print(pred)

#enable_stdout_logging()

if __name__ == "__main__":

    examples()
    
