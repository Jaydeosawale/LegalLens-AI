import 'package:flutter/foundation.dart';
import 'package:dio/dio.dart';

import '../../domain/models/chat_models.dart';
import '../../domain/repositories/chat_repository.dart';

class ChatController extends ChangeNotifier {
  ChatController({required this.repository, this.dio});

  final ChatRepository repository;
  final Dio? dio;
  bool _disposed = false;

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }

  @override
  void notifyListeners() {
    if (!_disposed) super.notifyListeners();
  }

  ChatConversation _parseConversation(Map<String, dynamic> row) =>
      ChatConversation(
        id: row['id'].toString(),
        backendConversationId: row['id'].toString(),
        title: row['title']?.toString() ?? 'Conversation',
        createdAt: DateTime.parse(row['created_at'].toString()),
        messages: ((row['messages'] as List?) ?? [])
            .map(
              (m) => ChatMessage(
                id: m['id'].toString(),
                content: m['content'].toString(),
                role: m['role'] == 'user'
                    ? MessageRole.user
                    : MessageRole.assistant,
                createdAt: DateTime.parse(m['created_at'].toString()),
                citations: ((m['citations'] as List?) ?? [])
                    .map(
                      (c) => ChatCitation(
                        filename: c['filename'].toString(),
                        page: (c['page'] as num?)?.toInt() ?? 1,
                      ),
                    )
                    .toList(),
              ),
            )
            .toList(),
      );

  Future<void> loadConversations({String? selectedId}) async {
    if (dio == null) return;
    try {
      final rows = (await dio!.get('/conversations/')).data as List;
      if (_disposed) return;
      _conversations.clear();
      _conversations.addAll(
        rows.map((row) => _parseConversation(Map<String, dynamic>.from(row))),
      );
      if (selectedId != null) await openConversation(selectedId);
      notifyListeners();
    } catch (_) {
      _errorMessage = 'Unable to load your conversation history.';
      notifyListeners();
    }
  }

  Future<void> openConversation(String id) async {
    if (dio == null) return;
    _isLoading = true;
    notifyListeners();
    try {
      final row = Map<String, dynamic>.from(
        (await dio!.get('/conversations/$id')).data,
      );
      if (_disposed) return;
      final conversation = _parseConversation(row);
      final index = _conversations.indexWhere((c) => c.id == id);
      if (index == -1) {
        _conversations.insert(0, conversation);
      } else {
        _conversations[index] = conversation;
      }
      _selectedConversationId = id;
      _errorMessage = null;
    } catch (_) {
      _errorMessage = 'Unable to open this conversation.';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  final List<ChatConversation> _conversations = [];

  String? _selectedConversationId;

  bool _isLoading = false;

  String? _errorMessage;

  List<ChatConversation> get conversations => List.unmodifiable(_conversations);

  String? get selectedConversationId => _selectedConversationId;

  bool get isLoading => _isLoading;

  String? get errorMessage => _errorMessage;

  ChatConversation? get selectedConversation {
    if (_selectedConversationId == null) {
      return null;
    }

    try {
      return _conversations.firstWhere(
        (conversation) => conversation.id == _selectedConversationId,
      );
    } catch (_) {
      return null;
    }
  }

  // ============================================================
  // CREATE NEW CHAT
  // ============================================================

  void createNewChat() {
    if (_isLoading) return;
    final conversation = ChatConversation(
      id: DateTime.now().microsecondsSinceEpoch.toString(),
      title: 'New Legal Conversation',
      createdAt: DateTime.now(),
      messages: const [],
    );

    _conversations.insert(0, conversation);

    _selectedConversationId = conversation.id;

    _errorMessage = null;

    notifyListeners();
  }

  // ============================================================
  // SELECT CONVERSATION
  // ============================================================

  void selectConversation(String conversationId) {
    if (_isLoading) return;
    final conversation = _conversations.firstWhere(
      (c) => c.id == conversationId,
    );
    if (conversation.backendConversationId != null &&
        conversation.messages.isEmpty) {
      openConversation(conversationId);
      return;
    }
    _selectedConversationId = conversationId;

    _errorMessage = null;

    notifyListeners();
  }

  // ============================================================
  // SEND MESSAGE
  // ============================================================

  Future<void> sendMessage(String message) async {
    final trimmedMessage = message.trim();

    if (trimmedMessage.isEmpty || _isLoading) {
      return;
    }

    // ----------------------------------------------------------
    // CREATE CONVERSATION IF NEEDED
    // ----------------------------------------------------------

    if (_selectedConversationId == null) {
      createNewChat();
    }

    final localConversationId = _selectedConversationId;

    if (localConversationId == null) {
      return;
    }

    final conversationIndex = _conversations.indexWhere(
      (conversation) => conversation.id == localConversationId,
    );

    if (conversationIndex == -1) {
      return;
    }

    final conversation = _conversations[conversationIndex];

    // ----------------------------------------------------------
    // CREATE USER MESSAGE
    // ----------------------------------------------------------

    final userMessage = ChatMessage(
      id: DateTime.now().microsecondsSinceEpoch.toString(),
      content: trimmedMessage,
      role: MessageRole.user,
      createdAt: DateTime.now(),
    );

    // ----------------------------------------------------------
    // UPDATE TITLE
    // ----------------------------------------------------------

    final updatedTitle = conversation.messages.isEmpty
        ? _generateConversationTitle(trimmedMessage)
        : conversation.title;

    _conversations[conversationIndex] = conversation.copyWith(
      title: updatedTitle,
      messages: [...conversation.messages, userMessage],
    );

    _isLoading = true;

    _errorMessage = null;

    notifyListeners();

    // ==========================================================
    // CALL BACKEND
    // ==========================================================

    try {
      final response = await repository.sendMessage(
        question: trimmedMessage,

        // Use backend conversation ID when available.
        conversationId: conversation.backendConversationId,
      );

      final latestConversationIndex = _conversations.indexWhere(
        (conversation) => conversation.id == localConversationId,
      );

      if (latestConversationIndex == -1) {
        return;
      }

      final latestConversation = _conversations[latestConversationIndex];

      _conversations[latestConversationIndex] = latestConversation.copyWith(
        messages: [...latestConversation.messages, response.message],

        // Save backend conversation ID.
        backendConversationId:
            response.conversationId ?? latestConversation.backendConversationId,
      );
    } catch (error) {
      _errorMessage = _getErrorMessage(error);

      final latestConversationIndex = _conversations.indexWhere(
        (conversation) => conversation.id == localConversationId,
      );

      if (latestConversationIndex != -1) {
        final latestConversation = _conversations[latestConversationIndex];

        final errorChatMessage = ChatMessage(
          id: DateTime.now().microsecondsSinceEpoch.toString(),
          content: _errorMessage!,
          role: MessageRole.assistant,
          createdAt: DateTime.now(),
        );

        _conversations[latestConversationIndex] = latestConversation.copyWith(
          messages: [...latestConversation.messages, errorChatMessage],
        );
      }
    } finally {
      _isLoading = false;

      notifyListeners();
    }
  }

  // ============================================================
  // TITLE GENERATOR
  // ============================================================

  String _generateConversationTitle(String message) {
    if (message.length <= 38) {
      return message;
    }

    return '${message.substring(0, 38)}...';
  }

  // ============================================================
  // ERROR HANDLING
  // ============================================================

  String _getErrorMessage(Object error) {
    return '''
Sorry, I couldn't connect to Legal Lens.

Please make sure the Legal Lens backend server is running and try again.
''';
  }
}
