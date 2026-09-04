import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'app.dart';
import 'config.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Supabase.initialize(
    url: HqConfig.supabaseUrl,
    publishableKey: HqConfig.supabasePublishableKey,
  );
  runApp(const HqApp());
}
