import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/app_colors.dart';
import '../../auth/providers/auth_provider.dart';
import '../domain/models/chat_models.dart';
import '../../../core/auth/user_role.dart';

class ChatSidebar extends ConsumerStatefulWidget {
  const ChatSidebar({
    super.key,
    required this.onNewChat,
    required this.conversations,
    required this.selectedConversationId,
    required this.onConversationSelected,
    this.showBrandHeader = true,
    this.showFooter = true,
  });

  final VoidCallback onNewChat;

  final List<ChatConversation> conversations;

  final String? selectedConversationId;

  final ValueChanged<String> onConversationSelected;

  // ===========================================================
  // LAYOUT OPTIONS
  // ===========================================================

  final bool showBrandHeader;
  final bool showFooter;

  @override
  ConsumerState<ChatSidebar> createState() => _ChatSidebarState();
}

class _ChatSidebarState extends ConsumerState<ChatSidebar> {
  String _searchQuery = '';

  @override
  Widget build(BuildContext context) {
    final filteredConversations = widget.conversations.where((conversation) {
      return conversation.title.toLowerCase().contains(
        _searchQuery.toLowerCase(),
      );
    }).toList();

    return Container(
      width: double.infinity,
      decoration: const BoxDecoration(
        color: AppColors.conversationPanel,
        border: Border(right: BorderSide(color: AppColors.sidebarBorder)),
      ),
      child: Column(
        children: [
          // =====================================================
          // BRAND HEADER
          //
          // Desktop: visible
          // Mobile conversation drawer: hidden
          // =====================================================

          if (widget.showBrandHeader) _buildHeader(),

          // =====================================================
          // NEW CONVERSATION
          // =====================================================
          _buildNewChatButton(),

          // =====================================================
          // SEARCH
          // =====================================================
          _buildSearchField(),

          const SizedBox(height: 8),

          // =====================================================
          // CONVERSATIONS
          // =====================================================
          Expanded(
            child: filteredConversations.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 8,
                    ),
                    itemCount: filteredConversations.length,
                    itemBuilder: (context, index) {
                      final conversation = filteredConversations[index];

                      final isSelected =
                          conversation.id == widget.selectedConversationId;

                      return _ConversationTile(
                        conversation: conversation,
                        isSelected: isSelected,
                        onTap: () {
                          widget.onConversationSelected(conversation.id);
                        },
                      );
                    },
                  ),
          ),

          // =====================================================
          // USER FOOTER
          // =====================================================
          if (widget.showFooter) _buildFooter(),
        ],
      ),
    );
  }

  // ===========================================================
  // BRAND HEADER
  // ===========================================================

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 22, 20, 16),
      child: Row(
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              color: AppColors.legalNavy,
              borderRadius: BorderRadius.circular(13),
            ),
            child: Padding(
              padding: const EdgeInsets.all(6),
              child: Image.asset(
                'assets/images/legallens_logo.png',
                fit: BoxFit.contain,
              ),
            ),
          ),

          const SizedBox(width: 12),

          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Legal Lens',
                  style: TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w700,
                    color: AppColors.legalNavy,
                  ),
                ),

                SizedBox(height: 2),

                Text(
                  'Legal intelligence',
                  style: TextStyle(fontSize: 11, color: AppColors.textMuted),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ===========================================================
  // NEW CHAT BUTTON
  // ===========================================================

  Widget _buildNewChatButton() {
    return Padding(
      padding: EdgeInsets.fromLTRB(16, widget.showBrandHeader ? 0 : 16, 16, 0),
      child: SizedBox(
        width: double.infinity,
        height: 48,
        child: ElevatedButton.icon(
          onPressed: widget.onNewChat,
          icon: const Icon(Icons.add_comment_outlined, size: 19),
          label: const Text('New conversation'),
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.legalNavy,
            foregroundColor: Colors.white,
            elevation: 0,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            textStyle: const TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
      ),
    );
  }

  // ===========================================================
  // SEARCH FIELD
  // ===========================================================

  Widget _buildSearchField() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      child: TextField(
        onChanged: (value) {
          setState(() {
            _searchQuery = value;
          });
        },
        style: const TextStyle(fontSize: 13, color: AppColors.textPrimary),
        decoration: InputDecoration(
          hintText: 'Search conversations',
          hintStyle: const TextStyle(color: AppColors.textMuted, fontSize: 13),
          prefixIcon: const Icon(
            Icons.search_rounded,
            size: 20,
            color: AppColors.textMuted,
          ),
          filled: true,
          fillColor: AppColors.workspace,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(11),
            borderSide: BorderSide.none,
          ),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 14,
            vertical: 12,
          ),
        ),
      ),
    );
  }

  // ===========================================================
  // EMPTY STATE
  // ===========================================================

  Widget _buildEmptyState() {
    return const Center(
      child: Padding(
        padding: EdgeInsets.all(28),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.forum_outlined, size: 40, color: AppColors.textMuted),

            SizedBox(height: 14),

            Text(
              'No conversations yet',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontWeight: FontWeight.w600,
                color: AppColors.legalNavy,
              ),
            ),

            SizedBox(height: 6),

            Text(
              'Start a new legal conversation to begin.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 12,
                color: AppColors.textMuted,
                height: 1.4,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ===========================================================
  // USER FOOTER
  // ===========================================================

  Widget _buildFooter() {
    final authState = ref.watch(authProvider);
    final user = authState.user;
    final role = authState.role ?? UserRole.user;

    final fullName = user?.fullName?.trim();
    final email = user?.email ?? '';

    final displayName = fullName != null && fullName.isNotEmpty
        ? fullName
        : email.isNotEmpty
        ? email.split('@').first
        : 'User';

    final initial = displayName.isNotEmpty
        ? displayName.substring(0, 1).toUpperCase()
        : 'U';

    final roleLabel = switch (role) {
      UserRole.superAdmin => 'Super Administrator',
      UserRole.admin => 'Administrator',
      UserRole.user => 'Legal Lens User',
      UserRole.legalProfessional => 'Legal Professional',
    };

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: AppColors.sidebarBorder)),
      ),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.borderLight),
        ),
        child: Row(
          children: [
            // ============================================================
            // AVATAR
            // ============================================================

            Container(
              width: 42,
              height: 42,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: AppColors.antiqueGold,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: AppColors.antiqueGold.withValues(alpha: 0.18),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Text(
                initial,
                style: const TextStyle(
                  color: AppColors.inkNavy,
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),

            const SizedBox(width: 12),

            // ============================================================
            // USER INFORMATION
            // ============================================================
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    displayName,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                    ),
                  ),

                  const SizedBox(height: 3),

                  Text(
                    roleLabel,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 11,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),

            // ============================================================
            // ACCOUNT MENU
            // ============================================================
            PopupMenuButton<String>(
              tooltip: 'Account options',
              padding: EdgeInsets.zero,
              icon: const Icon(
                Icons.more_horiz_rounded,
                color: AppColors.textSecondary,
              ),
              onSelected: (value) async {
                if (value == 'profile') {
                  _showProfileDialog(
                    context,
                    displayName: displayName,
                    email: email,
                  );
                }

                if (value == 'logout') {
                  await ref.read(authProvider.notifier).logout();
                }
              },
              itemBuilder: (context) => [
                const PopupMenuItem(
                  value: 'profile',
                  child: Row(
                    children: [
                      Icon(Icons.person_outline_rounded),
                      SizedBox(width: 10),
                      Text('Profile'),
                    ],
                  ),
                ),

                const PopupMenuDivider(),

                const PopupMenuItem(
                  value: 'logout',
                  child: Row(
                    children: [
                      Icon(Icons.logout_rounded, color: Colors.redAccent),
                      SizedBox(width: 10),
                      Text(
                        'Logout',
                        style: TextStyle(
                          color: Colors.redAccent,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // ===========================================================
  // PROFILE DIALOG
  // ===========================================================

  void _showProfileDialog(
    BuildContext context, {
    required String displayName,
    required String email,
  }) {
    showDialog<void>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Profile'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                displayName,
                style: const TextStyle(
                  fontWeight: FontWeight.w700,
                  fontSize: 16,
                ),
              ),

              const SizedBox(height: 8),

              Text(
                email.isNotEmpty ? email : 'No email available',
                style: const TextStyle(color: AppColors.textMuted),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Close'),
            ),
          ],
        );
      },
    );
  }
}

// ============================================================
// CONVERSATION TILE
// ============================================================

class _ConversationTile extends StatelessWidget {
  const _ConversationTile({
    required this.conversation,
    required this.isSelected,
    required this.onTap,
  });

  final ChatConversation conversation;
  final bool isSelected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Material(
        color: isSelected ? AppColors.selectedConversation : Colors.transparent,
        borderRadius: BorderRadius.circular(11),
        child: InkWell(
          borderRadius: BorderRadius.circular(11),
          onTap: onTap,
          hoverColor: AppColors.hoverConversation,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            child: Row(
              children: [
                Icon(
                  Icons.chat_bubble_outline_rounded,
                  size: 18,
                  color: isSelected ? AppColors.legalNavy : AppColors.textMuted,
                ),

                const SizedBox(width: 11),

                Expanded(
                  child: Text(
                    conversation.title,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontSize: 13,
                      height: 1.3,
                      color: AppColors.textPrimary,
                      fontWeight: isSelected
                          ? FontWeight.w600
                          : FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
