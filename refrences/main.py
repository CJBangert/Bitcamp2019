import requests
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


