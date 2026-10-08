import 'dart:io';

import '../models/chat_models.dart';

abstract class ChatRepository {
  Future<ChatResponse> sendMessage({
    required String question,
    String? conversationId,
    File? image,
  });
}
