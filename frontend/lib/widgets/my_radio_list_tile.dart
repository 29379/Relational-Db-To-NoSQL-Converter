import 'package:flutter/material.dart';

class MyRadioListTile extends StatelessWidget {
  final Object value;
  final Function(Object?) onChanged;
  final String title;
  final Object groupValue;
  const MyRadioListTile(
      {super.key,
      required this.value,
      required this.onChanged,
      required this.title,
      required this.groupValue});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 50,
      width: 400,
      child: RadioListTile(
        activeColor: Theme.of(context).colorScheme.primary,
        controlAffinity: ListTileControlAffinity.leading,
        value: value,
        groupValue: groupValue,
        onChanged: (newValue) {
          onChanged(newValue);
        },
        title: Text(title,
            textAlign: TextAlign.justify, style: const TextStyle(fontSize: 12)),
      ),
    );
  }
}
