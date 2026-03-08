import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:logger/logger.dart';
import 'package:shelf/shelf.dart';
import 'package:shelf/shelf_io.dart' as shelf_io;
import 'package:shelf_web_socket/shelf_web_socket.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../models/player.dart';
import '../models/room.dart';

/// 服务器服务
/// 管理公共服务器，处理多房间、玩家连接、协议桥接
class ServerService extends ChangeNotifier {
  final Logger _logger = Logger();
  
  // 服务器状态
  bool _isRunning = false;
  bool get isRunning => _isRunning;
  
  // HTTP服务器
  HttpServer? _httpServer;
  
  // WebSocket连接
  final Map<String, WebSocketChannel> _connections = {};
  
  // 房间管理
  final Map<String, Room> _rooms = {};
  Map<String, Room> get rooms => Map.unmodifiable(_rooms);
  
  // 玩家管理
  final Map<String, Player> _players = {};
  Map<String, Player> get players => Map.unmodifiable(_players);
  
  // 统计
  int _totalConnections = 0;
  int get totalConnections => _totalConnections;
  
  DateTime? _startTime;
  Duration? get uptime => _startTime != null 
    ? DateTime.now().difference(_startTime!) 
    : null;
  
  // 配置
  int _maxRooms = 100;
  int get maxRooms => _maxRooms;
  
  int _maxPlayersPerRoom = 40;
  int get maxPlayersPerRoom => _maxPlayersPerRoom;
  
  int _tcpPort = 25565;
  int get tcpPort => _tcpPort;
  
  int _wsPort = 8080;
  int get wsPort => _wsPort;
  
  // 日志
  final List<String> _logs = [];
  List<String> get logs => List.unmodifiable(_logs);
  
  void _log(String message) {
    final timestamp = DateTime.now().toIso8601String();
    final logEntry = '[$timestamp] $message';
    _logs.add(logEntry);
    if (_logs.length > 1000) {
      _logs.removeAt(0);
    }
    _logger.i(message);
    notifyListeners();
  }
  
  /// 启动服务器
  Future<void> start({
    int? tcpPort,
    int? wsPort,
    int? maxRooms,
    int? maxPlayersPerRoom,
  }) async {
    if (_isRunning) {
      throw Exception('Server already running');
    }
    
    _tcpPort = tcpPort ?? _tcpPort;
    _wsPort = wsPort ?? _wsPort;
    _maxRooms = maxRooms ?? _maxRooms;
    _maxPlayersPerRoom = maxPlayersPerRoom ?? _maxPlayersPerRoom;
    
    _log('Starting MnMCP Server...');
    _log('TCP Port: $_tcpPort, WebSocket Port: $_wsPort');
    
    try {
      // 启动HTTP/WebSocket服务器
      final handler = const Pipeline()
        .addMiddleware(logRequests())
        .addHandler(_handleRequest);
      
      _httpServer = await shelf_io.serve(
        handler, 
        InternetAddress.anyIPv4, 
        _wsPort,
      );
      
      _isRunning = true;
      _startTime = DateTime.now();
      
      _log('Server started successfully');
      notifyListeners();
      
    } catch (e) {
      _log('Failed to start server: $e');
      rethrow;
    }
  }
  
  /// 停止服务器
  Future<void> stop() async {
    if (!_isRunning) return;
    
    _log('Stopping server...');
    
    // 断开所有连接
    for (final conn in _connections.values) {
      conn.sink.close();
    }
    _connections.clear();
    
    // 关闭HTTP服务器
    await _httpServer?.close();
    _httpServer = null;
    
    _isRunning = false;
    _startTime = null;
    
    _log('Server stopped');
    notifyListeners();
  }
  
  /// 处理HTTP请求
  Response _handleRequest(Request request) {
    // WebSocket升级
    if (request.url.path == 'ws') {
      return webSocketHandler(_handleWebSocket)(request);
    }
    
    // API端点
    if (request.url.path == 'api/status') {
      return _handleStatusRequest(request);
    }
    
    if (request.url.path == 'api/rooms') {
      return _handleRoomsRequest(request);
    }
    
    // 默认响应
    return Response.ok(
      jsonEncode({
        'name': 'MnMCP Server',
        'version': '0.4.0',
        'status': _isRunning ? 'running' : 'stopped',
      }),
      headers: {'Content-Type': 'application/json'},
    );
  }
  
