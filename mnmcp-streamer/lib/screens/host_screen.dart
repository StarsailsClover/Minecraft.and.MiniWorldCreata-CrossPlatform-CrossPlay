import 'package:mnmcp_shared/mnmcp_shared.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:window_manager/window_manager.dart';

import '../services/game_server_service.dart';

class HostScreen extends StatefulWidget {
  const HostScreen({super.key});

  @override
  State<HostScreen> createState() => _HostScreenState();
}

class _HostScreenState extends State<HostScreen> {
  // Form controllers
  final _worldNameController = TextEditingController(text: 'My MnMCP World');
  final _portController = TextEditingController(text: '19132');
  final _maxPlayersController = TextEditingController(text: '40');
  
  // State
  String _selectedGameMode = 'miniworld';
  String _selectedGameType = 'cn';

  @override
  void dispose() {
    _worldNameController.dispose();
    _portController.dispose();
    _maxPlayersController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final serverService = context.watch<GameServerService>();

    return Scaffold(
      backgroundColor: MnMCPTheme.bgPrimary,
      body: Column(
        children: [
          // Title Bar
          _buildTitleBar(),
          
          // Main Content
          Expanded(
            child: Row(
              children: [
                // Left Panel - Server Config
                Expanded(
                  flex: 2,
                  child: _buildConfigPanel(serverService),
                ),
                
                // Right Panel - Status & Players
                Expanded(
                  flex: 3,
                  child: _buildStatusPanel(serverService),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTitleBar() {
    return Container(
      height: 40,
      color: MnMCPTheme.bgSecondary,
      child: Row(
        children: [
          const SizedBox(width: 16),
          const Icon(Icons.dns, color: MnMCPTheme.accent, size: 20),
          const SizedBox(width: 8),
          const Text(
            'MnMCP Streamer',
            style: TextStyle(
              color: MnMCPTheme.textPrimary,
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
          const Spacer(),
          IconButton(
            icon: const Icon(Icons.remove, color: MnMCPTheme.textSecondary, size: 18),
            onPressed: () => windowManager.minimize(),
            splashRadius: 16,
          ),
          IconButton(
            icon: const Icon(Icons.close, color: MnMCPTheme.textSecondary, size: 18),
            onPressed: () => windowManager.close(),
            splashRadius: 16,
          ),
          const SizedBox(width: 8),
        ],
      ),
    );
  }

  Widget _buildConfigPanel(GameServerService server) {
    return Container(
      margin: const EdgeInsets.all(16),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSectionTitle('Server Configuration'),
            const SizedBox(height: 16),
            
            // Game Mode
            _buildGameModeSelector(),
            const SizedBox(height: 16),
            
            // World Name
            TextField(
              controller: _worldNameController,
              decoration: const InputDecoration(
                labelText: 'World Name',
                hintText: 'Enter world name',
              ),
              enabled: !server.isRunning,
            ),
            const SizedBox(height: 12),
            
            // Port
            TextField(
              controller: _portController,
              decoration: const InputDecoration(
                labelText: 'Port',
                hintText: '19132 or 25565',
              ),
              keyboardType: TextInputType.number,
              enabled: !server.isRunning,
            ),
            const SizedBox(height: 12),
            
            // Max Players
            TextField(
              controller: _maxPlayersController,
              decoration: const InputDecoration(
                labelText: 'Max Players',
                hintText: '10-100',
              ),
              keyboardType: TextInputType.number,
              enabled: !server.isRunning,
            ),
            const SizedBox(height: 24),
            
            // Start/Stop Button
            _buildActionButton(server),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        color: MnMCPTheme.textPrimary,
        fontSize: 16,
        fontWeight: FontWeight.w600,
      ),
    );
  }

  Widget _buildGameModeSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Game Mode',
          style: TextStyle(color: MnMCPTheme.textSecondary, fontSize: 13),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: _buildModeCard(
                'MiniWorld',
                'CN / Global',
                _selectedGameMode == 'miniworld',
                () => setState(() => _selectedGameMode = 'miniworld'),
                !context.read<GameServerService>().isRunning,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildModeCard(
                'Minecraft',
                'Java / Bedrock',
                _selectedGameMode == 'minecraft',
                () => setState(() => _selectedGameMode = 'minecraft'),
                !context.read<GameServerService>().isRunning,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildModeCard(String title, String subtitle, bool isSelected, VoidCallback onTap, bool enabled) {
    return GestureDetector(
      onTap: enabled ? onTap : null,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isSelected ? MnMCPTheme.bgHover : MnMCPTheme.bgSecondary,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? MnMCPTheme.accent : MnMCPTheme.border,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Column(
          children: [
            Text(
              title,
              style: TextStyle(
                color: isSelected ? MnMCPTheme.textPrimary : MnMCPTheme.textSecondary,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: const TextStyle(
                color: MnMCPTheme.textMuted,
                fontSize: 11,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButton(GameServerService server) {
    final bool isRunning = server.isRunning;
    final bool isStarting = server.isStarting;
    
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: isStarting ? null : () {
          if (isRunning) {
            server.stop();
          } else {
            _startServer(server);
          }
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: isRunning ? MnMCPTheme.error : MnMCPTheme.success,
          padding: const EdgeInsets.symmetric(vertical: 16),
        ),
        child: isStarting
          ? const SizedBox(
              height: 20,
              width: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              ),
            )
          : Text(
              isRunning ? 'Stop Server' : 'Start Server',
              style: const TextStyle(fontSize: 16),
            ),
      ),
    );
  }

  void _startServer(GameServerService server) {
    final config = ServerConfig(
      gameMode: _selectedGameMode,
      gameType: _selectedGameMode == 'miniworld' ? 'cn' : 'java',
      tcpPort: int.tryParse(_portController.text) ?? 19132,
      maxPlayers: int.tryParse(_maxPlayersController.text) ?? 40,
      worldName: _worldNameController.text,
    );
    
    server.start(config);
  }

  Widget _buildStatusPanel(GameServerService server) {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: MnMCPTheme.bgSecondary,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: MnMCPTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Status Header
          Row(
            children: [
              Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  color: server.isRunning ? MnMCPTheme.success : MnMCPTheme.error,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: (server.isRunning ? MnMCPTheme.success : MnMCPTheme.error).withValues(alpha: 0.5),
                      blurRadius: 8,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              Text(
                server.isRunning ? 'Server Running' : 'Server Stopped',
                style: const TextStyle(
                  color: MnMCPTheme.textPrimary,
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // Stats
          if (server.isRunning) ...[
            _buildStatRow('Uptime', _formatDuration(server.uptime)),
            _buildStatRow('Tick Count', '${server.tickCount}'),
            _buildStatRow('World Time', '${server.worldTime}'),
            const Divider(color: MnMCPTheme.border, height: 24),
          ],
          
          // Player Count
          _buildStatRow('Players', '${server.playerCount} / ${server.maxPlayers}'),
          
          const SizedBox(height: 16),
          
          // Player List
          const Text(
            'Connected Players',
            style: TextStyle(
              color: MnMCPTheme.textSecondary,
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          
          Expanded(
            child: server.players.isEmpty
              ? const Center(
                  child: Text(
                    'No players connected',
                    style: TextStyle(color: MnMCPTheme.textMuted),
                  ),
                )
              : ListView.builder(
                  itemCount: server.players.length,
                  itemBuilder: (context, index) {
                    final player = server.players.values.elementAt(index);
                    return _buildPlayerTile(player);
                  },
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: MnMCPTheme.textSecondary,
              fontSize: 13,
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              color: MnMCPTheme.textPrimary,
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPlayerTile(GamePlayer player) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: MnMCPTheme.bgTertiary,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          const Icon(Icons.person, color: MnMCPTheme.accent, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  player.name,
                  style: const TextStyle(
                    color: MnMCPTheme.textPrimary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  '${player.platform} • ${player.health}/${player.maxHealth} HP',
                  style: const TextStyle(
                    color: MnMCPTheme.textMuted,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close, color: MnMCPTheme.error, size: 18),
            onPressed: () {
              // Kick player
            },
            splashRadius: 16,
          ),
        ],
      ),
    );
  }

  String _formatDuration(Duration? duration) {
    if (duration == null) return '--:--:--';
    return '${duration.inHours.toString().padLeft(2, '0')}:${(duration.inMinutes % 60).toString().padLeft(2, '0')}:${(duration.inSeconds % 60).toString().padLeft(2, '0')}';
  }
}
