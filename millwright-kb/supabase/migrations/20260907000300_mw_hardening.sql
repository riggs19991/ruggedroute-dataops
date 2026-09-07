-- Hardening per Supabase security advisor: pin search_path on every mw_ function and
-- stop anonymous callers from executing helper/definer functions they never need.

alter function public.mw_new_join_code()      set search_path = public;
alter function public.mw_guard_role_change()  set search_path = public;
alter function public.mw_arr_text(text[])     set search_path = public;
alter function public.mw_touch_updated_at()   set search_path = public;
alter function public.mw_search(text, text, int) set search_path = public;

revoke execute on function public.mw_handle_new_user()        from anon, authenticated, public;
revoke execute on function public.mw_guard_role_change()      from anon, authenticated, public;
revoke execute on function public.mw_touch_updated_at()       from anon, authenticated, public;
-- NOTE: mw_is_teacher / mw_is_group_member / mw_is_group_teacher must stay executable by anon:
-- the RLS policies on mw_articles and mw_groups call them as the calling role.
revoke execute on function public.mw_become_teacher(text)     from anon, public;
revoke execute on function public.mw_join_group(text)         from anon, public;
revoke execute on function public.mw_new_join_code()          from anon, public;
-- mw_bump_view and mw_import_content stay callable by anon on purpose:
-- bump_view is a harmless counter; import_content is gated by the seed token.
