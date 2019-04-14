#!/usr/bin/env python
# coding: utf-8

# # How To Run Automated Backtests in Research
# ## Step 1: Import zipline libraries
# Research uses the zipline libraries instead of the default Quantopian ones. 
# You must switch all your 'from quantopian' imports to 'from zipline', 'from zipline.api', etc. to run your code  

# In[4]:


import zipline
from zipline.api import order_target_percent
import pytz
from datetime import datetime
import matplotlib.pyplot as pyplot
from collections import defaultdict
from datetime import datetime

from zipline import TradingAlgorithm
from zipline.api import order_target, record, symbol, history
import numpy as np
import pandas as pd
from zipline.api import order, sid


# In[3]:




# ## Step 2: Determine Variables
# Determine which variables are going to change from iteration to iteration. Put these variables in a global setting, when create new context variables that assign to these global variables.  

# In[13]:


#: NOTICE HOW THIS IS OUTSIDE INITIALIZE, BECAUSE IT IS, WE CAN REDEFINE IT EVERYTIME WE REDINE INITIALIZE
short_mavg_days = 20
long_mavg_days = 50
# dtafrm = None
def initialize(context):
    context.aapl = 24
    context.spy = 8554
    
    # Set context parameters based on global parameters 
    context.short_mavg_days = short_mavg_days
    context.long_mavg_days = long_mavg_days

    # Used to warm-up moving averages
    context.i = 0


# ## Step 3: Creating handle_data
# Perhaps the biggest change from the Quantopian IDE to using research books is the shift from pipelines to using the handle_data(context, data) function. This function takes in all historical data such that back-testing can take place.

# In[14]:


def handle_data(context, data):
    
    # Skip days to get full windows
    context.i += 1
    if context.i < context.long_mavg_days:
        return
    
    sym = [sid(context.aapl)]
    
    # Compute averages
    # history() has to be called with the same params
    # from above and returns a pandas dataframe.
    short_mavg = data.history(sym, bar_count=context.short_mavg_days, frequency='1d', fields='price').mean()
    long_mavg = data.history(sym, bar_count=context.long_mavg_days, frequency='1d', fields='price').mean()

    

    # Trading logic
    if short_mavg[context.aapl] > long_mavg[context.aapl]:
        # order_target orders as many shares as needed to
        # achieve the desired number of shares.
        order_target_percent(sid(context.aapl), 1)
    elif short_mavg[context.aapl] < long_mavg[context.aapl]:
        order_target_percent(sid(context.aapl), 0)


# ## Step 4: Gathering the Stock Data
# Because we no longer have access to pipelines, we must find all the stock data beforehand and save it to a variable

# In[15]:
# def get_pricing (symbols, start_date, end_date, freq):
#     FMT = '%Y-%M-%d'
#     bars = datetime.strptime(end_date, FMT) - datetime.strptime(start_date, FMT)
#     return data.history(symbols, bar_count = bars, frequency =freq)


data = get_pricing(
    ['AAPL','SPY'],
    start_date='2014-01-01',
    end_date = '2015-02-15',
    freq = '1d'
)


# ## Step 5: Create the TradingAlgorithm object

# In[16]:


algo_obj = TradingAlgorithm(
    initialize=initialize, 
    handle_data=handle_data
)


# ## Step 6: Run and Calculate Metrics
# All trading metrics (such as the Sharpe ratio) will have to be calculated manually.

# In[17]:


#: Run the backtest and save the result.
perf_manual = algo_obj.run(data.transpose(2,1,0))

#: Get the sharpe ratio
sharpe = (perf_manual.returns.mean()*252)/(perf_manual.returns.std() * np.sqrt(252))
print "The Sharpe ratio is %0.6f" % sharpe


# ## Step 7: Iteration
# Turn steps 5 and 6 into a loop. Cut-paste the "initialize" function into the loop and set the context variables to a different value on each iteration. Store the results.

# In[18]:


# This will create a list with 9 entries
short_mavg_days = [days for days in np.arange(5, 40, 5)]
# This will create a list with 40 entries
long_mavg_days = [days for days in np.arange(10, 50, 5)]

#: Create a dictionary to hold all the results of our algorithm run
all_sharpes = defaultdict(dict)

# Count the number of backtests run
backtest_count = 0

# This will loop and run 324 backtests
# Each backtest takes about 3 seconds, so this will take around 16 minutes
for short_mavg_day in short_mavg_days:
    for long_mavg_day in long_mavg_days:
        # Only consider cases where the short is less than long.. but why this not working?
        if short_mavg_day < long_mavg_day:
            
            #: Redefine initialize with new weights
            def initialize(context):
                context.aapl = 24
    
                # Set context parameters based on global parameters 
                context.short_mavg_days = short_mavg_day
                context.long_mavg_days = long_mavg_day

                # Used to warm-up moving averages
                context.i = 0  
      
            algo_obj = TradingAlgorithm(
                initialize=initialize, 
                handle_data=handle_data
            )
            perf_manual = algo_obj.run(data.transpose(2,1,0))
            
            # Keep track of how many backtests were run
            backtest_count += 1
            print("Backtest {0} completed...").format(backtest_count)
            
            # Calculate the sharpe for this backtest
            sharpe = (perf_manual.returns.mean()*252)/(perf_manual.returns.std() * np.sqrt(252))
        
            #: Add the result to our dict
            all_sharpes[short_mavg_day][long_mavg_day] = sharpe

print " "
print "All backtest simulations completed!"
print " "


# ## Step 8: Aggregation
# Display the results in a readable and easy-to-consume manner

# In[19]:


all_sharpes = pd.DataFrame(all_sharpes)
all_sharpes.index.name = "Long Moving Average Days"
all_sharpes.columns.name = "Short Moving Average Days"

all_sharpes


# In[20]:


import matplotlib.pyplot as pyplot

def heat_map(df):
    """
    This creates our heatmap using our sharpe ratio dataframe
    """
    fig = pyplot.figure()
    ax = fig.add_subplot(111)
    axim = ax.imshow(df.values,cmap = pyplot.get_cmap('RdYlGn'), interpolation = 'nearest')
    ax.set_xlabel(df.columns.name)
    ax.set_xticks(np.arange(len(df.columns)))
    ax.set_xticklabels(list(df.columns))
    ax.set_ylabel(df.index.name)
    ax.set_yticks(np.arange(len(df.index)))
    ax.set_yticklabels(list(df.index))
    ax.set_title("Sharpe Ratios")
    pyplot.colorbar(axim)
    
#: Plot our heatmap
heat_map(all_sharpes)


# In[ ]:




