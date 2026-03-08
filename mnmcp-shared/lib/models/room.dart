import 'player.dart';

/// 房间模型 (三端共用)
class Room {
  final String id;
  final String name;
  final String hostId;
  final String gameMode;
  final int maxPlayers;
  final bool isPersistent;
  final List<Player> players = [];
  DateTime createdAt;

  Room({
    required this.id,
    required this.name,
    required this.hostId,
    required this.gameMode,
    this.maxPlayers = 40,
    this.isPersistent = false,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  bool get isFull => players.length >= maxPlayers;

  void addPlayer(Player player) {
    if (!players.any((p) => p.id == player.id)) {
      players.add(player);
    }
  }

  void removePlayer(String playerId) {
    players.removeWhere((p) => p.id == playerId);
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'gameMode': gameMode,
    'players': players.length,
    'maxPlayers': maxPlayers,
    'createdAt': createdAt.toIso8601String(),
  };
}
