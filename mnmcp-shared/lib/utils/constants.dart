/// MnMCP 常量
class MnMCPConstants {
  static const String version = '1.0.0_26w13a';
  static const String appName = 'MnMCP';

  // 默认端口
  static const int defaultMCPort = 25565;
  static const int defaultMNWPort = 19132;
  static const int defaultWSPort = 8080;
  static const int defaultAPIPort = 8081;

  // 限制
  static const int maxPlayers = 40;
  static const int maxRooms = 100;
  static const int heartbeatInterval = 15; // seconds
  static const int sessionTimeout = 30; // seconds
}
