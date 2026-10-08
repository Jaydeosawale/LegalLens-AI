import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';

import '../../../core/theme/app_colors.dart';
import '../domain/models/chat_models.dart';

class ChatMessages extends StatefulWidget {
  const ChatMessages({
    super.key,
    required this.messages,
    required this.isLoading,
  });

  final List<ChatMessage> messages;
  final bool isLoading;

  @override
  State<ChatMessages> createState() => _ChatMessagesState();
}

class _ChatMessagesState extends State<ChatMessages> {
  final ScrollController _scrollController = ScrollController();

  @override
  void didUpdateWidget(covariant ChatMessages oldWidget) {
    super.didUpdateWidget(oldWidget);

    if (oldWidget.messages.length != widget.messages.length ||
        oldWidget.isLoading != widget.isLoading) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _scrollToBottom();
      });
    }
  }

  void _scrollToBottom() {
    if (!_scrollController.hasClients) return;

    _scrollController.animateTo(
      _scrollController.position.maxScrollExtent,
      duration: const Duration(milliseconds: 350),
      curve: Curves.easeOutCubic,
    );
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      controller: _scrollController,
      padding: const EdgeInsets.fromLTRB(32, 32, 32, 40),
      children: [
        Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 900),
            child: Column(
              children: [
                ...widget.messages.map(
                  (message) => _MessageBubble(message: message),
                ),

                if (widget.isLoading) const _TypingIndicator(),

                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

// =====================================================================
// MESSAGE BUBBLE
// =====================================================================

class _MessageBubble extends StatelessWidget {
  const _MessageBubble({required this.message});

  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    final isUser = message.role == MessageRole.user;

    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Align(
        alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
        child: ConstrainedBox(
          constraints: BoxConstraints(maxWidth: isUser ? 680 : 780),
          child: Row(
            mainAxisAlignment: isUser
                ? MainAxisAlignment.end
                : MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // =====================================================
              // LEGALLENS AI AVATAR
              // =====================================================
              if (!isUser) ...[
                const _LegalLensAvatar(),

                const SizedBox(width: 14),
              ],

              // =====================================================
              // MESSAGE CONTENT
              // =====================================================
              Flexible(
                child: Column(
                  crossAxisAlignment: isUser
                      ? CrossAxisAlignment.end
                      : CrossAxisAlignment.start,
                  children: [
                    if (!isUser) ...[
                      const Padding(
                        padding: EdgeInsets.only(left: 4, bottom: 8),
                        child: Text(
                          'Legal Lens',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ),
                    ],

                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 16,
                      ),
                      decoration: BoxDecoration(
                        color: isUser
                            ? AppColors.inkNavy
                            : AppColors.surfaceMuted,

                        borderRadius: isUser
                            ? const BorderRadius.only(
                                topLeft: Radius.circular(18),
                                topRight: Radius.circular(18),
                                bottomLeft: Radius.circular(18),
                                bottomRight: Radius.circular(6),
                              )
                            : BorderRadius.circular(16),

                        border: Border.all(
                          color: isUser ? AppColors.inkNavy : AppColors.border,
                        ),

                        boxShadow: isUser
                            ? const []
                            : [
                                BoxShadow(
                                  color: Colors.black.withValues(alpha: 0.025),
                                  blurRadius: 12,
                                  offset: const Offset(0, 3),
                                ),
                              ],
                      ),
                      child: isUser
                          ? SelectableText(
                              message.content,
                              style: const TextStyle(
                                fontSize: 15,
                                height: 1.65,
                                color: AppColors.textOnDark,
                              ),
                            )
                          : MarkdownBody(
                              data: message.content,
                              selectable: true,
                              styleSheet: MarkdownStyleSheet(
                                p: const TextStyle(
                                  fontSize: 15,
                                  height: 1.7,
                                  color: AppColors.textPrimary,
                                ),
                                h1: const TextStyle(
                                  fontSize: 24,
                                  height: 1.3,
                                  fontWeight: FontWeight.w700,
                                  color: AppColors.inkNavy,
                                ),
                                h2: const TextStyle(
                                  fontSize: 20,
                                  height: 1.35,
                                  fontWeight: FontWeight.w700,
                                  color: AppColors.inkNavy,
                                ),
                                h3: const TextStyle(
                                  fontSize: 17,
                                  height: 1.4,
                                  fontWeight: FontWeight.w700,
                                  color: AppColors.inkNavy,
                                ),
                                strong: const TextStyle(
                                  fontWeight: FontWeight.w700,
                                  color: AppColors.inkNavy,
                                ),
                                em: const TextStyle(
                                  fontStyle: FontStyle.italic,
                                ),
                                blockquote: const TextStyle(
                                  fontSize: 15,
                                  height: 1.6,
                                  color: AppColors.textSecondary,
                                  fontStyle: FontStyle.italic,
                                ),
                                code: const TextStyle(
                                  fontSize: 13,
                                  fontFamily: 'monospace',
                                  color: AppColors.inkNavy,
                                ),
                                listBullet: const TextStyle(
                                  fontSize: 15,
                                  color: AppColors.inkNavy,
                                ),
                                horizontalRuleDecoration: const BoxDecoration(
                                  border: Border(
                                    top: BorderSide(color: AppColors.border),
                                  ),
                                ),
                              ),
                            ),
                    ),

                    if (!isUser && message.citations.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 8,
                        runSpacing: 6,
                        children: [
                          for (final citation in message.citations)
                            Tooltip(
                              message: 'Source document, page ${citation.page}',
                              child: ConstrainedBox(
                                constraints: const BoxConstraints(
                                  maxWidth: 260,
                                ),
                                child: Chip(
                                  avatar: const Icon(
                                    Icons.description_outlined,
                                    size: 16,
                                  ),
                                  label: Text(
                                    '${citation.filename}, p. ${citation.page}',
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              ),
                            ),
                        ],
                      ),
                    ],

                    const SizedBox(height: 6),

                    Text(
                      _formatTime(message.createdAt),
                      style: const TextStyle(
                        fontSize: 11,
                        color: AppColors.textMuted,
                      ),
                    ),
                  ],
                ),
              ),

              // =====================================================
              // USER AVATAR
              // =====================================================
              if (isUser) ...[const SizedBox(width: 14), const _UserAvatar()],
            ],
          ),
        ),
      ),
    );
  }

  String _formatTime(DateTime dateTime) {
    final hour = dateTime.hour > 12
        ? dateTime.hour - 12
        : dateTime.hour == 0
        ? 12
        : dateTime.hour;

    final minute = dateTime.minute.toString().padLeft(2, '0');

    final period = dateTime.hour >= 12 ? 'PM' : 'AM';

    return '$hour:$minute $period';
  }
}

