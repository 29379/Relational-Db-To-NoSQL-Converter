import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:sql_converter/global.dart';
import 'package:sql_converter/widgets/my_check_box_tile.dart';
import 'package:sql_converter/widgets/my_radio_list_tile.dart';

class Configure extends StatefulWidget {
  const Configure({super.key});

  @override
  State<Configure> createState() => _ConfigureState();
}

class _ConfigureState extends State<Configure> {
  @override
  Widget build(BuildContext context) {
    return Column(mainAxisAlignment: MainAxisAlignment.center, children: [
      Text(
        "Configuration",
        style: GoogleFonts.ibmPlexMono(fontSize: 80),
      ),
      const SizedBox(height: 20),
      const Text(
        "Show generated JSON file:",
        style: TextStyle(fontSize: 15),
      ),
      MyCheckBoxTile(
        title: "Show JSON file",
        value: viewJson,
        onChanged: (value) {
          setState(() {
            viewJson = value ?? false;
            if (relationType.contains(RelationshipType.oto)) {
              relationType.remove(RelationshipType.oto);
            }
          });
        },
      ),
      const Text(
        "Choose reference method:",
        style: TextStyle(fontSize: 15),
      ),
      MyRadioListTile(
        title: 'Reference by id',
        value: ReferencingType.id,
        groupValue: referencingType,
        onChanged: (type) {
          setState(() {
            if (type != null) {
              referencingType = type as ReferencingType;
            }
          });
        },
      ),
      MyRadioListTile(
        title: 'Reference by Object',
        value: ReferencingType.object,
        groupValue: referencingType,
        onChanged: (type) {
          setState(() {
            if (type != null) {
              referencingType = type as ReferencingType;
            }
          });
        },
      ),
      const Text(
        "Choose the relationship handling method:",
        style: TextStyle(fontSize: 15),
      ),
      MyRadioListTile(
        title: 'Table to collection',
        value: ConversionType.ttb,
        groupValue: conversionType,
        onChanged: (type) {
          setState(() {
            if (type != null) {
              conversionType = type as ConversionType;
            }
          });
        },
      ),
      MyRadioListTile(
        title: 'Smart conversion',
        value: ConversionType.smart,
        groupValue: conversionType,
        onChanged: (type) {
          setState(() {
            if (type != null) {
              conversionType = type as ConversionType;
            }
          });
        },
      ),
      if (conversionType == ConversionType.smart)
        Padding(
          padding: const EdgeInsets.only(left: 50),
          child: Column(
            children: [
              MyCheckBoxTile(
                title: "Merge tables",
                value: relationType.contains(RelationshipType.oto),
                onChanged: (value) {
                  setState(() {
                    if (relationType.contains(RelationshipType.oto)) {
                      relationType.remove(RelationshipType.oto);
                    } else {
                      relationType.add(RelationshipType.oto);
                      viewJson = false;
                    }
                  });
                },
              ),
              MyCheckBoxTile(
                title: "Delete juntion tables",
                value: relationType.contains(RelationshipType.mtm),
                onChanged: (value) {
                  setState(() {
                    if (relationType.contains(RelationshipType.mtm)) {
                      relationType.remove(RelationshipType.mtm);
                    } else {
                      relationType.add(RelationshipType.mtm);
                    }
                  });
                },
              ),
            ],
          ),
        )
      else
        const SizedBox(height: 100),
    ]);
  }
}
