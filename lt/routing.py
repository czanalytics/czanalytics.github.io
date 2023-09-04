"""
Finite-state machine, FSM, for routing,
where transportation agents move between network location nodes
and perform pick, drop actions for cargo.

Ref. https://en.wikipedia.org/wiki/Finite-state_machine
"""

def policy(id, order, picks, drops, agents):
  """
  Set routing policy for agents.

  {'order': {'id': '230824-0', 'da': '23-08-26'},
   'picks':  [(52.3676, 4.9041, [1, 2, 3, 4, 5],    [1], 'amsterdam'),
              (52.0907, 5.1214, [6, 7, 8],          [1], 'utrecht')],
   'drops':  [(45.7640, 4.8357, [1, 2, 3, 4],    [1, 2], 'lyon'),
              (44.9334, 4.8924, [5, 6],             [2], 'valence'),
              (43.2965, 5.3698, [7, 8],             [2], 'marseille')],
   'agents': [(52.3676, 4.9041, 6,                    1, 'a1ams'),
              (45.7640, 4.8357, 3,                    2, 'a2lyo')]}
   """
  ver = 'v230829'

  ags  =     [id for (lat, lon, u, id, name) in agents]  # agent id list [1, 2]
  us   =     [u  for (lat, lon, u, id, name) in agents]  # agent capacity list [6, 3]
  utot = sum([u  for (lat, lon, u, id, name) in agents]) # tot. capacity 9

  a1 = agents[:][0] # TODO loop over
  a2 = agents[:][1] #
  pol1 = 'policy1'
  pol2 = 'policy2'

  # a2[3] inital location, umax = a2[2]

  pu_ = [pu for (lat, lon, pu, a, name) in picks] #
  pu  = list_join(pu_)
  pus = pu.size

  du_ = [du for (lat, lon, du, a, name) in drops] #
  du  = list_join(du_)
  dus = du.size

  # agents configures  LOOP TBD
  ui = np.array([], dtype=object)

  cols =        ['id',    'order',        'da', 't', 'ag', 'name', 'act', 'u', 'ui', 'lct', 'lat', 'lon', 'pu', 'du', 'policy', 'umax', 'home', 'info']
  s1 = np.array( [id, order['id'], order['da'], 0.0,  a1[3] , a1[4],     0,  0,    ui, a1[4], a1[0], a1[1],  pus,  dus,    pol1,  a1[2],  a1[4], ver], dtype=object)
  s2 = np.array( [id, order['id'], order['da'], 0.0,  a2[3] , a2[4],     0,  0,    ui, a2[4], a2[0], a2[1],  pus,  dus,    pol2,  a2[2],  a2[4], ver], dtype=object)

  status = s1 # select agent
  #status = s2

  st = pd.DataFrame([status.tolist()]) # line per agent TBD
  st.columns = cols

  st['act'] = 'policy'

  #st['info'] = 'xxx'
  #print(st.to_dict('records'))

  return st


def move(st, net):
  """
  State machine action to move another network node.

  The next location is selected based on policy
  that considers current cargo, location rewards, penalty and owerall target.
  """
  s = st.tail(1).copy()
  loc = s.lct.item()
  #print('move loc', loc)

  sm1 = net[net.loc1 == loc].copy() # filter lanes leaving form the current loc

  # sm  = sm[sm.a2 = s. ] # further filter to lanes served by the agent

  display(s); display(sm)

  #sm['reward'] = sm['d2'] + sm['p2']
  #sm['penalty'] = sm['time_road']

  net = sm1.copy() # debug
  """
  sm = sm.sort_values(by=['reward'], ascending=False) # or distance, etc.
  #sm = sm.sort_values(by=['time_road']) # or distance, etc.
  #print("OPTIONS", sm)

  n = sm.head(1).copy() # n(ext)
  #print('n', n)
  #print('n.time_road', n.time_road.item())

  reward = s.du.item() + s.pu.item()
  #print(">>>>>>stop", reward)

  if reward > 0:
    s.t = s.t + n.time_road.item()
    #print('s.t', s.t)

    s.lct = n.loc2.item()
    s['act'] = 'move'
    s.lat = n.lat2.item()
    s.lon = n.lon2.item()

    st = pd.concat([st, s],  ignore_index=True)
  else:
    st, net = home(st, net)

  """
  return st, net


def drop(st, net):
  """
  State machine action to drop cargo.
  """
  s = st.tail(1).copy()
  loc = s.lct.item()
  #print('drop loc', loc)

  sm = net[(net.loc1 == loc)].copy()
  #print("NET", sm)

  #ud = sm.d1
  ud = sm.d1.iloc[0] # pick possible unit drops
  #print('possible drops', ud)

  u = s.u.item()
  #print('cargo units', u)
  #udrop = 0

  udrop = min(ud, u)  # based on availability, need
  #print('udrop', udrop)

  if udrop > 0:
    s.t = s.t + 0.1 * udrop
    s.u = u - udrop # update agent
    s.du = s.du - udrop
    #sm.d1 = m.d1.item() + udrop # update net
    s['act'] = 'drop'
    net.loc[net['loc1'] == loc, 'd1'] = ud - udrop
    net.loc[net['loc2'] == loc, 'd2'] = ud - udrop
    st = pd.concat([st, s],  ignore_index=True)

  return st, net


