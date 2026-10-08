import 'dart:io';

import '../../domain/models/chat_models.dart';
import '../../domain/repositories/chat_repository.dart';
import '../services/chat_api_service.dart';

class ChatRepositoryImpl implements ChatRepository {
  ChatRepositoryImpl({required this._apiService});

  final ChatApiService _apiService;

  @override
  Future<ChatResponse> sendMessage({
    required String question,
    String? conversationId,
    File? image,
  }) async {
    final response = await _apiService.sendMessage(
      question: question,
      conversationId: conversationId,
      image: image,
    );

    final answer =
        response['answer']?.toString() ??
        response['response']?.toString() ??
        'No response received from Legal Lens.';

    final citations = (response['citations'] as List<dynamic>? ?? [])
        .whereType<Map<String, dynamic>>()
        .map(
          (item) => ChatCitation(
            filename: item['filename']?.toString() ?? 'Unknown source',
            page: (item['page'] as num?)?.toInt() ?? 0,
          ),
        )
        .toList();

    final message = ChatMessage(
      id:
          response['message_id']?.toString() ??
          response['chat_id']?.toString() ??
          DateTime.now().microsecondsSinceEpoch.toString(),
      content: answer,
      role: MessageRole.assistant,
      createdAt: DateTime.now(),
      citations: citations,
    );

    return ChatResponse(
      message: message,
      conversationId: response['conversation_id']?.toString(),
    );
  }
}
