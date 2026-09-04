import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../../config.dart';
import '../../data/hq.dart';

/// Email + password sign-in (primary) with an emailed one-time code as the
/// alternative. Only the allow-listed founder email can get past the database.
class SignInScreen extends StatefulWidget {
  const SignInScreen({super.key});
  @override
  State<SignInScreen> createState() => _SignInScreenState();
}

enum _Mode { password, codeRequest, codeEnter }

class _SignInScreenState extends State<SignInScreen> {
  final _email = TextEditingController(text: 'riggs1991@gmail.com');
  final _password = TextEditingController();
  final _code = TextEditingController();
  _Mode _mode = _Mode.password;
  bool _busy = false;
  bool _showPassword = false;
  String? _error;

  Future<void> _run(Future<void> Function() action, String fallback) async {
    setState(() { _busy = true; _error = null; });
    try {
      await action();
    } on AuthException catch (e) {
      setState(() => _error = e.message);
    } catch (_) {
      setState(() => _error = fallback);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _signInWithPassword() => _run(
        () => Hq.instance.auth.signInWithPassword(
          email: _email.text.trim(),
          password: _password.text,
        ),
        'Could not sign in. Check your connection and try again.',
      );

  Future<void> _sendCode() => _run(() async {
        await Hq.instance.auth.signInWithOtp(email: _email.text.trim(), shouldCreateUser: true);
        setState(() => _mode = _Mode.codeEnter);
      }, 'Could not send the code. Check your connection and try again.');

  Future<void> _verifyCode() => _run(
        () => Hq.instance.auth.verifyOTP(
          type: OtpType.email,
          email: _email.text.trim(),
          token: _code.text.trim(),
        ),
        'That code did not work. Request a new one.',
      );

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final emailField = TextField(
      controller: _email,
      keyboardType: TextInputType.emailAddress,
      autofillHints: const [AutofillHints.email],
      decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder()),
    );
    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 400),
          child: SingleChildScrollView(
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
                switch (_mode) {
                  _Mode.password => Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                      emailField,
                      const SizedBox(height: 12),
                      TextField(
                        controller: _password,
                        obscureText: !_showPassword,
                        autofillHints: const [AutofillHints.password],
                        decoration: InputDecoration(
                          labelText: 'Password',
                          border: const OutlineInputBorder(),
                          suffixIcon: IconButton(
                            icon: Icon(_showPassword ? Icons.visibility_off : Icons.visibility),
                            onPressed: () => setState(() => _showPassword = !_showPassword),
                          ),
                        ),
                        onSubmitted: (_) => _busy ? null : _signInWithPassword(),
                      ),
                      const SizedBox(height: 16),
                      FilledButton(
                        onPressed: _busy ? null : _signInWithPassword,
                        child: Text(_busy ? 'Signing in…' : 'Sign in'),
                      ),
                      TextButton(
                        onPressed: _busy ? null : () => setState(() { _mode = _Mode.codeRequest; _error = null; }),
                        child: const Text('Email me a one-time code instead'),
                      ),
                    ]),
                  _Mode.codeRequest => Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                      emailField,
                      const SizedBox(height: 16),
                      FilledButton(
                        onPressed: _busy ? null : _sendCode,
                        child: Text(_busy ? 'Sending…' : 'Email me a sign-in code'),
                      ),
                      TextButton(
                        onPressed: _busy ? null : () => setState(() { _mode = _Mode.password; _error = null; }),
                        child: const Text('Use my password instead'),
                      ),
                    ]),
                  _Mode.codeEnter => Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                      Text('Enter the 6-digit code sent to ${_email.text.trim()}. '
                          'If the email only contains a link, use your password instead.',
                          style: theme.textTheme.bodyMedium),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _code,
                        keyboardType: TextInputType.number,
                        autofocus: true,
                        decoration: const InputDecoration(labelText: 'Code', border: OutlineInputBorder()),
                        onSubmitted: (_) => _busy ? null : _verifyCode(),
                      ),
                      const SizedBox(height: 16),
                      FilledButton(
                        onPressed: _busy ? null : _verifyCode,
                        child: Text(_busy ? 'Checking…' : 'Sign in'),
                      ),
                      TextButton(
                        onPressed: _busy ? null : () => setState(() { _mode = _Mode.password; _code.clear(); _error = null; }),
                        child: const Text('Use my password instead'),
                      ),
                    ]),
                },
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
