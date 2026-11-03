import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:go_router/go_router.dart';

class ForgotPasswordPage extends StatefulWidget {
  const ForgotPasswordPage({super.key, this.sendResetEmail});
  final Future<void> Function(String email)? sendResetEmail;
  @override
  State<ForgotPasswordPage> createState() => _ForgotPasswordPageState();
}

class _ForgotPasswordPageState extends State<ForgotPasswordPage> {
  final _email = TextEditingController();
  bool _busy = false;
  String? _message;
  @override
  void dispose() {
    _email.dispose();
    super.dispose();
  }

  Future<void> _send() async {
    if (_busy) return;
    final email = _email.text.trim();
    if (!RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]+$').hasMatch(email)) {
      setState(() => _message = 'Enter a valid email address.');
      return;
    }
    setState(() {
      _busy = true;
      _message = null;
    });
    try {
      final sender = widget.sendResetEmail;
      if (sender != null) {
        await sender(email);
      } else {
        await FirebaseAuth.instance.sendPasswordResetEmail(email: email);
      }
      if (mounted) {
        setState(
          () => _message =
              'If this account exists, a reset link has been sent. Check your inbox and spam folder.',
        );
      }
    } on FirebaseAuthException catch (error) {
      if (mounted) {
        setState(
          () => _message = error.code == 'user-not-found'
              ? 'If this account exists, a reset link has been sent. Check your inbox and spam folder.'
              : error.code == 'too-many-requests'
              ? 'Too many reset requests. Please wait before trying again.'
              : 'Unable to send the reset email. Please check your connection and try again.',
        );
      }
    } catch (_) {
      if (mounted) {
        setState(
          () => _message =
              'Unable to send the reset email. Please try again shortly.',
        );
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Reset password')),
    body: Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 440),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Enter your Legal Lens email to receive a password-reset link.',
              ),
              const SizedBox(height: 20),
              TextField(
                controller: _email,
                enabled: !_busy,
                keyboardType: TextInputType.emailAddress,
                autocorrect: false,
                enableSuggestions: false,
                textCapitalization: TextCapitalization.none,
                autofillHints: const [AutofillHints.email],
                decoration: const InputDecoration(labelText: 'Email address'),
                onSubmitted: (_) {
                  if (!_busy) _send();
                },
              ),
              const SizedBox(height: 16),
              if (_message != null)
                Semantics(liveRegion: true, child: Text(_message!)),
              const SizedBox(height: 16),
              FilledButton(
                onPressed: _busy ? null : _send,
                child: Text(_busy ? 'Sending…' : 'Send reset link'),
              ),
              TextButton(
                onPressed: () => context.go('/login'),
                child: const Text('Back to sign in'),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}
