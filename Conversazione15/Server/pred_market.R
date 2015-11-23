library(diskmemoiser)

source("do_rpc.R")

forecast_market_get_version <- function() {
  return(1)
}

################################
# set time zone
library("timeDate")
Sys.setenv(TZ='Australia/Sydney')
setRmetricsOptions(myFinCenter="Australia/Sydney")


year_to_timedate <- function(x) trunc(as.timeDate(as.POSIXct(yearmon(x))))

window.ex <- function(x, start = NULL, end = NULL, ...) {
  window(x, start=index(x)[start], end=index(x)[end])
}

as.xts.ts <- function(x) {
  if ("numeric" %in% class(index(x))) {
    x = xts(as.numeric(x), year_to_timedate(index(x)))
  } else {
    x = as.xts(x)
  }
}

################################
library("fpp")

get_data_names <- function() {
  list(a10     = list(name = "a10", 
                      description = "Monthly anti-diabetic drug sales in Australia from 1992 to 2008"),
       ausair  = list(name = "ausair", 
                      description = "Air Transport Passengers Australia"),
       #ausbeer = list(name = "ausbeer", 
       #               description = "Quarterly Australian Beer production"),
       austa   = list(name = "austa",
                      description = "International vistors to Australia"),
       #departures = list(name = "departures",
       #                 description = "Total monthly departures from Australia"),
       elecequip  = list(name = "elecequip",
                      description = "Electrical equipment manufactured in the Euro area"),
       elecsales  = list(name = "elecsales",
                      description = "Electricity sales to residential customers in South Australia"),
       #vn         = list(name = "vn",
       #               description = "Quarterly visitor nights for various regions of Australia"),
       livestock  = list(name = "livestock",
                      description = "Livestock (sheep) in Asia, 1961-2007"))
}

get_ts <- function(dataname) {
  return (eval(parse(text=dataname)))
}

get_ts_as_json <- function(dataname) xts.to.json(as.xts.ts(get_ts(dataname)))

####
library("forecast")

get_algo_names <- function() {
  list(Theta = list(name = "Theta", 
                    description = "Theta method<BR>By Assimakopoulos and Nikolopoulos"),
       ARIMA = list(name = "ARIMA", 
                    description = "Autoregressive integrated moving average<BR>Script by R.J. Hyndman"),
       ETS   = list(name = "ETS", 
            description = "Exponentional smoothing<BR>Script by R.J. Hyndman"),
       BATS   = list(name = "BATS", 
            description = "BATS<BR>By De Livera, Hyndman and Snyder")
       #RWF    = list(name = "RWF",
           # description = "Random Walk Forecast")
           )
}

algo_dispatch <- function(algo, x, h) {
  algo = toupper(algo)
  
  if (algo == "THETA") {
    thetaf(x, h)$mean
  } else if (algo == "ARIMA") {
    mdl = auto.arima(x)
    forecast(mdl, h)$mean
  } else if (algo == "ETS") {
    mdl = ets(x)
    forecast(mdl, h)$mean
  } else if (algo == "BATS") {
    mdl = bats(x)
    forecast(mdl, h)$mean
  } else if (algo == "RWF") {
    rwf(x, h)$mean
  }
}

get_prediction_for_part_n <- function(test_data_name, algorithm, part_to_forecast, max_parts) {
  
  # load the data
  dt = get_ts(test_data_name)
  
  # separate the training and testing parts
  total_len = length(dt)
  train_end = round(total_len/2)
  test_steps = round(total_len/(2*max_parts))
  
  part_head = (part_to_forecast - 1) * test_steps
  part_end = part_head + test_steps

  train_data = window.ex(dt, 1, train_end + part_head - 1)
  test_data = window.ex(dt, train_end + part_head, min(train_end + part_end, total_len))
  
  # call the forecasting function
  if (algorithm == "prescient") {
    fcast = test_data
  } else {
    fcast = algo_dispatch(algorithm, train_data, test_steps)
  }
  

  # convert to xts
  fcast = as.xts.ts(fcast)
  
  # return the forecast
  return(fcast)
}

get_prediction_for_part_n.m = diskMemoiser(get_prediction_for_part_n, use.func.contents = TRUE, compare.args.as.characters = FALSE)

get_prediction_for_part_n_as_vec <- function(...) xts.to.vec(get_prediction_for_part_n.m(...))

get_prediction_for_part_n_as_json <- function(...) xts.to.json(get_prediction_for_part_n.m(...))

get_prediction.json.test <- function() {
  x = get_prediction_for_part_n("austa", "arima", 4, 5)
  
  y = fromJSON(do.rpc(toJSON(list(json_rpc = "2.0",
                                  method = "get_prediction_for_part_n_as_vec",
                                  params = list("austa", "arima", 4, 5),
                                  id = NULL))))
  x2 = vec.to.xts(y$result)
  
  stopifnot(sum(abs(x-x2)) < 1e-4)
}

########################################################################
RMSE <- function(x,y) sqrt(mean((x-y)^2))
MAE <- function(x,y) (mean(abs(x-y)))

get_prediction_with_statistics <- function(test_data_name, algorithm, part_to_forecast, max_parts) {
  fcast = get_prediction_for_part_n.m(test_data_name, algorithm, part_to_forecast, max_parts)
  observed = get_prediction_for_part_n.m(test_data_name, "prescient", part_to_forecast, max_parts)
  
  return (list(forecast = xts.to.json(fcast),
               observed = xts.to.json(observed),
               rmse = RMSE(fcast, observed),
               mae = MAE(fcast, observed)))
}
