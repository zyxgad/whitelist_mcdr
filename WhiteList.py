
import os
import re
import json
import mcdreforged.api.all as MCDR

PLUGIN_METADATA = {
  'id': 'whitelist',
  'version': '1.0.3',
  'name': 'WhiteList',
  'description': 'Minecraft WhiteList Plugin',
  'author': 'zyxgad',
  'link': 'https://github.com/zyxgad/whitelist_mcdr',
  'dependencies': {
    'mcdreforged': '>=1.0.0'
  }
}

default_config = {
  'enable_whitelist': True,
  'enable_blacklist': True,
  'messages': {
    'not_in_whitelist': '你不在白名单内',
    'in_blacklist': '你在黑名单内'
  },
  'white_list': [
  ],
  'black_list': [
  ],
  # 0:guest 1:user 2:helper 3:admin
  'minimum_permission_level': {
    'help':   0,
    'list':   2,
    'add':    2,
    'remove': 2,
    'query':  1,
    'enable': 2,
    'reload': 2,
    'save':   2,
    'bk':     0
  },
  'black_minimum_permission_level': {
    'help':   0,
    'list':   2,
    'add':    2,
    'remove': 2,
    'query':  1,
    'enable': 2
  }
}
config = default_config.copy()
CONFIG_FILE = os.path.join('config', 'WhiteList.json')
Prefix = '!!whl'
HelpMessage = '''
------------ {1} v{2} ------------
{0} help 显示帮助信息
{0} list 列出当前白名单列表内的所有玩家
{0} add <player> 将<player>添加到白名单内
{0} remove <player> 将<player>从白名单内移除
{0} query <player> 检测<player>是否在白名单内
{0} enable [true|false] 查询/设置白名单的启用情况
{0} reload 重新加载配置文件
{0} save 保存配置文件
{0} bk [...] 黑名单指令
============ {1} v{2} ============
'''.strip().format(Prefix, PLUGIN_METADATA['name'], PLUGIN_METADATA['version'])
HelpMessageBlack = '''
------------ {1} v{2} ------------
{0} bk help 显示帮助信息
{0} bk list 列出当前黑名单列表内的所有玩家
{0} bk add <player> 将<player>添加到黑名单内
{0} bk remove <player> 将<player>从黑名单内移除
{0} bk query <player> 检测<player>是否在黑名单内
{0} bk enable [true|false] 查询/设置黑名单的启用情况
============ {1} v{2} ============
'''.strip().format(Prefix, PLUGIN_METADATA['name'], PLUGIN_METADATA['version'])

PLAYER_LOGGED_RE = re.compile(r'^([0-9a-zA-Z_-]+)\[/(\S+):(\d+)\] logged in')
PLAYER_LIST_RE = re.compile(r'^There are (\d+) of a max of (\d+) players online: ((?:[0-9A-Za-z_-]+,\s*)*[0-9A-Za-z_-]+)')

listed = False

def send_message(source: MCDR.CommandSource or None, *args, sep=' ', prefix='[WHL] '):
  if source is None:
    return
  (source.get_server().say if source.is_player else source.reply)\
    (MCDR.RTextList(prefix, args[0], *([MCDR.RTextList(sep, a) for a in args][1:])))

def flush_game_players(server: MCDR.ServerInterface):
  global listed
  if server.is_server_startup():
    listed = True
    server.execute('list')

######## COMMANDS ########

def command_help(source: MCDR.CommandSource):
  send_message(source, HelpMessage, prefix='')

def command_list_whitelist(source: MCDR.CommandSource):
  send_message(source, '当前白名单列表: [{}]'.format(', '.join(config['white_list'])))

def command_add_player(source: MCDR.CommandSource, player: str):
  if player in config['white_list']:
    send_message(source, '"{}"已经在白名单内了'.format(player))
    return
  config['white_list'].append(player)
  source.get_server().logger.info('[WHL] added "{}" to whitelist'.format(player))
  send_message(source, '已将"{}"添加到白名单'.format(player))

