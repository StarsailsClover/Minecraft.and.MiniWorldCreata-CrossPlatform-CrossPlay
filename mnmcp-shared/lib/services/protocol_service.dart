import 'dart:typed_data';
import 'package:flutter/foundation.dart';

import '../protocol/translator.dart';
import '../protocol/packet.dart';

/// 协议处理服务 (三端共用)
class ProtocolService extends ChangeNotifier {
  final ProtocolTranslator _translator = ProtocolTranslator();
  bool _isProcessing = false;

  bool get isProcessing => _isProcessing;
  int get packetsProcessed => _translator.packetsProcessed;
  int get packetsTranslated => _translator.packetsTranslated;
  int get translationErrors => _translator.translationErrors;

  void start() {
    _isProcessing = true;
    notifyListeners();
  }

  void stop() {
    _isProcessing = false;
    notifyListeners();
  }

  UnifiedPacket? processMNWPacket(Uint8List data) {
    final pkt = _translator.decodeMNW(data);
    notifyListeners();
    return pkt;
  }

  UnifiedPacket? processMCPacket(Uint8List data) {
    final pkt = _translator.decodeMC(data);
    notifyListeners();
    return pkt;
  }
}
