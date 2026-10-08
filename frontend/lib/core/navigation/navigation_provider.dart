import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/auth/models/app_user.dart';
import '../../features/platform/providers/platform_permissions_provider.dart';
import '../auth/user_role.dart';
import 'navigation_config.dart';
import 'navigation_item.dart';

final navigationItemsProvider = Provider.family<List<NavigationItem>, AppUser>((
  ref,
  user,
) {
  final permissionsState = ref.watch(platformPermissionsProvider);

  final roleItems = NavigationConfig.forRole(user.role);

  // =========================================================
  // SUPER ADMIN
  //
  // Always has access to everything allowed by role.
  // =========================================================

  if (user.role == UserRole.superAdmin) {
    return roleItems;
  }

  // =========================================================
  // NORMAL USER
  //
  // Only sees normal user navigation.
  // =========================================================

  if (!user.role.isAdministrator) {
    return roleItems;
  }

  // =========================================================
  // ADMIN
  //
  // Role access + platform permissions.
  // =========================================================

  return roleItems.where((item) {
    final moduleName = _routeToPlatformModule(item.route);

    // No platform restriction for this route.
    if (moduleName == null) {
      return true;
    }

    return permissionsState.isModuleEnabled(moduleName);
  }).toList();
});

// =========================================================
// ROUTE → BACKEND PLATFORM MODULE
// =========================================================

String? _routeToPlatformModule(String route) {
  switch (route) {
    case '/home':
      return 'dashboard';

    case '/documents':
      return 'documents';

    case '/history':
      return 'research_history';

    case '/advanced':
      return 'advanced_research';

    case '/knowledge-base':
      return 'knowledge_base';

    case '/analytics':
      return 'analytics';

    case '/users':
      return 'users';

    default:
      return null;
  }
}