def command_remove_player(source: MCDR.CommandSource, player: str):
  if player not in config['white_list']:
    send_message(source, '"{}"不在白名单内'.format(player))
    return
  config['white_list'].remove(player)
  source.get_server().logger.info('[WHL] removed "{}" from whitelist'.format(player))
  send_message(source, '已将"{}"移出白名单'.format(player))
  flush_game_players(source.get_server())

def command_query_player(source: MCDR.CommandSource, player: str):
  send_message(source, ('"{}"在白名单中' if player in config['white_list'] else '"{}"不在白名单中').format(player))

def command_query_enable(source: MCDR.CommandSource):
  send_message(source, '白名单当前已启用' if config['enable_whitelist'] else '白名单当前已禁用')

def command_set_enable(source: MCDR.CommandSource, val: bool):
  config['enable_whitelist'] = val
  send_message(source, '已启用白名单' if config['enable_whitelist'] else '已禁用白名单')
  flush_game_players(source.get_server())

def command_black_help(source: MCDR.CommandSource):
  send_message(source, HelpMessageBlack, prefix='')

def command_list_blacklist(source: MCDR.CommandSource):
  send_message(source, '当前黑名单列表: [{}]'.format(', '.join(config['black_list'])))

def command_black_add_player(source: MCDR.CommandSource, player: str):
  if player in config['black_list']:
    send_message(source, '"{}"已经在黑名单内了'.format(player))
    return
  config['black_list'].append(player)
  source.get_server().logger.info('[WHL] added "{}" to blacklist'.format(player))
  send_message(source, '已将"{}"添加到黑名单'.format(player))
  flush_game_players(source.get_server())

def command_black_remove_player(source: MCDR.CommandSource, player: str):
  if player not in config['black_list']:
    send_message(source, '"{}"不在黑名单内'.format(player))
    return
  config['black_list'].remove(player)
  source.get_server().logger.info('[WHL] removed "{}" from blacklist'.format(player))
  send_message(source, '已将"{}"移出黑名单'.format(player))

def command_black_query_player(source: MCDR.CommandSource, player: str):
  send_message(source, ('"{}"在黑名单中' if player in config['black_list'] else '"{}"不在黑名单中').format(player))

def command_black_query_enable(source: MCDR.CommandSource):
  send_message(source, '黑名单当前已启用' if config['enable_blacklist'] else '黑名单当前已禁用')

def command_black_set_enable(source: MCDR.CommandSource, val: bool):
  config['enable_blacklist'] = val
  send_message(source, '已启用黑名单' if config['enable_blacklist'] else '已禁用黑名单')
  flush_game_players(source.get_server())

######## APIs ########

def on_load(server :MCDR.ServerInterface, prev_module):
  if prev_module is None:
    server.logger.info('WhiteList is on load')
  else:
    server.logger.info('WhiteList is on reload')
  
  flush_game_players(server)
  load_config(server)
  register_command(server)

def on_unload(server: MCDR.ServerInterface):
  server.logger.info('WhiteList is on unload')

def on_remove(server: MCDR.ServerInterface):
  server.logger.info('WhiteList is on disable')
  save_config(server)

def on_server_stop(server: MCDR.ServerInterface, server_return_code: int):
  server.logger.info('[WHL] Server is on stop, saving config now...')
  save_config(server)

def on_info(server: MCDR.ServerInterface, info: MCDR.Info):
  if info.is_user:
    return
  try_player_logged_info(server, info)
  try_player_list_info(server, info)

def try_player_logged_info(server: MCDR.ServerInterface, info: MCDR.Info):
  match = PLAYER_LOGGED_RE.match(info.content)
  if match is None:
    return
  player = match.group(1)
  connip = match.group(2)
  if config['enable_whitelist'] and player not in config['white_list']:
    server.execute('kick {player} {msg}'.format(player=player, msg=config['messages']['not_in_whitelist']))
  elif config['enable_blacklist'] and player in config['black_list']:
    server.execute('kick {player} {msg}'.format(player=player, msg=config['messages']['in_blacklist']))

