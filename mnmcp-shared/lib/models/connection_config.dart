/// 游戏模式
enum GameMode { minecraft, miniworld }

/// 游戏类型
enum GameType { java, bedrock, cn, global }

/// 连接目标
enum TargetType { streamer, server, direct }

/// 连接配置 (三端共用)
class ConnectionConfig {
  final GameMode gameMode;
  final GameType gameType;
  final TargetType targetType;
  final String host;
  final int port;
  final bool usePenetration;
  final String? playerName;

  const ConnectionConfig({
    required this.gameMode,
    required this.gameType,
    required this.targetType,
    required this.host,
    required this.port,
    this.usePenetration = false,
    this.playerName,
  });

  Map<String, dynamic> toJson() => {
    'gameMode': gameMode.name,
    'gameType': gameType.name,
    'targetType': targetType.name,
    'host': host,
    'port': port,
    'playerName': playerName,
  };
}
