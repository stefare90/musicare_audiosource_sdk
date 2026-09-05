import 'package:flutter/material.dart';

void main() {
  runApp(const PluginHarnessApp());
}

class PluginHarnessApp extends StatelessWidget {
  const PluginHarnessApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: Scaffold(
        body: Center(child: Text('MusicAre Plugin Test Harness Running...')),
      ),
    );
  }
}
