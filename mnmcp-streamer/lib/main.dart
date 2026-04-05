import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:window_manager/window_manager.dart';

import 'package:mnmcp_shared/mnmcp_shared.dart';
import 'screens/host_screen.dart';
import 'services/game_server_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await windowManager.ensureInitialized();

  WindowOptions windowOptions = const WindowOptions(
    size: Size(1200, 800),
    center: true,
    backgroundColor: Colors.transparent,
    skipTaskbar: false,
    titleBarStyle: TitleBarStyle.hidden,
    title: 'MnMCP Streamer',
  );

  windowManager.waitUntilReadyToShow(windowOptions, () async {
    await windowManager.show();
    await windowManager.focus();
  });

  runApp(const MnMCPStreamerApp());
}

class MnMCPStreamerApp extends StatelessWidget {
  const MnMCPStreamerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => GameServerService()),
        ChangeNotifierProvider(create: (_) => ConnectionService()),
        ChangeNotifierProvider(create: (_) => ProtocolService()),
      ],
      child: MaterialApp(
        title: 'MnMCP Streamer',
        debugShowCheckedModeBanner: false,
        theme: MnMCPTheme.darkTheme,
        home: const HostScreen(),
      ),
    );
  }
}
