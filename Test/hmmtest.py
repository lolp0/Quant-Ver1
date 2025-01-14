from __future__ import print_function

import datetime
import numpy as np
import pylab as pl
import pandas as pd
from hmmlearn.hmm import GaussianHMM
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from pandas.core.frame import DataFrame

print(__doc__)

###############################################################################
# Downloading the data
df =pd.read_csv('/home/peng/workspace/datafortrainCao.csv',header=None)

dates = np.array(df[0])
close_v = np.array(df[2])
volume1 = np.array(df[3])[1:]
label= np.array(df[4])


# take diff of close value
# this makes len(diff) = len(close_t) - 1
# therefore, others quantity also need to be shifted
diff = close_v[1:] - close_v[:-1]
dates = dates[1:]
close_v = close_v[1:]

# pack diff and volume1 for training
X = np.column_stack([volume1])

  ###############################################################################
# Run Gaussian HMM
print("fitting to HMM and decoding ...", end='')

# make an HMM instance and execute fit
model = GaussianHMM(n_components=3, covariance_type="full", n_iter=100).fit(X)

# predict the optimal sequence of internal hidden state
hidden_states = model.predict(X)

print("done\n")

  ###############################################################################
# print trained parameters and plot
print("Transition matrix")
print(model.transmat_)
print()

print("means and vars of each hidden state")
for i in range(model.n_components):
    print("%dth hidden state" % i)
    print("mean = ", model.means_[i])
    print("var = ", np.diag(model.covars_[i]))
    print()

years = YearLocator()   # every year
months = MonthLocator()  # every month
yearsFmt = DateFormatter('%Y')
fig = pl.figure()
ax = fig.add_subplot(111)
for i in range(model.n_components):
    # use fancy indexing to plot data in each state
    idx = (hidden_states == i)
    ax.plot_date(dates[idx], close_v[idx], 'o', label="%dth hidden state" % i)
ax.legend()
# format the ticks
#--------------------------------------------- ax.xaxis.set_major_locator(years)
#---------------------------------------- ax.xaxis.set_major_formatter(yearsFmt)
#-------------------------------------------- ax.xaxis.set_minor_locator(months)
ax.autoscale_view()
# format the coords message box
ax.fmt_xdata = DateFormatter('%Y-%m-%d')
ax.fmt_ydata = lambda x: '$%1.2f' % x
ax.grid(True)
fig.autofmt_xdate()
pl.show()