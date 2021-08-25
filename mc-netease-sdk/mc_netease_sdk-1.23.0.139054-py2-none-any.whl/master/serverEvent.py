# -*- coding: utf-8 -*-

"""
事件的定义。
"""

class ServerEvent:
		"""
		公共配置发生变化时触发，具体包括：新增或删服服务器；服务器相关配置变化；日志等级发生变化

		"""
		NetGameCommonConfChangeEvent = "NetGameCommonConfChangeEvent"

		"""
		玩家开始登陆事件，此时master开始给玩家分配lobby/game，可以区分玩家是登录还是切服

		Event Function Args:
			serverId       int            客户端连接的proxy服务器id
			uid            int            玩家的uid
			protocolVersionint            协议版本号
			isTransfer     bool           True: 切服，False：登录

		"""
		PlayerLoginServerEvent = "PlayerLoginServerEvent"

		"""
		玩家登出时触发，玩家在lobby/game下载行为包的过程中退出也会触发该事件，可以以区分玩家是登出还是切服

		Event Function Args:
			serverId       int            客户端连接的proxy服务器id
			uid            int            玩家的uid
			isTransfer     bool           True: 切服，False：登出

		"""
		PlayerLogoutServerEvent = "PlayerLogoutServerEvent"

		"""
		玩家开始切服事件，此时master开始为玩家准备服务器，玩家还没切服完毕，后续可能切服失败

		Event Function Args:
			serverId       int            客户端连接的proxy服务器id
			uid            int            玩家的uid
			targetServerId int            目标lobby/game服务器id
			targetServerTypestr            目标服务器类型，比如"game"或"lobby"。若targetServerId为0，则会从目标类型的多个服务器中随机选一个，作为目标服务器
			protocolVersionint            协议版本号
			transferParam  str            切服参数。调用【TransferToOtherServer】或【TransferToOtherServerById】传入的切服参数。

		"""
		PlayerTransferServerEvent = "PlayerTransferServerEvent"

		"""
		开始重置lobby/game事件。具体可以参见API【ResetServer】

		Event Function Args:
			serverId       int            服务器id

		"""
		ResetGamesBeginEvent = "ResetGamesBeginEvent"

		"""
		重置lobby/game结束事件。本事件只是表示重置完成了，但是服务器可能还未完成初始化。具体可以参见API【ResetServer】

		Event Function Args:
			serverId       int            服务器id
			bSuccess       bool           重置是否成功。true表示重置成功，否则表示失败

		"""
		ResetGamesEndEvent = "ResetGamesEndEvent"

		"""
		lobby/game/proxy成功建立连接时触发

		Event Function Args:
			serverId       int            服务器id
			protocolVersionint            协议版本号

		"""
		ServerConnectedEvent = "ServerConnectedEvent"

		"""
		lobby/game/proxy断开连接时触发

		Event Function Args:
			serverId       int            服务器id

		"""
		ServerDisconnectEvent = "ServerDisconnectEvent"

