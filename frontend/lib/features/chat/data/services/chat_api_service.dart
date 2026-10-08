import 'dart:io';

import 'package:dio/dio.dart';

class ChatApiService {
  ChatApiService({required this._dio, required this._baseUrl});

  final Dio _dio;
  final String _baseUrl;

  // ============================================================
  // SEND MESSAGE
  // ============================================================

  Future<Map<String, dynamic>> sendMessage({
    required String question,
    String? conversationId,
    File? image,
  }) async {
    final formData = FormData.fromMap({
      'question': question,

      if (conversationId != null && conversationId.isNotEmpty)
        'conversation_id': conversationId,

      if (image != null)
        'image': await MultipartFile.fromFile(
          image.path,
          filename: image.path.split('/').last,
        ),
    });

    try {
      final response = await _dio.post<Map<String, dynamic>>(
        '$_baseUrl/chat/',
        data: formData,
      );

      return response.data ?? {};
    } on DioException catch (error) {
      throw ChatApiException(
        message: _extractErrorMessage(error),
        statusCode: error.response?.statusCode,
      );
    }
  }

  // ============================================================
  // ERROR HANDLING
  // ============================================================

  String _extractErrorMessage(DioException error) {
    final data = error.response?.data;

    if (data is Map<String, dynamic>) {
      final detail = data['detail'];

      if (detail != null) {
        return detail.toString();
      }
    }

    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return 'The Legal Lens server is taking too long to respond.';

      case DioExceptionType.connectionError:
        return 'Unable to connect to the Legal Lens server.';

      default:
        return 'Unable to process your legal question.';
    }
  }
}

// ============================================================
// CHAT API EXCEPTION
// ============================================================

class ChatApiException implements Exception {
  const ChatApiException({required this.message, this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() {
    return 'ChatApiException($statusCode): $message';
  }
}
