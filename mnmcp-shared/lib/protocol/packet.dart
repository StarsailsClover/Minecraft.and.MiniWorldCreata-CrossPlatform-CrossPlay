import 'dart:typed_data';

/// 统一数据包 (与 mnmcp-core 的 UnifiedPacket 对应)
enum PacketAction {
  playerMove,
  playerLook,
  blockPlace,
  blockBreak,
  chatMessage,
  playerJoin,
  playerLeave,
  entitySpawn,
  entityMove,
  entityRemove,
  heartbeat,
  login,
  disconnect,
}

class UnifiedPacket {
  final PacketAction action;
  final String source; // 'mc' | 'mnw'
  final double x, y, z;
  final double yaw, pitch;
  final int blockId;
  final String message;
  final String playerName;
  final Uint8List? rawData;
  final DateTime timestamp;

  UnifiedPacket({
    required this.action,
    this.source = '',
    this.x = 0, this.y = 0, this.z = 0,
    this.yaw = 0, this.pitch = 0,
    this.blockId = 0,
    this.message = '',
    this.playerName = '',
    this.rawData,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
}
