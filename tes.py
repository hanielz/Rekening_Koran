from datetime import date
from datetime import timedelta

# Get today's date
date='20220824'


# Yesterday date
yesterday = today - timedelta(days = 1)
print("Yesterday was: ", yesterday)
