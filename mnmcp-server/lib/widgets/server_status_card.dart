import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../services/server_service.dart';

class ServerStatusCard extends StatelessWidget {
  const ServerStatusCard({super.key});

  @override
  Widget build(BuildContext context) {
    final server = context.watch<ServerService>();
    
    return Card(
      color: const Color(0xFF1A1A2E),
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.white.withOpacity(0.1)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 12,
                  height: 12,
                  decoration: BoxDecoration(
                    color: server.isRunning ? Colors.green : Colors.red,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: (server.isRunning ? Colors.green : Colors.red).withOpacity(0.5),
                        blurRadius: 8,
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  server.isRunning ? '运行中' : '已停止',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                ElevatedButton.icon(
                  onPressed: () {
                    if (server.isRunning) {
                      server.stop();
                    } else {
                      server.start();
                    }
                  },
                  icon: Icon(
                    server.isRunning ? Icons.stop : Icons.play_arrow,
                    size: 18,
                  ),
                  label: Text(server.isRunning ? '停止' : '启动'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: server.isRunning ? Colors.red : const Color(0xFF6C63FF),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                _StatItem(
                  label: '运行时间',
                  value: server.uptime != null
                      ? '${server.uptime!.inHours}h ${server.uptime!.inMinutes % 60}m'
                      : '--',
                ),
                _StatItem(
                  label: '总连接',
                  value: server.totalConnections.toString(),
                ),
                _StatItem(
                  label: '当前连接',
                  value: server.players.length.toString(),
                ),
                _StatItem(
                  label: '房间数',
                  value: server.rooms.length.toString(),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final String label;
  final String value;

  const _StatItem({
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: TextStyle(
              color: Colors.white.withOpacity(0.5),
              fontSize: 12,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}
