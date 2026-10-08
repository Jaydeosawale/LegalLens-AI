import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/theme/app_colors.dart';

class ChatInput extends StatefulWidget {
  const ChatInput({super.key, this.onSend, this.isLoading = false});

  final ValueChanged<String>? onSend;
  final bool isLoading;

  @override
  State<ChatInput> createState() => _ChatInputState();
}

class _ChatInputState extends State<ChatInput> {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();

  bool get _hasText => _controller.text.trim().isNotEmpty;

  void _sendMessage() {
    if (widget.isLoading) return;

    final message = _controller.text.trim();

    if (message.isEmpty) return;

    widget.onSend?.call(message);

    _controller.clear();

    setState(() {});
  }

  @override
  void initState() {
    super.initState();

    _focusNode.addListener(() {
      if (mounted) {
        setState(() {});
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();

    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isFocused = _focusNode.hasFocus;

    return SafeArea(
      top: false,
      child: Container(
        padding: const EdgeInsets.fromLTRB(24, 14, 24, 18),
        decoration: const BoxDecoration(
          color: AppColors.workspace,
          border: Border(top: BorderSide(color: AppColors.borderLight)),
        ),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1000),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                AnimatedContainer(
                  duration: const Duration(milliseconds: 180),
                  curve: Curves.easeOut,
                  decoration: BoxDecoration(
                    // Premium warm surface instead of pure white.
                    color: AppColors.surface,

                    // Softer, more premium corners.
                    borderRadius: BorderRadius.circular(18),

                    border: Border.all(
                      color: isFocused ? AppColors.mutedGold : AppColors.border,
                      width: isFocused ? 1.3 : 1,
                    ),

                    // Very subtle elevation.
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.inkNavy.withValues(
                          alpha: isFocused ? 0.09 : 0.035,
                        ),
                        blurRadius: isFocused ? 22 : 14,
                        offset: const Offset(0, 5),
                      ),
                    ],
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(20),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        // =====================================================
                        // TEXT INPUT
                        // =====================================================
                        Shortcuts(
                          shortcuts: const <ShortcutActivator, Intent>{
                            SingleActivator(LogicalKeyboardKey.enter):
                                _SendMessageIntent(),
                          },
                          child: Actions(
                            actions: <Type, Action<Intent>>{
                              _SendMessageIntent:
                                  CallbackAction<_SendMessageIntent>(
                                    onInvoke: (_) {
                                      _sendMessage();
                                      return null;
                                    },
                                  ),
                            },
                            child: TextField(
                              controller: _controller,
                              focusNode: _focusNode,
                              enabled: !widget.isLoading,
                              minLines: 1,
                              maxLines: 5,
                              keyboardType: TextInputType.multiline,
                              textInputAction: TextInputAction.newline,
                              onChanged: (_) {
                                setState(() {});
                              },
                              decoration: const InputDecoration(
                                hintText:
                                    'Ask Legal Lens about laws, cases or documents...',
                                hintStyle: TextStyle(
                                  color: AppColors.textMuted,
                                  fontSize: 15,
                                ),
                                border: InputBorder.none,
                                enabledBorder: InputBorder.none,
                                focusedBorder: InputBorder.none,
                                contentPadding: EdgeInsets.fromLTRB(
                                  20,
                                  18,
                                  20,
                                  12,
                                ),
                              ),
                              style: const TextStyle(
                                fontSize: 15,
                                height: 1.5,
                                color: AppColors.textPrimary,
                              ),
                            ),
                          ),
                        ),

                        // =====================================================
                        // ACTION BAR
                        // =====================================================
                        Padding(
                          padding: const EdgeInsets.fromLTRB(12, 2, 12, 12),
                          child: Row(
                            children: [
                              _InputActionButton(
                                tooltip: 'Attach document',
                                icon: Icons.attach_file_rounded,
                                onPressed: widget.isLoading
                                    ? null
                                    : () {
                                        // TODO: Open document picker.
                                      },
                              ),

                              const SizedBox(width: 2),

                              _InputActionButton(
                                tooltip: 'Research mode',
                                icon: Icons.auto_awesome_outlined,
                                onPressed: widget.isLoading
                                    ? null
                                    : () {
                                        // TODO: Open research mode selector.
                                      },
                              ),

                              const Spacer(),

                              // =================================================
                              // SEND BUTTON
                              // =================================================
                              AnimatedContainer(
                                duration: const Duration(milliseconds: 180),
                                curve: Curves.easeOut,
                                width: 44,
                                height: 44,
                                decoration: BoxDecoration(
                                  color: _hasText && !widget.isLoading
                                      ? AppColors.inkNavy
                                      : AppColors.surfaceMuted,
                                  borderRadius: BorderRadius.circular(14),
                                  border: Border.all(
                                    color: _hasText && !widget.isLoading
                                        ? AppColors.inkNavy
                                        : AppColors.borderLight,
                                  ),
                                ),
                                child: widget.isLoading
                                    ? const Padding(
                                        padding: EdgeInsets.all(12),
                                        child: SizedBox(
                                          width: 20,
                                          height: 20,
                                          child: CircularProgressIndicator(
                                            strokeWidth: 2,
                                            color: AppColors.antiqueGold,
                                          ),
                                        ),
                                      )
                                    : IconButton(
                                        tooltip: 'Send message',
                                        onPressed: _hasText
                                            ? _sendMessage
                                            : null,
                                        splashRadius: 22,
                                        icon: Icon(
                                          Icons.arrow_upward_rounded,
                                          size: 21,
                                          color: _hasText
                                              ? Colors.white
                                              : AppColors.textMuted,
                                        ),
                                      ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 10),

                const Text(
                  'Legal Lens may make mistakes. Verify important legal information.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 11,
                    color: AppColors.textMuted,
                    height: 1.4,
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

// =====================================================================
// SEND MESSAGE INTENT
// =====================================================================

class _SendMessageIntent extends Intent {
  const _SendMessageIntent();
}

// =====================================================================
// INPUT ACTION BUTTON
// =====================================================================

class _InputActionButton extends StatelessWidget {
  const _InputActionButton({
    required this.tooltip,
    required this.icon,
    required this.onPressed,
  });

  final String tooltip;
  final IconData icon;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: tooltip,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onPressed,
          borderRadius: BorderRadius.circular(10),
          child: SizedBox(
            width: 40,
            height: 40,
            child: Icon(
              icon,
              size: 20,
              color: onPressed == null
                  ? AppColors.border
                  : AppColors.textSecondary,
            ),
          ),
        ),
      ),
    );
  }
}
