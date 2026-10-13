import 'package:flutter/material.dart';

import '../api_service.dart';
import '../widgets/snack.dart';
import 'home_screen.dart';

/// Sign in and register share one screen; the link under the button switches between them.
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _api = ApiService.instance;
  final _formKey = GlobalKey<FormState>();
  final _username = TextEditingController();
  final _name = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  late final TextEditingController _server =
      TextEditingController(text: _api.baseUrl);

  bool _registering = false;
  bool _showServer = false;
  bool _hidePassword = true;
  bool _busy = false;

  @override
  void dispose() {
    _username.dispose();
    _name.dispose();
    _email.dispose();
    _password.dispose();
    _server.dispose();
    super.dispose();
  }

  InputDecoration _decoration(String label, {Widget? suffix}) {
    return InputDecoration(
      labelText: label,
      border: const OutlineInputBorder(),
      suffixIcon: suffix,
    );
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _busy = true);
    _api.setBaseUrl(_server.text);

    try {
      if (_registering) {
        final accountNumber = await _api.register(
          username: _username.text.trim(),
          name: _name.text.trim(),
          email: _email.text.trim(),
          password: _password.text,
        );
        if (!mounted) {
          return;
        }
        setState(() {
          _registering = false;
          _password.clear();
        });
        showAppSnack(
          context,
          'Account created. Your account number is $accountNumber. Sign in to continue.',
        );
      } else {
        final profile = await _api.login(_username.text.trim(), _password.text);
        if (!mounted) {
          return;
        }
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (_) => HomeScreen(initialProfile: profile),
          ),
        );
      }
    } on ApiException catch (e) {
      if (!mounted) {
        return;
      }
      showAppSnack(context, e.message, error: true);
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  Future<void> _testConnection() async {
    _api.setBaseUrl(_server.text);
    try {
      await _api.ping();
      if (!mounted) {
        return;
      }
      showAppSnack(context, 'Connected to ${_api.baseUrl}');
    } on ApiException catch (e) {
      if (!mounted) {
        return;
      }
      showAppSnack(context, e.message, error: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Passbook',
                      style: text.headlineLarge?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: scheme.primary,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _registering ? 'Open an account' : 'Sign in to your account',
                      style: text.titleMedium,
                    ),
                    const SizedBox(height: 24),
                    TextFormField(
                      controller: _username,
                      autocorrect: false,
                      textInputAction: TextInputAction.next,
                      decoration: _decoration('Username'),
                      validator: (v) => (v == null || v.trim().isEmpty)
                          ? 'Enter your username'
                          : null,
                    ),
                    if (_registering) ...[
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _name,
                        textInputAction: TextInputAction.next,
                        decoration: _decoration('Full name'),
                        validator: (v) => (v == null || v.trim().isEmpty)
                            ? 'Enter your full name'
                            : null,
                      ),
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _email,
                        autocorrect: false,
                        keyboardType: TextInputType.emailAddress,
                        textInputAction: TextInputAction.next,
                        decoration: _decoration('Email'),
                        validator: (v) =>
                            (v == null || !v.contains('@') || !v.contains('.'))
                                ? 'Enter a valid email address'
                                : null,
                      ),
                    ],
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _password,
                      obscureText: _hidePassword,
                      textInputAction: TextInputAction.done,
                      onFieldSubmitted: (_) => _busy ? null : _submit(),
                      decoration: _decoration(
                        _registering ? 'Password (at least 6 characters)' : 'Password',
                        suffix: IconButton(
                          tooltip: _hidePassword ? 'Show password' : 'Hide password',
                          icon: Icon(
                            _hidePassword ? Icons.visibility : Icons.visibility_off,
                          ),
                          onPressed: () =>
                              setState(() => _hidePassword = !_hidePassword),
                        ),
                      ),
                      validator: (v) {
                        if (v == null || v.isEmpty) {
                          return 'Enter your password';
                        }
                        if (_registering && v.length < 6) {
                          return 'Use at least 6 characters';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 24),
                    FilledButton(
                      onPressed: _busy ? null : _submit,
                      style: FilledButton.styleFrom(
                        minimumSize: const Size.fromHeight(48),
                      ),
                      child: _busy
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : Text(_registering ? 'Create account' : 'Sign in'),
                    ),
                    const SizedBox(height: 8),
                    TextButton(
                      onPressed: _busy
                          ? null
                          : () => setState(() => _registering = !_registering),
                      child: Text(
                        _registering
                            ? 'I already have an account'
                            : 'Create an account',
                      ),
                    ),
                    TextButton.icon(
                      onPressed: () => setState(() => _showServer = !_showServer),
                      icon: const Icon(Icons.settings_ethernet, size: 18),
                      label: Text(
                        _showServer ? 'Hide server address' : 'Server address',
                      ),
                    ),
                    if (_showServer) ...[
                      const SizedBox(height: 8),
                      TextFormField(
                        controller: _server,
                        autocorrect: false,
                        keyboardType: TextInputType.url,
                        decoration: _decoration('Python API address'),
                      ),
                      Align(
                        alignment: Alignment.centerLeft,
                        child: TextButton(
                          onPressed: _testConnection,
                          child: const Text('Test connection'),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
