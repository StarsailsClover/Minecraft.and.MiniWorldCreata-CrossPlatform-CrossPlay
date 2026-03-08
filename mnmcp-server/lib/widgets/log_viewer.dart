import 'package:flutter/material.dart';

class LogViewer extends StatelessWidget {
  final List<String> logs;

  const LogViewer({
    super.key,
    required this.logs,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFF1A1A2E),
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.white.withOpacity(0.1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                const Icon(
                  Icons.terminal,
                  color: Color(0xFF6C63FF),
                  size: 20,
                ),
                const SizedBox(width: 8),
                const Text(
                  '服务器日志',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                Text(
                  '${logs.length} 条',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.5),
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: Container(
              margin: const EdgeInsets.all(16),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF0F0F17),
                borderRadius: BorderRadius.circular(8),
              ),
              child: logs.isEmpty
                  ? Center(
                      child: Text(
                        '暂无日志',
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.3),
                        ),
                      ),
                    )
                  : ListView.builder(
                      reverse: true,
                      itemCount: logs.length,
                      itemBuilder: (context, index) {
                        final log = logs[logs.length - 1 - index];
                        return _LogEntry(text: log);
                      },
                    ),
            ),
          ),
        ],
      ),
    );
  }
}

class _LogEntry extends StatelessWidget {
  final String text;

  const _LogEntry({required this.text});

  @override
  Widget build(BuildContext context) {
    Color color = Colors.white70;
    
    if (text.contains('[ERROR]')) {
      color = Colors.red;
    } else if (text.contains('[WARN]')) {
      color = Colors.orange;
    } else if (text.contains('✓') || text.contains('success')) {
      color = Colors.green;
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Text(
        text,
        style: TextStyle(
          color: color,
          fontSize: 12,
          fontFamily: 'Consolas',
        ),
      ),
    );
  }
}