  /// 处理WebSocket连接
  void _handleWebSocket(WebSocketChannel channel) {
    final connectionId = DateTime.now().millisecondsSinceEpoch.toString();
    _connections[connectionId] = channel;
    _totalConnections++;
    
    _log('New connection: $connectionId');
    
    channel.stream.listen(
      (message) => _handleMessage(connectionId, channel, message),
      onDone: () => _handleDisconnect(connectionId),
      onError: (error) => _log('Connection error: $error'),
    );
    
    // 发送欢迎消息
    channel.sink.add(jsonEncode({
      'type': 'welcome',
      'server': 'MnMCP Server',
      'version': '0.4.0',
    }));
    
    notifyListeners();
  }
  
  /// 处理WebSocket消息
  void _handleMessage(String connectionId, WebSocketChannel channel, dynamic message) {
    try {
      final data = jsonDecode(message);
      final type = data['type'];
      
      switch (type) {
        case 'auth':
          _handleAuth(connectionId, data);
          break;
        case 'join_room':
          _handleJoinRoom(connectionId, data);
          break;
        case 'leave_room':
          _handleLeaveRoom(connectionId);
          break;
        case 'create_room':
          _handleCreateRoom(connectionId, data);
          break;
        case 'game_data':
          _handleGameData(connectionId, data);
          break;
        case 'ping':
          channel.sink.add(jsonEncode({'type': 'pong'}));
          break;
        default:
          _log('Unknown message type: $type');
      }
    } catch (e) {
      _log('Error handling message: $e');
    }
  }
  
  /// 处理认证
  void _handleAuth(String connectionId, Map<String, dynamic> data) {
    final playerId = data['playerId'];
    final playerName = data['playerName'];
    
    final player = Player(
      id: playerId,
      name: playerName,
      connectionId: connectionId,
      platform: data['platform'] ?? 'unknown',
    );
    
    _players[connectionId] = player;
    _log('Player authenticated: $playerName ($playerId)');
    
    _connections[connectionId]?.sink.add(jsonEncode({
      'type': 'auth_success',
      'playerId': playerId,
    }));
    
    notifyListeners();
  }
  
  /// 处理加入房间
  void _handleJoinRoom(String connectionId, Map<String, dynamic> data) {
    final roomId = data['roomId'];
    final player = _players[connectionId];
    
    if (player == null) {
      _connections[connectionId]?.sink.add(jsonEncode({
        'type': 'error',
        'message': 'Not authenticated',
      }));
      return;
    }
    
    final room = _rooms[roomId];
    if (room == null) {
      _connections[connectionId]?.sink.add(jsonEncode({
        'type': 'error',
        'message': 'Room not found',
      }));
      return;
    }
    
    if (room.players.length >= _maxPlayersPerRoom) {
      _connections[connectionId]?.sink.add(jsonEncode({
        'type': 'error',
        'message': 'Room is full',
      }));
      return;
    }
    
    room.addPlayer(player);
    player.roomId = roomId;
    
    _log('Player ${player.name} joined room ${room.name}');
    
    // 通知房间内的其他玩家
    _broadcastToRoom(roomId, {
      'type': 'player_join',
      'playerId': player.id,
      'playerName': player.name,
    }, excludeConnectionId: connectionId);
    
    _connections[connectionId]?.sink.add(jsonEncode({
      'type': 'join_success',
      'roomId': roomId,
      'roomName': room.name,
      'players': room.players.map((p) => {
        return {'id': p.id, 'name': p.name};
      }).toList(),
    }));
    
    notifyListeners();
  }
  
