import 'dart:async';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:shelf/shelf.dart';
import 'package:shelf/shelf_io.dart' as shelf_io;
import 'package:shelf_web_socket/shelf_web_socket.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

/// Game server states
enum ServerState {
  stopped,
  starting,
  running,
  error,
}

/// Game server configuration
class ServerConfig {
  final String gameMode; // 'miniworld' or 'minecraft'
  final String gameType; // 'cn', 'global', 'java', 'bedrock'
  final int tcpPort;
  final int udpPort;
  final int maxPlayers;
  final String worldName;
  final int? worldSeed;

  ServerConfig({
    required this.gameMode,
    required this.gameType,
    this.tcpPort = 19132,
    this.udpPort = 19132,
    this.maxPlayers = 40,
    this.worldName = 'MnMCP World',
    this.worldSeed,
  });
}

/// Player data
class GamePlayer {
  final String id;
  String name;
  String platform;
  DateTime joinTime;
  Map<String, dynamic> position;
  int health;
  int maxHealth;
  WebSocketChannel? channel;

  GamePlayer({
    required this.id,
    required this.name,
    required this.platform,
    required this.joinTime,
    this.position = const {'x': 0, 'y': 64, 'z': 0},
    this.health = 20,
    this.maxHealth = 20,
    this.channel,
  });
}

/// Game server service for hosting game sessions
class GameServerService extends ChangeNotifier {
  ServerState _state = ServerState.stopped;
  ServerConfig? _config;
  HttpServer? _httpServer;
  
  // Players
  final Map<String, GamePlayer> _players = {};
  
  // World state
  final Map<String, int> _blocks = {}; // "x,y,z" -> blockId
  final Map<String, dynamic> _entities = {};
  int _worldTime = 0;
  
  // Game loop
  Timer? _gameLoop;
  int _tickCount = 0;
  static const int _tickRate = 20; // 20 TPS
  
  // Statistics
  DateTime? _startTime;
  int _totalConnections = 0;
  int _totalPackets = 0;

  // Getters
  ServerState get state => _state;
  ServerConfig? get config => _config;
  bool get isRunning => _state == ServerState.running;
  bool get isStarting => _state == ServerState.starting;
  
  Map<String, GamePlayer> get players => Map.unmodifiable(_players);
  int get playerCount => _players.length;
  int get maxPlayers => _config?.maxPlayers ?? 40;
  int get worldTime => _worldTime;
  int get tickCount => _tickCount;
  
  DateTime? get startTime => _startTime;
  Duration? get uptime => _startTime != null 
    ? DateTime.now().difference(_startTime!) 
    : null;

  /// Start the game server
  Future<bool> start(ServerConfig config) async {
    if (_state == ServerState.running || _state == ServerState.starting) {
      return false;
    }

    _state = ServerState.starting;
    _config = config;
    notifyListeners();

    try {
      // Create HTTP server for WebSocket connections
      final handler = const Pipeline()
        .addMiddleware(logRequests())
        .addHandler(_handleRequest);
      
      _httpServer = await shelf_io.serve(
        handler,
        InternetAddress.anyIPv4,
        config.tcpPort,
      );

      // Start game loop
      _startGameLoop();

      _state = ServerState.running;
      _startTime = DateTime.now();
      notifyListeners();

      return true;
    } catch (e) {
      _state = ServerState.error;
      notifyListeners();
      return false;
    }
  }

  /// Stop the game server
  Future<void> stop() async {
    if (_state == ServerState.stopped) {
      return;
    }

    // Stop game loop
    _gameLoop?.cancel();
    _gameLoop = null;

    // Disconnect all players
    for (final player in _players.values) {
      player.channel?.sink.close();
    }
    _players.clear();

    // Close HTTP server
    await _httpServer?.close();
    _httpServer = null;

    _state = ServerState.stopped;
    _startTime = null;
    _tickCount = 0;
    notifyListeners();
  }

  /// Handle HTTP/WebSocket requests
  FutureOr<Response> _handleRequest(Request request) {
    if (request.url.path == 'ws' || request.url.path == 'ws/') {
      return webSocketHandler(_handleWebSocket)(request);
    }
    
    return Response.ok('MnMCP Streamer Server');
  }

  /// Handle WebSocket connections
  void _handleWebSocket(WebSocketChannel channel) {
    final clientId = DateTime.now().millisecondsSinceEpoch.toString();
    
    channel.stream.listen(
      (message) => _onMessage(clientId, channel, message),
      onError: (error) => _onError(clientId, error),
      onDone: () => _onDisconnect(clientId),
    );

    // Send welcome message
    channel.sink.add({
      'type': 'welcome',
      'serverVersion': '0.4.0',
      'gameMode': _config?.gameMode,
      'worldTime': _worldTime,
      'playerCount': _players.length,
      'maxPlayers': _config?.maxPlayers,
    });
  }

  void _onMessage(String clientId, WebSocketChannel channel, dynamic message) {
    _totalPackets++;
    
    try {
      // Parse message
      final data = message is String ? message : message.toString();
      
      // Handle different message types
      // TODO: Implement protocol handling
      
    } catch (e) {
      debugPrint('Error handling message: $e');
    }
    
    notifyListeners();
  }

  void _onError(String clientId, dynamic error) {
    debugPrint('Client $clientId error: $error');
  }

  void _onDisconnect(String clientId) {
    if (_players.containsKey(clientId)) {
      _players.remove(clientId);
      _broadcastPlayerLeave(clientId);
      notifyListeners();
    }
  }

  /// Start the game loop
  void _startGameLoop() {
    _gameLoop = Timer.periodic(
      const Duration(milliseconds: 1000 ~/ _tickRate),
      (_) => _gameTick(),
    );
  }

  /// Game tick
  void _gameTick() {
    _tickCount++;
    
    // Update world time
    _worldTime++;
    if (_worldTime > 24000) {
      _worldTime = 0;
    }
    
    // Broadcast world time every second
    if (_tickCount % _tickRate == 0) {
      _broadcast({
        'type': 'world_time',
        'time': _worldTime,
      });
    }
    
    // Broadcast player list every 5 seconds
    if (_tickCount % (_tickRate * 5) == 0) {
      _broadcastPlayerList();
    }
    
    notifyListeners();
  }

  /// Broadcast message to all players
  void _broadcast(dynamic message) {
    final payload = message is String ? message : message.toString();
    
    for (final player in _players.values) {
      player.channel?.sink.add(payload);
    }
  }

  /// Broadcast player list
  void _broadcastPlayerList() {
    final playerList = _players.values.map((p) => {
      'id': p.id,
      'name': p.name,
      'platform': p.platform,
    }).toList();
    
    _broadcast({
      'type': 'player_list',
      'players': playerList,
    });
  }

  /// Broadcast player leave
  void _broadcastPlayerLeave(String playerId) {
    _broadcast({
      'type': 'player_leave',
      'playerId': playerId,
    });
  }

  /// Set a block in the world
  void setBlock(int x, int y, int z, int blockId) {
    final key = '$x,$y,$z';
    _blocks[key] = blockId;
    
    _broadcast({
      'type': 'block_update',
      'x': x,
      'y': y,
      'z': z,
      'blockId': blockId,
    });
    
    notifyListeners();
  }

  /// Get a block from the world
  int getBlock(int x, int y, int z) {
    final key = '$x,$y,$z';
    return _blocks[key] ?? 0;
  }

  @override
  void dispose() {
    stop();
    super.dispose();
  }
}
