import 'package:dio/dio.dart';

import '../../models/platform_permission.dart';

class PlatformApiService {
  const PlatformApiService(this._dio);

  final Dio _dio;

  // =========================================================
  // GET PLATFORM PERMISSIONS
  // =========================================================

  Future<List<PlatformPermission>> getPlatformPermissions() async {
    final response = await _dio.get<List<dynamic>>('/auth/permissions');

    final data = response.data ?? [];

    return data
        .map(
          (item) => PlatformPermission.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  // =========================================================
  // UPDATE PLATFORM PERMISSION
  // =========================================================

  Future<PlatformPermission> updatePlatformPermission({
    required String moduleName,
    required bool enabledForAdmin,
  }) async {
    final response = await _dio.put<Map<String, dynamic>>(
      '/admin/platform-permissions/$moduleName',
      data: {'enabled_for_admin': enabledForAdmin},
    );

    final data = response.data;

    if (data == null) {
      throw Exception('Unable to update platform permission.');
    }

    return PlatformPermission.fromJson(data);
  }
}
