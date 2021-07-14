
import os
import json
import mcdreforged.api.all as MCDR

PLUGIN_METADATA = {
  'id': 'whitelist',
  'version': '1.0.1',
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
	'messages': {
		'not_in_whitelist': '你不在白名单内'
	},
	'white_list': [
	],
  # 0:guest 1:user 2:helper 3:admin
  'minimum_permission_level': {
    'help':   0,
    'list':   2,
    'add':    2,
    'remove': 2,
    'query':  1
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
============ {1} v{2} ============
'''.strip().format(Prefix, PLUGIN_METADATA['name'], PLUGIN_METADATA['version'])


def send_message(source: MCDR.CommandSource or None, *args, sep=' ', format_='[WHL] {msg}'):
  if source is None:
    return
  msg = format_.format(msg=sep.join(args))
  (source.get_server().say if source.is_player else source.reply)(msg)

######## COMMANDS ########

def command_help(source: MCDR.CommandSource):
  send_message(source, HelpMessage, format_="{msg}")

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

def command_query_player(source: MCDR.CommandSource, player: str):
	send_message(source, ('"{}"在白名单中' if player in config['white_list'] else '"{}"不在白名单中').format(player))

def command_query_enable(source: MCDR.CommandSource):
	send_message(source, '白名单当前已启用' if config['enable_whitelist'] else '白名单当前已禁用')

def command_set_enable(source: MCDR.CommandSource, val: bool):
	config['enable_whitelist'] = val
	send_message(source, '已启用白名单' if config['enable_whitelist'] else '已禁用白名单')

######## APIs ########

def on_load(server :MCDR.ServerInterface, prev_module):
  if prev_module is None:
    server.logger.info('WhiteList is on load')
  else:
    server.logger.info('WhiteList is on reload')

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

def on_player_joined(server: MCDR.ServerInterface, player: str, info: MCDR.Info):
	if config['enable_whitelist'] and player not in config['white_list']:
		server.execute('kick {player} {msg}'.format(player=player, msg=config['messages']['not_in_whitelist']))

def register_command(server: MCDR.ServerInterface):
  def get_literal_node(literal):
    lvl = config['minimum_permission_level'].get(literal, 0)
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
    then(get_literal_node('save').runs(lambda src: save_config(server, src)))
  )

def load_config(server: MCDR.ServerInterface, source: MCDR.CommandSource or None = None):
  global config
  try:
    config = {}
    with open(CONFIG_FILE) as file:
      js = json.load(file)
    for key in default_config.keys():
      config[key] = js[key]
    server.logger.info('Config file loaded')
    send_message(source, '配置文件加载成功')
  except:
    server.logger.info('Fail to read config file, using default value')
    send_message(source, '配置文件加载失败, 切换默认配置')
    config = default_config.copy()
    save_config(server)

def save_config(server: MCDR.ServerInterface, source: MCDR.CommandSource or None = None):
    with open(CONFIG_FILE, 'w') as file:
      json.dump(config, file, indent=4)
    server.logger.info('Config file saved')
    send_message(source, '配置文件保存成功')
