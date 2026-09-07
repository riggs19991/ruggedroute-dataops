import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../../data/hq.dart';
import '../../theme.dart';
import 'receipt_capture.dart';

class ReceiptsListScreen extends StatefulWidget {
  const ReceiptsListScreen({super.key, this.initialStatus});
  final String? initialStatus;
  @override
  State<ReceiptsListScreen> createState() => _ReceiptsListScreenState();
}

class _ReceiptsListScreenState extends State<ReceiptsListScreen> {
  String _status = 'all';
  final _search = TextEditingController();
  late Future<List<Map<String, dynamic>>> _future;

  @override
  void initState() {
    super.initState();
    _status = widget.initialStatus ?? 'all';
    _future = _load();
  }

  Future<List<Map<String, dynamic>>> _load() async {
    var q = Hq.instance.client
        .from('hq_receipts')
        .select('id, date, total, currency, status, paid_personally, source, created_at, hq_vendors(name), hq_categories(name)')
        .isFilter('deleted_at', null);
    if (_status != 'all') q = q.eq('status', _status);
    final s = _search.text.trim();
    if (s.isNotEmpty) q = q.textSearch('search', s, type: TextSearchType.websearch, config: 'english');
    final rows = await q.order('date', ascending: false, nullsFirst: true).order('created_at', ascending: false).limit(200);
    return (rows as List).map((r) => Map<String, dynamic>.from(r)).toList();
  }

  void _reload() => setState(() => _future = _load());

  @override
  Widget build(BuildContext context) {
    final money = NumberFormat.simpleCurrency();
    return Scaffold(
      appBar: AppBar(title: const Text('Receipts')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => runCaptureFlow(context, (id) { context.push('/receipts/$id').then((_) => _reload()); }),
        icon: const Icon(Icons.photo_camera),
        label: const Text('Capture'),
      ),
      body: Column(children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
          child: TextField(
            controller: _search,
            decoration: InputDecoration(
              hintText: 'Search vendor, notes, receipt text',
              prefixIcon: const Icon(Icons.search),
              suffixIcon: _search.text.isEmpty ? null : IconButton(icon: const Icon(Icons.clear), onPressed: () { _search.clear(); _reload(); }),
            ),
            onSubmitted: (_) => _reload(),
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(children: [
            for (final s in const [('all', 'All'), ('needs_review', 'Needs review'), ('confirmed', 'Confirmed'), ('reconciled', 'Reconciled')])
              Padding(
                padding: const EdgeInsets.only(right: 8),
                child: ChoiceChip(label: Text(s.$2), selected: _status == s.$1, onSelected: (_) { _status = s.$1; _reload(); }),
              ),
          ]),
        ),
        Expanded(
          child: FutureBuilder<List<Map<String, dynamic>>>(
            future: _future,
            builder: (context, snap) {
              if (snap.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
              if (snap.hasError) return Center(child: Text('Could not load receipts: ${snap.error}'));
              final rows = snap.data!;
              if (rows.isEmpty) {
                return const Center(child: Padding(padding: EdgeInsets.all(24), child: Text('No receipts here yet. Tap Capture to add one.')));
              }
              return RefreshIndicator(
                onRefresh: () async { _reload(); await _future; },
                child: ListView.builder(
                  padding: const EdgeInsets.fromLTRB(16, 0, 16, 96),
                  itemCount: rows.length,
                  itemBuilder: (context, i) {
                    final r = rows[i];
                    final vendor = (r['hq_vendors'] as Map?)?['name'] as String? ?? 'Unknown vendor';
                    final cat = (r['hq_categories'] as Map?)?['name'] as String?;
                    final date = r['date'] == null ? null : DateTime.parse(r['date'] as String);
                    final total = (r['total'] as num?)?.toDouble();
                    final status = r['status'] as String;
                    return Card(
                      child: ListTile(
                        leading: _StatusDot(status: status),
                        title: Text(vendor, maxLines: 1, overflow: TextOverflow.ellipsis),
                        subtitle: Text([
                          if (date != null) DateFormat.yMMMd().format(date) else 'no date',
                          ?cat,
                          if (r['paid_personally'] == true) 'personal card',
                        ].join(' · ')),
                        trailing: Text(total == null ? '—' : money.format(total),
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(fontFeatures: const [FontFeature.tabularFigures()])),
                        onTap: () => context.push('/receipts/${r['id']}').then((_) => _reload()),
                      ),
                    );
                  },
                ),
              );
            },
          ),
        ),
      ]),
    );
  }
}

class _StatusDot extends StatelessWidget {
  const _StatusDot({required this.status});
  final String status;
  @override
  Widget build(BuildContext context) {
    final (color, icon) = switch (status) {
      'needs_review' => (AmpBrand.amber, Icons.pending_outlined),
      'confirmed' => (AmpBrand.green, Icons.check_circle_outline),
      'reconciled' => (AmpBrand.green, Icons.verified_outlined),
      _ => (AmpBrand.textSecondary, Icons.block),
    };
    return Icon(icon, color: color);
  }
}
