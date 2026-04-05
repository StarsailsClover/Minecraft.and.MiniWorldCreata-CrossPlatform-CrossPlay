import 'package:flutter/material.dart';

import '../models/room.dart';

class RoomList extends StatelessWidget {
  final List<Room> rooms;

  const RoomList({
    super.key,
    required this.rooms,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFF1A1A2E),
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.white.withOpacity(0.1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                const Icon(
                  Icons.meeting_room,
                  color: Color(0xFF6C63FF),
                  size: 20,
                ),
                const SizedBox(width: 8),
                const Text(
                  '房间列表',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                Text(
                  '${rooms.length} 个房间',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.5),
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: rooms.isEmpty
                ? Center(
                    child: Text(
                      '暂无房间',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.3),
                      ),
                    ),
                  )
                : ListView.builder(
                    itemCount: rooms.length,
                    itemBuilder: (context, index) {
                      final room = rooms[index];
                      return _RoomItem(room: room);
                    },
                  ),
          ),
        ],
      ),
    );
  }
}

class _RoomItem extends StatelessWidget {
  final Room room;

  const _RoomItem({required this.room});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(
        room.gameMode == 'miniworld' ? Icons.home : Icons.sports_esports,
        color: const Color(0xFF6C63FF),
      ),
      title: Text(
        room.name,
        style: const TextStyle(color: Colors.white),
      ),
      subtitle: Text(
        '${room.players.length}/${room.maxPlayers} 玩家',
        style: TextStyle(color: Colors.white.withOpacity(0.5)),
      ),
      trailing: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: const Color(0xFF6C63FF).withOpacity(0.2),
          borderRadius: BorderRadius.circular(4),
        ),
        child: Text(
          room.gameMode.toUpperCase(),
          style: const TextStyle(
            color: Color(0xFF6C63FF),
            fontSize: 10,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}
