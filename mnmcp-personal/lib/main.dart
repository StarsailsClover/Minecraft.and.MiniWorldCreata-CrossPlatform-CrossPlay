import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:window_manager/window_manager.dart';

import 'package:mnmcp_shared/mnmcp_shared.dart';
import 'screens/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await windowManager.ensureInitialized();

  WindowOptions windowOptions = const WindowOptions(
    size: Size(1200, 800),
    center: true,
    backgroundColor: Colors.transparent,
    skipTaskbar: false,
    titleBarStyle: TitleBarStyle.hidden,
    title: 'MnMCP Personal',
  );

  windowManager.waitUntilReadyToShow(windowOptions, () async {
    await windowManager.show();
    await windowManager.focus();
  });

  runApp(const MnMCPPersonalApp());
}

class MnMCPPersonalApp extends StatelessWidget {
  const MnMCPPersonalApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ConnectionService()),
        ChangeNotifierProvider(create: (_) => ProtocolService()),
      ],
      child: MaterialApp(
        title: 'MnMCP Personal',
        debugShowCheckedModeBanner: false,
        theme: MnMCPTheme.darkTheme,
        home: const HomeScreen(),
      ),
    );
  }
}