  /// 处理离开房间
  void _handleLeaveRoom(String connectionId) {
    final player = _players[connectionId];
    if (player == null || player.roomId == null) return;
    
    final room = _rooms[player.roomId];
    if (room != null) {
      room.removePlayer(player);
      _log('Player ${player.name} left room ${room.name}');
      
      _broadcastToRoom(player.roomId!, {
        'type': 'player_leave',
        'playerId': player.id,
        'playerName': player.name,
      });
      
      // 如果房间空了，删除房间
      if (room.players.isEmpty && !room.isPersistent) {
        _rooms.remove(room.id);
        _log('Room ${room.name} removed (empty)');
      }
    }
    
    player.roomId = null;
    notifyListeners();
  }
  
  /// 处理创建房间
  void _handleCreateRoom(String connectionId, Map<String, dynamic> data) {
    if (_rooms.length >= _maxRooms) {
      _connections[connectionId]?.sink.add(jsonEncode({
        'type': 'error',
        'message': 'Max rooms reached',
      }));
      return;
    }
    
    final room = Room(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      name: data['name'] ?? 'Unnamed Room',
      hostId: connectionId,
      gameMode: data['gameMode'] ?? 'miniworld',
      maxPlayers: data['maxPlayers'] ?? _maxPlayersPerRoom,
    );
    
    _rooms[room.id] = room;
    _log('Room created: ${room.name} (${room.id})');
    
    _connections[connectionId]?.sink.add(jsonEncode({
      'type': 'room_created',
      'roomId': room.id,
      'roomName': room.name,
    }));
    
    notifyListeners();
  }
  
  /// 处理游戏数据
  void _handleGameData(String connectionId, Map<String, dynamic> data) {
    final player = _players[connectionId];
    if (player?.roomId == null) return;
    
    // 转发给房间内的其他玩家
    _broadcastToRoom(player!.roomId!, {
      'type': 'game_data',
      'from': player.id,
      'data': data['data'],
    }, excludeConnectionId: connectionId);
  }
  
  /// 处理断开连接
  void _handleDisconnect(String connectionId) {
    _log('Connection closed: $connectionId');
    
    // 如果玩家在房间中，先离开房间
    _handleLeaveRoom(connectionId);
    
    _players.remove(connectionId);
    _connections.remove(connectionId);
    
    notifyListeners();
  }
  
  /// 广播到房间
  void _broadcastToRoom(String roomId, Map<String, dynamic> message, {String? excludeConnectionId}) {
    final room = _rooms[roomId];
    if (room == null) return;
    
    final encoded = jsonEncode(message);
    
    for (final player in room.players) {
      if (player.connectionId != excludeConnectionId) {
        _connections[player.connectionId]?.sink.add(encoded);
      }
    }
  }
  
  /// 处理状态请求
  Response _handleStatusRequest(Request request) {
    return Response.ok(
      jsonEncode({
        'running': _isRunning,
        'uptime': uptime?.inSeconds ?? 0,
        'totalConnections': _totalConnections,
        'currentConnections': _connections.length,
        'rooms': _rooms.length,
        'players': _players.length,
      }),
      headers: {'Content-Type': 'application/json'},
    );
  }
  
  /// 处理房间列表请求
  Response _handleRoomsRequest(Request request) {
    final roomList = _rooms.values.map((room) => {
      return {
        'id': room.id,
        'name': room.name,
        'gameMode': room.gameMode,
        'players': room.players.length,
        'maxPlayers': room.maxPlayers,
      };
    }).toList();
    
    return Response.ok(
      jsonEncode({'rooms': roomList}),
      headers: {'Content-Type': 'application/json'},
    );
  }
  
  /// 删除房间
  void deleteRoom(String roomId) {
    final room = _rooms.remove(roomId);
    if (room != null) {
      // 踢出所有玩家
      for (final player in room.players) {
        _connections[player.connectionId]?.sink.add(jsonEncode({
          'type': 'kicked',
          'reason': 'Room closed',
        }));
        player.roomId = null;
      }
      _log('Room deleted: ${room.name}');
      notifyListeners();
    }
  }
  
  /// 踢出玩家
  void kickPlayer(String connectionId, String reason) {
    final player = _players[connectionId];
    if (player != null) {
      _connections[connectionId]?.sink.add(jsonEncode({
        'type': 'kicked',
        'reason': reason,
      }));
      _handleDisconnect(connectionId);
      _log('Player kicked: ${player.name} ($reason)');
    }
  }
}
