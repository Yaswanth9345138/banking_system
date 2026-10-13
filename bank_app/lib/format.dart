// Small helpers that turn the server's raw text into what the user sees.

/// "1234567.5" -> "₹12,34,567.50"  (Indian digit grouping, always 2 decimals).
String formatMoney(String raw) {
  var text = raw.trim();
  var sign = '';
  if (text.startsWith('-')) {
    sign = '-';
    text = text.substring(1);
  }

  final parts = text.split('.');
  var whole = parts[0].isEmpty ? '0' : parts[0];
  final decimals = parts.length > 1 ? parts[1] : '';
  final fraction = '${decimals}00'.substring(0, 2); // pad or cut to exactly 2 digits

  if (whole.length > 3) {
    // last three digits stay together, everything before them goes in pairs
    final lastThree = whole.substring(whole.length - 3);
    var rest = whole.substring(0, whole.length - 3);
    final groups = <String>[];
    while (rest.length > 2) {
      groups.insert(0, rest.substring(rest.length - 2));
      rest = rest.substring(0, rest.length - 2);
    }
    if (rest.isNotEmpty) {
      groups.insert(0, rest);
    }
    whole = '${groups.join(',')},$lastThree';
  }

  return '$sign₹$whole.$fraction';
}

/// "2026-10-12T10:43:00" -> "12 Oct 2026, 10:43 AM"
String formatDate(String raw) {
  final date = DateTime.tryParse(raw);
  if (date == null) {
    return raw;
  }

  const months = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
  ];

  final hour = date.hour % 12 == 0 ? 12 : date.hour % 12;
  final minute = date.minute.toString().padLeft(2, '0');
  final period = date.hour >= 12 ? 'PM' : 'AM';

  return '${date.day} ${months[date.month - 1]} ${date.year}, $hour:$minute $period';
}
