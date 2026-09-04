import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../data/hq.dart';
import '../../updater/updater.dart';

/// The home screen is an exceptions inbox: only things that need a decision.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late Future<_HomeData> _future;

  @override
  void initState() {
    super.initState();
    _future = _load();
    _checkForUpdateQuietly();
  }

  Future<_HomeData> _load() async {
    final summary = await Hq.instance.bootstrap();
    final rules = await Hq.instance.enabledRuleCount();
    return _HomeData(summary, rules);
  }

  Future<void> _checkForUpdateQuietly() async {
    try {
      final rel = await Updater.instance.checkForUpdate();
      if (rel != null && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Version ${rel.version} is available'),
          action: SnackBarAction(label: 'Update', onPressed: () => context.go('/settings')),
          duration: const Duration(seconds: 8),
        ));
      }
    } catch (_) {/* offline or no releases yet */}
  }

  Future<void> _refresh() async {
    setState(() => _future = _load());
    await _future;
  }

  void _comingSoon(String what) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text('$what arrives in the next update.'),
    ));
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Home'), actions: [
        IconButton(icon: const Icon(Icons.refresh), onPressed: _refresh, tooltip: 'Refresh'),
      ]),
      body: FutureBuilder<_HomeData>(
        future: _future,
        builder: (context, snap) {
          if (snap.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snap.hasError) {
            return _ErrorView(error: snap.error.toString(), onRetry: _refresh);
          }
          final d = snap.data!;
          final items = _exceptions(d);
          return RefreshIndicator(
            onRefresh: _refresh,
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                SizedBox(
                  height: 64,
                  child: FilledButton.icon(
                    onPressed: () => _comingSoon('Receipt capture'),
                    icon: const Icon(Icons.photo_camera, size: 28),
                    label: const Text('Capture receipt', style: TextStyle(fontSize: 18)),
                  ),
                ),
                const SizedBox(height: 16),
                _GoodStandingTile(data: d),
                const SizedBox(height: 16),
                Text('Needs a decision', style: theme.textTheme.titleMedium),
                const SizedBox(height: 8),
                if (items.isEmpty)
                  Card(
                    child: ListTile(
                      leading: Icon(Icons.check_circle, color: theme.colorScheme.primary),
                      title: const Text('Nothing needs your attention'),
                      subtitle: const Text('Everything is filed, reviewed, and current.'),
                    ),
                  )
                else
                  for (final it in items)
                    Card(
                      child: ListTile(
                        leading: Icon(it.icon, color: it.critical ? theme.colorScheme.error : null),
                        title: Text(it.title),
                        subtitle: it.subtitle == null ? null : Text(it.subtitle!),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: it.route != null ? () => context.go(it.route!) : () => _comingSoon(it.title),
                      ),
                    ),
                const SizedBox(height: 16),
                _MonthStrip(summary: d.summary),
              ],
            ),
          );
        },
      ),
    );
  }

  List<_Exception> _exceptions(_HomeData d) {
    final s = d.summary;
    int n(String k) => (s[k] as num?)?.toInt() ?? 0;
    final out = <_Exception>[];
    if (s['profile_complete'] != true) {
      out.add(const _Exception(Icons.business, 'Finish your business profile',
          'Formation date sets the Idaho annual-report clock.', route: '/profile'));
    }
    if (n('deadlines_overdue') > 0) {
      out.add(_Exception(Icons.warning_amber, '${n('deadlines_overdue')} overdue deadline(s)', null, critical: true));
    }
    if (n('deadlines_30d') > 0) {
      out.add(_Exception(Icons.event, '${n('deadlines_30d')} deadline(s) due within 30 days', null));
    }
    if (n('receipts_needs_review') > 0) {
      out.add(_Exception(Icons.receipt_long, '${n('receipts_needs_review')} receipt(s) awaiting review', null));
    }
    if (n('transactions_unmatched') > 0) {
      out.add(_Exception(Icons.credit_card, '${n('transactions_unmatched')} charge(s) with no receipt', null));
    }
    if (n('documents_inbox') > 0) {
      out.add(_Exception(Icons.move_to_inbox, '${n('documents_inbox')} document(s) to file', null));
    }
    if (n('agency_letters_open') > 0) {
      out.add(_Exception(Icons.mail, '${n('agency_letters_open')} agency letter(s) not actioned', null, critical: true));
    }
    if (n('documents_expiring_90d') > 0) {
      out.add(_Exception(Icons.timer, '${n('documents_expiring_90d')} document(s) expiring within 90 days', null));
    }
    return out;
  }
}

