// ignore_for_file: use_build_context_synchronously

import 'package:flutter/material.dart';
import 'package:sql_converter/convert/configure.dart';
import 'package:sql_converter/convert/convert.dart';
import 'package:sql_converter/services/converter_service.dart';

class ConvertMain extends StatefulWidget {
  const ConvertMain({super.key});

  @override
  State<ConvertMain> createState() => _ConvertMainState();
}

class _ConvertMainState extends State<ConvertMain> {
  showImageDialog(String url) {
    return showDialog(
        context: context,
        builder: (context) => AlertDialog(
              contentPadding: EdgeInsets.zero,
              content: Image.network(url),
            ));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: const Center(
        child: IntrinsicHeight(
          child: Row(
            children: [
              Expanded(child: Configure()),
              VerticalDivider(
                indent: 10,
                endIndent: 10,
                color: Colors.white,
              ),
              Expanded(child: Convert()),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        tooltip: "View ERD diagram",
        backgroundColor: Theme.of(context).colorScheme.primary,
        onPressed: () async {
          String? url = await ConverterService().generateErd();
          if (url != null) showImageDialog(url);
        },
        child: Icon(
          Icons.image,
          color: Theme.of(context).scaffoldBackgroundColor,
        ),
      ),
    );
  }
}
