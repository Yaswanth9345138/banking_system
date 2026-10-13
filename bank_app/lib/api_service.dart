import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import 'models.dart';

/// Thrown whenever the server (or the network) says no. `message` is safe to show the user.
class ApiException implements Exception {
  ApiException(this.message, [this.statusCode]);

  final String message;
  final int? statusCode;

  bool get isUnauthorized => statusCode == 401;

  @override
  String toString() => message;
}

/// The only class that talks to the Python API (api.py).
/// Every screen calls these methods; none of them builds an HTTP request itself.
class ApiService {
  ApiService._();

  static final ApiService instance = ApiService._();

  String baseUrl = _defaultBaseUrl();
  String? _token;

  /// The Android emulator reaches the computer running Python at 10.0.2.2.
  /// Chrome, Windows, Linux and macOS use 127.0.0.1.
  static String _defaultBaseUrl() {
    if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
      return 'http://10.0.2.2:8000';
    }
    return 'http://127.0.0.1:8000';
  }

  void setBaseUrl(String value) {
    var url = value.trim();
    if (url.isEmpty) {
      return;
    }
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'http://$url';
    }
    while (url.endsWith('/')) {
      url = url.substring(0, url.length - 1);
    }
    baseUrl = url;
  }

  // ---------- low-level helpers ----------

  Uri _uri(String path) => Uri.parse('$baseUrl$path');

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_token != null) 'Authorization': 'Bearer $_token',
      };

  Future<http.Response> _send(Future<http.Response> Function() request) async {
    try {
      final response = await request().timeout(const Duration(seconds: 10));

      if (response.statusCode >= 200 && response.statusCode < 300) {
        return response;
      }
      throw ApiException(_errorMessage(response), response.statusCode);
    } on ApiException {
      rethrow;
    } on TimeoutException {
      throw ApiException(
        'The server took too long to answer. Is the Python API running?',
      );
    } catch (_) {
      throw ApiException(
        'Cannot reach the server at $baseUrl. Start the API with '
        '"uvicorn api:app" and check the server address.',
      );
    }
  }

  String _errorMessage(http.Response response) {
    try {
      final body = jsonDecode(utf8.decode(response.bodyBytes));
      if (body is Map) {
        final detail = body['detail'];
        if (detail is String) {
          return detail;
        }
        if (detail is List && detail.isNotEmpty) {
          final first = detail.first;
          if (first is Map && first['msg'] is String) {
            return 'Invalid input: ${first['msg']}';
          }
        }
      }
    } catch (_) {
      // body was not JSON; fall through to the generic message
    }
    return 'The server returned an error (HTTP ${response.statusCode}).';
  }

  dynamic _decode(http.Response response) {
    return jsonDecode(utf8.decode(response.bodyBytes));
  }

  Future<dynamic> _get(String path) async {
    final response = await _send(() => http.get(_uri(path), headers: _headers));
    return _decode(response);
  }

  Future<dynamic> _post(String path, [Map<String, dynamic>? body]) async {
    final response = await _send(
      () => http.post(_uri(path), headers: _headers, body: jsonEncode(body ?? {})),
    );
    return _decode(response);
  }

  // ---------- connection ----------

  /// Throws an [ApiException] if the Python API cannot be reached.
  Future<void> ping() async {
    await _get('/');
  }

  // ---------- authentication ----------

  /// Returns the new account number.
  Future<int> register({
    required String username,
    required String name,
    required String email,
    required String password,
  }) async {
    final body = await _post('/register', {
      'username': username,
      'name': name,
      'email': email,
      'password': password,
    });
    return (body['account_number'] as num).toInt();
  }

  Future<UserProfile> login(String username, String password) async {
    final body = await _post('/login', {
      'username': username,
      'password': password,
    });
    _token = body['token'] as String;
    return getProfile();
  }

  Future<void> logout() async {
    try {
      await _post('/logout');
    } on ApiException {
      // the session was already gone; nothing more to do
    }
    _token = null;
  }

  // ---------- account ----------

  Future<UserProfile> getProfile() async {
    final body = await _get('/profile');
    return UserProfile.fromJson(body as Map<String, dynamic>);
  }

  Future<List<BankTransaction>> getTransactions() async {
    final body = await _get('/transactions');
    final list = body['transactions'] as List;
    return list
        .map((item) => BankTransaction.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<AccountSummary> getSummary() async {
    final body = await _get('/summary');
    return AccountSummary.fromJson(body as Map<String, dynamic>);
  }

  // ---------- money ----------
  // Amounts travel as text ("250.50") so no precision is lost on the way.
  // Each method returns the new balance reported by the server.

  Future<String> deposit(String amount) async {
    final body = await _post('/deposit', {'amount': amount});
    return body['balance'].toString();
  }

  Future<String> withdraw(String amount) async {
    final body = await _post('/withdraw', {'amount': amount});
    return body['balance'].toString();
  }

  Future<String> transfer(int receiverAccount, String amount) async {
    final body = await _post('/transfer', {
      'receiver_account': receiverAccount,
      'amount': amount,
    });
    return body['balance'].toString();
  }

  /// The server writes the statement to a .txt file and sends it back; we show its text.
  Future<String> exportStatement() async {
    final response = await _send(
      () => http.get(_uri('/export'), headers: _headers),
    );
    return utf8.decode(response.bodyBytes);
  }
}
