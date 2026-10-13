// Plain data classes that mirror the JSON sent by the Python API (api.py).
//
// Money is kept as a String (for example "1500.00") exactly as the server sends it,
// so the app never does floating-point maths on balances.

class UserProfile {
  const UserProfile({
    required this.username,
    required this.name,
    required this.email,
    required this.accountNumber,
    required this.balance,
  });

  final String username;
  final String name;
  final String email;
  final int accountNumber;
  final String balance;

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      username: json['username'].toString(),
      name: json['name'].toString(),
      email: json['email'].toString(),
      accountNumber: (json['account_number'] as num).toInt(),
      balance: json['balance'].toString(),
    );
  }
}

class BankTransaction {
  const BankTransaction({
    required this.id,
    required this.type,
    required this.amount,
    required this.description,
    required this.date,
  });

  final int id;
  final String type; // DEPOSIT, WITHDRAW, TRANSFER_SENT or TRANSFER_RECEIVED
  final String amount;
  final String description;
  final String date;

  factory BankTransaction.fromJson(Map<String, dynamic> json) {
    return BankTransaction(
      id: (json['transaction_id'] as num).toInt(),
      type: json['transaction_type'].toString(),
      amount: json['amount'].toString(),
      description: (json['description'] ?? '').toString(),
      date: json['transaction_date'].toString(),
    );
  }

  /// True when money came IN to the account.
  bool get isCredit => type == 'DEPOSIT' || type == 'TRANSFER_RECEIVED';

  String get title {
    return switch (type) {
      'DEPOSIT' => 'Deposit',
      'WITHDRAW' => 'Withdrawal',
      'TRANSFER_SENT' => 'Money sent',
      'TRANSFER_RECEIVED' => 'Money received',
      _ => type,
    };
  }
}

class AccountSummary {
  const AccountSummary({
    required this.totalDeposits,
    required this.totalWithdrawals,
    required this.totalSent,
    required this.totalReceived,
  });

  static const empty = AccountSummary(
    totalDeposits: '0',
    totalWithdrawals: '0',
    totalSent: '0',
    totalReceived: '0',
  );

  final String totalDeposits;
  final String totalWithdrawals;
  final String totalSent;
  final String totalReceived;

  factory AccountSummary.fromJson(Map<String, dynamic> json) {
    return AccountSummary(
      totalDeposits: json['total_deposits'].toString(),
      totalWithdrawals: json['total_withdrawals'].toString(),
      totalSent: json['total_sent'].toString(),
      totalReceived: json['total_received'].toString(),
    );
  }
}
