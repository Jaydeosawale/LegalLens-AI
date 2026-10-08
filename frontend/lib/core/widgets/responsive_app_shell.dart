import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/auth/providers/auth_provider.dart';
import '../../features/platform/providers/platform_permissions_provider.dart';
import '../auth/user_role.dart';
import '../navigation/navigation_config.dart';
import '../navigation/navigation_item.dart';
import '../responsive/app_breakpoints.dart';
import '../theme/app_colors.dart';
import 'app_navigation_drawer.dart';
import 'navigation_sidebar.dart';

class ResponsiveAppShell extends ConsumerWidget {
  const ResponsiveAppShell({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final role = authState.role ?? UserRole.user;

    final platformPermissionsState = ref.watch(platformPermissionsProvider);

    final roleNavigationItems = NavigationConfig.forRole(role);

    final navigationItems = roleNavigationItems.where((item) {
      // =====================================================
      // MODULE DOES NOT REQUIRE PLATFORM PERMISSION
      // =====================================================

      if (item.platformModule == null) {
        return true;
      }

      // =====================================================
      // SUPER ADMIN
      //
      // Always has access to everything allowed by role.
      // =====================================================

      if (role == UserRole.superAdmin) {
        return true;
      }

      // =====================================================
      // NORMAL USER
      //
      // Platform permissions do not control normal users.
      // =====================================================

      if (!role.isAdministrator) {
        return true;
      }

      // =====================================================
      // ADMIN
      //
      // IMPORTANT:
      // Do not hide navigation while permissions are loading.
      // =====================================================

      if (platformPermissionsState.isLoading) {
        return false;
      }

      return platformPermissionsState.isModuleEnabled(item.platformModule!);
    }).toList();

    return LayoutBuilder(
      builder: (context, constraints) {
        final isDesktop = constraints.maxWidth >= AppBreakpoints.tablet;

        if (isDesktop) {
          return _DesktopShell(navigationItems: navigationItems, child: child);
        }

        return _MobileShell(navigationItems: navigationItems, child: child);
      },
    );
  }
}

class _DesktopShell extends StatelessWidget {
  const _DesktopShell({required this.navigationItems, required this.child});

  final List<NavigationItem> navigationItems;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.workspace,
      body: Row(
        children: [
          NavigationSidebar(navigationItems: navigationItems),
          Expanded(
            child: ColoredBox(color: AppColors.workspace, child: child),
          ),
        ],
      ),
    );
  }
}

class _MobileShell extends StatelessWidget {
  const _MobileShell({required this.navigationItems, required this.child});

  final List<NavigationItem> navigationItems;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.workspace,
      drawer: AppNavigationDrawer(navigationItems: navigationItems),
      appBar: AppBar(
        title: const Text(
          'Legal Lens',
          style: TextStyle(fontWeight: FontWeight.w700),
        ),
      ),
      body: ColoredBox(color: AppColors.workspace, child: child),
    );
  }
}
