/// 玩家模型
class Player {
  final String id;
  final String name;
  final String connectionId;
  final String platform; // miniworld, minecraft
  String? roomId;
  
  DateTime joinTime;
  DateTime? lastActivity;
  
  Player({
    required this.id,
    required this.name,
    required this.connectionId,
    required this.platform,
    this.roomId,
    DateTime? joinTime,
  }) : joinTime = joinTime ?? DateTime.now();
  
  void updateActivity() {
    lastActivity = DateTime.now();
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'platform': platform,
      'roomId': roomId,
      'joinTime': joinTime.toIso8601String(),
    };
  }
}