// =====================================================================
// LEGALLENS AI AVATAR
// =====================================================================

class _LegalLensAvatar extends StatelessWidget {
  const _LegalLensAvatar();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 42,
      height: 42,
      decoration: BoxDecoration(
        color: AppColors.inkNavy,
        borderRadius: BorderRadius.circular(13),
      ),
      child: const Icon(
        Icons.balance_rounded,
        color: AppColors.antiqueGold,
        size: 22,
      ),
    );
  }
}

// =====================================================================
// USER AVATAR
// =====================================================================

class _UserAvatar extends StatelessWidget {
  const _UserAvatar();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 42,
      height: 42,
      decoration: const BoxDecoration(
        color: AppColors.legalNavyLight,
        shape: BoxShape.circle,
      ),
      child: const Icon(
        Icons.person_rounded,
        color: AppColors.inkNavy,
        size: 21,
      ),
    );
  }
}

// =====================================================================
// TYPING INDICATOR
// =====================================================================

class _TypingIndicator extends StatelessWidget {
  const _TypingIndicator();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.only(bottom: 28),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _LegalLensAvatar(),

          SizedBox(width: 14),

          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: EdgeInsets.only(left: 4, bottom: 8),
                child: Text(
                  'Legal Lens',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textSecondary,
                  ),
                ),
              ),

              _TypingBubble(),
            ],
          ),
        ],
      ),
    );
  }
}

// =====================================================================
// TYPING BUBBLE
// =====================================================================

class _TypingBubble extends StatelessWidget {
  const _TypingBubble();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.borderLight),
      ),
      child: const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              color: AppColors.antiqueGold,
            ),
          ),

          SizedBox(width: 12),

          Text(
            'Legal Lens is analyzing...',
            style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
          ),
        ],
      ),
    );
  }
}
