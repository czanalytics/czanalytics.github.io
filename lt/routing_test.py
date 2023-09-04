import lane

#import pandas as pd
#import numpy as np

import net as nt
import routing as rt

print("Routing test")

r1, state1 = nt.net_test()

st1 = rt.policy(1, r1['order'], r1['picks'], r1['drops'], r1['agents']) # just r1 as input?

print(st1)
print(st1.describe());

sm1 = state1.copy()

print(sm1)

#st, sm = move(st1, sm1)
