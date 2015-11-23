import os

# These are to make it work on Windows
#os.environ["R_USER"]=r"e:\46\MarketPredictor\scripts\R_USER"
#os.environ["R_HOME"]=r"d:\Programs\Programming\R"

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

import rpy2.robjects as robjects

R = robjects.r

def R_forecast_setup():
    # "source" (import) the R files
    R_directory = os.getcwd() #+ "/scripts"
    R.source(R_directory + "/pred_market.R", chdir=True)

    # add the do_rpc
    R.RPC = R["do.rpc"]

def RPC_example():
    example_json = '{\n \"json_rpc\": \"2.0\",\n\"method\": \"get_prediction_for_part_n_as_vec\",\n\"params\": [\n \"austa\",\n\"arima\",\n     4,\n     5 \n],\n\"id\": null \n}'
    response = R.RPC(example_json)
    return response[0]

@Request.application
def application(request):
    result = R.RPC(request.data.decode('utf-8'))[0]
    return Response(result, mimetype='application/json')
   
if __name__ == '__main__':
    R_forecast_setup()
    #run_simple('localhost', 4001, application)
    run_simple('0.0.0.0', 4001, application)
