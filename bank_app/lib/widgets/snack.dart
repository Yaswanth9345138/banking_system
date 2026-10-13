import 'package:flutter/material.dart';

/// One place for the little message bar at the bottom of the screen.
void showAppSnack(BuildContext context, String message, {bool error = false}) {
  final scheme = Theme.of(context).colorScheme;

  ScaffoldMessenger.of(context)
    ..hideCurrentSnackBar()
    ..showSnackBar(
      SnackBar(
        backgroundColor: error ? scheme.errorContainer : null,
        content: Text(
          message,
          style: TextStyle(color: error ? scheme.onErrorContainer : null),
        ),
      ),
    );
}
