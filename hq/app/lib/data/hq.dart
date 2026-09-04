import 'package:supabase_flutter/supabase_flutter.dart';

/// Thin data layer over Supabase. Every call runs as the signed-in founder;
/// row-level security on the server does the real gatekeeping.
class Hq {
  Hq._();
  static final Hq instance = Hq._();

  SupabaseClient get client => Supabase.instance.client;
  GoTrueClient get auth => client.auth;
  String? get userId => auth.currentUser?.id;
  String? get email => auth.currentUser?.email;
  bool get signedIn => auth.currentSession != null;

  /// Creates the profile + default categories/deadlines/checklist on first
  /// sign-in. Idempotent, so it is safe to call on every launch.
  Future<Map<String, dynamic>> bootstrap() async {
    final res = await client.rpc('hq_bootstrap');
    return Map<String, dynamic>.from(res as Map);
  }

  Future<Map<String, dynamic>> homeSummary() async {
    final res = await client.rpc('hq_home_summary');
    return Map<String, dynamic>.from(res as Map);
  }

  Future<int> enabledRuleCount() async {
    final rows = await client
        .from('hq_deadline_rules')
        .select('id')
        .eq('enabled', true)
        .isFilter('retired_on', null);
    return (rows as List).length;
  }

  Future<Map<String, dynamic>?> profile() async {
    final row = await client
        .from('hq_business_profile')
        .select()
        .eq('owner', userId!)
        .maybeSingle();
    return row == null ? null : Map<String, dynamic>.from(row);
  }

  Future<void> saveProfile(Map<String, dynamic> values) async {
    await client.from('hq_business_profile').update(values).eq('owner', userId!);
  }

  Future<void> setEin(String ein) => client.rpc('hq_set_ein', params: {'p_ein': ein});

  Future<String?> revealEin() async {
    final res = await client.rpc('hq_get_ein');
    return res as String?;
  }

  Future<List<Map<String, dynamic>>> checklist() async {
    final rows = await client
        .from('hq_checklist_items')
        .select()
        .order('sort');
    return (rows as List).map((r) => Map<String, dynamic>.from(r)).toList();
  }

  Future<void> setChecklistStatus(String id, String status) async {
    await client.from('hq_checklist_items').update({
      'status': status,
      'last_reviewed': DateTime.now().toIso8601String().substring(0, 10),
    }).eq('id', id);
  }
}
