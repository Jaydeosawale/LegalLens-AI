import 'package:dio/dio.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/repositories/chat_repository_impl.dart';
import '../data/services/chat_api_service.dart';
import '../domain/repositories/chat_repository.dart';

// ============================================================
// API CONFIGURATION
// ============================================================

const String _baseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://127.0.0.1:8000',
);

// ============================================================
// DIO
// ============================================================

final dioProvider = Provider<Dio>((ref) {
  final dio = Dio(
    BaseOptions(
      baseUrl: _baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 60),
      sendTimeout: const Duration(seconds: 30),
      headers: {'Accept': 'application/json'},
    ),
  );

  // ==========================================================
  // FIREBASE AUTH TOKEN INTERCEPTOR
  // ==========================================================

  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) async {
        final firebaseUser = FirebaseAuth.instance.currentUser;

        if (firebaseUser != null) {
          final idToken = await firebaseUser.getIdToken();

          if (idToken != null && idToken.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $idToken';
          }
        }

        handler.next(options);
      },
    ),
  );

  return dio;
});

// ============================================================
// CHAT API SERVICE
// ============================================================

final chatApiServiceProvider = Provider<ChatApiService>((ref) {
  final dio = ref.watch(dioProvider);

  return ChatApiService(dio: dio, baseUrl: _baseUrl);
});

// ============================================================
// CHAT REPOSITORY
// ============================================================

final chatRepositoryProvider = Provider<ChatRepository>((ref) {
  final apiService = ref.watch(chatApiServiceProvider);

  return ChatRepositoryImpl(apiService: apiService);
});
