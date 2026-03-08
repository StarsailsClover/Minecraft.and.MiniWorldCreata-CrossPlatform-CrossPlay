import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../models/connection_config.dart';

/// 连接状态
enum MnMCPConnectionState {
  disconnected,
  connecting,
  connected,
  error,
}

/// 连接服务 (三端共用)
class ConnectionService extends ChangeNotifier {
  MnMCPConnectionState _state = MnMCPConnectionState.disconnected;
  ConnectionConfig? _config;
  WebSocketChannel? _channel;
  String _errorMessage = '';

  // 统计
  DateTime? _connectTime;
  int _bytesSent = 0;
  int _bytesReceived = 0;
  int _packetsSent = 0;
  int _packetsReceived = 0;

  // Getters
  MnMCPConnectionState get state => _state;
  ConnectionConfig? get config => _config;
  bool get isConnected => _state == MnMCPConnectionState.connected;
  String get errorMessage => _errorMessage;
  DateTime? get connectTime => _connectTime;
  int get bytesSent => _bytesSent;
  int get bytesReceived => _bytesReceived;
  int get packetsSent => _packetsSent;
  int get packetsReceived => _packetsReceived;
  Duration? get uptime => _connectTime != null
      ? DateTime.now().difference(_connectTime!)
      : null;

  // 数据流
  Stream<dynamic>? get dataStream => _channel?.stream;

  /// 连接到服务器
  Future<void> connect(ConnectionConfig config) async {
    _config = config;
    _state = MnMCPConnectionState.connecting;
    _errorMessage = '';
    notifyListeners();

    try {
      final uri = Uri.parse('ws://\${config.host}:\${config.port}');
      _channel = WebSocketChannel.connect(uri);
      await _channel!.ready;

      _state = MnMCPConnectionState.connected;
      _connectTime = DateTime.now();
      _bytesSent = 0;
      _bytesReceived = 0;

      _channel!.stream.listen(
        (data) {
          _packetsReceived++;
          if (data is List<int>) _bytesReceived += data.length;
          notifyListeners();
        },
        onError: (error) {
          _state = MnMCPConnectionState.error;
          _errorMessage = error.toString();
          notifyListeners();
        },
        onDone: () {
          _state = MnMCPConnectionState.disconnected;
          notifyListeners();
        },
      );

      notifyListeners();
    } catch (e) {
      _state = MnMCPConnectionState.error;
      _errorMessage = e.toString();
      notifyListeners();
    }
  }

  /// 发送数据
  void send(dynamic data) {
    if (_channel != null && isConnected) {
      _channel!.sink.add(data);
      _packetsSent++;
      if (data is List<int>) _bytesSent += data.length;
      notifyListeners();
    }
  }

  /// 断开连接
  Future<void> disconnect() async {
    await _channel?.sink.close();
    _channel = null;
    _state = MnMCPConnectionState.disconnected;
    notifyListeners();
  }

  @override
  void dispose() {
    _channel?.sink.close();
    super.dispose();
  }
}
