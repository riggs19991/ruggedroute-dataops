import 'dart:async';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'config.dart';
import 'data/hq.dart';
import 'features/auth/sign_in_screen.dart';
import 'features/home/home_screen.dart';
import 'features/profile/profile_screen.dart';
import 'features/settings/settings_screen.dart';

/// Notifies the router whenever the auth session changes.
class AuthListenable extends ChangeNotifier {
  AuthListenable() {
    _sub = Hq.instance.auth.onAuthStateChange.listen((_) => notifyListeners());
  }
  late final StreamSubscription<AuthState> _sub;
  @override
  void dispose() {
    _sub.cancel();
    super.dispose();
  }
}

class HqApp extends StatefulWidget {
  const HqApp({super.key});
  @override
  State<HqApp> createState() => _HqAppState();
}

class _HqAppState extends State<HqApp> {
  final _auth = AuthListenable();
  late final GoRouter _router = GoRouter(
    initialLocation: '/home',
    refreshListenable: _auth,
    redirect: (context, state) {
      final signedIn = Hq.instance.signedIn;
      final onSignIn = state.matchedLocation == '/sign-in';
      if (!signedIn && !onSignIn) return '/sign-in';
      if (signedIn && onSignIn) return '/home';
      return null;
    },
    routes: [
      GoRoute(path: '/sign-in', builder: (_, _) => const SignInScreen()),
      ShellRoute(
        builder: (context, state, child) => HqShell(location: state.matchedLocation, child: child),
        routes: [
          GoRoute(path: '/home', builder: (_, _) => const HomeScreen()),
          GoRoute(path: '/profile', builder: (_, _) => const ProfileScreen()),
          GoRoute(path: '/settings', builder: (_, _) => const SettingsScreen()),
        ],
      ),
    ],
  );

  @override
  void dispose() {
    _auth.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const seed = Color(0xFF2E5E3F); // trail-sign green
    return MaterialApp.router(
      title: HqConfig.appName,
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: seed), useMaterial3: true),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: seed, brightness: Brightness.dark),
        useMaterial3: true,
      ),
      routerConfig: _router,
    );
  }
}

/// App frame: bottom navigation on phones, side rail on wide windows.
class HqShell extends StatelessWidget {
  const HqShell({super.key, required this.location, required this.child});
  final String location;
  final Widget child;

  static const _tabs = [
    (path: '/home', icon: Icons.inbox_outlined, selected: Icons.inbox, label: 'Home'),
    (path: '/profile', icon: Icons.business_outlined, selected: Icons.business, label: 'Business'),
    (path: '/settings', icon: Icons.settings_outlined, selected: Icons.settings, label: 'Settings'),
  ];

  int get _index {
    final i = _tabs.indexWhere((t) => location.startsWith(t.path));
    return i < 0 ? 0 : i;
  }

  @override
  Widget build(BuildContext context) {
    final wide = MediaQuery.sizeOf(context).width >= 720;
    if (wide) {
      return Scaffold(
        body: Row(children: [
          NavigationRail(
            selectedIndex: _index,
            labelType: NavigationRailLabelType.all,
            onDestinationSelected: (i) => context.go(_tabs[i].path),
            leading: const Padding(
              padding: EdgeInsets.symmetric(vertical: 12),
              child: Icon(Icons.terrain, size: 32),
            ),
            destinations: [
              for (final t in _tabs)
                NavigationRailDestination(
                  icon: Icon(t.icon),
                  selectedIcon: Icon(t.selected),
                  label: Text(t.label),
                ),
            ],
          ),
          const VerticalDivider(width: 1),
          Expanded(child: child),
        ]),
      );
    }
    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => context.go(_tabs[i].path),
        destinations: [
          for (final t in _tabs)
            NavigationDestination(icon: Icon(t.icon), selectedIcon: Icon(t.selected), label: t.label),
        ],
      ),
    );
  }
}
