/// 玩家模型 (三端共用)
class Player {
  final String id;
  final String name;
  final String connectionId;
  final String platform; // 'miniworld' | 'minecraft'
  String? roomId;
  DateTime joinTime;
  DateTime? lastActivity;

  // 游戏状态
  Map<String, double> position;
  double health;
  double maxHealth;
  int gameMode; // 0=survival, 1=creative

  Player({
    required this.id,
    required this.name,
    required this.connectionId,
    required this.platform,
    this.roomId,
    DateTime? joinTime,
    this.position = const {'x': 0, 'y': 64, 'z': 0},
    this.health = 20,
    this.maxHealth = 20,
    this.gameMode = 0,
  }) : joinTime = joinTime ?? DateTime.now();

  void updateActivity() => lastActivity = DateTime.now();

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'platform': platform,
    'roomId': roomId,
    'position': position,
    'health': health,
    'joinTime': joinTime.toIso8601String(),
  };

  factory Player.fromJson(Map<String, dynamic> json) => Player(
    id: json['id'] ?? '',
    name: json['name'] ?? '',
    connectionId: json['connectionId'] ?? '',
    platform: json['platform'] ?? 'minecraft',
    roomId: json['roomId'],
  );
}
