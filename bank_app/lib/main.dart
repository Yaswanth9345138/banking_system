import 'package:flutter/material.dart';

import 'screens/login_screen.dart';
import 'theme.dart';

void main() => runApp(const BankApp());

class BankApp extends StatelessWidget {
  const BankApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Passbook',
      debugShowCheckedModeBanner: false,
      theme: buildTheme(Brightness.light),
      darkTheme: buildTheme(Brightness.dark),
      home: const LoginScreen(),
    );
  }
}
