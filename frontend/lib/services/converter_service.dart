// ignore_for_file: avoid_web_libraries_in_flutter

import 'dart:async';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:sql_converter/global.dart';
import 'dart:html' as html;
import 'network_service.dart';
import 'dart:convert';

class ConverterService {
  final String _urlPrefix = NetworkService.getApiUrl();

  Map<String, String> headers = <String, String>{
    'Content-Type': 'application/json; charset=UTF-8',
  };

  Future<String?> generateErd() async {
    var response = await http.get(Uri.parse('$_urlPrefix/generate-erd'));
    if (response.statusCode == 200) {
      Uint8List imageData = response.bodyBytes;
      String mimeType = "image/png";

      final blob = html.Blob([imageData], mimeType);
      final url = html.Url.createObjectUrlFromBlob(blob);

      return url;
    }

    return null;
  }

  Future sqlToJson() async {
    var response =
        await http.get(Uri.parse('$_urlPrefix/sql-to-json'), headers: headers);

    return json.decode(response.body);
  }

  Future viewJson() async {
    var response =
        await http.get(Uri.parse('$_urlPrefix/view-json'), headers: headers);

    return json.decode(response.body);
  }

  Future sendChangedJson(Map changes) async {
    await http.post(
      Uri.parse('$_urlPrefix/update-json'),
      headers: headers,
      body: json.encode(changes),
    );
  }

  Future getRelationshipDetails() async {
    var response = await http.get(
        Uri.parse('$_urlPrefix/get-relationship-details'),
        headers: headers);

    return json.decode(response.body);
  }

  Future handleRelations({List? userChoicesForManyToMany}) async {
    String referencingTypeString = referencingType.toString();
    String conversionTypetring = conversionType.toString();
    List<String> relationTypeString = [];
    for (var type in relationType) {
      relationTypeString.add(type.toString());
    }

    Map<String, dynamic> body = {
      'relationType': relationTypeString,
      'referencingType': referencingTypeString,
      'conversionType': conversionTypetring,
      'userChoices': userChoicesForManyToMany,
    };

    var response = await http.post(Uri.parse('$_urlPrefix/handle-relationship'),
        headers: headers, body: jsonEncode(body));

    return json.decode(response.body);
  }
}
