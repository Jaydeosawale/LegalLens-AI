import 'package:dio/dio.dart';

import '../../models/app_user.dart';

class AuthApiService {
  const AuthApiService(this._dio);

  final Dio _dio;

  // =========================================================
  // CURRENT LEGALLENS USER
  // =========================================================

  Future<AppUser> getCurrentUser() async {
    final response = await _dio.get<Map<String, dynamic>>('/auth/me');

    final data = response.data;

    if (data == null) {
      throw Exception('Unable to load user profile.');
    }

    return AppUser.fromJson(data);
  }
}