class _HomeData {
  _HomeData(this.summary, this.enabledRules);
  final Map<String, dynamic> summary;
  final int enabledRules;
}

class _Exception {
  const _Exception(this.icon, this.title, this.subtitle, {this.route, this.critical = false});
  final IconData icon;
  final String title;
  final String? subtitle;
  final String? route;
  final bool critical;
}

class _GoodStandingTile extends StatelessWidget {
  const _GoodStandingTile({required this.data});
  final _HomeData data;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final s = data.summary;
    final overdue = (s['deadlines_overdue'] as num?)?.toInt() ?? 0;
    final next = s['next_deadline'] as Map?;
    Color color;
    String headline;
    String detail;
    if (overdue > 0) {
      color = theme.colorScheme.error;
      headline = 'Action needed';
      detail = '$overdue deadline(s) overdue';
    } else if (next != null) {
      final due = DateTime.parse(next['due_on'] as String);
      final days = due.difference(DateTime.now()).inDays;
      color = days <= 30 ? Colors.amber.shade700 : Colors.green.shade700;
      headline = days <= 30 ? 'Due soon' : 'In good standing';
      detail = '${next['title']} · ${DateFormat.yMMMd().format(due)} ($days days)';
    } else {
      color = theme.colorScheme.outline;
      headline = 'Deadline engine not active yet';
      detail = '${data.enabledRules} rules loaded. Dates are generated once your formation date is confirmed and the deadline update ships.';
    }
    return Card(
      child: ListTile(
        leading: CircleAvatar(backgroundColor: color, child: const Icon(Icons.shield, color: Colors.white)),
        title: Text(headline, style: theme.textTheme.titleMedium),
        subtitle: Text(detail),
      ),
    );
  }
}

class _MonthStrip extends StatelessWidget {
  const _MonthStrip({required this.summary});
  final Map<String, dynamic> summary;

  @override
  Widget build(BuildContext context) {
    final money = NumberFormat.simpleCurrency(decimalDigits: 0);
    num v(String k) => (summary[k] as num?) ?? 0;
    final month = DateFormat.MMMM().format(DateTime.now());
    Widget cell(String label, String value) => Expanded(
          child: Column(children: [
            Text(value, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontFeatures: const [])),
            Text(label, style: Theme.of(context).textTheme.bodySmall),
          ]),
        );
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
        child: Column(children: [
          Text(month, style: Theme.of(context).textTheme.labelLarge),
          const SizedBox(height: 8),
          Row(children: [
            cell('spent', money.format(v('month_spent'))),
            cell('income', money.format(v('month_income'))),
            cell('miles', v('month_miles').toStringAsFixed(0)),
          ]),
        ]),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.error, required this.onRetry});
  final String error;
  final Future<void> Function() onRetry;
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          const Icon(Icons.cloud_off, size: 48),
          const SizedBox(height: 12),
          const Text('Could not load your data.'),
          const SizedBox(height: 4),
          Text(error, style: Theme.of(context).textTheme.bodySmall, textAlign: TextAlign.center),
          const SizedBox(height: 12),
          FilledButton(onPressed: onRetry, child: const Text('Try again')),
        ]),
      ),
    );
  }
}
