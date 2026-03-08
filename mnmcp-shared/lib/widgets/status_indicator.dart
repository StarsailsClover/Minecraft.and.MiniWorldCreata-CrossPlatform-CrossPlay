import 'package:flutter/material.dart';

/// 状态指示灯 (三端共用)
class StatusIndicator extends StatelessWidget {
  final bool isActive;
  final String label;
  final Color? activeColor;
  final Color? inactiveColor;

  const StatusIndicator({
    super.key,
    required this.isActive,
    required this.label,
    this.activeColor,
    this.inactiveColor,
  });

  @override
  Widget build(BuildContext context) {
    final color = isActive
        ? (activeColor ?? Colors.green)
        : (inactiveColor ?? Colors.red);

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(color: color.withOpacity(0.5), blurRadius: 8),
            ],
          ),
        ),
        const SizedBox(width: 8),
        Text(
          label,
          style: TextStyle(
            color: Colors.white,
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}
