import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/platform_permission.dart';
import 'platform_api_provider.dart';
import '../../auth/providers/auth_provider.dart';
import '../../../core/auth/user_role.dart';

// ============================================================
// PLATFORM PERMISSIONS STATE
// ============================================================

class PlatformPermissionsState {
  const PlatformPermissionsState({
    this.permissions = const [],
    this.isLoading = false,
    this.errorMessage,
  });

  final List<PlatformPermission> permissions;
  final bool isLoading;
  final String? errorMessage;

  PlatformPermissionsState copyWith({
    List<PlatformPermission>? permissions,
    bool? isLoading,
    String? errorMessage,
    bool clearError = false,
  }) {
    return PlatformPermissionsState(
      permissions: permissions ?? this.permissions,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }

  // =========================================================
  // CHECK MODULE ACCESS
  // =========================================================

  bool isModuleEnabled(String moduleName) {
    for (final permission in permissions) {
      if (permission.moduleName == moduleName) {
        return permission.enabledForAdmin;
      }
    }

    // Default false until permissions are loaded.
    return false;
  }
}

// ============================================================
// PLATFORM PERMISSIONS NOTIFIER
// ============================================================

class PlatformPermissionsNotifier extends Notifier<PlatformPermissionsState> {
  @override
  PlatformPermissionsState build() {
    final role = ref.watch(authProvider).role;
    if (role == null || !role.isAdministrator) {
      return const PlatformPermissionsState();
    }
    Future.microtask(loadPermissions);

    return const PlatformPermissionsState(isLoading: true);
  }

  // =========================================================
  // LOAD PERMISSIONS
  // =========================================================

  Future<void> loadPermissions() async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final apiService = ref.read(platformApiServiceProvider);

      final permissions = await apiService.getPlatformPermissions();

      state = state.copyWith(permissions: permissions, isLoading: false);
    } catch (error) {
      state = state.copyWith(isLoading: false, errorMessage: error.toString());
    }
  }

  // =========================================================
  // UPDATE PERMISSION
  // =========================================================

  Future<void> updatePermission({
    required String moduleName,
    required bool enabledForAdmin,
  }) async {
    final previousPermissions = state.permissions;

    // -------------------------------------------------------
    // OPTIMISTIC UI UPDATE
    // -------------------------------------------------------

    final updatedPermissions = previousPermissions.map((permission) {
      if (permission.moduleName == moduleName) {
        return permission.copyWith(enabledForAdmin: enabledForAdmin);
      }

      return permission;
    }).toList();

    state = state.copyWith(permissions: updatedPermissions, clearError: true);

    try {
      final apiService = ref.read(platformApiServiceProvider);

      final updatedPermission = await apiService.updatePlatformPermission(
        moduleName: moduleName,
        enabledForAdmin: enabledForAdmin,
      );

      final finalPermissions = state.permissions.map((permission) {
        if (permission.moduleName == moduleName) {
          return updatedPermission;
        }

        return permission;
      }).toList();

      state = state.copyWith(permissions: finalPermissions);
    } catch (error) {
      // -----------------------------------------------------
      // ROLLBACK IF API FAILS
      // -----------------------------------------------------

      state = state.copyWith(
        permissions: state.permissions
            .map(
              (permission) => permission.moduleName == moduleName
                  ? previousPermissions.firstWhere(
                      (previous) => previous.moduleName == moduleName,
                    )
                  : permission,
            )
            .toList(),
        errorMessage: error.toString(),
      );

      rethrow;
    }
  }

  // =========================================================
  // REFRESH
  // =========================================================

  Future<void> refresh() async {
    await loadPermissions();
  }
}

// ============================================================
// PROVIDER
// ============================================================

final platformPermissionsProvider =
    NotifierProvider<PlatformPermissionsNotifier, PlatformPermissionsState>(
      PlatformPermissionsNotifier.new,
    );
