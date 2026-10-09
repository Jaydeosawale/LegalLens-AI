import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend_flutter/features/chat/data/services/chat_api_service.dart';
import 'package:frontend_flutter/features/chat/domain/models/chat_models.dart';
import 'package:frontend_flutter/features/chat/domain/repositories/chat_repository.dart';
import 'package:frontend_flutter/features/chat/presentation/controllers/chat_controller.dart';

class FailingChatRepository implements ChatRepository {
  FailingChatRepository(this.error);
  final Exception error;

  @override
  Future<ChatResponse> sendMessage({
    required String question,
    String? conversationId,
    File? image,
  }) async => throw error;
}

void main() {
  test('daily limit message appears in the RAG chat unchanged', () async {
    const message = 'Daily chat limit reached. You have used your 10 chat messages for today. '
        'You can chat again after the daily reset at 05:30 IST (00:00 UTC), '
        'or ask the super admin to increase your limit.';
    final controller = ChatController(repository: FailingChatRepository(
      const ChatApiException(message: message, statusCode: 429),
    ));
    await controller.sendMessage('What is income tax?');
    expect(controller.errorMessage, message);
    expect(controller.selectedConversation!.messages.last.content, message);
    expect(controller.isLoading, isFalse);
    controller.dispose();
  });

  test('provider quota is not reported as a connection failure', () async {
    const message = 'The AI service has reached its free usage limit. Please try again later.';
    final controller = ChatController(repository: FailingChatRepository(
      const ChatApiException(message: message, statusCode: 503),
    ));
    await controller.sendMessage('income tax');
    expect(controller.errorMessage, message);
    controller.dispose();
  });
}
