import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:window_manager/window_manager.dart';

import '../services/connection_service.dart';
import '../services/protocol_service.dart';
import '../utils/theme.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  // Form controllers
  final _hostController = TextEditingController(text: '127.0.0.1');
  final _portController = TextEditingController(text: '19132');
  final _nameController = TextEditingController();
  
  // State
  GameMode _selectedGameMode = GameMode.miniworld;
  GameType _selectedGameType = GameType.cn;
  TargetType _selectedTargetType = TargetType.streamer;

  @override
  void dispose() {
    _hostController.dispose();
    _portController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final connectionService = context.watch<ConnectionService>();
    final protocolService = context.watch<ProtocolService>();

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
                // Left Panel - Configuration
                Expanded(
                  flex: 2,
                  child: _buildConfigPanel(),
                ),
                
                // Right Panel - Status & Logs
                Expanded(
                  flex: 3,
                  child: _buildStatusPanel(connectionService, protocolService),
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
          const Icon(Icons.gamepad, color: MnMCPTheme.accent, size: 20),
          const SizedBox(width: 8),
          const Text(
            'MnMCP Personal',
            style: TextStyle(
              color: MnMCPTheme.textPrimary,
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
          const Spacer(),
          // Window controls
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

  Widget _buildConfigPanel() {
    return Container(
      margin: const EdgeInsets.all(16),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Step 1: Game Mode
            _buildSectionTitle('Step 1: Select Game Mode'),
            const SizedBox(height: 12),
            _buildGameModeSelector(),
            const SizedBox(height: 24),
            
            // Step 2: Connection
            _buildSectionTitle('Step 2: Connection Settings'),
            const SizedBox(height: 12),
            _buildConnectionSettings(),
            const SizedBox(height: 24),
            
            // Step 3: Action
            _buildSectionTitle('Step 3: Start Connection'),
            const SizedBox(height: 12),
            _buildActionButton(),
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
      children: [
        // Game Mode
        Row(
          children: [
            Expanded(
              child: _buildModeCard(
                'Minecraft',
                'Java / Bedrock',
                Icons.square_outlined,
                _selectedGameMode == GameMode.minecraft,
                () => setState(() => _selectedGameMode = GameMode.minecraft),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildModeCard(
                'MiniWorld',
                'CN / Global',
                Icons.home_outlined,
                _selectedGameMode == GameMode.miniworld,
                () => setState(() => _selectedGameMode = GameMode.miniworld),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        
        // Game Type
        if (_selectedGameMode == GameMode.minecraft) ...[
          Row(
            children: [
              Expanded(
                child: _buildTypeChip('Java', GameType.java),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildTypeChip('Bedrock', GameType.bedrock),
              ),
            ],
          ),
        ] else ...[
          Row(
            children: [
              Expanded(
                child: _buildTypeChip('CN Server', GameType.cn),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildTypeChip('Global', GameType.global),
              ),
            ],
          ),
        ],
      ],
    );
  }

  Widget _buildModeCard(String title, String subtitle, IconData icon, bool isSelected, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
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
            Icon(icon, color: isSelected ? MnMCPTheme.accent : MnMCPTheme.textSecondary, size: 32),
            const SizedBox(height: 8),
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
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTypeChip(String label, GameType type) {
    final isSelected = _selectedGameType == type;
    return GestureDetector(
      onTap: () => setState(() => _selectedGameType = type),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 16),
        decoration: BoxDecoration(
          color: isSelected ? MnMCPTheme.accent.withOpacity(0.2) : MnMCPTheme.bgTertiary,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected ? MnMCPTheme.accent : MnMCPTheme.border,
          ),
        ),
        child: Text(
          label,
          textAlign: TextAlign.center,
          style: TextStyle(
            color: isSelected ? MnMCPTheme.accent : MnMCPTheme.textSecondary,
            fontSize: 13,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
          ),
        ),
      ),
    );
  }

  Widget _buildConnectionSettings() {
    return Column(
      children: [
        // Target Type
        DropdownButtonFormField<TargetType>(
          value: _selectedTargetType,
          decoration: const InputDecoration(labelText: 'Target Type'),
          items: TargetType.values.map((type) {
            return DropdownMenuItem(
              value: type,
              child: Text(type == TargetType.streamer ? 'Streamer (Host)' : 'Public Server'),
            );
          }).toList(),
          onChanged: (value) {
            if (value != null) {
              setState(() => _selectedTargetType = value);
            }
          },
        ),
        const SizedBox(height: 12),
        
        // Host
        TextField(
          controller: _hostController,
          decoration: const InputDecoration(
            labelText: 'Host',
            hintText: '127.0.0.1 or your-server.com',
          ),
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
        ),
        const SizedBox(height: 12),
        
        // Player Name
        TextField(
          controller: _nameController,
          decoration: const InputDecoration(
            labelText: 'Player Name (Optional)',
            hintText: 'Your display name',
          ),
        ),
      ],
    );
  }

  Widget _buildActionButton() {
    final connectionService = context.watch<ConnectionService>();
    
    final bool isConnected = connectionService.isConnected;
    final bool isConnecting = connectionService.isConnecting;
    
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: isConnecting ? null : () {
          if (isConnected) {
            connectionService.disconnect();
          } else {
            _connect();
          }
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: isConnected ? MnMCPTheme.error : MnMCPTheme.accent,
          padding: const EdgeInsets.symmetric(vertical: 16),
        ),
        child: isConnecting
          ? const SizedBox(
              height: 20,
              width: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              ),
            )
          : Text(
              isConnected ? 'Disconnect' : 'Connect',
              style: const TextStyle(fontSize: 16),
            ),
      ),
    );
  }

  void _connect() {
    final config = ConnectionConfig(
      gameMode: _selectedGameMode,
      gameType: _selectedGameType,
      targetType: _selectedTargetType,
      host: _hostController.text,
      port: int.tryParse(_portController.text) ?? 19132,
      playerName: _nameController.text.isEmpty ? null : _nameController.text,
    );
    
    context.read<ConnectionService>().connect(config);
  }

  Widget _buildStatusPanel(ConnectionService connection, ProtocolService protocol) {
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
                  color: connection.isConnected ? MnMCPTheme.success : MnMCPTheme.error,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: (connection.isConnected ? MnMCPTheme.success : MnMCPTheme.error).withOpacity(0.5),
                      blurRadius: 8,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              Text(
                connection.isConnected ? 'Connected' : 'Disconnected',
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
          if (connection.isConnected) ...[
            _buildStatRow('Uptime', _formatDuration(connection.uptime)),
            _buildStatRow('Latency', '${connection.latency} ms'),
            _buildStatRow('Packets Sent', '${connection.packetsSent}'),
            _buildStatRow('Packets Received', '${connection.packetsReceived}'),
            const Divider(color: MnMCPTheme.border, height: 24),
          ],
          
          // Protocol Stats
          _buildStatRow('Packets Processed', '${protocol.packetsProcessed}'),
          _buildStatRow('Packets Translated', '${protocol.packetsTranslated}'),
          _buildStatRow('Translation Errors', '${protocol.translationErrors}'),
          
          const Spacer(),
          
          // Log Area
          Container(
            height: 200,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: MnMCPTheme.bgTertiary,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Logs',
                  style: TextStyle(
                    color: MnMCPTheme.textSecondary,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                SizedBox(height: 8),
                Expanded(
                  child: SingleChildScrollView(
                    child: Text(
                      'Waiting for connection...',
                      style: TextStyle(
                        color: MnMCPTheme.textMuted,
                        fontSize: 12,
                        fontFamily: 'monospace',
                      ),
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

  String _formatDuration(Duration? duration) {
    if (duration == null) return '--:--:--';
    return '${duration.inHours.toString().padLeft(2, '0')}:${(duration.inMinutes % 60).toString().padLeft(2, '0')}:${(duration.inSeconds % 60).toString().padLeft(2, '0')}';
  }
}
