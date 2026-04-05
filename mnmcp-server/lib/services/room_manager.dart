import 'package:flutter/foundation.dart';

import '../models/room.dart';
import '../models/player.dart';

/// 房间管理器
class RoomManager extends ChangeNotifier {
  final Map<String, Room> _rooms = {};
  
  List<Room> get rooms => List.unmodifiable(_rooms.values);
  int get roomCount => _rooms.length;
  
  /// 创建房间
  Room createRoom({
    required String name,
    required String hostId,
    required String gameMode,
    int maxPlayers = 40,
  }) {
    final room = Room(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      name: name,
      hostId: hostId,
      gameMode: gameMode,
      maxPlayers: maxPlayers,
    );
    
    _rooms[room.id] = room;
    notifyListeners();
    return room;
  }
  
  /// 删除房间
  void deleteRoom(String roomId) {
    _rooms.remove(roomId);
    notifyListeners();
  }
  
  /// 获取房间
  Room? getRoom(String roomId) {
    return _rooms[roomId];
  }
  
  /// 获取可加入的房间列表
  List<Room> getAvailableRooms() {
    return _rooms.values
      .where((room) => room.players.length < room.maxPlayers)
      .toList();
  }
  
  /// 按游戏模式筛选房间
  List<Room> getRoomsByMode(String gameMode) {
    return _rooms.values
      .where((room) => room.gameMode == gameMode)
      .toList();
  }
  
  /// 清理空房间
  void cleanupEmptyRooms() {
    final emptyRooms = _rooms.values
      .where((room) => room.players.isEmpty && !room.isPersistent)
      .map((room) => room.id)
      .toList();
    
    for (final id in emptyRooms) {
      _rooms.remove(id);
    }
    
    if (emptyRooms.isNotEmpty) {
      notifyListeners();
    }
  }
}
