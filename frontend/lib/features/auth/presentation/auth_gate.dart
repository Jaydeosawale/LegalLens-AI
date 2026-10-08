import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/auth/user_role.dart';
import '../providers/auth_provider.dart';
import 'login_page.dart';

class AuthGate extends ConsumerWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);

    // Keep the form mounted while sign-in is pending so failures remain visible.
    if (!authState.isAuthenticated) {
      return const LoginPage();
    }

    final role = authState.role ?? UserRole.user;

    final router = GoRouter.of(context);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      router.go(role == UserRole.user ? '/chat' : '/home');
    });
    return const Scaffold(body: Center(child: CircularProgressIndicator()));
  }
}
