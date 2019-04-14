# Trading Bot

Getting started
Make a Quandl account
Clone the repo and run

```bash
$ pip install zipline
$ QUANDL_API_KEY=<yourkey> zipline ingest -b quandl
$ zipline run -f dual_moving_average.py --start 2014-1-1 --end 2018-1-1 -o dma.pickle


```
*dma is the dataframe