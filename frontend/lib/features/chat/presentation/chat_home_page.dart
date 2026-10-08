import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/user_role.dart';
import '../../../core/responsive/app_breakpoints.dart';
import '../../../core/theme/app_colors.dart';

import '../../auth/providers/auth_provider.dart';

import '../providers/chat_providers.dart';
import '../widgets/chat_input.dart';
import '../widgets/chat_messages.dart';
import '../widgets/chat_sidebar.dart';
import '../widgets/chat_welcome.dart';
import 'controllers/chat_controller.dart';

class ChatHomePage extends ConsumerStatefulWidget {
  const ChatHomePage({super.key, this.conversationId, this.initialQuestion});
  final String? conversationId;
  final String? initialQuestion;

  @override
  ConsumerState<ChatHomePage> createState() => _ChatHomePageState();
}

class _ChatHomePageState extends ConsumerState<ChatHomePage> {
  late final ChatController _controller;

  @override
  void initState() {
    super.initState();

    final repository = ref.read(chatRepositoryProvider);

    _controller = ChatController(
      repository: repository,
      dio: ref.read(dioProvider),
    );

    _controller.addListener(_onControllerChanged);
    _initialize();
  }

  Future<void> _initialize() async {
    await _controller.loadConversations(selectedId: widget.conversationId);
    if (mounted && widget.initialQuestion != null) {
      await _controller.sendMessage(widget.initialQuestion!);
    }
  }

  void _onControllerChanged() {
    if (mounted) {
      setState(() {});
    }
  }

  @override
  void dispose() {
    _controller.removeListener(_onControllerChanged);
    _controller.dispose();

    super.dispose();
  }

  void _sendMessage(String message) {
    _controller.sendMessage(message);
  }

  @override
  Widget build(BuildContext context) {
    final role = ref.watch(authProvider).role ?? UserRole.user;

    final chatContent = _ChatContent(
      controller: _controller,
      onSendMessage: _sendMessage,
    );

    // =========================================================
    // ADMIN + SUPER ADMIN
    //
    // Main navigation is already provided by ResponsiveAppShell.
    // =========================================================

    if (role == UserRole.admin || role == UserRole.superAdmin) {
      return chatContent;
    }

    // =========================================================
    // NORMAL USER
    // =========================================================

    return Scaffold(
      backgroundColor: AppColors.workspace,
      body: SafeArea(child: chatContent),
    );
  }
}

// ============================================================
// CHAT CONTENT
// ============================================================

class _ChatContent extends StatefulWidget {
  const _ChatContent({required this.controller, required this.onSendMessage});

  final ChatController controller;
  final ValueChanged<String> onSendMessage;

  @override
  State<_ChatContent> createState() => _ChatContentState();
}

class _ChatContentState extends State<_ChatContent> {
  // =========================================================
  // MOBILE CONVERSATION PANEL
  //
  // Closed by default.
  // =========================================================

  bool _isMobileSidebarOpen = false;

  void _toggleMobileSidebar() {
    setState(() {
      _isMobileSidebarOpen = !_isMobileSidebarOpen;
    });
  }

  void _closeMobileSidebar() {
    if (_isMobileSidebarOpen) {
      setState(() {
        _isMobileSidebarOpen = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isDesktop = constraints.maxWidth >= AppBreakpoints.tablet;

        if (isDesktop) {
          return _DesktopChatLayout(
            controller: widget.controller,
            onSendMessage: widget.onSendMessage,
          );
        }

        return _MobileChatLayout(
          controller: widget.controller,
          onSendMessage: widget.onSendMessage,
          isSidebarOpen: _isMobileSidebarOpen,
          onToggleSidebar: _toggleMobileSidebar,
          onCloseSidebar: _closeMobileSidebar,
        );
      },
    );
  }
}

// ============================================================
// DESKTOP CHAT LAYOUT
// ============================================================

class _DesktopChatLayout extends StatelessWidget {
  const _DesktopChatLayout({
    required this.controller,
    required this.onSendMessage,
  });

  final ChatController controller;
  final ValueChanged<String> onSendMessage;

