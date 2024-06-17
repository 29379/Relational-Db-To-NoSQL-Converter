// ignore_for_file: use_build_context_synchronously

import 'package:flutter/material.dart';
import 'package:sql_converter/global.dart';
import 'package:sql_converter/services/converter_service.dart';
import 'package:sql_converter/widgets/main_switch.dart';
import 'package:sql_converter/widgets/message.dart';
import 'package:sql_converter/widgets/my_radio_list_tile.dart';
import 'package:sql_converter/widgets/round_button.dart';

class Convert extends StatefulWidget {
  const Convert({super.key});

  @override
  State<Convert> createState() => _ConvertState();
}

class _ConvertState extends State<Convert> {
  TextEditingController jsonFile = TextEditingController();
  bool isJsonFilled = false;
  bool isLoading = false;
  List choices = [];
  List chosenTable = [];

  Map originalJson = {};
  Map controllers = {};
  bool isEdit = false;

  bool showConvertButton() {
    return (!isLoading && choices.isEmpty);
  }

  bool showIndicator() {
    return (choices.isEmpty && !isJsonFilled);
  }

  bool showChoices() {
    return choices.isNotEmpty;
  }

  bool checkIfConfigurationIsNotValid() {
    return conversionType == ConversionType.smart && relationType.isEmpty;
  }

  bool showJsonWindow() {
    return (isJsonFilled && viewJson);
  }

  handleManyToManyRealtions() async {
    try {
      setState(() {
        chosenTable = [];
      });
      choices = await ConverterService().getRelationshipDetails();
      for (int i = 0; i < choices.length; i++) {
        chosenTable.add({
          'junction': choices[i]['junction'],
          'table': choices[i]['tables'][0]
        });
      }
    } catch (e) {
      message(context, 'Failure', "An error occurred");
    }

    setState(() {
      isLoading = false;
    });
  }

  handleRelations({List? userChoicesForManyToMany}) async {
    try {
      var res = await ConverterService()
          .handleRelations(userChoicesForManyToMany: userChoicesForManyToMany);
      if (res['success']) {
        message(context, 'Success', res['message'], 'success');
      } else {
        message(context, 'Failure', res['message']);
      }
    } catch (e) {
      message(context, 'Failure', "An error occurred");
    }
    setState(() {
      isLoading = false;
      choices = [];
    });
  }

  viewAndEditJson() async {
    if (viewJson) {
      var res = await ConverterService().viewJson();

      originalJson = res;
      jsonFile.text = getPrettyJSONString(originalJson).toString();

      originalJson.forEach((key, value) {
        if (value is List) {
          for (var field in value) {
            if (field is Map && field.containsKey('column_name')) {
              String controllerKey = '$key-${field['column_name']}';
              controllers[controllerKey] =
                  TextEditingController(text: field['column_name']);
            }
          }
        }
      });

      setState(() {
        isJsonFilled = true;
      });
    } else {
      realtions();
    }
  }

  Map detectChanges() {
    Map changes = {};
    originalJson.forEach((table, fields) {
      if (table != "relationships") {
        List<Map> tableChanges = [];
        fields.asMap().forEach((index, originalField) {
          if (originalField.containsKey('column_name')) {
            String controllerKey = '$table-${originalField['column_name']}';
            TextEditingController? controller = controllers[controllerKey];
            if (controller != null &&
                originalField['column_name'] != controller.text) {
              tableChanges.add({
                'old': originalField['column_name'],
                'new': controller.text
              });
            }
          }
        });
        if (tableChanges.isNotEmpty) {
          changes[table] = tableChanges;
        }
      }
    });
    return changes;
  }

  handleJsonFile() async {
    try {
      await ConverterService().sqlToJson();
      viewAndEditJson();
    } catch (e) {
      message(context, 'Failure', "An error occurred");
      return;
    }
  }

