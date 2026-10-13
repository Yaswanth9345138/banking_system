import 'package:flutter/material.dart';

/// The look of the app is an old bank passbook: a solid ink-blue cover,
/// pale ledger paper, green for money in and brick red for money out.
class AppColors {
  static const ink = Color(0xFF123B4A);
  static const paperLight = Color(0xFFF3F4EF);
  static const paperDark = Color(0xFF12171A);
  static const brass = Color(0xFFE0A83A);

  static const _creditLight = Color(0xFF1E7B4F);
  static const _creditDark = Color(0xFF5FCB93);
  static const _debitLight = Color(0xFFB3361F);
  static const _debitDark = Color(0xFFF08A74);

  static Color credit(BuildContext context) {
    return Theme.of(context).brightness == Brightness.dark
        ? _creditDark
        : _creditLight;
  }

  static Color debit(BuildContext context) {
    return Theme.of(context).brightness == Brightness.dark
        ? _debitDark
        : _debitLight;
  }
}

ThemeData buildTheme(Brightness brightness) {
  final isDark = brightness == Brightness.dark;
  final base = ColorScheme.fromSeed(
    seedColor: AppColors.ink,
    brightness: brightness,
  );

  final scheme = isDark
      ? base.copyWith(surface: AppColors.paperDark)
      : base.copyWith(
          primary: AppColors.ink,
          onPrimary: Colors.white,
          surface: AppColors.paperLight,
        );

  return ThemeData(
    colorScheme: scheme,
    scaffoldBackgroundColor: scheme.surface,
  );
}
