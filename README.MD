
# 中文

## 依赖
- **mcdreforged** >= ***1.0.0***

## 功能
- 检查玩家是否在白名单内
- 支持启用/禁用白名单
- 支持启用/重载时检查所有玩家是否在白名单内

## 配置

### 安装
1. 将本插件放入**MCDR**目录下的`plugins`文件夹下
2. 运行一遍插件, 以获取`config/WhiteList.json`配置文件
3. 根据下文调整配置文件
4. 使用`!!MCDR plugin reloadall`重新加载本插件

### 配置文件 (config/WhiteList.json)
```javascript
{
    "enable_whitelist": true, // 是否启用白名单
    "messages": {
        "not_in_whitelist": "\u4f60\u4e0d\u5728\u767d\u540d\u5355\u5185" // 踢出未再白名单中的玩家时向他们提示此消息
    },
    "white_list": [], // 白名单列表
    "minimum_permission_level": { // 指令权限
        "help": 0,
        "list": 2,
        "add": 2,
        "remove": 2,
        "query": 1
    }
}
```

## 使用
### 指令

- `!!whl help` 显示帮助信息
- `!!whl list` 列出当前白名单列表内的所有玩家
- `!!whl add <player>` 将`<player>`添加到白名单内
- `!!whl remove <player>` 将`<player>`从白名单内移除
- `!!whl query <player>` 检测`<player>`是否在白名单内
- `!!whl enable [true|false]` 查询/设置白名单的启用情况
- `!!whl reload` 重新加载配置文件
- `!!whl save` 保存配置文件

# English
None
