import 'package:flutter/material.dart';
import 'package:window_manager/window_manager.dart';

import '../utils/theme.dart';

/// 统一标题栏 (三端共用, 通过 title 和 icon 区分)
class MnMCPTitleBar extends StatelessWidget {
  final String title;
  final IconData icon;

  const MnMCPTitleBar({
    super.key,
    required this.title,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onPanStart: (_) => windowManager.startDragging(),
      child: Container(
        height: 40,
        color: MnMCPTheme.bgSecondary,
        child: Row(
          children: [
            const SizedBox(width: 16),
            Icon(icon, color: MnMCPTheme.accent, size: 20),
            const SizedBox(width: 8),
            Text(
              title,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
            const Spacer(),
            _WinBtn(Icons.remove, () => windowManager.minimize()),
            _WinBtn(Icons.crop_square, () async {
              if (await windowManager.isMaximized()) {
                windowManager.unmaximize();
              } else {
                windowManager.maximize();
              }
            }),
            _WinBtn(Icons.close, () => windowManager.close(),
                hoverColor: Colors.red),
          ],
        ),
      ),
    );
  }
}

class _WinBtn extends StatefulWidget {
  final IconData icon;
  final VoidCallback onPressed;
  final Color? hoverColor;
  const _WinBtn(this.icon, this.onPressed, {this.hoverColor});

  @override
  State<_WinBtn> createState() => _WinBtnState();
}

class _WinBtnState extends State<_WinBtn> {
  bool _hovering = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _hovering = true),
      onExit: (_) => setState(() => _hovering = false),
      child: GestureDetector(
        onTap: widget.onPressed,
        child: Container(
          width: 46,
          height: 40,
          color: _hovering
              ? (widget.hoverColor ?? Colors.white.withOpacity(0.1))
              : Colors.transparent,
          child: Icon(widget.icon, color: Colors.white, size: 16),
        ),
      ),
    );
  }
}
