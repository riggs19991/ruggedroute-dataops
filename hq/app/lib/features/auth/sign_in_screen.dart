import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../../config.dart';
import '../../data/hq.dart';

/// Email + one-time code sign-in. Only the allow-listed founder email can get
/// past the database, so there is nothing to guess here.
class SignInScreen extends StatefulWidget {
  const SignInScreen({super.key});
  @override
  State<SignInScreen> createState() => _SignInScreenState();
}

class _SignInScreenState extends State<SignInScreen> {
  final _email = TextEditingController();
  final _code = TextEditingController();
  bool _codeSent = false;
  bool _busy = false;
  String? _error;

  Future<void> _sendCode() async {
    setState(() { _busy = true; _error = null; });
    try {
      await Hq.instance.auth.signInWithOtp(email: _email.text.trim(), shouldCreateUser: true);
      setState(() => _codeSent = true);
    } on AuthException catch (e) {
      setState(() => _error = e.message);
    } catch (e) {
      setState(() => _error = 'Could not send the code. Check your connection and try again.');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _verify() async {
    setState(() { _busy = true; _error = null; });
    try {
      await Hq.instance.auth.verifyOTP(
        type: OtpType.email,
        email: _email.text.trim(),
        token: _code.text.trim(),
      );
      // Router redirects to /home on the auth state change.
    } on AuthException catch (e) {
      setState(() => _error = e.message);
    } catch (e) {
      setState(() => _error = 'That code did not work. Request a new one.');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 400),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Icon(Icons.terrain, size: 56, color: theme.colorScheme.primary),
                const SizedBox(height: 12),
                Text(HqConfig.appName, textAlign: TextAlign.center, style: theme.textTheme.headlineSmall),
                Text('Addictive Media Productions LLC',
                    textAlign: TextAlign.center, style: theme.textTheme.bodyMedium),
                const SizedBox(height: 32),
                if (!_codeSent) ...[
                  TextField(
                    controller: _email,
                    keyboardType: TextInputType.emailAddress,
                    autofillHints: const [AutofillHints.email],
                    decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder()),
                    onSubmitted: (_) => _busy ? null : _sendCode(),
                  ),
                  const SizedBox(height: 16),
                  FilledButton(
                    onPressed: _busy ? null : _sendCode,
                    child: Text(_busy ? 'Sending…' : 'Email me a sign-in code'),
                  ),
                ] else ...[
                  Text('Enter the 6-digit code sent to ${_email.text.trim()}',
                      style: theme.textTheme.bodyMedium),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _code,
                    keyboardType: TextInputType.number,
                    autofocus: true,
                    decoration: const InputDecoration(labelText: 'Code', border: OutlineInputBorder()),
                    onSubmitted: (_) => _busy ? null : _verify(),
                  ),
                  const SizedBox(height: 16),
                  FilledButton(
                    onPressed: _busy ? null : _verify,
                    child: Text(_busy ? 'Checking…' : 'Sign in'),
                  ),
                  TextButton(
                    onPressed: _busy ? null : () => setState(() { _codeSent = false; _code.clear(); }),
                    child: const Text('Use a different email'),
                  ),
                ],
                if (_error != null) ...[
                  const SizedBox(height: 12),
                  Text(_error!, style: TextStyle(color: theme.colorScheme.error)),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
