# net.py

import numpy as np

def routing_conf():
  """
  Configuration for a routing task.
  - Line per location.
  - Location defined by  (lat, lon) -location, list of cargo IDs, list of agent IDs, and optional name


  """
  order    = {'id':'231122-0', 'da':'23-11-22'}                              # required fields

  picks    = [(52.367600,	4.90410,  [1, 2, 3, 4, 5], [1],    'amsterdam'), # OPTIONAL PLACE NAME
              (52.090700,	5.12140,  [6, 7, 8],       [1],    'utrecht')]

  drops    = [(45.764000,	4.83570,  [1, 2, 3, 4],    [1, 2], 'lyon'),      # both agents serve this location
              (44.933400,	4.89240,  [5, 6],          [2],    'valence'),
              (43.296500,	5.36980,  [7, 8],          [2],    'marseille')] # lyon is close to valence

  agents   = [(52.367600,	4.90410,  6,               1,      'a1ams'),
              (45.764000,	4.83570,  3,               2,      'a2lyo')]     # carrier loc. and capacity

  return {'order':order, 'picks':picks, 'drops':drops, 'agents':agents}


def links(a, dd, dp):
  """
  Find routing network links between locations 1 and 2.
  Input a = (lat1, lon1, n1, a1, c1, p1, d1,
             lat2, lon2, n2, a2, c2, p2, d2)

  Picks (p1, p2) and drops (d1, d2) are vectors, as well as agents (a1, a2).
  """
  lat1 = a[0]; lon1 = a[1]; loc1 = a[2]
  lat2 = a[7]; lon2 = a[8]; loc2 = a[9]

  #print("lane", a)

  r = 0 # default
  try:
    r = nuts_intel(dd, dp, lat1, lon1, lat2, lon2) # the slow part
    #display(r)
  except:
    pass

  #p1 = np.array(a[4]).tolist() # ok

  a1 = np.array(a[3]);  c1 = a[4];  p1 = np.array(a[5]); d1 = np.array(a[6])
  a2 = np.array(a[10]); c2 = a[11]; p2 = np.array(a[12]); d2 = np.array(a[13])

  start_nuts = r.start_nuts.item()
  end_nuts = r.end_nuts.item()

  time_road  = r.time_road.item()

  #print(time_road)

  a = np.array([loc1, start_nuts, lat1, lon1, a1, p1, d1, loc2, end_nuts, lat2, lon2, a2, p2, d2, time_road], dtype=object)

  r = pd.DataFrame([a.tolist()])
  r.columns = ['loc1', 'start_nuts', 'lat1', 'lon1', 'a1', 'p1', 'd1', 'loc2', 'end_nuts', 'lat2', 'lon2', 'a2', 'p2', 'd2', 'time_road']

  return r


def build_network(picks, drops, agents):
  """
  Build network with all location pairs for cargo picks and drops.
   (lat, lon, n, a, c, p, d) notation means
   (latitude, longitude, name, agents, cargo [0/1], picks, drops)
  """
  pnodes = [(plat, plon, ploc,     ag, 1, pu, 0) for plat, plon, pu, ag, ploc in picks]         # (loc, [u1, u2, ..],            0)
  dnodes = [(dlat, dlon, dloc,     ag, 1, 0, du) for dlat, dlon, du, ag, dloc in drops]         # (loc,            0, [u1, u2, ..])
  anodes = [(alat, alon, aloc, np.nan, 0, 0,  0) for alat, alon,  u, ag, aloc in agents]        # (loc,           #u,            0)

  nodes = pnodes + dnodes + anodes

  # TODO: solve case where agent depo (drops=0, picks=0) overlaps with picks/drops > 0

  lane_matrix = [(lat1, lon1, n1, a1, c1, p1, d1, lat2, lon2, n2, a2, c2, p2, d2) for (lat1, lon1, n1, a1, c1, p1, d1) in nodes for (lat2, lon2, n2, a2, c2, p2, d2) in nodes if n1 != n2]
  print(lane_matrix) # all loc pairs

  n = [links(link, dd, dp) for link in lane_matrix] # line-by-line
  nn = pd.concat(n, ignore_index=True)

  return nn


def net_test():
  """
  Test routing conf and building network.
  """
  r1 = routing_conf()

  print("routing conf.:", r1)
  print("order:", r1['order'])
  print("picks:", r1['picks'])
  print("drops:", r1['drops'])
  print("agents:", r1['agents'])

  state1 = build_network(r1['picks'], r1['drops'], r1['agents']);
  return r1, state1

#net_test()

