import 'package:flutter/material.dart';

import '../utils/theme.dart';

/// 日志查看器 (三端共用)
class LogViewer extends StatelessWidget {
  final List<String> logs;
  final String title;

  const LogViewer({
    super.key,
    required this.logs,
    this.title = '日志',
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: MnMCPTheme.bgSecondary,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.white.withOpacity(0.1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                const Icon(Icons.terminal, color: MnMCPTheme.accent, size: 18),
                const SizedBox(width: 8),
                Text(title,
                    style: const TextStyle(
                        color: Colors.white,
                        fontSize: 14,
                        fontWeight: FontWeight.w600)),
                const Spacer(),
                Text('\${logs.length} 条',
                    style: TextStyle(
                        color: MnMCPTheme.textMuted, fontSize: 12)),
              ],
            ),
          ),
          const Divider(height: 1, color: MnMCPTheme.border),
          Expanded(
            child: ListView.builder(
              reverse: true,
              padding: const EdgeInsets.all(8),
              itemCount: logs.length,
              itemBuilder: (_, i) {
                final log = logs[logs.length - 1 - i];
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 1),
                  child: Text(
                    log,
                    style: const TextStyle(
                      fontFamily: 'Cascadia Code',
                      fontSize: 11,
                      color: MnMCPTheme.textSecondary,
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
