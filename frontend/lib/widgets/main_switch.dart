import 'package:animated_toggle_switch/animated_toggle_switch.dart';
import 'package:flutter/material.dart';

class MainSwitch extends StatefulWidget {
  final bool current;
  final String firstTitle;
  final String secondTitle;
  final IconData firstIconData;
  final IconData secondIconData;
  final Function(bool) onChanged;
  const MainSwitch(
      {super.key,
      required this.current,
      required this.firstTitle,
      required this.secondTitle,
      required this.firstIconData,
      required this.secondIconData,
      required this.onChanged});

  @override
  State<MainSwitch> createState() => _MainSwitchState();
}

class _MainSwitchState extends State<MainSwitch> {
  late bool current;

  @override
  void initState() {
    current = widget.current;
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedToggleSwitch<bool>.dual(
      current: current,
      first: true,
      second: false,
      borderColor: Colors.white,
      borderRadius: BorderRadius.circular(5),
      borderWidth: 1,
      height: 40,
      indicatorBorderRadius: BorderRadius.circular(0),
      onChanged: (b) {
        setState(() {
          current = b;
        });
        widget.onChanged(current);
      },
      onTap: () {
        setState(() {
          current = !current;
        });
        widget.onChanged(current);
      },
      colorBuilder: (b) => Theme.of(context).colorScheme.secondary,
      iconBuilder: (value) => !value
          ? Icon(
              widget.firstIconData,
              color: Colors.white,
              size: 24,
            )
          : Icon(
              widget.secondIconData,
              color: Colors.white,
              size: 24,
            ),
      textBuilder: (value) => !value
          ? Center(
              child: Text(
              widget.firstTitle,
              style: const TextStyle(fontSize: 14),
            ))
          : Center(
              child: Text(
              widget.secondTitle,
              style: const TextStyle(fontSize: 14),
            )),
    );
  }
}
