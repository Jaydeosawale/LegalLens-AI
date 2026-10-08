import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/providers/auth_provider.dart';
import '../auth/user_role.dart';
import '../navigation/navigation_config.dart';
import '../../features/platform/providers/platform_permissions_provider.dart';
import '../../features/auth/presentation/login_page.dart';
import 'responsive_app_shell.dart';

class AppRoleShell extends ConsumerWidget {
  const AppRoleShell({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);
    if (!auth.isAuthenticated) return const LoginPage();
    if (auth.isLoading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final role = auth.role ?? UserRole.user;
    final path = GoRouterState.of(context).uri.path;
    if (role == UserRole.user && path == '/home') {
      final router = GoRouter.of(context);
      WidgetsBinding.instance.addPostFrameCallback((_) => router.go('/chat'));
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final matches = NavigationConfig.items.where((item) => item.route == path);
    if (matches.isNotEmpty) {
      final item = matches.first;
      var allowed = item.allowedRoles.contains(role);
      if (allowed && role == UserRole.admin && item.platformModule != null) {
        final permissions = ref.watch(platformPermissionsProvider);
        if (permissions.isLoading) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        allowed = permissions.isModuleEnabled(item.platformModule!);
      }
      if (!allowed) {
        return ResponsiveAppShell(
          child: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.lock_outline, size: 40),
                const SizedBox(height: 16),
                const Text('This section is unavailable for your account.'),
                TextButton(
                  onPressed: () => context.go('/chat'),
                  child: const Text('Go to research'),
                ),
              ],
            ),
          ),
        );
      }
    }

    // =========================================================
    // ADMIN + SUPER ADMIN
    //
    // Keep LegalLens platform navigation persistent across
    // ALL application pages.
    // =========================================================

    if (role == UserRole.admin || role == UserRole.superAdmin) {
      return ResponsiveAppShell(child: child);
    }

    // =========================================================
    // NORMAL USER
    //
    // Preserve the normal standalone page experience.
    // =========================================================

    return ResponsiveAppShell(child: child);
  }
}
