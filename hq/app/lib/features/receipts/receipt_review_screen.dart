import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../config.dart';
import '../../data/hq.dart';
import '../../theme.dart';
import 'receipt_capture.dart';

/// Review and confirm a receipt. AI-filled fields stay marked until you touch or
/// confirm them; low-confidence fields are called out.
class ReceiptReviewScreen extends StatefulWidget {
  const ReceiptReviewScreen({super.key, required this.receiptId});
  final String receiptId;
  @override
  State<ReceiptReviewScreen> createState() => _ReceiptReviewScreenState();
}

class _ReceiptReviewScreenState extends State<ReceiptReviewScreen> {
  Map<String, dynamic>? _r;
  List<Map<String, dynamic>> _categories = [];
  List<Map<String, dynamic>> _vendors = [];
  List<Map<String, dynamic>> _lines = [];
  List<Map<String, dynamic>> _dupes = [];
  String? _imageUrl;
  String? _fileMime;
  bool _loading = true;
  bool _saving = false;
  String? _error;

  final _vendor = TextEditingController();
  final _total = TextEditingController();
  final _subtotal = TextEditingController();
  final _tax = TextEditingController();
  final _tip = TextEditingController();
  final _last4 = TextEditingController();
  final _notes = TextEditingController();
  DateTime? _date;
  String? _categoryId;
  String? _vendorId;
  String? _vendorDefaultCategoryId;
  String? _payment;
  bool _personal = false;
  final Set<String> _verified = {};
  Map<String, dynamic> _confidence = {};

