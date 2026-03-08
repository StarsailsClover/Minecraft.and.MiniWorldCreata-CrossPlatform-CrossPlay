import 'package:flutter/material.dart';

import '../models/player.dart';

class PlayerList extends StatelessWidget {
  final List<Player> players;

  const PlayerList({
    super.key,
    required this.players,
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
                  Icons.people,
                  color: Color(0xFF6C63FF),
                  size: 20,
                ),
                const SizedBox(width: 8),
                const Text(
                  '在线玩家',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                Text(
                  '${players.length} 人',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.5),
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: players.isEmpty
                ? Center(
                    child: Text(
                      '暂无玩家',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.3),
                      ),
                    ),
                  )
                : ListView.builder(
                    itemCount: players.length,
                    itemBuilder: (context, index) {
                      final player = players[index];
                      return _PlayerItem(player: player);
                    },
                  ),
          ),
        ],
      ),
    );
  }
}

class _PlayerItem extends StatelessWidget {
  final Player player;

  const _PlayerItem({required this.player});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: const Color(0xFF6C63FF).withOpacity(0.2),
        child: Icon(
          player.platform == 'miniworld' ? Icons.home : Icons.sports_esports,
          color: const Color(0xFF6C63FF),
          size: 16,
        ),
      ),
      title: Text(
        player.name,
        style: const TextStyle(color: Colors.white),
      ),
      subtitle: Text(
        player.roomId != null ? '在房间中' : '大厅',
        style: TextStyle(color: Colors.white.withOpacity(0.5)),
      ),
      trailing: Container(
        width: 8,
        height: 8,
        decoration: const BoxDecoration(
          color: Colors.green,
          shape: BoxShape.circle,
        ),
      ),
    );
  }
}