  @override
  Widget build(BuildContext context) {
    final selectedConversation = controller.selectedConversation;

    return Row(
      children: [
        // =====================================================
        // CONVERSATION SIDEBAR
        // =====================================================

        SizedBox(
          width: 300,
          child: ChatSidebar(
            onNewChat: controller.createNewChat,
            conversations: controller.conversations,
            selectedConversationId: controller.selectedConversationId,
            onConversationSelected: controller.selectConversation,
          ),
        ),

        const VerticalDivider(
          width: 1,
          thickness: 1,
          color: AppColors.borderLight,
        ),

        // =====================================================
        // MAIN CHAT AREA
        // =====================================================
        Expanded(
          child: _ChatMainArea(
            controller: controller,
            selectedConversation: selectedConversation,
            onSendMessage: onSendMessage,
            showConversationButton: false,
          ),
        ),
      ],
    );
  }
}

// ============================================================
// MOBILE CHAT LAYOUT
// ============================================================

class _MobileChatLayout extends StatelessWidget {
  const _MobileChatLayout({
    required this.controller,
    required this.onSendMessage,
    required this.isSidebarOpen,
    required this.onToggleSidebar,
    required this.onCloseSidebar,
  });

  final ChatController controller;
  final ValueChanged<String> onSendMessage;

  final bool isSidebarOpen;

  final VoidCallback onToggleSidebar;
  final VoidCallback onCloseSidebar;

