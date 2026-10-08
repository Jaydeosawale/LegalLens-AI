import 'package:flutter/material.dart';

import '../auth/user_role.dart';

class NavigationItem {
  const NavigationItem({
    required this.label,
    required this.icon,
    required this.route,
    required this.allowedRoles,
    this.platformModule,
  });

  final String label;
  final IconData icon;
  final String route;
  final List<UserRole> allowedRoles;

  // =========================================================
  // PLATFORM MODULE
  //
  // Used to control ADMIN navigation access.
  //
  // SUPER_ADMIN always has access.
  // USER navigation is not affected by platform permissions.
  // =========================================================

  final String? platformModule;
}