def try_player_list_info(server: MCDR.ServerInterface, info: MCDR.Info):
  global listed
  if not listed:
    return
  listed = False
  match = PLAYER_LIST_RE.match(info.content)
  if match is None:
    return
  count = int(match.group(1))
  if count == 0:
    return
  players_str = match.group(3)
  players = re.split(r',\s*', players_str)
  for p in players:
    if config['enable_whitelist'] and p not in config['white_list']:
      server.execute('kick {player} {msg}'.format(player=p, msg=config['messages']['not_in_whitelist']))
    elif config['enable_blacklist'] and p in config['black_list']:
      server.execute('kick {player} {msg}'.format(player=p, msg=config['messages']['in_blacklist']))

def register_command(server: MCDR.ServerInterface):
  def get_literal_node(literal):
    lvl = config['minimum_permission_level'].get(literal, 0)
    return MCDR.Literal(literal).requires(lambda src: src.has_permission(lvl), lambda: '权限不足')
  def get_literal_node_black(literal):
    lvl = config['black_minimum_permission_level'].get(literal, 0)
    return MCDR.Literal(literal).requires(lambda src: src.has_permission(lvl), lambda: '权限不足')
  server.register_command(
    get_literal_node(Prefix).
    runs(command_help).
    then(get_literal_node('help').runs(command_help)).
    then(get_literal_node('list').runs(command_list_whitelist)).
    then(get_literal_node('add').
      then(MCDR.Text('name').runs(lambda src, ctx: command_add_player(src, ctx['name'])))).
    then(get_literal_node('remove').
      then(MCDR.Text('name').runs(lambda src, ctx: command_remove_player(src, ctx['name'])))).
    then(get_literal_node('query').
      then(MCDR.Text('name').runs(lambda src, ctx: command_query_player(src, ctx['name'])))).
    then(get_literal_node('enable').
      runs(command_query_enable).
      then(MCDR.Literal('true').runs(lambda src: command_set_enable(src, True))).
      then(MCDR.Literal('false').runs(lambda src: command_set_enable(src, False)))).
    then(get_literal_node('reload').runs(lambda src: load_config(server, src))).
    then(get_literal_node('save').runs(lambda src: save_config(server, src))).
    then(get_literal_node('bk').
      runs(command_black_help).
      then(get_literal_node_black('help').runs(command_black_help)).
      then(get_literal_node_black('list').runs(command_list_blacklist)).
      then(get_literal_node_black('add').
        then(MCDR.Text('name').runs(lambda src, ctx: command_black_add_player(src, ctx['name'])))).
      then(get_literal_node_black('remove').
        then(MCDR.Text('name').runs(lambda src, ctx: command_black_remove_player(src, ctx['name'])))).
      then(get_literal_node_black('query').
        then(MCDR.Text('name').runs(lambda src, ctx: command_black_query_player(src, ctx['name'])))).
      then(get_literal_node_black('enable').
        runs(command_black_query_enable).
        then(MCDR.Literal('true').runs(lambda src: command_black_set_enable(src, True))).
        then(MCDR.Literal('false').runs(lambda src: command_black_set_enable(src, False)))))
  )

def load_config(server: MCDR.ServerInterface, source: MCDR.CommandSource or None = None):
  global config
  try:
    config = {}
    with open(CONFIG_FILE) as file:
      js = json.load(file)
    for key in default_config.keys():
      config[key] = (js if key in js else default_config)[key]
    server.logger.info('Config file loaded')
    send_message(source, '配置文件加载成功')
  except:
    server.logger.info('Fail to read config file, using default value')
    send_message(source, '配置文件加载失败, 切换默认配置')
    config = default_config.copy()
    save_config(server)
  flush_game_players(server)

def save_config(server: MCDR.ServerInterface, source: MCDR.CommandSource or None = None):
    with open(CONFIG_FILE, 'w') as file:
      json.dump(config, file, indent=4)
    server.logger.info('Config file saved')
    send_message(source, '配置文件保存成功')