  static const _payments = ['visa', 'mastercard', 'amex', 'discover', 'debit', 'cash', 'check', 'paypal', 'other'];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final c = Hq.instance.client;
      final r = await c.from('hq_receipts')
          .select('*, hq_vendors(id, name, default_category_id), hq_files(storage_path, mime)')
          .eq('id', widget.receiptId).single();
      final cats = await c.from('hq_categories').select('id, key, name, schedule_c_line').eq('active', true).order('sort');
      final vendors = await c.from('hq_vendors').select('id, name, default_category_id').order('name');
      final lines = await c.from('hq_receipt_line_items').select().eq('receipt_id', widget.receiptId).order('sort');
      final dupes = await c.rpc('hq_receipt_duplicates', params: {'p_receipt_id': widget.receiptId});
      final file = r['hq_files'] as Map?;
      String? url;
      if (file != null) {
        url = await c.storage.from(HqConfig.vaultBucket).createSignedUrl(file['storage_path'] as String, 900);
      }
      _r = Map<String, dynamic>.from(r);
      _categories = (cats as List).map((e) => Map<String, dynamic>.from(e)).toList();
      _vendors = (vendors as List).map((e) => Map<String, dynamic>.from(e)).toList();
      _lines = (lines as List).map((e) => Map<String, dynamic>.from(e)).toList();
      _dupes = ((dupes as List?) ?? []).map((e) => Map<String, dynamic>.from(e as Map)).toList();
      _imageUrl = url;
      _fileMime = file?['mime'] as String?;
      final v = r['hq_vendors'] as Map?;
      _vendor.text = v?['name'] ?? '';
      _vendorId = v?['id'];
      _vendorDefaultCategoryId = v?['default_category_id'];
      _total.text = _num(r['total']);
      _subtotal.text = _num(r['subtotal']);
      _tax.text = _num(r['tax']);
      _tip.text = _num(r['tip']);
      _last4.text = r['last4'] ?? '';
      _notes.text = r['notes'] ?? '';
      _date = r['date'] == null ? null : DateTime.parse(r['date']);
      _categoryId = r['category_id'];
      _payment = _payments.contains(r['payment_method']) ? r['payment_method'] : (r['payment_method'] == null ? null : 'other');
      _personal = r['paid_personally'] == true;
      _verified..clear()..addAll(((r['verified_fields'] as List?) ?? []).cast<String>());
      _confidence = Map<String, dynamic>.from((r['field_confidence'] as Map?) ?? {});
    } catch (e) {
      _error = '$e';
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  String _num(dynamic v) => v == null ? '' : (v as num).toStringAsFixed(2);
  double? _parse(String s) => s.trim().isEmpty ? null : double.tryParse(s.replaceAll(RegExp(r'[^0-9.\-]'), ''));

  bool _needsCheck(String field) {
    final c = (_confidence[field] as num?)?.toDouble();
    return !_verified.contains(field) && c != null && c < 0.7;
  }
  bool _aiSet(String field) => !_verified.contains(field) && _confidence.containsKey(field);

  InputDecoration _dec(String label, String field) => InputDecoration(
        labelText: label,
        suffixIcon: _needsCheck(field)
            ? const Tooltip(message: 'Low confidence — please check', child: Icon(Icons.warning_amber, color: AmpBrand.amber))
            : _aiSet(field) ? const Tooltip(message: 'Read automatically, not yet confirmed', child: Icon(Icons.auto_fix_high, size: 18)) : null,
      );

  Future<void> _save({String status = 'confirmed'}) async {
    setState(() => _saving = true);
    try {
      final c = Hq.instance.client;
      // Vendor: resolve by name (creates if new).
      String? vendorId = _vendorId;
      final vName = _vendor.text.trim();
      if (vName.isNotEmpty) {
        final current = _vendors.firstWhere((v) => v['id'] == _vendorId, orElse: () => {});
        if (current.isEmpty || current['name'] != vName) {
          vendorId = await c.rpc('hq_upsert_vendor', params: {'p_name': vName}) as String?;
        }
      }
      await c.from('hq_receipts').update({
        'vendor_id': vendorId,
        'date': _date?.toIso8601String().substring(0, 10),
        'total': _parse(_total.text), 'subtotal': _parse(_subtotal.text), 'tax': _parse(_tax.text), 'tip': _parse(_tip.text),
        'last4': _last4.text.trim().isEmpty ? null : _last4.text.trim(),
        'payment_method': _payment,
        'category_id': _categoryId,
        'paid_personally': _personal,
        'notes': _notes.text.trim().isEmpty ? null : _notes.text.trim(),
        'status': status,
        'verified_fields': ['vendor', 'date', 'total', 'subtotal', 'tax', 'tip', 'payment_method', 'last4', 'category'],
      }).eq('id', widget.receiptId);

      // "Make this a rule?" when the category differs from the vendor's default.
      if (status == 'confirmed' && vendorId != null && _categoryId != null && _categoryId != _vendorDefaultCategoryId && mounted) {
        final cat = _categories.firstWhere((x) => x['id'] == _categoryId, orElse: () => {'name': 'this category'});
        final yes = await showDialog<bool>(
          context: context,
          builder: (ctx) => AlertDialog(
            title: const Text('Make this a rule?'),
            content: Text('Always file $vName under ${cat['name']}? You can change it later.'),
            actions: [
              TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Just this once')),
              FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Always')),
            ],
          ),
        );
        if (yes == true) {
          await c.rpc('hq_apply_vendor_rule', params: {'p_vendor_id': vendorId, 'p_category_id': _categoryId, 'p_receipt_id': widget.receiptId});
        }
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(status == 'confirmed' ? 'Receipt confirmed' : 'Saved')));
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Save failed: $e')));
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _reread() async {
    setState(() => _saving = true);
    final res = await ReceiptCapture.instance.extract(widget.receiptId);
    if (!mounted) return;
    if (res.extractionError != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(res.extractionError!)));
      setState(() => _saving = false);
    } else {
      await _load();
      setState(() => _saving = false);
    }
  }

  Future<void> _delete() async {
    final yes = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete this receipt?'),
        content: const Text('It moves to the trash and can be restored later. The file is kept.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Delete')),
        ],
      ),
    );
    if (yes != true) return;
    await Hq.instance.client.from('hq_receipts').update({'deleted_at': DateTime.now().toUtc().toIso8601String()}).eq('id', widget.receiptId);
    if (mounted) Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (_loading) return Scaffold(appBar: AppBar(title: const Text('Receipt')), body: const Center(child: CircularProgressIndicator()));
    if (_error != null) return Scaffold(appBar: AppBar(title: const Text('Receipt')), body: Center(child: Text(_error!)));
    final status = _r!['status'] as String;
    final wide = MediaQuery.sizeOf(context).width >= 900;

    final form = ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (_dupes.isNotEmpty)
          Card(
            color: const Color(0xFF3A2A00),
            child: ListTile(
              leading: const Icon(Icons.copy_all, color: AmpBrand.amber),
              title: Text('Possible duplicate of ${_dupes.length} receipt(s)'),
              subtitle: Text(_dupes.map((d) => '${d['vendor_name'] ?? '?'} · ${d['date'] ?? '?'} · ${d['total'] ?? '?'} (${d['reason']})').join('\n')),
            ),
          ),
        if (_r!['notes'] != null && _aiSet('vendor'))
          Padding(padding: const EdgeInsets.only(bottom: 8), child: Text('Note: ${_r!['notes']}', style: theme.textTheme.bodySmall)),
        Autocomplete<String>(
          initialValue: TextEditingValue(text: _vendor.text),
          optionsBuilder: (v) => v.text.isEmpty ? const Iterable<String>.empty()
              : _vendors.map((x) => x['name'] as String).where((n) => n.toLowerCase().contains(v.text.toLowerCase())),
          onSelected: (s) { _vendor.text = s; _verified.add('vendor'); final m = _vendors.firstWhere((x) => x['name'] == s, orElse: () => {}); if (m.isNotEmpty) { _vendorId = m['id']; _vendorDefaultCategoryId = m['default_category_id']; _categoryId ??= m['default_category_id']; } setState(() {}); },
          fieldViewBuilder: (ctx, ctl, focus, onSubmit) {
            ctl.text = _vendor.text;
            ctl.addListener(() { _vendor.text = ctl.text; });
            return TextField(controller: ctl, focusNode: focus, decoration: _dec('Vendor', 'vendor'), onChanged: (_) => setState(() => _verified.add('vendor')));
          },
        ),
        const SizedBox(height: 12),
        Row(children: [
          Expanded(child: TextField(controller: _total, keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: _dec('Total', 'total'), onChanged: (_) => setState(() => _verified.add('total')))),
          const SizedBox(width: 12),
          Expanded(
            child: InkWell(
              onTap: () async {
                final d = await showDatePicker(context: context, initialDate: _date ?? DateTime.now(), firstDate: DateTime(2015), lastDate: DateTime.now().add(const Duration(days: 1)));
                if (d != null) setState(() { _date = d; _verified.add('date'); });
              },
              child: InputDecorator(
                decoration: _dec('Date', 'date'),
                child: Text(_date == null ? 'Pick' : DateFormat.yMMMd().format(_date!)),
              ),
            ),
          ),
        ]),
        const SizedBox(height: 12),
        DropdownButtonFormField<String>(
          initialValue: _categories.any((c) => c['id'] == _categoryId) ? _categoryId : null,
          decoration: _dec('Category (Schedule C)', 'category'),
          items: [for (final c in _categories) DropdownMenuItem(value: c['id'] as String, child: Text('${c['name']}${c['schedule_c_line'] != null ? '  ·  line ${c['schedule_c_line']}' : ''}', overflow: TextOverflow.ellipsis))],
          onChanged: (v) => setState(() { _categoryId = v; _verified.add('category'); }),
        ),
        const SizedBox(height: 12),
        Row(children: [
          Expanded(child: TextField(controller: _subtotal, keyboardType: const TextInputType.numberWithOptions(decimal: true), decoration: _dec('Subtotal', 'subtotal'), onChanged: (_) => setState(() => _verified.add('subtotal')))),
          const SizedBox(width: 8),
          Expanded(child: TextField(controller: _tax, keyboardType: const TextInputType.numberWithOptions(decimal: true), decoration: _dec('Tax', 'tax'), onChanged: (_) => setState(() => _verified.add('tax')))),
          const SizedBox(width: 8),
          Expanded(child: TextField(controller: _tip, keyboardType: const TextInputType.numberWithOptions(decimal: true), decoration: _dec('Tip', 'tip'), onChanged: (_) => setState(() => _verified.add('tip')))),
        ]),
        const SizedBox(height: 12),
        Row(children: [
          Expanded(
            flex: 2,
            child: DropdownButtonFormField<String>(
              initialValue: _payment,
              decoration: _dec('Paid with', 'payment_method'),
              items: [for (final p in _payments) DropdownMenuItem(value: p, child: Text(p))],
              onChanged: (v) => setState(() { _payment = v; _verified.add('payment_method'); }),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(child: TextField(controller: _last4, keyboardType: TextInputType.number, maxLength: 4, decoration: _dec('Last 4', 'last4').copyWith(counterText: ''), onChanged: (_) => setState(() => _verified.add('last4')))),
        ]),
        SwitchListTile(
          contentPadding: EdgeInsets.zero,
          title: const Text('Paid with a personal card'),
          subtitle: const Text('Tracked as owed to you by the business'),
          value: _personal,
          onChanged: (v) => setState(() => _personal = v),
        ),
        TextField(controller: _notes, maxLines: 2, decoration: const InputDecoration(labelText: 'Notes')),
        if (_lines.isNotEmpty) ...[
          const SizedBox(height: 16),
          Text('Line items', style: theme.textTheme.titleMedium),
          for (final l in _lines)
            ListTile(dense: true, contentPadding: EdgeInsets.zero,
              title: Text(l['description'] ?? ''), trailing: Text(_num(l['amount']))),
        ],
        const SizedBox(height: 20),
        Row(children: [
          Expanded(child: FilledButton(onPressed: _saving ? null : () => _save(), child: Text(status == 'confirmed' || status == 'reconciled' ? 'Save' : 'Confirm'))),
          const SizedBox(width: 8),
          PopupMenuButton<String>(
            onSelected: (v) { if (v == 'reread') _reread(); if (v == 'void') _save(status: 'void'); if (v == 'delete') _delete(); },
            itemBuilder: (_) => const [
              PopupMenuItem(value: 'reread', child: Text('Read the text again')),
              PopupMenuItem(value: 'void', child: Text('Mark void')),
              PopupMenuItem(value: 'delete', child: Text('Delete')),
            ],
            child: const Padding(padding: EdgeInsets.all(12), child: Icon(Icons.more_vert)),
          ),
        ]),
        const SizedBox(height: 40),
      ],
    );

    final preview = _Preview(url: _imageUrl, mime: _fileMime);

    return Scaffold(
      appBar: AppBar(title: Text(status == 'needs_review' ? 'Review receipt' : 'Receipt')),
      body: wide
          ? Row(children: [Expanded(child: preview), const VerticalDivider(width: 1), SizedBox(width: 460, child: form)])
          : Column(children: [SizedBox(height: 220, child: preview), const Divider(height: 1), Expanded(child: form)]),
    );
  }
}

class _Preview extends StatelessWidget {
  const _Preview({required this.url, required this.mime});
  final String? url;
  final String? mime;
  @override
  Widget build(BuildContext context) {
    if (url == null) return const Center(child: Text('No file'));
    if (mime == 'application/pdf') {
      return Center(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          const Icon(Icons.picture_as_pdf, size: 56),
          TextButton.icon(onPressed: () => launchUrl(Uri.parse(url!), mode: LaunchMode.externalApplication), icon: const Icon(Icons.open_in_new), label: const Text('Open PDF')),
        ]),
      );
    }
    return InteractiveViewer(
      minScale: 0.5, maxScale: 5,
      child: Image.network(url!, fit: BoxFit.contain, width: double.infinity,
          loadingBuilder: (c, w, p) => p == null ? w : const Center(child: CircularProgressIndicator()),
          errorBuilder: (c, e, s) => const Center(child: Text('Could not load the image'))),
    );
  }
}
