import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../../data/hq.dart';

const _entityTypes = {
  'sole': 'Sole proprietor',
  'smllc': 'Single-member LLC',
  'llc': 'Multi-member LLC',
  'scorp': 'S corporation',
  'ccorp': 'C corporation',
};

const _timezones = ['America/Los_Angeles', 'America/Boise', 'America/Denver', 'America/Chicago', 'America/New_York'];

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _form = GlobalKey<FormState>();
  final _legalName = TextEditingController();
  final _dba = TextEditingController();
  final _county = TextEditingController();
  String _entity = 'smllc';
  String _tz = 'America/Los_Angeles';
  DateTime? _formation;
  bool _formationVerified = false;
  String? _einLast4;
  bool _loading = true;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final p = await Hq.instance.profile();
    if (p != null) {
      _legalName.text = p['legal_name'] ?? '';
      _dba.text = p['dba'] ?? '';
      _county.text = p['county'] ?? '';
      _entity = p['entity_type'] ?? 'smllc';
      _tz = p['timezone'] ?? 'America/Los_Angeles';
      _formation = p['formation_date'] == null ? null : DateTime.parse(p['formation_date']);
      _formationVerified = p['formation_date_verified'] == true;
      _einLast4 = p['ein_last4'];
    }
    if (mounted) setState(() => _loading = false);
  }

  Future<void> _save() async {
    if (!_form.currentState!.validate()) return;
    setState(() => _saving = true);
    try {
      await Hq.instance.saveProfile({
        'legal_name': _legalName.text.trim(),
        'dba': _dba.text.trim().isEmpty ? null : _dba.text.trim(),
        'county': _county.text.trim().isEmpty ? null : _county.text.trim(),
        'entity_type': _entity,
        'timezone': _tz,
        'formation_date': _formation?.toIso8601String().substring(0, 10),
        'formation_date_verified': _formationVerified,
      });
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Saved')));
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Save failed: $e')));
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _pickFormation() async {
    final d = await showDatePicker(
      context: context,
      initialDate: _formation ?? DateTime(2024, 8, 1),
      firstDate: DateTime(1990),
      lastDate: DateTime.now(),
      helpText: 'Organization date shown on SOSBiz',
    );
    if (d != null) setState(() => _formation = d);
  }

  Future<void> _setEin() async {
    final ctl = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Employer Identification Number'),
        content: TextField(
          controller: ctl,
          autofocus: true,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(hintText: '12-3456789'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Store securely')),
        ],
      ),
    );
    if (ok != true) return;
    try {
      await Hq.instance.setEin(ctl.text);
      final digits = ctl.text.replaceAll(RegExp(r'[^0-9]'), '');
      setState(() => _einLast4 = digits.substring(digits.length - 4));
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('EIN stored in the encrypted vault')));
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e')));
    }
  }

  Future<void> _revealEin() async {
    final ein = await Hq.instance.revealEin();
    if (!mounted) return;
    final shown = ein == null ? 'Not set' : '${ein.substring(0, 2)}-${ein.substring(2)}';
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('EIN'),
        content: SelectableText(shown, style: Theme.of(ctx).textTheme.headlineSmall),
        actions: [TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Close'))],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (_loading) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    return Scaffold(
      appBar: AppBar(title: const Text('Business')),
      body: Form(
        key: _form,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            TextFormField(
              controller: _legalName,
              decoration: const InputDecoration(labelText: 'Legal name', border: OutlineInputBorder()),
              validator: (v) => (v ?? '').trim().isEmpty ? 'Required' : null,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _dba,
              decoration: const InputDecoration(
                labelText: 'Assumed business name (DBA)',
                helperText: 'e.g. RuggedRoute, once filed with the Idaho SOS',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              initialValue: _entity,
              decoration: const InputDecoration(labelText: 'Entity type', border: OutlineInputBorder()),
              items: [for (final e in _entityTypes.entries) DropdownMenuItem(value: e.key, child: Text(e.value))],
              onChanged: (v) => setState(() => _entity = v ?? _entity),
            ),
            const SizedBox(height: 12),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Formation date (from SOSBiz)'),
              subtitle: Text(_formation == null ? 'Not set — this drives the annual-report deadline' : DateFormat.yMMMMd().format(_formation!)),
              trailing: FilledButton.tonal(onPressed: _pickFormation, child: const Text('Pick')),
            ),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Verified against SOSBiz'),
              subtitle: const Text('Turn on once you have read the organization date on your entity page.'),
              value: _formationVerified,
              onChanged: (v) => setState(() => _formationVerified = v),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _county,
              decoration: const InputDecoration(labelText: 'County', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              initialValue: _timezones.contains(_tz) ? _tz : _timezones.first,
              decoration: const InputDecoration(labelText: 'Time zone for deadlines', border: OutlineInputBorder()),
              items: [for (final t in _timezones) DropdownMenuItem(value: t, child: Text(t))],
              onChanged: (v) => setState(() => _tz = v ?? _tz),
            ),
            const SizedBox(height: 20),
            Card(
              child: ListTile(
                leading: const Icon(Icons.lock_outline),
                title: const Text('EIN'),
                subtitle: Text(_einLast4 == null ? 'Not stored yet' : 'Stored in the encrypted vault · ends in $_einLast4'),
                trailing: Wrap(spacing: 4, children: [
                  if (_einLast4 != null) TextButton(onPressed: _revealEin, child: const Text('Reveal')),
                  TextButton(onPressed: _setEin, child: Text(_einLast4 == null ? 'Set' : 'Change')),
                ]),
              ),
            ),
            const SizedBox(height: 24),
            FilledButton(onPressed: _saving ? null : _save, child: Text(_saving ? 'Saving…' : 'Save')),
            const SizedBox(height: 12),
            Text(
              'Federal: Schedule C + SE on Form 1040 (April 15), 1040-ES quarterlies. '
              'Idaho: Form 40 (April 15), no state estimates required. No sales tax for services or app subscriptions.',
              style: theme.textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}
