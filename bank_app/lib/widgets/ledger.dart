import 'dart:ui' show FontFeature;

import 'package:flutter/material.dart';

import '../format.dart';
import '../models.dart';
import '../theme.dart';

/// Figures with equal-width digits, so amounts line up like entries in a ledger.
TextStyle? tabularFigures(TextStyle? style) {
  return style?.copyWith(fontFeatures: const [FontFeature.tabularFigures()]);
}

/// One line of the passbook: a label (with optional small print under it) on the
/// left and a figure on the right.
class LedgerRow extends StatelessWidget {
  const LedgerRow({
    super.key,
    required this.label,
    required this.value,
    this.detail,
    this.valueColor,
  });

  final String label;
  final String value;
  final String? detail;
  final Color? valueColor;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    final muted = Theme.of(context).colorScheme.onSurfaceVariant;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            flex: 3,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: text.bodyLarge),
                if (detail != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 2),
                    child: Text(
                      detail!,
                      style: text.bodySmall?.copyWith(color: muted),
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          Flexible(
            flex: 2,
            child: Text(
              value,
              textAlign: TextAlign.right,
              style: tabularFigures(
                text.bodyLarge?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: valueColor,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// A [LedgerRow] filled in from one transaction: green "+" for money in,
/// red "−" for money out.
class TransactionRow extends StatelessWidget {
  const TransactionRow({super.key, required this.transaction});

  final BankTransaction transaction;

  @override
  Widget build(BuildContext context) {
    final credit = transaction.isCredit;
    final sign = credit ? '+' : '\u2212';

    return LedgerRow(
      label: transaction.title,
      detail: '${transaction.description}\n${formatDate(transaction.date)}',
      value: '$sign${formatMoney(transaction.amount)}',
      valueColor: credit ? AppColors.credit(context) : AppColors.debit(context),
    );
  }
}
