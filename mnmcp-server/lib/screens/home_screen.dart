import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../services/server_service.dart';
import '../services/room_manager.dart';
import '../widgets/title_bar.dart';
import '../widgets/server_status_card.dart';
import '../widgets/room_list.dart';
import '../widgets/player_list.dart';
import '../widgets/log_viewer.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0F17),
      body: Column(
        children: [
          const TitleBar(),
          Expanded(
            child: Row(
              children: [
                // 左侧：服务器状态和房间列表
                Expanded(
                  flex: 2,
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: [
                        const ServerStatusCard(),
                        const SizedBox(height: 16),
                        Expanded(
                          child: RoomList(
                            rooms: context.watch<RoomManager>().rooms,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                
                // 中间：玩家列表
                Expanded(
                  flex: 2,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    child: PlayerList(
                      players: context.watch<ServerService>().players.values.toList(),
                    ),
                  ),
                ),
                
                // 右侧：日志
                Expanded(
                  flex: 3,
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: LogViewer(
                      logs: context.watch<ServerService>().logs,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
