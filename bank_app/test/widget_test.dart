import 'package:bank_app/format.dart';
import 'package:bank_app/models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('formatMoney', () {
    test('uses Indian digit grouping', () {
      expect(formatMoney('1234567.5'), '₹12,34,567.50');
      expect(formatMoney('100000.00'), '₹1,00,000.00');
      expect(formatMoney('1234'), '₹1,234.00');
    });

    test('always shows two decimals', () {
      expect(formatMoney('100'), '₹100.00');
      expect(formatMoney('0'), '₹0.00');
      expect(formatMoney('99.5'), '₹99.50');
    });
  });

  group('formatDate', () {
    test('formats an ISO timestamp from the API', () {
      expect(formatDate('2026-10-12T10:43:00'), '12 Oct 2026, 10:43 AM');
      expect(formatDate('2026-10-12T00:05:00'), '12 Oct 2026, 12:05 AM');
      expect(formatDate('2026-10-12T15:30:00'), '12 Oct 2026, 3:30 PM');
    });
  });

  group('BankTransaction', () {
    test('parses the API JSON and knows money in from money out', () {
      final deposit = BankTransaction.fromJson({
        'transaction_id': 7,
        'transaction_type': 'DEPOSIT',
        'amount': '500.00',
        'description': 'Money deposited',
        'transaction_date': '2026-10-12T10:43:00',
      });
      expect(deposit.id, 7);
      expect(deposit.isCredit, isTrue);
      expect(deposit.title, 'Deposit');

      final sent = BankTransaction.fromJson({
        'transaction_id': 8,
        'transaction_type': 'TRANSFER_SENT',
        'amount': '200.00',
        'description': 'Transferred to account 1001',
        'transaction_date': '2026-10-12T10:44:00',
      });
      expect(sent.isCredit, isFalse);
      expect(sent.title, 'Money sent');
    });
  });
}
