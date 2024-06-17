import 'package:flutter/material.dart';

class MyCheckBoxTile extends StatelessWidget {
  final bool value;
  final Function(bool?) onChanged;
  final String title;
  const MyCheckBoxTile(
      {super.key,
      required this.value,
      required this.onChanged,
      required this.title});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 50,
      width: 400,
      child: CheckboxListTile(
        activeColor: Theme.of(context).colorScheme.primary,
        controlAffinity: ListTileControlAffinity.leading,
        value: value,
        onChanged: (bool? newValue) {
          onChanged(newValue);
        },
        title: Text(title,
            textAlign: TextAlign.justify, style: const TextStyle(fontSize: 12)),
      ),
    );
  }
}