  realtions() {
    if (conversionType == ConversionType.smart &&
        (relationType.contains(RelationshipType.mtm) &&
            !relationType.contains(RelationshipType.oto))) {
      handleManyToManyRealtions();
    } else {
      if (relationType.contains(RelationshipType.mtm)) {
        setState(() {
          chosenTable = [];
          chosenTable = [
            {'junction': 'route_app_user', 'table': 'app_user'},
            {'junction': 'route_stop', 'table': 'stop'}
          ];
        });
      }
      handleRelations(userChoicesForManyToMany: chosenTable);
    }
  }

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Stack(
          children: [
            if (showConvertButton())
              RoundButton(
                  height: 60,
                  title: 'CONVERT',
                  textColor: Theme.of(context).scaffoldBackgroundColor,
                  onPressed: () async {
                    setState(() {
                      isLoading = true;
                    });

                    if (checkIfConfigurationIsNotValid()) {
                      message(context, 'Failure',
                          'Choose at least one relation type.');
                      return;
                    }

                    handleJsonFile();
                  })
            else if (showIndicator())
              const CircularProgressIndicator()
            else if (showJsonWindow())
              showJsonContainer(size)
            else if (showChoices())
              showManyToManyChoices()
          ],
        ),
      ],
    );
  }

  Widget showManyToManyChoices() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        for (int i = 0; i < choices.length; i++)
          Column(
            children: [
              Text(
                "Relation between ${choices[i]['junction']} and embed into:",
                style: const TextStyle(fontSize: 15),
              ),
              ...choices[i]['tables']
                  .map((table) => MyRadioListTile(
                        title: table,
                        value: table,
                        groupValue: chosenTable[i]['table'],
                        onChanged: (newValue) {
                          if (newValue != null) {
                            setState(() {
                              chosenTable[i]['table'] = newValue;
                            });
                          }
                        },
                      ))
                  .toList(),
            ],
          ),
        RoundButton(
          height: 60,
          title: "CONFIRM",
          textColor: Theme.of(context).scaffoldBackgroundColor,
          onPressed: () async {
            setState(() {
              isLoading = true;
              choices = [];
            });

            try {
              var res = await ConverterService()
                  .handleRelations(userChoicesForManyToMany: chosenTable);
              if (res['success']) {
                message(context, 'Success', res['message'], 'success');
              } else {
                message(context, 'Failure', res['message']);
              }
            } catch (e) {
              message(context, 'Failure', "An error occurred");
            }

            setState(() {
              isLoading = false;
              chosenTable = [];
            });
          },
        ),
      ],
    );
  }

  Widget showJsonContainer(Size size) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 5.0),
          child: SizedBox(
            width: 450,
            child: MainSwitch(
                current: isEdit,
                firstTitle: 'CHANGE TO EDIT VIEW',
                secondTitle: 'CHANGE TO ORIGINAL PREVIEW',
                firstIconData: Icons.edit,
                secondIconData: Icons.remove_red_eye,
                onChanged: (value) => setState(
                      () => isEdit = value,
                    )),
          ),
        ),
        if (isEdit)
          SizedBox(
            width: 600,
            height: size.height - 140,
            child: ListView(
              children: originalJson.keys
                  .where((key) => key != "relationships")
                  .map((table) {
                return ExpansionTile(
                  title: Text(table),
                  children: (originalJson[table] as List)
                      .where((field) => (field['column_name'] != null &&
                          field['column_name'] != 'id'))
                      .map((field) {
                    String controllerKey = '$table-${field['column_name']}';
                    return ListTile(
                      title: TextFormField(
                        controller: controllers[controllerKey],
                        decoration:
                            const InputDecoration(labelText: "Column Name"),
                      ),
                    );
                  }).toList(),
                );
              }).toList(),
            ),
          )
        else
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
            child: Container(
              constraints: BoxConstraints(maxHeight: size.height - 160),
              decoration: BoxDecoration(
                  border: Border.all(color: Colors.white),
                  borderRadius: BorderRadius.circular(10)),
              child: SingleChildScrollView(
                child: TextField(
                  controller: jsonFile,
                  maxLines: null,
                  readOnly: true,
                ),
              ),
            ),
          ),
        Padding(
          padding: const EdgeInsets.only(bottom: 10),
          child: RoundButton(
              height: 60,
              title: "CONFIRM",
              textColor: Theme.of(context).scaffoldBackgroundColor,
              onPressed: () async {
                Map jsonChanges = detectChanges();

                await ConverterService().sendChangedJson(jsonChanges);

                setState(() {
                  isJsonFilled = false;
                });
                realtions();
              }),
        ),
      ],
    );
  }
}
