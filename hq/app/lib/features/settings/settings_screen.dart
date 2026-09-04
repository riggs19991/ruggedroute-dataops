import 'package:flutter/material.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../config.dart';
import '../../data/hq.dart';
import '../../updater/updater.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});
  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  PackageInfo? _info;
  ReleaseInfo? _available;
  double? _progress;
  String? _status;

  @override
  void initState() {
    super.initState();
    PackageInfo.fromPlatform().then((i) => mounted ? setState(() => _info = i) : null);
  }

  Future<void> _check() async {
    setState(() { _status = 'Checking…'; _available = null; });
    try {
      final rel = await Updater.instance.checkForUpdate();
      setState(() {
        _available = rel;
        _status = rel == null ? 'You have the latest version.' : 'Version ${rel.version} is available.';
      });
    } catch (e) {
      setState(() => _status = 'Could not check: $e');
    }
  }

  Future<void> _install() async {
    final rel = _available;
    if (rel == null) return;
    setState(() { _progress = 0; _status = 'Downloading…'; });
    try {
      await Updater.instance.downloadAndInstall(rel, (p) => setState(() => _progress = p));
      setState(() { _status = 'Installer opened. Follow the prompts.'; _progress = null; });
    } catch (e) {
      setState(() { _status = '$e'; _progress = null; });
    }
  }

  Future<void> _changePassword() async {
    final a = TextEditingController();
    final b = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Change password'),
        content: Column(mainAxisSize: MainAxisSize.min, children: [
          TextField(controller: a, obscureText: true, autofocus: true,
              decoration: const InputDecoration(labelText: 'New password (12+ characters)')),
          const SizedBox(height: 8),
          TextField(controller: b, obscureText: true,
              decoration: const InputDecoration(labelText: 'Repeat new password')),
        ]),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Change')),
        ],
      ),
    );
    if (ok != true) return;
    if (a.text.length < 12 || a.text != b.text) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Passwords must match and be at least 12 characters.')));
      return;
    }
    try {
      await Hq.instance.auth.updateUser(UserAttributes(password: a.text));
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Password changed')));
    } on AuthException catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Column(children: [
              ListTile(
                leading: const Icon(Icons.system_update),
                title: Text('${HqConfig.appName} ${_info?.version ?? ''} (build ${_info?.buildNumber ?? ''})'),
                subtitle: Text(_status ?? 'Updates install directly, no app store.'),
                trailing: _available == null
                    ? TextButton(onPressed: _check, child: const Text('Check'))
                    : FilledButton(onPressed: _progress == null ? _install : null, child: const Text('Update')),
              ),
              if (_progress != null)
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
                  child: LinearProgressIndicator(value: _progress),
                ),
              if (_available?.notes != null)
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
                  child: Text(_available!.notes!, style: theme.textTheme.bodySmall),
                ),
            ]),
          ),
          const SizedBox(height: 12),
          Card(
            child: Column(children: [
              ListTile(
                leading: const Icon(Icons.account_circle_outlined),
                title: Text(Hq.instance.email ?? ''),
                subtitle: const Text('Only this email can open HQ.'),
                trailing: TextButton(
                  onPressed: () => Hq.instance.auth.signOut(),
                  child: const Text('Sign out'),
                ),
              ),
              ListTile(
                leading: const Icon(Icons.password),
                title: const Text('Change password'),
                onTap: _changePassword,
              ),
            ]),
          ),
          const SizedBox(height: 12),
          Card(
            child: Column(children: [
              ListTile(
                leading: const Icon(Icons.storage_outlined),
                title: const Text('Where your data lives'),
                subtitle: const Text('Supabase project tzucpijgyjhpgwukjsau, tables prefixed hq_, private buckets hq-vault and hq-releases. Everything is row-level-secured to your login.'),
              ),
              ListTile(
                leading: const Icon(Icons.open_in_new),
                title: const Text('Supabase dashboard'),
                onTap: () => launchUrl(Uri.parse('https://supabase.com/dashboard/project/tzucpijgyjhpgwukjsau')),
              ),
              ListTile(
                leading: const Icon(Icons.open_in_new),
                title: const Text('Idaho SOSBiz'),
                onTap: () => launchUrl(Uri.parse('https://sosbiz.idaho.gov')),
              ),
            ]),
          ),
        ],
      ),
    );
  }
}
