import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Shows the .txt statement that the Python server generated, with a copy button.
class StatementDialog extends StatefulWidget {
  const StatementDialog({super.key, required this.text});

  final String text;

  @override
  State<StatementDialog> createState() => _StatementDialogState();
}

class _StatementDialogState extends State<StatementDialog> {
  bool _copied = false;

  Future<void> _copy() async {
    await Clipboard.setData(ClipboardData(text: widget.text));
    if (!mounted) {
      return;
    }
    setState(() => _copied = true);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Statement'),
      scrollable: true,
      content: SizedBox(
        width: 480,
        child: SelectableText(
          widget.text,
          style: const TextStyle(fontFamily: 'monospace', fontSize: 11),
        ),
      ),
      actions: [
        TextButton.icon(
          onPressed: _copy,
          icon: Icon(_copied ? Icons.check : Icons.copy, size: 18),
          label: Text(_copied ? 'Copied' : 'Copy text'),
        ),
        FilledButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Close'),
        ),
      ],
    );
  }
}
