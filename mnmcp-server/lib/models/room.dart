import 'player.dart';

/// 房间模型
class Room {
  final String id;
  final String name;
  final String hostId;
  final String gameMode; // miniworld, minecraft
  final int maxPlayers;
  final bool isPersistent;
  
  final List<Player> players = [];
  DateTime createdAt;
  
  Room({
    required this.id,
    required this.name,
    required this.hostId,
    required this.gameMode,
    required this.maxPlayers,
    this.isPersistent = false,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();
  
  void addPlayer(Player player) {
    if (!players.contains(player)) {
      players.add(player);
    }
  }
  
  void removePlayer(Player player) {
    players.remove(player);
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'gameMode': gameMode,
      'players': players.length,
      'maxPlayers': maxPlayers,
      'createdAt': createdAt.toIso8601String(),
    };
  }
}
