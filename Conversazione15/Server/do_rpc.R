library("RJSONIO")

source("xts_tools.R")


#' Runs a function on given data
#' 
#' @param ts.data    The time-series data.
#' @param ts.format  The format of time-series data, can be xts, JSON, or csv.
#' @param func       The function to run of time-series.
#' @param ...        Other arguments to the \code{func}.
#' 
#' @return Results of calling \code{func(ts.data, ...)}

ts.wrapper = function(ts.data, ts.format = c("xts", "vec", "json", "csv"), func, ...) {
  ts.format <- match.arg(ts.format)
  
  # convert data to xts
  if (ts.format == "json") {
    ts.data = json.to.xts(ts.data)
  } else if (ts.format == "csv") {
    ts.data = csv.text.to.xts(ts.data) 
  } else if (ts.format == "vec") {
    ts.data = vec.to.xts(ts.data)
  }
  
  # run the function using given data and other arguements
  forecast.results = func(ts.data, ...)
  
  # convert data to requested format
  if (ts.format == "json") {
    forecast.results = xts.to.json(forecast.results)
  } else if (ts.format == "csv") {
    forecast.results = xts.to.csv.text(forecast.results) 
  } else if (ts.format == "vec") {
    forecast.results = xts.to.vec(forecast.results)
  }

  test_data_name
  return (forecast.results)
}


#' JSON RPC dispatcher
#' 
#' @param json_cmd   A character string containing JSON RPC command
#' 
#' @return Results of function call in JSON format
do.rpc <- function(json_cmd) {
  
  rpc <- try( fromJSON(json_cmd), silent = TRUE )
  
  rpc$params <- as.list( rpc$params)
  
  result <- try( do.call( rpc$method, rpc$params ), silent = TRUE )
  
  if("try-error" %in% class( result )) {
    #TODO JSON-RPC defines several erorrs (call not found, invalid params, and server error)
    #if a call exists but fails, I am sending a procedure not found - when really it was found
    #but had an internal error. the data contains the actual error from R
    rpc_result <- list(
      jsonrpc = "2.0",
      error = list( code = -32601, message = "Procedure not found.", data = as.character( result ) ),
      id = rpc$id
    )
  } else {
    #RPC call suceeded
    rpc_result <- list(
      jsonrpc = "2.0",
      result = result,
      id = rpc$id
    )
  }
  
  #return the JSON string
  ret <- toJSON( rpc_result )
  ret <- paste( ret, "\n", sep="" )
  return( ret )
}

do.rpc.test <- function() {
  
  rpc <-  toJSON(list(
    json_rpc = "2.0",
    method = "sin",
    params = list(1),
    id = NULL
  ))
  
  res = do.rpc(rpc)
  
  
  ts_string = '{"1991-07-01T00:00:00.000Z":3.526591,"1991-08-01T00:00:00.000Z":3.180891,"1991-09-01T00:00:00.000Z":3.252221,
"1991-10-01T00:00:00.000Z":3.611003,"1991-11-01T00:00:00.000Z":3.565869,"1991-12-01T00:00:00.000Z":4.306371}'
  
  printxxxts <- function(x) {a = vec.to.xts(x); print(a)}
  
  rpc <-  toJSON(list(
    json_rpc = "2.0",
    method = "printxxxts",
    params = list(fromJSON(ts_string)),
    id = NULL
  ))
  
  res = do.rpc(rpc)
}
