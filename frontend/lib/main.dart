import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:sql_converter/convert/convert_main.dart';
import 'package:sql_converter/widgets/round_button.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SQL to NoSQL Converter',
      debugShowCheckedModeBanner: false,
      darkTheme: ThemeData(
        scaffoldBackgroundColor: const Color(0xFF180e2c),
        dialogBackgroundColor: const Color(0xFF180e2c),
        brightness: Brightness.dark,
        useMaterial3: true,
        colorSchemeSeed: Colors.indigo,
        fontFamily: 'Poppins',
      ),
      home: const MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              "SQL Converter",
              style: GoogleFonts.ibmPlexMono(fontSize: 100),
            ),
            RoundButton(
              height: 60,
              onPressed: () => Navigator.of(context).push(
                  MaterialPageRoute(builder: (context) => const ConvertMain())),
              title: "GET STARTED",
              textColor: Theme.of(context).scaffoldBackgroundColor,
            ),
          ],
        ),
      ),
    );
  }
}
