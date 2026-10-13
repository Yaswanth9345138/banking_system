import 'package:flutter/material.dart';

import '../format.dart';
import '../models.dart';
import '../theme.dart';
import '../widgets/ledger.dart';

// The three tabs of the home screen. They only draw what they are given;
// all the data loading and button actions live in home_screen.dart.

/// Tab 1: the passbook cover with the balance, the summary and the latest entries.
class AccountTab extends StatelessWidget {
  const AccountTab({
    super.key,
    required this.profile,
    required this.summary,
    required this.recent,
    required this.onDeposit,
    required this.onWithdraw,
    required this.onSend,
    required this.onSeeAll,
    required this.onRefresh,
  });

  final UserProfile profile;
  final AccountSummary summary;
  final List<BankTransaction> recent;
  final VoidCallback onDeposit;
  final VoidCallback onWithdraw;
  final VoidCallback onSend;
  final VoidCallback onSeeAll;
  final Future<void> Function() onRefresh;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    final muted = Theme.of(context).colorScheme.onSurfaceVariant;
    final credit = AppColors.credit(context);
    final debit = AppColors.debit(context);

    return RefreshIndicator(
      onRefresh: onRefresh,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
        children: [
          _Cover(
            profile: profile,
            onDeposit: onDeposit,
            onWithdraw: onWithdraw,
            onSend: onSend,
          ),
          const SizedBox(height: 28),
          Text('This account so far', style: text.titleMedium),
          LedgerRow(
            label: 'Deposits',
            value: formatMoney(summary.totalDeposits),
            valueColor: credit,
          ),
          const Divider(height: 1),
          LedgerRow(
            label: 'Money received',
            value: formatMoney(summary.totalReceived),
            valueColor: credit,
          ),
          const Divider(height: 1),
          LedgerRow(
            label: 'Withdrawals',
            value: formatMoney(summary.totalWithdrawals),
            valueColor: debit,
          ),
          const Divider(height: 1),
          LedgerRow(
            label: 'Money sent',
            value: formatMoney(summary.totalSent),
            valueColor: debit,
          ),
          const SizedBox(height: 28),
          Row(
            children: [
              Expanded(child: Text('Latest entries', style: text.titleMedium)),
              if (recent.isNotEmpty)
                TextButton(onPressed: onSeeAll, child: const Text('See all')),
            ],
          ),
          if (recent.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 16),
              child: Text(
                'No entries yet. Make a deposit and it will show up here.',
                style: text.bodyMedium?.copyWith(color: muted),
              ),
            )
          else
            for (final transaction in recent) ...[
              TransactionRow(transaction: transaction),
              const Divider(height: 1),
            ],
        ],
      ),
    );
  }
}

/// The ink-blue "cover": holder name, account number stamp, balance and the three actions.
class _Cover extends StatelessWidget {
  const _Cover({
    required this.profile,
    required this.onDeposit,
    required this.onWithdraw,
    required this.onSend,
  });

  final UserProfile profile;
  final VoidCallback onDeposit;
  final VoidCallback onWithdraw;
  final VoidCallback onSend;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;

    final buttonStyle = OutlinedButton.styleFrom(
      foregroundColor: Colors.white,
      side: const BorderSide(color: Colors.white54),
    );

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.ink,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  profile.name,
                  overflow: TextOverflow.ellipsis,
                  style: text.titleMedium?.copyWith(color: Colors.white),
                ),
              ),
              const SizedBox(width: 12),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  border: Border.all(color: AppColors.brass),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  'A/c ${profile.accountNumber}',
                  style: tabularFigures(
                    text.bodyMedium?.copyWith(
                      color: AppColors.brass,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Text(
            'Balance',
            style: text.bodyMedium?.copyWith(color: Colors.white70),
          ),
          const SizedBox(height: 2),
          FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerLeft,
            child: Text(
              formatMoney(profile.balance),
              style: tabularFigures(
                text.displaySmall?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
          const SizedBox(height: 20),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              OutlinedButton.icon(
                onPressed: onDeposit,
                style: buttonStyle,
                icon: const Icon(Icons.add_circle_outline, size: 18),
                label: const Text('Deposit'),
              ),
              OutlinedButton.icon(
                onPressed: onWithdraw,
                style: buttonStyle,
                icon: const Icon(Icons.remove_circle_outline, size: 18),
                label: const Text('Withdraw'),
              ),
              OutlinedButton.icon(
                onPressed: onSend,
                style: buttonStyle,
                icon: const Icon(Icons.north_east, size: 18),
                label: const Text('Send money'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

/// Tab 2: every transaction, newest first.
class HistoryTab extends StatelessWidget {
  const HistoryTab({
    super.key,
    required this.transactions,
    required this.onRefresh,
  });

  final List<BankTransaction> transactions;
  final Future<void> Function() onRefresh;

  @override
  Widget build(BuildContext context) {
    if (transactions.isEmpty) {
      final muted = Theme.of(context).colorScheme.onSurfaceVariant;
      return RefreshIndicator(
        onRefresh: onRefresh,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          children: [
            Text(
              'No entries yet. Deposits, withdrawals and transfers appear here.',
              style: Theme.of(context)
                  .textTheme
                  .bodyMedium
                  ?.copyWith(color: muted),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: onRefresh,
      child: ListView.separated(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
        itemCount: transactions.length,
        separatorBuilder: (_, __) => const Divider(height: 1),
        itemBuilder: (context, index) =>
            TransactionRow(transaction: transactions[index]),
      ),
    );
  }
}

/// Tab 3: who is signed in, and the log out button.
class ProfileTab extends StatelessWidget {
  const ProfileTab({super.key, required this.profile, required this.onLogout});

  final UserProfile profile;
  final VoidCallback onLogout;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
      children: [
        LedgerRow(label: 'Name', value: profile.name),
        const Divider(height: 1),
        LedgerRow(label: 'Username', value: profile.username),
        const Divider(height: 1),
        LedgerRow(label: 'Email', value: profile.email),
        const Divider(height: 1),
        LedgerRow(label: 'Account number', value: '${profile.accountNumber}'),
        const SizedBox(height: 24),
        Align(
          alignment: Alignment.centerLeft,
          child: OutlinedButton.icon(
            onPressed: onLogout,
            icon: const Icon(Icons.logout, size: 18),
            label: const Text('Log out'),
          ),
        ),
      ],
    );
  }
}