def pick(st, net):
  """
  State machine action to pick cargo.
  """
  s = st.tail(1).copy()
  #display(s)
  #print("state", s)

  loc = s.lct.item() # location
  #print('pic loc', loc)

  # filter all connected nodes from the master matrix
  sm = net[(net.loc1 == loc)].copy()

  sm = sm.sort_values(by=['time_road']) # or distance, etc.

  #display(sm)

  m = sm.head(1) # pick first

  up = sm.p1.iloc[0] # pick vector of picks
  #up = m.p1.item()
  #print("up:", up)

  up_len = len(up) # number of units to pick

  ui = s.ui.iloc[0]

  print('ui', ui)

  space = s.umax.item() - s.u.item()

  #print('space', space)
  print('pick option', up, 'length', up_len)

  upick = min(up_len, space)

  #print('upick', upick)

  # hungry-policy -- pick all you can
  # order policy -- pick first upick, TDD ordering

  if upick > 0:
    s.t = s.t + 0.1 * upick
    s.u = s.u + upick # update agent #units, u
    print('picking ui', up[0:upick])

    s.ui = s.ui
    ui_ = np.append(ui, up[0:upick])
    print('ui_', ui_)

    ar1 = np.array([1, 2, 3, 4],  dtype=object) # np.array objects
    ar2 = np.array([2, 3],        dtype=object)
    ar3 = np.array([5, 6],        dtype=object)

    a1 = np.setdiff1d(ar1, ar2, assume_unique=True) # [1 4]
    print("remove with diff\n:", a1)

    a2 = np.union1d(ar1, ar3)
    print("add with union\n:", a2)

    """
    s['ui'] = ui_ # ERR
    display(s)
    s.pu = s.pu - upick
    sm.p1 = up - upick
    net.loc[net['loc1'] == loc, 'p1'] = up - upick # update net
    net.loc[net['loc2'] == loc, 'p2'] = up - upick

    s['act'] = 'pick'
    st = pd.concat([st, s],  ignore_index=True) # concat instead deprecated append
    """

  return st, net


def home(st, net):
  """
  State machine action to go home after routing task is done.
  Routing is stopped when there is no cargo to be handled.
  """
  s = st.tail(1).copy()
  loc = s.lct.item()
  home = s.home.item()

  #print('move loc', loc)
  #print('home', home)

  if (loc == home):
    s.lct = home
  else:
    sm = net[net.loc1 == loc].copy()
    sm = sm[sm.loc2 == home].copy()

    #print("======", sm)

    n = sm.head(1).copy() # n(ext)

    #print("()()()()", n)

    s.t = s.t + n.time_road.item()

    #print('s.t', s.t)

    s.lct = n.loc2.item()
    s.lat = n.lat2.item()
    s.lon = n.lon2.item()


  s['act'] = 'home'
  st = pd.concat([st, s],  ignore_index=True)

  return st, net

def state_sync(st1, sm1, st2, sm2):
  """
  States syncronized between agents.
  """
  s1 = st1.tail(1).copy()
  s2 = st2.tail(1).copy()

  # share state > optimize

  s1['act'] = 'sync'
  st1 = pd.concat([st1, s1],  ignore_index=True)

  s2['act'] = 'sync'
  st2 = pd.concat([st2, s2],  ignore_index=True)

  return st1, sm1, st2, sm2


def state_update(st, sm):
  """
  State machine update with network state update.
  """

  st, sm = move(st, sm) # if reward

  #print(st); #print(sm)

  st, sm = drop(st, sm) # if target and units

  #print(st); #print(sm)

  st, sm = pick(st, sm) # if target and capacity

  return st, sm


def routing(order1, picks1, drops1, agents1, state1,
            order2, picks2, drops2, agents2, state2):
  """
  Main for routing between two orders, specified with (pick, drop) -networks.
  """
  n = 1
  while n <= 3:
    print("Routing", n)
    id=n

    st1 = policy(id, order1, picks1, drops1, agents1)
    sm1 = state1.copy()

    st2 = policy(id, order2, picks2, drops2, agents2)
    sm2 = state2.copy()

    #print(st1); print(sm1)

    st1, sm1 = pick(st1, sm1) # initial pick
    st2, sm2 = pick(st2, sm2) #

    i=1;

    # continue until home, orders delivered
    while (st1.tail(1).act.item() != 'home' and st2.tail(1).act.item() != 'home'):
      #print(i, "--------")

      st1, sm1, st2, sm2 = state_sync(st1, sm1, st2, sm2)

      st1, sm1 = state_update(st1, sm1)
      st2, sm2 = state_update(st2, sm2)

      i += 1

    vars = ['id', 'order', 'da', 't', 'agent', 'lct', 'u', 'du', 'pu', 'act', 'info']

    #print(st1)
    #display(st1[vars]) # Colab
    #display(st2[vars])

    n += 1

  return 0, 1
