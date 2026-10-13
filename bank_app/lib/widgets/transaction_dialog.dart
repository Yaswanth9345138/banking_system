import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// What the user typed into the dialog.
class TransactionInput {
  const TransactionInput({required this.amount, this.receiver});

  final String amount;
  final int? receiver; // only filled in for "Send money"
}

/// Opens the amount dialog. Returns null if the user cancels.
/// Pass [askReceiver] to also ask for the other account number.
Future<TransactionInput?> showTransactionDialog(
  BuildContext context, {
  required String title,
  required String confirmLabel,
  bool askReceiver = false,
}) {
  return showDialog<TransactionInput>(
    context: context,
    builder: (_) => _TransactionDialog(
      title: title,
      confirmLabel: confirmLabel,
      askReceiver: askReceiver,
    ),
  );
}

class _TransactionDialog extends StatefulWidget {
  const _TransactionDialog({
    required this.title,
    required this.confirmLabel,
    required this.askReceiver,
  });

  final String title;
  final String confirmLabel;
  final bool askReceiver;

  @override
  State<_TransactionDialog> createState() => _TransactionDialogState();
}

class _TransactionDialogState extends State<_TransactionDialog> {
  final _formKey = GlobalKey<FormState>();
  final _amount = TextEditingController();
  final _receiver = TextEditingController();

  @override
  void dispose() {
    _amount.dispose();
    _receiver.dispose();
    super.dispose();
  }

  String? _validateAmount(String? value) {
    final text = (value ?? '').trim();
    if (!RegExp(r'^\d{1,8}(\.\d{1,2})?$').hasMatch(text)) {
      return 'Enter an amount like 500 or 249.50';
    }
    if (double.parse(text) <= 0) {
      return 'Amount must be more than zero';
    }
    return null;
  }

  String? _validateReceiver(String? value) {
    if (!RegExp(r'^\d{1,9}$').hasMatch((value ?? '').trim())) {
      return 'Enter the receiver\'s account number';
    }
    return null;
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    Navigator.of(context).pop(
      TransactionInput(
        amount: _amount.text.trim(),
        receiver: widget.askReceiver ? int.parse(_receiver.text.trim()) : null,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.title),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (widget.askReceiver) ...[
              TextFormField(
                controller: _receiver,
                autofocus: true,
                keyboardType: TextInputType.number,
                inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                textInputAction: TextInputAction.next,
                decoration: const InputDecoration(
                  labelText: 'Receiver account number',
                  border: OutlineInputBorder(),
                ),
                validator: _validateReceiver,
              ),
              const SizedBox(height: 16),
            ],
            TextFormField(
              controller: _amount,
              autofocus: !widget.askReceiver,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              inputFormatters: [
                FilteringTextInputFormatter.allow(RegExp(r'[0-9.]')),
              ],
              decoration: const InputDecoration(
                labelText: 'Amount',
                prefixText: '₹ ',
                border: OutlineInputBorder(),
              ),
              validator: _validateAmount,
              onFieldSubmitted: (_) => _submit(),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: _submit,
          child: Text(widget.confirmLabel),
        ),
      ],
    );
  }
}
