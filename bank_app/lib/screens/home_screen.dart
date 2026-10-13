import 'package:flutter/material.dart';

import '../api_service.dart';
import '../format.dart';
import '../models.dart';
import '../widgets/snack.dart';
import '../widgets/statement_dialog.dart';
import '../widgets/transaction_dialog.dart';
import 'login_screen.dart';
import 'tabs.dart';

/// The screen after signing in. It loads the data from the Python API and runs
/// the deposit / withdraw / send actions; the tabs in tabs.dart just draw it.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key, required this.initialProfile});

  final UserProfile initialProfile;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _api = ApiService.instance;

  int _tab = 0;
  bool _loading = true;
  late UserProfile _profile = widget.initialProfile;
  List<BankTransaction> _transactions = [];
  AccountSummary _summary = AccountSummary.empty;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  /// Fetches balance, history and summary again from the server.
  Future<void> _refresh() async {
    try {
      final profile = await _api.getProfile();
      final transactions = await _api.getTransactions();
      final summary = await _api.getSummary();
      if (!mounted) {
        return;
      }
      setState(() {
        _profile = profile;
        _transactions = transactions;
        _summary = summary;
        _loading = false;
      });
    } on ApiException catch (e) {
      if (!mounted) {
        return;
      }
      setState(() => _loading = false);
      _handleError(e);
    }
  }

  void _handleError(ApiException e) {
    if (e.isUnauthorized) {
      showAppSnack(context, 'Your session ended. Please sign in again.', error: true);
      _goToLogin();
      return;
    }
    showAppSnack(context, e.message, error: true);
  }

  void _goToLogin() {
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  /// Runs one money action, shows its result message, then reloads the data.
  Future<void> _run(Future<String> Function() action) async {
    try {
      final message = await action();
      if (!mounted) {
        return;
      }
      showAppSnack(context, message);
      await _refresh();
    } on ApiException catch (e) {
      if (!mounted) {
        return;
      }
      _handleError(e);
    }
  }

  Future<void> _deposit() async {
    final input = await showTransactionDialog(
      context,
      title: 'Deposit',
      confirmLabel: 'Deposit',
    );
    if (input == null || !mounted) {
      return;
    }
    await _run(() async {
      final balance = await _api.deposit(input.amount);
      return 'Deposited ${formatMoney(input.amount)}. Balance is now ${formatMoney(balance)}.';
    });
  }

  Future<void> _withdraw() async {
    final input = await showTransactionDialog(
      context,
      title: 'Withdraw',
      confirmLabel: 'Withdraw',
    );
    if (input == null || !mounted) {
      return;
    }
    await _run(() async {
      final balance = await _api.withdraw(input.amount);
      return 'Withdrew ${formatMoney(input.amount)}. Balance is now ${formatMoney(balance)}.';
    });
  }

  Future<void> _send() async {
    final input = await showTransactionDialog(
      context,
      title: 'Send money',
      confirmLabel: 'Send',
      askReceiver: true,
    );
    if (input == null || input.receiver == null || !mounted) {
      return;
    }
    await _run(() async {
      final balance = await _api.transfer(input.receiver!, input.amount);
      return 'Sent ${formatMoney(input.amount)} to account ${input.receiver}. Balance is now ${formatMoney(balance)}.';
    });
  }

  Future<void> _export() async {
    try {
      final text = await _api.exportStatement();
      if (!mounted) {
        return;
      }
      await showDialog<void>(
        context: context,
        builder: (_) => StatementDialog(text: text),
      );
    } on ApiException catch (e) {
      if (!mounted) {
        return;
      }
      _handleError(e);
    }
  }

  Future<void> _logout() async {
    await _api.logout();
    if (!mounted) {
      return;
    }
    _goToLogin();
  }

  Widget _currentTab() {
    switch (_tab) {
      case 0:
        return AccountTab(
          profile: _profile,
          summary: _summary,
          recent: _transactions.take(5).toList(),
          onDeposit: _deposit,
          onWithdraw: _withdraw,
          onSend: _send,
          onSeeAll: () => setState(() => _tab = 1),
          onRefresh: _refresh,
        );
      case 1:
        return HistoryTab(transactions: _transactions, onRefresh: _refresh);
      default:
        return ProfileTab(profile: _profile, onLogout: _logout);
    }
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    const titles = ['Passbook', 'History', 'Profile'];

    return Scaffold(
      appBar: AppBar(
        title: Text(titles[_tab]),
        backgroundColor: scheme.surface,
        scrolledUnderElevation: 0,
        actions: [
          if (_tab == 1)
            IconButton(
              tooltip: 'Export statement',
              icon: const Icon(Icons.file_download_outlined),
              onPressed: _export,
            ),
          IconButton(
            tooltip: 'Refresh',
            icon: const Icon(Icons.refresh),
            onPressed: _refresh,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Align(
              alignment: Alignment.topCenter,
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 640),
                child: _currentTab(),
              ),
            ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        backgroundColor: scheme.surface,
        onDestinationSelected: (index) => setState(() => _tab = index),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.account_balance_wallet_outlined),
            selectedIcon: Icon(Icons.account_balance_wallet),
            label: 'Account',
          ),
          NavigationDestination(
            icon: Icon(Icons.receipt_long_outlined),
            selectedIcon: Icon(Icons.receipt_long),
            label: 'History',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}
