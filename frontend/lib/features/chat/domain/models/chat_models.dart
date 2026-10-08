class ChatConversation {
  const ChatConversation({
    required this.id,
    required this.title,
    required this.createdAt,
    required this.messages,
    this.backendConversationId,
  });

  final String id;
  final String title;
  final DateTime createdAt;
  final List<ChatMessage> messages;

  /// Conversation ID returned by the LegalLens FastAPI backend.
  ///
  /// This is used when sending future messages so the backend
  /// can maintain conversation memory/context.
  final String? backendConversationId;

  ChatConversation copyWith({
    String? id,
    String? title,
    DateTime? createdAt,
    List<ChatMessage>? messages,
    String? backendConversationId,
  }) {
    return ChatConversation(
      id: id ?? this.id,
      title: title ?? this.title,
      createdAt: createdAt ?? this.createdAt,
      messages: messages ?? this.messages,
      backendConversationId:
          backendConversationId ?? this.backendConversationId,
    );
  }
}

// ============================================================
// MESSAGE ROLE
// ============================================================

enum MessageRole { user, assistant }

// ============================================================
// CHAT MESSAGE
// ============================================================

class ChatMessage {
  const ChatMessage({
    required this.id,
    required this.content,
    required this.role,
    required this.createdAt,
    this.citations = const [],
  });

  final String id;
  final String content;
  final MessageRole role;
  final DateTime createdAt;
  final List<ChatCitation> citations;
}

class ChatCitation {
  const ChatCitation({required this.filename, required this.page});

  final String filename;
  final int page;
}

// ============================================================
// BACKEND CHAT RESPONSE
// ============================================================

class ChatResponse {
  const ChatResponse({required this.message, this.conversationId});

  final ChatMessage message;

  /// Conversation ID returned by FastAPI.
  final String? conversationId;
}