  @override
  Widget build(BuildContext context) {
    final selectedConversation = controller.selectedConversation;

    final screenWidth = MediaQuery.sizeOf(context).width;

    // =========================================================
    // MOBILE DRAWER WIDTH
    //
    // Keeps part of the main screen visible.
    // =========================================================

    final sidebarWidth = screenWidth < 380 ? screenWidth * 0.88 : 330.0;

    return Stack(
      children: [
        // =====================================================
        // MAIN CHAT CONTENT
        // =====================================================

        Positioned.fill(
          child: _ChatMainArea(
            controller: controller,
            selectedConversation: selectedConversation,
            onSendMessage: onSendMessage,
            showConversationButton: true,
            onConversationPressed: onToggleSidebar,
          ),
        ),

        // =====================================================
        // BACKDROP
        // =====================================================
        if (isSidebarOpen)
          Positioned.fill(
            child: GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTap: onCloseSidebar,
              child: Container(color: Colors.black.withValues(alpha: 0.32)),
            ),
          ),

        // =====================================================
        // SLIDING CONVERSATION PANEL
        // =====================================================
        AnimatedPositioned(
          duration: const Duration(milliseconds: 260),
          curve: Curves.easeOutCubic,
          top: 0,
          bottom: 0,
          left: isSidebarOpen ? 0 : -sidebarWidth,
          width: sidebarWidth,
          child: Material(
            color: AppColors.background,
            elevation: 18,
            child: SafeArea(
              child: Column(
                children: [
                  // =================================================
                  // CONVERSATION PANEL HEADER
                  // =================================================

                  Container(
                    height: 72,
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    decoration: const BoxDecoration(
                      color: AppColors.background,
                      border: Border(
                        bottom: BorderSide(color: AppColors.borderLight),
                      ),
                    ),
                    child: Row(
                      children: [
                        // =============================================
                        // CONVERSATION ICON
                        // =============================================

                        Container(
                          width: 40,
                          height: 40,
                          alignment: Alignment.center,
                          decoration: BoxDecoration(
                            color: AppColors.antiqueGoldLight,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Icon(
                            Icons.forum_outlined,
                            size: 21,
                            color: AppColors.inkNavy,
                          ),
                        ),

                        const SizedBox(width: 12),

                        // =============================================
                        // TITLE
                        // =============================================
                        const Expanded(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Conversations',
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: TextStyle(
                                  color: AppColors.textPrimary,
                                  fontSize: 16,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),

                              SizedBox(height: 3),

                              Text(
                                'Your legal research history',
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: TextStyle(
                                  color: AppColors.textSecondary,
                                  fontSize: 11,
                                ),
                              ),
                            ],
                          ),
                        ),

                        // =============================================
                        // COLLAPSE PANEL BUTTON
                        //
                        // Cleaner than X / close icon.
                        // =============================================
                        Material(
                          color: Colors.transparent,
                          borderRadius: BorderRadius.circular(10),
                          child: InkWell(
                            onTap: onCloseSidebar,
                            borderRadius: BorderRadius.circular(10),
                            child: const SizedBox(
                              width: 42,
                              height: 42,
                              child: Icon(
                                Icons.keyboard_arrow_left_rounded,
                                size: 28,
                                color: AppColors.textSecondary,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                  // =================================================
                  // CHAT SIDEBAR
                  //
                  // Header disabled because mobile drawer already
                  // provides the Conversations header.
                  // =================================================
                  Expanded(
                    child: ChatSidebar(
                      showBrandHeader: false,
                      onNewChat: () {
                        controller.createNewChat();
                        onCloseSidebar();
                      },
                      conversations: controller.conversations,
                      selectedConversationId: controller.selectedConversationId,
                      onConversationSelected: (conversationId) {
                        controller.selectConversation(conversationId);

                        onCloseSidebar();
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}

// ============================================================
// MAIN CHAT AREA
// ============================================================

class _ChatMainArea extends StatelessWidget {
  const _ChatMainArea({
    required this.controller,
    required this.selectedConversation,
    required this.onSendMessage,
    required this.showConversationButton,
    this.onConversationPressed,
  });

  final ChatController controller;

  final dynamic selectedConversation;

  final ValueChanged<String> onSendMessage;

  final bool showConversationButton;

  final VoidCallback? onConversationPressed;

  @override
  Widget build(BuildContext context) {
    return ColoredBox(
      color: AppColors.workspace,
      child: Column(
        children: [
          // ===================================================
          // MOBILE CHAT HEADER
          // ===================================================

          if (showConversationButton)
            _MobileChatHeader(onConversationPressed: onConversationPressed),

          // ===================================================
          // CHAT CONTENT
          // ===================================================
          Expanded(
            child:
                selectedConversation == null ||
                    selectedConversation.messages.isEmpty
                ? ChatWelcome(onSuggestionSelected: onSendMessage)
                : ChatMessages(
                    messages: selectedConversation.messages,
                    isLoading: controller.isLoading,
                  ),
          ),

          if (controller.errorMessage != null)
            Padding(
              padding: const EdgeInsets.all(8),
              child: Text(
                controller.errorMessage!,
                style: const TextStyle(color: Colors.red),
              ),
            ),

          // ===================================================
          // CHAT INPUT
          // ===================================================
          SafeArea(
            top: false,
            child: Container(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
              decoration: const BoxDecoration(color: AppColors.workspace),
              child: ChatInput(
                isLoading: controller.isLoading,
                onSend: onSendMessage,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ============================================================
// MOBILE CHAT HEADER
// ============================================================

class _MobileChatHeader extends StatelessWidget {
  const _MobileChatHeader({required this.onConversationPressed});

  final VoidCallback? onConversationPressed;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 60,
      padding: const EdgeInsets.symmetric(horizontal: 12),
      decoration: const BoxDecoration(
        color: AppColors.background,
        border: Border(bottom: BorderSide(color: AppColors.borderLight)),
      ),
      child: Row(
        children: [
          // ===================================================
          // CONVERSATION PANEL BUTTON
          //
          // NOT a hamburger.
          //
          // Main app navigation = hamburger
          // Chat navigation = conversation panel icon
          // ===================================================

          Material(
            color: Colors.transparent,
            borderRadius: BorderRadius.circular(10),
            child: InkWell(
              onTap: onConversationPressed,
              borderRadius: BorderRadius.circular(10),
              child: Container(
                width: 42,
                height: 42,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(
                  Icons.forum_outlined,
                  size: 23,
                  color: AppColors.textPrimary,
                ),
              ),
            ),
          ),

          const SizedBox(width: 10),

          // ===================================================
          // TITLE
          // ===================================================
          const Expanded(
            child: Text(
              'Legal AI Assistant',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                color: AppColors.textPrimary,
                fontSize: 16,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),

          // ===================================================
          // NO PLUS BUTTON
          //
          // New conversation is already clearly available
          // inside the Conversations panel.
          // ===================================================
        ],
      ),
    );
  }
}
