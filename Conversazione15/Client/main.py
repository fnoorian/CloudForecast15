import os
import socket
import time
import threading
import sys
import time
from enum import Enum
from collections import OrderedDict

import numpy
import pandas

from PyQt4 import QtGui, QtCore
from matplotlib.backends import qt_compat
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from market_dialog import Ui_Dialog
from r_rpc_client import ForecastRPCClient

MAX_FORECAST_PARTS = 5
DEMO_WAIT_ENDS = 20

class DemoState(Enum): # state of demo in the demo state machine
    stopped = 0
    start = 1
    select_next_algo = 2
    predict_next_part = 3
    finalize = 4
    wait = 5
    select_next_ts = 6

class MarketPlaceUI:
    def __init__(self):
        self.ui = None # the UI place uolder
        self.rpc = ForecastRPCClient("http://10.65.196.249:4001/jsonrpc")
        self.demo_state = DemoState.stopped
        self.demo_scores = dict()

    def plot_timeseries(self, main_ts, pred_ts = None):

        self.ui.figcav.figure.clf()

        self.ui.fig = main_ts.plot(grid=True, color="blue", label="Observations")
        self.ui.fig.figure.set_canvas(self.ui.figcav)

        if not pred_ts is None:
            self.ui.fcast_fig = pred_ts.plot(grid=True, color="red", label="Forecasts")
            self.ui.fig.figure.set_canvas(self.ui.figcav)

        #print()

        #self.ui.fig.figure.legend(self.ui.fig.get_legend_handles_labels(), ["blue"])
        self.ui.fig.figure.tight_layout()
        self.ui.figcav.draw()

    def on_selected_ts_changes(self):
        # get the selected time-series from list box
        current_item = self.ui.list_ts.currentItem()
        ts_item = current_item.data(QtCore.Qt.UserRole)

        self.demo_ts_name = ts_item["name"]

        # update ui
        self.ui.label_ts_description.setText("<B>Selected data:</B><BR>" + ts_item["description"])

        # get data from RPC and update figure
        self.demo_ts_data = self.rpc.get_ts(self.demo_ts_name)

        self.plot_timeseries(self.demo_ts_data)

        # start demo state machine
        self.demo_state = DemoState.start

    def on_selected_algo_changes(self):
        # get the selected time-series from list box
        current_item = self.ui.list_algos.currentItem()
        ts_item = current_item.data(QtCore.Qt.UserRole)

        # update ui
        self.ui.label_algo_description.setText("<B>Selected algorithm:</B><BR>" + ts_item["description"])

    def select_algo_in_list(self, algo_name):
        # select algorithm in the list widget
        for i, algo in enumerate(self.algo_names):
            if algo_name == algo:
                self.ui.list_algos.setCurrentRow(i)

    def setup_timer(self):
        self.ui.timer = QtCore.QTimer()
        self.ui.timer.timeout.connect(self.on_timer)
        self.ui.timer.start(500) # 2 Hz is the max for 4 plots

    def fill_scores_table(self, best_color):

        label_text = "<span style='font-size:16pt;'>" + \
                     "<table border='1' style='margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;' cellspacing='0' cellpadding='12'>\n"
        label_text += "<tr><td>Algorithm</td><td>RMSE</td><td>MAE</td></tr>\n"


        # find the minimum algo score, if we have any algorithm computed
        if len(self.demo_scores) > 0:
            min_algo_name = min(self.demo_scores.items(), key = lambda x: x[1]["rmse"])[0]

        for algo_name in self.algo_names:

            if algo_name in self.demo_scores:
                # if the algorithm is computed
                algo_score = self.demo_scores[algo_name]

                # check if the score is minimum
                if algo_name == min_algo_name:
                    # set minimum text color
                    label_text += "<tr><td><font color='{3}'>{0}</font></td><td><font color='{3}'>{1:.2f}</font></td><td><font color='{3}'>{2:.2f}</font></td></tr>\n".format(
                        algo_name, algo_score["rmse"], algo_score["mae"], best_color)
                else:
                    # ordinary text
                    label_text += "<tr><td>{0}</td><td>{1:.2f}</td><td>{2:.2f}</td></tr>\n".format(algo_name, algo_score["rmse"], algo_score["mae"])
            else:
                # algorithm is not computed, fill with dashes
                label_text += "<tr><td><font color='{3}'>{0}</font></td><td><font color='{3}'>{1}</font></td><td><font color='{3}'>{2}</font></td></tr>\n".format(
                        algo_name, "-", "-", "gray")

        label_text += "</table></span>"

        self.ui.lbl_scoretable.setText(label_text)

    def on_timer(self):
        print(self.demo_state)

        if self.demo_state == DemoState.start:

            self.demo_current_algo = -1
            self.demo_state = DemoState.select_next_algo

            # clear the score for this data
            self.demo_scores = dict()

        if self.demo_state == DemoState.select_next_algo:
            self.demo_current_algo += 1
            if self.demo_current_algo < len(self.algo_names):
                self.dem_current_algo_name = self.algo_names[self.demo_current_algo]
                self.select_algo_in_list(self.dem_current_algo_name)
                self.demo_state = DemoState.predict_next_part

                self.demo_current_part = 1

                # clear the score for this algo
                self.demo_rmse = 0
                self.demo_mae = 0
                self.demo_scores[self.dem_current_algo_name] = dict()

            else:
                self.demo_state = DemoState.finalize
            
        if self.demo_state == DemoState.predict_next_part:
            results = self.rpc.get_prediction_with_statistics(self.demo_ts_name, 
                                                              self.algo_names[self.demo_current_algo], 
                                                              self.demo_current_part, 
                                                              max_parts = MAX_FORECAST_PARTS)

            self.plot_timeseries(self.demo_ts_data, results["forecast"])

            # add up error 
            self.demo_rmse += results["rmse"]
            self.demo_mae += results["mae"]
            self.demo_scores[self.dem_current_algo_name]["rmse"] = self.demo_rmse
            self.demo_scores[self.dem_current_algo_name]["mae"] = self.demo_mae

            # fill table
            self.fill_scores_table("red")

            # go to next part
            self.demo_current_part += 1
            if self.demo_current_part > MAX_FORECAST_PARTS:
                self.demo_state = DemoState.select_next_algo

        if self.demo_state == DemoState.finalize:

            # find the algorithm with minimum RMSE error
            min_algo = min(self.demo_scores.items(), key = lambda x: x[1]["rmse"])[0]

            # select best forecast, update table and plot accordingly
            self.select_algo_in_list(min_algo)

            all_fcast = pandas.Series()
            for i in range(MAX_FORECAST_PARTS):
                fcast = self.rpc.get_prediction_for_part_n(self.demo_ts_name, 
                                                           min_algo, 
                                                           i + 1, 
                                                           max_parts = MAX_FORECAST_PARTS)
                all_fcast = pandas.concat([all_fcast, fcast])

            self.plot_timeseries(self.demo_ts_data, all_fcast)

            self.fill_scores_table("green")

            # get in to the wait state
            self.demo_wait_counter = 0
            self.demo_state = DemoState.wait

        if self.demo_state == DemoState.wait:
            self.demo_wait_counter += 1
            if self.demo_wait_counter == DEMO_WAIT_ENDS:
                self.demo_state = DemoState.select_next_ts
                
        
        if self.demo_state == DemoState.select_next_ts:
            next_row = self.ui.list_ts.currentRow() + 1
            if next_row > self.ui.list_ts.count():
                next_row = 0
                
            # this automatically changes the state to start
            self.ui.list_ts.setCurrentRow(next_row)
    
    def setup_graphics(self, app):

        # create main dialog and main window
        self.ui = Ui_Dialog()
        self.ui.main_window = QtGui.QDialog()

        # setup the window
        ui = self.ui
        main_window = ui.main_window
        ui.setupUi(main_window)

        # configure the main window to maximise and set its title
        main_window.setWindowFlags(QtCore.Qt.Window or QtCore.Qt.WindowMaximizeButtonHint) 
        main_window.setWindowTitle('Prediction Market Demo')

        # create a new PixelMap, loaded from the image
        pix = QtGui.QPixmap(os.getcwd() + "/images/usyd_logo.png")
        ui.lbl_Usyd_logo.setPixmap(pix)#.scaled(200, 70, aspectRatioMode = QtCore.Qt.KeepAspectRatio))

        pix = QtGui.QPixmap(os.getcwd() + "/images/algorithm3.png")
        ui.lbl_algo.setPixmap(pix)#.scaled(200, 70, aspectRatioMode = QtCore.Qt.KeepAspectRatio))

        pix = QtGui.QPixmap(os.getcwd() + "/images/user.png")
        ui.lbl_user.setPixmap(pix)#.scaled(200, 70, aspectRatioMode = QtCore.Qt.KeepAspectRatio))

        pix = QtGui.QPixmap(os.getcwd() + "/images/scale.png")
        ui.lbl_market.setPixmap(pix)#.scaled(200, 70, aspectRatioMode = QtCore.Qt.KeepAspectRatio))

        # fill the ts name box from the data
        self.ts_names = self.rpc.get_data_names()
        for ts_key in sorted(self.ts_names.keys()):
            ts_item = self.ts_names[ts_key]
            item = QtGui.QListWidgetItem(ts_item["name"])
            item.setData(QtCore.Qt.UserRole, ts_item)
            ui.list_ts.addItem(item)

        # also get algorithm names and fill the algo name box
        self.algo_collection = OrderedDict(self.rpc.get_algo_names())
        self.algo_names = sorted([algo["name"] for (key, algo) in self.algo_collection.items()])

        for algo_key in sorted(self.algo_collection.keys()):
            algo_item = self.algo_collection[algo_key]
            item = QtGui.QListWidgetItem(algo_item["name"])
            item.setData(QtCore.Qt.UserRole, algo_item)
            ui.list_algos.addItem(item)

        # add the listWidget select event
        ui.list_ts.itemSelectionChanged.connect(self.on_selected_ts_changes)
        ui.list_algos.itemSelectionChanged.connect(self.on_selected_algo_changes)

        # add a plot figure and its canvase
        ts = self.rpc.get_ts(ts_item["name"])

        ui.fig = ts.plot(grid=True)
        self.ui.fig.figure.set_facecolor("white")
        self.ui.fig.figure.tight_layout()
        ui.figcav = FigureCanvas(ui.fig.figure)
        ui.verticalLayout_3.addWidget(ui.figcav)

        # fill the table
        self.fill_scores_table("black")

        # start the timer
        self.setup_timer()

        print("Setup complete")

        # show the main window
        main_window.showFullScreen()
        main_window.show()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':

    main_gui = MarketPlaceUI()

    # execute the main application
    app = QtGui.QApplication([])

    main_gui.setup_graphics(app)

    sys.exit(app.exec_())

