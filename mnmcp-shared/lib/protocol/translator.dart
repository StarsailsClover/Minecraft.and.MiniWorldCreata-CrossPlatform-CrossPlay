import 'dart:typed_data';
import 'packet.dart';

/// 协议翻译服务 (Dart 端轻量实现)
class ProtocolTranslator {
  int packetsProcessed = 0;
  int packetsTranslated = 0;
  int translationErrors = 0;

  /// MNW → 统一格式
  UnifiedPacket? decodeMNW(Uint8List data) {
    packetsProcessed++;
    if (data.length < 8) return null;
    try {
      final bd = ByteData.sublistView(data);
      final length = bd.getUint32(0, Endian.little);
      final msgType = bd.getUint32(4, Endian.little);

      // 心跳
      if (msgType == 3003) {
        packetsTranslated++;
        return UnifiedPacket(action: PacketAction.heartbeat, source: 'mnw');
      }

      // 聊天
      if (msgType == 2001 && data.length > 8) {
        final payload = String.fromCharCodes(data.sublist(8));
        packetsTranslated++;
        return UnifiedPacket(
          action: PacketAction.chatMessage, source: 'mnw', message: payload,
        );
      }

      packetsTranslated++;
      return UnifiedPacket(
        action: PacketAction.heartbeat, source: 'mnw', rawData: data,
      );
    } catch (e) {
      translationErrors++;
      return null;
    }
  }

  /// MC → 统一格式
  UnifiedPacket? decodeMC(Uint8List data) {
    packetsProcessed++;
    if (data.isEmpty) return null;
    try {
      packetsTranslated++;
      return UnifiedPacket(
        action: PacketAction.heartbeat, source: 'mc', rawData: data,
      );
    } catch (e) {
      translationErrors++;
      return null;
    }
  }

  /// 统一格式 → MNW bytes
  Uint8List encodeMNW(UnifiedPacket pkt) {
    if (pkt.action == PacketAction.heartbeat) {
      final bd = ByteData(8);
      bd.setUint32(0, 8, Endian.little);
      bd.setUint32(4, 3003, Endian.little);
      return bd.buffer.asUint8List();
    }
    return pkt.rawData ?? Uint8List(0);
  }
}
