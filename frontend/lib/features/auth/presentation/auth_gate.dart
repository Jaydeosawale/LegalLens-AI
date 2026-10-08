import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/user_role.dart';
import '../../../core/widgets/app_role_shell.dart';
import '../../workspace/presentation/workspace_pages.dart';
import '../providers/auth_provider.dart';
import 'login_page.dart';

class AuthGate extends ConsumerWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);

    // =======================================================
    // LOADING
    // =======================================================

    if (authState.isLoading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    // =======================================================
    // NOT AUTHENTICATED
    // =======================================================

    if (!authState.isAuthenticated) {
      return const LoginPage();
    }

    final role = authState.role ?? UserRole.user;

    // =======================================================
    // NORMAL USER
    //
    // Focused Legal AI Assistant experience.
    // =======================================================

    if (!role.isAdministrator) {
      return const AppRoleShell(child: DashboardPage());
    }

    // =======================================================
    // ADMIN + SUPER ADMIN
    //
    // IMPORTANT:
    // AuthGate must also use AppRoleShell.
    //
    // Otherwise authenticated admins entering through "/"
    // bypass ResponsiveAppShell and NavigationSidebar.
    // =======================================================

    return const AppRoleShell(child: DashboardPage());
  }
}
