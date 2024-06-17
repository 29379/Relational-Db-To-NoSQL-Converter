import 'dart:convert';

enum RelationshipType { oto, mtm }

enum ReferencingType { id, object }

enum ConversionType { ttb, smart }

bool viewJson = false;

ConversionType conversionType = ConversionType.ttb;

ReferencingType referencingType = ReferencingType.id;

List<RelationshipType> relationType = [RelationshipType.oto];

String getPrettyJSONString(jsonObject) {
  var encoder = const JsonEncoder.withIndent("     ");
  return encoder.convert(jsonObject);
}
